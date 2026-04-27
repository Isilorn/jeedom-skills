> **Archive du projet source — ne pas reproduire tel quel.**
> Ce fichier référence `.claude/commands/jeedom.md` (ancien format slash-command) qui ne s'applique plus : la décision V1 est **skill**, pas slash-command (ADR 0001). Il sert de référence d'inspiration historique et de traçabilité des idées initiales. La source de vérité V1 est [`docs/PLANNING.md`](../PLANNING.md).

---

# Brief — Projet Claude Code : Skill Jeedom

> Document de démarrage pour le nouveau projet. Ne pas committer dans ce repo.

---

## Objectif

Créer un skill Claude Code générique et distribuable à la communauté Jeedom.
Le skill charge dans Claude la connaissance structurelle de Jeedom (DB, conventions de nommage,
patterns d'audit, gotchas) pour permettre des audits, diagnostics et accompagnements de
modification sans jamais toucher l'installation directement.

---

## Fichiers à transférer depuis ce repo

### Documentation technique (base du skill)

| Fichier | Valeur | Action |
|---------|--------|--------|
| `docs/jeedom_audit_db.md` | ⭐ Référence centrale — schéma DB complet, requêtes, patterns scénarios, gotchas | Copier, **retirer les credentials** ligne 3 → `mysql -u $JEEDOM_DB_USER -p$JEEDOM_DB_PASS jeedom` |

### Artefacts de test (données réelles anonymisables)

Ces fichiers permettent de tester le skill sur une installation réelle sans connexion live.
Les données sont déjà sanitisées (passwords REDACTED), mais vérifier qu'aucune info personnelle ne subsiste avant distribution.

**`data/artifacts_sanitized/2026-04-05/jeedom/`** — audit complet :
- `jeedom__mysql_scenarios_full.json` — tous les scénarios avec structure complète
- `jeedom__mysql_scenarioExpression.sql` — expressions brutes (INSERT) → excellent pour tests de parsing
- `jeedom__mysql_scenario_elements.tsv` + `jeedom__mysql_scenario_subelements.tsv` — structure arborescente
- `jeedom__mysql_eqlogic_summary.csv` — inventaire équipements
- `jeedom__mysql_cmd_summary.csv` — inventaire commandes
- `jeedom__mysql_objects.csv` — hiérarchie objets/pièces
- `jeedom__mysql_plugins.csv` — plugins installés
- `jeedom__mysql_virtual_eqlogic.csv` — détail virtuels
- `jeedom__audit_equipements.json` — dump JSON équipements (API Jeedom)
- `jeedom__audit_scenarios.json` — dump JSON scénarios (API Jeedom)
- `jeedom__scenarios_php_export.json` — export natif PHP

**`data/artifacts_sanitized/2026-04-12/jeedom/`** — exemples jMQTT :
- `jmqtt__presence_eqlogics.txt` — exemple concret structure eqLogic jMQTT
- `jeedom__scenarios_presence.txt` — scénarios de présence annotés

**Ne pas transférer** :
- `jeedom__mysql_mqtt_config__REDACTED.txt` (config MQTT spécifique à cette infra)
- Tout ce qui est dans `data/derived/` (synthèses liées au projet migration)

---

## Structure du nouveau projet

```
jeedom-skill/
├── .claude/
│   └── commands/
│       └── jeedom.md          ← le skill
├── docs/
│   └── jeedom_db_reference.md ← jeedom_audit_db.md nettoyé
├── tests/
│   └── fixtures/              ← artefacts copiés depuis ce repo
│       ├── scenarios_full.json
│       ├── eqlogic_summary.csv
│       └── ...
└── README.md
```

---

## Draft du skill — `.claude/commands/jeedom.md`

```markdown
# Jeedom — Audit et diagnostic

Ce skill te donne le contexte pour travailler avec une installation Jeedom 4.x.
Il couvre l'audit SSH/MySQL, la lecture des scénarios, l'inspection des équipements
et le diagnostic des plugins. **Aucune modification directe** — tu guides l'utilisateur
via l'interface web Jeedom.

## Connexion

Avant toute requête, demande à l'utilisateur :
- Son alias SSH vers Jeedom (ex: `Jeedom`, ou `user@host`)
- Ses credentials MySQL Jeedom (user + password + nom de la base, souvent `jeedom`)

Pattern de requête :
```bash
ssh <ALIAS> "mysql -u <DB_USER> -p<DB_PASS> jeedom -e \"<QUERY>\" 2>/dev/null"
```

⚠️ Toujours passer `-e` avec la requête entre guillemets doubles. Backtick-quoter
les mots réservés MySQL : `trigger`, `interval`, `status`.

---

## Règle fondamentale

**Lecture seule.** Tu ne modifies jamais Jeedom par SSH, API ou MySQL directement.
Si une modification est nécessaire, tu décris pas à pas ce que l'utilisateur doit faire
dans l'interface web Jeedom. Cette règle est non négociable — la structure interne
de Jeedom est fragile et les modifications directes sont sources d'erreurs silencieuses.

---

## Conventions de nommage Jeedom

Les utilisateurs Jeedom n'utilisent **jamais** les IDs numériques. Ils référencent
toujours les commandes sous la forme :

```
#[Objet][Équipement][Commande]#
```

Exemples :
- `#[Salon][Lampe salon][ON]#`
- `#[Maison][Présence Géraud][Présence]#`
- `#[Chauffage][Thermostat bureau][Consigne]#`

**Toujours présenter les résultats par nom.** Les IDs numériques ne servent qu'en interne
pour les requêtes SQL — ne les expose jamais à l'utilisateur sauf demande explicite.

### Résolution nom → ID

```sql
-- Résoudre #[Objet][Équipement][Commande]# vers l'ID de la commande
SELECT c.id, c.name, c.type, c.subType, c.value,
       e.name AS equipement, o.name AS objet
FROM cmd c
JOIN eqLogic e ON e.id = c.eqLogic_id
LEFT JOIN object o ON o.id = e.object_id
WHERE o.name = '<Objet>'
  AND e.name = '<Équipement>'
  AND c.name = '<Commande>';

-- Chercher un équipement par nom (partiel)
SELECT e.id, e.name, e.eqType_name, e.isEnable, o.name AS objet
FROM eqLogic e
LEFT JOIN object o ON o.id = e.object_id
WHERE e.name LIKE '%<terme>%';

-- Chercher un scénario par nom
SELECT id, name, isActive, mode, `trigger` FROM scenario WHERE name LIKE '%<terme>%';
```

---

## Modèle de données

### Hiérarchie des objets

```
object                       ← pièce ou groupe (Salon, Chambre…)
└── eqLogic                  ← équipement (un plugin + sa config)
    └── cmd                  ← commande : info (mesure) ou action

scenario
└── scenarioElement          ← bloc IF / POUR / TANT QUE
    └── scenarioSubElement   ← condition / alors / sinon (métadonnées)
        └── scenarioExpression  ← expression réelle : condition ou action
```

**Point clé scénarios** : `scenarioSubElement.options` est souvent vide ou trompeur.
Les vraies conditions et actions sont **toujours** dans `scenarioExpression`. Ne jamais
conclure qu'un bloc est vide sans avoir requêté `scenarioExpression`.

### Tables clés

| Table | Rôle | Colonnes importantes |
|-------|------|---------------------|
| `object` | Pièces/groupes | `id`, `name` |
| `eqLogic` | Équipements | `id`, `name`, `eqType_name` (plugin), `isEnable`, `object_id`, `configuration` (JSON) |
| `cmd` | Commandes | `id`, `name`, `type` (info/action), `subType`, `value`, `eqLogic_id`, `configuration` (JSON) |
| `scenario` | Scénarios | `id`, `name`, `isActive`, `mode`, `` `trigger` `` (JSON), `scenarioElement` (JSON) |
| `scenarioElement` | Blocs IF/FOR | `id`, `type`, `subType` |
| `scenarioSubElement` | Cond/then/else | `id`, `type`, `subtype`, `scenarioElement_id` |
| `scenarioExpression` | ⭐ Expressions | `id`, `type`, `expression`, `options` (JSON), `scenarioSubElement_id`, `order` |
| `dataStore` | Variables | `key`, `value`, `type` ('scenario'), `link_id` (-1 = global) |
| `history` | Historique | `cmd_id`, `datetime`, `value` |
| `historyArch` | Historique archivé | idem |

### Colonnes JSON à parser

- `eqLogic.configuration` — paramètres plugin (mqttAddress, calcul, etc.)
- `cmd.configuration` — topic jMQTT, calcul virtual, etc.
- `scenario.trigger` — array d'IDs : `["#15663#","#1111#"]`
- `scenario.scenarioElement` — array d'IDs des blocs racine : `["8"]`
- `scenarioExpression.options` — paramètres d'action (scenario_id, message, etc.)

---

## Lire le contenu d'un scénario

### Étape 1 — Obtenir les IDs d'éléments racine
```sql
SELECT id, name, `trigger`, scenarioElement
FROM scenario WHERE name LIKE '%<nom>%';
-- scenarioElement → ex: ["8", "42"]
```

### Étape 2 — Récupérer tous les éléments enfants (récursif, 2-3 passes)
```sql
-- Passe 1 : enfants directs des racines
SELECT DISTINCT CAST(expr.expression AS UNSIGNED) AS child_id
FROM scenarioExpression expr
JOIN scenarioSubElement ss ON expr.scenarioSubElement_id = ss.id
WHERE ss.scenarioElement_id IN (<racines>)
  AND expr.type = 'element';

-- Répéter avec les nouveaux IDs jusqu'à stabilisation
```

### Étape 3 — Dump complet à plat
```sql
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
WHERE sel.id IN (<tous_les_ids>)
ORDER BY sel.id, ss.id, expr.order;
```

### Interpréter `scenarioExpression`

| `expr.type` | `expression` | Signification |
|-------------|--------------|---------------|
| `condition` | `#15663# == 1` | Condition du IF |
| `action` | `#15670#` | Appel commande action |
| `action` | `scenario` | Lancer scénario → `options.scenario_id` |
| `action` | `variable` | Écrire variable → `options.name` + `options.value` |
| `action` | `log` | Log → `options.message` |
| `action` | `equipement` | Activer/désactiver équipement |
| `element` | `511` | Référence à un sous-arbre (bloc SINON imbriqué) |

**Résoudre les IDs dans les expressions** : toute référence `#ID#` dans une expression
doit être résolue via `SELECT name FROM cmd WHERE id = <ID>` puis reformatée en
`#[Objet][Équipement][Commande]#` pour la présenter à l'utilisateur.

---

## Gotchas connus

### 1. `trigger` = mot réservé MySQL
```sql
-- ❌ Échoue silencieusement
SELECT trigger FROM scenario WHERE id = 4;

-- ✅ Correct
SELECT `trigger` FROM scenario WHERE id = 4;
```

### 2. `scenarioElement` n'a pas de colonne `scenario_id`
La relation scénario → éléments racine passe par le champ JSON `scenario.scenarioElement`,
pas par une FK directe. Ne pas chercher `scenario_id` dans `scenarioElement`.

### 3. Daemon ≠ eqLogic actif
Un plugin peut avoir son daemon actif et ses eqLogics désactivés (et vice-versa).
Toujours vérifier les deux :
```sql
SELECT name, isEnable FROM eqLogic WHERE eqType_name = '<plugin>';
-- + vérifier état daemon via SSH : php /var/www/html/core/php/jeeDaemon.php --daemon <plugin>
```

### 4. Configuration JSON : int vs string
Certains plugins stockent des FK en JSON sous forme d'entier (`"eqLogic":714`) d'autres
sous forme de string (`"eqLogic":"714"`). En cas de bug de routage plugin, inspecter
`eqLogic.configuration` et comparer avec ce qu'attend le code PHP du plugin.

### 5. `scenarioSubElement.options` ≠ contenu
Ce champ contient des métadonnées de bloc (timeout, repeat…), pas les actions/conditions.
Les vraies expressions sont dans `scenarioExpression`.

---

## Plugins courants

### jMQTT
- eqLogics de type broker (`eqLogic.configuration` contient `mqttAddress`, `mqttPort`, `mqttIncTopic`)
- eqLogics de type device, attachés à un broker
- cmd de type info : `configuration.topic` + `configuration.jsonPath`
- Problème courant : un device ne reçoit pas les messages → vérifier `configuration.eqLogic` (string vs int)

### Virtual
- cmd info calculées : `configuration.calcul` = formule avec `#ID#`
- cmd action ON/OFF : `configuration.virtualAction`, `configuration.updateCmdId`, `configuration.updateCmdToValue`

### Calendar (plugin agenda)
- eqLogics = agendas, cmd = événements avec plages horaires
- Inspectables via `eqLogic` + `cmd` comme n'importe quel plugin

### script / jeedom-connect / geoloc
- Inspecter `eqLogic.configuration` pour comprendre les sources de données

---

## Commandes utiles (argument du skill)

Quand l'utilisateur invoque ce skill avec `$ARGUMENTS` :

- **`audit`** → lancer un audit général : plugins actifs, nb équipements par plugin, scénarios actifs, dernières erreurs log
- **`scenario <nom>`** → résoudre et afficher la logique complète du scénario nommé
- **`eqlogic <nom>`** → inspecter l'équipement (config, commandes, valeurs actuelles)
- **`cmd "#[O][E][C]#"`** → résoudre la référence Jeedom, afficher valeur + historique récent
- **`plugin <nom>`** → état du plugin, nb eqLogics, erreurs daemon
- **`variable <nom>`** → valeur courante dans `dataStore`
- **`history "#[O][E][C]#"`** → 20 dernières valeurs historisées

Si `$ARGUMENTS` est vide, proposer le menu ci-dessus et demander l'accès SSH + MySQL.
```

---

## Points à approfondir dans le projet

1. **Résolution `#ID#` → `#[O][E][C]#`** dans les expressions de scénarios — écrire une
   procédure propre (batch lookup pour éviter N requêtes)

2. **Audit général** — définir un template de rapport : plugins, équipements orphelins
   (sans objet), scénarios inactifs depuis X jours, variables inutilisées

3. **Support API Jeedom** — alternative à MySQL pour les installations où l'accès DB
   n'est pas disponible : `POST /core/api/jeeApi.php` avec `apikey`

4. **Tests** — utiliser les fixtures du dossier `tests/` pour valider les requêtes
   sur des données réelles avant de les inclure dans le skill

5. **Jeedom 4.x vs 4.4+** — vérifier si le schéma `scenarioExpression` a évolué
   entre versions (colonne `options` : JSON vs texte sérialisé selon la version)
```
