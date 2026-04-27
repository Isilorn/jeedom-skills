# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Note: Each release mentions the Jeedom version tested at the time of publication.

---

## [Unreleased]

---

## [0.5.0] — 2026-04-27

Testé sur Jeedom 4.5.3.

### Added

- `jeedom-audit/references/plugin-agenda.md` : référence plugin Agenda (`eqType_name = 'calendar'`) — table `calendar_event` (structure complète), règle de récurrence (`repeat` JSON), commandes fixes (`in_progress`, `add_include_date`, `add_exclude_date`), requêtes d'audit, patterns de log
- `jeedom-audit/references/plugin-script.md` : référence plugin Script — syntaxes (`script`, `url`, `html`, `xml`, `json`), champs `scriptSyntax`/`jsonPath`/`regexp`, sécurité credentials, patterns de log (non présent sur box de réf.)
- `jeedom-audit/references/plugin-alarme.md` : référence plugin Alarme (`eqType_name = 'alarm'`) — zones multi-déclencheurs avec délais, modes, variables spéciales `#alarm_trigger#` et `#time#`, hooks d'événements (outbreak, activationOk/Ko, reenableTrigger), requêtes d'audit
- `jeedom-audit/references/plugin-thermostat.md` : référence plugin Thermostat — algorithme temporel avec coefficients autolearn, gestion fenêtres, modes (Confort/Eco/Absent), commandes complètes (order/status/mode/power/lock), requête état multi-thermostats, patterns de log (défaillance, température minimale)
- `jeedom-audit/references/plugin-generic-pattern.md` : pattern d'inspection en 4 temps pour tous les plugins non tier-1 — identification, eqLogics, commandes, logs ; cas MQTT Manager (`mqtt2`) documenté explicitement

### Changed

- `jeedom-audit/SKILL.md` §8 : 4 nouveaux plugins tier-1 (calendar, script, alarm, thermostat) — total 6 plugins tier-1
- `jeedom-audit/SKILL.md` §9 : index mis à jour avec statuts J4 pour les 5 nouveaux fichiers de référence

### Validated

- WF3 (diagnostic équipement) validé end-to-end sur box réelle — Thermostat bureau Géraud (db_query + cmd.value + logs_query)
- WF4 (diagnostic plugin) validé end-to-end sur box réelle — plugin thermostat (api_call plugin::listPlugin + eqLogics status + logs)

### Discovered

- `calendar_event.repeat` est un mot réservé MariaDB — toujours backtick-quoter dans les requêtes SQL
- `eqLogic.configuration` d'un agenda contient des champs thermostat hérités (`heating`, `cooling`, etc.) — vides, non utilisés par le plugin calendar
- `eqType_name = 'alarm'` (sans accent) pour le plugin Alarme
- `cmd.value` des commandes info thermostat = NULL en DB — les valeurs runtime sont dans la table `history`

---

## [0.4.0] — 2026-04-27

### Added

- `jeedom-audit/scripts/logs_query.py` : tail SSH structuré sur les logs Jeedom — détection automatique du répertoire (`/var/www/html/log/`), support des sous-répertoires (`scenarioLog/scenario{ID}.log`), filtrage grep côté client (sécurité injection shell)
- `jeedom-audit/scripts/api_call.py` : wrapper JSON-RPC Jeedom — blacklist V1 des méthodes modifiantes (`cmd::execCmd`, `scenario::changeState`, verbes `save/delete/update/...`), retry sur erreur réseau, filtrage `sensitive_fields` à la sortie
- `jeedom-audit/scripts/usage_graph.py` : graphe d'usage pour `cmd`, `eqLogic` et `scenario` — jointure `scenarioExpression → scenarioSubElement → scenarioElement → scenario`, détection des appels de scénarios via `options["scenario_id"]`, faux positifs blocs PHP signalés
- `jeedom-audit/references/plugin-virtual.md` : référence plugin Virtuel (9 sections) — patterns commandes info/action, `virtualAction`, `calcul`, requêtes d'audit
- `jeedom-audit/references/plugin-jmqtt.md` : référence plugin jMQTT (9 sections) — topics MQTT, `jsonPath`, daemon, `availability`, sécurité credentials
- `tests/unit/test_logs_query.py` : 22 tests (validation nom, résolution chemin, grep, timeout, sous-répertoires)
- `tests/unit/test_api_call.py` : 27 tests (blacklist, retry, filtrage, erreurs JSON-RPC, transport)
- `tests/unit/test_usage_graph.py` : 23 tests (cmd/eqLogic/scenario, classification conditions/actions, déduplication)
- `pyproject.toml` : ajout `[tool.pytest.ini_options]` avec `testpaths = ["tests/unit"]`

### Validated

