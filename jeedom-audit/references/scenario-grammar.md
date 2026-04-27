---
title: Grammaire scenarioExpression — jeedom-audit
description: Interprétation complète de la table scenarioExpression de Jeedom 4.5 — types, subtypes, champs options, cas particuliers.
updated: 2026-04-27
---

# Grammaire scenarioExpression

> **Source :** schéma officiel `V4-stable` (github.com/jeedom/core) + observations sur box réelle.

---

## 1. Hiérarchie de l'arbre

```
scenario
└── scenarioElement (id dans scenario.scenarioElement JSON array)
    └── scenarioSubElement (type = "if" | "for" | "in")
        ├── ss_subtype = "condition"  → ce que teste le bloc
        ├── ss_subtype = "then"       → exécuté si vrai
        └── ss_subtype = "else"       → exécuté si faux
            └── scenarioExpression (les vraies expressions)
```

**Gotcha critique :** `scenarioSubElement.options` peut être `[]` même si des expressions existent. Les expressions réelles sont **toujours dans `scenarioExpression`**, pas dans `options`.

---

## 2. Types de blocs (`scenarioElement.type`)

| Type | Signification |
|------|--------------|
| `if` | Bloc conditionnel IF/THEN/ELSE |
| `for` | Boucle (rarement utilisé) |
| `in` | Boucle `in` sur une liste |

La plupart des scénarios n'utilisent que `if`.

---

## 3. Sous-types (`scenarioSubElement.subtype`)

| `ss_type` | `ss_subtype` | Rôle |
|-----------|-------------|------|
| `if` | `condition` | Expression(s) booléenne(s) testée(s) |
| `if` | `then` | Actions/éléments si condition vraie |
| `if` | `else` | Actions/éléments si condition fausse |
| `for` | `condition` | Condition de boucle |
| `for` | `do` | Corps de boucle |

---

## 4. Types d'expressions (`scenarioExpression.type`)

### 4.1 `condition`

Condition booléenne testée dans un bloc IF.

| Champ | Exemple | Notes |
|-------|---------|-------|
| `expression` | `#15663# == 1` | Opérateurs : `==`, `!=`, `>`, `<`, `>=`, `<=`, `&&`, `\|\|` |
| `options` | `{}` | Rarement peuplé pour les conditions |

**Formats courants :**
```
#15663# == 1                    → commande info = 1
#15663# == 1 && #15669# == 0    → ET logique
#15663# == 1 || #1111# == 1     → OU logique
variable(NbAbsGeraud) > 3       → variable dataStore globale
```

### 4.2 `action` (commande)

Exécute une commande Jeedom (action ou info en lecture).

| Champ | Valeur | Notes |
|-------|--------|-------|
| `expression` | `#15670#` | ID de la commande entre `#` |
| `options` | JSON avec `message`, `title`, `delay`, etc. | Dépend du subType de la commande |

**Options fréquentes :**
```json
{"delay": 0, "background": 0, "enable": 1}
```

### 4.3 `action` (log)

Écrit dans les logs du scénario.

| Champ | Valeur |
|-------|--------|
| `expression` | `"log"` |
| `options` | `{"message": "Géraud présent"}` |

### 4.4 `action` (variable)

Écrit ou lit une variable dataStore.

| Champ | Valeur |
|-------|--------|
| `expression` | `"variable"` |
| `options` | `{"name": "NbAbsGeraud", "value": "0"}` |

**Formats de valeur :**
```
"0"                 → littéral
"#15663#"           → valeur d'une commande
"variable(X) + 1"  → expression calculée
```

### 4.5 `action` (delete_variable)

Supprime une variable dataStore.

| Champ | Valeur |
|-------|--------|
| `expression` | `"delete_variable"` |
| `options` | `{"name": "NbAbsGeraud"}` |

### 4.6 `action` (scenario)

Lance, arrête ou met en pause un autre scénario.

| Champ | Valeur |
|-------|--------|
| `expression` | `"scenario"` |
| `options` | `{"scenario_id": "5", "action": "start"}` |

**Valeurs de `action` :**

| Valeur | Signification |
|--------|--------------|
| `"start"` | Démarrer le scénario |
| `"stop"` | Arrêter le scénario |
| `"activate"` | Activer (isActive=1) |
| `"deactivate"` | Désactiver (isActive=0) |

**Pour la résolution :** `options.scenario_id` → `SELECT name FROM scenario WHERE id = ?`

### 4.7 `action` (equipement)

Active ou désactive un équipement.

| Champ | Valeur |
|-------|--------|
| `expression` | `"equipement"` |
| `options` | `{"eqLogic_id": "705", "action": "enable"}` |

**Valeurs de `action` :** `"enable"` / `"disable"`

### 4.8 `action` (sleep / wait)

Pause dans l'exécution.

