# Brief jalon M5 — WF Entités

**Branche** : `develop`
**Pré-requis** : M2 terminé (indépendant de M3 et M4)
**Référence** : `docs/state/migration-jeedom-audit-brief.md` §4 (WF3, WF4)

## Contexte

WF3 (diagnostic équipement) et WF4 (diagnostic plugin) sont les deux workflows
centrés sur les entités physiques. Ils partagent `find_equipments_advanced` et `tail_log`.
WF4 bénéficie en plus de `get_config()` pour inspecter la configuration d'un plugin.

---

## M5-1 — WF3

### SKILL.md §7 WF3 — Diagnostic équipement

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `find_equipment_by_name()`, `get_equipment()`,
`get_health_summary()`, `tail_log()`
```

Mapping :

| Ancienne approche | Nouvel appel |
|---|---|
| `db_query.run("SELECT ... FROM eqLogic WHERE name LIKE ?")` | `holmes__find_equipment_by_name(name=...)` |
| `db_query.run("SELECT ... FROM cmd WHERE eqLogic_id = ?")` | `holmes__get_equipment(equipment_id)` (inclut commandes + `currentValue`) |
| `api_call.run("plugin::listPlugin")` pour état daemon | `holmes__get_health_summary()` |
| `logs_query.py tail <plugin>` | `holmes__tail_log(log_name="<plugin>", lines=200)` |

Ajouter note : la resource `jeedom://equipment/{equipment_id}` expose l'équipement
complet avec commandes, config sanitisée et valeurs courantes — alternative directe
à la combinaison `find_equipment_by_name` + `get_equipment`.

### Test WF3

Exécuter le prompt WF3 du tableau baseline avec Holmes MCP connecté.
Remplir colonne Phase 1 dans `docs/sessions/2026-05-06-M0-baseline.md`.

**Gate qualité M5-1** :
- SKILL.md §7 WF3 : aucune référence à `db_query`, `api_call`, `logs_query`
- WF3 testé, verdict Phase 1 noté

---

## M5-2 — WF4

### SKILL.md §7 WF4 — Diagnostic plugin

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `list_plugins()`, `get_health_summary()`,
`find_equipments_advanced()`, `tail_log()`, `get_config()`
```

Mapping :

| Ancienne approche | Nouvel appel |
|---|---|
| `db_query.run("SELECT ... FROM update WHERE type='plugin'")` | `holmes__list_plugins()` |
| `api_call.run("plugin::listPlugin")` | `holmes__get_health_summary()` → champ daemons nok |
| `db_query.run("SELECT ... FROM eqLogic WHERE eqType_name = ?")` | `holmes__find_equipments_advanced(plugin=...)` |
| `logs_query.py tail <plugin>_dep` | `holmes__tail_log(log_name="<plugin>_dep", lines=200)` |

Ajouter note `get_config` :

```
**Inspection configuration plugin** : `holmes__get_config(plugin="<nom_plugin>")` retourne
la configuration du plugin depuis la table `config` Jeedom (champs sensibles masqués
automatiquement). Utile pour inspecter comment jMQTT, agenda ou tout autre plugin
est configuré sans passer par l'UI.
```

### Test WF4

Exécuter le prompt WF4 du tableau baseline avec Holmes MCP connecté.
Remplir colonne Phase 1.

**Gate qualité M5-2** :
- SKILL.md §7 WF4 : aucune référence aux scripts supprimés, note `get_config` présente
- WF4 testé, verdict Phase 1 noté

---

## DoD — Jalon M5

- [ ] SKILL.md §7 WF3 mis à jour — note resource `jeedom://equipment/{id}` présente
- [ ] SKILL.md §7 WF4 mis à jour — note `get_config(plugin=...)` présente
- [ ] WF3 et WF4 testés avec Holmes MCP — verdicts Phase 1 notés
- [ ] Aucun ⚠️ ou ❌ non documenté dans le tableau Phase 1
