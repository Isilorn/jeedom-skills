---
title: SQL Cookbook — jeedom-audit
description: Requêtes SQL de référence par famille, testées sur box réelle (Jeedom 4.5). Toutes les requêtes sont passées à `db_query.run()` — pas besoin d'échapper `trigger` manuellement, `db_query.py` le fait automatiquement.
updated: 2026-04-27
---

# SQL Cookbook — jeedom-audit

> **Utilisation :** passer chaque requête à `db_query.run(query, params, creds)`.  
> `trigger` est auto-backtické par `db_query.py` — l'écrire sans backticks dans ce fichier.  
> Les `?` sont des paramètres positionnels (anti-injection).

---

## 1. Système et configuration

### Version Jeedom
```sql
SELECT value FROM config WHERE `key` = 'version' AND plugin = 'core';
```

### Clé API (chiffrée — utiliser `version_check.py` pour la déchiffrer via SSH/PHP)
```sql
SELECT value FROM config WHERE `key` = 'api' AND plugin = 'core';
```

### Toute la configuration core utile à l'audit
```sql
SELECT `key`, value
FROM config
WHERE plugin = 'core'
  AND `key` IN ('version', 'name', 'market::allowDNS', 'updateManager::lastCheck',
                'hardware_name', 'internalAddr', 'externalAddr')
ORDER BY `key`;
```

---

## 2. Plugins installés

### Liste complète avec version et état
```sql
SELECT id, name, version, isEnable, state
FROM update
WHERE type = 'plugin'
ORDER BY name;
```

### Plugins avec mises à jour disponibles
```sql
SELECT id, name, version, status
FROM update
WHERE type = 'plugin' AND status != 'ok'
ORDER BY name;
```

### Plugins actifs seulement
```sql
SELECT id, name, version
FROM update
WHERE type = 'plugin' AND isEnable = 1
ORDER BY name;
```

---

## 3. Équipements — `eqLogic`

### Comptage global
```sql
SELECT COUNT(*) AS total,
       SUM(isEnable = 1) AS actifs,
       SUM(isEnable = 0) AS desactives
FROM eqLogic;
```

### Liste complète avec pièce et plugin
```sql
SELECT e.id, e.name, e.eqType_name, e.isEnable,
       o.name AS objet
FROM eqLogic e
LEFT JOIN object o ON e.object_id = o.id
ORDER BY o.name, e.name;
```

### Chercher par nom (insensible à la casse)
```sql
SELECT e.id, e.name, e.eqType_name, e.isEnable,
       o.name AS objet
FROM eqLogic e
LEFT JOIN object o ON e.object_id = o.id
WHERE e.name LIKE ?;
-- params: ['%presence%']
```

### Équipements par plugin
```sql
SELECT id, name, isEnable
FROM eqLogic
WHERE eqType_name = ?
ORDER BY name;
-- params: ['jMQTT']
```

### Détail complet d'un équipement (configuration JSON inclus)
```sql
SELECT e.id, e.name, e.eqType_name, e.isEnable,
       e.configuration, e.status,
       o.name AS objet
FROM eqLogic e
LEFT JOIN object o ON e.object_id = o.id
WHERE e.id = ?;
-- params: [705]
```

### Équipements en warning ou danger (champ status JSON)
```sql
SELECT id, name, eqType_name, status
FROM eqLogic
WHERE JSON_UNQUOTE(JSON_EXTRACT(status, '$.warning')) != ''
   OR JSON_UNQUOTE(JSON_EXTRACT(status, '$.danger')) != '';
```

### Équipements désactivés mais référencés dans des scénarios
```sql
SELECT DISTINCT e.id, e.name, e.eqType_name
FROM eqLogic e
JOIN cmd c ON c.eqLogic_id = e.id
WHERE e.isEnable = 0
  AND EXISTS (
    SELECT 1 FROM scenarioExpression expr
    WHERE expr.expression LIKE CONCAT('%#', c.id, '#%')
  );
```

---

## 4. Commandes — `cmd`

