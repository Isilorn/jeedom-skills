# ADRs — Architecture Decision Records

Index des décisions structurantes du projet `jeedom-audit`.

## Format de chaque ADR

Fichier : `NNNN-<titre-court-kebab>.md` — numéroté chronologiquement.

```markdown
# ADR NNNN : <titre court et factuel>

- **Date** : YYYY-MM-DD
- **Statut** : Proposé | Accepté | Déprécié | Superseded by ADR NNNN
- **Contexte de décision** : idéation initiale | retour communauté | bug | session de dev

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

## Critère d'éligibilité

Une décision mérite une ADR si elle remplit **au moins un** des critères :

- Trade-off non trivial avec alternatives sérieuses considérées
- Contrainte forte qui s'imposera longtemps (architecture, licence, périmètre)
- Susceptible d'être contestée ou rouverte dans le futur

**En cas de doute : créer l'ADR.** Trop > trop peu.

**Ne méritent PAS d'ADR** : conventions de nommage internes, choix de variables, formulations de texte.

## Index

### Lot a — Décisions structurelles (J0)

| # | Titre | Statut | Date |
| --- | --- | --- | --- |
| [0001](0001-skill-vs-slash-command.md) | Skill vs slash-command | Accepté | 2026-04-27 |
| [0002](0002-jeedom-version-supportee.md) | Jeedom 4.5 uniquement en V1 | Accepté | 2026-04-27 |
| [0003](0003-architecture-repo-multi-skills.md) | Architecture repo multi-skills | Accepté | 2026-04-27 |
| [0004](0004-credentials-strategy.md) | Stratégie credentials (remote_mycnf) | Accepté | 2026-04-27 |
| [0005](0005-mode-acces-mysql-vs-api.md) | Mode d'accès MySQL+SSH préféré, API secondaire | Accepté | 2026-04-27 |

### Lot b — Posture et UX (J0)

| # | Titre | Statut | Date |
| --- | --- | --- | --- |
| [0006](0006-lecture-seule-absolue.md) | Lecture seule absolue V1 + roadmap V2/V3 | Accepté | 2026-04-27 |
| [0007](0007-13-intentions-5-familles.md) | 13 intentions utilisateur dans 5 familles | Accepté | 2026-04-27 |
| [0008](0008-helpers-python-vs-sql-cookbook.md) | Helpers Python factorisés vs SQL cookbook | Accepté | 2026-04-27 |
| [0009](0009-couverture-plugins-tier-1.md) | Couverture plugins : tier-1 (4) + tier-générique | Accepté | 2026-04-27 |
| [0010](0010-discipline-naming-OEC.md) | Discipline `#[O][E][C]#` — chaîne 4 couches | Accepté | 2026-04-27 |

### Lot c — Documentation et distribution (J0)

| # | Titre | Statut | Date |
| --- | --- | --- | --- |
| [0011](0011-frontmatter-en-anglais.md) | Frontmatter en anglais, contenu en français | Accepté | 2026-04-27 |
| [0012](0012-distribution-skill-package.md) | Distribution `.skill` packagé en GitHub Release | Accepté | 2026-04-27 |
| [0013](0013-licence-mit.md) | Licence MIT | Accepté | 2026-04-27 |
| [0014](0014-zero-telemetrie.md) | Télémétrie opt-in (compteurs agrégés uniquement) | Accepté | 2026-04-27 |
| [0015](0015-strategie-documentaire.md) | Stratégie documentaire à 3 axes | Accepté | 2026-04-27 |

### Clarifications en session (J0)

| # | Titre | Statut | Date |
| --- | --- | --- | --- |
| [0016](0016-tests-via-ssh-par-claude-code.md) | Tests sur box réelle exécutés par Claude Code via SSH | Accepté | 2026-04-27 |

---

*D'autres ADRs émergeront au fil du développement (~5-10 supplémentaires d'ici V1.0.0).*
*Spécifié en PLANNING §7.2.*
