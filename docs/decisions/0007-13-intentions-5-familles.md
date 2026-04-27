# ADR 0007 : 13 intentions utilisateur dans 5 familles

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D4.1 v3)

## Contexte

Une skill d'audit Jeedom peut couvrir un spectre très large de besoins utilisateurs : de la simple lecture d'une valeur à l'enquête forensique multi-scénarios. Il faut délimiter le périmètre fonctionnel V1 de manière explicite, afin de guider le développement et de définir les refus de périmètre.

## Options considérées

- **Option A — Périmètre minimal (3-5 workflows)** : audit général + diagnostic scénario + explication. ➕ MVP rapide. ➖ Couvre mal les besoins réels (usage graph, refactor très demandés).
- **Option B — 13 intentions dans 5 familles** : périmètre complet établi en idéation (v3 après 3 itérations). ➕ Couverture complète des cas d'usage communauté, cohérence. ➖ Développement plus long.
- **Option C — Périmètre ouvert** : "tout ce qui est possible en lecture seule". ➕ Flexibilité. ➖ Impossible à tester, documenter et maintenir de manière rigoureuse.

## Décision

**Option B — 13 intentions dans 5 familles** comme base de départ V1, avec périmètre extensible.

| Famille | Intentions V1 |
|---|---|
| Audit | 1 — Audit général |
| Diagnostic | 2 — Diagnostic scénario, 3 — Diagnostic équipement, 4 — Diagnostic plugin, 13 — Diagnostic causal (forensique) |
| Explication | 5 — Explication scénario |
| Graphe / Orchestration | 6 — Graphe d'usage, 12 — Cartographie d'orchestration |
| Refactor | 7 — Suggestions de refactor verbales |
| Lecture rapide | 8 — Valeur courante, 9 — Historique, 10 — Variable dataStore, 11 — Recherche |

**Hors scope initial** : présentation/design, gestion utilisateurs, infrastructure étendue, interactions vocales, listeners, parsing logs structuré (niveau 3+), format-aware plugins.

**Extension possible** : si un cas d'usage pertinent émerge (retour communauté, découverte en session de dev), il peut être intégré via une ADR dédiée documentant la justification et la portée. Pas de 14ème intention sans ADR.

## Conséquences

- ✅ 13 workflows documentés et testables (un jeu d'évals par workflow majeur)
- ✅ Refus de périmètre définis et implémentables dans SKILL.md §11
- ✅ Chaque workflow a des déclencheurs, étapes, sources et format de sortie définis
- ✅ Extensible au fil du développement V1 ou en V2+ via ADR
- ⚠️ Toute extension nécessite une ADR : justification, périmètre, éval associée — pas d'ajout ad-hoc
- ⚠️ Les workflows 12 et 13 (orchestration, forensique) sont les plus complexes — à développer en J6 et J3
- 🔗 PLANNING §3.10 (workflows détaillés), ADR 0008 (helpers), ADR 0009 (plugins)
