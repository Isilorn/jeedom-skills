> **Archive du projet source — ne pas reproduire tel quel.**
> Schéma DB observé empiriquement sur une seule installation — sera cross-checké contre la doc officielle Jeedom 4.5 à J1 (cf. PLANNING §11.1). La commande de connexion ci-dessous a été **expurgée** (password et user remplacés) : voir PLANNING §3.5 pour la stratégie credentials propre (jamais de password en argument CLI).

---

# Jeedom — Référence audit base de données

Connexion : `ssh Jeedom "mysql -u [DB_USER] -p[REDACTED-DB-PASSWORD] jeedom -e \"<QUERY>\" 2>/dev/null"`

---

## Hiérarchie des objets

```
object                          ← pièce/groupe (salon, chambre…)
└── eqLogic                     ← équipement (plugin + config)
    └── cmd                     ← commande info ou action

scenario
└── scenarioElement             ← bloc IF / FOR
    └── scenarioSubElement      ← condition / then / else
        └── scenarioExpression  ← expression réelle (condition ou action)
```

---

## Équipements — `eqLogic`

```sql
-- Chercher par nom
SELECT id, name, eqType_name, isEnable FROM eqLogic WHERE name LIKE '%presence%';

-- Lister par plugin
SELECT id, name, isEnable FROM eqLogic WHERE eqType_name = 'jMQTT';
SELECT id, name, isEnable FROM eqLogic WHERE eqType_name = 'virtual';
```

| Colonne | Contenu |
|---------|---------|
| `eqType_name` | Plugin : `jMQTT`, `virtual`, `JeedomConnect`, `script`… |
| `configuration` | JSON — paramètres spécifiques au plugin |
| `isEnable` | 1 = actif |
| `object_id` | FK vers `object` (pièce) |

---

## Commandes — `cmd`

```sql
-- Toutes les commandes d'un équipement
SELECT id, name, type, subType, value, configuration
FROM cmd WHERE eqLogic_id = 705;

-- Identifier des commandes par leurs IDs
SELECT c.id, c.name, c.type, c.subType, c.value, e.name AS eqLogic, c.configuration
FROM cmd c JOIN eqLogic e ON c.eqLogic_id = e.id
WHERE c.id IN (15663, 15669, 15670);
```

| Colonne | Contenu |
|---------|---------|
| `type` | `info` ou `action` |
| `subType` | `binary`, `numeric`, `string`, `other` |
| `value` | Valeur courante (mise en cache par Jeedom) |
| `configuration` | JSON — voir formats ci-dessous |

### configuration jMQTT (info)
```json
{ "topic": "home/presence/geraud", "jsonPath": "$.present" }
```

### configuration Virtual (info calculée)
```json
{ "calcul": "#652#" }
```
Calcul vide = valeur positionnée manuellement par une action.

### configuration Virtual (action ON/OFF)
```json
{
  "virtualAction": "1",
  "updateCmdId": "15669",
  "updateCmdToValue": "1"
}
```

### configuration jMQTT broker
```json
{
  "mqttAddress": "mqtt.cname.iot.home.lan",
  "mqttPort": "1883",
  "mqttIncTopic": "home/presence/#",
  "Qos": "1",
  "auto_add_cmd": "1"
}
```

---

## Scénarios — `scenario`

```sql
-- Lister les scénarios actifs
SELECT id, name, trigger, isActive, mode FROM scenario WHERE isActive = 1 ORDER BY name;

-- Détail d'un scénario (triggers + éléments racine)
SELECT id, name, trigger, isActive, scenarioElement FROM scenario WHERE id = 70;
```

| Colonne | Contenu |
|---------|---------|
| `trigger` | JSON array : `["#15663#","#1111#"]` — IDs de commandes déclencheurs |
| `scenarioElement` | JSON array : IDs des blocs IF/FOR racine |
| `mode` | `provoke` / `schedule` / `always` |

---

## Lire le contenu d'un scénario

### Requête à 3 tables — tous niveaux à plat

La clé : `scenarioExpression` contient les vraies conditions et actions.  
`scenarioSubElement.options = []` ne veut pas dire vide — les expressions sont dans `scenarioExpression`.

```sql
-- Dump complet d'un scénario (remplacer les IDs d'éléments par ceux du scénario cible)
SELECT
    sel.id      AS element_id,
    ss.id       AS sub_id,
    ss.type     AS ss_type,
    ss.subtype  AS ss_subtype,
    expr.order  AS expr_order,
    expr.type   AS expr_type,
    expr.expression,
    expr.options
FROM scenarioExpression expr
JOIN scenarioSubElement ss ON expr.scenarioSubElement_id = ss.id
JOIN scenarioElement sel   ON ss.scenarioElement_id = sel.id
WHERE sel.id IN (<liste_element_ids>)
ORDER BY sel.id, ss.id, expr.order;
```

### Comment obtenir tous les IDs d'éléments d'un scénario

Les éléments forment un arbre : les nœuds enfants sont référencés via des expressions de `type = 'element'`.

**Étape 1** — Récupérer les IDs racine depuis `scenario.scenarioElement` :
```sql
SELECT scenarioElement FROM scenario WHERE id = 4;
-- → ["8"]  : l'élément racine est 8
```

