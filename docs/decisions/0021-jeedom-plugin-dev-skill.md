# ADR-0021 — jeedom-plugin-dev : second skill dans ce repo

- **Date** : 2026-05-01
- **Statut** : Accepté (en réflexion pour l'implémentation)
- **Contexte de décision** : session de réflexion stratégique post-release v1.0.1

## Contexte

Le repo `jeedom-skills` a été créé dès J0 avec une architecture multi-skills en tête (ADR-0003 : structure `<nom-skill>/` + `shared/`). `jeedom-audit` est la première skill. La question est : quelle est la deuxième ?

Le développement de plugins Jeedom est un besoin communautaire récurrent et sous-servi. La doc officielle est parcellaire. Les patterns répétitifs (structure de plugin, classes PHP, tests, CI) bénéficieraient d'une skill d'assistance.

## Décision

**Créer une second skill `jeedom-plugin-dev`** dans ce repo, pour l'assistance au développement de plugins Jeedom (PHP, structure, tests, CI, market).

Cette skill est distincte de `holmesMCP` (ADR-0020) : elle cible les **développeurs** qui créent des plugins, pas les utilisateurs finaux qui pilotent leur box.

### Périmètre envisagé

- Structure d'un plugin Jeedom (fichiers obligatoires, conventions de nommage)
- Classes PHP héritées (eqLogic, cmd, etc.) et leurs méthodes attendues
- Installation de dépendances via `composer` ou `npm`
- Tests (PHPUnit, structure de test Jeedom)
- CI/CD (GitHub Actions pour plugin Jeedom)
- Soumission au market (contraintes, checklist)
- Patterns communs (daemon, cron, widget, panel)

### Impact sur l'architecture repo

- Création de `jeedom-plugin-dev/SKILL.md` et `jeedom-plugin-dev/references/`
- Extraction de la matière commune dans `shared/` si pertinent (credentials, SSH — moins central pour un outil de dev)
- Le script `build/package_skill.py` produit déjà un `.skill` par répertoire skill — aucune modification nécessaire

## Options écartées

### Repo séparé `jeedom-plugin-dev-skill`

Écarté : la structure multi-skills a été anticipée dès J0. Un repo séparé crée de la friction de maintenance sans bénéfice. Les deux skills partagent la même audience avancée (power users Jeedom).

### Extension de jeedom-audit avec un mode "dev"

Écarté : les deux usages sont orthogonaux — auditer une install existante vs créer un nouveau plugin. Un mode "dev" dans jeedom-audit serait une confusion de responsabilités.

## Conséquences

- ✅ Le repo `jeedom-skills` justifie pleinement son nom pluriel
- ✅ L'architecture multi-skills (ADR-0003) est activée pour la première fois
- ⚠️ Implémentation reportée post-V1.1 — priorité à la stabilisation de jeedom-audit
- ⚠️ Nécessite une session d'idéation dédiée pour cadrer le périmètre exact et les sources de connaissance (doc officielle Jeedom, code source market)
- 🔗 ADR-0003 (architecture repo multi-skills), PLANNING §10 (V2 — seconde skill)
