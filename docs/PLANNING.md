# Brief de planification — skill `jeedom-audit`

> **⚠️ Document de référence original — pas une source d'autorité vivante.**
>
> Ce document capture les intentions et décisions de la session d'idéation initiale. Il est **intentionnellement conservé tel quel** pour préserver la traçabilité "prévu vs décidé". Il peut être en décalage avec l'état réel du projet.
>
> **Hiérarchie des sources d'autorité (en cas de conflit, la source la plus haute gagne) :**
>
> 1. `docs/decisions/` — ADRs : toute décision couverte par une ADR supersède ce document
> 2. `docs/state/PROJECT_STATE.md` — état actuel du projet (jalons, blocages, prochaines étapes)
> 3. Le code source et les tests
> 4. Ce document — intention originale, valide là où aucune des sources ci-dessus ne tranche
>
>
> Modifier ce document uniquement pour un amendement stratégique majeur (cf. `docs/state/CONTRIBUTING-CLAUDE-CODE.md §7`).

---

> Document autonome destiné à être ingéré par Claude Code en mode planification, dans un repo GitHub vide nouvellement créé. Ce brief résume l'intégralité des décisions issues d'une session d'idéation (D1.1 à D13.5) et liste les fichiers de référence à transférer depuis le projet source. **Claude Code n'aura pas accès au projet source** ; tout ce qui n'est pas listé dans la section « Fichiers à transférer » ou inliné ici n'existera pas dans le nouveau contexte.
>
> **Note méthodologique** : ce brief lui-même devient `docs/PLANNING.md` dans le nouveau repo (D13.5). Il peut évoluer à mesure que le projet avance, avec ADRs spécifiques pour les amendements non triviaux.

---

## 0. Modèle opérationnel ProductOwner / Claude Code

**À lire en premier par Claude Code.** Ce brief décrit ce qui doit être construit, mais pas qui le construit. Cette section pose le binôme.

### 0.1 Répartition des rôles

| Rôle | Qui | Responsabilités |
|---|---|---|
| **Product Owner (PO)** | L'utilisateur humain | Décide, oriente, arbitre. Fournit les matières que Claude Code ne peut pas produire seul (captures d'écran, validation sur box réelle, sanity check sanitisation, retours utilisateurs externes). Ne tape pas de code, ne rédige pas de doc. |
| **Implémenteur** | Claude Code | Code, rédige, propose, pose des questions structurées quand un arbitrage est nécessaire. Produit tous les artefacts du repo (ADRs, guides, SKILL.md, références, scripts, tests). Demande explicitement les matières physiques au PO. |

### 0.2 Conséquences pratiques pour Claude Code

**(a) Pas d'attente que le PO rédige.** Tout texte (ADR, guide, SKILL.md, README, code, tests) est **rédigé par Claude Code**. Le PO valide ou demande retouche.

**(b) Pose des questions structurées, pas ouvertes.** Quand un arbitrage est nécessaire, présenter au PO **2 à 4 options claires** avec leurs trade-offs plutôt qu'une question abstraite. Si possible, indiquer une recommandation par défaut. Le PO peut accepter, choisir une autre option, ou demander à débattre.

**(c) Préférer "valider un draft" à "produire ex nihilo via questions".** Quand il s'agit de rédiger une section ou un fichier, **Claude Code produit un draft** et le PO le critique. Plus efficient que d'extraire le contenu via une série de questions.

**(d) Auto-validation des choix triviaux.** Conventions de nommage internes, organisation de fichiers internes au-delà de ce qui est déjà tranché dans ce brief, choix de variables, formulations mineures dans les drafts : Claude Code décide seul et avance. Pas de gaspillage de cycles de validation sur des détails.

**(e) Demande explicite des matières physiques quand nécessaire.** Trois cas où le PO doit fournir quelque chose que Claude Code ne peut pas produire :
- **Captures d'écran** pour README, `getting-started.md`, `usage.md` (Claude Code ne navigue pas dans Jeedom)
- **Validation sur box réelle** : tests live impossibles côté Claude Code, le PO exécute la skill et rapporte les résultats
- **Sanity check sanitisation** : le linter aide mais ne remplace pas l'œil humain qui connaît son install (cf. 9.5)

Ces demandes doivent être **explicites et timées** : "À l'étape J1.20, j'aurai besoin de 2 captures Jeedom : (a) écran Plugins, (b) écran Réglages → Système → Configuration → API."

**(f) Sessions courtes orientées avancement, pas marathon.** Préférer plusieurs sessions ciblées avec validation du PO entre les deux à une session unique qui produit beaucoup sans validation intermédiaire.

### 0.3 Discipline de continuité (anticipée — détail en 7.3)

Le PO ne mémorise pas les détails techniques du projet entre sessions. C'est l'**axe 2 documentaire** (continuité Claude Code) qui assure la persistance — `docs/state/PROJECT_STATE.md` et `docs/sessions/*.md` mis à jour à chaque session significative.

À chaque début de session, Claude Code lit dans cet ordre : `docs/README.md` → `docs/state/PROJECT_STATE.md` → ADRs récentes → dernière entrée `docs/sessions/`. À chaque fin de session significative : maj `PROJECT_STATE.md` + nouvelle entrée session + ADR(s) si décisions non triviales prises.

---

## 1. Contexte et objectifs

