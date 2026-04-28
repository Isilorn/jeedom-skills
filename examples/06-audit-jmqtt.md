---
id: accept-06
titre: Audit plugin jMQTT — broker, devices, topics
workflow: WF3/WF4
statut: ✅ validé
---

# Cas d'acceptation 06 — Audit jMQTT (WF3/WF4)

## Prompt utilisateur

> "audite mes équipements jMQTT — je veux voir le broker, les devices, et si les topics sont cohérents"

## Prérequis

- Accès SSH+MySQL configuré
- Plugin jMQTT installé avec au moins un broker et des devices

## Ce que la skill doit faire

1. Charger `plugin-jmqtt.md`
2. Identifier brokers et devices via DB
3. Filtrer les champs sensibles (mot de passe broker)
4. Vérifier cohérence topics/brokers
5. Lire les logs daemon jMQTT

## Critères de validation

- [x] Mot de passe broker masqué (non exposé dans la sortie)
- [x] Distinction broker / device claire
- [x] Topics extraits et analysés (`configuration.mqttIncTopic`, `configuration.topic`)
- [x] Devices sans topic signalés ⚠️
- [x] Anti-patterns détectés (catch-all, doublons de topic)
- [x] Logs daemon analysés

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Jeedom 4.5.3 — Mac → SSH+MySQL | ✅ PASS | 5 brokers, 54 devices, anomalies critiques détectées, ~4 min |
| 2026-04-28 | Jeedom 4.5.3 — Linux dev | ✅ PASS | Référence J3 |

## Sortie réelle (sanitisée — extraits clés)

```
> audite mes équipements jMQTT — je veux voir le broker, les devices,
  et si les topics sont cohérents

⏺ Je charge plugin-jmqtt.md puis interroge la box.
  [requêtes broker + devices + logs daemon jMQTT]

---
Audit jMQTT — Maison

5 brokers · 54 devices · 4 581 commandes auto-créées

§1 — Brokers (5)

┌─────┬────────────────┬───────────────┬──────────────────┬────────┐
│ ID  │      Nom       │    Adresse    │  Topic d'écoute  │ Statut │
├─────┼────────────────┼───────────────┼──────────────────┼────────┤
│ 447 │ Zwave          │ mqtt.local    │ zwave/#          │ ✅     │
│ 448 │ Zigbee         │ mqtt.local    │ zigbee2mqtt/#    │ ✅     │
│ 452 │ Nodered        │ mqtt.local    │ nodered/#        │ ✅     │
│ 704 │ Room Assistant │ MQTT.local    │ NULL             │ ⚠️     │
│ 714 │ Présence       │ mqtt.local    │ home/presence/#  │ ✅     │
└─────┴────────────────┴───────────────┴──────────────────┴────────┘
> ⚠️ Mot de passe broker omis de ce rapport.

⚠️ Broker "Room Assistant" (704) :
- Hostname MQTT.local (M majuscule) vs mqtt.local — risque DNS selon resolver
- inc_topic = NULL — aucun message reçu. Intentionnel ?

§2 — Répartition devices par broker

┌──────────────┬────────────┐
│    Broker    │ Nb devices │
├──────────────┼────────────┤
│ 448 Zigbee   │ 28         │
│ 447 Zwave    │ 22         │
│ 714 Présence │ 3          │
│ 452 Nodered  │ 1          │
└──────────────┴────────────┘

§3 — Devices Zigbee (28) — topics zigbee2mqtt/0xXXXX/# cohérents ✅

⚠️ Anti-pattern — device "zigbee2mqtt" (ID 449) :
Topic zigbee2mqtt/# = même que le broker 448.
148 commandes auto-créées (topics système bridge/state, bridge/devices…).
Pollue la base, inutilisable directement.

§4 — Devices Zwave (22)

❌ Anti-pattern critique — device catch-all "zwave" (ID 451) :
Topic zwave/# = même que le broker 447.
1 926 commandes auto-créées, sans jsonPath utilisable.
Principal responsable des commandes "sans Type Générique" de l'audit général.

⚠️ Doublon de topic — nodeID_32 :
"Prise Zwave Bureau Alice" (315) et "Prise ZWave Bureau Alice 2" (691)
écoutent tous deux zwave/nodeID_32/#.
591 + 583 = 1 174 commandes en double pour un seul node physique.

§6 — Logs daemon jMQTT

Erreurs détectées sur les 30 derniers jours :
- 2026-04-07 : "Pas d'équipement jMQTT avec l'id 447" (×19)
  → rechargement plugin, transitoire, non récurrent ✅
- 2026-04-08 / 2026-04-24 : MySQL SQLSTATE HY000
  → redémarrage MySQL, normal ✅
- 2026-04-12 : "Accès non autorisé depuis 127.0.0.1 sans clé API"
  → script local mal configuré, non récurrent ✅

Aucune erreur de connexion broker → daemon opérationnel ✅

§7 — Actions recommandées

🔴 Urgent
1. Supprimer le device catch-all "zwave" (ID 451)
   → 1 926 commandes inutiles — UI : jMQTT → broker Zwave → supprimer
2. Supprimer "Prise ZWave Bureau Alice 2" (ID 691)
   → doublon nodeID_32, 583 commandes en double

🟡 À faire
3. Corriger broker "Room Assistant" (704) — hostname + topic d'écoute NULL
4. Supprimer device catch-all "zigbee2mqtt" (ID 449) — 148 commandes système

🟢 Optionnel
5. Assigner un objet aux devices sans objet (invisibles sur dashboard)
6. Activer suivi availability comme indicateur de santé Zigbee
```

## Observation technique

Les requêtes SQL avec `JSON_EXTRACT` imbriqué dans `echo '...' | python3` échouent
sur l'échappement JSON. Claude se corrige en utilisant Python subprocess directement.
Pattern récurrent → gotcha ajouté dans `SKILL.md`.
