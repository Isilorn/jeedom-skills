# État du projet jeedom-audit

**Version actuelle** : 0.1.0 (pré-release J0)
**Jalon en cours** : J0 terminé — en attente push/tag
**Dernière session** : 2026-04-27

---

## Ce qui marche

- Infrastructure documentaire posée (arborescence 2.2 complète)
- `docs/PLANNING.md` ingéré (brief ~1350 lignes, ~55 décisions)
- Fichiers racine créés : LICENSE, .gitignore, pyproject.toml, CHANGELOG.md, README.md v0, CONTRIBUTING.md v0
- Archives source transférées dans `docs/references-source/` (brief-initial.md, audit_db.md sanitisé)
- Documentation Claude Code (axe 2) : PROJECT_STATE, CONTRIBUTING-CLAUDE-CODE, sessions/README, entrée session J0
- Documentation traçabilité (axe 1) : 15 ADRs initiales rédigées (statut Proposé)
- Index navigation `docs/README.md`

## Ce qui est en cours / en attente

| Quoi | Statut |
| --- | --- |
| Commit initial + push + tag v0.1.0 | ⏳ Confirmation PO requise avant push/tag |

## Décisions ouvertes

Aucune décision ouverte à J0 — toutes les décisions sont couvertes par les 15 ADRs initiales ou auto-validées (conventions triviales).

## Blocages

Aucun blocage technique. En attente validations PO listées ci-dessus.

## Prochaines étapes

**J0 (fin)** :

1. Commit initial + push + tag v0.1.0 (confirmation PO reçue)

**J1 (prochaine session)** :

1. Lire `docs/README.md`, `docs/state/PROJECT_STATE.md`, dernière entrée `docs/sessions/`
2. Annoncer au PO l'état + objectifs de la session J1
3. Cross-check `docs/references-source/audit_db.md` contre la doc officielle Jeedom 4.5 (divergences → ADR si sérieuses)
4. Rédiger `jeedom-audit/SKILL.md` selon maquette PLANNING §3.9 + frontmatter §3.8
5. Coder `jeedom-audit/scripts/_common/` (credentials, ssh, tags, sensitive_fields, version_check)
6. Coder `jeedom-audit/scripts/db_query.py`
7. Rédiger `jeedom-audit/references/connection.md` et `sql-cookbook.md`
8. Implémenter sous-commande `setup` interactive

## En attente du PO

- **À J0** : Confirmation push + tag `v0.1.0`
- **À J1** : Tests SSH sur box réelle (setup + db_query) | Sanity check fixtures sanitisées | Éventuelles captures pour `connection.md`

---

*Document vivant — mis à jour par Claude Code à chaque session significative.*
*Format spécifié en PLANNING §7.3.a.*