### Toutes les commandes d'un équipement
```sql
SELECT c.id, c.name, c.type, c.subType, c.value,
       c.isHistorized, c.configuration
FROM cmd c
WHERE c.eqLogic_id = ?
ORDER BY c.type, c.name;
-- params: [705]
```

### Résolution d'une liste d'IDs → noms [O][E][C]
```sql
SELECT c.id,
       o.name AS objet,
       e.name AS equipement,
       c.name AS commande,
       c.type, c.subType
FROM cmd c
JOIN eqLogic e ON c.eqLogic_id = e.id
LEFT JOIN object o ON e.object_id = o.id
WHERE c.id IN (15663, 15669, 15670);
-- Adapter la liste d'IDs ; utiliser resolve_cmd_refs.py en batch
```

### Commandes mortes (équipement désactivé ou supprimé)
```sql
SELECT c.id, c.name, c.eqLogic_id
FROM cmd c
LEFT JOIN eqLogic e ON c.eqLogic_id = e.id
WHERE e.id IS NULL OR e.isEnable = 0
ORDER BY c.eqLogic_id;
```

### Commandes sans Type Générique (anti-pattern WF7)
```sql
SELECT c.id, c.name, c.type, c.subType,
       e.name AS equipement, e.eqType_name
FROM cmd c
JOIN eqLogic e ON c.eqLogic_id = e.id
WHERE c.type = 'info'
  AND (c.generic_type IS NULL OR c.generic_type = '')
ORDER BY e.name, c.name;
```

### Valeurs courantes de plusieurs commandes
```sql
SELECT c.id, c.name, c.value, c.type, c.subType,
       e.name AS equipement
FROM cmd c
JOIN eqLogic e ON c.eqLogic_id = e.id
WHERE c.id IN (15663, 15669, 1111);
```

### Commandes jMQTT : topic et jsonPath
```sql
SELECT c.id, c.name,
       JSON_UNQUOTE(JSON_EXTRACT(c.configuration, '$.topic')) AS topic,
       JSON_UNQUOTE(JSON_EXTRACT(c.configuration, '$.jsonPath')) AS json_path
FROM cmd c
JOIN eqLogic e ON c.eqLogic_id = e.id
WHERE e.eqType_name = 'jMQTT'
  AND c.type = 'info'
ORDER BY topic;
```

### Broker jMQTT : topic d'écoute entrant
```sql
SELECT e.id, e.name,
       JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.mqttAddress')) AS broker_addr,
       JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.mqttPort')) AS broker_port,
       JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.mqttIncTopic')) AS inc_topic
FROM eqLogic e
WHERE e.eqType_name = 'jMQTT'
  AND JSON_EXTRACT(e.configuration, '$.mqttAddress') IS NOT NULL;
```

---

## 5. Scénarios — `scenario`

### Comptage global
```sql
SELECT COUNT(*) AS total,
       SUM(isActive = 1) AS actifs,
       SUM(isActive = 0) AS inactifs
FROM scenario;
```

### Liste complète avec mode et triggers
```sql
SELECT id, name, isActive, mode, trigger, scenarioElement
FROM scenario
ORDER BY name;
```
> `trigger` contient un JSON array d'IDs : `["#15663#", "#1111#"]`.  
> `lastLaunch` et `state` sont absents de la DB → passer par l'API `scenario::byId`.

### Scénarios actifs seulement
```sql
SELECT id, name, mode, trigger
FROM scenario
WHERE isActive = 1
ORDER BY name;
```

### Chercher un scénario par nom
```sql
SELECT id, name, isActive, mode, trigger, scenarioElement
FROM scenario
WHERE name LIKE ?;
-- params: ['%presence%']
```

### Détail d'un scénario (triggers + IDs d'éléments racine)
```sql
SELECT id, name, isActive, mode, trigger, scenarioElement,
       description, timeout
FROM scenario
WHERE id = ?;
-- params: [70]
```

