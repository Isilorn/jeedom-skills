---
title: Architecture — jeedom-audit
audience: contributeur curieux (vue aérienne)
---

# Architecture de jeedom-audit

Vue aérienne pour comprendre comment la skill est conçue. Pour les décisions de conception détaillées, voir les [ADRs](../decisions/).

---

## Principe fondamental

La skill injecte une **connaissance structurelle de Jeedom 4.5** dans le contexte de Claude Code, qui l'utilise pour exécuter des scripts Python via SSH et produire des rapports en langage naturel.

```
Utilisateur
    │ prompt naturel
    ▼
Claude Code (avec skill jeedom-audit chargée)
    │ lit SKILL.md + references/ au démarrage
    │ exécute scripts Python via SSH
    ▼
Box Jeedom (SSH+MySQL ou API)
    │ retourne données JSON
    ▼
Claude Code
    │ interprète, filtre les données sensibles
    ▼
Rapport structuré en langage naturel
```

**Règle absolue** : lecture seule. Aucun script ne peut modifier la box. ([ADR 0006](../decisions/0006-lecture-seule-absolue.md))

---

## Structure du repo

```
jeedom-skills/
├── jeedom-audit/          ← LA SKILL (seul dossier packagé en .skill)
│   ├── SKILL.md           ← chargé par Claude Code au démarrage (instructions + index)
│   ├── references/        ← docs de référence chargées à la demande
│   └── scripts/           ← helpers Python exécutés via SSH
│       └── _common/       ← modules partagés (credentials, SSH, router, tags...)
├── tests/                 ← outils de dev (hors skill)
│   ├── unit/              ← 191 tests pytest avec mocks
│   ├── evals/             ← évals comportementales (15 cas)
│   └── fixtures/          ← données sanitisées pour tests
├── examples/              ← 8 cas d'acceptation V1
├── docs/                  ← documentation du repo
│   ├── decisions/         ← ADRs (Architecture Decision Records)
│   ├── guides/            ← documentation communautaire
│   └── state/             ← état vivant du projet
└── build/                 ← outillage de packaging
    └── package_skill.py   ← produit le .skill
```

---

## Scripts Python (helpers)

Chaque script a une responsabilité unique, lit via SSH, et retourne du JSON :

| Script | Rôle |
|---|---|
| `db_query.py` | Requêtes SELECT MySQL génériques |
| `api_call.py` | Appels JSON-RPC Jeedom (méthodes autorisées uniquement) |
| `logs_query.py` | Lecture de logs via SSH (tail, détection auto du répertoire) |
| `resolve_cmd_refs.py` | Résolution batch `#ID#` → `#[Objet][Équipement][Commande]#` |
| `scenario_tree_walker.py` | Parcours récursif de l'arbre de scénario (anti-cycle) |
| `usage_graph.py` | Graphe d'usage d'une commande, équipement ou scénario |
| `setup.py` | Assistant de configuration interactif |

Modules partagés dans `_common/` :

| Module | Rôle |
|---|---|
| `credentials.py` | Lecture/écriture `credentials.json` |
| `ssh.py` | Exécution de commandes SSH + requêtes MySQL |
| `router.py` | Routage transparent MySQL/API selon les capacités détectées |
| `tags.py` | Filtrage des données sensibles dans les sorties |
| `sensitive_fields.py` | Liste des champs à masquer (mots de passe, IPs) |
| `version_check.py` | Vérification de la version Jeedom |

---

## Routage MySQL/API (`router.py`)

La skill détecte automatiquement les capacités disponibles au premier appel :

```
router.detect_capabilities(ssh_alias, api_url)
  → mysql=True/False
  → api=True/False
```

Puis route chaque opération vers la source la plus appropriée, avec fallback automatique si MySQL est indisponible. ([ADR 0017](../decisions/0017-couche-routage-intelligent.md))

---

## SKILL.md — point d'entrée pour Claude

`jeedom-audit/SKILL.md` est chargé par Claude Code à chaque démarrage de conversation. Il contient :

1. Contexte et règle absolue (lecture seule)
2. Prérequis techniques
3. Routage MySQL/API
4. Accès aux données (DB schema, API methods)
5. Données sensibles à filtrer
6. Plugins tier-1 (comportements spécifiques)
7. Workflows (13 intentions → étapes → scripts)
8. Conventions de sortie
9. Index des fichiers de référence

Les fichiers `references/` sont chargés **à la demande** (quand un workflow les nécessite), pour ne pas saturer le contexte.

---

## Stratégie de tests

- **191 tests unitaires** (`tests/unit/`) — chaque script a happy path + cas limite, tout mocké (pas de vraie box)
- **15 évals comportementales** (`tests/evals/`) — prompts réels avec critères de succès/échec
- **8 cas d'acceptation** (`examples/`) — recette go/no-go release V1
- **Tests live** sur box réelle Jeedom 4.5.3 (via SSH) par le PO

---

## Décisions de conception

Les 17 ADRs dans `docs/decisions/` documentent toutes les décisions structurantes. Les plus importantes :

| ADR | Décision |
|---|---|
| [0001](../decisions/0001-skill-vs-slash-command.md) | Skill (pas slash-command) |
| [0005](../decisions/0005-mode-acces-mysql-vs-api.md) | SSH+MySQL préféré, API secondaire |
| [0006](../decisions/0006-lecture-seule-absolue.md) | Lecture seule absolue V1 |
| [0007](../decisions/0007-13-intentions-5-familles.md) | 13 intentions dans 5 familles |
| [0009](../decisions/0009-couverture-plugins-tier-1.md) | 6 plugins tier-1 + tier-générique |
| [0017](../decisions/0017-couche-routage-intelligent.md) | Routage transparent MySQL/API |

---

## Contribuer

Voir [CONTRIBUTING.md](../../CONTRIBUTING.md) pour les critères d'acceptation des PRs.
