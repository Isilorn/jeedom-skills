---
description: Index des cas d'acceptation V1 — recette go/no-go avant release
---

# Recette d'acceptation V1

Ces 8 cas valident la skill `jeedom-audit` avant la release `v1.0.0`.
**Critère go/no-go : 100 % passent + tests unitaires verts + 2 utilisateurs externes confirmés.**

| # | Cas | Workflow | Statut |
|---|---|---|---|
| [01](01-audit-general.md) | Audit général de santé | WF1 | ✅ validé |
| [02](02-explication-scenario.md) | Explication scénario complexe | WF5 | ✅ validé |
| [03](03-diagnostic-causal.md) | Diagnostic causal | WF13 | ✅ validé |
| [04](04-graphe-usage.md) | Graphe d'usage d'une commande | WF6 | ✅ validé |
| [05](05-cartographie-orchestration.md) | Cartographie d'orchestration | WF12 | ✅ validé |
| [06](06-audit-jmqtt.md) | Audit plugin jMQTT | WF3/WF4 | ✅ validé |
| [07](07-refus-modification.md) | Refus de modification | lecture seule | ✅ validé |
| [08](08-plugin-tier-generique.md) | Plugin tier-générique inconnu | WF3/WF4 | ✅ validé |

## Comment valider un cas

1. Installer la skill (`docs/guides/getting-started.md`)
2. Envoyer le prompt exact décrit dans le cas
3. Vérifier chaque critère de la checklist
4. Renseigner la ligne "Résultats" avec date, environnement et notes