### Scénarios qui ont un ID de commande donné en trigger
```sql
SELECT id, name, isActive, trigger
FROM scenario
WHERE trigger LIKE ?;
-- params: ['%15663%']
```

### Scénarios en mode schedule (planifiés)
```sql
SELECT id, name, isActive, trigger
FROM scenario
WHERE mode = 'schedule'
ORDER BY name;
```
> `trigger` contient le format CRON Jeedom (`Gi` pour hh:mm, ex. `0730`).

### Scénarios désactivés mais appelés en action depuis d'autres scénarios
```sql
SELECT DISTINCT s.id, s.name
FROM scenario s
WHERE s.isActive = 0
  AND EXISTS (
    SELECT 1 FROM scenarioExpression expr
    WHERE expr.type = 'action'
      AND expr.expression = 'scenario'
      AND JSON_UNQUOTE(JSON_EXTRACT(expr.options, '$.scenario_id')) = CAST(s.id AS CHAR)
  );
```

---

## 6. Contenu des scénarios — traversée de l'arbre

> L'arbre d'un scénario ne se traverse pas en une seule requête SQL.  
> Utiliser `scripts/scenario_tree_walker.py` pour le parcours complet.  
> Les requêtes ci-dessous sont les briques utilisées par ce script.

### Étape 1 — IDs des éléments racine
```sql
SELECT id, name, scenarioElement
FROM scenario
WHERE id = ?;
-- scenarioElement retourne un JSON array d'IDs, ex: ["8", "12"]
-- params: [70]
```

### Étape 2 — Dump plat d'un niveau (liste d'IDs d'éléments connus)
```sql
SELECT
    sel.id      AS element_id,
    ss.id       AS sub_id,
    ss.type     AS ss_type,
    ss.subtype  AS ss_subtype,
    expr.id     AS expr_id,
    expr.order  AS expr_order,
    expr.type   AS expr_type,
    expr.expression,
    expr.options
FROM scenarioExpression expr
JOIN scenarioSubElement ss ON expr.scenarioSubElement_id = ss.id
JOIN scenarioElement sel   ON ss.scenarioElement_id = sel.id
WHERE sel.id IN (8, 9, 511)
ORDER BY sel.id, ss.id, expr.order;
-- Remplacer (8, 9, 511) par les IDs réels extraits de l'étape 1 + récursion
```

### Étape 3 — Trouver les éléments enfants (pour la récursion)
```sql
SELECT DISTINCT CAST(expr.expression AS UNSIGNED) AS child_element_id
FROM scenarioExpression expr
JOIN scenarioSubElement ss ON expr.scenarioSubElement_id = ss.id
WHERE ss.scenarioElement_id IN (8, 9)
  AND expr.type = 'element';
-- Répéter avec les nouveaux IDs jusqu'à stabilisation
```

### Recherche croisée — scénarios qui appellent une commande en action
```sql
SELECT DISTINCT s.id, s.name
FROM scenarioExpression expr
JOIN scenarioSubElement ss  ON expr.scenarioSubElement_id = ss.id
JOIN scenarioElement sel    ON ss.scenarioElement_id = sel.id
JOIN scenario s             ON JSON_CONTAINS(s.scenarioElement, CAST(sel.id AS JSON))
WHERE expr.expression LIKE ?;
-- params: ['%15670%']
```

### Recherche croisée — scénarios qui lancent un autre scénario en action
```sql
SELECT DISTINCT s.id, s.name,
       JSON_UNQUOTE(JSON_EXTRACT(expr.options, '$.scenario_id')) AS appelle_scenario_id
FROM scenarioExpression expr
JOIN scenarioSubElement ss ON expr.scenarioSubElement_id = ss.id
JOIN scenarioElement sel   ON ss.scenarioElement_id = sel.id
JOIN scenario s            ON JSON_CONTAINS(s.scenarioElement, CAST(sel.id AS JSON))
WHERE expr.type = 'action'
  AND expr.expression = 'scenario';
```

---

## 7. Variables — `dataStore`

