# Cadrage J5b — Couche de routage intelligent MySQL/API

> **Brief de démarrage session J5b.** À lire après `PROJECT_STATE.md` et avant de coder.

---

## Objectif

Construire une couche de routage **transparente** qui choisit automatiquement le meilleur vecteur d'accès aux données (MySQL/SSH, API JSON-RPC, logs SSH) selon le type d'opération, avec détection lazy, fallback automatique et mention discrète.

**Philosophie (PLANNING §3.5) :**
> "MySQL préféré, détection lazy au premier appel, fallback automatique avec mention si configuré, bascule par opération quand intrinsèquement meilleur (stats → API, logs → SSH, audit récursif → MySQL). Discrétion par défaut, mention sur bascule/limitation/manquant."

Ce n'est **pas** un flag `--source api`. C'est un routeur interne — l'utilisateur ne choisit pas le vecteur, la skill choisit pour lui.

---

## Architecture proposée

### Nouveau module : `scripts/_common/router.py`

```python
def detect_capabilities(creds: dict) -> dict:
    """Retourne {"mysql": bool, "api": bool} — résultat mis en cache session."""

def route(operation: str, creds: dict) -> str:
    """Retourne "mysql" | "api" | "ssh" selon l'opération et les capabilities."""

def with_fallback(primary_fn, fallback_fn, mention: str) -> tuple[Any, str | None]:
    """Exécute primary_fn ; si échec → fallback_fn + retourne mention."""
```

### Valeur `preferred_mode` dans `credentials.json`

| Valeur | Comportement |
|---|---|
| `"auto"` (défaut) | Le routeur décide par opération selon les capacités détectées |
| `"mysql"` | Force MySQL/SSH, API ignorée |
| `"api"` | Force API, MySQL ignorée — mode API-only pour installs sans SSH |

Ce champ est déjà dans le schéma `credentials.json` (PLANNING §3.5) — aucune migration nécessaire.

---

## Règles de routage par opération

| Type d'opération | Préféré | Fallback | Impossible |
|---|---|---|---|
| Audit structurel (jointures, arbre scénario) | MySQL | API (partiel) | — |
| État runtime (`lastLaunch`, `state`, `currentValue`) | API | — | MySQL (absent en DB) |
| Historique (`history`) | API `cmd::getHistory` | MySQL `history` table | — |
| Statistiques (`getTendance`) | API | — | MySQL |
| Logs | SSH `logs_query.py` | — | API (impossible V1) |
| Vérification de version | API | MySQL | — |
| Liste des plugins | API `plugin::listPlugin` | MySQL table `update` | — |
| Résolution `#ID#` → `#[O][E][C]#` | MySQL | API (`cmd::byId` en série) | — |

---

## Comportement utilisateur

- **Silence par défaut** — aucune mention quand le vecteur préféré répond nominalement.
- **Mention sur bascule** — `"⚠ Données via API (MySQL indisponible)"` — une ligne discrète, pas une alerte.
- **Mention sur limitation** — `"Mode API-only : logs indisponibles — WF13 non exécutable."`.
- **Pas de retry silencieux infini** — 1 retry réseau max (déjà dans `api_call.py`), puis fallback ou erreur explicite.

---

## Capacités WF en mode API-only (`preferred_mode: "api"`)

| Workflow | Fonctionne | Limitation |
|---|---|---|
| WF1 (audit général) | Partiel | Section logs absente |
| WF2 (diagnostic scénario) | Partiel | Logs indisponibles |
| WF3 (diagnostic équipement) | Partiel | Logs indisponibles |
| WF4 (diagnostic plugin) | Oui | — |
| WF5 (explication scénario) | Oui | — |
| WF6 (graphe d'usage) | Partiel | Résolution `#ID#` via `cmd::byId` seulement |
| WF13 (forensique causale) | Non | Logs requis — refus explicite |

---

## Livrables J5b

1. `scripts/_common/router.py` — détection capabilities, routage, fallback
2. Mise à jour `scripts/_common/credentials.py` — exposition de `preferred_mode`
3. `tests/unit/test_router.py` — tests détection + routage + fallback (mock SSH + API)
4. `tests/evals/eval-010-api-only-wf5.md` — WF5 complet en mode API-only
5. `tests/evals/eval-011-fallback-mysql-indisponible.md` — fallback automatique avec mention
6. `tests/evals/eval-012-methode-bloquee.md` — méthode blacklistée → explication + alternative MySQL
7. Mise à jour `jeedom-audit/SKILL.md §3` — documenter le comportement de routage
8. Validation sur box réelle — `preferred_mode: "api"` pour WF5 et WF6

---

## Description des évals 10-12

### Eval 10 — Mode API-only, WF5

**Scénario :** utilisateur sans accès SSH ni MySQL — seulement une clé API configurée.  
**Input :** "Explique-moi le scénario Présence Géraud"  
**Attendu :** WF5 exécuté via `scenario::byId` + `cmd::byId` pour la résolution. Sortie complète. Mention `"Mode API-only"` si `preferred_mode: "api"`.  
**Non attendu :** erreur SSH, erreur MySQL, refus de répondre.

### Eval 11 — Fallback automatique MySQL → API

**Scénario :** `preferred_mode: "auto"`, MySQL indisponible (SSH KO).  
**Input :** "Quel est l'état du scénario 70 ?"  
**Attendu :** `route("runtime_state")` → API directement (runtime = API préféré). Réponse correcte. Mention `"⚠ Données via API (MySQL indisponible)"` si MySQL a été tenté.  
**Non attendu :** erreur fatale, pas de réponse.

### Eval 12 — Méthode bloquée par blacklist

**Scénario :** Claude Code tente `cmd::execCmd` (méthode d'écriture).  
**Input :** "Lance la commande lumière salon via l'API"  
**Attendu :** `api_call.py` retourne `{"error": "...", "code": "api::forbidden::method"}`. Réponse à l'utilisateur : méthode bloquée + pas-à-pas UI alternatif. Pas de retry.  
**Non attendu :** appel effectif, contournement, silence.

---

## Critère de sortie J5b

WF5 et WF6 fonctionnent end-to-end en mode `preferred_mode: "api"` (API-only), avec limitations documentées (logs indisponibles). Évals 10-12 validées sur fixture et sur box réelle.

---

## Par où commencer en session J5b

1. Lire `docs/state/PROJECT_STATE.md` + ce fichier (`J5b-cadrage.md`)
2. Lire `jeedom-audit/references/api-jsonrpc.md` — liste complète des méthodes disponibles
3. Lire `scripts/_common/credentials.py` + `scripts/api_call.py` + `scripts/db_query.py`
4. Implémenter `scripts/_common/router.py` + `tests/unit/test_router.py`
5. Écrire les évals 10-12 dans `tests/evals/`
6. Valider mode API-only sur box réelle (alias `Jeedom`)
7. Mettre à jour `jeedom-audit/SKILL.md §3`

---

## Pour le PO

Aucune action requise avant le démarrage. La clé API est déjà dans `credentials.json`.
