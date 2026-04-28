---
name: jeedom-audit
description: Audit, diagnose, and explain a Jeedom 4.5 home automation install in a read-only way. Use this skill whenever the user asks about an existing Jeedom installation — diagnosing scenarios that don't trigger or misbehave, explaining what a scenario does step by step, mapping which scenarios depend on a given device or command (usage graph), auditing installation health (dead commands, orphan equipments, daemon status, plugin issues, history quality), suggesting cleanup or refactors verbally with UI walkthroughs, or interpreting Jeedom logs. Trigger this even when "Jeedom" isn't mentioned explicitly but the context implies it: mentions of eqLogic, scenario/scenarioElement, virtual switch, jMQTT, MQTT broker, dataStore, #ID# command references, or generally a French-speaking user asking about their home automation install. Always read-only — never modifies the install, only describes UI steps.
---

## 2. Règle d'or absolue

Cette skill est **strictement en lecture seule**. Elle observe, analyse, explique — jamais ne modifie.

**Ce que cela signifie concrètement :**
- Uniquement des `SELECT` en SQL — aucune requête d'écriture
- Aucun appel API d'écriture (`cmd::execCmd`, `scenario::changeState`, `config::save`…)
- Aucun script shell modifiant la configuration ou les données
- Si l'utilisateur demande une modification : décrire **pas-à-pas les étapes dans l'UI Jeedom**

**Face à l'insistance :** "Cette skill est en lecture seule. Je ne peux pas exécuter cette modification, mais voici comment la faire dans l'interface : [pas-à-pas UI]."

Toute sortie destinée à l'utilisateur utilise des **noms lisibles** (`#[Objet][Équipement][Commande]#`), jamais d'IDs bruts. Si un ID ne peut pas être résolu, le mentionner explicitement (`#ID_NON_RÉSOLU:XXXX#`).

---

## 3. Pré-requis et connexion

**Modes d'accès V1 :**

| Mode | Usage |
|---|---|
| SSH + MySQL | Audit structurel, scénarios, commandes, dataStore |
| API JSON-RPC | Runtime : `lastLaunch`, `state`, `currentValue`, historique |
| SSH (logs) | Lecture des fichiers de log (`scenarioLog/`, `http.error`, etc.) |

**Configuration requise :**
- Alias SSH `Jeedom` opérationnel sur la machine locale
- `~/.my.cnf` sur la box avec user `jeedom_audit_ro` (SELECT uniquement, perm 600)
- `~/.config/jeedom-audit/credentials.json` local (perm 600) — voir `references/connection.md`
- Si credentials absents : lancer `python3 scripts/setup.py`

**Vérification de version (obligatoire au démarrage) :**
Via `scripts/_common/version_check.py` :
- Jeedom < 4.4 → refus explicite
- Jeedom 4.4 → refus avec mention
- Jeedom 4.5.x → ✅ nominal
- Jeedom ≥ 4.6 → avertissement (schéma peut différer)

**Connexion MySQL :**
```
ssh Jeedom "mysql jeedom -e '<QUERY>'"
```
Le `~/.my.cnf` fournit les credentials côté serveur — jamais de password en argument CLI.

**Connexion API :**
```
POST http://<ip>/core/api/jeeApi.php
{"jsonrpc":"2.0","method":"...","params":{"apikey":"..."},"id":1}
```
Voir `references/connection.md` pour le setup complet et la liste des méthodes autorisées.

---

### Routage automatique (router.py)

La skill utilise `scripts/_common/router.py` pour choisir automatiquement le vecteur d'accès selon l'opération. **L'utilisateur ne choisit pas le vecteur** — le routeur décide en interne.

**`preferred_mode` dans `credentials.json` :**

| Valeur | Comportement |
|---|---|
| `"auto"` (défaut) | Routeur décide par opération selon les capacités détectées |
| `"mysql"` | Force MySQL/SSH — API ignorée sauf pour les données runtime-only |
| `"api"` | Force API — mode API-only pour installations sans SSH |

**Règles de routage par opération (`preferred_mode: "auto"`) :**

| Opération | Préféré | Fallback |
|---|---|---|
| Audit structurel (jointures, arbre scénario) | MySQL | API (partiel) |
| État runtime (`lastLaunch`, `state`, `currentValue`) | API | — |
| Historique (`cmd::getHistory`) | API | MySQL (`history` table) |
| Statistiques (`getTendance`) | API | — |
| Logs | SSH | — |
| Vérification version | API | MySQL |
| Liste plugins | API | MySQL (`update` table) |
| Résolution `#ID#` | MySQL | API (`cmd::byId` en série) |

