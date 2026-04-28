---
id: accept-08
titre: Plugin tier-générique inconnu — inférence assumée
workflow: WF3/WF4 + tier-générique
statut: ✅ validé
---

# Cas d'acceptation 08 — Plugin tier-générique inconnu (WF3/WF4)

## Prompt utilisateur

> "Audite mes équipements du plugin Philips Hue"

*(Plugin non couvert en tier-1 — pas de fiche `references/plugin-philips-hue.md`)*

## Ce que la skill doit faire

1. Constater l'absence de fiche tier-1 pour ce plugin
2. Appliquer le pattern `plugin-generic-pattern.md` en 4 temps :
   - Identification de surface (eqType_name, nb eqLogics, structure DB)
   - Extraction d'échantillons (1-3 eqLogics + leurs commandes)
   - Inférence Claude assumée explicitement (pas de certitude feinte)
   - Intégration aux workflows standards (santé, commandes sans type générique, etc.)
3. Mentionner explicitement que l'analyse repose sur l'inférence, non sur une fiche de référence

## Format de sortie attendu

```markdown
### Audit — Plugin Philips Hue (eqType_name: `philipshue`)

> ℹ️ Ce plugin n'a pas de fiche de référence tier-1 dans jeedom-audit.
> L'analyse ci-dessous repose sur l'inspection de la structure DB et sur l'inférence —
> elle peut être incomplète. Pour une couverture complète, consultez la
> [documentation officielle Jeedom](https://doc.jeedom.com/fr_FR/plugins/).

**Surface détectée :** 8 eqLogics, 47 commandes, eqType_name = `philipshue`

**Échantillon (eqLogic id 234 — "Ampoule Salon") :**
| Commande | Type | Sous-type | isHistorized |
|---|---|---|---|
| Couleur | action | color | 0 |
| Luminosité | action | slider | 0 |
| État | info | binary | 1 |

**Inférence :**
Ce plugin semble gérer des ampoules connectées Philips Hue.
Les commandes "Couleur" et "Luminosité" sont probablement des actionneurs.

**Points d'attention :**
⚠️ 12 commandes sans Type Générique assigné
```

## Critères de validation

- [ ] La mention "inférence" est explicite et visible
- [ ] Le pattern 4 temps est appliqué (surface → échantillon → inférence → intégration)
- [ ] La skill ne prétend pas avoir une certitude sur la logique interne du plugin
- [ ] Les données factuelles (nb eqLogics, structure DB) sont exactes
- [ ] Un lien vers la documentation officielle est fourni

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | — | ✅ PASS | Inférence assumée explicitement, pattern 4 temps appliqué, lien doc fourni |
