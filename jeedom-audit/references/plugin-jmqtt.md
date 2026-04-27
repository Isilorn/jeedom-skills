# Référence plugin — jMQTT

**Version testée** : compatible Jeedom ≥ 4.3.12 — testé sur Jeedom 4.5.3 (box réelle, 2026-04-27)
**Catégorie** : Automation protocol — Daemon : oui (`mosquitto` ou broker embarqué) — Dépendances : Python/pip, PHP-MQTT

---

## 1. Identification

jMQTT est le bridge MQTT natif de Jeedom. Il abonne Jeedom à des topics MQTT et crée automatiquement des commandes à partir des messages reçus. Sur la box de référence : 59 eqLogics jMQTT, tous actifs, principalement des capteurs Zigbee via Zigbee2MQTT.

Identification DB : `eqLogic.eqType_name = 'jMQTT'`

---

## 2. Structure eqLogic

| Champ DB | Valeurs typiques | Signification |
|---|---|---|
| `eqType_name` | `jMQTT` | type plugin |
| `isEnable` | `1` | quasi-systématiquement actif |
| `configuration` | JSON avec `"mqttId"`, `"topic"`, `"qos"` | config broker + topic racine |

Exemple de `eqLogic.configuration` (valeurs sensibles filtrées) :
```json
{
  "mqttId": "1",
  "topic": "zigbee2mqtt/0x00158d0003ceaa01",
  "qos": "1",
  "isListened": "1",
  "sendToJeedom": "1"
}
```

`mqttId` référence le broker jMQTT configuré (id de l'eqLogic broker parent).

---

## 3. Structure des commandes

### Pattern typique (capteur Zigbee via Zigbee2MQTT)

```
cmd info/string    "0x00158d0003ceaa01"   logicalId="NULL"   jsonPath=""         ← dump JSON brut
cmd info/numeric   "Batterie"             logicalId="NULL"   jsonPath="[battery]"
cmd info/binary    "Contact"              logicalId=""       jsonPath="[contact]"
cmd info/numeric   "Link"                 logicalId="NULL"   jsonPath="[linkquality]"
cmd info/numeric   "Temperature"          logicalId="NULL"   jsonPath="[temperature]"
cmd info/string    "Last seen"            logicalId="NULL"   jsonPath="[last_seen]"
cmd info/string    "availability"         logicalId="NULL"   topic spécifique      ← topic /availability
```

### Champs clés dans `cmd.configuration` (JSON)

| Champ | Rôle |
|---|---|
| `topic` | topic MQTT complet de la commande (peut différer du topic parent) |
| `jsonPath` | chemin d'extraction dans le payload JSON reçu — ex. `[battery]`, `[contact]` |
| `historizeMode` | `avg`, `none` — mode d'historisation |
| `timeline::enable` | `0`/`1` — timeline Jeedom |

**`logicalId = "NULL"` (string)** : commandes auto-créées par jMQTT à la réception d'un message. Distinct de `logicalId = ""` qui est une commande créée manuellement.

### Topic `/availability`

Les capteurs Zigbee2MQTT publient sur `<topic_racine>/availability` leur statut online/offline. jMQTT crée automatiquement une commande `availability` sur un topic distinct du topic parent de l'eqLogic.

---

## 4. Points d'audit

**Anti-patterns fréquents :**
- eqLogic jMQTT avec `isEnable=1` mais daemon jMQTT arrêté → toutes les commandes info figées à leur dernière valeur, sans erreur visible
- Commande avec `jsonPath` invalide → valeur `NULL` ou vide, silencieux
- Topic parent trop large (ex. `#`) → explosion du nombre de commandes auto-créées
- `availability` offline mais valeurs récentes → capteur offline mais Jeedom n'a pas détecté la rupture

**Requête utile — commandes jMQTT sans valeur récente (>24h) :**
```sql
SELECT c.id, c.name, e.name AS eqLogic_name, c.currentValue, c.collectDate
FROM cmd c
JOIN eqLogic e ON e.id = c.eqLogic_id
WHERE e.eqType_name = 'jMQTT'
  AND c.type = 'info'
  AND c.isHistorized = 1
  AND (c.collectDate IS NULL
       OR c.collectDate < NOW() - INTERVAL 24 HOUR)
ORDER BY c.collectDate ASC
LIMIT 20
```

**Requête utile — eqLogics jMQTT avec commande availability offline :**
```sql
SELECT e.id, e.name, c.currentValue AS availability
FROM eqLogic e
JOIN cmd c ON c.eqLogic_id = e.id AND c.name = 'availability'
WHERE e.eqType_name = 'jMQTT'
  AND c.currentValue NOT IN ('online', '1', '')
```

---

## 5. Daemon

jMQTT dispose d'un daemon PHP/Python qui maintient la connexion MQTT. Points clés :

- **Vérification statut** : disponible via `plugin::listPlugin` (champ `functionality.cron`) — le statut runtime est dans le log `jMQTT`
- **Log daemon** : `/var/www/html/log/jMQTT` — erreurs de connexion broker, messages reçus en debug
- **Redémarrage** : UI uniquement (Plugins > Protocoles domotiques > jMQTT > Daemon)
- **Si daemon arrêté** : aucune commande info ne se met à jour, mais `isEnable=1` en DB — diagnostic trompeur

```json
// Lecture du log jMQTT via logs_query :
{"log": "jMQTT", "lines": 50, "grep": "ERROR"}
```

---

## 6. Interactions scénarios

Les commandes jMQTT sont des sources de déclenchement fréquentes (`trigger` = topic MQTT via event jMQTT). Dans les logs de scénario, le trigger est identifié par :

```
#trigger# = "jMQTTCmd"
#trigger_name# = "[Bluetooth][Présence Shelly Géraud][present]"
#trigger_id# = "15663"
```

WF2 (diagnostic scénario) : si un scénario déclenché par jMQTT ne s'exécute pas, vérifier d'abord que le daemon jMQTT est actif et que le topic publie.

---

## 7. Sécurité / lecture seule

`cmd.configuration` peut contenir des credentials MQTT si le broker nécessite une authentification. `filter_rows` redacte automatiquement les champs contenant `mqttPassword`, `mqttpass`, `password`, `token`.

Lors d'un audit, mentionner si des credentials MQTT apparaissent — suggérer d'utiliser un user MQTT dédié avec permissions minimales.

---

## 8. Patterns de log

- `/var/www/html/log/jMQTT` — log principal daemon (connexion, messages reçus)
- `/var/www/html/log/jMQTT_dep` — installation des dépendances Python
- `/var/www/html/log/scenarioLog/scenario{ID}.log` — scénarios déclenchés par jMQTT

Lecture type pour diagnostic :
```json
{"log": "jMQTT", "lines": 100, "grep": "ERROR"}
{"log": "jMQTT", "lines": 100, "grep": "MQTT"}
```

---

## 9. Liens

- Documentation officielle : https://jmqtt.onl/
- GitHub : https://github.com/domotruc/jMQTT
- Changelog Jeedom Market : disponible sur le plugin dans l'UI
