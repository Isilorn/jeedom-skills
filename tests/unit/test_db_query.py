"""Tests unitaires pour scripts/db_query.py."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "jeedom-audit" / "scripts"))

from db_query import _escape_trigger, _substitute_params, run


# ── _escape_trigger ────────────────────────────────────────────────────────────

class TestEscapeTrigger:
    def test_bare_trigger_gets_backticked(self):
        assert _escape_trigger("SELECT trigger FROM scenario") == "SELECT `trigger` FROM scenario"

    def test_already_backticked_unchanged(self):
        q = "SELECT `trigger` FROM scenario"
        assert _escape_trigger(q) == q

    def test_trigger_in_string_literal_unchanged(self):
        # Cas simple — le mot trigger dans un alias ne doit pas poser problème
        result = _escape_trigger("SELECT id AS trigger_id FROM scenario")
        assert "`trigger`" not in result or "trigger_id" in result

    def test_multiple_occurrences(self):
        q = "SELECT trigger FROM scenario WHERE trigger LIKE '%x%'"
        result = _escape_trigger(q)
        assert result.count("`trigger`") == 2

    def test_case_insensitive(self):
        assert "`TRIGGER`" in _escape_trigger("SELECT TRIGGER FROM scenario")

    def test_no_trigger_unchanged(self):
        q = "SELECT id, name FROM eqLogic"
        assert _escape_trigger(q) == q


# ── _substitute_params ─────────────────────────────────────────────────────────

class TestSubstituteParams:
    def test_string_param_quoted(self):
        result = _substitute_params("SELECT * FROM eqLogic WHERE name = ?", ["Lampe"])
        assert result == "SELECT * FROM eqLogic WHERE name = 'Lampe'"

    def test_int_param_unquoted(self):
        result = _substitute_params("SELECT * FROM cmd WHERE eqLogic_id = ?", [42])
        assert result == "SELECT * FROM cmd WHERE eqLogic_id = 42"

    def test_none_param_becomes_null(self):
        result = _substitute_params("SELECT * FROM eqLogic WHERE object_id = ?", [None])
        assert result == "SELECT * FROM eqLogic WHERE object_id = NULL"

    def test_string_with_single_quote_escaped(self):
        result = _substitute_params("SELECT * FROM eqLogic WHERE name = ?", ["L'ampe"])
        assert "\\'" in result

    def test_multiple_params(self):
        result = _substitute_params(
            "SELECT * FROM cmd WHERE eqLogic_id = ? AND type = ?",
            [42, "info"],
        )
        assert result == "SELECT * FROM cmd WHERE eqLogic_id = 42 AND type = 'info'"

    def test_bool_param(self):
        result = _substitute_params("SELECT * FROM eqLogic WHERE isEnable = ?", [True])
        assert result == "SELECT * FROM eqLogic WHERE isEnable = 1"


# ── run() avec SSH mocké ───────────────────────────────────────────────────────

MOCK_ROWS = [
    {"id": "8", "name": "Meteo", "eqType_name": "weather", "isEnable": "1"},
    {"id": "25", "name": "Thermostat", "eqType_name": "thermostat", "isEnable": "1"},
]

MOCK_CREDS = {
    "ssh_alias": "Jeedom",
    "db_name": "jeedom",
    "preferred_mode": "auto",
}


class TestRun:
    def _mock_ssh_ok(self, rows=None):
        mock = MagicMock()
        mock.ok = True
        mock.stdout = json.dumps(rows or MOCK_ROWS)
        mock.stderr = ""
        return mock

    def _mock_ssh_fail(self, stderr="mysql error"):
        mock = MagicMock()
        mock.ok = False
        mock.stdout = ""
        mock.stderr = stderr
        mock.returncode = 1
        return mock

    def test_basic_query_returns_rows(self):
        with patch("db_query._ssh.mysql_json", return_value=self._mock_ssh_ok()):
            result = run("SELECT id, name FROM eqLogic LIMIT 2", creds=MOCK_CREDS)
        assert result["rows"] == MOCK_ROWS
        assert result["_filtered_fields"] == []

    def test_ssh_failure_returns_error(self):
        with patch("db_query._ssh.mysql_json", return_value=self._mock_ssh_fail("Access denied")):
            result = run("SELECT 1", creds=MOCK_CREDS)
        assert "error" in result
        assert "Access denied" in result["error"]
        assert result["rows"] == []

    def test_trigger_auto_escaped(self):
        captured = {}

        def capture_call(alias, db, query, **kw):
            captured["query"] = query
            return self._mock_ssh_ok([])

        with patch("db_query._ssh.mysql_json", side_effect=capture_call):
            run("SELECT trigger FROM scenario", creds=MOCK_CREDS)

        assert "`trigger`" in captured["query"]

    def test_sensitive_field_filtered(self):
        rows_with_password = [{"id": "1", "name": "broker", "mqttPassword": "secret123"}]
        with patch("db_query._ssh.mysql_json", return_value=self._mock_ssh_ok(rows_with_password)):
            result = run("SELECT id, name, mqttPassword FROM eqLogic", creds=MOCK_CREDS)

        assert result["rows"][0]["mqttPassword"] == "[FILTRÉ]"
        assert "mqttPassword" in result["_filtered_fields"]

    def test_params_substituted(self):
        captured = {}

        def capture_call(alias, db, query, **kw):
            captured["query"] = query
            return self._mock_ssh_ok([])

        with patch("db_query._ssh.mysql_json", side_effect=capture_call):
            run("SELECT * FROM eqLogic WHERE id = ?", params=[42], creds=MOCK_CREDS)

        assert "42" in captured["query"]
        assert "?" not in captured["query"]

    def test_invalid_json_from_mysql(self):
        bad = MagicMock()
        bad.ok = True
        bad.stdout = "not json at all"
        bad.stderr = ""
        with patch("db_query._ssh.mysql_json", return_value=bad):
            result = run("SELECT 1", creds=MOCK_CREDS)
        assert "error" in result
        assert result["rows"] == []
