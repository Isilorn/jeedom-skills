# État du projet jeedom-audit

**Version actuelle** : 0.5.0 (pré-release J4)
**Jalon en cours** : J4 terminé — J5 à démarrer
**Dernière session** : 2026-04-27

---

## Ce qui marche

- Infrastructure documentaire J0 complète (ADRs 0001-0016, arborescence, fichiers racine)
- `jeedom-audit/SKILL.md` rédigé (~260 lignes, 11 sections, 6 plugins tier-1)
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
- `references/plugin-agenda.md` rédigé (10 sections, `calendar_event`, récurrence, requêtes d'audit)
- `references/plugin-script.md` rédigé (9 sections, syntaxes, credentials, logs)
- `references/plugin-alarme.md` rédigé (12 sections, zones, modes, variables spéciales)
- `references/plugin-thermostat.md` rédigé (11 sections, algorithme temporel, coefficients, logs)
- `references/plugin-generic-pattern.md` rédigé (4 temps + cas MQTT Manager)
- `tests/unit/` : 123/123 passants
- WF1 validé end-to-end sur box réelle (Jeedom 4.5.3, 177 eqLogics actifs, 57 scénarios actifs)
- WF2 validé end-to-end sur box réelle (API state+lastLaunch + DB arbre + logs scenarioLog/)
- WF3 validé end-to-end sur box réelle (Thermostat bureau Géraud — db_query + cmd.value + logs_query)
- WF4 validé end-to-end sur box réelle (plugin thermostat — api_call plugin::listPlugin + eqLogics + logs)
- WF5 validé end-to-end sur box réelle (scénario 70 "Présence Géraud Shelly")
- WF6 validé end-to-end sur box réelle (cmd 15663 → trigger+condition scénario 70)
- Credentials configurés : user RO `jeedom_audit_ro`, `~/.my.cnf` box, `credentials.json` local (perm 600)

## Ce qui est en cours / en attente

Aucun — J4 fermé proprement.

## Décisions ouvertes

Aucune décision ouverte.

## Blocages

Aucun blocage technique.

## Prochaines étapes

**J5 — à définir avec le PO**

Thèmes candidats (selon PLANNING) :
- Révision cross-check SKILL.md complet (cohérence §3/§8/§9)
- Enrichissement `sql-cookbook.md` avec les requêtes thermostat/alarme/agenda découvertes en J4
- Packaging `.skill` et getting-started

**Critère de sortie J4** : ✅ atteint — 6 plugins tier-1 documentés + pattern générique + WF3/WF4 validés.

## Découvertes techniques J4 (pour J5+)

- `calendar_event.repeat` est un mot réservé MariaDB — backtick obligatoire dans les requêtes SQL
- `eqLogic.configuration` d'un agenda contient des champs thermostat hérités (`heating`, `cooling`, etc.) — vides, héritage de modèle partagé
- `eqType_name = 'alarm'` (sans accent) pour le plugin Alarme
- `cmd.value` des commandes info thermostat = NULL — valeurs runtime dans `history`, pas dans `cmd`
- 32 eqLogics calendar (12 actifs), 9 thermostat (9 actifs), 2 alarm (2 actifs), 0 script sur la box de réf.

## Données connues de la box réelle (Jeedom 4.5.3)

- 217 eqLogics (177 actifs, 40 désactivés)
- 62 scénarios (57 actifs, 5 inactifs)
- 6219 commandes dont 221 info historisées
- 58 variables globales dataStore
- 0 erreur système récente
- 133 commandes info historisées sans valeur en base (principalement thermostats + météo)
- 35 eqLogics virtual, 59 eqLogics jMQTT, 32 calendar, 9 thermostat, 2 alarm, 36 plugins distincts

## En attente du PO

Aucune action requise pour démarrer J5.

---

*Document vivant — mis à jour par Claude Code à chaque session significative.*
*Format spécifié en PLANNING §7.3.a.*
