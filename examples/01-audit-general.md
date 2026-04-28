---
id: accept-01
titre: Audit général de santé
workflow: WF1
statut: ✅ validé
---

# Cas d'acceptation 01 — Audit général de santé (WF1)

## Prompt utilisateur

> "Fais un audit général de mon Jeedom"

## Prérequis

- Skill `jeedom-audit` installée
- Accès SSH+MySQL configuré (credentials.json présent)
- Jeedom 4.5.x

## Ce que la skill doit faire

1. Charger `audit-templates.md`, `health-checks.md`, `sql-cookbook.md`
2. Exécuter un batch de requêtes (inventaire, plugins, scénarios, variables, messages, historique)
3. Appliquer les seuils `health-checks.md` (✅/⚠️/❌/🔴/🟡/🟢)
4. Produire un rapport structuré en 12 sections

## Critères de validation

- [x] Le rapport contient au moins : inventaire, points d'attention, plugins
- [x] Les seuils ✅/⚠️ sont appliqués avec données chiffrées
- [x] Actions recommandées avec pas-à-pas UI (pas de commandes shell)
- [x] Aucune modification de la base (lecture seule)
- [x] Données sensibles filtrées (clé API absente du rapport)

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Jeedom 4.5.3 — Mac → SSH+MySQL | ✅ PASS | Rapport 12 sections, ~2 min, seuils corrects |
| 2026-04-28 | Jeedom 4.5.3 — Linux dev | ✅ PASS | Référence J1 |

## Sortie réelle (sanitisée)

```
> fais un audit général de mon Jeedom

⏺ Je charge les références d'audit avant de lancer les requêtes.
  Read audit-templates.md, health-checks.md, sql-cookbook.md

[batch de ~20 requêtes SQL + 1 appel API plugin::listPlugin]

---
Audit Jeedom 4.5.3 — Maison — 28 avril 2026

⚠️ Quelques points à surveiller — installation fonctionnelle, aucune erreur
système, mais plusieurs points d'hygiène importants dont un compteur RAID
très élevé.

┌──────────────────────────────────────────────┬───────────────────────┐
│                  Indicateur                  │        Valeur         │
├──────────────────────────────────────────────┼───────────────────────┤
│ Équipements actifs                           │ 177 / 217 (81,5 %)    │
├──────────────────────────────────────────────┼───────────────────────┤
│ Scénarios actifs                             │ 57 / 62 (92 %)        │
├──────────────────────────────────────────────┼───────────────────────┤
│ Commandes liées à équipements désactivés     │ 232                   │
├──────────────────────────────────────────────┼───────────────────────┤
│ Commandes sans Type Générique                │ 4 869                 │
├──────────────────────────────────────────────┼───────────────────────┤
│ Erreurs système                              │ 0                     │
├──────────────────────────────────────────────┼───────────────────────┤
│ Variables orphelines                         │ 14                    │
├──────────────────────────────────────────────┼───────────────────────┤
│ Mises à jour                                 │ Données indisponibles │
└──────────────────────────────────────────────┴───────────────────────┘

§2 — Système
┌─────────────────────────┬──────────────────────────┐
│ Version Jeedom          │ 4.5.3 ✅                 │
│ Nom installation        │ Maison                   │
│ Hardware                │ DIY (build personnalisé) │
│ IP interne              │ 192.168.1.10             │
└─────────────────────────┴──────────────────────────┘

§3 — Plugins installés (42)
42 plugins via API. Table update vide (marché non synchronisé).
Plugins : Agenda, Alarme, Alexa API, jMQTT, Localisation, Mode,
MQTT Manager, Script, Thermostat, Virtuel, wifilightV2…
⚠️ CozyTouch apparaît deux fois — doublon à vérifier.

§4 — Équipements
Total : 217 — Actifs : 177 (81,5 %) — Désactivés : 40
✅ Aucun équipement en warning ou danger.

§5 — Scénarios
Total : 62 — Actifs : 57 (92 %) ✅ — Inactifs : 5
Provoke : 54 — Schedule : 7 — All : 1
⚠️ 25 scénarios provoke avec trigger vide (utilitaires ou appelés via API).
⚠️ "Alarme_nuit" (ID 26, inactif) potentiellement référencé dans un autre
scénario — à vérifier.

§7 — Variables dataStore
57 variables globales ⚠️ (seuil : >50)
Variables métier : PresentAlice, PresentBob, consigne (nuit),
consignetemp (16 °C), temp (20.9 °C), equipementsKO (3),
NbFailRAID (15 949 ⚠️)
14 variables orphelines : Firstfail, toto, HeureExtinction,
collectdate, lastseen, HeureExtinctionSalon, msg…

§8 — Messages système
✅ Table message vide — aucune erreur système récente.

§10 — Qualité de l'historique
123 commandes historisées sans aucune donnée enregistrée.
Exemples : coefficients thermostat, caméras remplacées, trackers Tile.

§12 — Actions recommandées

🔴 Urgent
1. Investiguer NbFailRAID = 15 949
   UI : Outils → Scénarios → chercher "RAID" → vérifier logs.

🟡 À faire prochainement
2. Vérifier les trackers Tile (3 équipements, jamais de présence remontée)
3. Vérifier "Alarme_nuit" (scénario inactif potentiellement appelé)
4. Lancer vérification mises à jour : Réglages → Mise à jour

🟢 Nettoyage optionnel
5. Supprimer agendas désactivés (200+ commandes en base inutiles)
6. Attribuer Types Génériques aux commandes prioritaires (4 869 sans)
7. Clarifier les 25 scénarios provoke sans trigger
```
