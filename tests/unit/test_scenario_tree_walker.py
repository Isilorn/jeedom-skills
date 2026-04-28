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

    def test_extract_scenario_call_id_returns_id_for_start(self):
        expr = {"type": "action", "expression": "scenario", "options": '{"scenario_id": "5", "action": "start"}'}
        assert stw._extract_scenario_call_id(expr) == 5

    def test_extract_scenario_call_id_ignores_stop(self):
        expr = {"type": "action", "expression": "scenario", "options": '{"scenario_id": "5", "action": "stop"}'}
        assert stw._extract_scenario_call_id(expr) is None

    def test_extract_scenario_call_id_ignores_non_scenario_action(self):
        expr = {"type": "action", "expression": "#15670#", "options": "{}"}
        assert stw._extract_scenario_call_id(expr) is None

    def test_extract_scenario_call_id_ignores_condition_type(self):
        expr = {"type": "condition", "expression": "scenario", "options": '{"scenario_id": "5"}'}
        assert stw._extract_scenario_call_id(expr) is None

    def test_extract_scenario_call_id_handles_invalid_options(self):
        expr = {"type": "action", "expression": "scenario", "options": "not_json"}
        assert stw._extract_scenario_call_id(expr) is None

    def test_extract_scenario_call_id_handles_missing_scenario_id(self):
        expr = {"type": "action", "expression": "scenario", "options": '{"action": "start"}'}
        assert stw._extract_scenario_call_id(expr) is None


# ── follow_scenario_calls ──────────────────────────────────────────────────────

def _scenario_call_expr_row(element_id, sub_id, expr_id, called_scenario_id, order=1):
    """Expression de type action/scenario (appel de scénario)."""
    opts = json.dumps({"scenario_id": str(called_scenario_id), "action": "start"})
    return _expr_row(element_id, sub_id, "if", "then", expr_id, order, "action", "scenario", opts)


