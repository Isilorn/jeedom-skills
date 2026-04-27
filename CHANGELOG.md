# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Note: Each release mentions the Jeedom version tested at the time of publication.

---

## [Unreleased]

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
