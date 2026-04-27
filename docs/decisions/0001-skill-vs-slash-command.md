# ADR 0001 : Skill vs slash-command

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D1 cadrage)

## Contexte

Deux mécanismes d'extension Claude Code coexistent : les **slash-commands** (fichiers `.md` dans `.claude/commands/`) et les **skills** (dossiers packagés en `.skill`). Le brief initial du projet source utilisait le format slash-command. Pour V1, il faut choisir l'un ou l'autre comme mécanisme de distribution.

## Options considérées

- **Option A — Slash-command** : fichier `.md` unique dans `.claude/commands/`, installation manuelle par copie. ➕ Simple, aucune dépendance. ➖ Pas de packaging standardisé, pas d'installation via marketplace ou release GitHub, référence documentaire moins claire, ne suit pas l'écosystème skill émergent.
- **Option B — Skill** : dossier packagé en `.skill` (archive zip), installable via Claude Code. ➕ Packaging standardisé, distribution via GitHub Releases, cohérence avec l'écosystème, meilleure progressive disclosure (SKILL.md + references/ séparés). ➖ Légèrement plus complexe à packager (script `build/package_skill.py` nécessaire).

## Décision

**Option B — Skill packagée.**

Le format skill permet une distribution propre (`.skill` attaché à chaque GitHub Release), un packaging vérifiable (`MANIFEST.txt`, checksums), et une meilleure organisation de la documentation technique (`SKILL.md` séparé des `references/`). La complexité additionnelle (script de packaging) est marginale et apporte une valeur réelle pour la communauté.

## Conséquences

- ✅ Distribution standardisée via GitHub Releases
- ✅ Meilleure progressive disclosure : SKILL.md (200-300 lignes) pointe vers `references/` sans les dupliquer
- ✅ Script de packaging avec vérification d'intégrité
- ⚠️ L'utilisateur doit installer le `.skill` (documentation nécessaire dans `getting-started.md`)
- 🔗 ADR 0003 (structure repo), ADR 0012 (distribution)

## Alternatives écartées

**Slash-command** : le brief initial (`docs/references-source/brief-initial.md`) utilisait ce format. Écarté car le format skill est plus adapté à la distribution communautaire et permet un packaging multi-fichiers (SKILL.md + references/ + scripts/).
