"""Tests unitaires pour scripts/resolve_cmd_refs.py."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "jeedom-audit" / "scripts"))

import resolve_cmd_refs as rcr

MOCK_CREDS = {"ssh_alias": "Jeedom", "db_name": "jeedom"}

DB_ROWS = [
    {"id": "15663", "objet": "Maison", "equipement": "Présence Géraud", "commande": "BLE présent"},
    {"id": "15669", "objet": "Maison", "equipement": "NUT Virtuel", "commande": "ON"},
    {"id": "15670", "objet": "Maison", "equipement": "NUT Virtuel", "commande": "OFF"},
]


def _mock_db(rows=None):
    return {"rows": rows if rows is not None else DB_ROWS, "_filtered_fields": []}


@pytest.fixture(autouse=True)
def clear_session_cache():
    rcr.clear_cache()
    yield
    rcr.clear_cache()


# ── Résolution basique ─────────────────────────────────────────────────────────

class TestResolveBasic:
    def test_single_id_resolved(self):
        with patch("resolve_cmd_refs._fetch_names", return_value={15663: "[Maison][Présence Géraud][BLE présent]"}):
            result = rcr.resolve("#15663#", creds=MOCK_CREDS)
        assert result["resolved"] == "#[Maison][Présence Géraud][BLE présent]#"
        assert result["mapping"] == {"15663": "[Maison][Présence Géraud][BLE présent]"}
        assert result["unresolved"] == []

    def test_multiple_ids_resolved_in_one_pass(self):
        fetched = {
            15663: "[Maison][Présence Géraud][BLE présent]",
            15669: "[Maison][NUT Virtuel][ON]",
        }
        with patch("resolve_cmd_refs._fetch_names", return_value=fetched) as mock_fetch:
            result = rcr.resolve("Si #15663# == 1 alors #15669#", creds=MOCK_CREDS)
        mock_fetch.assert_called_once()
        assert "#[Maison][Présence Géraud][BLE présent]#" in result["resolved"]
        assert "#[Maison][NUT Virtuel][ON]#" in result["resolved"]

    def test_duplicate_id_resolved_once(self):
        fetched = {15663: "[Maison][Présence Géraud][BLE présent]"}
        call_count = []

        def counting_fetch(ids, creds):
            call_count.append(ids)
            return fetched

        with patch("resolve_cmd_refs._fetch_names", side_effect=counting_fetch):
            result = rcr.resolve("#15663# == 1 || #15663# == 0", creds=MOCK_CREDS)

        assert len(call_count) == 1
        assert result["resolved"].count("#[Maison][Présence Géraud][BLE présent]#") == 2

    def test_text_without_ids_unchanged(self):
        with patch("resolve_cmd_refs._fetch_names", return_value={}) as mock_fetch:
            result = rcr.resolve("Aucun identifiant ici", creds=MOCK_CREDS)
        mock_fetch.assert_not_called()
        assert result["resolved"] == "Aucun identifiant ici"
        assert result["mapping"] == {}
        assert result["unresolved"] == []


# ── IDs non résolus ────────────────────────────────────────────────────────────

class TestUnresolved:
    def test_unknown_id_marked_as_unresolved(self):
        with patch("resolve_cmd_refs._fetch_names", return_value={}):
            result = rcr.resolve("#99999#", creds=MOCK_CREDS)
        assert result["resolved"] == "#ID_NON_RÉSOLU:99999#"
        assert result["unresolved"] == [99999]
        assert result["mapping"] == {}

    def test_mixed_resolved_and_unresolved(self):
        with patch("resolve_cmd_refs._fetch_names", return_value={15663: "[M][EQ][CMD]"}):
            result = rcr.resolve("#15663# et #99999#", creds=MOCK_CREDS)
        assert "#[M][EQ][CMD]#" in result["resolved"]
        assert "#ID_NON_RÉSOLU:99999#" in result["resolved"]
        assert 99999 in result["unresolved"]
        assert "15663" in result["mapping"]


# ── Tags système Jeedom ────────────────────────────────────────────────────────

class TestSystemTags:
    def test_system_tags_not_matched_by_numeric_pattern(self):
        """Les tags système comme #trigger_id# ne contiennent pas que des chiffres."""
        with patch("resolve_cmd_refs._fetch_names", return_value={}) as mock_fetch:
            result = rcr.resolve("#trigger_id# == 1", creds=MOCK_CREDS)
        mock_fetch.assert_not_called()
        assert "#trigger_id#" in result["resolved"]

    def test_system_tags_preserved_alongside_numeric_ids(self):
        with patch("resolve_cmd_refs._fetch_names", return_value={15663: "[M][EQ][CMD]"}):
            result = rcr.resolve("Si #15663# == #trigger_value#", creds=MOCK_CREDS)
        assert "#trigger_value#" in result["resolved"]
        assert "#[M][EQ][CMD]#" in result["resolved"]


