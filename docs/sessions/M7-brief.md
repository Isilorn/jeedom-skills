# Brief jalon M7 — WF Graphe d'usage

**Branche** : `develop`
**Pré-requis** : M2 terminé (indépendant de M3, M4, M5, M6)
**Référence** : `docs/state/migration-jeedom-audit-brief.md` §4 (WF6), checklist §9

## Contexte

WF6 est traité seul car il est explicitement isolé dans la checklist de validation §9 :
"WF6 graphe d'usage cmd opérationnel via `find_command_usages()`". C'est le workflow
le plus susceptible d'écart de comportement — l'ancienne `usage_graph.py` prenait
une interface JSON `{"target_type": ..., "target_id": ...}` ; les nouveaux outils
ont des interfaces séparées par type de cible.

---

## M7-1 — WF6 *(unique sous-session)*

### SKILL.md §7 WF6 — Graphe d'usage

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `find_command_usages()`, `find_scenario_dependencies()`,
`find_equipment_usages()`
```

Mapping complet :

| Ancienne approche | Nouvel appel |
|---|---|
| `usage_graph.py {"target_type": "cmd", "target_id": N}` | `holmes__find_command_usages(cmd_id=N, limit=50)` |
| `usage_graph.py {"target_type": "scenario", "target_id": N}` | `holmes__find_scenario_dependencies(scenario_id=N, limit=50)` |
| `usage_graph.py {"target_type": "eqLogic", "target_id": N}` | `holmes__find_equipment_usages(equipment_id=N, limit=50)` |
| `resolve_cmd_refs.py` sur résultats | Non nécessaire — si contexte scénario : `describe_scenario()` résout |

Supprimer toute mention de l'interface JSON `{"target_type": ..., "target_id": ...}`.
Les trois outils Holmes MCP sont désormais appelés séparément selon le type de cible.

Ajouter note :

```
Les trois outils retournent des résultats paginés (limit=50 par défaut).
Pour une cible très utilisée, itérer avec offset si nécessaire.
```

### Test WF6

Exécuter le prompt WF6 du tableau baseline avec Holmes MCP connecté.
Tester les trois variantes : usage d'une commande, d'un scénario, d'un équipement.
Remplir colonne Phase 1 dans `docs/sessions/2026-05-06-M0-baseline.md`.

Point de vigilance : vérifier que `find_command_usages()` retourne bien les scénarios
et équipements qui utilisent la commande cible — c'est le cas d'usage principal du WF.

**Gate qualité M7-1** :
- SKILL.md §7 WF6 : aucune référence à `usage_graph.py`, interface JSON supprimée
- Trois variantes testées (cmd, scenario, eqLogic)
- Verdict Phase 1 noté — distinguer les trois variantes si les résultats diffèrent

---

## DoD — Jalon M7

- [ ] SKILL.md §7 WF6 mis à jour — trois outils séparés, interface JSON supprimée
- [ ] WF6 testé dans ses trois variantes (cmd / scenario / eqLogic)
- [ ] Verdict Phase 1 noté dans le tableau baseline
- [ ] Aucun ⚠️ ou ❌ non documenté
