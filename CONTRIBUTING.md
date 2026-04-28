# Contribuer à jeedom-audit

Les contributions sont ouvertes depuis V1.0.0. Merci de lire ce guide avant d'ouvrir une issue ou une PR.

---

## Ouvrir une issue

Utilisez les templates GitHub disponibles :

- **[Bug](https://github.com/Isilorn/jeedom-skills/issues/new?template=bug.yml)** — comportement inattendu de la skill
- **[Feature](https://github.com/Isilorn/jeedom-skills/issues/new?template=feature.yml)** — suggestion de fonctionnalité ou nouveau workflow
- **[Divergence de version](https://github.com/Isilorn/jeedom-skills/issues/new?template=version-divergence.yml)** — comportement différent sur une version Jeedom spécifique
- **[Nouveau plugin tier-1](https://github.com/Isilorn/jeedom-skills/issues/new?template=nouveau-plugin-tier1.yml)** — proposition de couverture documentaire complète d'un plugin

---

## Ouvrir une Pull Request

### Avant de commencer

1. Ouvrez une issue pour discuter de la proposition
2. Lisez [docs/guides/architecture.md](docs/guides/architecture.md) pour comprendre la structure
3. Vérifiez les [ADRs](docs/decisions/) pour les décisions de conception déjà actées

### Critères d'acceptation selon le type de PR

#### Nouveau helper Python

- Mono-responsabilité : un script = une opération
- I/O JSON conforme : lit via SSH/API, retourne JSON structuré
- Test unitaire associé (happy path + au moins 2 cas limites)
- Aucun INSERT/UPDATE/DELETE — lecture seule absolue
- Données sensibles filtrées via `_common/tags.py`

#### Nouveau plugin tier-1

- Fiche `references/plugin-<nom>.md` en 9 sections (voir template dans [PLANNING §3.7](docs/PLANNING.md))
- Fixture sanitisée dans `tests/fixtures/plugins/`
- Version Jeedom testée mentionnée
- Tests unitaires si nouveau code Python associé

#### Modification de SKILL.md ou references/

- Passer les évals comportementales concernées (`tests/evals/`)
- Documenter le résultat dans le tableau "Résultats" de l'éval

#### Divergence de version Jeedom

- Version exacte documentée (ex. Jeedom 4.4.8 + MariaDB 10.5)
- Preuve de test fournie (log, capture ou extrait de réponse)
- Ne pas casser le comportement sur Jeedom 4.5.x de référence

### Checklist PR

Avant de soumettre, vérifiez le [template PR](.github/PULL_REQUEST_TEMPLATE.md) :

- [ ] `pytest tests/unit/ -v` — 100 % passants
- [ ] Aucune donnée sensible dans les fixtures (`python tests/sanitize_check.py`)
- [ ] SKILL.md mis à jour si comportement ou périmètre modifié
- [ ] Évals concernées relues et validées

---

## Conventions de code

- Python 3.10+ — pas de dépendances au-delà de `mysql-connector-python` et `requests`
- Chaque script lit via SSH, retourne JSON sur stdout, erreurs sur stderr avec code de sortie non nul
- Pas de credentials en dur — utiliser `_common/credentials.py`
- Pas de commentaires explicatifs inutiles — le code se lit seul

---

## Sanitisation des fixtures

Toute fixture dans `tests/fixtures/` doit être sanitisée :

- Noms réels → noms génériques (`Salon`, `Cuisine`, etc.)
- IPs réelles → `192.168.1.X`
- Prénoms réels → prénoms génériques (`Alice`, `Bob`)
- Mots de passe → `REDACTED`

Vérification : `python tests/sanitize_check.py tests/fixtures/`

---

## Pattern d'extension multi-skill

Si une seconde skill `jeedom-plugin-dev` est créée à terme :

- Nouveau dossier `jeedom-plugin-dev/` à côté de `jeedom-audit/`
- Matière commune via `shared/` si besoin (décision à prendre par ADR)
- Ne pas modifier `jeedom-audit/` pour des besoins spécifiques à l'autre skill

---

## Roadmap ouverte aux contributions

Ces extensions sont documentées mais hors périmètre V1 — contributions bienvenues :

- Support Jeedom 4.4 (divergences de schéma à documenter)
- Plugins tier-1 supplémentaires (Zigbee2MQTT natif, Philips Hue, Z-Wave JS...)
- Tests d'intégration automatisés contre fixture DB complète
- Automatisation des évals comportementales

---

## Code de conduite

Ce projet respecte le [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

---

*Architecture et décisions de conception → [`docs/guides/architecture.md`](docs/guides/architecture.md) et [`docs/decisions/`](docs/decisions/)*
