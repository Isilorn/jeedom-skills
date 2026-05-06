# Brief jalon M2 — Nettoyage structurel

**Branche** : `develop`
**Pré-requis** : M1 terminé (branche `develop` existante, `.mcp.json` présent)
**Référence** : `docs/state/migration-jeedom-audit-brief.md` §2, §5, §6, §7

## Contexte

Éliminer tous les fichiers remplacés par Holmes MCP et réécrire les sections de
SKILL.md qui référencent l'ancienne couche d'accès (§3, §Routage, §6, §9).
Les sections §7 (WF) de SKILL.md sont laissées aux jalons M3–M7.
Après ce jalon, le repo ne contient plus de code Python lié à l'accès aux données.

---

## M2-1 — Suppressions + lint check

### Fichiers à supprimer

**Scripts** :
- `jeedom-audit/scripts/setup.py`
- `jeedom-audit/scripts/api_call.py`
- `jeedom-audit/scripts/db_query.py`
- `jeedom-audit/scripts/logs_query.py`
- `jeedom-audit/scripts/scenario_tree_walker.py`
- `jeedom-audit/scripts/resolve_cmd_refs.py`
- `jeedom-audit/scripts/usage_graph.py`

**Modules communs** :
- `jeedom-audit/scripts/_common/credentials.py`
- `jeedom-audit/scripts/_common/ssh.py`
- `jeedom-audit/scripts/_common/router.py`
- `jeedom-audit/scripts/_common/sensitive_fields.py`
- `jeedom-audit/scripts/_common/version_check.py`
- `jeedom-audit/scripts/_common/tags.py`

**Références** :
- `jeedom-audit/references/connection.md`
- `jeedom-audit/references/api-jsonrpc.md`
- `jeedom-audit/references/api-http.md`

**Tests unitaires** (testent le code supprimé) :
- `tests/unit/test_api_call.py`
- `tests/unit/test_db_query.py`
- `tests/unit/test_logs_query.py`
- `tests/unit/test_resolve_cmd_refs.py`
- `tests/unit/test_router.py`
- `tests/unit/test_scenario_tree_walker.py`
- `tests/unit/test_usage_graph.py`

