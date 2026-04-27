# Référence plugin — Agenda (`calendar`)

**Version testée** : compatible Jeedom ≥ 4.3 — testé sur Jeedom 4.5.3 (box réelle, 2026-04-27)
**Catégorie** : Programming — Daemon : aucun — Dépendances système : aucune

---

## 1. Identification

Le plugin Agenda permet de créer des plannings récurrents ou ponctuels qui déclenchent des commandes Jeedom à leur début et à leur fin. Usages typiques sur la box de référence (32 eqLogics, 12 actifs) :

- **Plannings de chauffage** — déclenchement des modes Confort/Eco des thermostats sur des plages horaires hebdomadaires
- **Plannings de présence** — activation de modes maison (Absent, Vacances, etc.) à des dates définies
- **Événements ponctuels** — actions one-shot avec dates d'exclusion/inclusion manuelles

Identification DB : `eqLogic.eqType_name = 'calendar'`

---

## 2. Structure eqLogic

| Champ DB | Valeurs typiques | Signification |
|---|---|---|
| `eqType_name` | `calendar` | type plugin (attention : pas `agenda`) |
| `isEnable` | `0` ou `1` | actif/inactif — 12/32 actifs sur box de réf. |
| `isVisible` | `0` ou `1` | visible dans le dashboard |
| `object_id` | référence pièce | objet Jeedom parent |

### Champs clés dans `eqLogic.configuration` (JSON)

| Champ | Rôle |
|---|---|
| `nbWidgetDay` | nombre de jours affichés dans le widget dashboard |
| `nbWidgetMaxEvent` | nombre max d'événements affichés (vide = illimité) |
| `modes` | modes agenda personnalisés (rarement utilisé) |
| `sendToHomebridge` | intégration Homebridge (hors scope audit) |
| `updatetime` | dernière mise à jour automatique |

Les champs `heating`, `cooling`, `stoping`, `window`, `failure`, `failureActuator`, `orderChange`, `existingMode` sont présents dans la configuration mais **non utilisés par le plugin calendar** — héritage de la structure partagée avec thermostat (les deux plugins partagent le même modèle de base).

---

## 3. Table `calendar_event`

Chaque événement est une ligne dans la table `calendar_event`. C'est ici que réside la logique métier du plugin.

| Colonne | Type | Rôle |
|---|---|---|
| `id` | int | PK |
| `eqLogic_id` | int | FK vers `eqLogic.id` |
| `cmd_param` | text (JSON) | définition de l'événement (nom, couleur, actions start/end) |
| `value` | varchar(127) | valeur courante (NULL en général) |
| `startDate` | datetime | date/heure de début |
| `endDate` | datetime | date/heure de fin |
| `until` | datetime | date de fin de récurrence (NULL = indéfinie) |
| `repeat` | text (JSON) | règle de récurrence |

### Structure de `cmd_param` (JSON)

```json
{
  "eventName": "Confort",
  "icon": "",
  "color": "#ff2600",
  "transparent": "0",
  "text_color": "#ffffff",
  "noDisplayOnDashboard": "0",
  "in_progress": 1,
  "start": [{"options": {"enable": "1", "background": "0"}, "cmd": "#273#"}],
  "end":   [{"options": {"enable": "1", "background": "0"}, "cmd": "#271#"}]
}
```

- `start` : liste d'actions exécutées au démarrage de l'événement (références `#ID#`)
- `end` : liste d'actions exécutées à la fin de l'événement
- `in_progress` : `1` si l'événement est actuellement actif (calculé à la volée, pas fiable en base)

### Structure de `repeat` (JSON)

```json
{
  "enable": "1",
  "mode": "simple",
  "positionAt": "first",
  "day": "monday",
  "freq": "1",
  "unite": "days",
  "excludeDay": {"1": "1", "2": "1", "3": "1", "4": "1", "5": "1", "6": "0", "7": "0"},
  "nationalDay": "all",
  "includeDate": "",
  "excludeDate": "",
  "includeDateFromCalendar": "",
  "excludeDateFromCalendar": ""
}
```

