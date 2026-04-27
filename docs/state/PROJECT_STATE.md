# État du projet jeedom-audit

**Version actuelle** : 0.3.0 (pré-release J2)
**Jalon en cours** : J2 terminé — J3 à démarrer
**Dernière session** : 2026-04-27

---

## Ce qui marche

- Infrastructure documentaire J0 complète (ADRs 0001-0016, arborescence, fichiers racine)
- `jeedom-audit/SKILL.md` rédigé (250 lignes, 11 sections, corrigé cross-check)
- `scripts/_common/` : `credentials.py`, `ssh.py`, `tags.py`, `sensitive_fields.py`, `version_check.py`
- `scripts/db_query.py` opérationnel — testé sur box réelle (217 eqLogics, 62 scénarios, 6219 commandes)
- `scripts/setup.py` interactif fonctionnel
- `scripts/resolve_cmd_refs.py` — résolution batch #ID# → #[O][E][C]# avec cache de session (17/17 tests)
- `scripts/scenario_tree_walker.py` — parcours récursif anti-cycle, max_depth, troncature >100 (16/16 tests)
- `references/connection.md` rédigé
- `references/sql-cookbook.md` rédigé (10 familles, ~200 lignes)
- `references/scenario-grammar.md` rédigé (types/subtypes/options, pseudo-code WF5)
- `references/audit-templates.md` rédigé (12 sections fixes WF1)
- `references/health-checks.md` rédigé (seuils ✅/⚠️/❌)
- `tests/unit/` : 51/51 passants (db_query + resolve_cmd_refs + scenario_tree_walker)
- WF5 validé end-to-end sur box réelle (scénario 70 "Présence Géraud Shelly")
- WF1 validé end-to-end sur box réelle (Jeedom 4.5.3, 177 eqLogics actifs, 57 scénarios actifs)
- Credentials configurés : user RO `jeedom_audit_ro`, `~/.my.cnf` box, `credentials.json` local (perm 600)

## Ce qui est en cours / en attente

Aucun — J2 fermé proprement.

## Décisions ouvertes

Aucune décision ouverte.

## Blocages

Aucun blocage technique.

## Prochaines étapes

**J3 — Scripts complémentaires + plugins tier-1**

Démarrer par la routine de début de session (`docs/state/CONTRIBUTING-CLAUDE-CODE.md §3`), puis :

1. Coder `scripts/logs_query.py` — tail SSH structuré sur logs Jeedom (nécessaire pour WF2, WF3, WF4)
2. Coder `scripts/api_call.py` — wrapper JSON-RPC (blacklist + retry + filtrage sensible)
3. Valider WF2 (diagnostic scénario) end-to-end sur box réelle — nécessite `logs_query.py` + `api_call.py`
4. Rédiger `references/plugin-virtual.md` + `references/plugin-jmqtt.md` (tier-1)
5. Coder `scripts/usage_graph.py` — graphe d'usage (WF6, WF12, WF13)
6. Valider WF6 end-to-end sur box réelle
7. Rédiger `references/plugin-agenda.md` + `references/plugin-script.md` + `references/plugin-generic-pattern.md`

**Critère de sortie J3** : WF2 (diagnostic scénario) + WF6 (graphe d'usage) validés sur box réelle.

## Données connues de la box réelle (Jeedom 4.5.3)

- 217 eqLogics (177 actifs, 40 désactivés)
- 62 scénarios (57 actifs, 5 inactifs)
- 6219 commandes dont 221 info historisées
- 58 variables globales dataStore
- 0 erreur système récente
- 133 commandes info historisées sans valeur en base (principalement thermostats + météo)

## En attente du PO

- **À J3** : Validation manuelle WF2 (diagnostic scénario) sur box réelle

---

*Document vivant — mis à jour par Claude Code à chaque session significative.*
*Format spécifié en PLANNING §7.3.a.*
