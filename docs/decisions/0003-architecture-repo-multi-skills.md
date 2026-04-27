# ADR 0003 : Architecture repo multi-skills (`jeedom-skills/jeedom-audit/`)

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D2.1, D2.2)

## Contexte

La skill V1 (`jeedom-audit`) est la première d'un potentiel écosystème. Une future skill `jeedom-plugin-dev` est envisagée (roadmap V2). Il faut décider de la structure du repo GitHub : un repo par skill, ou un repo multi-skills.

## Options considérées

- **Option A — Repo dédié par skill** : `github.com/Isilorn/jeedom-audit` pour V1, `github.com/Isilorn/jeedom-plugin-dev` pour V2. ➕ Isolation totale, indépendance des cycles de release. ➖ Matière commune dupliquée (docs/, tests/fixtures partagés éventuels), fragmentation de la communauté.
- **Option B — Repo multi-skills** : `github.com/Isilorn/jeedom-skills` avec un sous-dossier par skill (`jeedom-audit/`, à terme `jeedom-plugin-dev/`). ➕ Matière commune partageable, communauté unifiée, un seul point d'entrée. ➖ Releases plus complexes (tag par skill ou tag global ?), structure à discipliner.
- **Option C — Monorepo avec workspaces** : structure monorepo outillée. ➕ Tooling avancé. ➖ Surcoût d'infrastructure non justifié pour 1-2 skills.

## Décision

**Option B — Repo multi-skills** (`jeedom-skills`), avec le sous-dossier `jeedom-audit/` comme **dossier-skill** au sens Claude Code.

Règle de packaging : `build/package_skill.py` ne zippe que le contenu de `jeedom-audit/`. Les autres dossiers (`docs/`, `tests/`, `examples/`, `build/`, `.github/`) sont des outils de dev hors skill.

Si une seconde skill émerge : créer `jeedom-plugin-dev/` à côté + `shared/` pour la matière commune, adapter le script de packaging.

## Conséquences

- ✅ Un seul repo GitHub, une seule communauté
- ✅ Matière commune partageable entre skills à terme
- ✅ Le dossier-skill `jeedom-audit/` est clairement isolé du reste
- ⚠️ Le packaging doit être discipliné (ne pas inclure `docs/` ou `tests/` dans le `.skill`)
- ⚠️ Les releases doivent taguer la skill concernée (ex. `jeedom-audit-v1.0.0`)
- 🔗 ADR 0001 (skill vs slash-command), ADR 0012 (distribution)
