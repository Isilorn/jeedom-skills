# Documentation jeedom-audit

Index de navigation pour le dossier `docs/`. Chaque public a son point d'entrée.

## Selon ce que tu cherches

| Je suis... | Je veux... | Je lis... |
|---|---|---|
| Utilisateur Jeedom | Installer et utiliser la skill | [README principal](../README.md) → [Getting started](guides/getting-started.md) |
| Utilisateur en difficulté | Résoudre un problème | [Troubleshooting](guides/troubleshooting.md) |
| Utilisateur régulier | Référence des cas d'usage | [Usage](guides/usage.md) |
| Contributeur curieux | Comprendre l'architecture | [Architecture](guides/architecture.md) → [ADRs](decisions/) |
| Contributeur actif | Ouvrir une PR | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| **Session Claude Code** | **Reprendre le projet** | **[PROJECT_STATE](state/PROJECT_STATE.md) → [dernière session](sessions/) → [ADRs récentes](decisions/)** |

## Structure du dossier

```
docs/
├── README.md                    ← ce fichier (index navigation)
├── PLANNING.md                  ← brief de planification V1 complet (~55 décisions, jalons J0-J7)
│
├── guides/                      ← AXE 3 : pédagogie communauté (disponible à J7)
│   ├── getting-started.md
│   ├── usage.md
│   ├── troubleshooting.md
│   └── architecture.md
│
├── decisions/                   ← AXE 1 : traçabilité (ADRs)
│   ├── README.md                ← index ADRs + template
│   └── 0001-*.md … 0015-*.md   ← 15 ADRs initiales V1
│
├── state/                       ← AXE 2 : continuité Claude Code
│   ├── PROJECT_STATE.md         ← état vivant (mis à jour à chaque session)
│   └── CONTRIBUTING-CLAUDE-CODE.md  ← contrat opérationnel binôme PO/Claude Code
│
├── sessions/                    ← AXE 2 : journal de bord
│   └── YYYY-MM-DD-<sujet>.md
│
├── references-source/           ← archives du projet source (historique, non reproductibles tels quels)
│   ├── audit_db.md              ← schéma DB Jeedom observé empiriquement (cross-checké à J1 vs schéma officiel V4-stable)
│   └── brief-initial.md        ← brief initial (format slash-command obsolète, remplacé par PLANNING.md)
│
└── screenshots/                 ← captures fournies par le PO pour README et guides (disponible à J7)
```

## Les trois axes documentaires

| Axe | Objectif | Lieu | Discipline |
|---|---|---|---|
| **1 — Traçabilité** | Pourquoi telle décision a été prise | `decisions/` (ADRs) | Immuable une fois acté ; nouvelles ADRs supersèdent |
| **2 — Continuité Claude Code** | Reprendre le projet sans perdre contexte | `state/` + `sessions/` | Mise à jour à chaque session significative |
| **3 — Pédagogie** | Appropriation par la communauté Jeedom | `../README.md` + `guides/` | Mise à jour aux jalons et retours communauté |

> Détail complet en [PLANNING.md §7](PLANNING.md#7-architecture-documentaire-3-axes--d13).