**Étape 2** — Trouver tous les enfants référencés (expressions de type `element`) :
```sql
SELECT DISTINCT CAST(expr.expression AS UNSIGNED) AS child_element_id
FROM scenarioExpression expr
JOIN scenarioSubElement ss ON expr.scenarioSubElement_id = ss.id
WHERE ss.scenarioElement_id IN (8)   -- remplacer par les IDs connus
  AND expr.type = 'element';
-- → donne les éléments enfants directs (ex: 9, 511…)
```

**Étape 3** — Répéter avec les nouveaux IDs jusqu'à stabilisation (2-3 passes suffisent pour la plupart des scénarios).

> **Astuce** : pour un audit rapide, récupérer TOUS les IDs d'éléments en une seule passe :
> ```sql
> SELECT DISTINCT CAST(expr.expression AS UNSIGNED) AS element_id
> FROM scenarioExpression expr WHERE expr.type = 'element'
> UNION
> SELECT 8;  -- racine
> ```
> Puis utiliser la liste complète dans le WHERE de la requête principale.

### Interprétation de `scenarioExpression`

| `expr.type` | `expression` | Signification |
|-------------|--------------|---------------|
| `condition` | `#15663# == 1` | Condition du IF |
| `action` | `#15670#` | Appel d'une commande action |
| `action` | `log` | Écriture log — message dans `options.message` |
| `action` | `variable` | Écrire une variable — nom/valeur dans `options` |
| `action` | `delete_variable` | Supprimer une variable |
| `action` | `scenario` | Lancer un scénario — `options.scenario_id` |
| `action` | `equipement` | Activer/désactiver un équipement |
| `element` | `511` | Référence à un sous-arbre (bloc SINON imbriqué) |

### Exemple réel — scénario 70 (simple)

```
Trigger : #15663# (BLE present jMQTT)

IF #15663# == 1
  THEN → #15670# (NUT ON)
  ELSE →
    IF #15663# == 0
      THEN → #15671# (NUT OFF)
```

### Exemple réel — scénario 4 (extrait, niveau 1)

```
Trigger : #15669# (NUT virtuel) OU #1111# (Réseau)

IF #15669# == 1 || #1111# == 1
  THEN → log("Nut ou réseau Géraud présent")
         → element 9  (suite présence)
  ELSE → log("absent")
         → variable NbAbsGeraud = 0
         → scenario::start::5  (scénario absent)
```

---

## Recherche croisée

```sql
-- Quels scénarios ont une commande en trigger ?
SELECT id, name, trigger FROM scenario WHERE trigger LIKE '%15663%';

-- Quels scénarios appellent une commande en action ?
SELECT DISTINCT s.id, s.name
FROM scenarioExpression expr
JOIN scenarioSubElement ss ON expr.scenarioSubElement_id = ss.id
JOIN scenarioElement sel ON ss.scenarioElement_id = sel.id
JOIN scenario s ON JSON_CONTAINS(s.scenarioElement, CAST(sel.id AS JSON))
WHERE expr.expression LIKE '%15670%';
```

---

## Variables de scénarios — `dataStore`

Les variables globales (`variable(xxx)` dans les scénarios) sont dans `dataStore`.

```sql
-- Lister toutes les variables de scénarios
SELECT key, value FROM dataStore WHERE type = 'scenario' AND link_id = -1 ORDER BY key;

-- Chercher une variable spécifique
SELECT key, value FROM dataStore WHERE type = 'scenario' AND key = 'NbAbsGeraud';
```

Résultat exemple :
```
PresentGeraud    → Fri Apr 17 21:59:51
AbsentGeraud     → Fri Apr 17 18:51:03
NbAbsGeraud      → 0
```

| `link_id` | Portée |
|-----------|--------|
| `-1` | Variable globale (accessible depuis tous les scénarios) |
| `>0` | Variable locale au scénario ID correspondant |

---

## Historique des valeurs — `history`

```sql
-- Dernières valeurs d'une commande
SELECT datetime, value FROM history
WHERE cmd_id = 15663 ORDER BY datetime DESC LIMIT 10;

-- Résumé dernière valeur par commande (plusieurs IDs)
SELECT cmd_id, MAX(datetime) AS last_update, value
FROM history WHERE cmd_id IN (15663, 15669, 1111)
GROUP BY cmd_id, value ORDER BY cmd_id, last_update DESC;
```

Résultat exemple :
```
15663  2026-04-18 09:24:17  0   ← BLE absent
15663  2026-04-18 09:22:42  1   ← BLE présent
15669  2026-04-18 09:24:18  0   ← NUT virtuel absent
1111   2026-04-18 07:30:45  1   ← Réseau présent
```

> `historyArch` contient l'historique archivé (même structure, données plus anciennes).

---

## Tables de référence rapide

| Table | Rôle |
|-------|------|
| `eqLogic` | Équipements |
| `cmd` | Commandes — `value` = valeur courante |
| `scenario` | Scénarios — `trigger` + `scenarioElement` (JSON) |
| `scenarioElement` | Blocs IF/FOR |
| `scenarioSubElement` | condition / then / else (métadonnées) |
| `scenarioExpression` | ⭐ Expressions réelles — conditions et actions |
| `dataStore` | Variables scénarios (`type='scenario'`, `link_id=-1`) |
| `history` / `historyArch` | Historique des valeurs par `cmd_id` |
| `object` | Pièces/groupes |