**Détection des capacités (lazy, mis en cache session) :**
```python
from _common.router import detect_capabilities, route, with_fallback
caps = detect_capabilities(creds)   # {"mysql": bool, "api": bool}
vector = route("structural_audit", creds)  # "mysql" | "api" | "ssh"
```

**Comportement sur bascule :**
- **Silence** si le vecteur préféré répond nominalement
- **Mention discrète** sur bascule : `"⚠ Données via API (MySQL indisponible)"`
- **Mention limitation** en mode API-only : `"Mode API-only : logs indisponibles."`
- **Pas de retry infini** — 1 retry réseau max (`api_call.py`), puis fallback ou erreur explicite

**Capacités WF en mode API-only (`preferred_mode: "api"`) :**

| Workflow | Fonctionne | Limitation |
|---|---|---|
| WF1 (audit général) | Partiel | Logs absents |
| WF2 (diagnostic scénario) | Partiel | Logs indisponibles |
| WF3 (diagnostic équipement) | Partiel | Logs indisponibles |
| WF4 (diagnostic plugin) | Oui | — |
| WF5 (explication scénario) | Oui | — |
| WF6 (graphe d'usage) | Partiel | Résolution `#ID#` via `cmd::byId` seulement |
| WF13 (forensique causale) | Non | Logs requis — refus explicite |

---

## 4. Convention de nommage

**Règle absolue :** toute restitution à l'utilisateur utilise `#[Objet][Équipement][Commande]#`.

Exemples :
- `#15663#` → `#[Maison][Présence Géraud][BLE présent]#`
- Variables dataStore globales : `#variable_globale_NbAbsGeraud#`
- Scénarios : `"Présence Géraud"` (entre guillemets)

**Pipeline de résolution :**
1. SQL : `cmd` JOIN `eqLogic` JOIN `object` pour ID → `[O][E][C]`
2. Script `scripts/resolve_cmd_refs.py` pour résoudre en batch tout texte contenant des `#ID#`
3. Si ID non résolu : indiquer `#ID_NON_RÉSOLU:XXXX#` et proposer une piste

**Tags système Jeedom** (à préserver intacts, ne jamais résoudre) :
`#trigger_id#`, `#trigger_value#`, `#trigger_name#`, `#user_connect#`, `#sunset#`, `#sunrise#`, `#time#`, `#date#`

---

## 5. Hiérarchie de données

```
object                          ← pièce / groupe
└── eqLogic                     ← équipement (plugin + config)
    └── cmd                     ← commande info ou action
        └── history             ← historique (cmd_id, datetime, value)

scenario
└── scenarioElement             ← bloc IF / FOR  [sans FK directe vers scenario]
    └── scenarioSubElement      ← condition / then / else
        └── scenarioExpression  ← ⭐ expressions réelles (conditions et actions)

dataStore                       ← variables (type='scenario', link_id=-1 = globale)
config                          ← configuration système (plugin='core', key='version'…)
message                         ← messages système et erreurs Jeedom
update                          ← versions plugins installées
```

**Champs runtime (API uniquement, absents de la DB) :**
- `scenario.lastLaunch`, `scenario.state` → `scenario::byId`
- `cmd.currentValue` → `cmd::byId`

**Attention** : `scenario.trigger` est un mot réservé MySQL → toujours échapper `` `trigger` ``.

---

## 6. Gotchas critiques

1. **`trigger` = mot réservé MySQL.** Toute requête sur `scenario.trigger` doit utiliser des backticks : `` `trigger` ``. `db_query.py` l'ajoute automatiquement — écrire sans backticks dans les requêtes passées à `db_query.run()`.

2. **`scenarioSubElement.options` ≠ contenu réel.** Les conditions et actions sont dans `scenarioExpression`, pas dans `options`. Un bloc avec `options = []` n'est pas vide — descendre dans `scenarioExpression`.

3. **`scenarioElement` sans FK directe vers `scenario`.** Les IDs des éléments racine sont dans `scenario.scenarioElement` (JSON array). Traversée : extraire les IDs racine, puis descendre via les expressions de `type = 'element'`. Voir `scripts/scenario_tree_walker.py`.

4. **jMQTT : topic dans `configuration`, pas `logicalId`.** Pour les commandes jMQTT : `configuration.topic`. Pour le broker : `configuration.mqttIncTopic`. `logicalId` est NULL pour les commandes jMQTT.

5. **`int` vs `string` dans les JSON de configuration.** Un même champ peut être `"1"` ou `1` selon le plugin et la version. Utiliser `JSON_UNQUOTE` et comparaison lâche, ou laisser Python normaliser après extraction.

6. **`calendar_event.repeat` = mot réservé MariaDB.** Sans backtick → `ERROR 1064`. `db_query.py` gère `` `repeat` `` automatiquement (comme `trigger`) — écrire sans backticks dans les requêtes passées à `db_query.run()`.

7. **`cmd.value` = NULL pour les thermostats.** Les valeurs runtime (consigne, température mesurée, mode) ne sont pas dans `cmd.value` mais dans `history`. Si `cmd.value` retourne NULL sur un thermostat : utiliser `cmd::getHistory` via API ou interroger la table `history`.

8. **`JSON_EXTRACT` dans une requête passée via `echo '...' | python3` échoue.** Les guillemets et accolades imbriqués cassent l'échappement shell. Symptôme : `JSONDecodeError` ou requête tronquée. Contournement : passer la requête SQL via `subprocess.run(['python3', 'scripts/db_query.py'], input=json.dumps(...))` en Python, ou via un fichier temporaire. Ne pas utiliser `echo '{"query": "...JSON_EXTRACT..."}' | python3` pour des requêtes complexes.

---

## 7. Cas d'usage et workflows

Chaque workflow : déclencheurs → étapes → sortie → scripts.

### WF1 — Audit général
**Déclencheurs** : "audit", "santé de mon Jeedom", "fais le tour", "qu'est-ce qui cloche", "diagnostic complet"
**Étapes** : (a) version check ; (b) charger `sql-cookbook.md §audit` + `audit-templates.md` + `health-checks.md` ; (c) batch SELECT : config système, plugins, eqLogics, scénarios, commandes mortes, dataStore, messages, mises à jour, qualité historique ; (d) optionnel `tail -n 200` logs core/php
**Sortie** : synthèse exécutive (3-5 lignes) + 12 sections fixes. Sections vides omises.
**Scripts** : SQL ad-hoc depuis cookbook

### WF2 — Diagnostic scénario
**Déclencheurs** : "pourquoi le scénario X ne se déclenche pas", "X est cassé", "X ne marche plus"
**Étapes** : (a) résolution + désambiguïsation ; (b) `scenario_tree_walker.py` ; (c) `lastLaunch` et `state` via **API** `scenario::byId` ; (d) triggers et leurs valeurs courantes ; (e) `logs_query.py` fenêtre récente ; (f) si mode schedule, vérifier format `Gi`
**Sortie** : *État courant / Triggers / Dernières exécutions / Pistes (probable/possible/improbable) / Pas-à-pas UI*
**Scripts** : `scenario_tree_walker.py`, `resolve_cmd_refs.py`, `logs_query.py`

### WF3 — Diagnostic équipement
**Déclencheurs** : "[X] est mort", "ce capteur ne remonte plus", "[X] ne répond plus"
**Étapes** : (a) résoudre eqLogic ; (b) `status` JSON, `isEnable`, `eqType_name`, `configuration` ; (c) état daemon plugin ; (d) dernière valeur via `cmd.value` + `history` ; (e) checks tier-1 si applicable ; (f) `logs_query.py` plugin
**Sortie** : *État / Communication récente / Plugin et daemon / Erreurs log / Pistes*
**Scripts** : SQL ad-hoc, `logs_query.py`

### WF4 — Diagnostic plugin
**Déclencheurs** : "jMQTT déconne", "le daemon ne démarre pas", "[plugin] a un problème"
**Étapes** : (a) identifier plugin ; (b) état via `plugin::listPlugin` ; (c) état daemon ; (d) eqLogics enabled/disabled, warning/danger ; (e) `logs_query.py` plugin + `<plugin>_dep`
**Scripts** : SQL ad-hoc, `logs_query.py`

### WF5 — Explication scénario
**Déclencheurs** : "explique-moi le scénario X", "que fait cette automatisation", "comment fonctionne X"
**Étapes** : (a) résoudre + `scenario_tree_walker.py` (sans récursion par défaut) ; (b) charger `scenario-grammar.md` ; (c) `resolve_cmd_refs.py` sur tout texte ; (d) construire pseudo-code IF/THEN/ELSE imbriqué
**Appels imbriqués** : mention par nom sans dérouler par défaut. Sur demande explicite : `follow_scenario_calls=2-3` avec anti-cycle.
**Sortie** : pseudo-code + prose (*Vue d'ensemble / Triggers / Mode / Pseudo-code / Effets de bord*)
**Scripts** : `scenario_tree_walker.py`, `resolve_cmd_refs.py`

### WF6 — Graphe d'usage
**Déclencheurs** : "qu'est-ce qui dépend de [X]", "qui utilise [Y]", "qu'est-ce qui appelle le scénario X"
**Étapes** : (a) identifier cible (cmd / eqLogic / scénario) ; (b) `usage_graph.py` ; (c) signaler false positifs éventuels
**Sortie** : sections *Triggers / Conditions / Actions / Plugins consommateurs / Variables dataStore* (sections vides omises)
**Scripts** : `usage_graph.py`, `resolve_cmd_refs.py`
**Interface `usage_graph.py`** : `{"target_type": "cmd"|"eqLogic"|"scenario", "target_id": <int>}`

### WF7 — Suggestions de refactor
**Déclencheurs** : "comment simplifier", "nettoyer", "améliorer", "factoriser"
**Étapes** : (a) audit/explication selon cible ; (b) anti-patterns : conditions dupliquées, délais en dur, `triggerId()` déprécié, cmd sans Type Générique, scénarios désactivés référencés, variables globales orphelines ; (c) hiérarchiser par impact/effort
**Sortie** : liste *Constat / Impact / Pas-à-pas UI / Vérification*. Aucun SQL ni script modificateur dans la réponse.

### WF8-11 — Lectures rapides
- **WF8** Valeur courante : `#[Salon][Température][Valeur]# = 21.3 °C, mis à jour il y a 2 min`
- **WF9** Historique : tableau si <50 lignes, résumé stat sinon ; API `cmd::getHistory` privilégiée
- **WF10** Variable dataStore : valeur + portée (globale `link_id=-1` / locale)
- **WF11** Recherche : tableau filtrable par critères verbalisés

### WF12 — Cartographie d'orchestration
**Déclencheurs** : "trace la chaîne", "qui appelle qui", "flux complet quand [événement]"
**Étapes** : (a) point d'entrée ; (b) `scenario_tree_walker.py` `follow_scenario_calls=3` + anti-cycle ; (c) arbre annoté
**Sortie** : prose indentée si ≤10 nœuds ; mermaid `graph TD` si >10 nœuds

### WF13 — Forensique causale
**Déclencheurs** : "ce scénario fait X au lieu de Y", "remonte la chaîne", "trouve d'où vient le bug"
**Particularité** : enquête data-driven, profondeur non déterminée a priori, **interactif** (l'utilisateur peut rediriger à chaque étape).
**Étapes** : (a) indices initiaux ; (b) `usage_graph.py` depuis le point d'arrivée ; (c) logs sur fenêtre temporelle ; (d) remontée triggers ascendante (garde-fous : max 5 niveaux, >10 candidats → stop + demande)
**Sortie** : récit chronologique *Indice → Étapes de remontée → Cause racine → Suggestions*
**Limitation** : indisponible en mode API-seul (logs requis)

---

## 8. Plugins

**Tier-1** — documentation profonde dans `references/` :

| Plugin | Fichier de référence |
|---|---|
| `virtual` | `references/plugin-virtual.md` |
| `jMQTT` | `references/plugin-jmqtt.md` |
| `calendar` (Agenda) | `references/plugin-agenda.md` |
| `script` | `references/plugin-script.md` |
| `alarm` (Alarme) | `references/plugin-alarme.md` |
| `thermostat` | `references/plugin-thermostat.md` |

**Tous les autres plugins** : pattern générique en 4 temps — voir `references/plugin-generic-pattern.md` :
1. Identification de surface (`eqType_name`, version, nb eqLogics)
2. Extraction d'échantillons de `configuration`
3. Inférence Claude assumée explicitement
4. Intégration aux workflows standards

Chaque `plugin-X.md` indique la version testée. Signaler si la version installée diffère.

---

## 9. Index des références

| Fichier | Contenu | Statut |
|---|---|---|
| `references/connection.md` | Setup credentials, SSH, MySQL user RO, sécurité | ✅ J1 |
| `references/sql-cookbook.md` | Requêtes par famille : audit, scénarios, équipements, commandes, dataStore, historique | ✅ J2 |
| `references/audit-templates.md` | Templates de rapport WF1 (12 sections fixes) + WF7 (refactor) + WF12 (orchestration prose/mermaid) | ✅ J6 |
| `references/health-checks.md` | Critères de santé : seuils, indicateurs, anomalies | ✅ J2 |
| `references/scenario-grammar.md` | Interprétation `scenarioExpression` : types, subtypes, options | ✅ J2 |
| `references/plugin-virtual.md` | Plugin Virtual : eqLogic, cmd, configuration JSON | ✅ J3 |
| `references/plugin-jmqtt.md` | Plugin jMQTT : broker, eqpt, commandes, topics | ✅ J3 |
| `references/plugin-agenda.md` | Plugin Agenda (`calendar`) : `calendar_event`, récurrence, commandes | ✅ J4 |
| `references/plugin-script.md` | Plugin Script : syntaxes, chemins, sécurité credentials | ✅ J4 |
| `references/plugin-alarme.md` | Plugin Alarme (`alarm`) : zones, modes, triggers, variables spéciales | ✅ J4 |
| `references/plugin-thermostat.md` | Plugin Thermostat : algorithme temporel, modes, coefficients, logs | ✅ J4 |
| `references/plugin-generic-pattern.md` | Pattern d'inspection générique (tous autres plugins, incl. MQTT Manager) | ✅ J4 |
| `references/api-jsonrpc.md` | API JSON-RPC : méthodes autorisées, blacklist, format requête/réponse | ✅ J5 |
| `references/api-http.md` | Connexion HTTP : SSL, auth, test de connectivité | ✅ J5 |
| `scripts/_common/credentials.py` | Lecture `credentials.json`, override env `JEEDOM_*` | ✅ J1 |
| `scripts/_common/ssh.py` | Wrapper SSH unifié (timeout, retries, stderr) | ✅ J1 |
| `scripts/_common/version_check.py` | Détection et politique de version | ✅ J1 |
| `scripts/_common/tags.py` | Tags système Jeedom à préserver intacts | ✅ J1 |
| `scripts/_common/sensitive_fields.py` | Filtrage champs sensibles à la sortie | ✅ J1 |
| `scripts/db_query.py` | Wrapper SQL générique (stdin JSON → stdout JSON) | ✅ J1 |
| `scripts/api_call.py` | Wrapper JSON-RPC (blacklist + retry + filtrage) | ✅ J3 |
| `scripts/logs_query.py` | Tail SSH structuré sur logs Jeedom | ✅ J3 |
| `scripts/resolve_cmd_refs.py` | Résolution `#ID#` → `#[O][E][C]#` en batch | ✅ J2 |
| `scripts/scenario_tree_walker.py` | Parcours récursif scénario (anti-cycle, max_depth, follow_scenario_calls inter-scénarios) | ✅ J6 |
| `scripts/usage_graph.py` | Graphe d'usage agrégé par cible | ✅ J3 |
| `scripts/_common/router.py` | Routage transparent MySQL/API (detect_capabilities, route, with_fallback) | ✅ J5b |

> **Note de maintenance :** les colonnes `Statut` et les marqueurs `✅ Jx` / `🔄 Jx` sont retirés à la release V1.0.0 (J7) — tous les fichiers seront alors présents et le tableau redevient une simple liste de références.

---

## 10. Mode opératoire de réponse

- **Toujours des noms, jamais d'IDs** : tout texte destiné à l'utilisateur passe par `resolve_cmd_refs.py` ou une résolution SQL équivalente.
- **Markdown lisible** : tableaux pour les listes, prose pour les analyses, pseudo-code pour les scénarios.
- **Jamais de SQL ou script modificateur** dans la réponse — uniquement des pas-à-pas UI.
- **Données filtrées** : mentionner explicitement si des champs ont été masqués (`[FILTRÉ]`), lister `_filtered_fields`.
- **Workflows longs** : annoncer les étapes à l'avance, proposer une pause après chaque phase majeure. L'utilisateur peut interrompre ou rediriger à tout moment.
- **Désambiguïsation proactive** : si plusieurs équipements ou scénarios correspondent, lister et demander lequel avant de creuser.

---

## 11. Quand cette skill ne s'applique pas

- **Jeedom < 4.4** : refus explicite — "Cette skill requiert Jeedom ≥ 4.5. Votre installation est en [version]."
- **Installation de Jeedom** : hors périmètre (skill séparée à prévoir).
- **Développement de plugin** : hors périmètre (skill séparée à prévoir).
- **Autres systèmes domotiques** (Home Assistant, Domoticz, Fibaro…) : hors périmètre.
- **Modifications de l'installation** : toujours refuser — proposer le pas-à-pas UI à la place.
