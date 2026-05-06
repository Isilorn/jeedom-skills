# Brief jalon M4 — WF Audit & Refactor

**Branche** : `develop`
**Pré-requis** : M3 terminé (WF5 migré — WF7 en dépend)
**Référence** : `docs/state/migration-jeedom-audit-brief.md` §4 (WF1, WF7)

## Contexte

WF1 (audit général) et WF7 (suggestions de refactor) sont les deux workflows les plus
riches en appels Holmes MCP — une dizaine de remplacements chacun. WF7 compose WF1 + WF5,
d'où la dépendance sur M3.

---

## M4-1 — WF1

### SKILL.md §7 WF1 — Audit général

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `get_install_overview()`, `list_plugins()`, `get_health_summary()`,
`find_equipments_advanced()`, `tail_log()`
```

Mapping complet :

| Ancienne approche | Nouvel appel |
|---|---|
| `db_query.run("SELECT value FROM config WHERE key='version'...")` | `holmes__get_install_overview()` |
| `db_query.run("SELECT ... FROM update WHERE type='plugin'")` | `holmes__list_plugins()` |
| `db_query.run("SELECT COUNT(*) FROM eqLogic")` | `holmes__get_install_overview()` (inclut comptages) |
| `db_query.run("SELECT COUNT(*) FROM scenario")` | `holmes__get_install_overview()` |
| `db_query.run("SELECT ... FROM message WHERE type='error'")` | `holmes__get_health_summary()` |
| `db_query.run("SELECT ... FROM update WHERE status != 'ok'")` | `holmes__list_plugins()` → filtrer `state != 'ok'` |
| `db_query.run(requête équipements warning/danger)` | `holmes__find_equipments_advanced(has_warning=True)` |
| `db_query.run(requête commandes mortes)` | `holmes__get_health_summary()` → champ `dead_commands` |
| `db_query.run(requête qualité historique)` | `holmes__get_health_summary()` → `summary.historized_cmds_without_data` |
| `logs_query.py tail http.error` | `holmes__tail_log(log_name="http", lines=200)` |

Ajouter note sur la vérification de version en début de session :
`holmes__get_install_overview()` → champ `jeedom_version`.
- `< 4.5` → refus explicite (comportement inchangé)
- `>= 4.6` → avertissement (schéma peut différer)

### Test WF1

Exécuter le prompt WF1 du tableau baseline avec Holmes MCP connecté.
Remplir colonne Phase 1 dans `docs/sessions/2026-05-06-M0-baseline.md`.

**Gate qualité M4-1** :
- SKILL.md §7 WF1 : aucune référence à `db_query`, `logs_query`, `api_call`
- WF1 testé, verdict Phase 1 noté

---

## M4-2 — WF7

### SKILL.md §7 WF7 — Suggestions de refactor

WF7 est une composition de WF1 + WF5. Les requêtes WF1 sont déjà couvertes.
Se concentrer sur les requêtes spécifiques au refactor :

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : (composition WF1 + WF5) + `list_datastore_variables()`,
`find_commands_advanced()`, `find_scenarios_advanced()`, `query_sql()`
```

Mapping spécifique WF7 :

| Ancienne approche | Nouvel appel |
|---|---|
| `db_query.run(requête variables orphelines)` | `holmes__list_datastore_variables(orphaned=True)` |
| `db_query.run(requête commandes sans generic_type)` | `holmes__find_commands_advanced(generic_type_missing=True)` |
| `db_query.run(requête scénarios désactivés mais appelés)` | `holmes__find_scenarios_advanced(called_while_inactive=True)` |
| Requêtes ad-hoc résiduelles | `holmes__query_sql(sql=...)` |

Ajouter note : pour les requêtes ad-hoc passant par `query_sql()`, respecter les
contraintes documentées dans `references/sql-cookbook.md` (LIMIT, MariaDB JSON, blacklist).

### Test WF7

Exécuter le prompt WF7 du tableau baseline avec Holmes MCP connecté.
Remplir colonne Phase 1.

**Gate qualité M4-2** :
- SKILL.md §7 WF7 : aucune référence aux scripts supprimés
- WF7 testé, verdict Phase 1 noté

---

## DoD — Jalon M4

- [ ] SKILL.md §7 WF1 mis à jour — mapping complet, note vérification version
- [ ] SKILL.md §7 WF7 mis à jour — composition WF1+WF5, outils dédiés refactor
- [ ] WF1 et WF7 testés avec Holmes MCP — verdicts Phase 1 notés
- [ ] Aucun ⚠️ ou ❌ non documenté dans le tableau Phase 1
