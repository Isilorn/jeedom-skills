---
id: eval-010
titre: Mode API-only — WF5 explication scénario
jalon: J5b
---

# Eval 010 — Mode API-only, WF5 (explication scénario)

## Contexte

Utilisateur sans accès SSH ni MySQL : seule une clé API Jeedom est configurée dans `credentials.json`.  
`preferred_mode: "api"` dans le fichier credentials.

## Input utilisateur

> "Explique-moi le scénario Présence Géraud"

## Configuration credentials

```json
{
  "preferred_mode": "api",
  "api_url": "https://jeedom.local",
  "api_key": "<clé>",
  "verify_ssl": false
}
```
*(Pas d'alias SSH ni de `db_name` configurés.)*

## Comportement attendu

1. `router.route("structural_audit", creds)` → `"api"`
2. `router.route("runtime_state", creds)` → `"api"`
3. `router.route("logs", creds)` → `"ssh"` — logs signalés indisponibles

**Appels API effectués :**
- `scenario::all` ou `scenario::byId` pour récupérer le scénario "Présence Géraud"
- `cmd::byId` pour chaque `#ID#` rencontré dans `scenarioElement` (résolution en série)
- `scenario::byId` pour récupérer `state` et `lastLaunch`

**Sortie attendue :**
- Explication complète du scénario avec les noms résolus (`#[Maison][Présence Géraud][BLE présent]#`)
- Mention discrète d'une ligne : `"Mode API-only : logs indisponibles pour ce workflow."`
- Pas d'erreur fatale, pas de refus de répondre

## Comportement non attendu

- Erreur SSH ou timeout SSH
- Erreur MySQL
- Refus de répondre ou message d'erreur bloquant
- Tentative de résolution `#ID#` via MySQL
- Absence de la mention mode API-only

## Script de vérification (fixture)

```bash
# Simuler credentials API-only
export JEEDOM_PREFERRED_MODE=api
export JEEDOM_API_URL=https://jeedom.local
export JEEDOM_API_KEY=<clé>

# Appel router
python3 -c "
import sys; sys.path.insert(0, 'jeedom-audit/scripts')
from _common import router
creds = {'preferred_mode': 'api', 'api_url': 'https://jeedom.local', 'api_key': 'test'}
print(router.route('structural_audit', creds))   # → api
print(router.route('runtime_state', creds))       # → api
print(router.route('logs', creds))                # → ssh
"
```

## Résultat sur box réelle

| Date | Résultat | Notes |
|---|---|---|
| 2026-04-27 | à valider | Session J5b |
