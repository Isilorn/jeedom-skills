# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Note: Each release mentions the Jeedom version tested at the time of publication.

---

## [Unreleased]

---

## [1.0.0] — 2026-04-28

Testé sur Jeedom 4.5.3 (MariaDB 10.5, Debian).

**Première release publique.** Skill `jeedom-audit` complète — 13 workflows, 6 plugins tier-1, 191 tests unitaires, 8 cas d'acceptation validés.

### Added

- `examples/` : 8 cas d'acceptation V1 (recette go/no-go release) — audit général, explication scénario, diagnostic causal, graphe d'usage, cartographie orchestration, audit jMQTT, refus modification, plugin tier-générique
- `docs/guides/getting-started.md` : tutoriel pas-à-pas de l'installation jusqu'au premier audit (15 min)
- `docs/guides/usage.md` : référence complète des 13 workflows avec exemples de phrases et formats de sortie
- `docs/guides/troubleshooting.md` : FAQ — connexion SSH, MySQL, mode API-only, erreurs courantes
- `docs/guides/architecture.md` : vue aérienne de la skill (scripts, routage, SKILL.md, stratégie de tests)
- `.github/workflows/tests.yml` : CI pytest sur Python 3.10/3.11/3.12 (push + PR sur `main`)
- `.github/ISSUE_TEMPLATE/` : 4 templates (bug, feature, divergence de version, nouveau plugin tier-1)
- `.github/PULL_REQUEST_TEMPLATE.md` : checklist contributeur
- `build/package_skill.py` : script de packaging — produit `jeedom-audit-vX.Y.Z.skill` depuis `jeedom-audit/`
- `docs/decisions/0018-release-v1.0.0.md` : ADR de release — bilan des écarts PLANNING/livraison
- `CONTRIBUTING.md` finalisé : critères d'acceptation PR, conventions de code, sanitisation fixtures, roadmap contributions

### Changed

- `README.md` : finalisé pour visiteur 30s — installation, configuration, exemples de phrases, limites V1
- `CONTRIBUTING.md` : squelette J0 → guide complet avec templates, critères et roadmap

### Validated (box réelle)

- 7/8 cas d'acceptation validés sur Jeedom 4.5.3 (cas 03 — diagnostic causal — en attente de matière PO)
- Tous les workflows WF1–WF6 + WF12 validés en SSH+MySQL
- WF5 + WF6 validés en mode API-only (router.py)

---

## [0.7.0] — 2026-04-28

Testé sur Jeedom 4.5.3.

### Added

- `jeedom-audit/scripts/scenario_tree_walker.py` : paramètre `follow_scenario_calls` (int) — suit les appels inter-scénarios (`action=start`) en profondeur décrémentale ; anti-cycle via `visited_scenarios` partagé entre tous les `walk()` récursifs ; chaque expression est enrichie d'une clé `called_scenario_tree` ; `_extract_scenario_call_id()` distingue `action=start` des autres (stop/activate/deactivate ignorés)
- `tests/unit/test_scenario_tree_walker.py` : 14 nouveaux tests — follow un niveau, décrémentation profondeur, anti-cycle direct, anti-cycle indirect A→B→A, scénario appelé introuvable, multi-appels dans le même bloc, follow_0 identique au défaut ; + 6 tests helper `_extract_scenario_call_id` (start, stop, type non action, condition, options invalides, scenario_id absent) — 30 tests au total (vs 16 en J2)
- `jeedom-audit/references/audit-templates.md` : template WF7 (suggestions de refactor — grille d'anti-patterns, structure *Constat/Impact/Pas-à-pas UI/Vérification*) et template WF12 (cartographie d'orchestration — prose ≤10 nœuds, mermaid `graph TD` >10 nœuds, conventions nœuds/arêtes)
- `tests/evals/eval-013-orchestration-mermaid-wf12.md` : WF12 orchestration mermaid — validé sur box réelle (sc13 "Mode_Absent_off" → 4 appels suivis, 0 cycle, 0 warning)
- `tests/evals/eval-014-refactor-wf7.md` : WF7 refactor verbal — anti-patterns, pas-à-pas UI, cas "aucun anti-pattern"
- `tests/evals/eval-015-lecture-rapide-wf8-11.md` : WF8-11 lecture rapide — 4 cas (valeur courante, historique, variable dataStore, recherche)

### Fixed

- Aucun

### Validated (box réelle)

- WF12 mode MySQL : `scenario_tree_walker.py` `follow_scenario_calls=3` sur sc13 "Mode_Absent_off" → chaîne sc10 (Mode_Normal_on), sc8 (Mode_Vacances_on), sc14 (Invites), sc20 (Centre de notifications) — 0 warning, anti-cycle correct
- Chaîne d'orchestration la plus riche sur la box : scénario 20 "Centre de notifications" appelé par 56 expressions réparties dans l'installation

### Discovered