**Public cible** : communauté francophone Jeedom — utilisateurs avancés mais pas experts (UI maîtrisée, mais pas la structure interne DB, pas l'API Jeedom).

**Objectif de la skill** : injecter dans Claude Code une connaissance structurelle de Jeedom 4.5 (DB, conventions, gotchas, patterns plugins courants) pour permettre **audits**, **diagnostics**, **explications de scénarios**, **suggestions de refactor**, et **accompagnement pas-à-pas dans l'UI** — sans jamais modifier l'installation directement.

**Règle absolue** : lecture seule côté technique. Toute modification est **décrite verbalement** et exécutée par l'utilisateur lui-même via l'UI Jeedom.

**Distribution V1** : repo GitHub public + fichier `.skill` packagé attaché à chaque GitHub Release.

**Versions Jeedom supportées V1** : **4.5 uniquement**. Antérieures (incl. 4.4) hors scope V1.

**Trois axes documentaires** (D13) traités spécifiquement en section 7 : traçabilité des décisions (ADRs), continuité de la mémoire Claude Code entre sessions, pédagogie communautaire.

---

## 2. Architecture (structure de fichiers)

### 2.1 Repo et nommage

- Nom du repo : `jeedom-skills` (pluriel, pour anticiper une 2ᵉ skill `jeedom-plugin-dev` à terme — pas en V1)
- Sous-dossier de la skill V1 : `jeedom-audit/` — c'est ce dossier qui correspond au "dossier-skill" Claude Code et qui sera packagé en `.skill`

### 2.2 Arborescence cible

```
jeedom-skills/                          ← repo public GitHub
│
├── jeedom-audit/                       ← LA SKILL V1 (= dossier-skill Claude Code, ce qui est packagé)
│   ├── SKILL.md                        ← frontmatter YAML + corps (200-300 lignes)
│   ├── references/
│   │   ├── connection.md               ← détails credentials, setup, sécurité MySQL
│   │   ├── sql-cookbook.md             ← templates SQL par cas d'usage
│   │   ├── scenario-grammar.md         ← grammaire scénarios, tags système, modes
│   │   ├── api-jsonrpc.md              ← méthodes JSON-RPC V1 + blacklist
│   │   ├── api-http.md                 ← API HTTP simple ?type=...
│   │   ├── plugin-virtual.md           ← tier-1
│   │   ├── plugin-jmqtt.md             ← tier-1
│   │   ├── plugin-agenda.md            ← tier-1
│   │   ├── plugin-script.md            ← tier-1
│   │   ├── plugin-generic-pattern.md   ← inspection tier-générique
│   │   ├── health-checks.md            ← status, daemons, messages, cron, MAJ
│   │   ├── logs-strategy.md            ← cartographie logs + tail/grep
│   │   └── audit-templates.md          ← modèles de rapport par workflow
│   └── scripts/
│       ├── README.md
│       ├── _common/
│       │   ├── __init__.py
│       │   ├── credentials.py
│       │   ├── ssh.py
│       │   ├── tags.py
│       │   ├── sensitive_fields.py
│       │   └── version_check.py
│       ├── db_query.py
│       ├── api_call.py
│       ├── logs_query.py
│       ├── resolve_cmd_refs.py
│       ├── scenario_tree_walker.py
│       └── usage_graph.py
│
├── docs/                               ← ARCHITECTURE DOCUMENTAIRE 3 AXES (D13)
│   ├── README.md                       ← index navigation : qui doit lire quoi
│   ├── PLANNING.md                     ← ce brief lui-même (référence V1)
│   │
│   ├── guides/                         ← AXE 3 : pédagogie communauté
│   │   ├── getting-started.md          ← tutoriel pas-à-pas première session (~15 min)
│   │   ├── usage.md                    ← référence des cas d'usage
│   │   ├── troubleshooting.md          ← FAQ + erreurs courantes
│   │   └── architecture.md             ← vue aérienne, pointe vers ADRs
│   │
│   ├── decisions/                      ← AXE 1 : traçabilité (ADRs)
│   │   ├── README.md                   ← index ADRs
│   │   ├── 0001-skill-vs-slash-command.md
│   │   ├── 0002-jeedom-version-supportee.md
│   │   ├── 0003-architecture-repo-multi-skills.md
│   │   ├── 0004-credentials-strategy.md
│   │   ├── 0005-mode-acces-mysql-vs-api.md
│   │   ├── 0006-lecture-seule-absolue.md
│   │   ├── 0007-13-intentions-utilisateur.md
│   │   ├── 0008-helpers-python-vs-sql-cookbook.md
│   │   ├── 0009-couverture-plugins-tier-1.md
│   │   ├── 0010-discipline-naming-OEC.md
│   │   ├── 0011-frontmatter-en-anglais.md
│   │   ├── 0012-distribution-skill-package.md
│   │   ├── 0013-licence-mit.md
│   │   ├── 0014-zero-telemetrie.md
│   │   └── 0015-strategie-documentaire.md
│   │
│   ├── state/                          ← AXE 2 : continuité Claude Code
│   │   ├── PROJECT_STATE.md            ← état vivant (mis à jour à chaque session)
│   │   └── CONTRIBUTING-CLAUDE-CODE.md ← discipline pour sessions futures + binôme PO/CC
│   │
│   ├── sessions/                       ← AXE 2 : journal de bord
│   │   ├── README.md
│   │   └── YYYY-MM-DD-<sujet>.md       ← une entrée par session significative
│   │
│   ├── references-source/              ← archives du projet source (cf. section 9.1)
│   │   ├── audit_db.md
│   │   ├── brief-initial.md
│   │   └── example-*.md
│   │
│   └── screenshots/                    ← captures fournies par le PO pour README et guides
│
├── tests/                              ← outils de dev (HORS skill, hors packaging)
│   ├── fixtures/
│   │   ├── README.md                   ← provenance + procédé sanitisation
│   │   ├── scenarios/
│   │   ├── plugins/
│   │   ├── audits/
│   │   └── db/
│   ├── unit/
│   │   ├── test_db_query.py
│   │   ├── test_api_call.py
│   │   ├── test_logs_query.py
│   │   ├── test_resolve_cmd_refs.py
│   │   ├── test_scenario_tree_walker.py
│   │   └── test_usage_graph.py
│   ├── integration/
│   │   ├── test_explanation_chain.py
│   │   └── test_orchestration_chain.py
│   ├── evals/
│   │   ├── README.md
│   │   └── eval-NNN-*.md (10-15 fichiers)
│   └── sanitize_check.py               ← linter optionnel
│
├── examples/                           ← recettes d'acceptation V1
│   ├── README.md
│   ├── audit-general.md
│   ├── explain-scenario.md
│   ├── usage-graph.md
│   ├── diagnose-presence.md
│   ├── orchestration.md
│   ├── refactor-suggestion.md
│   ├── audit-jmqtt.md
│   └── refus-modification.md
│
├── build/
│   ├── package_skill.py                ← produit jeedom-audit-vX.Y.Z.skill
│   └── list_todos.py                   ← optionnel : agrège TODOs traçables
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   ├── divergence_version.md
│   │   └── new_plugin_tier1.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       └── tests.yml                   ← CI minimal pytest unit + integration
│
├── README.md                           ← visiteur 30s (orienté communauté)
├── CONTRIBUTING.md                     ← contributeur humain
├── CHANGELOG.md                        ← Keep a Changelog
├── LICENSE                             ← MIT
├── pyproject.toml
└── .gitignore
```

### 2.3 Cadrage critique

- Le **dossier-skill** au sens Claude Code est `jeedom-audit/`, pas la racine. Toutes les autres arbo (`docs/`, `tests/`, `examples/`, `build/`, `.github/`) sont des outils de dev et de doc hors skill.
- Le packaging (`build/package_skill.py`) **ne zippe que le contenu de `jeedom-audit/`**.
- Les scripts dans `jeedom-audit/scripts/` sont les helpers exécutés par Claude Code en runtime ; les tests sont dans `tests/unit/` et `tests/integration/` (hors skill).
- `docs/PLANNING.md` (ce brief) sert de **référence vivante** du périmètre V1.

---

## 3. Décisions techniques (par sujet, avec rationale)

### 3.1 Sources d'autorité (D1.1)

- **Doc officielle Jeedom** = vérité de référence : `https://doc.jeedom.com/fr_FR`
- Sources canoniques markdown :
  - `github.com/jeedom/documentations` (général) — branche `master`, dossier `fr_FR/`
  - `github.com/jeedom/core` (core) — branche `alpha`, dossier `docs/fr_FR/`
  - `github.com/jeedom/plugin-<nom>` (plugins officiels) — `docs/fr_FR/`
- Forum communautaire (`community.jeedom.com`) = backup en cas de carence de la doc

### 3.2 Périmètre fonctionnel V1 (D1.3, D4.1 v3, D1.7)

**13 intentions dans 5 familles** :

| Famille | # | Intention |
|---|---|---|
| Audit | 1 | Audit général |
| Diagnostic | 2 | Diagnostic scénario |
| | 3 | Diagnostic équipement |
| | 4 | Diagnostic plugin |
| | 13 | Diagnostic causal d'une chaîne de scénarios (enquête forensique) |
| Explication | 5 | Explication scénario (avec comportement explicite sur appels imbriqués) |
| Graphe d'usage | 6 | Graphe d'usage d'une cmd / eqLogic / **scénario** |
| Cartographie d'orchestration | 12 | Arbre d'orchestration depuis un point d'entrée |
| Refactor | 7 | Suggestions de refactor verbales avec pas-à-pas UI **(aucune génération SQL ou script modificateur)** |
| Lecture rapide | 8 | Valeur courante d'une cmd |
| | 9 | Historique d'une cmd |
| | 10 | Variable dataStore |
| | 11 | Recherche |

**Hors scope V1** : présentation/design (vues, plans, widgets), gestion utilisateurs, infrastructure étendue (sauvegardes, réseau, marketplace avancé), interactions vocales, listeners, parsing logs structuré, format-aware plugins.

### 3.3 Lecture seule absolue (D1.5, D8.1)

| Phase | Posture | Périmètre |
|---|---|---|
| **V1** | Lecture seule absolue | Aucune méthode API modifiante, aucun INSERT/UPDATE/DELETE SQL, **même si l'utilisateur insiste**. Toute modif = pas-à-pas UI verbal |
| **V2** *(roadmap)* | Opérations réversibles à faible empreinte, via API officielle, avec confirmation explicite | Lancer un scénario, activer/désactiver, exécuter cmd action, écrire variable `dataStore` |
| **V3** *(roadmap)* | Modifications de configuration légère via API | Renommages, déplacements de hiérarchie, ajout de Types Génériques |
| **Jamais** | Hors limite indéfinie | UPDATE/DELETE/INSERT SQL directs, modifications de schéma, création de scénarios complexes |

**User MySQL read-only à perpétuité (D3.2)** : même en V2/V3, les écritures passent par l'API. Le user DB reste read-only.

**Méthodes API blacklistées V1** (à coder en dur dans `api_call.py` et documenter dans `references/api-jsonrpc.md`) :
- `cmd::execCmd`
- `scenario::changeState`
- `datastore::save`
- `interact::tryToReply`
- toute méthode dont le nom suggère une modification

### 3.4 Refus aux contournements (D8.1)

| Tentative | Réponse |
|---|---|
| *"Écris-moi le UPDATE SQL"* | Refus net + pas-à-pas UI |
| *"Génère un script Python qui appelle l'API pour modifier"* | Refus net pour méthodes blacklistées |
| *"Désactive la lecture seule pour cette session"* | Refus, posture inchangée |
| *"Pour mon test, simule la modification"* | OK pour la **décrire**, pas pour produire un artefact applicable |

Discipline : refus en une phrase, sans excuses longues, énergie sur l'alternative.

### 3.5 Méthodes d'accès V1 (D3.1, D3.3, D3.5)

**Deux modes coexistants V1** : SSH+MySQL (préféré par défaut) + API Jeedom (secondaire).

**Stratégie credentials** :
- Fichier `~/.config/jeedom-audit/credentials.json` (perm 600) — voie principale
- Sous-commande `setup` interactive — première utilisation
- Variables d'environnement (`JEEDOM_*`) en override
- User MySQL read-only dédié fortement recommandé via `setup`

**Format `credentials.json`** :
```json
{
  "preferred_mode": "auto",
  "ssh_alias": "Jeedom",
  "db_name": "jeedom",
  "db_user": "jeedom_audit_ro",
  "db_password_source": "remote_mycnf",
  "api_url": "https://my-jeedom.example.com",
  "api_key": "..."
}
```

**`db_password_source` valeurs** :
1. `"remote_mycnf"` — défaut recommandé. Le password vit dans `~/.my.cnf` côté serveur Jeedom (perm 600). Le client ne le connaît jamais
2. `"client_file"` — fallback si le serveur ne permet pas le `~/.my.cnf`. Lu via `MYSQL_PWD` env, jamais en argument CLI
3. `"prompt"` — demandé à chaque session, jamais persisté

**Anti-patterns bannis** : `mysql -p<pass>` en CLI (visible dans `ps aux`), password en argument SSH, password sans perm 600.

**Coexistence** : MySQL préféré, détection lazy au premier appel, fallback automatique avec mention si configuré, bascule par opération quand intrinsèquement meilleur (stats → API, logs → SSH, audit récursif → MySQL). Discrétion par défaut, mention sur bascule/limitation/manquant.

### 3.6 Sous-ensemble API V1 (D3.4)

Méthodes JSON-RPC à mobiliser, par famille :
- **Sanity** : `ping`, `version`, `config::byKey`
- **Découverte** : `jeeObject::all`, `jeeObject::byId`, `jeeObject::full`, `eqLogic::byType`, `eqLogic::fullById`, `eqLogic::byId`, `cmd::byId`, `cmd::all`
- **Données runtime** : `cmd::getHistory`, `cmd::getStatistique`, `cmd::getTendance`
- **Scénarios (lecture)** : `scenario::byId`, `scenario::all`
- **Résumés** : `summary::global`, `summary::byObjectId`
- **Système** : `plugin::listPlugin`, `event::changes`
- **Méthodes plugin** : par plugin tier-1 selon disponibilité

### 3.7 Plugins en couverture (D1.4, D5.1, D5.2)

**Tier-1 V1** (documentation profonde dans `references/plugin-X.md`) : `virtual`, `jmqtt`, `agenda`, `script`.

**Tous les autres plugins** : tier-générique via `references/plugin-generic-pattern.md` — pattern d'inspection en 4 temps (identification de surface, extraction d'échantillons, inférence Claude assumée explicitement, intégration aux workflows).

**Template `plugin-X.md`** : 9 sections normalisées (identification, eqLogic, cmd, audit, anti-patterns, scénarios, daemon, sécurité, liens). Pas d'exhaustivité visée, citer les sources, ne pas dupliquer la doc officielle.

**Versions testées** (D5.3) : chaque `plugin-X.md` indique la version testée du plugin. Au runtime, comparaison signalée si écart détecté.

### 3.8 Frontmatter SKILL.md (D2.3)

```yaml
---
name: jeedom-audit
description: Audit, diagnose, and explain a Jeedom 4.5 home automation install in a read-only way. Use this skill whenever the user asks about an existing Jeedom installation — diagnosing scenarios that don't trigger or misbehave, explaining what a scenario does step by step, mapping which scenarios depend on a given device or command (usage graph), auditing installation health (dead commands, orphan equipments, daemon status, plugin issues, history quality), suggesting cleanup or refactors verbally with UI walkthroughs, or interpreting Jeedom logs. Trigger this even when "Jeedom" isn't mentioned explicitly but the context implies it: mentions of eqLogic, scenario/scenarioElement, virtual switch, jMQTT, MQTT broker, dataStore, #ID# command references, or generally a French-speaking user asking about their home automation install. Always read-only — never modifies the install, only describes UI steps.
---
```

**À raffiner par les évals** au cours du développement (sujet 10).

### 3.9 Maquette du corps SKILL.md (D2.4) — 11 sections

| § | Section | Volume | Intention |
|---|---|---|---|
| 1 | Frontmatter YAML | ~10 l | Cf. 3.8 |
| 2 | Règle d'or absolue | ~15 l | Lecture seule + comportement face à l'insistance |
| 3 | Pré-requis et connexion | ~30 l | Modes SSH+MySQL, API JSON-RPC ; détection version (refus si ≠ 4.5) ; renvoi vers `references/connection.md` |
| 4 | Convention de nommage | ~20 l | `#[Objet][Équipement][Commande]#`, résolution `#ID#` ↔ humanName, **discipline absolue : jamais d'IDs dans la restitution** |
| 5 | Hiérarchie de données | ~25 l | Diagrammes texte object → eqLogic → cmd ; scenario → element → subElement → expression ; dataStore et history |
| 6 | Top-5 gotchas critiques | ~25 l | (1) `trigger` mot réservé MySQL ; (2) `scenarioSubElement.options` ≠ contenu ; (3) `scenarioElement` sans FK directe ; (4) jMQTT topic dans `logicalId` pas `configuration` ; (5) int vs string dans JSON config plugin |
| 7 | **Cas d'usage et workflows** | ~50 l | **Cœur fonctionnel.** Mapping prompt-typique → références à charger. Voir 3.10 |
| 8 | Plugins | ~25 l | Tier-1 (4 plugins, pointeurs vers leur fichier) ; tier-générique (pointeur vers pattern) |
| 9 | Index des références | ~20 l | **Liste explicite** des fichiers `references/` et `scripts/` avec une ligne par fichier — critique pour rendre la progressive disclosure effective |
| 10 | Mode opératoire de réponse | ~15 l | Discipline éditoriale : noms toujours, pas d'IDs ; markdown lisible ; jamais SQL/script de modification ; pas-à-pas UI ; mention explicite si données filtrées ; **workflows longs interruptibles** (D4.6) |
| 11 | Quand cette skill ne s'applique pas | ~10 l | Auto-rejet poli pour version < 4.5, installation Jeedom (non couvert), production de plugin (skill séparée future), autres systèmes domotiques |

