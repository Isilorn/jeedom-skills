# ADR 0013 : Licence MIT

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D11.3)

## Contexte

Le projet vise la communauté open source francophone Jeedom. Il faut choisir une licence adaptée à un outil communautaire : permissif, copyleft, ou autre.

## Options considérées

- **Option A — MIT** : licence permissive, courte, universellement connue. ➕ Permet la réutilisation sans friction, compatible avec les skills Claude Code, standard communauté. ➖ Pas de "viral" — les forks peuvent être propriétaires.
- **Option B — Apache 2.0** : permissive avec clause de brevets. ➕ Protection brevets. ➖ Plus complexe, rarement nécessaire pour un outil de skill.
- **Option C — GPL v3** : copyleft fort. ➕ Garantit que les forks restent open source. ➖ Incompatible avec certaines intégrations propriétaires potentielles, trop contraignant pour un outil de skill.

## Décision

**Option A — Licence MIT.**

Simple, permissive, standard communauté open source. Compatible avec l'usage en skill Claude Code. Pas de contrainte sur les intégrations ou les forks communautaires.

## Conséquences

- ✅ Adoption maximale dans la communauté
- ✅ Compatible avec toutes les intégrations potentielles
- ✅ Standard reconnu : les contributeurs savent ce qu'ils signent
- ⚠️ Les forks peuvent être propriétaires — acceptable pour ce type de projet
- 🔗 `LICENSE` MIT à la racine du repo