class TestFollowScenarioCalls:
    """Tests du mode follow_scenario_calls."""

    def _make_simple_subtree_rows(self, element_id=20, sub_id=30):
        """Arbre minimal pour le scénario appelé."""
        return [_expr_row(element_id, sub_id, "if", "condition", 99, 1, "condition", "#ID# == 1")]

    def test_follow_disabled_by_default(self):
        """Sans follow_scenario_calls, les appels de scénario ne sont pas suivis."""
        rows = SIMPLE_TREE_ROWS + [_scenario_call_expr_row(8, 13, 50, called_scenario_id=5)]

        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=rows):
            result = stw.walk(70, creds=MOCK_CREDS)

        then_sub = next(s for s in result["tree"][0]["sub_elements"] if s["sub_id"] == 13)
        scenario_expr = next(e for e in then_sub["expressions"] if e["expression"] == "scenario")
        assert "called_scenario_tree" not in scenario_expr

    def test_follow_one_level_embeds_subtree(self):
        """follow_scenario_calls=1 : l'appel de scénario est résolu et embarqué."""
        parent_rows = SIMPLE_TREE_ROWS + [_scenario_call_expr_row(8, 13, 50, called_scenario_id=5)]
        child_scenario = _scenario_row(scenario_id=5, element_ids=[20])
        child_tree_rows = self._make_simple_subtree_rows()

        def fetch_scenario_side(scenario_id, creds):
            if scenario_id == 70:
                return _scenario_row(element_ids=[8])
            if scenario_id == 5:
                return child_scenario
            return None

        def fetch_elements_side(element_ids, creds):
            if set(element_ids) == {8}:
                return parent_rows
            if set(element_ids) == {20}:
                return child_tree_rows
            return []

        with patch("scenario_tree_walker._fetch_scenario", side_effect=fetch_scenario_side), \
             patch("scenario_tree_walker._fetch_elements", side_effect=fetch_elements_side):
            result = stw.walk(70, follow_scenario_calls=1, creds=MOCK_CREDS)

        then_sub = next(s for s in result["tree"][0]["sub_elements"] if s["sub_id"] == 13)
        scenario_expr = next(e for e in then_sub["expressions"] if e["expression"] == "scenario")
        assert "called_scenario_tree" in scenario_expr
        subtree = scenario_expr["called_scenario_tree"]
        assert subtree["scenario"]["id"] == 5
        assert len(subtree["tree"]) == 1

    def test_follow_depth_decrements(self):
        """follow_scenario_calls=1 → le scénario appelé ne suit pas ses propres appels."""
        parent_rows = SIMPLE_TREE_ROWS + [_scenario_call_expr_row(8, 13, 50, called_scenario_id=5)]
        child_rows = self._make_simple_subtree_rows() + [_scenario_call_expr_row(20, 30, 60, called_scenario_id=7)]

        def fetch_scenario_side(scenario_id, creds):
            if scenario_id == 70:
                return _scenario_row(element_ids=[8])
            if scenario_id == 5:
                return _scenario_row(scenario_id=5, element_ids=[20])
            return None

        def fetch_elements_side(element_ids, creds):
            if set(element_ids) == {8}:
                return parent_rows
            if set(element_ids) == {20}:
                return child_rows
            return []

        with patch("scenario_tree_walker._fetch_scenario", side_effect=fetch_scenario_side), \
             patch("scenario_tree_walker._fetch_elements", side_effect=fetch_elements_side):
            result = stw.walk(70, follow_scenario_calls=1, creds=MOCK_CREDS)

        then_sub = next(s for s in result["tree"][0]["sub_elements"] if s["sub_id"] == 13)
        scenario_expr = next(e for e in then_sub["expressions"] if e["expression"] == "scenario")
        child_subtree = scenario_expr["called_scenario_tree"]
        # Le scénario 5 a un appel vers 7, mais follow=0 pour lui → pas embarqué
        child_then = next(s for s in child_subtree["tree"][0]["sub_elements"] if s["sub_id"] == 30)
        inner_expr = next(e for e in child_then["expressions"] if e["expression"] == "scenario")
        assert "called_scenario_tree" not in inner_expr

    def test_anti_cycle_direct(self):
        """Un scénario qui s'appelle lui-même ne boucle pas."""
        rows = SIMPLE_TREE_ROWS + [_scenario_call_expr_row(8, 13, 50, called_scenario_id=70)]

        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=rows):
            result = stw.walk(70, follow_scenario_calls=3, creds=MOCK_CREDS)

        then_sub = next(s for s in result["tree"][0]["sub_elements"] if s["sub_id"] == 13)
        scenario_expr = next(e for e in then_sub["expressions"] if e["expression"] == "scenario")
        assert "called_scenario_tree" in scenario_expr
        assert "warning" in scenario_expr["called_scenario_tree"]
        assert "cycle" in scenario_expr["called_scenario_tree"]["warning"]

    def test_anti_cycle_indirect(self):
        """Cycle indirect A→B→A détecté correctement."""
        rows_a = SIMPLE_TREE_ROWS + [_scenario_call_expr_row(8, 13, 50, called_scenario_id=5)]
        rows_b = [
            _expr_row(20, 30, "if", "condition", 70, 1, "condition", "#X# == 1"),
            _scenario_call_expr_row(20, 31, 71, called_scenario_id=70),  # B→A (cycle)
        ]

        def fetch_scenario_side(scenario_id, creds):
            if scenario_id == 70:
                return _scenario_row(element_ids=[8])
            if scenario_id == 5:
                return _scenario_row(scenario_id=5, element_ids=[20])
            return None

        def fetch_elements_side(element_ids, creds):
            if set(element_ids) == {8}:
                return rows_a
            if set(element_ids) == {20}:
                return rows_b
            return []

        with patch("scenario_tree_walker._fetch_scenario", side_effect=fetch_scenario_side), \
             patch("scenario_tree_walker._fetch_elements", side_effect=fetch_elements_side):
            result = stw.walk(70, follow_scenario_calls=3, creds=MOCK_CREDS)

        then_sub = next(s for s in result["tree"][0]["sub_elements"] if s["sub_id"] == 13)
        scenario_expr = next(e for e in then_sub["expressions"] if e["expression"] == "scenario")
        child_subtree = scenario_expr["called_scenario_tree"]
        child_then = next(s for s in child_subtree["tree"][0]["sub_elements"] if s["sub_id"] == 31)
        back_expr = next(e for e in child_then["expressions"] if e["expression"] == "scenario")
        assert "called_scenario_tree" in back_expr
        assert "warning" in back_expr["called_scenario_tree"]
        assert "cycle" in back_expr["called_scenario_tree"]["warning"]

    def test_called_scenario_not_found_returns_error(self):
        """Scénario appelé introuvable → erreur embarquée dans called_scenario_tree."""
        rows = SIMPLE_TREE_ROWS + [_scenario_call_expr_row(8, 13, 50, called_scenario_id=999)]

        def fetch_scenario_side(scenario_id, creds):
            if scenario_id == 70:
                return _scenario_row(element_ids=[8])
            return None  # 999 introuvable

        with patch("scenario_tree_walker._fetch_scenario", side_effect=fetch_scenario_side), \
             patch("scenario_tree_walker._fetch_elements", return_value=rows):
            result = stw.walk(70, follow_scenario_calls=1, creds=MOCK_CREDS)

        then_sub = next(s for s in result["tree"][0]["sub_elements"] if s["sub_id"] == 13)
        scenario_expr = next(e for e in then_sub["expressions"] if e["expression"] == "scenario")
        assert "error" in scenario_expr["called_scenario_tree"]

    def test_multiple_scenario_calls_in_same_block(self):
        """Plusieurs appels dans le même bloc sont tous suivis."""
        call_rows = [
            _scenario_call_expr_row(8, 13, 50, called_scenario_id=5, order=1),
            _scenario_call_expr_row(8, 13, 51, called_scenario_id=6, order=2),
        ]
        rows_root = [_expr_row(8, 12, "if", "condition", 1, 1, "condition", "#X# == 1")] + call_rows
        rows_child5 = [_expr_row(20, 99, "if", "condition", 88, 1, "condition", "#Y# == 1")]
        rows_child6 = [_expr_row(21, 98, "if", "condition", 87, 1, "condition", "#Z# == 1")]

        def fetch_scenario_side(scenario_id, creds):
            if scenario_id == 70:
                return _scenario_row(scenario_id=70, element_ids=[8])
            if scenario_id == 5:
                return _scenario_row(scenario_id=5, element_ids=[20])
            if scenario_id == 6:
                return _scenario_row(scenario_id=6, element_ids=[21])
            return None

        def fetch_elements_side(element_ids, creds):
            if set(element_ids) == {8}:
                return rows_root
            if set(element_ids) == {20}:
                return rows_child5
            if set(element_ids) == {21}:
                return rows_child6
            return []

        with patch("scenario_tree_walker._fetch_scenario", side_effect=fetch_scenario_side), \
             patch("scenario_tree_walker._fetch_elements", side_effect=fetch_elements_side):
            result = stw.walk(70, follow_scenario_calls=1, creds=MOCK_CREDS)

        then_sub = next(s for s in result["tree"][0]["sub_elements"] if s["sub_id"] == 13)
        call_exprs = [e for e in then_sub["expressions"] if e["expression"] == "scenario"]
        assert all("called_scenario_tree" in e for e in call_exprs)
        called_ids = {e["called_scenario_tree"]["scenario"]["id"] for e in call_exprs}
        assert called_ids == {5, 6}

    def test_follow_zero_is_same_as_disabled(self):
        """follow_scenario_calls=0 est identique au comportement par défaut."""
        rows = SIMPLE_TREE_ROWS + [_scenario_call_expr_row(8, 13, 50, called_scenario_id=5)]

        with patch("scenario_tree_walker._fetch_scenario", return_value=_scenario_row(element_ids=[8])), \
             patch("scenario_tree_walker._fetch_elements", return_value=rows):
            result = stw.walk(70, follow_scenario_calls=0, creds=MOCK_CREDS)

        then_sub = next(s for s in result["tree"][0]["sub_elements"] if s["sub_id"] == 13)
        scenario_expr = next(e for e in then_sub["expressions"] if e["expression"] == "scenario")
        assert "called_scenario_tree" not in scenario_expr