**Volume cible total : 200-300 lignes** (max 500 lignes pour respecter la convention skill).

**Aucune requête SQL complète ni description plugin détaillée dans SKILL.md** — tout va dans `references/`.

### 3.10 Workflows V1 (D4.1 v3, D6.1)

Pour chaque workflow, le SKILL.md §7 indique : **(1) déclencheurs**, **(2) étapes**, **(3) sources**, **(4) format de sortie**, **(5) scripts mobilisés**.

#### Workflow 1 — Audit général
- **Déclencheurs** : "audit", "fais le tour", "santé de mon Jeedom", "qu'est-ce qui cloche", "diagnostic complet"
- **Étapes** : (a) version check ; (b) charger `sql-cookbook.md` § audit + `audit-templates.md` + `health-checks.md` ; (c) batch de requêtes en parallèle (config, plugins, eqLogics, scénarios, commandes mortes, dataStore, daemons, messages, mises à jour, qualité historique) ; (d) optionnel `tail -n 200` logs core/php ; (e) synthétiser
- **Sortie** : rapport markdown — synthèse exécutive (3-5 lignes) + 12 sections fixes (Système, Plugins, Équipements, Scénarios, Commandes mortes, Variables dataStore, Historiques, Daemons, Messages système, Mises à jour, Erreurs récentes). **Pas de section vide affichée** — sauter ou résumer en une ligne dans la synthèse.
- **Variantes** : "audit court" → top 3 par section ; "audit centré scénarios" → sections ciblées
- **Scripts** : aucun script obligatoire — SQL composé par Claude depuis cookbook

#### Workflow 2 — Diagnostic scénario
- **Déclencheurs** : "pourquoi le scénario X échoue", "X ne se déclenche pas", "X est cassé"
- **Étapes** : (a) résolution référence + désambiguïsation ; (b) `scenario_tree_walker.py` sans suivi imbriqué ; (c) lire `lastLaunch`, `state`, `isActive` ; (d) inspecter triggers et leurs valeurs courantes ; (e) `logs_query.py` sur `scenario_<id>.log` fenêtre récente ; (f) si schedule, vérifier format `Gi` ; (g) synthétiser pistes hiérarchisées
- **Sortie** : prose en sections — *État courant* / *Triggers* / *Dernières exécutions (logs)* / *Pistes de cause* (probable / possible / improbable avec evidence) / *Pas-à-pas pour vérifier dans l'UI*
- **Scripts** : `scenario_tree_walker.py`, `resolve_cmd_refs.py`, `logs_query.py`

#### Workflow 3 — Diagnostic équipement
- **Déclencheurs** : "[X] est mort", "ce capteur ne remonte plus"
- **Étapes** : (a) résoudre eqLogic ; (b) lire `status` JSON, `isEnable`, `eqType_name`, `configuration`, `logicalId` ; (c) état daemon plugin ; (d) `cmd.collectDate`, `cmd.valueDate` ; (e) checks plugin-spécifiques si tier-1 ; (f) `logs_query.py` plugin
- **Sortie** : prose — *État* / *Communication récente* / *Plugin et daemon* / *Erreurs log* / *Pistes*

#### Workflow 4 — Diagnostic plugin
- **Déclencheurs** : "jMQTT déconne", "le daemon ne démarre pas"
- **Étapes** : (a) identifier plugin ; (b) état (`plugin::listPlugin` ou table `plugin`) ; (c) état daemon ; (d) compter eqLogics enabled/disabled, warning/danger ; (e) `logs_query.py` plugin et `<plugin>_dep`

#### Workflow 5 — Explication scénario
- **Déclencheurs** : "explique-moi le scénario X", "que fait cette automatisation"
- **Étapes** : (a) résoudre + `scenario_tree_walker.py` (par défaut sans récursion appels imbriqués) ; (b) charger `scenario-grammar.md` ; (c) `resolve_cmd_refs.py` sur tout texte ; (d) construire pseudo-code IF/THEN/ELSE imbriqué
- **Comportement appels imbriqués** : par défaut mention par nom sans dérouler. Sur demande ("déroule la chaîne", "vue récursive") : `follow_scenario_calls=2-3` avec garde-fou anti-cycle
- **Sortie** : pseudo-code en bloc `code` + prose ; *Vue d'ensemble* / *Triggers* / *Mode et programmation* / *Pseudo-code* / *Effets de bord* / *Notes*

#### Workflow 6 — Graphe d'usage
- **Déclencheurs** : "qu'est-ce qui dépend de [X]", "qui utilise [Y]", "qu'est-ce qui appelle le scénario X"
- **Étapes** : (a) identifier cible (cmd, eqLogic, ou scénario) ; (b) `usage_graph.py` qui agrège triggers + conditions + actions + plugins consumers + dataStore + appels scénarios ; (c) filtrer false positives signalés
- **Sortie** : sections par catégorie d'usage (optionnelles si vides) — *Triggers* / *Conditions* / *Actions* / *Plugins consommateurs* / *Variables dataStore* / *Visualisations (V2 uniquement)*

#### Workflow 7 — Refactor
- **Déclencheurs** : "comment simplifier", "améliorer", "nettoyer", "factoriser"
- **Étapes** : (a) lancer audit/explication selon cible ; (b) identifier anti-patterns (conditions dupliquées, délais en dur, `triggerId()` déprécié, cmd sans Type Générique, scénarios désactivés référencés, variables globales orphelines) ; (c) hiérarchiser par impact/effort
- **Sortie** : liste hiérarchisée. Pour chaque suggestion : *Constat* / *Impact* / *Pas-à-pas UI* / *Vérification*. **Aucun SQL ni script modificateur**.

#### Workflows 8-11 — Lecture rapide
- **Workflow 8** Valeur courante : prose une ligne (`[Salon][Température][Valeur] = 21.3 °C, mis à jour il y a 2 minutes`)
- **Workflow 9** Historique : tableau si <50 lignes, résumé stat sinon ; API privilégiée (`cmd::getHistory`)
- **Workflow 10** Variable dataStore : valeur + portée (globale `link_id=-1` / locale)
- **Workflow 11** Recherche : tableau filtrable par critères verbalisés

#### Workflow 12 — Cartographie d'orchestration
- **Déclencheurs** : "trace la chaîne d'appels à partir de X", "montre le flux complet quand Y", "qui appelle qui"
- **Étapes** : (a) point d'entrée (scénario/cmd/événement) ; (b) si cmd, trouver scénarios qui l'ont en trigger ; (c) `scenario_tree_walker.py` avec `follow_scenario_calls=3` et anti-cycle ; (d) construire arbre annoté des conditions
- **Sortie** : choix automatique — prose hiérarchique indentée si ≤10 nœuds, **mermaid `graph TD`** si >10 nœuds