- `JSON_TABLE` non disponible sur MariaDB 10.5 — utiliser `JSON_UNQUOTE(JSON_EXTRACT(...))` pour les requêtes sur colonnes JSON
- La box de référence n'a pas de chaîne >10 nœuds-scénario (max 5) — la règle prose/mermaid sera validée sur box communautaire plus complexe

---

## [0.6.0] — 2026-04-27

Testé sur Jeedom 4.5.3.

### Added

- `jeedom-audit/scripts/_common/router.py` : couche de routage transparent MySQL/API — `detect_capabilities()` (lazy + cache session), `route()` (8 types d'opérations × 3 modes), `with_fallback()` (fallback automatique + mention discrète) ; règles : `preferred_mode` `auto`/`mysql`/`api`, fallback basé sur les capacités détectées, `runtime_state`/`statistics` API-only même en mode `mysql`
- `tests/unit/test_router.py` : 50 nouveaux tests — detect_capabilities (SSH OK/KO, API OK/KO, exceptions, cache hit, clés distinctes), route × 3 modes (api/mysql/auto) sur toutes les opérations, with_fallback (succès, erreur dict, exception primary, fallback KO, résultats scalaire/liste)
- `tests/evals/eval-010-api-only-wf5.md` : scénario WF5 en mode `preferred_mode: "api"` — WF5 complet via `scenario::byId` + `cmd::byId`, mention mode API-only
- `tests/evals/eval-011-fallback-mysql-indisponible.md` : fallback automatique MySQL → API — MySQL KO, `with_fallback` déclenché, mention `"⚠ Données via API (MySQL indisponible)"`
- `tests/evals/eval-012-methode-bloquee.md` : blacklist V1 — `cmd::execCmd` bloqué avant envoi réseau, réponse utilisateur avec pas-à-pas UI, tableau des verbes bloqués
- `jeedom-audit/SKILL.md §3` : section routage automatique ajoutée — tableau `preferred_mode`, règles par opération, comportement sur bascule (silence/mention/refus), capacités WF en mode API-only

### Fixed

- Aucun

### Validated (box réelle)

- `router.detect_capabilities` : MySQL=True, API=True sur Jeedom 4.5.3
- WF5 mode API-only : `scenario::byId` scénario 70 "Présence Géraud Shelly" — state=stop, lastLaunch OK
- WF6 mode API-only : `cmd::byId` cmd 15663 — currentValue=1 OK
- `with_fallback` : MySQL KO simulé → fallback API → mention correcte

---

## [0.5.1] — 2026-04-27

Testé sur Jeedom 4.5.3.

### Added

- `jeedom-audit/references/api-jsonrpc.md` : référence API JSON-RPC Jeedom — méthodes autorisées par famille (Sanity, Découverte, Runtime, Scénarios, Résumés, Système), blacklist V1 (méthodes exactes + verbes), format requête/réponse JSON-RPC 2.0, champs runtime-only (`lastLaunch`, `state`, `currentValue`), codes d'erreur, gotchas
- `jeedom-audit/references/api-http.md` : transport HTTP — SSL et certificats auto-signés, configuration `credentials.json` (champs API), test de connectivité via curl, timeouts/retry, codes d'erreur transport fréquents, procédure de récupération de la clé API
- `jeedom-audit/references/sql-cookbook.md §11` : requêtes SQL par plugin tier-1 — thermostat (état multi-thermostats, coefficients appris, capteurs liés), alarme (mode courant, zones et modes), agenda (événements en cours, agendas désactivés, actions orphelines, événements avec état de récurrence)
- `docs/sessions/J5b-cadrage.md` : brief complet de démarrage de la session J5b — architecture `router.py`, règles de routage par type d'opération, comportement utilisateur, capacités WF en mode API-only, livrables, description des évals 10-12, critère de sortie
- `docs/decisions/0017-couche-routage-intelligent.md` : ADR — routage transparent (`router.py`) retenu vs flag `--source` explicite vs duplication de fallback

### Fixed

- `jeedom-audit/scripts/db_query.py` : `repeat` (mot réservé MariaDB, présent dans `calendar_event.repeat`) ajouté à la liste des mots auto-backtiqués, au même titre que `trigger` — 4 nouveaux tests, 127/127 passants
- `jeedom-audit/SKILL.md` §6 : gotchas 6 (`calendar_event.repeat`) et 7 (`cmd.value = NULL` thermostat) ajoutés ; titre "Top-5" → "Gotchas critiques"
- `jeedom-audit/SKILL.md` §9 : marqueurs `🔄 J3` corrigés en `✅ J3` pour `plugin-virtual.md`, `plugin-jmqtt.md`, `api_call.py`, `logs_query.py`, `usage_graph.py` ; `api-jsonrpc.md` et `api-http.md` ajoutés à l'index

### Discovered

- `api_call.py` était déjà implémenté en J3 — les livrables restants du J5 PLANNING étaient uniquement les deux fichiers de référence doc
- Le volet "couche de routage intelligent" (PLANNING §3.5) constitue un jalon à part entière (J5b) — trop substantiel pour être un appendice de J5

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
