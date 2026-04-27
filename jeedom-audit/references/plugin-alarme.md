# Référence plugin — Alarme (`alarm`)

**Version testée** : compatible Jeedom ≥ 4.3 — testé sur Jeedom 4.5.3 (box réelle, 2026-04-27)
**Catégorie** : Security — Daemon : aucun — Dépendances système : aucune

---

## 1. Identification

Le plugin Alarme gère des systèmes d'alarme logiciels multi-zones avec délais, modes et actions configurables. Usages sur la box de référence (2 eqLogics, 2 actifs) :

- **Alarme intrusion** (`Maison`) — multi-zones (Rdc, Etage, Porte cave), 3 modes (Nuit, Absent, Nuit invites), délais d'armement et de détection
- **Alarme incendie** (`Incendie`) — zone unique, toujours active, déclenchement immédiat

Identification DB : `eqLogic.eqType_name = 'alarm'`

---

## 2. Structure eqLogic

| Champ DB | Valeurs typiques | Signification |
|---|---|---|
| `eqType_name` | `alarm` | type plugin |
| `isEnable` | `1` (les deux actifs sur box de réf.) | actif/inactif |
| `isVisible` | `0` ou `1` | visible dans le dashboard |
| `object_id` | référence pièce | objet Jeedom parent |

### Champs clés dans `eqLogic.configuration` (JSON)

| Champ | Type | Rôle |
|---|---|---|
| `always_active` | `"0"` ou `"1"` | toujours armée, sans bouton Activer/Désactiver |
| `armed_visible` | `"0"` ou `"1"` | afficher le bouton Activer dans le widget |
| `immediateState_visible` | `"0"` ou `"1"` | afficher le statut immédiat dans le widget |
| `autorearm` | `"0"` ou `"1"` | réarmement automatique après déclenchement |
| `historizedState` | `"0"` ou `"1"` | historiser l'état de l'alarme |
| `splitZone` | `"0"` ou `"1"` | zones indépendantes (chacune peut déclencher séparément) |
| `ignoreImmediatIfNoDelay` | `"0"` ou `"1"` | ignorer l'immédiat si aucun délai configuré |
| `zones` | array | définition des zones (voir §3) |
| `modes` | array | définition des modes (voir §4) |
| `release` | array | actions exécutées lors du désarmement |
| `raz` | array | actions exécutées lors du RAZ (après délai) |
| `razImmediate` | array | actions exécutées lors du RAZ immédiat |
| `activationOk` | array | actions exécutées lors d'une activation réussie |
| `activationKo` | array | actions exécutées lors d'une activation échouée (capteur ouvert) |
| `activationImmediateOk` | array | actions exécutées lors d'une activation immédiate réussie |
| `outbreak` | array | actions exécutées lors d'un déclenchement (avec délai) |
| `outbreakImmediate` | array | actions exécutées lors d'un déclenchement immédiat |
| `reenableTrigger` | array | actions exécutées lors de la reprise de surveillance |

---

## 3. Structure des zones

Chaque zone dans `configuration.zones` est un objet :

```json
{
  "name": "Rdc",
  "triggers": [
    {
      "enable": "1",
      "cmd": "#2070#",
      "invert": "1",
      "triggerHold": "2",
      "armedDelay": "",
      "waitDelay": ""
    }
  ],
  "actions": [],
  "actionsImmediate": []
}
```

| Champ trigger | Rôle |
|---|---|
| `cmd` | référence `#ID#` du capteur surveillé |
| `invert` | `"1"` = déclenche si la valeur passe à `0` (capteur normalement fermé → ouverture = alarme) |
| `triggerHold` | durée (secondes) pendant laquelle la valeur doit rester vraie avant déclenchement |
| `armedDelay` | délai (secondes) après armement avant que le capteur soit surveillé (délai entrée) |
| `waitDelay` | délai (secondes) entre détection et déclenchement (temps pour désarmer) |
| `actions` | actions exécutées lors du déclenchement (avec délai `waitDelay`) |
| `actionsImmediate` | actions exécutées immédiatement lors de la détection |

---

## 4. Structure des modes

Chaque mode dans `configuration.modes` associe un nom à une ou plusieurs zones :

```json
{"name": "Nuit", "zone": "Rdc"}
{"name": "Absent", "zone": ["Rdc", "Porte cave"]}
```

Un mode peut activer une seule zone (string) ou plusieurs (array).

---