### Variables globales (tous scénarios)
```sql
SELECT `key`, value, type
FROM dataStore
WHERE type = 'scenario' AND link_id = -1
ORDER BY `key`;
```

### Variable globale spécifique
```sql
SELECT `key`, value
FROM dataStore
WHERE type = 'scenario' AND link_id = -1 AND `key` = ?;
-- params: ['NbAbsGeraud']
```

### Variables locales d'un scénario
```sql
SELECT `key`, value
FROM dataStore
WHERE type = 'scenario' AND link_id = ?
ORDER BY `key`;
-- params: [70]
```

### Toutes les variables avec leur portée
```sql
SELECT `key`, value,
       CASE WHEN link_id = -1 THEN 'globale' ELSE CONCAT('locale-scénario-', link_id) END AS portee
FROM dataStore
WHERE type = 'scenario'
ORDER BY portee, `key`;
```

### Variables globales orphelines (non référencées dans les expressions)
```sql
SELECT d.key, d.value
FROM dataStore d
WHERE d.type = 'scenario' AND d.link_id = -1
  AND NOT EXISTS (
    SELECT 1 FROM scenarioExpression expr
    WHERE expr.expression LIKE CONCAT('%variable(', d.key, ')%')
       OR (expr.options IS NOT NULL AND expr.options LIKE CONCAT('%"', d.key, '"%'))
  );
```

---

## 8. Historique — `history`

### Dernières N valeurs d'une commande
```sql
SELECT datetime, value
FROM history
WHERE cmd_id = ?
ORDER BY datetime DESC
LIMIT 20;
-- params: [15663]
```

### Dernière valeur connue d'une commande
```sql
SELECT datetime, value
FROM history
WHERE cmd_id = ?
ORDER BY datetime DESC
LIMIT 1;
-- params: [15663]
```

### Résumé dernière valeur pour plusieurs commandes
```sql
SELECT h.cmd_id,
       c.name AS commande,
       MAX(h.datetime) AS last_update,
       SUBSTRING_INDEX(GROUP_CONCAT(h.value ORDER BY h.datetime DESC), ',', 1) AS last_value
FROM history h
JOIN cmd c ON h.cmd_id = c.id
WHERE h.cmd_id IN (15663, 15669, 1111)
GROUP BY h.cmd_id, c.name;
```

### Commandes historisées sans entrée récente (commandes potentiellement mortes)
```sql
SELECT c.id, c.name,
       e.name AS equipement,
       MAX(h.datetime) AS derniere_valeur
FROM cmd c
JOIN eqLogic e ON c.eqLogic_id = e.id
LEFT JOIN history h ON h.cmd_id = c.id
WHERE c.isHistorized = 1
GROUP BY c.id, c.name, e.name
HAVING derniere_valeur IS NULL
    OR derniere_valeur < DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY derniere_valeur ASC;
```

### Qualité d'historique — commandes info sans aucune valeur historisée
```sql
SELECT COUNT(*) AS cmd_info_sans_historique
FROM cmd c
WHERE c.type = 'info'
  AND c.isHistorized = 1
  AND NOT EXISTS (SELECT 1 FROM history h WHERE h.cmd_id = c.id);
```

### Historique archivé (mêmes requêtes sur `historyArch`)
```sql
SELECT datetime, value
FROM historyArch
WHERE cmd_id = ?
ORDER BY datetime DESC
LIMIT 20;
-- params: [15663]
```

---

## 9. Messages système — `message`

### Messages récents (erreurs et avertissements)
```sql
SELECT date, type, message, plugin, logicalId
FROM message
ORDER BY date DESC
LIMIT 50;
```

### Messages d'un plugin spécifique
```sql
SELECT date, type, message, logicalId
FROM message
WHERE plugin = ?
ORDER BY date DESC
LIMIT 20;
-- params: ['jMQTT']
```

### Messages d'erreur uniquement
```sql
SELECT date, plugin, message, logicalId
FROM message
WHERE type = 'error'
ORDER BY date DESC
LIMIT 30;
```