| Champ | Valeur |
|-------|--------|
| `expression` | `"sleep"` |
| `options` | `{"duration": "300"}` (secondes) |

Ou attente conditionnelle :

| Champ | Valeur |
|-------|--------|
| `expression` | `"wait"` |
| `options` | `{"condition": "#15663# == 1", "timeout": "300"}` |

### 4.9 `action` (message / notification)

Envoie un message (push, SMS, email selon plugin).

| Champ | Valeur |
|-------|--------|
| `expression` | ID d'une commande action de type message `#XXXX#` |
| `options` | `{"title": "Alerte", "message": "Géraud est arrivé"}` |

### 4.10 `element` (référence à un sous-arbre)

Pointeur vers un autre `scenarioElement` (SINON imbriqué, sous-bloc).

| Champ | Valeur |
|-------|--------|
| `expression` | `"511"` (ID de l'élément enfant) |
| `type` | `"element"` |

**C'est le mécanisme de récursion** — `scenario_tree_walker.py` suit ces pointeurs.

---

## 5. Champ `options` — structure générale

`options` est un JSON stocké en string. Toujours parser avec `json.loads`.

```python
opts = json.loads(row["options"] or "{}")
```

Champs courants selon le type d'action :

| Action | Champs `options` |
|--------|-----------------|
| `action` (cmd) | `delay`, `background`, `enable`, `value` |
| `log` | `message` |
| `variable` | `name`, `value` |
| `delete_variable` | `name` |
| `scenario` | `scenario_id`, `action` |
| `equipement` | `eqLogic_id`, `action` |
| `sleep` | `duration` |
| `wait` | `condition`, `timeout` |

---

## 6. Expressions dans les conditions — opérateurs et fonctions

### Opérateurs de comparaison
```
== != > < >= <=
```

### Opérateurs logiques
```
&&  (ET)
||  (OU)
```

### Fonctions Jeedom dans les expressions
```
variable(nom)           → valeur d'une variable dataStore globale
scenario(#ID#)          → état d'un scénario (0/1)
lastBetween(#ID#,A,B)   → dernière valeur entre les heures A et B
```

### Tags système (préserver intacts — ne pas résoudre)
```
#trigger_id#            → ID de la commande déclencheuse
#trigger_value#         → valeur au moment du déclenchement
#trigger_name#          → nom de la commande déclencheuse
#trigger_type#          → type de déclenchement
#user_connect#          → utilisateur connecté (si déclenchement connexion)
#sunset#  #sunrise#     → heure coucher/lever soleil
#time#    #date#        → heure et date courantes
```

---

## 7. Triggers (`scenario.trigger`)

JSON array stocké dans `scenario.trigger`.

### Mode `provoke` (déclenché par commande)
```json
["#15663#", "#1111#"]
```
Chaque entrée est un ID de commande info entre `#`. Le scénario se déclenche quand la valeur change.

### Mode `schedule` (planifié)
```json
["0730", "1800"]
```
Format `Gi` de PHP : heures (0-23) + minutes (00-59) sans séparateur.
- `"0730"` → 07h30
- `"1800"` → 18h00
- `"0"` → minuit

Pour interpréter : `hhmm = trigger.zfill(4)` → `hh = hhmm[:2], mm = hhmm[2:]`

### Mode `always` (toujours actif)
```json
[]
```
Le scénario est en mode daemon — aucun trigger explicite.

---

## 8. Anti-patterns courants (WF7)

| Anti-pattern | Détection |
|--------------|-----------|
| `triggerId()` déprécié | `expression LIKE '%triggerId()%'` dans conditions |
| Délai en dur dans sleep | `expression = 'sleep'` avec `options.duration` > 300 |
| Scénario désactivé appelé | `expression = 'scenario'` + `isActive = 0` sur la cible |
| Conditions dupliquées | Même `expression` dans plusieurs `ss_subtype='condition'` d'un même bloc |
| Variables globales orphelines | Variable lue mais jamais écrite (ou inversement) |

---

## 9. Pseudo-code WF5 — conventions de rendu

```
QUAND #[Maison][Présence Géraud][BLE présent]# change
MODE  provoke

SI #[Maison][Présence Géraud][BLE présent]# == 1
  ALORS
    → Commande "#[Maison][NUT Virtuel][ON]#"
  SINON
    SI #[Maison][Présence Géraud][BLE présent]# == 0
      ALORS
        → Commande "#[Maison][NUT Virtuel][OFF]#"
```

**Règles :**
- Indentation par niveau de 2 espaces
- `QUAND` pour les triggers (mode `provoke`)
- `PLANIFIÉ` + heure pour les triggers mode `schedule`
- IDs toujours résolus en `#[O][E][C]#` (jamais d'IDs bruts)
- Appels de scénario : `→ Scénario "Nom du scénario" (start|stop|...)`
- Variables : `→ variable NomVar = "valeur"`
- Log : `→ log "message"`
