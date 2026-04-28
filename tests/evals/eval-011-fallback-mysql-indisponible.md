---
id: eval-011
titre: Fallback automatique MySQL → API (MySQL indisponible)
jalon: J5b
---

# Eval 011 — Fallback automatique MySQL → API

## Contexte

`preferred_mode: "auto"`. La connexion SSH/MySQL est indisponible (réseau KO, alias SSH non configuré, ou tunnel fermé).  
L'API JSON-RPC est disponible.

## Input utilisateur

> "Quel est l'état du scénario 70 ?"

## Configuration credentials

```json
{
  "preferred_mode": "auto",
  "ssh_alias": "Jeedom",
  "db_name": "jeedom",
  "api_url": "https://jeedom.local",
  "api_key": "<clé>",
  "verify_ssl": false
}
```

## Comportement attendu

1. `router.detect_capabilities(creds)` → `{"mysql": False, "api": True}`
2. `router.route("runtime_state", creds)` → `"api"` (runtime_state est API-preferred de toute façon)
3. Appel `api_call.run("scenario::byId", {"id": 70})` → `state`, `lastLaunch`
4. Réponse correcte à l'utilisateur avec l'état du scénario
5. Si MySQL a été tenté avant détection : mention `"⚠ Données via API (MySQL indisponible)"`

**Note :** pour `runtime_state`, MySQL n'est jamais la source préférée — la mention n'apparaît que si une tentative MySQL a eu lieu et échoué (via `with_fallback`).

## Comportement non attendu

- Erreur fatale ou exception non gérée
- Pas de réponse à l'utilisateur
- Retry infini sur SSH
- Mention d'erreur alarmiste (une ligne discrète suffit)

## Script de vérification (fixture)

```bash
python3 -c "
import sys; sys.path.insert(0, 'jeedom-audit/scripts')
from _common import router
from unittest.mock import MagicMock, patch

creds = {
    'preferred_mode': 'auto',
    'ssh_alias': 'Jeedom',
    'db_name': 'jeedom',
    'api_url': 'https://jeedom.local',
    'api_key': 'test',
}

# Simuler MySQL KO, API OK
with patch.object(router._ssh, 'mysql_json', return_value=MagicMock(ok=False)), \
     patch.object(router._api_call, 'run', return_value={'result': 'ok'}):
    caps = router.detect_capabilities(creds)
    print('caps:', caps)                           # {"mysql": False, "api": True}
    print('route:', router.route('runtime_state', creds))  # api
"
```

## Test with_fallback intégré

```python
# Exemple d'usage with_fallback pour structural_audit avec MySQL KO
from _common.router import with_fallback

result, mention = with_fallback(
    primary_fn=lambda: {"error": "SSH timeout"},
    fallback_fn=lambda: {"result": [{"id": "70", "name": "Présence Géraud"}]},
    mention="⚠ Données via API (MySQL indisponible)",
)
assert mention == "⚠ Données via API (MySQL indisponible)"
assert "result" in result
```

## Résultat sur box réelle

| Date | Résultat | Notes |
|---|---|---|
| 2026-04-27 | à valider | Simuler SSH KO en désactivant l'alias |
