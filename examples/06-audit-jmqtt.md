---
id: accept-06
titre: Audit plugin jMQTT — broker, devices, topics
workflow: WF3/WF4
statut: ✅ validé
---

# Cas d'acceptation 06 — Audit jMQTT (WF3/WF4)

## Prompt utilisateur

> "Audite mes équipements jMQTT — je veux voir le broker, les devices, et si les topics sont cohérents"

## Prérequis

- Accès SSH+MySQL configuré
- Plugin jMQTT installé (`eqType_name = 'jMQTT'`)
- Au moins un broker et un device jMQTT configurés

## Ce que la skill doit faire

1. Requête DB : identifier brokers et devices jMQTT
2. Extraire pour chaque device : `configuration.mqttIncTopic`, `configuration.topic`
3. Filtrer les champs sensibles (mot de passe broker via `sensitive_fields.py`)
4. Vérifier la cohérence topic/broker
5. Produire une vue structurée

## Format de sortie attendu

```markdown
### Audit jMQTT

**Broker(s) détecté(s) :**
| Nom | id | État daemon | Adresse |
|---|---|---|---|
| Zigbee2MQTT | 42 | OK | [filtré] |

> ⚠️ Le mot de passe broker a été omis de ce rapport.

**Devices jMQTT (extrait) :**
| Équipement | id | Topic souscrit | Actif |
|---|---|---|---|
| Prise Salon | 101 | zigbee2mqtt/prise_salon | ✅ |
| Capteur Porte | 102 | zigbee2mqtt/capteur_porte | ✅ |

**Cohérence :**
✅ Tous les topics correspondent au préfixe broker configuré
⚠️ 2 devices sans topic configuré (topics vides)
```

## Critères de validation

- [ ] Le mot de passe broker est masqué ou omis explicitement
- [ ] La distinction broker / device est claire
- [ ] Les topics sont extraits depuis `configuration.mqttIncTopic` (broker) et `configuration.topic` (cmd)
- [ ] Les devices sans topic sont signalés ⚠️

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Box réelle Jeedom 4.5.3 — SSH+MySQL | ✅ PASS | 59 eqLogics jMQTT, broker Zigbee2MQTT — password filtré, 0 topic incohérent |