## 5. Structure des commandes

| `logicalId` | Nom typique | Type | Rôle |
|---|---|---|---|
| `enable` | Actif | info/binary | `1` si l'alarme est armée |
| `statePause` | Statut pause | info/binary | `1` si l'alarme est en pause |
| `state` | Statut | info/binary | `1` si un déclenchement est en cours |
| `immediatState` | Immédiat | info/binary | `1` si détection immédiate en cours |
| `mode` | Mode | info/string | nom du mode actif (ex: `"Absent"`) |
| `armed` | Activer | action/other | arme l'alarme |
| `released` | Désactiver | action/other | désarme l'alarme |
| `pauseOn` | Pause | action/other | met en pause la surveillance |
| `pauseOff` | Reprise | action/other | reprend la surveillance |
| *(mode)* | ex: `Nuit` | action/other | active un mode spécifique — `logicalId = NULL`, `configuration.state = "Nuit"` |

Les commandes de mode ont `logicalId = NULL` et `configuration.mode = "1"` + `configuration.state = "<nom du mode>"`.

---

## 6. Variables spéciales

Dans les chaînes d'actions (`outbreak`, `activationKo`, etc.), deux variables sont injectées dynamiquement par le plugin :

| Variable | Valeur |
|---|---|
| `#alarm_trigger#` | nom ou ID du capteur qui a déclenché l'alarme |
| `#time#` | horodatage du déclenchement |

Ces variables peuvent être utilisées dans les champs `tags` des actions scénario ou dans les messages de notification.

---

## 7. Points d'audit

**Anti-patterns fréquents :**
- Triggers référençant un `#ID#` de capteur supprimé → zone inactive silencieusement
- `armedDelay` vide sur tous les triggers → impossible d'entrer chez soi sans déclencher immédiatement
- `always_active = "1"` sur une alarme intrusion → ne peut pas être désarmée via l'UI (prévu pour incendie)
- `autorearm = "1"` sans action de notification dans `outbreak` → déclenchements silencieux

**Requête — alarmes actives et leur mode courant :**
```sql
SELECT e.id, e.name,
       JSON_UNQUOTE(JSON_EXTRACT(c.value, '$')) AS mode_actif
FROM eqLogic e
JOIN cmd c ON c.eqLogic_id = e.id AND c.logicalId = 'mode'
WHERE e.eqType_name = 'alarm'
  AND e.isEnable = 1
```

**Requête — nombre de zones et triggers par alarme :**
```sql
SELECT e.id, e.name,
       JSON_LENGTH(e.configuration, '$.zones') AS nb_zones,
       JSON_LENGTH(e.configuration, '$.modes') AS nb_modes
FROM eqLogic e
WHERE e.eqType_name = 'alarm'
```

---

## 8. Interactions scénarios

Les actions dans `outbreak`, `activationOk`, `activationKo`, etc. référencent des scénarios via :
```json
{"cmd": "scenario", "options": {"scenario_id": "20", "action": "start", "tags": "DISCORD=1 CHANNEL=Alarme ..."}}
```

Le champ `tags` est passé au scénario démarré — c'est un mécanisme de paramétrage de scénario générique (tag `DISCORD`, `CHANNEL`, `TITLE`, `MSG` sur la box de référence).

Les commandes info de l'alarme (`enable`, `state`, `mode`) peuvent être utilisées comme conditions ou déclencheurs dans les scénarios.

---

## 9. Daemon

Aucun daemon — le plugin évalue les conditions en temps réel sur mise à jour des capteurs via le moteur d'événements Jeedom. Pas de statut daemon à vérifier.

---

## 10. Sécurité / lecture seule

`eqLogic.configuration` contient les IDs de tous les capteurs surveillés et la logique complète de l'alarme. Données sensibles (topologie de l'installation) — à traiter avec discrétion dans les réponses.

`filter_rows` ne redacte pas ce type par défaut, mais les références `#ID#` de capteurs sont présentes dans la configuration.

---

## 11. Patterns de log

Aucun fichier log dédié au plugin alarm dans `/var/www/html/log/`. Les événements d'alarme (déclenchements, armements) apparaissent dans `/var/www/html/log/event` et dans les logs des scénarios déclenchés.

---

## 12. Liens

- Documentation officielle : https://doc.jeedom.com/fr_FR/plugins/security/alarm/
- Changelog : https://doc.jeedom.com/fr_FR/plugins/security/alarm/changelog
