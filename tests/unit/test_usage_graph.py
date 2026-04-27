"""Tests unitaires pour scripts/usage_graph.py."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "jeedom-audit" / "scripts"))

from usage_graph import _classify_expr_rows, run

MOCK_CREDS = {
    "ssh_alias": "Jeedom",
    "db_name": "jeedom",
    "preferred_mode": "auto",
}


# ── _classify_expr_rows ────────────────────────────────────────────────────────


class TestClassifyExprRows:
    def _row(self, sid: int, name: str, ss_type: str, ss_subtype: str) -> dict:
        return {
            "scenario_id": str(sid),
            "scenario_name": name,
            "ss_type": ss_type,
            "ss_subtype": ss_subtype,
        }

    def test_condition_subtype_classified_as_condition(self):
        rows = [self._row(10, "S1", "if", "condition")]
        conds, acts = _classify_expr_rows(rows)
        assert len(conds) == 1
        assert conds[0]["id"] == 10
        assert acts == []

    def test_then_classified_as_action(self):
        rows = [self._row(10, "S1", "if", "then")]
        conds, acts = _classify_expr_rows(rows)
        assert conds == []
        assert len(acts) == 1

    def test_else_classified_as_action(self):
        rows = [self._row(10, "S1", "if", "else")]
        _, acts = _classify_expr_rows(rows)
        assert len(acts) == 1

    def test_duplicate_scenario_deduplicated(self):
        rows = [
            self._row(10, "S1", "if", "condition"),
            self._row(10, "S1", "if", "condition"),  # doublon
        ]
        conds, _ = _classify_expr_rows(rows)
        assert len(conds) == 1

    def test_same_scenario_in_both_buckets(self):
        rows = [
            self._row(10, "S1", "if", "condition"),
            self._row(10, "S1", "if", "then"),
        ]
        conds, acts = _classify_expr_rows(rows)
        assert len(conds) == 1
        assert len(acts) == 1

    def test_empty_rows_returns_empty(self):
        conds, acts = _classify_expr_rows([])
        assert conds == []
        assert acts == []


# ── run() — fixtures DB mockées ───────────────────────────────────────────────


def _db_ok(rows: list[dict]) -> dict:
    return {"rows": rows, "_filtered_fields": []}


def _db_empty() -> dict:
    return {"rows": [], "_filtered_fields": []}


CMD_ROW = {
    "id": "15663",
    "name": "present",
    "type": "info",
    "subType": "binary",
    "eqLogic_id": "705",
    "eqLogic_name": "Présence Shelly Géraud",
}

TRIGGER_ROW = {"id": "70", "name": "Présence Géraud Shelly"}

EXPR_ROW = {
    "scenario_id": "70",
    "scenario_name": "Présence Géraud Shelly",
    "ss_type": "if",
    "ss_subtype": "condition",
}

EQLOGIC_ROW = {
    "id": "705",
    "name": "Présence Shelly Géraud",
    "eqType_name": "blea",
    "isEnable": "1",
}

SCENARIO_ROW = {
    "id": "5",
    "name": "Absence Geraud",
    "isActive": "1",
    "mode": "provoke",
}

CALLER_ROW = {
    "scenario_id": "4",
    "scenario_name": "Presence Geraud",
}


class TestRunCmd:
    def _make_db_responses(
        self,
        cmd_rows=None,
        trigger_rows=None,
        expr_rows=None,
        code_rows=None,
        ds_rows=None,
    ) -> list:
        # Ordre des appels dans _refs_for_cmd_id :
        # 1. _resolve_cmd → cmd info
        # 2. triggers
        # 3. expr_refs (conditions/actions)
        # 4. datastore_refs
        # 5. code_refs
        return [
            _db_ok(cmd_rows if cmd_rows is not None else [CMD_ROW]),
            _db_ok(trigger_rows if trigger_rows is not None else [TRIGGER_ROW]),
            _db_ok(expr_rows if expr_rows is not None else [EXPR_ROW]),
            _db_ok(ds_rows if ds_rows is not None else []),
            _db_ok(code_rows if code_rows is not None else []),
        ]

    def test_cmd_not_found_returns_error(self):
        with patch("usage_graph._db.run", return_value=_db_empty()):
            result = run("cmd", 99999, creds=MOCK_CREDS)
        assert "error" in result

    def test_cmd_target_fields_populated(self):
        with patch("usage_graph._db.run", side_effect=self._make_db_responses()):
            result = run("cmd", 15663, creds=MOCK_CREDS)
        assert result["target"]["id"] == 15663
        assert result["target"]["name"] == "present"
        assert result["target"]["eqLogic_name"] == "Présence Shelly Géraud"
        assert "error" not in result

    def test_triggers_found(self):
        with patch("usage_graph._db.run", side_effect=self._make_db_responses()):
            result = run("cmd", 15663, creds=MOCK_CREDS)
        assert len(result["references"]["triggers"]) == 1
        assert result["references"]["triggers"][0]["id"] == 70

    def test_conditions_found(self):
        with patch("usage_graph._db.run", side_effect=self._make_db_responses()):
            result = run("cmd", 15663, creds=MOCK_CREDS)
        assert len(result["references"]["conditions"]) == 1

    def test_actions_empty_when_no_action_subtype(self):
        with patch("usage_graph._db.run", side_effect=self._make_db_responses()):
            result = run("cmd", 15663, creds=MOCK_CREDS)
        assert result["references"]["actions"] == []

    def test_code_refs_generate_false_positive_warning(self):
        code_row = {"scenario_id": "30", "scenario_name": "Bureau Geraud"}
        responses = self._make_db_responses(code_rows=[code_row])
        with patch("usage_graph._db.run", side_effect=responses):
            result = run("cmd", 15663, creds=MOCK_CREDS)
        assert len(result["false_positive_warnings"]) == 1
        assert "code" in result["false_positive_warnings"][0]

    def test_datastore_refs_returned(self):
        ds_row = {"id": "42", "name": "presence_geraud", "type": "string"}
        responses = self._make_db_responses(ds_rows=[ds_row])
        with patch("usage_graph._db.run", side_effect=responses):
            result = run("cmd", 15663, creds=MOCK_CREDS)
        assert len(result["references"]["datastore_refs"]) == 1
        assert result["references"]["datastore_refs"][0]["name"] == "presence_geraud"

    def test_no_refs_returns_empty_lists(self):
        responses = self._make_db_responses(
            trigger_rows=[], expr_rows=[], code_rows=[], ds_rows=[]
        )
        with patch("usage_graph._db.run", side_effect=responses):
            result = run("cmd", 15663, creds=MOCK_CREDS)
        refs = result["references"]
        assert refs["triggers"] == []
        assert refs["conditions"] == []
        assert refs["actions"] == []


class TestRunEqLogic:
    def _responses_for_eqlogic(
        self,
        cmd_ids=None,
        trigger_rows=None,
        expr_rows=None,
        code_rows=None,
        ds_rows=None,
    ) -> list:
        """Simule : eqLogic info + cmd_ids + (trigger+expr+code+ds) par cmd."""
        cmd_id_rows = [{"id": str(cid)} for cid in (cmd_ids or [15663])]
        per_cmd = [
            _db_ok(trigger_rows if trigger_rows is not None else [TRIGGER_ROW]),
            _db_ok(expr_rows if expr_rows is not None else [EXPR_ROW]),
            _db_ok(code_rows if code_rows is not None else []),
            _db_ok(ds_rows if ds_rows is not None else []),
        ]
        return [_db_ok([EQLOGIC_ROW]), _db_ok(cmd_id_rows)] + per_cmd

    def test_eqlogic_not_found_returns_error(self):
        with patch("usage_graph._db.run", return_value=_db_empty()):
            result = run("eqLogic", 99999, creds=MOCK_CREDS)
        assert "error" in result

    def test_eqlogic_target_fields(self):
        with patch("usage_graph._db.run", side_effect=self._responses_for_eqlogic()):
            result = run("eqLogic", 705, creds=MOCK_CREDS)
        assert result["target"]["id"] == 705
        assert result["target"]["plugin"] == "blea"

    def test_eqlogic_aggregates_cmd_refs(self):
        with patch("usage_graph._db.run", side_effect=self._responses_for_eqlogic()):
            result = run("eqLogic", 705, creds=MOCK_CREDS)
        assert len(result["references"]["triggers"]) == 1

    def test_eqlogic_deduplicates_scenario_refs_across_cmds(self):
        # Deux cmds référencent le même scénario → une seule entrée dans triggers
        cmd_id_rows = [{"id": "100"}, {"id": "101"}]
        responses = (
            [_db_ok([EQLOGIC_ROW]), _db_ok(cmd_id_rows)]
            # cmd 100
            + [
                _db_ok([TRIGGER_ROW]),
                _db_ok([EXPR_ROW]),
                _db_ok([]),
                _db_ok([]),
            ]
            # cmd 101 — même trigger
            + [
                _db_ok([TRIGGER_ROW]),
                _db_ok([]),
                _db_ok([]),
                _db_ok([]),
            ]
        )
        with patch("usage_graph._db.run", side_effect=responses):
            result = run("eqLogic", 705, creds=MOCK_CREDS)
        assert len(result["references"]["triggers"]) == 1


class TestRunScenario:
    def _responses_for_scenario(self, caller_rows=None) -> list:
        return [
            _db_ok([SCENARIO_ROW]),
            _db_ok(caller_rows if caller_rows is not None else [CALLER_ROW]),
        ]

    def test_scenario_not_found_returns_error(self):
        with patch("usage_graph._db.run", return_value=_db_empty()):
            result = run("scenario", 99999, creds=MOCK_CREDS)
        assert "error" in result

    def test_scenario_target_fields(self):
        with patch("usage_graph._db.run", side_effect=self._responses_for_scenario()):
            result = run("scenario", 5, creds=MOCK_CREDS)
        assert result["target"]["id"] == 5
        assert result["target"]["name"] == "Absence Geraud"

    def test_scenario_callers_returned(self):
        with patch("usage_graph._db.run", side_effect=self._responses_for_scenario()):
            result = run("scenario", 5, creds=MOCK_CREDS)
        assert len(result["references"]["scenario_calls"]) == 1
        assert result["references"]["scenario_calls"][0]["id"] == 4

    def test_scenario_no_callers(self):
        with patch("usage_graph._db.run", side_effect=self._responses_for_scenario(caller_rows=[])):
            result = run("scenario", 5, creds=MOCK_CREDS)
        assert result["references"]["scenario_calls"] == []


class TestRunInvalidType:
    def test_unknown_target_type_returns_error(self):
        result = run("plugin", 42, creds=MOCK_CREDS)
        assert "error" in result
        assert "target_type" in result["error"]