#### Workflow 13 — Diagnostic causal d'une chaîne (forensique)
- **Déclencheurs** : "ce scénario fait X au lieu de Y", "remonte la chaîne", "trouve d'où vient le bug"
- **Particularité** : enquête dirigée par les **données** (comportement observé) plutôt que par la **structure**. Profondeur non déterminée a priori. **Interactif** — l'utilisateur peut interrompre/rediriger à chaque étape (cf. D4.6).
- **Étapes** : (a) récolter indices initiaux (comportement, fenêtre, point d'arrivée) ; (b) remonter depuis le point d'arrivée via `usage_graph.py` ; (c) regarder logs sur fenêtre temporelle pour chaque candidat ; (d) suivre triggers en chaîne ascendante avec garde-fous (max 5 niveaux, anti-cycle, anti-explosion >10 candidats à un niveau) ; (e) restituer récit causal
- **Sortie** : récit chronologique — *Indice de départ* / *Étapes de remontée* (sections par scénario inspecté avec evidence à chaque saut) / *Cause racine* / *Suggestions de correction*
- **Limitation** : indisponible en mode API-seul (logs requis)

### 3.11 Couplage scripts ↔ workflows (D7.4)

| Workflow | Scripts mobilisés |
|---|---|
| 1 — Audit général | Aucun script obligatoire ; SQL ad-hoc depuis cookbook |
| 2 — Diagnostic scénario | `scenario_tree_walker.py` (sans récursion), `resolve_cmd_refs.py`, `logs_query.py` |
| 3, 4 — Diagnostic eqLogic / plugin | SQL ad-hoc, `logs_query.py` |
| 5 — Explication scénario | `scenario_tree_walker.py`, `resolve_cmd_refs.py` |
| 6 — Graphe d'usage | `usage_graph.py`, `resolve_cmd_refs.py` |
| 7 — Refactor | Composition des sorties d'autres workflows |
| 8-11 — Lecture rapide | SQL ou API directe + `resolve_cmd_refs.py` pour mise en forme |
| 12 — Cartographie d'orchestration | `scenario_tree_walker.py` avec `follow_scenario_calls=3`, `resolve_cmd_refs.py` |
| 13 — Diagnostic causal | Composition `usage_graph.py` + `scenario_tree_walker.py` au fil de l'enquête + `logs_query.py` |

### 3.12 Conventions scripts (D2.6, D2.7, D7.1-D7.7)

- **Langage** : Python 3
- **Dépendances minimales** : `mysql-connector-python` (ou équivalent), `requests`, pas de framework lourd
- **Convention I/O** :
  - Entrée : args CLI (cas simples) ou JSON sur stdin (cas complexes)
  - Stdout : **JSON structuré uniquement**, format documenté en tête de chaque script
  - Stderr : log et erreurs en français lisible humainement (D12.1)
  - Code retour : 0 succès, ≠0 erreur
- **Crédentials** : jamais en argument CLI ; via env vars ou via `_common/credentials.py` qui lit `~/.config/jeedom-audit/credentials.json`
- **Anti-explosion** :
  - Une opération = un script (mono-responsabilité)
  - Batch SQL `WHERE id IN (...)` toujours, jamais N requêtes par ID
  - Jointure en mémoire Python plutôt que CTE SQL complexes
  - Cache de session en mémoire et `/tmp/` (5 min TTL)
- **Anti-pattern banni** : `audit_everything.py` ou tout helper omnibus

### 3.13 Spécifications scripts V1 (D7.5)

#### `_common/credentials.py`
Lit `~/.config/jeedom-audit/credentials.json` (perm 600), applique override env vars `JEEDOM_*`, retourne dict standardisé. Lance `setup` interactif si absent.

#### `_common/ssh.py`
Wrapper subprocess SSH unifié. Gère timeout, retries, captures stderr proprement. Jamais de password en argument CLI.

#### `_common/tags.py`
Liste hard-codée des tags système Jeedom à préserver intacts dans `resolve_cmd_refs.py` : `#trigger_id#`, `#trigger_value#`, `#trigger_name#`, `#user_connect#`, `#sunset#`, `#sunrise#`, `#time#`, etc.

#### `_common/sensitive_fields.py` (D8.3)
Liste hard-codée de noms de champs sensibles à filtrer : `password`, `pwd`, `pass`, `apikey`, `api_key`, `token`, `secret`, `auth`, `mqttPassword`. Match insensible à la casse, partiel.

#### `_common/version_check.py` (D9.1)
Détecte version Jeedom (API `version` → API HTTP `?type=version` → MySQL `config`), cache de session, applique politique : refus < 4.4, refus avec mention 4.4, OK 4.5, warning 4.6+.

#### `db_query.py`
Wrapper SQL générique. Exécute requête paramétrée via SSH+MySQL, retourne résultat en JSON. Centralise échappement `trigger` mot réservé. Applique filtrage `sensitive_fields.py` à la sortie.
- **Entrée** : `{"query": "...", "params": [...]}` sur stdin
- **Sortie** : `{"rows": [...], "_filtered_fields": [...]}`

#### `api_call.py`
Wrapper JSON-RPC. Applique blacklist D3.4 côté code. Gère erreurs -32xxx, retry une fois sur timeout. Filtrage sensitive_fields à la sortie.
- **Entrée** : `{"method": "...", "params": {...}}` sur stdin
- **Sortie** : `{"result": ..., "_filtered_fields": [...]}` ou `{"error": {...}}`

#### `logs_query.py`
Tail SSH structuré sur fichiers de log Jeedom.
- **Entrée** : `{"log_name": "scenario_42|core|<plugin>|...", "max_lines": 200, "min_level": "WARNING|ERROR", "since": "ISO8601"}` sur stdin
- **Sortie** : `{"lines": [...], "log_path": "...", "found": true}` ou `{"found": false, "reason": "..."}`

#### `resolve_cmd_refs.py` (D7.1)
Résolution `#ID#` → `#[O][E][C]#` par batch.
- **Entrée** : `{"text": "...", "include_eqlogics": true, "include_scenarios": true}` sur stdin
- **Sortie** : `{"resolved_text": "...", "lookups": {"15663": "[O][E][C]"}, "unresolved_ids": [...], "stats": {"total_refs": N, "resolved": M, "unresolved": K}}`
- **Implémentation** : 3 requêtes SQL groupées (cmd, eqLogic, object), cache de session, préserve les tags système intacts.

#### `scenario_tree_walker.py` (D7.2)
Récupération récursive d'un scénario.
- **Entrée** : `{"scenario_id": 42, "follow_scenario_calls": 0, "max_depth": 3}` sur stdin
- **Sortie** : structure arborescente avec `tree`, `called_scenarios` (si suivi), `warnings` (cycles, profondeur, explosion)
- **Implémentation** : 3 requêtes SQL par scénario (jointure mémoire Python), garde-fous anti-cycle / max_depth=3 / >100 sous-éléments tronqués
- **Mono-responsabilité** : ne résout pas les `#ID#` (pipeline avec `resolve_cmd_refs.py`)

#### `usage_graph.py` (D7.3)
Graphe d'usage agrégé.
- **Entrée** : `{"target_type": "cmd|eqLogic|scenario", "target_id": 15663}` sur stdin
- **Sortie** : `{"target": {...}, "references": {"triggers": [...], "conditions": [...], "actions": [...], "plugin_consumers": [...], "datastore_refs": [...], "scenario_calls": [...]}, "false_positive_warnings": [...]}`
- **Implémentation** : 5-6 requêtes SQL par source avec `LIKE '%#ID#%'` ou `LIKE '%"ID"%'` ou `LIKE '%:ID%'` selon source. Pas de récursion (workflow 12 utilise le walker).

### 3.14 Templates de sortie (D6.1, D6.2)

**Quatre formes utilisées** :
1. **Prose (paragraphes)** — synthèses, pistes de cause, récits causaux
2. **Pseudo-code IF/THEN/ELSE** — explication scénario (workflow 5)
3. **Tableaux markdown** — listes structurées, comparaisons, top N (workflows 1, 6, 8-11)
4. **Mermaid** — cartographie d'orchestration >10 nœuds uniquement (workflow 12) ou sur demande explicite

**Convention pseudo-code (workflow 5)** :
```
SI #[Maison][Présence Géraud][Présence]# == 1 ALORS
  ATTENDRE 30 secondes
  EXÉCUTER scénario "Présence-V2-Présent"
  METTRE #variable_globale_NbAbsGeraud# à 0
SINON SI #[Maison][Présence Géraud][Présence]# == 0 ALORS
  EXÉCUTER scénario "Présence-V2-Absent"
FIN SI
```
- Mots-clés majuscules françaises (SI, ALORS, SINON, FIN SI, ATTENDRE, EXÉCUTER, METTRE)
- Noms de scénarios en `"guillemets"`
- Variables locales `#var#`, globales `#variable_globale_xxx#`
- Cmd en `#[O][E][C]#`

### 3.15 Discipline `#[O][E][C]#` — chaîne 4 couches (D6.3, D4.3)

1. **Instructions explicites SKILL.md §10** : "Toute restitution utilise `#[Objet][Équipement][Commande]#`. Aucun ID brut. Si un ID n'est pas résolu, mentionner explicitement et proposer alternative."
2. **Script `resolve_cmd_refs.py`** : tout texte produit destiné à l'utilisateur passe par lui. Signale les `unresolved_ids`.
3. **Exemples disciplinés** dans `references/audit-templates.md` et `examples/`.
4. **Validation post-hoc dans les évals** : test automatique — pas d'occurrence de `#\d+#` non encadrée d'autre format dans la sortie attendue.

### 3.16 Désambiguïsation proactive (D4.2)

- **Référence ambiguë par nom** : short-list ("Je vois 3 scénarios contenant 'Géraud', 1 eqLogic 'Présence Géraud'. Lequel ?")
- **Intention floue** ("regarde mon Jeedom") : menu d'options sans imposer de défaut
- **Référence introuvable** : correspondances proches ou liste plausible

### 3.17 NLP en entrée + workflows déterministes en interne (D4.4)

- Pas de syntaxe formelle type `/jeedom audit`
- Phrasings canoniques **documentés dans le README** comme exemples mais **non obligatoires**
- Chaque intention reconnue déclenche un workflow canonique reproductible
- Anti-patterns : forcer "audit:scenario:42", mots-clés réservés, réponse standardisée verbeuse à chaque invocation

### 3.18 Questions de suivi (D4.5)

À la fin de la réponse, ciblées, optionnelles, pas systématiques. Format type :
> *Pour aller plus loin : veux-tu que je vérifie les logs récents de ce scénario ? Que je trace le graphe d'usage de la cmd `[Maison][Présence Géraud][Présence]` ?*

### 3.19 Workflows longs interruptibles (D4.6)

Workflows 1, 2, 12, 13 : structurés en étapes visibles, l'utilisateur peut interrompre et rediriger. Pas de raisonnement monolithique masqué. Cohérent avec le récit causal de l'expérience utilisateur (workflow 13).

### 3.20 Cas limites (D4.7)

| Cas | Comportement |
|---|---|
| Hors périmètre (modification, autre système, < 4.5) | Refus poli, alternative pas-à-pas si pertinent |
| Version Jeedom < 4.4 | Refus net |
| Version 4.4.x | Refus avec mention "support 4.4 en roadmap" |
| Version 4.5.x | OK silencieux |
| Version 4.6+ | Warning + continuer ("teste à tes risques") |
| Crédentials invalides | Diagnostic ciblé sans deviner ; relancer `setup` ou correction |
| API restriction `api::forbidden::method` | Mentionner méthode bloquée, expliquer ajustement regex côté admin, fallback MySQL |
| Schéma DB inattendu | Détecter via INFORMATION_SCHEMA, signaler exactement quoi manque |
| JSON `configuration` corrompu | Signaler le record, continuer, pas de plantage global |
| Scripts lèvent exception | stderr récupéré, erreur explicite à l'utilisateur, suggérer report bug |
| Insistance utilisateur après refus | Posture inchangée, pas de cession |

### 3.21 Filtrage données sensibles (D8.3) — 4 niveaux

1. **Liste hard-codée** dans `scripts/_common/sensitive_fields.py`
2. **Filtrage automatique à la sortie** des wrappers `db_query.py` et `api_call.py` ; substitution par `[FILTRÉ]` ; mention `_filtered_fields` dans la sortie
3. **Filtrage regex sur blobs** (logs, expressions) : pattern `(password|token|apikey)\s*[=:]\s*\S+` → `\1=[FILTRÉ]`
4. **Refus explicite** aux demandes directes ("donne-moi le mot de passe broker MQTT") même si techniquement lisible

**Transparence systématique** : toujours mentionner les champs filtrés dans la restitution, avec pas-à-pas pour consultation directe via UI Jeedom si nécessaire.

### 3.22 Comportement en erreur (D8.2)

| Erreur | Comportement |
|---|---|
| SSH connexion refusée | Diagnostic alias/host/clé ; fallback API si dispo |
| MySQL auth refusée | Diagnostic user/mode/`~/.my.cnf` ; corrections proposées |
| API timeout | Retry **une fois** avec backoff 2s |
| API `-32xxx` | Mentionner code ; suggérer correction selon code |
| API méthode inexistante (`-32500`) | Probable changement de version, suggérer report repo |
| API droits insuffisants (`-32701`) | Suggérer régénération clé avec profil admin |
| SQL table/colonne absente (1146/1054) | Signaler exactement quoi manque, suggérer report |
| JSON malformé record | Signaler record (id, table), continuer |
| Logs absents | Signaler que jamais exécuté ou logs purgés ; continuer sur structure |
| Profondeur max atteinte | Mentionner et proposer d'augmenter |
| Cycle détecté | Mentionner explicitement la chaîne, continuer autres branches |

**Principe directeur** : transparence. Pas masquer.

### 3.23 Privacy / télémétrie (D12.2)

**Zéro télémétrie en V1**. Aucune donnée n'est envoyée à l'extérieur de l'environnement utilisateur. Mention explicite dans le README sous une section "Privacy" courte.

### 3.24 Mode plan vs run dans Claude Code (D12.3)

La skill nécessite l'exécution d'outils (`bash` notamment). Le README mentionne ce prérequis pour un nouvel utilisateur.

### 3.25 Langue (D12.1, D2.3)

- Frontmatter : **anglais** (convention écosystème, matching cross-langue)
- Corps SKILL.md, references/, examples/, restitutions à l'utilisateur : **français**
- Messages d'erreur stderr scripts, logs runtime : **français**
- Labels JSON techniques (clés stdout) : **anglais** (interopérabilité)
- Documentation `docs/` : **français** (audience communauté francophone)
- ADRs : **français**

---

## 4. Périmètre fonctionnel V1 (synthèse)

**Ce que la skill V1 fait** :
- Audit général d'une installation Jeedom 4.5
- Diagnostics ciblés (scénario, équipement, plugin, chaîne causale)
- Explication de scénarios (avec ou sans suivi des appels imbriqués)
- Graphe d'usage de cmd / eqLogic / scénario
- Cartographie d'orchestration depuis un point d'entrée
- Suggestions de refactor verbales avec pas-à-pas UI
- Lecture rapide (valeurs courantes, historiques, variables, recherches)
- Lecture des logs niveaux 1+2 (cartographie + tail/grep brut)
- Tier-1 plugins : virtual, jMQTT, agenda, script
- Tier-générique pour tous autres plugins (inférence assumée)

**Ce que la skill V1 ne fait pas** :
- Aucune modification (UPDATE/DELETE/INSERT SQL ; méthodes API modifiantes ; production de scripts ou SQL applicables)
- Pas de support Jeedom < 4.5
- Pas d'audit présentation/design (vues, plans, widgets)
- Pas de gestion utilisateurs
- Pas d'audit infrastructure étendu (sauvegardes, réseau, marketplace avancé)
- Pas d'inspection interactions vocales / listeners
- Pas de parsing logs structuré ni format-aware plugins (niveau 3+ logs)
- Pas de mode offline (consommation de dump JSON)
- Pas d'aide à l'installation Jeedom ni au développement de plugins

---

## 5. Plan de livraison

> **Conventions de la section** : sauf mention "PO fournit", chaque livrable est **rédigé/codé par Claude Code**, qui pose les questions structurées nécessaires au PO pour les arbitrages. Les livrables marqués "PO fournit" attendent une matière physique du PO (capture, validation sur box réelle, etc.).

### Jalon J0 — Bootstrap documentaire (avant tout code)

**Objectif** : poser l'infrastructure documentaire avant la première ligne de code, pour que toutes les décisions et sessions ultérieures soient traçables.

**Livrables Claude Code** :
- Création du repo `jeedom-skills` sur GitHub *(PO doit fournir l'accès initial — ouverture du repo via interface GitHub ou validation que Claude Code crée via gh CLI)*
- Initialisation de la structure 2.2 (dossiers + `.gitkeep`)
- `LICENSE` MIT, `.gitignore` Python standard, `pyproject.toml` minimal, `CHANGELOG.md` initial
- `docs/PLANNING.md` = ce brief, transféré tel quel
- `docs/README.md` (index navigation) — Claude Code rédige
- `docs/state/PROJECT_STATE.md` (état initial, jalon J0 en cours) — Claude Code rédige
- `docs/state/CONTRIBUTING-CLAUDE-CODE.md` (discipline binôme PO/CC + routine sessions) — Claude Code rédige selon spec 7.3
- `docs/decisions/README.md` (index ADRs + template ADR fixe) — Claude Code rédige
- **15 ADRs initiales** (cf. 7.2) — Claude Code rédige à partir de la matière du brief, soumet par lots de 3-5 au PO pour validation
- `docs/sessions/README.md` + première entrée de session documentant le bootstrap — Claude Code
- `README.md` v0 (statut "en construction", tagline minimale) — Claude Code rédige, PO valide
- `CONTRIBUTING.md` v0 (squelette à étoffer à J7) — Claude Code

**Livrables PO** :
- Validation des ADRs initiales par lots
- Validation `CONTRIBUTING-CLAUDE-CODE.md` (c'est le contrat opérationnel du binôme — important)

**Critère de sortie J0** : un nouveau contributeur (ou une nouvelle session Claude Code) peut comprendre l'état du projet en lisant `docs/README.md` puis les ADRs.

### Jalon J1 — Skeleton skill + connexion SSH+MySQL stabilisée

**Objectif** : la skill se charge, `setup` interactif fonctionne, `db_query.py` exécute des SELECT contre une fixture sanitisée et une vraie box.

**Livrables Claude Code** :
- `jeedom-audit/SKILL.md` rédigé selon maquette 3.9 et frontmatter 3.8
- `jeedom-audit/scripts/_common/credentials.py`, `ssh.py`, `version_check.py`, `tags.py`, `sensitive_fields.py`
- `jeedom-audit/scripts/db_query.py` opérationnel
- `jeedom-audit/references/connection.md` rédigé
- `jeedom-audit/references/sql-cookbook.md` rédigé (sections audit + cmd + eqLogic)
- Sous-commande `setup` interactive
- Tests unitaires `tests/unit/test_db_query.py`
- Maj `docs/state/PROJECT_STATE.md`, entrées `docs/sessions/`, ADRs si décisions imprévues émergent

**Livrables PO** :
- Sanity check sanitisation des fixtures transférées (sécurité — PO connaît son install et repère ce qui doit être anonymisé)
- Validation sur box réelle : exécuter le `setup` interactif et l'audit général sur fixture
- Captures d'écran des étapes de configuration MySQL (création user read-only, `~/.my.cnf`) si nécessaire pour `references/connection.md`
- Cross-check `audit_db.md` vs doc officielle Jeedom 4.5 (Claude Code propose les divergences détectées, PO confirme la pertinence)

**Critère de sortie J1** : audit général sur fixture passe (workflow 1 manuellement validé) ET sur box réelle du PO.

### Jalon J2 — Workflows DB-only + helpers cœur

**Objectif** : workflows 1, 2 (sans logs), 5, 6 fonctionnels en mode SSH+MySQL.

**Livrables Claude Code** :
- `resolve_cmd_refs.py`, `scenario_tree_walker.py`, `usage_graph.py`
- `references/scenario-grammar.md`, `references/audit-templates.md`, `references/health-checks.md`
- Tests unitaires des trois scripts
- Tests d'intégration `test_explanation_chain.py`
- Évals 1-3 (audit, explication, graphe) — Claude Code rédige les fichiers d'éval, exécute manuellement, rapporte les résultats au PO
- `docs/guides/getting-started.md` v1 — Claude Code rédige draft, PO valide pédagogie
- Maj `docs/state/PROJECT_STATE.md`, sessions journalisées

**Livrables PO** :
- Validation des évals 1-3 sur fixture et idéalement sur box réelle
- Validation pédagogique des drafts `getting-started.md` (lecture comme un nouvel utilisateur, retour sur ce qui n'est pas clair)

**Critère de sortie J2** : workflow 5 sur scenario fixture produit pseudo-code avec discipline `#[O][E][C]#` ; workflow 6 liste structurée par catégorie.

### Jalon J3 — Logs + diagnostic causal

**Objectif** : workflows 2 (avec logs), 3, 4, 13 fonctionnels.

**Livrables Claude Code** :
- `logs_query.py`
- `references/logs-strategy.md`
- Tests unitaires `test_logs_query.py`
- Évals 4-6 (diagnostic scénario, équipement, causal)
- Maj `docs/state/PROJECT_STATE.md`

**Livrables PO** :
- Fournir un cas réel pré-identifié de bug de chaîne de scénarios sur la box du PO (l'expérience qu'il a évoquée pendant l'idéation) pour servir de cas de validation du workflow 13
- Validation sur box réelle du workflow 13 sur ce cas

**Critère de sortie J3** : workflow 13 sur cas réel pré-identifié remonte la chaîne avec evidence à chaque saut.

### Jalon J4 — Plugins tier-1 et tier-générique

**Objectif** : couverture documentaire des 4 plugins tier-1 + pattern générique.

**Livrables Claude Code** :
- `references/plugin-virtual.md`
- `references/plugin-jmqtt.md`
- `references/plugin-agenda.md`
- `references/plugin-script.md`
- `references/plugin-generic-pattern.md`
- Évals 7-9 (audit jMQTT, plugin tier-générique inconnu, refus modification)

**Livrables PO** :
- Validation que la matière sur les 4 plugins correspond bien à ce qu'il observe sur sa propre install (Claude Code peut errer sur des subtilités plugin-spécifiques que seul un utilisateur réel détecte)

**Critère de sortie J4** : audit jMQTT distingue broker/device, filtre password, identifie topic dans `logicalId`.

### Jalon J5 — API Jeedom

**Objectif** : mode API JSON-RPC opérationnel avec coexistence MySQL/API.

**Livrables Claude Code** :
- `api_call.py` avec blacklist D3.4
- `references/api-jsonrpc.md`
- `references/api-http.md`
- Tests unitaires `test_api_call.py`
- Tests d'intégration sur bascule MySQL ↔ API
- Évals 10-12 (mode API only, fallback automatique, méthode bloquée)

**Livrables PO** :
- Génération d'une clé API Jeedom dédiée pour les tests (côté UI Jeedom)
- Validation sur box réelle du mode API only

**Critère de sortie J5** : workflows 5 et 6 fonctionnent en mode API-only (avec limitations documentées : pas de logs).

### Jalon J6 — Cartographie d'orchestration et workflows compositionnels

**Objectif** : workflows 7 (refactor) et 12 (orchestration) opérationnels.

**Livrables Claude Code** :
- Mode `follow_scenario_calls` activé dans `scenario_tree_walker.py`
- Templates refactor dans `audit-templates.md`
- Évals 13-15 (orchestration mermaid, refactor, lecture rapide)

**Livrables PO** :
- Validation sur box réelle du workflow 12 (orchestration) sur une chaîne complexe de la propre installation

### Jalon J7 — Recette, doc communautaire et release

**Objectif** : passer la recette d'acceptation V1 (D10.4), finaliser la doc pédagogique, publier `v1.0.0`.

**Livrables Claude Code** :
- 8 cas d'acceptation (`examples/`) tous validés sur fixture
- `README.md` finalisé (orienté visiteur 30s, cf. 8.5)
- `docs/guides/getting-started.md` finalisé
- `docs/guides/usage.md` complet
- `docs/guides/troubleshooting.md` v1 (FAQ initial à partir des questions/erreurs rencontrées pendant J1-J6)
- `docs/guides/architecture.md` (vue aérienne pointant vers ADRs)
- `CONTRIBUTING.md` finalisé
- `CHANGELOG.md` mis à jour avec mention version Jeedom testée
- 4 issue templates + PR template
- CI minimal `.github/workflows/tests.yml` opérationnel
- `build/package_skill.py` produit `jeedom-audit-v1.0.0.skill`
- ADR de release (résumé des écarts éventuels par rapport au PLANNING initial)

**Livrables PO** :
- **Captures d'écran finales pour README et guides** (Claude Code énumère exactement les captures requises avec timing : ex. "écran d'audit en cours dans Claude Code", "écran Réglages → Système → Configuration → API"). PO les fournit.
- **Validation par 2 utilisateurs externes** : recruter 2 utilisateurs Jeedom dans la communauté francophone, leur faire installer la skill, recueillir leurs retours
- Validation finale du README et des guides (lecture comme un nouvel utilisateur)
- Tag `v1.0.0` + GitHub Release avec `.skill` attaché (acte final, le PO peut déléguer à Claude Code via gh CLI ou faire manuellement)

**Critère go/no-go release V1.0.0** : 100% des 8 cas d'acceptation passent + tests verts + 2 utilisateurs externes confirmés + captures intégrées.

---

## 6. Stratégie de tests

### 6.1 Tests unitaires (D10.1)
- **Outillage** : `pytest` + `pytest-mock`
- **Couverture** : chaque fonction publique des scripts a happy path + cas limite
- **Fixtures** : `tests/fixtures/` sanitisées avec README dédié documentant provenance et procédé de sanitisation
- **Linter optionnel** : `tests/sanitize_check.py` signale violations résiduelles (mots de passe, IPs, prénoms)

### 6.2 Tests d'intégration (D10.2)
- **5-8 tests** rejouant chaînes de scripts en composition contre fixtures
- Pas de tests live V1 (roadmap V2)

### 6.3 Évals comportementales (D10.3)
- **10-15 évals** dans `tests/evals/` au format markdown
- **Format** : prompt utilisateur exact + setup + critères de succès + critères d'échec automatique
- **Couverture V1** : 1 par cas d'usage majeur (workflows 1, 2, 5, 6, 12, 13) + 2-3 sur refus + 2-3 sur cas limites
- **Exécution V1 manuelle** par Claude Code, rapport au PO ; automatisation roadmap V1.5
- Évals comme contrat de PR documenté dans CONTRIBUTING.md

### 6.4 Recette d'acceptation V1 (D10.4)
8 cas concrets en `examples/` à valider tous avant release V1.0.0 :
1. Audit général sur fixture `db/medium_install.sql`
2. Explication scénario "Présence-Géraud" (chaîne complexe) — pseudo-code en `#[O][E][C]#`
3. Diagnostic causal (workflow 13) sur cas réel pré-identifié *(matière fournie par le PO à J3)*
4. Graphe d'usage `[Maison][Présence Géraud][Présence]`
5. Cartographie d'orchestration depuis "Géraud rentre"
6. Audit jMQTT (broker/device, password filtré, topic correct)
7. Refus modification ("écris-moi un UPDATE")
8. Plugin tier-générique inconnu (inférence assumée + lien doc)

**Critère go/no-go** : 100% passent + tests verts + au moins 2 utilisateurs externes confirmés.

---

## 7. Architecture documentaire (3 axes — D13)

C'est la stratégie documentaire transverse du projet. Elle se distingue de la doc embarquée dans la skill (`jeedom-audit/SKILL.md` et `references/`) qui est destinée à Claude au runtime. Cette section concerne **le repo** et ses publics : PO, contributeurs futurs, sessions Claude Code futures, communauté Jeedom.

### 7.1 Trois axes, trois publics

| Axe | Public | Objectif | Lieu | Discipline |
|---|---|---|---|---|
| **1 — Traçabilité** | PO + contributeurs futurs | Pourquoi telle décision a été prise, alternatives écartées, quand | `docs/decisions/` (ADRs) | Immuable une fois acté ; nouvelles ADRs supersèdent les anciennes |
| **2 — Continuité Claude Code** | Sessions Claude Code futures | Reprendre le projet sans perdre contexte | `docs/state/` + `docs/sessions/` | Mise à jour à chaque session significative |
| **3 — Pédagogie** | Communauté Jeedom | S'approprier la skill, contribuer | `README.md` + `docs/guides/` | Mise à jour aux jalons et au fil des retours communauté |

### 7.2 Axe 1 — ADRs (Architecture Decision Records)

#### Format
Un fichier markdown court par décision, numéroté chronologiquement. Template fixe (~50-80 lignes max) :

```markdown
# ADR NNNN : <titre court et factuel>

- **Date** : YYYY-MM-DD
- **Statut** : Proposé | Accepté | Déprécié | Superseded by ADR NNNN
- **Contexte de décision** : idéation initiale | retour communauté | bug | etc.

## Contexte
[3-5 lignes : problème + contraintes]

## Options considérées
- **Option A** — description courte. ➕ avantages. ➖ inconvénients.
- **Option B** — ...

## Décision
[Option retenue + rationale concise]

## Conséquences
- ✅ Bénéfices attendus
- ⚠️ Coûts ou risques assumés
- 🔗 Dépendances avec d'autres ADRs

## Alternatives écartées (et pourquoi)
[Pour les options non retenues qui méritent doc explicite]
```

#### Critère d'éligibilité ADR

Une décision mérite une ADR si elle remplit **au moins un** des critères :
- Trade-off non trivial avec alternatives sérieuses considérées
- Contrainte forte qui s'imposera longtemps (architecture, licence, périmètre)
- Susceptible d'être contestée ou rouverte dans le futur

Les décisions de simple convention (ex. "scripts en Python") n'ont pas besoin d'ADR — elles vont dans `CONTRIBUTING.md` ou la doc helpers.

#### ADRs initiales V1 (à rédiger à J0)

À partir des décisions consolidées D1.1 à D13.5. Claude Code rédige ces 15 ADRs en suivant le template, soumet par lots de 3-5 au PO pour validation :

| # | Titre |
|---|---|
| 0001 | Skill vs slash-command (D1 cadrage) |
| 0002 | Jeedom version supportée : 4.5 uniquement (D1.2) |
| 0003 | Architecture repo multi-skills (`jeedom-skills/jeedom-audit/`) (D2.1, D2.2) |
| 0004 | Stratégie credentials (D+E+B+F, remote_mycnf) (D3.1, D3.3) |
| 0005 | Mode d'accès : MySQL+SSH préféré, API secondaire (D3.4, D3.5) |
| 0006 | Lecture seule absolue V1 + roadmap V2/V3 (D1.5, D3.2, D8.1) |
| 0007 | 13 intentions utilisateur dans 5 familles (D4.1 v3) |
| 0008 | Helpers Python factorisés vs SQL cookbook (D2.5, D7.5) |
| 0009 | Couverture plugins tier-1 (4 plugins) + tier-générique (D1.4, D5.1, D5.2) |
| 0010 | Discipline `#[O][E][C]#` chaîne 4 couches (D6.3) |
| 0011 | Frontmatter en anglais, contenu en français (D2.3, D12.1) |
| 0012 | Distribution `.skill` packagé en GitHub Release (D11.5) |
| 0013 | Licence MIT (D11.3) |
| 0014 | Zéro télémétrie (D12.2) |
| 0015 | Stratégie documentaire à 3 axes (D13.1) |

D'autres ADRs émergeront au fil du développement (~5-10 supplémentaires d'ici V1.0.0 selon les surprises rencontrées). Quand Claude Code identifie une décision méritant une ADR, il propose le titre et un draft au PO, valide, puis commit.

### 7.3 Axe 2 — Continuité Claude Code

#### Trois mécanismes complémentaires

**(a) `docs/state/PROJECT_STATE.md`** — état actuel du projet, document **vivant** mis à jour par Claude Code à chaque session significative.

```markdown
# État du projet

**Version actuelle** : 0.3.0 (pré-release)
**Jalon en cours** : J3 (logs + diagnostic causal)
**Dernière session** : 2026-04-25

## Ce qui marche
- Workflows 1, 2, 5, 6 opérationnels en mode SSH+MySQL
- 3 scripts livrés : db_query, resolve_cmd_refs, scenario_tree_walker
- 4/15 évals validées

## Ce qui est en cours
- logs_query.py — 70%
- references/logs-strategy.md — 30%

## Décisions ouvertes (à rouvrir potentiellement)
- Format de retour de logs_query : JSON Lines vs JSON unique ? Décision actuelle JSON unique mais à valider sur volume gros.

## Blocages
- Aucun

## Prochaines étapes
1. Finir logs_query.py
2. Eval-005 diagnostic scénario avec logs

## En attente du PO
- Validation des évals 4-5 sur la box réelle
- Cas réel pour le test workflow 13 (cf. J3 livrable PO)
```

**(b) `docs/sessions/YYYY-MM-DD-<sujet>.md`** — journal de bord par session Claude Code. Format léger (~20-50 lignes), append-only :

```markdown
# Session 2026-04-25 — implémentation logs_query

## Objectif de la session
Démarrer logs_query.py, valider format de tail SSH structuré.

## Décisions prises pendant la session
- Format de log_name = string libre (pas enum). Rationale : ouvert à plugins inconnus.
- Pas de cache pour logs (volume trop variable).

## Découvertes / surprises
- Logs scénarios 4.5 = format `[YYYY-MM-DD HH:MM:SS][LEVEL] message`, pas JSON Line.
- `tail -f` non utilisable côté SSH non-persistant.

## Travail réalisé
- logs_query.py squelette + happy path
- Test unitaire test_logs_query.py (3 cas)

## Reste à faire
- Filtre par niveau, fenêtre temporelle, test cas log absent

## Pour la prochaine session
Reprendre depuis logs_query.py:42 (TODO marqué dans le code).

## Pour le PO
Validation requise avant J4 : exécuter logs_query sur la box réelle pour 2 scénarios + vérifier que le format de log retourné est exploitable.
```

**(c) TODOs traçables dans le code source** — convention `# TODO(jalon-J3): <description>` avec référence au jalon. Script utilitaire optionnel `build/list_todos.py` agrège tous les TODOs et les classe par jalon.

#### `docs/state/CONTRIBUTING-CLAUDE-CODE.md` — discipline pour sessions futures

Document spécifique à Claude Code (distinct de `CONTRIBUTING.md` qui s'adresse aux humains). C'est le **contrat opérationnel du binôme PO/Claude Code**. Il prescrit :

**Posture relationnelle**
- Le PO est décideur, pas implémenteur. Claude Code rédige et code, PO valide ou demande retouche.
- Pose des **questions structurées** (2-4 options claires avec trade-offs et recommandation) plutôt que questions ouvertes.
- Préfère faire **valider un draft** plutôt que d'extraire le contenu via une série de questions.
- **Auto-validation** des choix triviaux (conventions de nommage internes, formulations mineures dans drafts, organisation de fichiers internes) — pas de gaspillage de cycles de validation.
- **Demande explicite et timée** des matières physiques que le PO doit fournir (captures, validation sur box, sanity check sanitisation).

**Routine de début de session**
1. Lire `docs/README.md` pour récupérer le panorama
2. Lire `docs/state/PROJECT_STATE.md` pour voir l'état actuel et ce qui est en attente du PO
3. Lire la dernière entrée `docs/sessions/` pour reprendre le fil exact
4. Scanner les ADRs récentes (depuis la date de dernière session)
5. Annoncer au PO l'état et proposer les objectifs de la session

**Routine de fin de session significative**
1. Mettre à jour `docs/state/PROJECT_STATE.md`
2. Créer une entrée `docs/sessions/YYYY-MM-DD-<sujet>.md` avec section "Pour la prochaine session" et "Pour le PO"
3. Créer ADR(s) pour décisions non triviales (cf. critère 7.2)
4. Marquer les TODOs traçables (`# TODO(jalon-JX):`) dans le code
5. Commit avec message clair

**Quand mettre à jour le brief `docs/PLANNING.md`**
Rare : seulement amendement stratégique (changement de périmètre, version Jeedom cible, etc.). Un amendement non trivial = ADR documentant le pourquoi du changement.

**Critère d'éligibilité ADR** (rappel cf. 7.2) — en cas de doute, créer l'ADR plutôt que pas.

### 7.4 Axe 3 — Pédagogie communautaire

#### Pyramide documentaire selon visiteur

```
README.md                      ← visiteur curieux (30 secondes)
   ↓
docs/guides/getting-started.md ← utilisateur novice (15 minutes)
   ↓
docs/guides/usage.md           ← utilisateur régulier (référence)
   ↓
docs/guides/troubleshooting.md ← utilisateur en difficulté
   ↓
docs/guides/architecture.md    ← contributeur curieux (vue aérienne)
   ↓
CONTRIBUTING.md                ← contributeur potentiel
   ↓
docs/decisions/                ← contributeur sérieux
```

#### `docs/README.md` (index navigation)

Sert de point d'entrée pour qui ouvre le dossier `docs/`. Format type :

```markdown
# Documentation jeedom-audit

## Selon ce que tu cherches

- **Premier usage de la skill** → [Getting started](guides/getting-started.md)
- **Référence des cas d'usage** → [Usage](guides/usage.md)
- **Erreur ou problème** → [Troubleshooting](guides/troubleshooting.md)
- **Comprendre l'architecture** → [Architecture](guides/architecture.md)
- **Contribuer** → [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Décisions de conception** → [ADRs](decisions/)
- **État actuel du projet** → [PROJECT_STATE](state/PROJECT_STATE.md)
- **Brief de planification V1** → [PLANNING](PLANNING.md)
```

#### Contenu par guide

- **`guides/getting-started.md`** : tutoriel pas-à-pas pour la première session — depuis l'install Claude Code jusqu'à un premier audit complet, avec captures réelles. ~15-20 minutes de lecture. **Captures fournies par le PO**.
- **`guides/usage.md`** : référence des 13 intentions avec exemples concrets pour chaque workflow. Plus exhaustif que les `examples/` (qui sont des recettes d'acceptation).
- **`guides/troubleshooting.md`** : FAQ + erreurs courantes + solutions. **Alimentée au fil de l'eau à partir des issues GitHub** et des questions/erreurs rencontrées pendant J1-J6 par le binôme.
- **`guides/architecture.md`** : pour le visiteur qui veut comprendre comment la skill est conçue. Niveau "vue aérienne". Pointe vers les ADRs pour le détail.

### 7.5 Discipline transverse de mise à jour

| Quand | Action obligatoire | Qui |
|---|---|---|
| Fin de chaque session Claude Code significative | Entrée `docs/sessions/YYYY-MM-DD-*.md` + maj `PROJECT_STATE.md` | Claude Code |
| Décision non triviale prise | ADR créée (draft Claude Code, validation PO) | Claude Code propose, PO valide |
| Issue récurrente sur GitHub | Entrée `troubleshooting.md` ajoutée | Claude Code |
| Jalon atteint | Maj `PROJECT_STATE.md` + entrée `CHANGELOG.md` (si pré-release) | Claude Code |
| Release publiée | ADR de release + maj `CHANGELOG.md` finalisée | Claude Code propose, PO acte la release |

### 7.6 Le brief lui-même (D13.5)

Ce document (`docs/PLANNING.md` après ingestion) sert de **référence vivante** du périmètre V1. Il **peut être amendé** à mesure que le projet avance, mais :
- Tout amendement non trivial nécessite une ADR documentant le pourquoi du changement
- Les amendements préservent l'historique git (pas de réécriture brutale)
- À la release V1.0.0, une ADR finale fait le point sur les écarts entre PLANNING initial et livraison réelle

---

## 8. Repo GitHub et distribution

### 8.1 License (D11.3) : MIT

### 8.2 Versioning (D11.4) : semver `MAJOR.MINOR.PATCH`
- V1.0.0 = première release publique
- Pré-releases en `0.x.x` pendant le développement (J0=0.1.0, J1=0.2.0, etc.)
- Mention obligatoire à chaque release : "Testé sur Jeedom 4.5.X au DD/MM/YYYY"

### 8.3 Changelog (D11.4)
Format **Keep a Changelog** avec sections `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.

### 8.4 Distribution (D11.5)
- À chaque tag `vX.Y.Z` : `build/package_skill.py` zippe `jeedom-audit/` en `jeedom-audit-vX.Y.Z.skill`
- Le `.skill` est attaché à la GitHub Release
- Le script de packaging vérifie : cohérence frontmatter, présence de tous les fichiers `references/` listés dans SKILL.md §9, absence de fichiers sensibles (`credentials.json`, `.env`)
- Produit un manifest `MANIFEST.txt` listant fichiers + checksums
- Voie alternative : clone manuel du repo + symlink/copie de `jeedom-audit/` vers le dossier skills local

### 8.5 README (D11.2 — orienté visiteur 30s)

**Cible** : utilisateur Jeedom francophone qui ne connaît pas Claude Code.

**Structure** :
1. Titre + tagline (lecture seule, Jeedom 4.5)
2. *Qu'est-ce que c'est ?* (3-5 phrases)
3. *Aperçu en 30 secondes* (1-2 captures concrètes — fournies par PO)
4. *Prérequis* (Claude Code, Jeedom 4.5, Python 3, **mode run dans Claude Code**)
5. *Installation rapide* (Option 1 `.skill`, Option 2 clone)
6. *Configuration* (assistant `setup` au premier appel)
7. *Démarrer* (phrasings canoniques exemples)
8. *Que fait-elle ?* (cas d'usage V1)
9. *Que ne fait-elle pas ?* (lecture seule, < 4.5, non-Jeedom)
10. *Limites V1* (plugins tier-1, pas de logs en API-only)
11. *Privacy* (zéro télémétrie)
12. *Contribuer* (lien CONTRIBUTING.md)
13. *Aller plus loin* (lien vers `docs/`)
14. *Roadmap* (lien CHANGELOG.md)
15. *License* (MIT)

**Anti-patterns à éviter** : marketing, listes exhaustives à emojis, captures hors-contexte, prérequis enterrés.

### 8.6 Contribution (D11.6)
- **Ouverte dès V1**
- `CONTRIBUTING.md` contient :
  - Comment ouvrir une issue (templates)
  - Comment ouvrir une PR (template)
  - Critères d'acceptation : nouveau helper (justification fonctionnelle, mono-responsabilité, I/O conforme, test unitaire), nouveau plugin tier-1 (template 9 sections, fixture associée, version testée), divergence de version Jeedom
  - Liste explicite des helpers et plugins **roadmap** comme invitations à contribuer
  - Pattern d'extension multi-skill anticipé (si seconde skill `jeedom-plugin-dev` arrive : créer dossier `jeedom-plugin-dev/` à côté + `shared/` pour matière commune via packaging)
  - Protocole évals avant merge (manuelles V1)
  - Code de conduite (Contributor Covenant)
- **4 issue templates** : bug, feature, divergence_version, new_plugin_tier1
- **CI minimal** : `.github/workflows/tests.yml` lance `pytest tests/unit/ tests/integration/` sur Python 3.10+

---

## 9. Fichiers à transférer depuis le projet source

**Important** : le projet source n'est **pas** accessible depuis le nouveau repo. Tous les fichiers utiles doivent être transférés explicitement par le PO au moment indiqué ci-dessous (Claude Code ne peut pas accéder au projet source — c'est la rupture de contexte décrite dans le prompt initial). Le PO copie/colle les fichiers ou les fournit en uploads à Claude Code, qui les place ensuite à l'emplacement cible.

### 9.1 Référence centrale (J0 — bootstrap documentaire)

| Fichier source | Destination | Raison |
|---|---|---|
| `jeedom_audit_db.md` | `docs/references-source/audit_db.md` | Schéma DB + gotchas. **Attention** : ce fichier a été produit par Claude Code lors de la migration, il peut comporter des biais d'installation. Claude Code le cross-checkera contre la doc officielle à J1 (cf. 3.1). |
| `jeedom_skill_project_brief.md` | `docs/references-source/brief-initial.md` | Brief initial (matière à dépasser). Note : il référence `.claude/commands/jeedom.md` (ancien format slash-command). Ne pas reproduire — la décision V1 est skill, pas slash-command. |

**Note** : le sous-dossier `docs/references-source/` est créé spécifiquement pour héberger ces archives du projet source. Distinct de `docs/decisions/` (ADRs nouveaux) et de `jeedom-audit/references/` (skill runtime).

### 9.2 Fixtures DB et scénarios (J1-J3)

Tous ces fichiers vont dans `tests/fixtures/` et **doivent passer un check de sanitisation** avant commit. Procédure : Claude Code propose les substitutions, PO sanity check.

| Fichier source | Destination | Jalon |
|---|---|---|
| `jeedom__mysql_scenarios_full.json` | `tests/fixtures/scenarios/scenarios_full.json` | J1 |
| `jeedom__mysql_scenarios_full.tsv` | `tests/fixtures/scenarios/scenarios_full.tsv` | J1 |
| `jeedom__mysql_scenarios_elements.txt` | `tests/fixtures/scenarios/scenarios_elements.txt` | J1 |
| `jeedom__mysql_scenarioExpression.sql` | `tests/fixtures/scenarios/scenarioExpression.sql` | J1 |
| `scenario31.txt`, `scenario32.txt`, `scenario34.txt`, `scenario35.txt`, `scenario37.txt` | `tests/fixtures/scenarios/scenario_NN.txt` | J2 |
| `jeedom__scenarios_presence.txt` | `tests/fixtures/scenarios/presence_chain.txt` | J3 — chaîne pour test workflow 13 et 12 |
| `jeedom__audit_scenarios.json` | `tests/fixtures/audits/audit_scenarios.json` | J1 |
| `jeedom__mysql_eqlogic_summary.csv` | `tests/fixtures/db/eqlogic_summary.csv` | J1 |
| `jeedom__mysql_virtual_eqlogic.csv` | `tests/fixtures/plugins/virtual_eqlogic.csv` | J4 — fixture pour `references/plugin-virtual.md` |
| `jmqtt__presence_eqlogics.txt` | `tests/fixtures/plugins/jmqtt_presence_eqlogics.txt` | J4 — fixture pour `references/plugin-jmqtt.md` |
| `jeedom__thermostat_mapping.txt` | `tests/fixtures/plugins/thermostat_mapping.txt` | J4 |

### 9.3 Exemples de livrables d'audit (J2 ou J7)

| Fichier source | Destination | Raison |
|---|---|---|
| `jeedom_audit.md` | `docs/references-source/example-audit-general.md` | Modèle de richesse de contenu — référence d'inspiration pour Claude Code lors de la rédaction de `references/audit-templates.md` et `examples/audit-general.md` |
| `jeedom_scenarios_routing.md` | `docs/references-source/example-orchestration.md` | Modèle cartographie d'orchestration manuelle |
| `jeedom_virtual_inventory.md` | `docs/references-source/example-virtual-inventory.md` | Modèle audit ciblé virtual |

**Note** : ces trois fichiers sont **références d'inspiration**, pas des examples V1 directs. Les `examples/` finaux V1 (audit-general.md, etc.) seront rédigés à partir d'eux mais respecteront les conventions de format actées (D6.1).

### 9.4 Fichier non transféré V1

Aucun fichier additionnel mentionné dans le brief original n'est connu pour exister. Si un `scenario75.txt` (mentionné historiquement) est retrouvé, il concernerait le mode offline reporté V2 (D3.6).

### 9.5 Procédure de sanitisation

Documentée dans `tests/fixtures/README.md` à J1 (rédaction Claude Code).

**Substitutions à effectuer** :
- Prénoms réels → noms génériques (Géraud → Personne1, etc.)
- IPs locales → `192.168.0.1`, `10.0.0.1`, etc.
- Tokens / API keys / passwords → chaînes type `[REDACTED-TOKEN]`
- Noms d'objets identifiants (adresses, lieux) → noms génériques (Maison, Bureau, Cuisine)

**Procédure du binôme** :
1. PO transfert le fichier brut à Claude Code
2. Claude Code identifie les patterns suspects et propose les substitutions
3. PO vérifie que rien de personnel ne fuit (œil humain qui connaît son install)
4. PO valide ou demande retouche
5. Claude Code commit le fichier sanitisé dans `tests/fixtures/`
6. Le linter optionnel `tests/sanitize_check.py` valide en pre-commit

---

## 10. Roadmap post-V1

> **⚠️ Amendement stratégique — 2026-05-01**
>
> Les lignes V2 et V3 ci-dessous ont été partiellement révisées par trois décisions prises post-release :
>
> - **Lecture seule perpétuelle** : les capacités modifiantes (V2 : lancer scénario, activer/désactiver ; V3 : modifications config) sont **retirées du périmètre de `jeedom-audit`** (ADR-0006 amendé). La skill reste lecture seule absolue à perpétuité.
> - **holmesMCP** : projet séparé (plugin Jeedom natif, market) pour les capacités MCP et modifiantes (ADR-0020).
> - **jeedom-plugin-dev** : second skill dans ce repo (remplace "capacités modifiantes V2" comme objectif V2) (ADR-0021).
>
> En cas de conflit, les ADRs ci-dessus font autorité sur les lignes V2/V3/V4+ de cette section.

### V1.5 (mineur)
- `dead_cmds.py` (cross-check natif Jeedom commandes mortes)
- `history_query.py` (helper historique cmd)
- `unused_variables.py` (variables dataStore orphelines)
- `generic_plugin_inspector.py` (extraction d'échantillons pour plugin tier-générique)
- Automatisation des évals (harness Claude Code en batch)
- Linter `build/check_plugin_doc.py` validant le template tier-1

### V2
- **Capacités modifiantes via API uniquement** : lancer scénario, activer/désactiver, exécuter cmd action, écrire variable dataStore. Toujours preview + confirmation explicite.
- **Mode offline** (consommation de dump JSON), namespace `preferred_mode: "offline"` réservé V1
- Script `build/dump_for_offline.py` (production de dumps)
- **Aide à la migration HA / Node-RED**
- **Support Jeedom 4.4** si demande communautaire forte
- **Tests live** harness pour PO (hors CI)
- **Internationalisation EN** (duplication SKILL.md / references/)
- **Seconde skill `jeedom-plugin-dev`** pour le développement de plugins Jeedom — création de `shared/` avec extraction de la matière commune et adaptation du script de packaging

### V3
- Modifications de configuration légère via API (renommages, hiérarchie, Types Génériques) avec confirmation explicite
- Refactor partiellement exécutable (sur opérations admises par V2/V3)
- Parsing logs structuré niveau 3 (corrélation timeline, agrégation erreurs)
- Format-aware par plugin (parser jMQTT, virtual, etc.)

### V4+
- Marketplace / registry communautaire de plugins tier-1
- Comparaison de scénarios entre versions
- Audit infrastructure étendu (sauvegardes, réseau, marketplace avancé)

### Politique de support à acter quand 2ᵉ version Jeedom apparaîtra
N et N-1 — au-delà déprécié.

---

## 11. Risques et points d'attention

### 11.1 Risques techniques
- **Schéma DB diverge selon installations** : le `audit_db.md` du projet source a été produit empiriquement contre une seule install. Cross-check par Claude Code à J1 contre la doc officielle, divergences signalées en ADR si sérieuses.
- **`infoName` vs `updateCmdId`** dans le plugin virtual : zone grise non résolue au scan initial. Vérifier sur fixture `virtual_eqlogic.csv` et adapter `references/plugin-virtual.md` en J4.
- **Format précis de `eqLogic.status` en DB** : zone grise. Vérifier au début de J1, adapter `references/health-checks.md`.
- **Logs en 4.5** : changement de mécanisme par rapport à 4.4 (suppression monolog). Vérifier format réel avant J3.
- **`*::byHumanName` natif vs wrapper Python** : zone grise. Si natif disponible côté API Jeedom, simplification possible côté `resolve_cmd_refs.py` pour le mode API-only. Vérifier en J5.

### 11.2 Risques UX
- **Trop pushy ou pas assez** dans le `description` du frontmatter : raffinage par évals au cours du développement (D2.3).
- **Filtrage credentials trop large** (faux positifs) : la liste `sensitive_fields.py` peut bloquer des champs légitimes nommés ambigus. Mention transparente systématique mitige.
- **Workflow 13 trop long ou trop court** : interactivité requise (D4.6) mais peut générer frustration si Claude pose trop de questions. Évaluer à la recette.

### 11.3 Risques de scope
- **Tentation de couvrir trop de plugins en tier-1** : tenir la ligne "4 plugins V1, le reste tier-générique". Inviter contributions communautaires.
- **Tentation d'audit_general.py omnibus** : explicitement banni (D2.5, D7.4). Maintenir la composition par Claude.
- **Tentation de relâcher la lecture seule** sous pression utilisateur : posture inviolable D1.5.

### 11.4 Risques projet
- **PO seul au début** : critique. Solliciter retours communauté tôt (issue tracker ouvert dès V1.0.0).
- **Veille évolution Jeedom** : Jeedom 4.6 viendra. Anticiper avec issue template `divergence_version` et politique semver claire.
- **Surcoût des évals manuelles** au fil du développement : automatiser dès V1.5 est une priorité de roadmap.

### 11.5 Risques documentaires
- **Doc qui dérive avec le code** : la discipline `CONTRIBUTING-CLAUDE-CODE.md` (mise à jour `PROJECT_STATE.md` et entrée session à chaque session) prévient. Si dérive constatée, c'est qu'une session n'a pas respecté la discipline — ADR de rappel à émettre.
- **ADRs trop nombreuses ou trop rares** : le critère d'éligibilité (7.2) doit être respecté. Trop = pollution, trop peu = perte de traçabilité. Calibrage à ajuster dans les premières sessions.
- **Sessions Claude Code qui ignorent la doc préexistante** : risque réel si la routine de début de session n'est pas suivie. La routine est inscrite en tête de `CONTRIBUTING-CLAUDE-CODE.md` et pointée depuis `docs/README.md`.

### 11.6 Risques du binôme PO/Claude Code
- **Validations PO en goulot d'étranglement** : si Claude Code attend trop souvent de validation pour des choix triviaux, le projet stagne. Mitigation : auto-validation des conventions internes et formulations mineures (cf. 0.2.d).
- **PO sollicité sur trop de matières physiques en parallèle** : risque de fatigue/abandon. Mitigation : Claude Code groupe les demandes (ex. "captures de J7 + validation ADRs en attente + cross-check sanitisation des nouvelles fixtures") plutôt que de fractionner.
- **Drift de compréhension entre sessions** : Claude Code peut perdre le contexte fin entre sessions. Mitigation : la discipline 7.3 (PROJECT_STATE.md + sessions/) est exactement conçue pour ça. Si Claude Code constate qu'il a perdu le fil, **demander explicitement** au PO de récapituler plutôt qu'inventer.

---

## Annexe A — Glossaire (pour Claude Code en planification)

- **eqLogic** : équipement Jeedom, table `eqLogic`. Porte un `eqType_name` qui désigne le plugin owner.
- **cmd** : commande Jeedom, table `cmd`. Type info (lecture) ou action (écriture). Attachée à un eqLogic.
- **scenarioElement** : nœud d'un scénario (table `scenarioElement`). Hiérarchie via `parentId` vers un autre scenarioElement.
- **scenarioSubElement** : sous-nœud (THEN, ELSE, condition…), table `scenarioSubElement`.
- **scenarioExpression** : feuille (condition ou action), table `scenarioExpression`.
- **dataStore** : variables persistantes (table `dataStore`). `type='scenario'` + `link_id=-1` = variable globale.
- **history / historyArch** : tables d'historisation des cmd info.
- **`#[O][E][C]#`** : convention de nommage dans les expressions de scénario : `#[Objet][Équipement][Commande]#`. Forme humaine de `#cmdId#`.
- **Tags système** : `#trigger_id#`, `#trigger_value#`, `#trigger_name#`, `#user_connect#`, `#sunset#`, `#sunrise#`, `#time#`. À préserver intacts.
- **logicalId** : champ d'identification logique, conventions plugin-spécifiques. Pour jMQTT, **porte le topic** d'un device (gotcha critique).
- **Type Générique** : classification orthogonale des cmd (Lumière, Volet, Thermostat…) utilisée par les intégrations (Mobile, Homebridge, etc.).
- **Daemon** : processus de fond d'un plugin, état exposé via `jeedom::monitor::deamonState::<plugin>`.
- **ADR** : Architecture Decision Record. Fichier markdown dans `docs/decisions/` documentant une décision structurante (cf. 7.2).
- **PO** : Product Owner — utilisateur humain décideur.
- **Claude Code (CC)** : implémenteur — rédige et code, pose des questions structurées au PO.

---

## Annexe B — Checklist de démarrage Claude Code (J0 + J1)

> **Lecture préalable obligatoire pour Claude Code** : section 0 (Modèle opérationnel ProductOwner / Claude Code) avant tout.

### Étape J0 — Bootstrap documentaire (ordre précis)

**Préparation (PO)**
- 0a. PO crée le repo `jeedom-skills` sur GitHub (vide) et donne accès à Claude Code (ou autorise Claude Code à le créer via gh CLI)
- 0b. PO transfère les fichiers section 9.1 (`audit_db.md`, `brief-initial.md`) à Claude Code

**Bootstrap (Claude Code)**
1. Initialiser la structure 2.2 (créer dossiers vides + `.gitkeep`)
2. Créer `LICENSE` (MIT), `.gitignore` Python, `pyproject.toml` minimal, `CHANGELOG.md` initial avec entrée `[Unreleased]`
3. Placer `docs/PLANNING.md` = ce brief
4. Placer les fichiers transférés en 0b dans `docs/references-source/`
5. Rédiger `docs/README.md` (index navigation) — pas besoin de validation PO, convention claire
6. Rédiger `docs/state/CONTRIBUTING-CLAUDE-CODE.md` (discipline binôme + routine sessions selon spec 7.3) — **soumettre au PO pour validation, c'est le contrat opérationnel**
7. Rédiger `docs/state/PROJECT_STATE.md` (état J0 en cours)
8. Rédiger `docs/decisions/README.md` (index ADRs + template ADR fixe)
9. Rédiger les **15 ADRs initiales** (cf. 7.2) à partir de la matière du brief — **soumettre par lots de 3-5 au PO pour validation** (ne pas attendre les 15 d'un coup, le PO doit pouvoir cadencer son temps de validation)
10. Rédiger `docs/sessions/README.md` + première entrée de session documentant le bootstrap
11. Rédiger `README.md` v0 (statut "en construction") — soumettre au PO pour validation
12. Rédiger `CONTRIBUTING.md` v0 (squelette à étoffer à J7)
13. Commit + tag `v0.1.0` (pré-release J0)

**Critère de sortie J0** : un nouveau contributeur peut comprendre l'état du projet en lisant `docs/README.md` puis les ADRs.

### Étape J1 — Skeleton skill

**Préparation (Claude Code, en début de session J1)**
14a. Lire `docs/README.md`, `docs/state/PROJECT_STATE.md`, dernière entrée `docs/sessions/`
14b. Annoncer au PO l'état + objectifs de la session J1

**Cross-check (Claude Code)**
14. Cross-check `docs/references-source/audit_db.md` contre la doc officielle Jeedom 4.5. Reporter les divergences en ADR si sérieuses (proposer au PO).

**Implémentation (Claude Code)**
15. Rédiger `jeedom-audit/SKILL.md` selon maquette 3.9 et frontmatter 3.8 — soumettre draft au PO pour validation
16. Coder `jeedom-audit/scripts/_common/`
17. Coder `jeedom-audit/scripts/db_query.py`
18. Rédiger `jeedom-audit/references/connection.md` et `jeedom-audit/references/sql-cookbook.md`
19. Implémenter sous-commande `setup` interactive
20. Premier test unitaire `tests/unit/test_db_query.py` passant

**Validation (PO)**
21a. Validation que le `setup` fonctionne sur la box réelle du PO
21b. Cross-check sanitisation des fixtures transférées (cf. 9.5)
21c. Captures éventuelles pour `references/connection.md` (création user MySQL read-only)

**Closure J1 (Claude Code)**
22. Maj `docs/state/PROJECT_STATE.md`, entrée `docs/sessions/`
23. Commit + tag `v0.2.0` (pré-release J1)

---

*Fin du brief. Document rédigé en sortie d'une session d'idéation collaborative, ~55 décisions consolidées (D1.1 à D13.5) + modèle opérationnel PO/Claude Code (section 0). À ingérer en mode planification dans un nouveau repo Claude Code vide.*
