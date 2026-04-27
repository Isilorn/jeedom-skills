"""Tests unitaires pour scripts/logs_query.py."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "jeedom-audit" / "scripts"))

from logs_query import _resolve_log_path, _validate_log_name, run

MOCK_CREDS = {"ssh_alias": "Jeedom"}

LOG_DIR_PRIMARY = "/var/www/html/log"
LOG_DIR_FALLBACK = "/usr/share/nginx/www/jeedom/log"


# ── _validate_log_name ─────────────────────────────────────────────────────────


class TestValidateLogName:
    def test_simple_name_ok(self):
        _validate_log_name("core")  # ne doit pas lever

    def test_name_with_hyphen_ok(self):
        _validate_log_name("jMQTT")

    def test_name_with_underscore_ok(self):
        _validate_log_name("plugin_virtual")

    def test_subdir_one_level_ok(self):
        _validate_log_name("scenarioLog/scenario70.log")  # ne doit pas lever

    def test_subdir_with_dot_ok(self):
        _validate_log_name("scenarioLog/scenario1.log")

    def test_path_traversal_rejected(self):
        with pytest.raises(ValueError, match="invalide"):
            _validate_log_name("../etc/passwd")

    def test_double_slash_rejected(self):
        with pytest.raises(ValueError, match="invalide"):
            _validate_log_name("scenarioLog/sub/deep")

    def test_space_rejected(self):
        with pytest.raises(ValueError, match="invalide"):
            _validate_log_name("my log")

    def test_empty_rejected(self):
        with pytest.raises(ValueError):
            _validate_log_name("")


# ── _resolve_log_path ──────────────────────────────────────────────────────────


def _ssh_ok(path: str) -> MagicMock:
    m = MagicMock()
    m.ok = True
    m.stdout = path + "\n"
    return m


def _ssh_empty() -> MagicMock:
    m = MagicMock()
    m.ok = True
    m.stdout = ""
    return m


class TestResolveLogPath:
    def test_found_primary(self):
        expected = f"{LOG_DIR_PRIMARY}/core"
        with patch("logs_query._ssh.run", return_value=_ssh_ok(expected)) as mock_run:
            result = _resolve_log_path("Jeedom", "core")
        assert result == expected
        mock_run.assert_called_once()

    def test_not_found_returns_none(self):
        with patch("logs_query._ssh.run", return_value=_ssh_empty()):
            result = _resolve_log_path("Jeedom", "core")
        assert result is None

    def test_ssh_fail_returns_none(self):
        m = MagicMock()
        m.ok = False
        m.stdout = ""
        with patch("logs_query._ssh.run", return_value=m):
            result = _resolve_log_path("Jeedom", "core")
        assert result is None


# ── run() ──────────────────────────────────────────────────────────────────────


SAMPLE_LOG_LINES = "\n".join([
    "[2026-04-27 10:00:01] [INFO] Démarrage du cœur Jeedom",
    "[2026-04-27 10:00:02] [ERROR] Plugin jMQTT — connexion perdue",
    "[2026-04-27 10:00:03] [WARNING] 133 commandes sans valeur",
    "[2026-04-27 10:00:04] [INFO] Scénario 70 déclenché",
])


def _make_tail_result(content: str = SAMPLE_LOG_LINES) -> MagicMock:
    m = MagicMock()
    m.ok = True
    m.stdout = content
    m.stderr = ""
    return m


def _make_fail_result(stderr: str = "permission denied", code: int = 1) -> MagicMock:
    m = MagicMock()
    m.ok = False
    m.stdout = ""
    m.stderr = stderr
    m.returncode = code
    return m


class TestRun:
    def _patch_resolve(self, path: str | None):
        return patch("logs_query._resolve_log_path", return_value=path)

    def test_basic_returns_lines(self):
        log_file = f"{LOG_DIR_PRIMARY}/core"
        with self._patch_resolve(log_file):
            with patch("logs_query._ssh.run", return_value=_make_tail_result()):
                result = run("core", creds=MOCK_CREDS)

        assert result["log_file"] == log_file
        assert result["count"] == 4
        assert len(result["lines"]) == 4
        assert "error" not in result

    def test_log_not_found_returns_error(self):
        with self._patch_resolve(None):
            result = run("inexistant", creds=MOCK_CREDS)

        assert "error" in result
        assert result["log_file"] is None
        assert result["lines"] == []
        assert result["count"] == 0

    def test_tail_failure_returns_error(self):
        log_file = f"{LOG_DIR_PRIMARY}/core"
        with self._patch_resolve(log_file):
            with patch("logs_query._ssh.run", return_value=_make_fail_result("permission denied")):
                result = run("core", creds=MOCK_CREDS)

        assert "error" in result
        assert "permission denied" in result["error"]
        assert result["lines"] == []

    def test_invalid_log_name_returns_error(self):
        result = run("../etc/passwd", creds=MOCK_CREDS)
        assert "error" in result
        assert "invalide" in result["error"]

    def test_grep_filters_lines(self):
        log_file = f"{LOG_DIR_PRIMARY}/core"
        with self._patch_resolve(log_file):
            with patch("logs_query._ssh.run", return_value=_make_tail_result()):
                result = run("core", grep="ERROR", creds=MOCK_CREDS)

        assert result["count"] == 1
        assert "ERROR" in result["lines"][0]

    def test_grep_case_insensitive(self):
        log_file = f"{LOG_DIR_PRIMARY}/core"
        with self._patch_resolve(log_file):
            with patch("logs_query._ssh.run", return_value=_make_tail_result()):
                result = run("core", grep="error", creds=MOCK_CREDS)

        assert result["count"] == 1

    def test_grep_no_match_returns_empty(self):
        log_file = f"{LOG_DIR_PRIMARY}/core"
        with self._patch_resolve(log_file):
            with patch("logs_query._ssh.run", return_value=_make_tail_result()):
                result = run("core", grep="CRITICAL", creds=MOCK_CREDS)

        assert result["count"] == 0
        assert result["lines"] == []
        assert result["log_file"] == log_file  # log_file toujours renseigné

    def test_lines_param_passed_to_tail(self):
        log_file = f"{LOG_DIR_PRIMARY}/core"
        captured = {}

        def capture_ssh(alias, cmd):
            captured["cmd"] = cmd
            return _make_tail_result()

        with self._patch_resolve(log_file):
            with patch("logs_query._ssh.run", side_effect=capture_ssh):
                run("core", lines=200, creds=MOCK_CREDS)

        assert "200" in captured["cmd"]

    def test_empty_log_file_ok(self):
        log_file = f"{LOG_DIR_PRIMARY}/php"
        with self._patch_resolve(log_file):
            with patch("logs_query._ssh.run", return_value=_make_tail_result("")):
                result = run("php", creds=MOCK_CREDS)

        assert result["count"] == 0
        assert result["lines"] == []
        assert "error" not in result

    def test_tail_timeout_stderr_propagated(self):
        log_file = f"{LOG_DIR_PRIMARY}/core"
        fail = _make_fail_result(stderr="Timeout après 30s (tentative 1/1)", code=124)
        with self._patch_resolve(log_file):
            with patch("logs_query._ssh.run", return_value=fail):
                result = run("core", creds=MOCK_CREDS)

        assert "error" in result
        assert "Timeout" in result["error"]