- WF2 (diagnostic scénario) validé end-to-end sur box réelle — API (`state`+`lastLaunch`) + DB (arbre) + logs (`scenarioLog/`)
- WF6 (graphe d'usage) validé end-to-end sur box réelle — cmd 15663 → trigger + condition scénario 70
- Suite de tests complète : 123/123 passants

### Discovered

- `scenarioLog/` est un répertoire (un fichier `scenario{ID}.log` par scénario, pas un fichier unique)
- `lastLaunch` et `state` sont des champs runtime exposés via l'API uniquement (absents de la table `scenario` en DB)
- Les appels de scénarios sont dans `scenarioExpression.options["scenario_id"]` (pas dans `expression`)

> Jeedom : testé sur 4.5.3 (MariaDB 10.5, Debian)

---

## [0.3.0] — 2026-04-27

### Added

- `jeedom-audit/references/sql-cookbook.md` : 10 familles de requêtes SQL (audit, plugins, eqLogics, commandes, scénarios, traversée arbre, variables, historique, messages, batch WF1)
- `jeedom-audit/scripts/resolve_cmd_refs.py` : résolution batch `#ID#` → `#[Objet][Équipement][Commande]#` avec cache de session, tags système préservés, marquage `#ID_NON_RÉSOLU:X#`
- `jeedom-audit/scripts/scenario_tree_walker.py` : parcours récursif de l'arbre `scenarioElement` (anti-cycle, max_depth=3, troncature au-delà de 100 sous-éléments)
- `jeedom-audit/references/scenario-grammar.md` : interprétation complète de `scenarioExpression` (10 types d'expressions, pseudo-code WF5, anti-patterns WF7)
- `jeedom-audit/references/audit-templates.md` : structure des 12 sections du rapport WF1 (audit général)
- `jeedom-audit/references/health-checks.md` : seuils ✅/⚠️/❌ pour chaque indicateur de santé
- `tests/unit/test_resolve_cmd_refs.py` : 17 tests (cache, résolution, tags système, IDs non résolus)
- `tests/unit/test_scenario_tree_walker.py` : 16 tests (récursion, anti-cycle, max_depth, troncature)

### Validated

- WF5 (explication scénario) validé end-to-end sur box réelle — scénario "Présence Géraud Shelly" (id=70)
- WF1 (audit général) validé end-to-end sur box réelle — Jeedom 4.5.3 (177 eqLogics actifs, 57 scénarios actifs)
- Suite de tests complète : 51/51 passants

> Jeedom : testé sur 4.5.3 (MariaDB 10.5, Debian)

---

## [0.2.0] — 2026-04-27

### Added

- `jeedom-audit/SKILL.md` : 250 lignes, 11 sections, frontmatter conforme PLANNING §3.8-3.9
- `jeedom-audit/scripts/_common/` : `credentials.py`, `ssh.py`, `tags.py`, `sensitive_fields.py`, `version_check.py`
- `jeedom-audit/scripts/db_query.py` : wrapper SQL générique (stdin JSON → stdout JSON), échappement automatique du mot réservé `trigger`, filtrage champs sensibles
- `jeedom-audit/scripts/setup.py` : configuration initiale interactive avec détection automatique des credentials depuis la box
- `jeedom-audit/references/connection.md` : guide setup SSH+MySQL, stratégie credentials, création user RO
- `tests/unit/test_db_query.py` : 18 tests unitaires (escape trigger, substitution params, filtrage sensible, SSH mocké)

### Fixed

- SKILL.md corrige le PLANNING §3.9 gotcha #4 : topic jMQTT dans `configuration.topic` (cmd) et `configuration.mqttIncTopic` (broker), pas dans `logicalId`
- `lastLaunch`/`state` documentés comme champs runtime API uniquement (absents de la DB `scenario`)
- `collectDate`/`valueDate` supprimés des workflows (n'existent pas en DB)

> Jeedom : testé sur 4.5.x (MariaDB 10.5, Debian)

---

## [0.1.0] — 2026-04-27

### Added

- Bootstrap documentaire J0 : arborescence complète du repo selon spec PLANNING §2.2
- `docs/PLANNING.md` : brief de planification V1 complet (~55 décisions, jalons J0-J7)
- `docs/README.md` : index de navigation documentaire (3 axes)
- `docs/state/PROJECT_STATE.md` : état vivant du projet (initialisé J0)
- `docs/state/CONTRIBUTING-CLAUDE-CODE.md` : contrat opérationnel binôme PO/Claude Code
- `docs/decisions/` : 15 ADRs initiales couvrant les décisions structurantes V1 (statut Proposé → Accepté après validation PO)
- `docs/sessions/` : journal de bord, première entrée session bootstrap J0
- `docs/references-source/` : archives du projet source (`audit_db.md` sanitisé, `brief-initial.md`)
- `README.md` v0 (statut "en construction")
- `CONTRIBUTING.md` v0 (squelette — à étoffer à J7)
- `LICENSE` MIT, `.gitignore` Python, `pyproject.toml` minimal, `CHANGELOG.md`

> Jeedom : aucune version testée à J0 (pas de code skill — uniquement infrastructure documentaire)