---

## 10. Audit rapide — batch WF1

Ensemble de requêtes à enchaîner pour produire le rapport WF1 (audit général).  
Chaque requête peut être exécutée indépendamment via `db_query.run()`.

```python
AUDIT_QUERIES = {
    "version": "SELECT value FROM config WHERE `key` = 'version' AND plugin = 'core'",
    "plugins": "SELECT id, name, version, isEnable, state FROM update WHERE type = 'plugin' ORDER BY name",
    "eqlogic_count": "SELECT COUNT(*) AS total, SUM(isEnable=1) AS actifs FROM eqLogic",
    "scenario_count": "SELECT COUNT(*) AS total, SUM(isActive=1) AS actifs FROM scenario",
    "cmd_count": "SELECT COUNT(*) AS total FROM cmd",
    "dead_cmds": """
        SELECT c.id, c.name, c.eqLogic_id
        FROM cmd c
        LEFT JOIN eqLogic e ON c.eqLogic_id = e.id
        WHERE e.id IS NULL OR e.isEnable = 0
        ORDER BY c.eqLogic_id LIMIT 50
    """,
    "messages_errors": """
        SELECT date, plugin, message
        FROM message
        WHERE type = 'error'
        ORDER BY date DESC LIMIT 20
    """,
    "datastore_globals": """
        SELECT `key`, value FROM dataStore
        WHERE type = 'scenario' AND link_id = -1
        ORDER BY `key`
    """,
    "history_quality": """
        SELECT COUNT(*) AS cmd_info_sans_historique
        FROM cmd c
        WHERE c.type = 'info' AND c.isHistorized = 1
          AND NOT EXISTS (SELECT 1 FROM history h WHERE h.cmd_id = c.id)
    """,
    "updates_available": """
        SELECT id, name, version, status
        FROM update WHERE type = 'plugin' AND status != 'ok'
        ORDER BY name
    """,
}
```

---

---

## 11. Plugins tier-1 — requêtes spécifiques

### Thermostat (`eqType_name = 'thermostat'`)

#### État actuel de tous les thermostats
```sql
SELECT e.id, e.name,
       JSON_UNQUOTE(JSON_EXTRACT(c_order.value,  '$')) AS consigne,
       JSON_UNQUOTE(JSON_EXTRACT(c_temp.value,   '$')) AS temperature,
       JSON_UNQUOTE(JSON_EXTRACT(c_mode.value,   '$')) AS mode,
       JSON_UNQUOTE(JSON_EXTRACT(c_status.value, '$')) AS statut
FROM eqLogic e
JOIN cmd c_order  ON c_order.eqLogic_id  = e.id AND c_order.logicalId  = 'order'
JOIN cmd c_temp   ON c_temp.eqLogic_id   = e.id AND c_temp.logicalId   = 'temperature'
JOIN cmd c_mode   ON c_mode.eqLogic_id   = e.id AND c_mode.logicalId   = 'mode'
JOIN cmd c_status ON c_status.eqLogic_id = e.id AND c_status.logicalId = 'status'
WHERE e.eqType_name = 'thermostat'
  AND e.isEnable = 1;
```
> `cmd.value` est NULL pour la plupart des commandes thermostat — les valeurs runtime sont dans `history`.  
> Si la requête retourne NULL : utiliser `cmd::getHistory` via API ou interroger la table `history`.

#### Coefficients appris (détection de dérive)
```sql
SELECT e.name,
       JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.coeff_indoor_heat'))  AS coeff_interieur,
       JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.coeff_outdoor_heat')) AS coeff_exterieur
FROM eqLogic e
WHERE e.eqType_name = 'thermostat'
ORDER BY CAST(JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.coeff_indoor_heat')) AS DECIMAL) DESC;
```

#### Capteurs de température liés à chaque thermostat
```sql
SELECT e.id, e.name,
       JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.temperature_indoor'))  AS capteur_interieur,
       JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.temperature_outdoor')) AS capteur_exterieur
FROM eqLogic e
WHERE e.eqType_name = 'thermostat';
```

