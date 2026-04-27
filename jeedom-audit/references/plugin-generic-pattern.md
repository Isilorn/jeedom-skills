# Pattern d'inspection générique — Plugins non tier-1

**Version** : J4 (2026-04-27)

Ce document décrit la procédure d'inspection en 4 temps applicable à tout plugin Jeedom qui n'a pas de fichier de référence dédié dans `references/`. Il couvre l'ensemble des plugins non tier-1, y compris MQTT Manager (souvent présent comme dépendance transparente d'autres plugins).

---

## Quand appliquer ce pattern

Utiliser ce pattern quand :
- L'utilisateur pose une question impliquant un plugin qui n'est pas `virtual`, `jMQTT`, `calendar`, `script`, `alarm` ou `thermostat`
- Le plugin est identifié dans `eqLogic.eqType_name` ou dans la liste des plugins installés

---

## Temps 1 — Identifier le plugin

```sql
SELECT e.eqType_name, COUNT(*) AS nb, SUM(e.isEnable) AS actifs
FROM eqLogic e
WHERE e.eqType_name = params['plugin']
GROUP BY e.eqType_name
```

Puis vérifier l'état du plugin dans la table `update` :
```sql
SELECT name, version, status
FROM update
WHERE logicalId = params['plugin']
  AND type = 'plugin'
```

Compléter avec l'API pour l'état du daemon si applicable :
```
plugin::listPlugin  → champ "daemon" de l'objet plugin
```

---

## Temps 2 — Inspecter les eqLogics

```sql
SELECT e.id, e.name, e.isEnable, e.isVisible, e.configuration
FROM eqLogic e
WHERE e.eqType_name = params['plugin']
ORDER BY e.isEnable DESC, e.name
LIMIT 20
```

Points à noter :
- Nombre d'équipements actifs vs inactifs
- Présence de `configuration` non vide (indique une config avancée)
- `object_id` pour localiser les équipements dans la hiérarchie Jeedom

---

## Temps 3 — Inspecter les commandes

```sql
SELECT c.id, c.name, c.logicalId, c.type, c.subType,
       c.value, c.configuration
FROM cmd c
JOIN eqLogic e ON e.id = c.eqLogic_id
WHERE e.eqType_name = params['plugin']
  AND e.isEnable = 1
ORDER BY e.id, c.id
LIMIT 50
```

Points à noter :
- Pattern de commandes exposées (info/action, types)
- Présence de `logicalId` standardisés (ex: `refresh`, `enable`, `state`) — indique un plugin bien structuré
- Valeurs récentes (`cmd.value`) pour évaluer si le plugin communique

---

## Temps 4 — Consulter les logs

```python
scripts/logs_query.py --log params['plugin'] --lines 50
```

Si le plugin a un daemon :
```python
scripts/logs_query.py --log params['plugin'] + "_dep" --lines 50
```

Patterns à chercher dans les logs :
- `[ERROR]` ou `[WARNING]` — problèmes actifs
- `Demon` ou `daemon` — état du processus de communication
- `Timeout` ou `connexion` — problèmes réseau/communication
- Absence totale de logs récents — plugin inactif ou silencieux

---

## Cas MQTT Manager

MQTT Manager (`eqType_name = 'mqtt2'`) est souvent installé comme **dépendance** de ZeeZigbee, zwavejs ou d'autres plugins, sans que l'utilisateur le configure directement. Son rôle est de gérer un broker Mosquitto embarqué.

Vérification rapide :
```sql
SELECT e.id, e.name, e.isEnable, e.configuration
FROM eqLogic e
WHERE e.eqType_name = 'mqtt2'
```

Si présent et daemon KO :
```python
scripts/logs_query.py --log mqtt2 --lines 30
scripts/logs_query.py --log mqtt2_dep --lines 30
```

Le daemon MQTT Manager partagé avec jMQTT peut générer des conflits de port si les deux sont actifs simultanément (deux brokers sur le même port 1883). Dans ce cas, l'un des deux doit utiliser un port différent.

---

## Limites du pattern générique

Ce pattern couvre l'inspection de surface (état, commandes, logs). Pour un diagnostic approfondi d'un plugin spécifique (structure de configuration, tables dédiées, variables spéciales), il est nécessaire de :
1. Consulter la documentation officielle du plugin
2. Explorer les tables spécifiques du plugin (`SHOW TABLES LIKE '%<plugin>%'`)
3. Créer un fichier `references/plugin-<nom>.md` si le plugin est suffisamment complexe ou fréquent

---

## Plugins connus avec tables dédiées

| Plugin | Table(s) spécifique(s) | Note |
|---|---|---|
| `calendar` | `calendar_event` | événements et règles de récurrence |
| Autres | à découvrir via `SHOW TABLES` | explorer au cas par cas |