Vérifier que le dossier `jeedom-audit/scripts/_common/` est vide après suppression
(sauf `__init__.py` s'il existe — le supprimer aussi).

### Créer `tests/lint/check_skill_refs.py`

Script qui vérifie que SKILL.md ne contient plus de références aux fichiers supprimés.
Il sera exécuté comme gate qualité finale en M8.

```python
"""Vérifie qu'aucune référence aux scripts supprimés ne subsiste dans SKILL.md."""
import re
import sys
from pathlib import Path

ELIMINATED = [
    "setup.py", "api_call.py", "db_query.py", "logs_query.py",
    "scenario_tree_walker.py", "resolve_cmd_refs.py", "usage_graph.py",
    "credentials.py", "ssh.py", "router.py", "sensitive_fields.py",
    "version_check.py", "tags.py",
    "connection.md", "api-jsonrpc.md", "api-http.md",
    "db_query.run", "api_call.run", "logs_query", "router.py",
]

skill_path = Path("jeedom-audit/SKILL.md")
text = skill_path.read_text()
findings = []

for ref in ELIMINATED:
    for i, line in enumerate(text.splitlines(), 1):
        if ref in line:
            findings.append(f"  ligne {i}: {line.strip()}")

if findings:
    print(f"❌ {len(findings)} référence(s) résiduelle(s) dans SKILL.md :")
    for f in findings:
        print(f)
    sys.exit(1)
else:
    print("✅ SKILL.md propre — aucune référence aux scripts supprimés.")
```

**Gate qualité M2-1** :
- `git status` : tous les fichiers listés ci-dessus absents
- `python -c "import ast; ast.parse(open('tests/lint/check_skill_refs.py').read())"` : syntaxe valide
- Ne pas exécuter `check_skill_refs.py` — §7 SKILL.md n'est pas encore mis à jour

---

## M2-2 — SKILL.md + sql-cookbook

### SKILL.md §3 — Réécrire entièrement

Remplacer la section `## 3. Pré-requis et connexion` par le contenu exact du
brief de migration §7 §3 (`docs/state/migration-jeedom-audit-brief.md`).

Résumé des changements :
- Supprimer : alias SSH, `~/.my.cnf`, `credentials.json`, `setup.py`, modes d'accès
- Ajouter : Holmes MCP pré-requis, format `.mcp.json`, vérification de version via `holmes__get_install_overview()`

### SKILL.md §Routage automatique — Supprimer

Supprimer entièrement la section `### Routage automatique (router.py)` et son contenu.

### SKILL.md §6 — Mettre à jour les gotchas

Modifications par gotcha (cf. brief migration §7 §6) :

- `trigger` mot réservé → remplacer "`db_query.py`" par "`query_sql()`"
- `repeat` mot réservé → même remplacement
- `update` mot réservé → même remplacement
- `JSON_EXTRACT via echo` → **supprimer ce gotcha** (`query_sql()` gère nativement)
- Ajouter : "**LIMIT auto-injectée par `query_sql()`** : 50 si absente, plafond 200. `COUNT(*)` non affecté."
- Ajouter : "**Colonnes sensibles** : `SELECT password, token, apikey, secret` rejeté. `SELECT *` autorisé et filtré."
- Ajouter : "**`CAST(col AS JSON)` échoue sur MariaDB** — utiliser `JSON_SEARCH(arr, 'one', CAST(id AS CHAR)) IS NOT NULL`"
- Ajouter : "**Tags système réservés** — ne jamais tenter de résoudre comme `#[O][E][C]#` : `#trigger_id#`, `#trigger_value#`, `#trigger_name#`, `#trigger_type#`, `#user_connect#`, `#sunset#`, `#sunrise#`, `#time#`, `#date#`, `#datetime#`, `#seconde#`, `#minute#`, `#heure#`, `#jour#`, `#mois#`, `#annee#`, `#sjour#`, `#smois#`, `#nweek#`, `#IP#`, `#hostname#`, `#jeedom_name#`"

Gotchas à conserver inchangés : `scenarioExpression`, `scenarioElement FK`, `jMQTT topic`, `int vs string JSON`, `cmd.value thermostat`.

### SKILL.md §9 — Nettoyer l'index

Supprimer les entrées correspondant aux fichiers Éliminer :
`connection.md`, `api-jsonrpc.md`, `api-http.md`, et toute référence aux scripts supprimés.
Conserver toutes les entrées des fichiers Conserver (références plugins, health-checks, audit-templates, scenario-grammar, sql-cookbook).

### `references/sql-cookbook.md` — Réécrire

Remplacer le contenu par les contraintes techniques de `query_sql()` uniquement.
Les 8 recettes SQL originales sont obsolètes (couvertes par des outils Holmes MCP dédiés).

Structure cible :

```markdown
# Contraintes `query_sql()`

> Les requêtes SQL ad-hoc passent par `holmes__query_sql(sql=...)`.
> Ce fichier documente les contraintes comportementales à connaître.

## LIMIT automatique

| Cas | Comportement |
|---|---|
| Requête sans LIMIT | LIMIT 50 injectée automatiquement |
| Requête avec LIMIT | Respectée, plafonnée à 200 |
| COUNT(*) | Non affecté |

Les requêtes d'audit exhaustif doivent inclure `LIMIT 200` explicitement.

## Blacklist tables

Refus immédiat : `user`, `session`, `network`, et tout nom contenant
`creds`, `credentials`, `password`, `token`.

## Colonnes sensibles

`SELECT password, token, apikey, secret` → rejeté.
`SELECT *` → autorisé, champs sensibles filtrés à la sortie (`[FILTRÉ]`).
Si `_filtered_fields` non vide dans la réponse : mentionner explicitement.

## MariaDB — JSON

`CAST(col AS JSON)` est syntaxe MySQL — **échoue sur MariaDB (Jeedom Bookworm)**.

```sql
-- NE PAS UTILISER
JSON_CONTAINS(arr_col, CAST(id_col AS JSON))

-- UTILISER
JSON_SEARCH(arr_col, 'one', CAST(id_col AS CHAR)) IS NOT NULL
```

Note : `scenario.scenarioElement` stocke les IDs comme chaînes (`["502"]`).
`JSON_SEARCH` avec `CAST AS CHAR` est cohérent.

## Mots réservés MariaDB

`query_sql()` auto-backtique automatiquement : `trigger`, `repeat`, `update`.
Écrire sans backticks dans les requêtes.
```

**Gate qualité M2-2** :
- Grep `SKILL.md` : aucune occurrence de `ssh.py`, `db_query`, `api_call`, `setup.py`, `router.py`
  dans les sections §3, §6, §9 (§7 est encore à migrer — ignorer)
- `sql-cookbook.md` : aucune des 8 anciennes recettes présentes

---

## DoD — Jalon M2

- [ ] 14 fichiers Éliminer supprimés (7 scripts + 6 `_common/` + 3 `references/`)
- [ ] 7 fichiers `tests/unit/test_*.py` supprimés
- [ ] `tests/lint/check_skill_refs.py` créé (syntaxe valide)
- [ ] SKILL.md §3 réécrit (Bearer token, sans SSH ni credentials)
- [ ] SKILL.md §Routage automatique supprimé
- [ ] SKILL.md §6 mis à jour (backticks, LIMIT, MariaDB JSON, blacklist, colonnes sensibles, tags système)
- [ ] SKILL.md §9 nettoyé (entrées Éliminer absentes)
- [ ] `references/sql-cookbook.md` réécrit (contraintes `query_sql()` uniquement)
- [ ] Grep §3/§6/§9 de SKILL.md : zéro référence aux scripts supprimés
