# ADR 0017 : Couche de routage intelligent MySQL/API

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : J5b — implémentation de la coexistence MySQL/API (PLANNING §3.5)

## Contexte

La skill doit fonctionner dans deux situations distinctes :
1. **Install standard** : SSH + MySQL disponibles — cas nominal
2. **Install sans accès direct** : API Jeedom uniquement — Jeedom Cloud, VPN absent, préférence utilisateur

PLANNING §3.5 spécifie la philosophie voulue : "MySQL préféré, détection lazy au premier appel, fallback automatique avec mention si configuré, bascule par opération quand intrinsèquement meilleur (stats → API, logs → SSH, audit récursif → MySQL). Discrétion par défaut, mention sur bascule/limitation/manquant."

Chaque vecteur a ses forces : MySQL pour les jointures et l'arbre récursif, API pour les données runtime (`lastLaunch`, `state`, `currentValue`), SSH pour les logs. Forcer l'utilisateur à choisir irait à l'encontre de la philosophie de transparence.

## Options considérées

**Option A — Flag `--source` explicite** : l'utilisateur (ou Claude Code selon le workflow) passe `--source mysql` ou `--source api` à chaque script. Simple à implémenter. Rompt la philosophie PLANNING — l'utilisateur doit connaître les modes d'accès et les choisir au bon moment.

**Option B — Couche de routage transparente** : un module `_common/router.py` détecte les capacités au premier appel (lazy, résultat mis en cache session) et choisit le vecteur optimal par type d'opération. L'utilisateur ne voit que les mentions de bascule. Implémentation plus complexe mais respecte la philosophie et est extensible.

**Option C — Duplication de fallback dans chaque script** : `db_query.py` et `api_call.py` implémentent chacun leur propre détection et fallback. Évite un module commun mais duplique la logique — difficile à maintenir si les règles de routage évoluent.

## Décision

**Option B — Couche de routage transparente via `scripts/_common/router.py`.**

Le module expose trois fonctions :
- `detect_capabilities(creds)` → `{"mysql": bool, "api": bool}` — lazy, résultat mis en cache
- `route(operation, creds)` → `"mysql" | "api" | "ssh"` — règles par type d'opération
- `with_fallback(primary_fn, fallback_fn, mention)` — exécution avec fallback gracieux

`preferred_mode: "auto"` dans `credentials.json` (déjà prévu dans le schéma PLANNING §3.5) permet à l'utilisateur de forcer un mode si nécessaire (`"mysql"` ou `"api"`).

## Conséquences

- Nouveau module `scripts/_common/router.py` avec ses propres tests unitaires
- Les scripts existants (`db_query.py`, `api_call.py`, `logs_query.py`) restent inchangés — le routeur les appelle
- `credentials.py` expose `preferred_mode` au reste du code
- WF5 et WF6 fonctionnent en mode `preferred_mode: "api"` (critère de sortie J5b)
- WF13 refuse explicitement en mode API-only : "Mode API-only : logs requis — WF13 non exécutable"
- Règles de routage centralisées dans `router.py` — un seul endroit à modifier si les règles évoluent