# ── Cache de session ───────────────────────────────────────────────────────────

class TestSessionCache:
    def test_second_call_uses_cache(self):
        fetched = {15663: "[M][EQ][CMD]"}
        call_count = []

        def counting_fetch(ids, creds):
            call_count.append(ids)
            return fetched

        with patch("resolve_cmd_refs._fetch_names", side_effect=counting_fetch):
            rcr.resolve("#15663#", creds=MOCK_CREDS)
            rcr.resolve("#15663#", creds=MOCK_CREDS)

        assert len(call_count) == 1

    def test_clear_cache_forces_refetch(self):
        fetched = {15663: "[M][EQ][CMD]"}
        call_count = []

        def counting_fetch(ids, creds):
            call_count.append(ids)
            return fetched

        with patch("resolve_cmd_refs._fetch_names", side_effect=counting_fetch):
            rcr.resolve("#15663#", creds=MOCK_CREDS)
            rcr.clear_cache()
            rcr.resolve("#15663#", creds=MOCK_CREDS)

        assert len(call_count) == 2

    def test_partial_cache_hit_fetches_only_missing(self):
        fetched_calls = []

        def tracking_fetch(ids, creds):
            fetched_calls.append(sorted(ids))
            return {i: f"[O][E][{i}]" for i in ids}

        with patch("resolve_cmd_refs._fetch_names", side_effect=tracking_fetch):
            rcr.resolve("#15663#", creds=MOCK_CREDS)
            rcr.resolve("#15663# et #15669#", creds=MOCK_CREDS)

        assert fetched_calls[0] == [15663]
        assert fetched_calls[1] == [15669]


# ── Format de sortie ───────────────────────────────────────────────────────────

class TestOutputFormat:
    def test_missing_object_name_handled(self):
        """Équipement sans pièce assignée — objet vide mais pas d'erreur."""
        with patch("resolve_cmd_refs._fetch_names", return_value={15663: "[][EQ][CMD]"}):
            result = rcr.resolve("#15663#", creds=MOCK_CREDS)
        assert "#[][EQ][CMD]#" in result["resolved"]

    def test_mapping_keys_are_strings(self):
        with patch("resolve_cmd_refs._fetch_names", return_value={15663: "[M][EQ][CMD]"}):
            result = rcr.resolve("#15663#", creds=MOCK_CREDS)
        assert all(isinstance(k, str) for k in result["mapping"].keys())

    def test_unresolved_sorted(self):
        with patch("resolve_cmd_refs._fetch_names", return_value={}):
            result = rcr.resolve("#300# #100# #200#", creds=MOCK_CREDS)
        assert result["unresolved"] == [100, 200, 300]


# ── Intégration avec _fetch_names (SQL mocké) ──────────────────────────────────

class TestFetchNames:
    def test_fetch_names_builds_labels(self):
        mock_result = {"rows": DB_ROWS, "_filtered_fields": []}
        with patch("db_query.run", return_value=mock_result):
            mapping = rcr._fetch_names([15663, 15669, 15670], MOCK_CREDS)
        assert mapping[15663] == "[Maison][Présence Géraud][BLE présent]"
        assert mapping[15669] == "[Maison][NUT Virtuel][ON]"
        assert mapping[15670] == "[Maison][NUT Virtuel][OFF]"

    def test_fetch_names_empty_list(self):
        with patch("db_query.run") as mock_run:
            mapping = rcr._fetch_names([], MOCK_CREDS)
        mock_run.assert_not_called()
        assert mapping == {}

    def test_fetch_names_null_object(self):
        rows_no_object = [{"id": "15663", "objet": None, "equipement": "EQ", "commande": "CMD"}]
        mock_result = {"rows": rows_no_object, "_filtered_fields": []}
        with patch("db_query.run", return_value=mock_result):
            mapping = rcr._fetch_names([15663], MOCK_CREDS)
        assert mapping[15663] == "[][EQ][CMD]"
