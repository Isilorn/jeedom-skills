"""Tests unitaires pour scripts/api_call.py."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "jeedom-audit" / "scripts"))

from api_call import is_blacklisted, run

MOCK_CREDS = {
    "ssh_alias": "Jeedom",
    "api_url": "https://jeedom.local",
    "api_key": "secret-api-key-123",
    "verify_ssl": False,
}

MOCK_CREDS_NO_API = {
    "ssh_alias": "Jeedom",
    "api_url": "",
    "api_key": "",
}


# ── is_blacklisted ─────────────────────────────────────────────────────────────


class TestIsBlacklisted:
    def test_exact_blacklisted_execCmd(self):
        assert is_blacklisted("cmd::execCmd") is True

    def test_exact_blacklisted_changeState(self):
        assert is_blacklisted("scenario::changeState") is True

    def test_exact_blacklisted_datastore_save(self):
        assert is_blacklisted("datastore::save") is True

    def test_exact_blacklisted_interact(self):
        assert is_blacklisted("interact::tryToReply") is True

    def test_pattern_save_blocked(self):
        assert is_blacklisted("scenario::save") is True

    def test_pattern_delete_blocked(self):
        assert is_blacklisted("eqLogic::delete") is True

    def test_pattern_update_blocked(self):
        assert is_blacklisted("cmd::update") is True

    def test_pattern_add_blocked(self):
        assert is_blacklisted("plugin::add") is True

    def test_pattern_create_blocked(self):
        assert is_blacklisted("object::create") is True

    def test_read_method_ok(self):
        assert is_blacklisted("scenario::byId") is False

    def test_ping_ok(self):
        assert is_blacklisted("ping") is False

    def test_scenario_all_ok(self):
        assert is_blacklisted("scenario::all") is False

    def test_cmd_get_history_ok(self):
        assert is_blacklisted("cmd::getHistory") is False

    def test_version_ok(self):
        assert is_blacklisted("version") is False

    def test_summary_global_ok(self):
        assert is_blacklisted("summary::global") is False


# ── run() ──────────────────────────────────────────────────────────────────────


def _rpc_ok(result) -> dict:
    return {"jsonrpc": "2.0", "result": result, "id": 1}


def _rpc_error(code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": 1}


def _transport_fail(msg: str = "Connection refused") -> dict:
    return {"_transport_error": msg}


class TestRun:
    def _patch_call(self, return_value):
        return patch("api_call._call_api", return_value=return_value)

    def test_blacklisted_method_blocked(self):
        result = run("cmd::execCmd", creds=MOCK_CREDS)
        assert "error" in result
        assert result.get("code") == "api::forbidden::method"

    def test_blacklisted_pattern_blocked(self):
        result = run("scenario::save", creds=MOCK_CREDS)
        assert "error" in result
        assert result.get("code") == "api::forbidden::method"

    def test_missing_api_url_returns_error(self):
        result = run("ping", creds=MOCK_CREDS_NO_API)
        assert "error" in result
        assert "api_url" in result["error"] or "setup" in result["error"]

    def test_ping_returns_scalar_result(self):
        with self._patch_call(_rpc_ok("ok")):
            result = run("ping", creds=MOCK_CREDS)
        assert result["result"] == "ok"
        assert result["_filtered_fields"] == []

    def test_dict_result_returned(self):
        scenario = {"id": "70", "name": "Présence", "isActive": "1"}
        with self._patch_call(_rpc_ok(scenario)):
            result = run("scenario::byId", params={"id": 70}, creds=MOCK_CREDS)
        assert result["result"]["id"] == "70"
        assert result["_filtered_fields"] == []

    def test_list_result_returned(self):
        scenarios = [{"id": "70", "name": "A"}, {"id": "71", "name": "B"}]
        with self._patch_call(_rpc_ok(scenarios)):
            result = run("scenario::all", creds=MOCK_CREDS)
        assert isinstance(result["result"], list)
        assert len(result["result"]) == 2

    def test_sensitive_field_filtered_in_dict(self):
        scenario_with_secret = {"id": "70", "name": "A", "apikey": "tok123"}
        with self._patch_call(_rpc_ok(scenario_with_secret)):
            result = run("scenario::byId", params={"id": 70}, creds=MOCK_CREDS)
        assert result["result"]["apikey"] == "[FILTRÉ]"
        assert "apikey" in result["_filtered_fields"]

    def test_sensitive_field_filtered_in_list(self):
        rows = [{"id": "1", "name": "broker", "mqttPassword": "secret"}]
        with self._patch_call(_rpc_ok(rows)):
            result = run("eqLogic::byType", params={"type": "jMQTT"}, creds=MOCK_CREDS)
        assert result["result"][0]["mqttPassword"] == "[FILTRÉ]"

    def test_rpc_error_returns_error_dict(self):
        with self._patch_call(_rpc_error(-32500, "Method not found")):
            result = run("nonexistent::method", creds=MOCK_CREDS)
        assert "error" in result
        assert result.get("code") == -32500
        assert "not found" in result["error"].lower()

    def test_transport_error_retried_then_returned(self):
        fail = _transport_fail("Timeout (15s)")
        with patch("api_call._call_api", side_effect=[fail, fail]) as mock_call:
            result = run("ping", creds=MOCK_CREDS)
        assert mock_call.call_count == 2
        assert "error" in result

    def test_transport_error_ok_on_retry(self):
        fail = _transport_fail("Timeout (15s)")
        success = _rpc_ok("ok")
        with patch("api_call._call_api", side_effect=[fail, success]) as mock_call:
            result = run("ping", creds=MOCK_CREDS)
        assert mock_call.call_count == 2
        assert result["result"] == "ok"

    def test_api_key_injected_in_params(self):
        captured = {}

        def capture(api_url, api_key, method, params, **kw):
            captured["params"] = params
            captured["api_key"] = api_key
            return _rpc_ok("ok")

        with patch("api_call._call_api", side_effect=capture):
            run("ping", creds=MOCK_CREDS)

        assert captured["api_key"] == MOCK_CREDS["api_key"]
