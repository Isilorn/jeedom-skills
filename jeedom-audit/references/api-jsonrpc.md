---
title: Référence API JSON-RPC Jeedom — jeedom-audit
description: Méthodes JSON-RPC autorisées et blacklistées, format requête/réponse, codes d'erreur — utilisées par scripts/api_call.py
updated: 2026-04-27
---

# API JSON-RPC Jeedom — Référence

> **Usage dans la skill :** toutes les interactions API passent par `scripts/api_call.py`.  
> L'API est secondaire à MySQL en mode `auto` — elle est préférée pour les données runtime (état, historique, statistiques).  
> Pour la couche transport (SSL, auth, test de connectivité), voir `references/api-http.md`.

---

## 1. Format de requête/réponse

**Endpoint :** `POST http(s)://<ip>/core/api/jeeApi.php`  
**Header :** `Content-Type: application/json`

**Requête :**
```json
{
  "jsonrpc": "2.0",
  "method": "scenario::byId",
  "params": {
    "apikey": "<votre_clé_api>",
    "id": 70
  },
  "id": 1
}
```

**Réponse — succès :**
```json
{
  "jsonrpc": "2.0",
  "result": { "id": "70", "name": "Présence Géraud", "state": "stop", "lastLaunch": "2026-04-27 08:12:00" },
  "id": 1
}
```

**Réponse — erreur :**
```json
{
  "jsonrpc": "2.0",
  "error": { "code": -32601, "message": "Méthode inconnue" },
  "id": 1
}
```

---

## 2. Méthodes autorisées V1

### Sanity

| Méthode | Params requis | Résultat |
|---|---|---|
| `ping` | — | `"ok"` |
| `version` | — | `"4.5.3"` |
| `config::byKey` | `key`, `plugin` | valeur de config |

Exemple `config::byKey` :
```json
{"method": "config::byKey", "params": {"key": "name", "plugin": "core"}}
```

---

### Découverte

| Méthode | Params requis | Résultat |
|---|---|---|
| `jeeObject::all` | — | array d'objets (pièces) |
| `jeeObject::byId` | `id` | objet par ID |
| `jeeObject::full` | `id` | objet + eqLogics + cmds imbriqués |
| `eqLogic::all` | — | tous les équipements |
| `eqLogic::byType` | `type` | eqLogics par type plugin (ex: `"virtual"`) |
| `eqLogic::byId` | `id` | équipement par ID |
| `eqLogic::fullById` | `id` | équipement + toutes ses cmds |
| `cmd::all` | — | toutes les commandes (volumineux) |
| `cmd::byId` | `id` | commande par ID — inclut `currentValue` et `collectDate` |

---

### Données runtime

Ces méthodes retournent des données **absentes de la base MySQL** — elles ne peuvent être obtenues que via l'API.

| Méthode | Params requis | Résultat |
|---|---|---|
| `cmd::getHistory` | `id`, `startTime`, `endTime` | historique de la commande sur la période |
| `cmd::getStatistique` | `id`, `startTime`, `endTime` | min / max / avg / somme sur la période |
| `cmd::getTendance` | `id`, `startTime`, `endTime` | tendance (hausse / baisse / stable) |

Format des dates : `"YYYY-MM-DD HH:MM:SS"`.

Exemple `cmd::getHistory` :
```json
{
  "method": "cmd::getHistory",
  "params": {
    "id": 15663,
    "startTime": "2026-04-20 00:00:00",
    "endTime": "2026-04-27 23:59:59"
  }
}
```

---

### Scénarios

| Méthode | Params requis | Résultat |
|---|---|---|
| `scenario::all` | — | tous les scénarios — inclut `state` et `lastLaunch` |
| `scenario::byId` | `id` | scénario par ID — inclut `state`, `lastLaunch`, `scenarioElement` |

`state` : `"run"` / `"stop"` / `"error"` / `"in progress"`  
`lastLaunch` : datetime de la dernière exécution, ou vide si jamais lancé.

---

### Résumés

| Méthode | Params requis | Résultat |
|---|---|---|
| `summary::global` | — | résumé global (températures, lumières, prises, etc.) |
| `summary::byObjectId` | `id` | résumé pour une pièce (objet Jeedom) |

