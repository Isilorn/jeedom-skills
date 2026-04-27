# Contribuer à jeedom-audit

> **Statut pré-V1** : les contributions de code seront ouvertes à V1.0.0 (jalon J7).
> En attendant, les retours d'expérience et les rapports de bugs sont les bienvenus via les [issues GitHub](https://github.com/Isilorn/jeedom-skills/issues).

---

## Comment ouvrir une issue

Utilise les templates disponibles (à créer à J7) :
- **Bug** : comportement inattendu de la skill
- **Feature** : suggestion de fonctionnalité
- **Divergence de version** : comportement différent sur une version Jeedom spécifique
- **Nouveau plugin tier-1** : proposition de couverture documentaire d'un nouveau plugin

## Comment ouvrir une Pull Request

*(Section à étoffer à J7 — jalons J0 à J6 : développement en binôme PO/Claude Code)*

Les critères d'acceptation d'une PR incluront :
- **Nouveau helper Python** : justification fonctionnelle, mono-responsabilité, I/O JSON conforme (spec PLANNING §3.12), test unitaire associé
- **Nouveau plugin tier-1** : template 9 sections (spec PLANNING §3.7), fixture associée sanitisée, version testée mentionnée
- **Divergence de version Jeedom** : preuve de test, version exacte documentée
- **Évals** : toute PR touchant SKILL.md ou references/ doit passer les évals manuelles concernées

## Code de conduite

Ce projet respecte le [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

---

*Pour plus de détails sur l'architecture et les décisions de conception, voir [`docs/decisions/`](docs/decisions/) (ADRs) et [`docs/guides/architecture.md`](docs/guides/architecture.md) (disponible à J7).*
