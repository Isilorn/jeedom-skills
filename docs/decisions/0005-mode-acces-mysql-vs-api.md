# ADR 0005 : Mode d'accès MySQL+SSH préféré, API Jeedom secondaire

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D3.4, D3.5)

## Contexte

Les données d'une installation Jeedom sont accessibles via deux mécanismes distincts : la base MySQL (via SSH) et l'API JSON-RPC Jeedom. Les deux ont des avantages complémentaires. Il faut décider du mode par défaut et de la stratégie de coexistence.

## Options considérées

- **Option A — MySQL+SSH uniquement** : accès direct à la DB, source de vérité complète. ➕ Données brutes complètes, jointures puissantes, pas de dépendance à l'API. ➖ Nécessite SSH + accès MySQL, plus complexe à configurer.
- **Option B — API Jeedom uniquement** : JSON-RPC officielle. ➕ Interface officielle, pas besoin d'accès SSH. ➖ Méthodes limitées, pas d'accès aux logs, pas de jointures, données runtime seulement.
- **Option C — Coexistence MySQL préféré + API secondaire** : MySQL par défaut, API pour les cas où elle est intrinsèquement meilleure (stats runtime, événements), fallback automatique si MySQL non configuré. ➕ Meilleur des deux mondes. ➖ Plus complexe à implémenter, deux chemins à maintenir.

## Décision

**Option C — Coexistence MySQL préféré + API secondaire.**

Stratégie de bascule :
- MySQL : audit récursif, scénarios, jointures complexes, recherches dans les blobs de configuration
- API : statistiques runtime (`cmd::getStatistique`, `cmd::getTendance`), events (`event::changes`)
- Logs : SSH uniquement (pas disponible via API)
- Détection lazy au premier appel, fallback automatique avec mention si configuré
- Bascule discrète (silencieuse sauf si fallback ou limitation notable)

Le user MySQL est **read-only à perpétuité** (même en V2/V3, les écritures passent par l'API).

## Conséquences

- ✅ Accès aux données les plus complètes (MySQL) et aux données runtime les plus fraîches (API)
- ✅ Fonctionne en mode API-only si SSH non configuré (avec limitations documentées)
- ✅ Logs accessibles via SSH uniquement (workflow 13 indisponible en mode API-only)
- ⚠️ Deux helpers à maintenir : `db_query.py` + `api_call.py`
- ⚠️ Coexistence requiert une logique de sélection dans chaque workflow
- 🔗 ADR 0004 (credentials), ADR 0006 (lecture seule), PLANNING §3.5-3.6
