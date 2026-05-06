# Brief jalon M3 — WF Scénarios

**Branche** : `develop`
**Pré-requis** : M2 terminé (fichiers supprimés, SKILL.md §3/§6/§9 mis à jour)
**Référence** : `docs/state/migration-jeedom-audit-brief.md` §4 (WF2, WF5, WF12, WF13)

## Contexte

Migrer les 4 workflows centrés sur les scénarios. Ces WF partagent les mêmes
outils Holmes MCP (`describe_scenario`, `get_scenario_structure`, `get_scenario_log`).
Après chaque mise à jour SKILL.md, tester le WF sur la box réelle avec Holmes MCP
connecté (`.mcp.json` configuré avec le token réel) et documenter le résultat Phase 1.

**Holmes MCP doit être actif sur la box pendant ces sous-sessions.**

Le document Phase 1 à compléter : `docs/sessions/2026-05-06-M0-baseline.md`
(même fichier que le baseline M0 — colonne "Phase 1 (après)" à remplir).

## Outils Holmes MCP impliqués

| Outil | Usage |
|---|---|
| `holmes__get_scenario(scenario_id)` | État + lastLaunch + state |
| `holmes__get_scenario_structure(scenario_id, max_depth=3, follow_scenario_calls=N)` | Arbre du scénario |
| `holmes__describe_scenario(scenario_id)` | Description LLM-friendly + résolution `#[O][E][C]#` intégrée |
| `holmes__find_scenarios_advanced(name_contains=...)` | Recherche par nom |
| `holmes__get_scenario_log(scenario_id, lines=100)` | Dernières lignes du log |
| `holmes__find_scenario_dependencies(scenario_id)` | Graphe de dépendances |

---

## M3-1 — WF2 + WF5

### SKILL.md §7 WF2 — Diagnostic scénario

Remplacer la ligne `**Scripts** :` et ses références par :

```
**Outils Holmes MCP** : `find_scenarios_advanced()`, `get_scenario()`,
`get_scenario_structure()`, `describe_scenario()`, `get_scenario_log()`
```

Remplacer dans le corps du WF :
- `db_query.run("SELECT ... FROM scenario WHERE name LIKE ?")` → `holmes__find_scenarios_advanced(name_contains=...)`
- `scenario_tree_walker.py` → `holmes__get_scenario_structure(scenario_id, follow_scenario_calls=0)`
- `api_call.run("scenario::byId")` → `holmes__get_scenario(scenario_id)` (inclut `lastLaunch` + `state`)
- `logs_query.py tail scenarioLog/N` → `holmes__get_scenario_log(scenario_id, lines=100)`
- `resolve_cmd_refs.py` → `holmes__describe_scenario(scenario_id)` (résolution intégrée)

### SKILL.md §7 WF5 — Explication scénario

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `describe_scenario()`, `get_scenario_structure()`
```

Remplacer dans le corps :
- `scenario_tree_walker.py` + `resolve_cmd_refs.py` → `holmes__describe_scenario(scenario_id)` (remplace les deux en une passe)
- `scenario_tree_walker.py follow_scenario_calls=2` → `holmes__get_scenario_structure(scenario_id, follow_scenario_calls=2)`

Ajouter note : `describe_scenario()` résout les références `#[O][E][C]#` en une seule passe
(vs l'ancien pipeline walker → refs en deux passes). Le formatage des nœuds imbriqués
peut différer légèrement — c'est attendu, pas une régression.

### Test WF2 + WF5

Exécuter les prompts correspondants du tableau baseline avec Holmes MCP connecté.
Remplir les colonnes "Phase 1" dans `docs/sessions/2026-05-06-M0-baseline.md`.

**Gate qualité M3-1** :
- SKILL.md §7 WF2 et WF5 : aucune référence à `scenario_tree_walker`, `resolve_cmd_refs`, `logs_query`, `db_query`
- WF2 et WF5 testés, verdicts notés dans le tableau Phase 1

---

## M3-2 — WF12 + WF13

### SKILL.md §7 WF12 — Cartographie d'orchestration

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `get_scenario_structure()`, `describe_scenario()`
```

Remplacer dans le corps :
- `scenario_tree_walker.py follow_scenario_calls=3` → `holmes__get_scenario_structure(scenario_id, follow_scenario_calls=3)`
- `resolve_cmd_refs.py` sur annotations → `holmes__describe_scenario(scenario_id)`

### SKILL.md §7 WF13 — Forensique causale

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `find_scenario_dependencies()`, `tail_log()`, `get_command_history()`
```

Remplacer dans le corps :
- `usage_graph.py` → `holmes__find_scenario_dependencies(scenario_id)`
- `logs_query.py` sur fenêtre temporelle → `holmes__tail_log(log_name=..., lines=500, grep=...)`
- `api_call.run("cmd::getHistory")` → `holmes__get_command_history(cmd_id)`

### Test WF12 + WF13

Exécuter les prompts du tableau baseline. Remplir colonnes Phase 1.

**Gate qualité M3-2** :
- SKILL.md §7 WF12 et WF13 : aucune référence aux anciens scripts
- WF12 et WF13 testés, verdicts notés

---

## DoD — Jalon M3

- [ ] SKILL.md §7 WF2 mis à jour — outils Holmes MCP, sans référence aux scripts supprimés
- [ ] SKILL.md §7 WF5 mis à jour — note comportement `describe_scenario()` présente
- [ ] SKILL.md §7 WF12 mis à jour
- [ ] SKILL.md §7 WF13 mis à jour
- [ ] WF2, WF5, WF12, WF13 testés avec Holmes MCP — verdicts Phase 1 notés
- [ ] Aucun ⚠️ ou ❌ non documenté dans le tableau Phase 1
