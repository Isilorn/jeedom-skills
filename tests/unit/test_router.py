"""Tests unitaires pour scripts/_common/router.py."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "jeedom-audit" / "scripts"))

from _common import router

MOCK_CREDS = {
    "ssh_alias": "Jeedom",
    "db_name": "jeedom",
    "api_url": "https://jeedom.local",
    "api_key": "secret-key",
    "preferred_mode": "auto",
    "verify_ssl": False,
}

CREDS_API_ONLY = {**MOCK_CREDS, "preferred_mode": "api"}
CREDS_MYSQL_ONLY = {**MOCK_CREDS, "preferred_mode": "mysql"}


def _ssh_ok() -> MagicMock:
    return MagicMock(ok=True)


def _ssh_ko() -> MagicMock:
    return MagicMock(ok=False)


@pytest.fixture(autouse=True)
def clear_cache():
    router._CAPS_CACHE.clear()
    yield
    router._CAPS_CACHE.clear()


# ── detect_capabilities ────────────────────────────────────────────────────────


class TestDetectCapabilities:
    def test_both_available(self):
        with (
            patch.object(router._ssh, "mysql_json", return_value=_ssh_ok()),
            patch.object(router._api_call, "run", return_value={"result": "ok"}),
        ):
            caps = router.detect_capabilities(MOCK_CREDS)
        assert caps == {"mysql": True, "api": True}

    def test_mysql_ko_api_ok(self):
        with (
            patch.object(router._ssh, "mysql_json", return_value=_ssh_ko()),
            patch.object(router._api_call, "run", return_value={"result": "ok"}),
        ):
            caps = router.detect_capabilities(MOCK_CREDS)
        assert caps == {"mysql": False, "api": True}

    def test_mysql_ok_api_ko(self):
        with (
            patch.object(router._ssh, "mysql_json", return_value=_ssh_ok()),
            patch.object(router._api_call, "run", return_value={"error": "timeout"}),
        ):
            caps = router.detect_capabilities(MOCK_CREDS)
        assert caps == {"mysql": True, "api": False}

    def test_both_ko(self):
        with (
            patch.object(router._ssh, "mysql_json", return_value=_ssh_ko()),
            patch.object(router._api_call, "run", return_value={"error": "unreachable"}),
        ):
            caps = router.detect_capabilities(MOCK_CREDS)
        assert caps == {"mysql": False, "api": False}

    def test_ssh_raises_exception(self):
        with (
            patch.object(router._ssh, "mysql_json", side_effect=ConnectionError("ssh fail")),
            patch.object(router._api_call, "run", return_value={"result": "ok"}),
        ):
            caps = router.detect_capabilities(MOCK_CREDS)
        assert caps["mysql"] is False
        assert caps["api"] is True

    def test_api_raises_exception(self):
        with (
            patch.object(router._ssh, "mysql_json", return_value=_ssh_ok()),
            patch.object(router._api_call, "run", side_effect=ConnectionError("api fail")),
        ):
            caps = router.detect_capabilities(MOCK_CREDS)
        assert caps["mysql"] is True
        assert caps["api"] is False

    def test_cache_hit_avoids_re_detection(self):
        with (
            patch.object(router._ssh, "mysql_json", return_value=_ssh_ok()) as mock_ssh,
            patch.object(router._api_call, "run", return_value={"result": "ok"}) as mock_api,
        ):
            router.detect_capabilities(MOCK_CREDS)
            router.detect_capabilities(MOCK_CREDS)
        assert mock_ssh.call_count == 1
        assert mock_api.call_count == 1

    def test_different_creds_different_cache_entries(self):
        creds_b = {**MOCK_CREDS, "api_url": "https://jeedom2.local"}
        with (
            patch.object(router._ssh, "mysql_json", return_value=_ssh_ok()) as mock_ssh,
            patch.object(router._api_call, "run", return_value={"result": "ok"}),
        ):
            router.detect_capabilities(MOCK_CREDS)
            router.detect_capabilities(creds_b)
        assert mock_ssh.call_count == 2


# ── route — preferred_mode="api" ───────────────────────────────────────────────


class TestRouteApiMode:
    def test_structural_audit_returns_api(self):
        assert router.route("structural_audit", CREDS_API_ONLY) == "api"

    def test_runtime_state_returns_api(self):
        assert router.route("runtime_state", CREDS_API_ONLY) == "api"

    def test_history_returns_api(self):
        assert router.route("history", CREDS_API_ONLY) == "api"

    def test_statistics_returns_api(self):
        assert router.route("statistics", CREDS_API_ONLY) == "api"

    def test_logs_returns_ssh(self):
        assert router.route("logs", CREDS_API_ONLY) == "ssh"

    def test_version_check_returns_api(self):
        assert router.route("version_check", CREDS_API_ONLY) == "api"

    def test_plugin_list_returns_api(self):
        assert router.route("plugin_list", CREDS_API_ONLY) == "api"

    def test_resolve_refs_returns_api(self):
        assert router.route("resolve_refs", CREDS_API_ONLY) == "api"

    def test_unknown_op_returns_api(self):
        assert router.route("unknown_operation", CREDS_API_ONLY) == "api"


# ── route — preferred_mode="mysql" ────────────────────────────────────────────


class TestRouteMysqlMode:
    def test_structural_audit_returns_mysql(self):
        assert router.route("structural_audit", CREDS_MYSQL_ONLY) == "mysql"

    def test_runtime_state_returns_api(self):
        # runtime_state est impossible en MySQL — API obligatoire
        assert router.route("runtime_state", CREDS_MYSQL_ONLY) == "api"

    def test_statistics_returns_api(self):
        # statistics aussi impossible en MySQL
        assert router.route("statistics", CREDS_MYSQL_ONLY) == "api"

    def test_logs_returns_ssh(self):
        assert router.route("logs", CREDS_MYSQL_ONLY) == "ssh"

    def test_history_returns_mysql(self):
        assert router.route("history", CREDS_MYSQL_ONLY) == "mysql"

    def test_version_check_returns_mysql(self):
        assert router.route("version_check", CREDS_MYSQL_ONLY) == "mysql"

    def test_plugin_list_returns_mysql(self):
        assert router.route("plugin_list", CREDS_MYSQL_ONLY) == "mysql"

    def test_resolve_refs_returns_mysql(self):
        assert router.route("resolve_refs", CREDS_MYSQL_ONLY) == "mysql"


# ── route — preferred_mode="auto" ─────────────────────────────────────────────


class TestRouteAutoMode:
    def _caps(self, mysql: bool, api: bool):
        return {"mysql": mysql, "api": api}

    def _route(self, operation: str, caps: dict) -> str:
        key = (MOCK_CREDS["ssh_alias"], MOCK_CREDS["api_url"])
        router._CAPS_CACHE[key] = caps
        return router.route(operation, MOCK_CREDS)

    def test_structural_audit_mysql_available(self):
        assert self._route("structural_audit", self._caps(True, True)) == "mysql"

    def test_structural_audit_mysql_ko_fallback_api(self):
        assert self._route("structural_audit", self._caps(False, True)) == "api"

    def test_structural_audit_both_ko_returns_preferred(self):
        # Pas de fallback disponible → retourne preferred (mysql) malgré KO
        assert self._route("structural_audit", self._caps(False, False)) == "mysql"

    def test_runtime_state_api_available(self):
        assert self._route("runtime_state", self._caps(True, True)) == "api"

    def test_runtime_state_api_ko_no_fallback(self):
        # runtime_state n'a pas de fallback MySQL
        assert self._route("runtime_state", self._caps(True, False)) == "api"

    def test_history_api_available(self):
        assert self._route("history", self._caps(True, True)) == "api"

    def test_history_api_ko_fallback_mysql(self):
        assert self._route("history", self._caps(True, False)) == "mysql"

    def test_statistics_api_ko_no_fallback(self):
        assert self._route("statistics", self._caps(True, False)) == "api"

    def test_logs_always_ssh(self):
        assert self._route("logs", self._caps(True, True)) == "ssh"

    def test_logs_ssh_ko_still_returns_ssh(self):
        # Pas de fallback API pour les logs en V1
        assert self._route("logs", self._caps(False, True)) == "ssh"

    def test_version_check_api_available(self):
        assert self._route("version_check", self._caps(True, True)) == "api"

    def test_version_check_api_ko_fallback_mysql(self):
        assert self._route("version_check", self._caps(True, False)) == "mysql"

    def test_plugin_list_api_available(self):
        assert self._route("plugin_list", self._caps(True, True)) == "api"

    def test_plugin_list_api_ko_fallback_mysql(self):
        assert self._route("plugin_list", self._caps(True, False)) == "mysql"

    def test_resolve_refs_mysql_available(self):
        assert self._route("resolve_refs", self._caps(True, True)) == "mysql"

    def test_resolve_refs_mysql_ko_fallback_api(self):
        assert self._route("resolve_refs", self._caps(False, True)) == "api"

    def test_unknown_op_defaults_to_mysql(self):
        assert self._route("unknown_op", self._caps(True, True)) == "mysql"

    def test_unknown_op_mysql_ko_fallback_none_returns_mysql(self):
        # Opération inconnue → preferred=mysql, fallback=None → retourne mysql même si KO
        assert self._route("unknown_op", self._caps(False, True)) == "mysql"


# ── with_fallback ──────────────────────────────────────────────────────────────


class TestWithFallback:
    def test_primary_success_returns_result_no_mention(self):
        primary = lambda: {"rows": [{"id": "1"}]}
        fallback = lambda: {"rows": []}
        result, mention = router.with_fallback(primary, fallback, "⚠ fallback")
        assert result == {"rows": [{"id": "1"}]}
        assert mention is None

    def test_primary_error_dict_triggers_fallback(self):
        primary = lambda: {"error": "MySQL KO"}
        fallback = lambda: {"result": "via api"}
        result, mention = router.with_fallback(primary, fallback, "⚠ Données via API")
        assert result == {"result": "via api"}
        assert mention == "⚠ Données via API"

    def test_primary_raises_triggers_fallback(self):
        def boom():
            raise ConnectionError("SSH unreachable")

        fallback = lambda: {"result": "fallback ok"}
        result, mention = router.with_fallback(boom, fallback, "⚠ SSH KO, API utilisée")
        assert result == {"result": "fallback ok"}
        assert mention == "⚠ SSH KO, API utilisée"

    def test_primary_fails_fallback_also_raises(self):
        primary = lambda: {"error": "primary fail"}

        def bad_fallback():
            raise RuntimeError("fallback aussi KO")

        result, mention = router.with_fallback(primary, bad_fallback, "⚠ tout KO")
        assert "error" in result
        assert mention == "⚠ tout KO"

    def test_primary_fails_fallback_returns_error_dict(self):
        primary = lambda: {"error": "primary fail"}
        fallback = lambda: {"error": "fallback fail"}
        result, mention = router.with_fallback(primary, fallback, "⚠ mention")
        assert result == {"error": "fallback fail"}
        assert mention == "⚠ mention"

    def test_result_not_dict_is_success(self):
        # Résultat scalaire (ex. ping → "ok") ne déclenche pas le fallback
        primary = lambda: "ok"
        fallback = lambda: "fallback"
        result, mention = router.with_fallback(primary, fallback, "⚠ mention")
        assert result == "ok"
        assert mention is None

    def test_result_list_is_success(self):
        primary = lambda: [{"id": "1"}, {"id": "2"}]
        fallback = lambda: []
        result, mention = router.with_fallback(primary, fallback, "⚠ mention")
        assert len(result) == 2
        assert mention is None
