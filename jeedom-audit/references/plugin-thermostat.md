# Référence plugin — Thermostat (`thermostat`)

**Version testée** : compatible Jeedom ≥ 4.3 — testé sur Jeedom 4.5.3 (box réelle, 2026-04-27)
**Catégorie** : Energy — Daemon : aucun — Dépendances système : aucune

---

## 1. Identification

Le plugin Thermostat gère des thermostats logiciels pilotant des actionneurs physiques (chaudière, radiateurs électriques, climatiseurs). Il calcule la durée de chauffe nécessaire selon l'algorithme temporel ou hystérésis. Usages sur la box de référence (9 eqLogics, 9 actifs) :

- **Thermostats par pièce** — un par pièce chauffée (bureau, couloir, salle de bain, chambres, cuisine, salon)
- **Moteur temporel** avec apprentissage automatique des coefficients
- **Modes Confort/Eco/Absent** — consignes différentes par mode, pilotés par l'Agenda

Identification DB : `eqLogic.eqType_name = 'thermostat'`

---

## 2. Structure eqLogic

| Champ DB | Valeurs typiques | Signification |
|---|---|---|
| `eqType_name` | `thermostat` | type plugin |
| `isEnable` | `1` (9/9 actifs sur box de réf.) | actif/inactif |
| `isVisible` | `0` ou `1` | visible dans le dashboard |
| `object_id` | référence pièce | objet Jeedom parent |

### Champs clés dans `eqLogic.configuration` (JSON)

#### Capteurs et actionneurs

| Champ | Type | Rôle |
|---|---|---|
| `temperature_indoor` | `#ID#` | commande info température intérieure |
| `temperature_outdoor` | `#ID#` | commande info température extérieure (peut être la même sur toute la maison) |
| `consumption` | `#ID#` ou vide | commande info consommation électrique (optionnel) |
| `heating` | array `[{"cmd": "#ID#"}]` | commandes action pour activer le chauffage |
| `cooling` | array `[{"cmd": "#ID#"}]` | commandes action pour activer la climatisation |
| `stoping` | array `[{"cmd": "#ID#"}]` | commandes action pour arrêter chauffage/clim |
| `window` | array | capteurs d'ouverture de fenêtre — pause automatique si ouvert |
| `failure` | array | capteurs de défaillance du capteur de température |
| `failureActuator` | array | actions exécutées en cas de défaillance de l'actionneur |

#### Algorithme

| Champ | Type | Rôle |
|---|---|---|
| `engine` | `temporal` ou `hysteresis` | algorithme de calcul |
| `allow_mode` | `heat`, `cool`, `all` | directions autorisées |
| `cycle` | int (minutes) | durée du cycle de calcul (ex: `30`) |
| `minCycleDuration` | int (minutes) | durée minimale d'activation par cycle |
| `smart_start` | `"0"` ou `"1"` | préchauffage anticipé pour atteindre la consigne à l'heure |
| `autolearn` | `"0"` ou `"1"` | apprentissage automatique des coefficients |
| `repeat_commande_cron` | cron | fréquence de renvoi des commandes (ex: `*/5 * * * *`) |

#### Coefficients (moteur temporel)

| Champ | Rôle |
|---|---|
| `coeff_indoor_heat` | coefficient d'isolation thermique intérieure (chaud) — appris par `autolearn` |
| `coeff_outdoor_heat` | coefficient d'influence extérieure (chaud) — appris par `autolearn` |
| `coeff_indoor_cool` | coefficient d'isolation thermique intérieure (froid) |
| `coeff_outdoor_cool` | coefficient d'influence extérieure (froid) |
| `offset_heat` / `offset_cool` | décalage appliqué à la consigne |

#### Limites et modes

| Champ | Rôle |
|---|---|
| `order_min` / `order_max` | bornes de la consigne (ex: 8°C / 28°C) |
| `temperature_indoor_min` | seuil minimal de température — déclenchement ERROR dans les logs |
| `existingMode` | array des modes disponibles avec leur actions (voir §4) |

---

## 3. Structure des commandes

| `logicalId` | Nom typique | Type | Rôle |
|---|---|---|---|
| `order` | Consigne | info/numeric | consigne courante (°C) |
| `thermostat` | Thermostat | action/slider | modifie la consigne |
| `status` | Statut | info/string | statut courant (`Chauffage`, `Off`, `Eco`, etc.) |
| `actif` | Actif | info/binary | `1` si le thermostat est en fonctionnement |
| `lock_state` | Verrouillage | info/binary | `1` si la consigne est verrouillée |
| `lock` | lock | action/other | verrouille la consigne |
| `unlock` | unlock | action/other | déverrouille la consigne |
| `temperature` | Température | info/numeric | température intérieure mesurée |
| `temperature_outdoor` | Température extérieure | info/numeric | température extérieure |
| `offset_heat` | Offset chauffage | action/slider | décalage de consigne chaud |
| `offset_cool` | Offset froid | action/slider | décalage de consigne froid |
| `heat_only` | Chauffage seulement | action/other | force le mode chauffage |
| `cool_only` | Climatisation seulement | action/other | force le mode climatisation |
| `all_allow` | Tout autorisé | action/other | autorise chauffage et climatisation |
| `mode` | Mode | info/string | mode actif (ex: `"Confort"`, `"Eco"`, `"Absent"`) |
| `off` | Off | action/other | éteint le thermostat |
| `deltaOrder` | Delta consigne | action/slider | décalage temporaire de la consigne |
| `power` | Puissance | info/numeric | pourcentage de chauffe calculé (moteur temporel) |
| `modeAction` | ex: `Confort` | action/other | active un mode — `logicalId = "modeAction"`, `name` = nom du mode |
| `coeff_indoor_heat` | Coefficient chaud | info/numeric | coefficient intérieur appris |
| `coeff_outdoor_heat` | Isolation chaud | info/numeric | coefficient extérieur appris |
| `coeff_indoor_cool` | Coefficient froid | info/numeric | coefficient intérieur froid |
| `coeff_outdoor_cool` | Isolation froid | info/numeric | coefficient extérieur froid |

