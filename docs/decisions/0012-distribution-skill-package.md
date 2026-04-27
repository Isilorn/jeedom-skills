# ADR 0012 : Distribution `.skill` packagé en GitHub Release

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D11.5)

## Contexte

La skill doit être distribuée à la communauté Jeedom. Il faut décider du mécanisme de distribution : clone manuel du repo, téléchargement d'un package, marketplace Claude Code, etc.

## Options considérées

- **Option A — Clone git uniquement** : l'utilisateur clone le repo et pointe Claude Code vers `jeedom-audit/`. ➕ Simple, toujours à jour. ➖ Nécessite git, moins accessible pour les utilisateurs non-techniques.
- **Option B — Package `.skill` en GitHub Release** : `build/package_skill.py` produit `jeedom-audit-vX.Y.Z.skill`, attaché à chaque tag GitHub Release. ➕ Installation standardisée, version figée, checksum vérifiable. ➖ Nécessite un processus de release.
- **Option C — Marketplace Claude Code** : soumission à un registry officiel. ➕ Découvrabilité maximale. ➖ Processus de soumission et de maintenance inconnus à ce stade, dépendance externe.

## Décision

**Option B — Package `.skill` + GitHub Release, avec Option A comme voie alternative.**

Processus de release :
- `build/package_skill.py` zippe uniquement `jeedom-audit/` → `jeedom-audit-vX.Y.Z.skill`
- Le script vérifie : cohérence frontmatter, présence des fichiers `references/` listés dans SKILL.md §9, absence de fichiers sensibles (`credentials.json`, `.env`)
- Produit `MANIFEST.txt` (liste des fichiers + checksums SHA256)
- Le `.skill` est attaché à la GitHub Release pour chaque tag `vX.Y.Z`

Option A (clone manuel + symlink) reste documentée comme alternative dans `getting-started.md`.

Option C (marketplace) : envisageable si un registry officiel émerge — roadmap sans engagement.

## Conséquences

- ✅ Distribution standardisée, versionnable, intègre (checksums)
- ✅ Script de packaging avec vérifications de sécurité
- ✅ Voie alternative (clone git) pour les utilisateurs avancés
- ⚠️ Le processus de release doit être discipliné (`.skill` dans `.gitignore`)
- ⚠️ Le script de packaging à développer à J7
- 🔗 ADR 0001 (skill vs slash-command), ADR 0003 (repo multi-skills), PLANNING §8.4
