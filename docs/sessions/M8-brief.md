# Brief jalon M8 — Validation finale & Release

**Branche** : `develop` → `main` (merge en fin de jalon)
**Pré-requis** : M3, M4, M5, M6, M7 tous terminés (13 WF migrés et testés)
**Référence** : `docs/state/migration-jeedom-audit-brief.md` §9 (checklist), §10 (protocole)

## Contexte

Jalon de validation et de release. Deux activités distinctes :
- M8-1 : vérifier que la migration est complète et sans régression
- M8-2 : mettre à jour la documentation de release et merger sur `main`

---

## M8-1 — Validation technique

### 1. Lint check

```bash
python tests/lint/check_skill_refs.py
```

Résultat attendu : `✅ SKILL.md propre — aucune référence aux scripts supprimés.`
Si des références résiduelles sont trouvées → identifier le WF concerné, corriger,
relancer avant de continuer.

### 2. Checklist §9 du brief de migration

Vérifier chaque point de `docs/state/migration-jeedom-audit-brief.md` §9 :

- [ ] Branche `develop` créée depuis `main`
- [ ] Fichiers Éliminer supprimés (§2)
- [ ] SKILL.md §3 réécrit (Bearer token, sans SSH ni credentials)
- [ ] SKILL.md §Routage supprimé
- [ ] SKILL.md §6 Gotchas mis à jour (backticks, LIMIT, MariaDB JSON)
- [ ] SKILL.md §7 scripts → outils Holmes MCP pour les 13 WF
- [ ] SKILL.md §9 Index références nettoyé
- [ ] `references/sql-cookbook.md` mis à jour
- [ ] 13 WF testés depuis Claude Code avec Holmes MCP connecté
- [ ] WF6 graphe d'usage cmd opérationnel via `find_command_usages()`
- [ ] Aucune référence à SSH, `db_query`, `api_call`, `setup.py` dans SKILL.md

### 3. Comparaison Phase 0 vs Phase 1

Ouvrir `docs/sessions/2026-05-06-M0-baseline.md`.
Comparer les verdicts Phase 0 et Phase 1 pour les 13 WF.

Pour chaque ⚠️ ou ❌ en Phase 1 :
- Si régression confirmée (Phase 0 ✅, Phase 1 ❌) → **bloquer la release**, corriger
- Si dégradation acceptable (Phase 0 ✅, Phase 1 ⚠️) → documenter + décision PO
- Si Phase 0 était déjà ⚠️ → acceptable, noter

Conclure le document baseline avec :

```markdown
## Conclusion

Migration validée / Points bloquants identifiés :
- [liste des anomalies retenues ou "Aucune régression constatée"]

**Verdict global** : ✅ Prêt pour release V2.0.0 / ❌ Blocages à corriger
```

**Gate qualité M8-1** :
- `check_skill_refs.py` : sortie `✅`
- Checklist §9 : tous les points cochés
- Tableau Phase 0/Phase 1 : conclusion rédigée, verdict global ✅

---

## M8-2 — Release

### 1. CHANGELOG.md

Ajouter entrée `[2.0.0] — 2026-MM-JJ` :

```markdown
## [2.0.0] — 2026-MM-JJ

### Changed
- Couche d'accès aux données migrée de SSH+MySQL+API vers Holmes MCP v1.2.0
- Pré-requis utilisateur : Holmes MCP installé sur la box Jeedom (Bearer token)
- SKILL.md §3 réécrit — plus de SSH, plus de credentials MySQL
- `references/sql-cookbook.md` réduit aux contraintes `query_sql()`

### Removed
- Scripts Python supprimés : `setup.py`, `api_call.py`, `db_query.py`, `logs_query.py`,
  `scenario_tree_walker.py`, `resolve_cmd_refs.py`, `usage_graph.py`
- Modules `_common/` supprimés : `credentials.py`, `ssh.py`, `router.py`,
  `sensitive_fields.py`, `version_check.py`, `tags.py`
- Références supprimées : `connection.md`, `api-jsonrpc.md`, `api-http.md`
- 191 tests unitaires Python (testaient le code supprimé)

### Added
- `.mcp.json` — configuration Holmes MCP (Bearer token, scope projet)
- `tests/lint/check_skill_refs.py` — lint SKILL.md pour références résiduelles

### Validated
- 13 workflows testés avec Holmes MCP v1.2.0 — aucune régression (Phase 0 → Phase 1)
```

### 2. README.md

Mettre à jour la section pré-requis :
- Remplacer : "alias SSH `Jeedom`", "`~/.my.cnf`", "`python3 scripts/setup.py`"
- Par : "Holmes MCP installé sur la box Jeedom", "`.mcp.json` configuré avec Bearer token"

Mettre à jour le tableau des jalons si présent.

### 3. PROJECT_STATE.md

- `Version actuelle` → `2.0.0`
- `Jalon en cours` → `post-release V2.0.0`
- `Prochaines étapes` → `V2.1 : support Jeedom 4.6, retours communauté`
- Ajouter dans `Jalons post-release` : `- **M8 (2026-MM-JJ)** : release V2.0.0 — migration Holmes MCP complète`

### 4. Routine de fin de jalon M8 (merge + tag)

```bash
# Merge develop → main
git checkout main
git merge --ff-only develop
git tag v2.0.0
git push origin main develop --tags

# Resync develop
git checkout develop
git merge --ff-only main
git push origin develop
```

> Si `main` a reçu un hotfix depuis M1 : utiliser `--no-ff` à la place de `--ff-only`.

**Gate qualité M8-2** :
- CHANGELOG.md : entrée V2.0.0 présente
- README.md : aucune mention de SSH, `~/.my.cnf`, `setup.py`
- `git tag` : tag `v2.0.0` présent sur le commit de merge
- `develop` resynchronisé sur `main`

---

## DoD — Jalon M8

- [ ] `check_skill_refs.py` : sortie `✅ SKILL.md propre`
- [ ] Checklist §9 du brief : tous les points cochés
- [ ] Tableau Phase 0/Phase 1 : 13 WF comparés, conclusion rédigée, verdict ✅
- [ ] CHANGELOG.md : entrée V2.0.0 complète
- [ ] README.md : pré-requis mis à jour (Holmes MCP, pas SSH)
- [ ] PROJECT_STATE.md : version 2.0.0, jalons à jour
- [ ] Tag `v2.0.0` posé sur `main`
- [ ] `develop` resynchronisé sur `main` post-merge
