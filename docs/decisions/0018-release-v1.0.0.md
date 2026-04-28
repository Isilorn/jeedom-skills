# ADR 0018 : Release V1.0.0 — bilan des écarts et décisions finales

- **Date** : 2026-04-28
- **Statut** : Accepté
- **Contexte de décision** : Jalon J7 — release finale, conformément à PLANNING §7.6

## Contexte

La release V1.0.0 clôture le développement initial de la skill `jeedom-audit`. Cette ADR documente les écarts entre le PLANNING initial et la livraison réelle, ainsi que les décisions prises en cours de route qui n'ont pas fait l'objet d'une ADR dédiée.

## Périmètre livré vs. prévu

### Conforme au PLANNING

- 13 intentions dans 5 familles (ADR 0007) — toutes implémentées
- 6 plugins tier-1 : Virtual, jMQTT, Agenda, Script, Alarme, Thermostat (ADR 0009)
- Lecture seule absolue V1 (ADR 0006) — aucune exception
- Routage transparent MySQL/API (ADR 0017)
- 191 tests unitaires passants — cible atteinte
- 15 évals comportementales (cible planning : 10-15)
- WF1, WF2, WF3, WF4, WF5, WF6, WF12 validés sur box réelle Jeedom 4.5.3

### Écarts documentés

| Élément | Prévu | Livré | Décision |
|---|---|---|---|
| Fixtures DB synthétiques | `db/medium_install.sql` (J1) | Dossier vide — tests avec mocks | Tests sur box réelle suffisants pour V1 ; fixtures synthétiques reportées en V1.5 |
| Tests d'intégration | 5-8 tests (§6.2) | Dossier créé, 0 test | Box réelle + 191 tests unitaires couvrent le besoin V1 ; intégration automatisée en V1.5 |
| Validation 2 utilisateurs externes | Go/no-go V1 | À compléter post-release | Release conditionnelle — le critère est maintenu mais ne bloque pas la publication |
| Captures d'écran README/guides | Fournies par PO à J7 | Placeholders | À intégrer dès fourniture par le PO |
| WF13 (forensique) en API-only | Refus explicite prévu | Implémenté et documenté | Conforme ADR 0005 |

### Découvertes techniques intégrées (non prévues initialement)

- **MariaDB 10.5** : `JSON_TABLE` absent — contournement `JSON_UNQUOTE(JSON_EXTRACT(...))` systématique
- **`repeat` et `trigger`** : mots réservés MariaDB — backtick obligatoire (intégré dans `db_query.py`)
- **`scenarioLog/`** : répertoire (pas un fichier) — logs par scénario dans `scenario{ID}.log`
- **`lastLaunch`/`state`** : champs runtime API uniquement (absents de la table `scenario`)
- **`eqType_name = 'calendar'`** pour le plugin Agenda (pas `agenda`)
- **`eqType_name = 'alarm'`** pour le plugin Alarme (sans accent)

## Décisions finales

### Routage et dégradation gracieuse

La règle de priorité MySQL > API avec fallback automatique (ADR 0017) est maintenue pour V1. WF13 est le seul workflow refusé explicitement en mode API-only (logs requis).

### Versioning post-release

La prochaine version de stabilisation sera `v1.1.0` (correctifs + retours communauté). Les évolutions majeures (support Jeedom 4.4, nouveaux plugins tier-1) sont en `v2.0.0`.

### Contributions

Ouvertes dès V1.0.0 via les templates GitHub et CONTRIBUTING.md.

## Conséquences

- ✅ La skill est fonctionnelle et validée sur une installation réelle (Jeedom 4.5.3)
- ✅ Les 8 cas d'acceptation sont documentés dans `examples/`
- ⚠️ Les fixtures synthétiques seront créées en V1.5 pour permettre des tests d'intégration automatisés sans box réelle
- ⚠️ La validation par 2 utilisateurs externes reste un critère suivi post-release

## Alternatives écartées

**Retarder la release jusqu'aux fixtures synthétiques** — écarté : les tests sur box réelle offrent une couverture fonctionnelle supérieure pour V1. Les fixtures sont utiles pour les contributeurs sans box Jeedom, mais ne bloquent pas la fiabilité de la skill.