Les commandes `modeAction` ont toutes le même `logicalId = "modeAction"` — le mode est identifié par `cmd.name`.

---

## 4. Structure des modes

Chaque mode dans `configuration.existingMode` :

```json
{
  "isVisible": "1",
  "name": "Confort",
  "actions": [
    {"cmd": "#251#", "options": {"slider": "#11757#"}}
  ]
}
```

- `cmd` : commande action à exécuter lors de l'activation du mode (ici l'action `thermostat` du thermostat lui-même)
- `options.slider` : valeur à appliquer — souvent une référence `#ID#` vers une commande info contenant la consigne du mode (variable partagée entre tous les thermostats)

---

## 5. Gestion des fenêtres (`window`)

```json
{"cmd": "#1986#", "stopTime": "2", "restartTime": "1", "invert": "1"}
```

- `cmd` : capteur d'ouverture de fenêtre
- `invert = "1"` : déclenche si la valeur passe à `0` (capteur normalement fermé)
- `stopTime` : minutes après l'ouverture avant de couper le chauffage
- `restartTime` : minutes après la fermeture avant de reprendre le chauffage

---

## 6. Points d'audit

**Anti-patterns fréquents :**
- `temperature_indoor` référençant une commande sans valeur récente → thermostat bloqué
- `autolearn = "1"` avec des coefficients aberrants (ex: `coeff_indoor_heat > 200`) → chauffe excessive
- `order_min` trop bas (`8°C`) sans action `failureActuator` → risque de gel silencieux si capteur défaillant
- Modes (`existingMode`) dont les actions référencent des `#ID#` de commandes supprimées → changement de mode sans effet

**Requête — état actuel de tous les thermostats :**
```sql
SELECT e.id, e.name,
       JSON_UNQUOTE(JSON_EXTRACT(c_order.value, '$'))  AS consigne,
       JSON_UNQUOTE(JSON_EXTRACT(c_temp.value, '$'))   AS temperature,
       JSON_UNQUOTE(JSON_EXTRACT(c_mode.value, '$'))   AS mode,
       JSON_UNQUOTE(JSON_EXTRACT(c_status.value, '$')) AS statut
FROM eqLogic e
JOIN cmd c_order  ON c_order.eqLogic_id  = e.id AND c_order.logicalId  = 'order'
JOIN cmd c_temp   ON c_temp.eqLogic_id   = e.id AND c_temp.logicalId   = 'temperature'
JOIN cmd c_mode   ON c_mode.eqLogic_id   = e.id AND c_mode.logicalId   = 'mode'
JOIN cmd c_status ON c_status.eqLogic_id = e.id AND c_status.logicalId = 'status'
WHERE e.eqType_name = 'thermostat'
  AND e.isEnable = 1
```

**Requête — coefficients appris (détection dérive) :**
```sql
SELECT e.name,
       JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.coeff_indoor_heat')) AS coeff_interieur,
       JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.coeff_outdoor_heat')) AS coeff_exterieur
FROM eqLogic e
WHERE e.eqType_name = 'thermostat'
ORDER BY CAST(JSON_UNQUOTE(JSON_EXTRACT(e.configuration, '$.coeff_indoor_heat')) AS DECIMAL) DESC
```

---

## 7. Interactions scénarios

Le plugin Thermostat interagit avec les scénarios de deux façons :

1. **`failureActuator`** — en cas de défaillance de l'actionneur de chauffage, le thermostat démarre un scénario avec des tags identifiant la pièce concernée
2. **Modes via Agenda** — les événements du plugin Agenda appellent les commandes `modeAction` (Confort/Eco/Absent) qui modifient la consigne

Les commandes `order`, `temperature`, `mode`, `status` peuvent être utilisées comme déclencheurs ou conditions dans les scénarios.

---

## 8. Daemon

Aucun daemon — le thermostat s'exécute via le cron Jeedom selon `repeat_commande_cron` (typiquement `*/5 * * * *`). Pas de statut daemon à vérifier.

---

## 9. Sécurité / lecture seule

Aucune donnée sensible dans `eqLogic.configuration`. Les références `#ID#` de capteurs présentes dans `configuration` sont des IDs de commandes Jeedom, non sensibles.

---

## 10. Patterns de log

Fichier : `/var/www/html/log/thermostat`

Patterns observés :
```
[TIMESTAMP][ERROR] : [<objet>][<thermostat>] Attention la température intérieure est en dessous du seuil autorisé : <valeur>
[TIMESTAMP][ERROR] : [<objet>][<thermostat>] Attention une défaillance du chauffage est détectée
[TIMESTAMP][INFO]  : [<objet>][<thermostat>] Calcul du cycle — puissance : <pct>%
```

Le premier pattern (`température en dessous du seuil`) indique une température intérieure inférieure à `temperature_indoor_min` — souvent symptôme d'un capteur hors ligne ou d'un chauffage défaillant.

Le second pattern (`défaillance du chauffage`) est déclenché par `failureActuator` quand l'actionneur de chauffage ne répond pas dans le délai attendu.

---

## 11. Liens

- Documentation officielle : https://doc.jeedom.com/fr_FR/plugins/energy/thermostat/
- Changelog : https://doc.jeedom.com/fr_FR/plugins/energy/thermostat/changelog
