# ADR 0015 : Stratégie documentaire à 3 axes

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D13.1)

## Contexte

Un projet de skill communautaire a plusieurs publics avec des besoins documentaires distincts : le PO (traçabilité des décisions), les sessions Claude Code futures (continuité de contexte), et la communauté Jeedom (appropriation et contribution). Sans architecture documentaire explicite, la documentation dérive et le contexte se perd entre sessions.

## Options considérées

- **Option A — Documentation unique (README + commentaires)** : un seul README + inline dans le code. ➕ Simple, pas de fragmentation. ➖ Mélange les publics, le contexte Claude Code se perd entre sessions.
- **Option B — Documentation wiki GitHub** : wiki séparé pour la doc publique. ➕ Interface familière. ➖ Non versionné avec le code, fragmentation, pas de notion de "continuité Claude Code".
- **Option C — 3 axes documentaires dans le repo** : axe 1 (ADRs, traçabilité), axe 2 (continuité Claude Code : state + sessions), axe 3 (pédagogie communauté : README + guides). ➕ Chaque public a son point d'entrée, tout est versionné avec le code, la continuité Claude Code est assurée structurellement. ➖ Plus complexe à maintenir.

## Décision

**Option C — 3 axes documentaires dans le repo.**

| Axe | Public | Lieu | Discipline |
|---|---|---|---|
| 1 — Traçabilité | PO + contributeurs futurs | `docs/decisions/` (ADRs) | Immuable une fois acté ; nouvelles ADRs supersèdent |
| 2 — Continuité Claude Code | Sessions Claude Code futures | `docs/state/` + `docs/sessions/` | Mise à jour à chaque session significative |
| 3 — Pédagogie | Communauté Jeedom | `README.md` + `docs/guides/` | Mise à jour aux jalons et retours communauté |

**Routine de continuité (axe 2)** :
- Début de session : lire `docs/README.md` → `PROJECT_STATE.md` → dernière entrée `sessions/` → ADRs récentes
- Fin de session : maj `PROJECT_STATE.md` + nouvelle entrée `sessions/` + ADR(s) si décisions non triviales

## Conséquences

- ✅ Chaque public a son point d'entrée sans bruit des autres axes
- ✅ La continuité Claude Code est assurée structurellement (pas de mémoire implicite requise)
- ✅ Toute la documentation est versionnée avec le code
- ✅ Les décisions sont traçables avec leurs alternatives écartées
- ⚠️ La discipline de mise à jour (axe 2) doit être respectée à chaque session — documentée dans `CONTRIBUTING-CLAUDE-CODE.md`
- ⚠️ L'axe 3 (guides communauté) est largement vide à J0 — à construire aux jalons J2-J7
- 🔗 `docs/state/CONTRIBUTING-CLAUDE-CODE.md`, PLANNING §7
