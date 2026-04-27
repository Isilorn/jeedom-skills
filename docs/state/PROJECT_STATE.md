# État du projet jeedom-audit

**Version actuelle** : 0.4.0 (pré-release J3)
**Jalon en cours** : J3 terminé — J4 à démarrer
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
- `scripts/logs_query.py` — tail SSH structuré, détection auto répertoire, support sous-dossiers (22/22 tests)
- `scripts/api_call.py` — wrapper JSON-RPC, blacklist V1, retry, filtrage sensible (27/27 tests)
- `scripts/usage_graph.py` — graphe d'usage cmd/eqLogic/scénario, jointure 4-tables (23/23 tests)
- `references/connection.md` rédigé
- `references/sql-cookbook.md` rédigé (10 familles, ~200 lignes)
- `references/scenario-grammar.md` rédigé (types/subtypes/options, pseudo-code WF5)
- `references/audit-templates.md` rédigé (12 sections fixes WF1)
- `references/health-checks.md` rédigé (seuils ✅/⚠️/❌)
- `references/plugin-virtual.md` rédigé (9 sections, patterns commandes, requêtes d'audit)
- `references/plugin-jmqtt.md` rédigé (9 sections, topics MQTT, jsonPath, daemon)
- `tests/unit/` : 123/123 passants
- WF1 validé end-to-end sur box réelle (Jeedom 4.5.3, 177 eqLogics actifs, 57 scénarios actifs)
- WF2 validé end-to-end sur box réelle (API state+lastLaunch + DB arbre + logs scenarioLog/)
- WF5 validé end-to-end sur box réelle (scénario 70 "Présence Géraud Shelly")
- WF6 validé end-to-end sur box réelle (cmd 15663 → trigger+condition scénario 70)
- Credentials configurés : user RO `jeedom_audit_ro`, `~/.my.cnf` box, `credentials.json` local (perm 600)

## Ce qui est en cours / en attente

Aucun — J3 fermé proprement.

## Décisions ouvertes

Aucune décision ouverte.

## Blocages

Aucun blocage technique.

## Prochaines étapes

**J4 — Plugins restants + fin de la couverture tier-1**

1. Rédiger `references/plugin-agenda.md` (plugin `calendar` sur la box)
2. Rédiger `references/plugin-script.md`
3. Rédiger `references/plugin-generic-pattern.md` — pattern 4 temps pour tous les autres plugins
4. Valider WF3 (lecture de logs structurés) et WF4 (corrélation événements) — s'appuient sur `logs_query.py`
5. CHANGELOG v0.4.0 + bump version

**Critère de sortie J4** : références plugins tier-1 complètes + WF3/WF4 validés.

## Découvertes techniques J3 (pour J4+)

- `scenarioLog/` est un répertoire (pas un fichier) — un fichier par scénario : `scenario{ID}.log`
- `scenarioElement` n'a pas de `scenario_id` — lien via `scenario.scenarioElement` (JSON array)
- Appels de scénarios dans `scenarioExpression.options["scenario_id"]` (pas dans `expression`)
- Guillemets doubles en SQL MySQL → valeurs string doivent être entre guillemets simples → toujours utiliser `params`
- 35 eqLogics virtual, 59 eqLogics jMQTT (principalement Zigbee2MQTT) sur la box de réf.

## Données connues de la box réelle (Jeedom 4.5.3)

- 217 eqLogics (177 actifs, 40 désactivés)
- 62 scénarios (57 actifs, 5 inactifs)
- 6219 commandes dont 221 info historisées
- 58 variables globales dataStore
- 0 erreur système récente
- 133 commandes info historisées sans valeur en base (principalement thermostats + météo)
- 35 eqLogics virtual, 59 eqLogics jMQTT, 36 plugins distincts

## En attente du PO

Aucune action requise pour démarrer J4.

---

*Document vivant — mis à jour par Claude Code à chaque session significative.*
*Format spécifié en PLANNING §7.3.a.*