- `unite` : `days`, `weeks`, `months`, `years`
- `excludeDay` : `1`=lundi … `7`=dimanche, `"1"` = exclu
- `includeDateFromCalendar` / `excludeDateFromCalendar` : id d'un autre agenda dont les événements servent de filtre
- `enable` : `"0"` = récurrence désactivée (événement one-shot)

---

## 4. Structure des commandes

Chaque eqLogic calendar expose exactement 3 commandes fixes :

| `logicalId` | Nom typique | Type | Rôle |
|---|---|---|---|
| `in_progress` | En cours | info/string | nom de l'événement en cours (vide si aucun) |
| `add_include_date` | Ajouter une date | action/message | ajoute une date d'inclusion manuelle |
| `add_exclude_date` | Retirer une date | action/message | ajoute une date d'exclusion manuelle |

La commande `in_progress` est la seule commande info — c'est elle qu'on lit pour savoir si un événement est actif et lequel.

---

## 5. Points d'audit

**Anti-patterns fréquents :**
- Agendas désactivés (`isEnable = 0`) avec des événements dont les dates sont passées — chauffage planifié qui ne se déclenche plus silencieusement
- `cmd_param.start` ou `end` référençant un `#ID#` de commande supprimée → action orpheline, silencieuse
- Événements sans règle de récurrence (`repeat.enable = "0"`) et `endDate` dépassée → événements morts en base

**Requête — agendas actifs avec leur événement en cours :**
```sql
SELECT e.id, e.name, ce.cmd_param
FROM eqLogic e
JOIN calendar_event ce ON ce.eqLogic_id = e.id
WHERE e.eqType_name = 'calendar'
  AND e.isEnable = 1
  AND NOW() BETWEEN ce.startDate AND ce.endDate
```

**Requête — agendas désactivés :**
```sql
SELECT id, name
FROM eqLogic
WHERE eqType_name = 'calendar'
  AND isEnable = 0
```

**Requête — événements dont les actions référencent des commandes supprimées :**
```sql
SELECT ce.id, ce.eqLogic_id, JSON_UNQUOTE(JSON_EXTRACT(ce.cmd_param, '$.eventName')) AS event_name,
       JSON_UNQUOTE(JSON_EXTRACT(ce.cmd_param, '$.start[0].cmd')) AS start_cmd
FROM calendar_event ce
WHERE ce.cmd_param LIKE '%#%'
```
*(à croiser avec les IDs de commandes existantes)*

---

## 6. Interactions scénarios

Les commandes `#ID#` dans `cmd_param.start` et `cmd_param.end` sont des déclencheurs d'actions Jeedom (commandes action d'autres plugins). Sur la box de référence, elles pointent systématiquement vers des commandes `modeAction` de thermostats (Confort, Eco, Absent).

La commande `in_progress` peut être utilisée comme condition dans un scénario :
```
#[Chauffage][Agenda_normal][En cours]# != ""
```

---

## 7. Daemon

Aucun daemon — le plugin tourne via le cron Jeedom (vérification toutes les minutes). Pas de statut daemon à vérifier.

---

## 8. Sécurité / lecture seule

Aucune donnée sensible dans `eqLogic.configuration` ni `calendar_event`. `filter_rows` ne redacte rien sur ce type.

---

## 9. Patterns de log

Fichier : `/var/www/html/log/calendar`

Patterns observés :
```
[TIMESTAMP][INFO] : Début d'activation du plugin
[TIMESTAMP][DEBUG] : Vérification événements — eqLogic <id>
[TIMESTAMP][ERROR] : Impossible d'exécuter la commande #<id># (commande introuvable)
```

Fréquence : le cron génère des entrées toutes les minutes quand des événements sont actifs. En l'absence d'événements actifs, le log reste silencieux.

---

## 10. Liens

- Documentation officielle : https://doc.jeedom.com/fr_FR/plugins/programming/calendar/
- Changelog : https://doc.jeedom.com/fr_FR/plugins/programming/calendar/changelog
