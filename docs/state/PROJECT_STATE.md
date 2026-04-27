# État du projet jeedom-audit

**Version actuelle** : 0.2.0 (pré-release J1)
**Jalon en cours** : J1 terminé — J2 à démarrer
**Dernière session** : 2026-04-27

---

## Ce qui marche

- Infrastructure documentaire J0 complète (ADRs 0001-0016, arborescence, fichiers racine)
- `jeedom-audit/SKILL.md` rédigé (250 lignes, 11 sections, corrigé cross-check)
- `scripts/_common/` : `credentials.py`, `ssh.py`, `tags.py`, `sensitive_fields.py`, `version_check.py`
- `scripts/db_query.py` opérationnel — testé sur box réelle (217 eqLogics, 62 scénarios, 6219 commandes)
- `scripts/setup.py` interactif fonctionnel
- `references/connection.md` rédigé
- `tests/unit/test_db_query.py` — 18/18 passants
- Credentials configurés : user RO `jeedom_audit_ro`, `~/.my.cnf` box, `credentials.json` local (perm 600)
- API Jeedom accessible (`ping` → `pong`)

## Ce qui est en cours / en attente

Aucun — J1 fermé proprement.

## Décisions ouvertes

Aucune décision ouverte.

## Blocages

Aucun blocage technique.

## Prochaines étapes

**J2 — Workflows DB-only + helpers cœur**

Démarrer par la routine de début de session (`docs/state/CONTRIBUTING-CLAUDE-CODE.md §3`), puis :

1. Rédiger `references/sql-cookbook.md` — requêtes par famille (audit, scénarios, équipements, commandes, dataStore, historique). Reporter les corrections cross-check : `trigger` backtické, `lastLaunch`/`state` via API, topic jMQTT dans `configuration.topic`.
2. Coder `scripts/resolve_cmd_refs.py` — résolution `#ID#` → `#[O][E][C]#` en batch (3 requêtes SQL groupées + cache de session + tags système préservés)
3. Coder `scripts/scenario_tree_walker.py` — parcours récursif (anti-cycle, max_depth=3, >100 sous-éléments tronqués)
4. Rédiger `references/scenario-grammar.md` — interprétation `scenarioExpression` (types, subtypes, options)
5. Implémenter WF5 (explication scénario) — première validation end-to-end sur box réelle
6. Rédiger `references/audit-templates.md` + `references/health-checks.md`
7. Implémenter WF1 (audit général) — validation sur box réelle

**Critère de sortie J2** : WF1 (audit général) + WF5 (explication scénario) validés manuellement sur box réelle du PO.

## En attente du PO

- **À J2** : Validation manuelle WF1 et WF5 sur box réelle (Claude Code exécute, PO valide les résultats)

---

*Document vivant — mis à jour par Claude Code à chaque session significative.*
*Format spécifié en PLANNING §7.3.a.*
