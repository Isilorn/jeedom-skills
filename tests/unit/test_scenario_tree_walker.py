"""Tests unitaires pour scripts/scenario_tree_walker.py."""

import json
import sys
from pathlib import Path
from unittest.mock import patch, call

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "jeedom-audit" / "scripts"))

import scenario_tree_walker as stw

MOCK_CREDS = {"ssh_alias": "Jeedom", "db_name": "jeedom"}


# ── Fixtures de données ────────────────────────────────────────────────────────

def _scenario_row(scenario_id=70, element_ids=None):
    """Row SQL simulant un scénario."""
    return {
        "id": str(scenario_id),
        "name": "Test scénario",
        "isActive": "1",
        "mode": "provoke",
        "trigger": '["#15663#"]',
        "scenarioElement": json.dumps(element_ids if element_ids is not None else [8]),
        "description": "",
        "timeout": "0",
    }


def _expr_row(element_id, sub_id, ss_type, ss_subtype, expr_id, order, expr_type, expression, options="{}"):
    return {
        "element_id": str(element_id),
        "sub_id": str(sub_id),
        "ss_type": ss_type,
        "ss_subtype": ss_subtype,
        "expr_id": str(expr_id),
        "expr_order": str(order),
        "expr_type": expr_type,
        "expression": expression,
        "options": options,
    }


SIMPLE_TREE_ROWS = [
    # Element 8, sub 12 (condition IF), expr condition
    _expr_row(8, 12, "if", "condition", 1, 1, "condition", "#15663# == 1"),
    # Element 8, sub 13 (then), expr action
    _expr_row(8, 13, "if", "then", 2, 1, "action", "#15670#"),
    # Element 8, sub 14 (else), expr action
    _expr_row(8, 14, "if", "else", 3, 1, "action", "#15671#"),
]


# ── Scénario introuvable ───────────────────────────────────────────────────────

class TestScenarioNotFound:
    def test_unknown_scenario_returns_error(self):
        with patch("scenario_tree_walker._fetch_scenario", return_value=None):
            result = stw.walk(9999, creds=MOCK_CREDS)
        assert "error" in result
        assert result["scenario"] is None
        assert result["tree"] == []


# ── Scénario simple (1 niveau) ─────────────────────────────────────────────────

class TestSimpleScenario:
    def test_single_element_returned(self):
        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=SIMPLE_TREE_ROWS):
            result = stw.walk(70, creds=MOCK_CREDS)

        assert result["scenario"]["id"] == 70
        assert result["scenario"]["name"] == "Test scénario"
        assert len(result["tree"]) == 1
        assert result["tree"][0]["element_id"] == 8
        assert result["tree"][0]["depth"] == 0

    def test_sub_elements_grouped_correctly(self):
        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=SIMPLE_TREE_ROWS):
            result = stw.walk(70, creds=MOCK_CREDS)

        sub_ids = [s["sub_id"] for s in result["tree"][0]["sub_elements"]]
        assert sub_ids == [12, 13, 14]

    def test_expressions_in_sub_elements(self):
        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=SIMPLE_TREE_ROWS):
            result = stw.walk(70, creds=MOCK_CREDS)

        condition_sub = result["tree"][0]["sub_elements"][0]
        assert condition_sub["ss_type"] == "if"
        assert condition_sub["ss_subtype"] == "condition"
        assert condition_sub["expressions"][0]["expression"] == "#15663# == 1"

    def test_no_children_key_when_no_sub_elements(self):
        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=SIMPLE_TREE_ROWS):
            result = stw.walk(70, creds=MOCK_CREDS)

        # Pas d'expression type 'element' → pas de clé 'children'
        assert "children" not in result["tree"][0]

    def test_not_truncated_for_simple_scenario(self):
        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=SIMPLE_TREE_ROWS):
            result = stw.walk(70, creds=MOCK_CREDS)
        assert result["truncated"] is False
        assert result["warnings"] == []


# ── Récursion et anti-cycle ────────────────────────────────────────────────────

