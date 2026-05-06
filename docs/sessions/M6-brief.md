# Brief jalon M6 — WF Lectures rapides

**Branche** : `develop`
**Pré-requis** : M2 terminé (indépendant de M3, M4, M5)
**Référence** : `docs/state/migration-jeedom-audit-brief.md` §4 (WF8, WF9, WF10, WF11)

## Contexte

Quatre workflows à remplacements simples (1–2 outils chacun). WF8 a un piège :
`find_commands_advanced()` ne retourne pas `currentValue` — il faut passer par
`list_commands(equipment_id)` ou `get_equipment(equipment_id)` en deux étapes.
Ce pattern doit être documenté explicitement dans SKILL.md.

---

## M6-1 — WF8 + WF9

### SKILL.md §7 WF8 — Valeur courante

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `find_commands_advanced()`, `list_commands()` ou `get_equipment()`
```

Mapping :

| Ancienne approche | Nouvel appel |
|---|---|
| `db_query.run("SELECT ... FROM cmd WHERE id = ?")` | `holmes__find_commands_advanced(...)` → obtenir `equipment_id` |
| `api_call.run("cmd::byId")` pour `currentValue` | `holmes__list_commands(equipment_id=...)` ou `holmes__get_equipment(equipment_id)` |

Ajouter note explicite sur le pattern obligatoire :

```
⚠️ `find_commands_advanced()` ne retourne pas `currentValue` (coût N×API prohibitif).
Pattern obligatoire :
1. `find_commands_advanced(name_contains=...)` → récupérer `equipment_id`
2. `list_commands(equipment_id=...)` ou `get_equipment(equipment_id)` → lire `currentValue`

Alternative directe : resource `jeedom://equipment/{equipment_id}` inclut les valeurs courantes.
```

### SKILL.md §7 WF9 — Historique

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `get_command_history()`
```

Mapping :

| Ancienne approche | Nouvel appel |
|---|---|
| `api_call.run("cmd::getHistory")` | `holmes__get_command_history(cmd_id=N)` (live + archivé, limit=100 par défaut) |

### Test WF8 + WF9

Exécuter les prompts WF8 et WF9 du tableau baseline avec Holmes MCP connecté.
Remplir colonnes Phase 1 dans `docs/sessions/2026-05-06-M0-baseline.md`.

**Gate qualité M6-1** :
- SKILL.md §7 WF8 : note pattern deux étapes présente, aucune référence à `db_query`/`api_call`
- SKILL.md §7 WF9 : aucune référence aux scripts supprimés
- WF8 et WF9 testés, verdicts Phase 1 notés

---

## M6-2 — WF10 + WF11

### SKILL.md §7 WF10 — Variable dataStore

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `list_datastore_variables()`, `get_datastore_variable()`
```

Mapping :

| Ancienne approche | Nouvel appel |
|---|---|
| `db_query.run("SELECT ... FROM dataStore WHERE type='scenario'")` | `holmes__list_datastore_variables()` |
| `db_query.run("SELECT ... FROM dataStore WHERE key = ?")` | `holmes__get_datastore_variable(key=...)` |

### SKILL.md §7 WF11 — Recherche libre

Remplacer `**Scripts** :` par :

```
**Outils Holmes MCP** : `search_text()`
```

Mapping :

| Ancienne approche | Nouvel appel |
|---|---|
| Multiples `db_query.run()` avec LIKE | `holmes__search_text(text=..., limit=20)` |

Ajouter note :

```
Note : `search_text()` a une limite par défaut de 20 résultats. Passer `limit=20`
explicitement pour signaler que c'est le plafond, pas une troncature silencieuse.
Pour une recherche plus large, enchaîner plusieurs appels avec des termes plus ciblés.
```

### Test WF10 + WF11

Exécuter les prompts WF10 et WF11 du tableau baseline avec Holmes MCP connecté.
Remplir colonnes Phase 1.

**Gate qualité M6-2** :
- SKILL.md §7 WF10 et WF11 : aucune référence aux scripts supprimés
- Note `limit=20` présente dans WF11
- WF10 et WF11 testés, verdicts Phase 1 notés

---

## DoD — Jalon M6

- [ ] SKILL.md §7 WF8 mis à jour — pattern deux étapes documenté, resource `jeedom://equipment/{id}` mentionnée
- [ ] SKILL.md §7 WF9 mis à jour
- [ ] SKILL.md §7 WF10 mis à jour
- [ ] SKILL.md §7 WF11 mis à jour — note `limit=20` présente
- [ ] WF8, WF9, WF10, WF11 testés avec Holmes MCP — verdicts Phase 1 notés
- [ ] Aucun ⚠️ ou ❌ non documenté dans le tableau Phase 1
