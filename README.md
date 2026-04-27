# jeedom-audit — skill Claude Code

> **🚧 En construction — Jalon J4 terminé (plugins tier-1 complets + WF3/WF4)**
> La skill `jeedom-audit` n'est pas encore publiée. WF1–WF6 sont tous validés sur box réelle. 6 plugins tier-1 documentés (Virtual, jMQTT, Agenda, Script, Alarme, Thermostat) + pattern générique.
> Voir [`docs/PLANNING.md`](docs/PLANNING.md) pour le périmètre complet et le calendrier prévu.

---

**Audite, diagnostique et explique une installation Jeedom 4.5 — sans jamais la modifier.**

`jeedom-audit` est une [skill Claude Code](https://docs.claude.ai) pour la communauté francophone Jeedom. Elle donne à Claude Code une connaissance structurelle de Jeedom 4.5 (base de données, scénarios, plugins, logs) afin de produire des audits, diagnostics et explications détaillées, le tout en **lecture seule absolue**.

## Ce que fera la skill (V1 — en développement)

- Audit général de santé d'une installation Jeedom 4.5
- Diagnostic de scénarios, équipements et plugins
- Explication pas-à-pas de ce que fait un scénario
- Graphe d'usage d'une commande ou d'un scénario
- Suggestions de refactor verbales avec pas-à-pas UI
- Support tier-1 : Virtual, jMQTT, Agenda, Script, Alarme, Thermostat

**Règle absolue** : lecture seule. Toute modification est décrite verbalement et exécutée par l'utilisateur via l'UI Jeedom. Aucun INSERT/UPDATE/DELETE SQL, aucune méthode API modifiante.

## Prérequis (prévisionnels)

- Claude Code (mode run activé)
- Jeedom 4.5.x
- Python 3.10+
- Accès SSH à la box Jeedom (recommandé) ou clé API Jeedom

## Statut

| Jalon | Description | Statut |
| --- | --- | --- |
| J0 | Bootstrap documentaire | **✅ Terminé** |
| J1 | Skeleton skill + connexion SSH+MySQL | **✅ Terminé** |
| J2 | Workflows DB-only + helpers cœur | **✅ Terminé** |
| J3 | Logs + API + graphe d'usage + plugins Virtual/jMQTT | **✅ Terminé** |
| J4 | Plugins tier-1 (Agenda, Script, Alarme, Thermostat, générique) + WF3/WF4 | **✅ Terminé** |
| J5 | Orchestration avancée (WF12/13) | À venir |
| J6 | Orchestration + refactor | À venir |
| J7 | Recette, doc communautaire, release V1.0.0 | À venir |

## Privacy

Aucune donnée d'installation ne quitte ton environnement (noms d'équipements, scénarios, valeurs, adresse IP de ta box).

La skill propose une télémétrie **opt-in facultative** : si tu l'actives via la commande `setup`, seuls des compteurs anonymes sont envoyés (workflow utilisé, version Jeedom, succès/échec). Pas d'identification, pas de données d'installation. Désactivé par défaut.

## Licence

[MIT](LICENSE)