class TestRecursion:
    def _make_element_expr_row(self, element_id, sub_id, child_id):
        """Crée une expression de type 'element' qui pointe vers un enfant."""
        return _expr_row(element_id, sub_id, "if", "else", 99, 2, "element", str(child_id))

    def test_child_element_discovered_at_depth_1(self):
        parent_rows = SIMPLE_TREE_ROWS + [
            self._make_element_expr_row(8, 14, 9)  # else → element 9
        ]
        child_rows = [
            _expr_row(9, 20, "if", "condition", 10, 1, "condition", "#15669# == 0"),
        ]

        def fetch_side(element_ids, creds):
            if set(element_ids) == {8}:
                return parent_rows
            if set(element_ids) == {9}:
                return child_rows
            return []

        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", side_effect=fetch_side):
            result = stw.walk(70, max_depth=3, creds=MOCK_CREDS)

        root = result["tree"][0]
        assert "children" in root
        assert root["children"][0]["element_id"] == 9
        assert root["children"][0]["depth"] == 1

    def test_anti_cycle_prevents_infinite_loop(self):
        """Un element qui pointe sur lui-même ne boucle pas."""
        cycle_rows = SIMPLE_TREE_ROWS + [
            self._make_element_expr_row(8, 14, 8)  # else → element 8 (cycle!)
        ]

        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=cycle_rows):
            result = stw.walk(70, max_depth=3, creds=MOCK_CREDS)

        # Doit terminer sans boucle infinie et ne pas avoir de children
        # (8 est déjà visité donc ignoré)
        assert result["tree"] is not None

    def test_max_depth_respected(self):
        """À max_depth=0, pas de récursion possible — un seul niveau."""
        parent_with_child = SIMPLE_TREE_ROWS + [
            self._make_element_expr_row(8, 14, 9)
        ]

        fetch_calls = []

        def tracking_fetch(element_ids, creds):
            fetch_calls.append(sorted(element_ids))
            return parent_with_child if element_ids == [8] else []

        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", side_effect=tracking_fetch):
            result = stw.walk(70, max_depth=0, creds=MOCK_CREDS)

        # Seul l'élément 8 est fetché (depth=0 = max)
        assert [8] in fetch_calls
        assert [9] not in fetch_calls


# ── Troncature ────────────────────────────────────────────────────────────────

class TestTruncation:
    def test_truncation_when_too_many_sub_elements(self):
        many_rows = [
            _expr_row(8, sub_id, "if", "condition", sub_id, 1, "condition", f"#ID{sub_id}# == 1")
            for sub_id in range(1, 110)  # 109 sous-éléments
        ]

        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=many_rows):
            result = stw.walk(70, creds=MOCK_CREDS)

        assert result["truncated"] is True
        assert len(result["tree"][0]["sub_elements"]) == stw.MAX_SUB_ELEMENTS
        assert any("tronqué" in w for w in result["warnings"])


# ── scenarioElement vide ou invalide ──────────────────────────────────────────

class TestEdgeCases:
    def test_empty_scenario_element_returns_empty_tree(self):
        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[])), \
             patch("scenario_tree_walker._fetch_elements", return_value=[]) as mock_fetch:
            result = stw.walk(70, creds=MOCK_CREDS)

        mock_fetch.assert_not_called()
        assert result["tree"] == []

    def test_scenario_metadata_in_output(self):
        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=SIMPLE_TREE_ROWS):
            result = stw.walk(70, creds=MOCK_CREDS)

        sc = result["scenario"]
        assert sc["mode"] == "provoke"
        assert sc["trigger"] == '["#15663#"]'
        assert sc["isActive"] == "1"

    def test_multiple_root_elements(self):
        rows_el8 = [_expr_row(8, 12, "if", "condition", 1, 1, "condition", "#A# == 1")]
        rows_el9 = [_expr_row(9, 20, "if", "condition", 2, 1, "condition", "#B# == 0")]

        def fetch_side(element_ids, creds):
            result = []
            if 8 in element_ids:
                result += rows_el8
            if 9 in element_ids:
                result += rows_el9
            return result

        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8, 9])), \
             patch("scenario_tree_walker._fetch_elements", side_effect=fetch_side):
            result = stw.walk(70, creds=MOCK_CREDS)

        assert len(result["tree"]) == 2
        assert {n["element_id"] for n in result["tree"]} == {8, 9}


# ── Helpers internes ──────────────────────────────────────────────────────────

class TestHelpers:
    def test_child_element_ids_extracted(self):
        rows = [
            {"expr_type": "condition", "expression": "#15663# == 1"},
            {"expr_type": "element", "expression": "511"},
            {"expr_type": "action", "expression": "#15670#"},
            {"expr_type": "element", "expression": "512"},
        ]
        assert sorted(stw._child_element_ids(rows)) == [511, 512]

    def test_child_element_ids_ignores_non_numeric(self):
        rows = [{"expr_type": "element", "expression": "not_a_number"}]
        assert stw._child_element_ids(rows) == []

    def test_group_by_element_orders_subs(self):
        rows = [
            _expr_row(8, 14, "if", "else", 3, 1, "action", "#A#"),
            _expr_row(8, 12, "if", "condition", 1, 1, "condition", "#B#"),
            _expr_row(8, 13, "if", "then", 2, 1, "action", "#C#"),
        ]
        grouped = stw._group_by_element(rows)
        sub_ids = [s["sub_id"] for s in grouped[8]]
        assert sub_ids == [12, 13, 14]
