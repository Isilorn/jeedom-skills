# ADR 0014 : Télémétrie opt-in (compteurs agrégés uniquement)

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D12.2) — amendé en session J0 après arbitrage PO

## Contexte

Certains outils collectent des données d'usage pour améliorer leur produit (crash reports, métriques d'usage, commandes les plus utilisées). Une skill d'audit Jeedom manipule des données potentiellement sensibles (noms d'équipements, scénarios, topologie réseau). Il faut décider d'une politique de télémétrie qui permette de guider le développement sans compromettre la privacy des utilisateurs.

## Options considérées

- **Option A — Zéro télémétrie** : aucune collecte, jamais. ➕ Confiance maximale, RGPD natif, pas d'infra. ➖ Pas de données d'usage automatiques — impossible de savoir quels workflows sont les plus utiles en production.
- **Option B — Opt-in compteurs agrégés uniquement** : si l'utilisateur active explicitement (via `setup`), envoi de compteurs anonymes stricts (workflow déclenché, version Jeedom, succès/échec). Aucune donnée d'installation. ➕ Données utiles pour prioriser les workflows et détecter les versions en production. ➖ Infrastructure légère à maintenir, code de collecte à auditer.
- **Option C — Opt-out** : collecte par défaut, désactivable. ➖ Confiance réduite, RGPD à gérer — écarté d'emblée.

## Décision

**Option B — Opt-in explicite, compteurs agrégés uniquement.**

### Ce qui peut être collecté (uniquement si opt-in activé)

| Donnée | Exemple | Justification |
| --- | --- | --- |
| Workflow déclenché | `workflow=2` (diagnostic scénario) | Prioriser les workflows les plus utiles |
| Résultat | `status=success|error` | Détecter les taux d'échec par workflow |
| Version Jeedom détectée | `jeedom_version=4.5.2` | Adapter la priorité de support par version |
| Version de la skill | `skill_version=0.3.0` | Savoir quelle version est en production |

### Ce qui n'est JAMAIS collecté (même avec opt-in)

- Noms d'équipements, de scénarios, d'objets Jeedom
- IDs, valeurs de commandes, historiques
- Adresses IP ou données réseau de l'installation
- Toute donnée permettant d'identifier l'utilisateur ou son installation

### Mise en œuvre

L'implémentation effective (endpoint de collecte, format d'envoi) fait l'objet d'une **ADR complémentaire** au moment du jalon concerné — pas avant que la base d'utilisateurs soit établie. L'activation se fait via `setup` interactif, désactivée par défaut (`telemetry: false` dans `credentials.json`).

## Conséquences

- ✅ Données d'usage disponibles pour prioriser le développement (si opt-in activé par l'utilisateur)
- ✅ Privacy garantie par design : seuls des compteurs agrégés sont envoyés
- ✅ RGPD : opt-in explicite, liste exhaustive des données collectées documentée
- ⚠️ Infrastructure légère à héberger (endpoint HTTP simple — décision d'implémentation à une ADR future)
- ⚠️ Le code de collecte doit être audité pour garantir qu'aucune donnée d'installation ne fuite accidentellement
- ⚠️ `README.md` §Privacy à mettre à jour pour refléter l'opt-in (remplacer "zéro télémétrie")
- 🔗 `README.md` §Privacy, `credentials.json` champ `telemetry`

## Alternatives écartées

**Zéro télémétrie** (décision initiale du brief D12.2) : écarté après arbitrage PO en session J0 — les données d'usage sont jugées utiles pour prioriser les workflows, à condition que la privacy soit garantie par design.