---

### Alarme (`eqType_name = 'alarm'`)

#### Alarmes actives et mode courant
```sql
SELECT e.id, e.name,
       JSON_UNQUOTE(JSON_EXTRACT(c.value, '$')) AS mode_actif
FROM eqLogic e
JOIN cmd c ON c.eqLogic_id = e.id AND c.logicalId = 'mode'
WHERE e.eqType_name = 'alarm'
  AND e.isEnable = 1;
```

#### Nombre de zones et de modes par alarme
```sql
SELECT e.id, e.name,
       JSON_LENGTH(e.configuration, '$.zones') AS nb_zones,
       JSON_LENGTH(e.configuration, '$.modes') AS nb_modes
FROM eqLogic e
WHERE e.eqType_name = 'alarm';
```

---

### Agenda (`eqType_name = 'calendar'`)

#### Agendas actifs avec leurs événements en cours
```sql
SELECT e.id, e.name, ce.cmd_param
FROM eqLogic e
JOIN calendar_event ce ON ce.eqLogic_id = e.id
WHERE e.eqType_name = 'calendar'
  AND e.isEnable = 1
  AND NOW() BETWEEN ce.startDate AND ce.endDate;
```

#### Agendas désactivés
```sql
SELECT id, name
FROM eqLogic
WHERE eqType_name = 'calendar'
  AND isEnable = 0;
```

#### Événements dont les actions référencent des commandes supprimées
```sql
SELECT ce.id, ce.eqLogic_id,
       JSON_UNQUOTE(JSON_EXTRACT(ce.cmd_param, '$.eventName'))   AS event_name,
       JSON_UNQUOTE(JSON_EXTRACT(ce.cmd_param, '$.start[0].cmd')) AS start_cmd
FROM calendar_event ce
WHERE ce.cmd_param LIKE '%#%';
```
*(à croiser avec les IDs de commandes existantes via la table `cmd`)*

#### Tous les événements d'un agenda avec état de récurrence
```sql
SELECT ce.id, ce.startDate, ce.endDate,
       JSON_UNQUOTE(JSON_EXTRACT(ce.cmd_param, '$.eventName'))       AS nom,
       JSON_UNQUOTE(JSON_EXTRACT(ce.`repeat`, '$.enable'))           AS recurrence_active
FROM calendar_event ce
JOIN eqLogic e ON ce.eqLogic_id = e.id
WHERE e.id = ?
ORDER BY ce.startDate;
-- params: [705]
```
> **Important :** `repeat` est un mot réservé MariaDB → backtick obligatoire `` `repeat` ``.  
> Contrairement à `trigger`, `db_query.py` **gère désormais les deux** automatiquement depuis J5.  
> Écrire sans backticks dans les nouvelles requêtes — le wrapper les ajoute.

---

## Notes gotchas

| Gotcha | Détail |
|--------|--------|
| `trigger` mot réservé | Auto-backtické par `db_query.py` — écrire sans backticks dans les requêtes |
| `repeat` mot réservé MariaDB | Auto-backtické par `db_query.py` depuis J5 — idem `trigger` |
| `lastLaunch`, `state` | Absents de la DB → API `scenario::byId` uniquement |
| `cmd.value` thermostat = NULL | Valeurs runtime dans `history` — utiliser `cmd::getHistory` via API si NULL |
| `scenarioSubElement.options = []` | Ne signifie pas vide — les vraies expressions sont dans `scenarioExpression` |
| `scenarioElement` sans FK directe | Les IDs racine sont dans `scenario.scenarioElement` (JSON array) |
| jMQTT topic | `cmd.configuration.topic` (commande info), `eqLogic.configuration.mqttIncTopic` (broker) |
| JSON types mixtes | Un même champ JSON peut être `"1"` ou `1` — utiliser `JSON_UNQUOTE` ou normaliser côté Python |
| `historyArch` | Même structure que `history`, données plus anciennes — interroger les deux si nécessaire |
