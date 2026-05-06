# Session Mplan-1 — Planification migration Holmes MCP

**Date** : 2026-05-06
**Branche** : `main` (session de planification — aucune modification de code)
**Commit(s)** : voir ci-dessous

---

## Objectif

Analyser le brief de migration `jeedom-audit → Holmes MCP` et produire l'ensemble
des documents de planification nécessaires au lancement des jalons M0–M8.

---

## Livrables

| Fichier | Ce qui a changé |
|---|---|
| `docs/state/CONTRIBUTING-CLAUDE-CODE.md` | §3 enrichi (brief jalon), §4 remplacé par §4a (fin de sous-session) + §4b (fin de jalon), §5 format hybride adopté, §8 dupliqué corrigé → §9 |
| `docs/sessions/M0-brief.md` | Brief jalon M0 — Baseline Phase 0 (13 WF sur `main`) |
| `docs/sessions/M1-brief.md` | Brief jalon M1 — Infrastructure (develop, .mcp.json, ADR-0020, roadmap) |
| `docs/sessions/M2-brief.md` | Brief jalon M2 — Nettoyage structurel (suppressions + SKILL.md §3/§6/§9 + sql-cookbook) |
| `docs/sessions/M3-brief.md` | Brief jalon M3 — WF Scénarios (WF2, WF5, WF12, WF13) |
| `docs/sessions/M4-brief.md` | Brief jalon M4 — WF Audit & Refactor (WF1, WF7) |
| `docs/sessions/M5-brief.md` | Brief jalon M5 — WF Entités (WF3, WF4) |
| `docs/sessions/M6-brief.md` | Brief jalon M6 — WF Lectures rapides (WF8, WF9, WF10, WF11) |
| `docs/sessions/M7-brief.md` | Brief jalon M7 — WF Graphe d'usage (WF6) |
| `docs/sessions/M8-brief.md` | Brief jalon M8 — Validation finale & Release V2.0.0 |

---

## Décisions prises en session

- **Numérotation M0–M8** : jalons de migration distincts des jalons V1 (J0–J8). M-0 renommé M0 (baseline), décalage de tout le reste d'un cran.
- **Phase 0 (M0) = session séparée** avant toute modification — baseline 13 WF sur `main` documenté avant de créer `develop`.
- **ADR-0020 amendé** (pas de nouvel ADR-0023) : le cas "jeedom-audit consommateur de Holmes MCP" est un amendement à l'ADR existant.
- **V1.5 obsolète** : couverte entièrement par Holmes MCP v1.2.0 — annulée dans l'amendement PLANNING.md §10.
- **V2.0.0** = cible post-migration (breaking change : nouvelle dépendance Holmes MCP). Ancienne V1.1 → V2.1.
- **Merge + tag uniquement en M8** : M0–M7 restent sur `develop`.
- **`tags.py`** : éliminé, contenu (21 tags système) intégré dans SKILL.md §6 comme gotcha.
- **`sql-cookbook.md`** : conservé, recentré sur les contraintes `query_sql()` (LIMIT, MariaDB JSON, blacklist).
- **`check_skill_refs.py`** : créé en M2, exécuté comme gate finale en M8.
- **4 outils Holmes MCP hors brief** documentés dans SKILL.md §7 au fil des WF : `list_objects`, `list_equipments`, `list_scenarios`, `list_log_files`, `get_config`.
- **`search_text` limit** : écrire `limit=20` (valeur réelle) dans SKILL.md, pas `limit=50` du brief.
- **Routines fin de sous-session / fin de jalon** adoptées immédiatement et rendues obligatoires (CONTRIBUTING-CLAUDE-CODE.md §4a/§4b).
- **16 sous-sessions** au total (M0:2, M1:1, M2:2, M3:2, M4:2, M5:2, M6:2, M7:1, M8:2).

---

## Résultats qualité

| Métrique | Valeur |
|---|---|
| Gate qualité | Complétude livrables ✅ |
| Tests | N/A (session planification) |
| Linter | N/A |

---

## Incidents / anomalies

Aucun.

---

## Reste à faire (dans ce jalon)

Aucun — jalon de planification complet.

---

## Pour le PO

- Renseigner le token Holmes MCP réel dans `.mcp.json` lors de M1 (généré dans Jeedom → page plugin → "Tokens d'accès")
- Prévoir des noms réels de la box (scénario, équipement, commande, plugin) pour les prompts de test M0

---

## Prochaine sous-session : M0-1

**Objectif** : exécuter et documenter WF1–WF7 sur `main` (SSH + MySQL, branch inchangée)
**Pré-requis** : alias SSH `Jeedom` configuré, `~/.my.cnf` présent sur la box, lire `docs/sessions/M0-brief.md`
