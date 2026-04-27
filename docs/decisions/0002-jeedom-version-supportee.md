# ADR 0002 : Jeedom 4.5 uniquement en V1

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D1.2)

## Contexte

Jeedom a plusieurs versions actives dans la communauté (4.4, 4.5, et bientôt 4.6+). La skill repose sur le schéma DB, les conventions d'API et la structure des logs. Ces éléments peuvent varier significativement entre versions. Il faut décider quelles versions supporter en V1.

## Options considérées

- **Option A — 4.5 uniquement** : documentation et tests ciblés Jeedom 4.5 exclusivement. Refus net si version < 4.4, refus avec mention si 4.4.x, warning si 4.6+. ➕ Focus, cohérence documentaire, schéma DB certain. ➖ Exclut les utilisateurs 4.4.
- **Option B — 4.4 + 4.5** : support des deux versions majeures. ➕ Couverture plus large. ➖ Divergences à gérer (notamment logs : monolog supprimé en 4.5), double jeu de fixtures, complexité accrue pour V1.
- **Option C — 4.5+ (avec adaptation dynamique)** : tentative d'adaptation automatique selon version détectée. ➕ Flexibilité maximale. ➖ Complexité très élevée, risques d'erreurs silencieuses sur versions non testées.

## Décision

**Option A — Jeedom 4.5 uniquement en V1.**

La suppression de monolog en 4.5 crée une rupture significative dans la gestion des logs par rapport à 4.4. Documenter les deux versions multiplierait la complexité sans garantie de couverture correcte des deux. Le focus 4.5 permet une documentation précise et testable.

Politique de version détectée :
- `< 4.4` : refus net
- `4.4.x` : refus avec mention "support 4.4 en roadmap V2 si demande communautaire"
- `4.5.x` : OK silencieux
- `4.6+` : warning + continuer ("teste à tes risques — signale les divergences")

## Conséquences

- ✅ Schéma DB, API et logs documentés avec précision pour 4.5
- ✅ Fixtures de test univoques
- ✅ `version_check.py` implémente la politique ci-dessus
- ⚠️ Utilisateurs 4.4 exclus en V1
- ⚠️ Issue template `divergence_version` pour anticiper 4.6
- 🔗 ADR 0005 (modes d'accès), PLANNING §3.20 (cas limites)

## Alternatives écartées

**Support 4.4** : roadmap V2 si la demande communautaire est forte (issue tracker).
**Adaptation dynamique** : trop complexe pour V1, envisageable en V3.
