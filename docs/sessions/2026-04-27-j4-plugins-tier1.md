# Session 2026-04-27 — J4 Plugins tier-1 + WF3/WF4

## Objectif de la session

Rédiger les références plugins tier-1 manquants (agenda, script, alarme, thermostat) + le pattern générique, puis valider WF3 et WF4 end-to-end sur box réelle.

## Décisions prises pendant la session

- **Alarme et Thermostat promus tier-1** : décision PO en début de session — ils sont suffisamment présents et complexes (alarme multi-zones, thermostat avec algorithme temporel et apprentissage) pour mériter une référence dédiée.
- **MQTT Manager maintenu en générique** : souvent une dépendance transparente d'autres plugins (ZeeZigbee, zwavejs), pas un plugin configuré directement par l'utilisateur. Noté explicitement dans `plugin-generic-pattern.md`.
- **`repeat` est un mot réservé MariaDB** : à toujours écrire \`repeat\` entre backticks dans les requêtes SQL sur `calendar_event`.
- **eqType_name `alarm` (pas `alarme`)** : l'identification DB utilise `alarm` sans accent — documenté dans le fichier de référence.

## Découvertes / surprises

- **`calendar_event.repeat` = mot réservé MariaDB** : la requête échoue avec `ERROR 1064` si `repeat` n'est pas backtick-quoté. Noté dans `plugin-agenda.md`.
- **Champs thermostat dans config calendar** : `eqLogic.configuration` pour un agenda contient `heating`, `cooling`, `stoping`, `window`, `failure`, `failureActuator` — héritage d'un modèle de base partagé avec thermostat. Ces champs sont vides sur l'agenda, non utilisés.
- **0 eqLogic script sur la box de référence** : `plugin-script.md` rédigé sur base documentaire uniquement — marqué explicitement.
- **`cmd.value` des commandes info thermostat = NULL** : les valeurs runtime ne sont pas stockées dans `cmd.value` pour le thermostat (hors mise à jour explicite). Les valeurs réelles sont dans la table `history`.
- **`always_active = "1"` sur l'alarme incendie** : l'alarme incendie de la box est conçue pour ne jamais être désactivable — pattern valide, documenté comme tel.

## Travail réalisé

- `jeedom-audit/references/plugin-agenda.md` (10 sections — `calendar_event`, récurrence, requêtes d'audit)
- `jeedom-audit/references/plugin-script.md` (9 sections — syntaxes, credentials, logs)
- `jeedom-audit/references/plugin-alarme.md` (12 sections — zones, modes, variables `#alarm_trigger#`, `#time#`)
- `jeedom-audit/references/plugin-thermostat.md` (11 sections — algorithme temporel, coefficients, modes, fenêtres)
- `jeedom-audit/references/plugin-generic-pattern.md` (4 temps + cas MQTT Manager)
- `jeedom-audit/SKILL.md` §8 + §9 mis à jour (6 plugins tier-1, statuts J4)
- WF3 validé sur box réelle — Thermostat bureau Géraud (db_query ✅, cmd.value ✅, logs_query ✅)
- WF4 validé sur box réelle — plugin thermostat (api_call plugin::listPlugin ✅, eqLogics status ✅, logs ✅)

## Reste à faire (dans ce jalon)

- CHANGELOG v0.5.0 (en cours — fin de session)
- Bump version dans pyproject.toml

## Pour la prochaine session (J5)

**Commencer par :** révision cross-check de SKILL.md complet (cohérence §3/§8/§9 avec les nouvelles références) + démarrer J5 selon PLANNING.

**Contexte :**
- 6 plugins tier-1 documentés : virtual, jMQTT, calendar, script, alarm, thermostat
- WF1-WF6 tous validés sur box réelle
- MQTT Manager → pattern générique (eqType_name = `mqtt2`)

## Pour le PO

Aucune action requise. WF3 + WF4 validés automatiquement sur box réelle.