---

### Système

| Méthode | Params requis | Résultat |
|---|---|---|
| `plugin::listPlugin` | — | tous les plugins installés — inclut `state`, `version`, daemon |
| `event::changes` | — | événements récents (polling) — usage interne Jeedom |

`plugin::listPlugin` est la source préférée pour WF4 (diagnostic plugin) — plus complète que la table MySQL `update` pour l'état du daemon.

---

## 3. Blacklist V1 (lecture seule)

Toute méthode dans cette liste est **rejetée par `api_call.py` avant envoi** à Jeedom.

**Méthodes explicitement bloquées :**
- `cmd::execCmd`
- `scenario::changeState`
- `datastore::save`
- `interact::tryToReply`

**Verbes bloqués par pattern** (dans tout nom de méthode) :  
`::save`, `::exec`, `::delete`, `::remove`, `::update`, `::set`, `::add`, `::create`, `::send`, `::apply`, `::move`, `::copy`, `::import`, `::export`

Réponse en cas de tentative blacklistée :
```json
{
  "error": "Méthode blacklistée V1 (lecture seule) : \"cmd::execCmd\"",
  "code": "api::forbidden::method"
}
```

---

## 4. Champs runtime — disponibles via API uniquement

Ces champs sont **absents de la base MySQL** — impossible de les obtenir par `db_query.py`.

| Objet | Champ | Via |
|---|---|---|
| Scénario | `lastLaunch` | `scenario::byId` ou `scenario::all` |
| Scénario | `state` (`run` / `stop` / `error`) | `scenario::byId` ou `scenario::all` |
| Commande info | `currentValue` | `cmd::byId` |
| Commande info | `collectDate` | `cmd::byId` |
| Plugin | état daemon | `plugin::listPlugin` |

---

## 5. Utilisation via `api_call.py`

```bash
# Ping
echo '{"method": "ping"}' | python3 scripts/api_call.py

# État + lastLaunch d'un scénario
echo '{"method": "scenario::byId", "params": {"id": 70}}' | python3 scripts/api_call.py

# Historique d'une commande (7 derniers jours)
echo '{"method": "cmd::getHistory", "params": {"id": 15663, "startTime": "2026-04-20 00:00:00", "endTime": "2026-04-27 23:59:59"}}' | python3 scripts/api_call.py

# Liste des plugins avec état daemon
echo '{"method": "plugin::listPlugin"}' | python3 scripts/api_call.py
```

**Sortie `api_call.py` — succès :**
```json
{
  "result": { "..." : "..." },
  "_filtered_fields": ["password", "api"]
}
```

**Sortie `api_call.py` — erreur :**
```json
{
  "error": "message d'erreur",
  "code": "api::forbidden::method"
}
```

---

## 6. Codes d'erreur fréquents

| Code | Source | Signification | Action |
|---|---|---|---|
| `-32601` | Jeedom | Méthode inconnue | Vérifier le nom exact |
| `-32602` | Jeedom | Paramètre invalide | Vérifier les params requis |
| `-32603` | Jeedom | Clé API invalide ou absente | Vérifier `api_key` dans `credentials.json` |
| `"api::forbidden::method"` | `api_call.py` | Méthode bloquée par blacklist V1 | Ne pas tenter d'écriture |
| `_transport_error` | `api_call.py` | Erreur réseau ou SSL | Vérifier `api_url` et `verify_ssl` |

---

## 7. Gotchas API

| Gotcha | Détail |
|---|---|
| `apikey` dans `params`, pas dans les headers | Contrairement aux API REST standard, la clé est dans le body JSON-RPC |
| `eqLogic::fullById` peut être volumineux | Sur des équipements jMQTT avec beaucoup de commandes — préférer `eqLogic::byId` + `cmd::all` filtrés |
| `cmd::getHistory` sans bornes temporelles | Retourne tout l'historique — toujours borner `startTime` / `endTime` |
| `event::changes` est un long-poll | Conçu pour des updates asynchrones — ne pas appeler en boucle courte |
| `verify_ssl: false` dans `credentials.json` | Nécessaire si Jeedom utilise un certificat auto-signé (LAN sans FQDN) |
