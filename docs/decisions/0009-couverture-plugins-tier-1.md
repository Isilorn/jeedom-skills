# ADR 0009 : Couverture plugins : tier-1 (4 plugins) + tier-générique

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D1.4, D5.1, D5.2)

## Contexte

Jeedom supporte des dizaines de plugins. La skill ne peut pas documenter tous les plugins en profondeur en V1. Il faut décider quels plugins méritent une documentation approfondie et comment traiter les autres.

## Options considérées

- **Option A — Documentation profonde pour tous les plugins** : ➕ Couverture maximale. ➖ Irréaliste en V1 (volume et maintenance considérables).
- **Option B — Tier-1 (4 plugins) + tier-générique** : documentation profonde pour les plugins les plus répandus, pattern d'inspection générique pour le reste. ➕ Focus réaliste, pattern générique extensible par la communauté. ➖ Certains plugins importants hors tier-1.
- **Option C — Tier-1 (10+ plugins)** : couverture élargie dès V1. ➕ Plus exhaustif. ➖ Risque de dilution et de maintenance difficile.

## Décision

**Option B — Tier-1 (4 plugins) + tier-générique.**

**Tier-1 V1** (documentation profonde dans `references/plugin-X.md`, template 9 sections) :
- `virtual` — virtuel, très répandu, patterns complexes (`infoName`, `updateCmdId`)
- `jMQTT` — MQTT broker/device, gotcha critique : topic dans `logicalId`
- `agenda` — scénarios programmés, format `Gi` des horaires
- `script` — scripts shell/PHP, daemon, sécurité

**Tier-générique** (`references/plugin-generic-pattern.md`) : pattern d'inspection en 4 temps (identification de surface, extraction d'échantillons, inférence Claude assumée explicitement, intégration aux workflows). Applicable à tout plugin inconnu.

Chaque `plugin-X.md` mentionne la version testée du plugin. Au runtime, comparaison signalée si écart détecté.

## Conséquences

- ✅ 4 plugins documentés avec précision, couvrant les cas d'usage les plus fréquents
- ✅ Pattern générique utilisable pour n'importe quel autre plugin
- ✅ Issue template `new_plugin_tier1` pour inviter les contributions communautaires
- ✅ Extensible pendant ou après V1 via ADR dédiée (justification + fixture + version testée requises)
- ⚠️ Tout ajout de plugin tier-1 nécessite une ADR : ne pas ajouter sans fixture sanitisée et version Jeedom+plugin vérifiée
- ⚠️ Plugins importants non couverts initialement (JeedomConnect, Zigbee, etc.) — invités via issue template
- 🔗 ADR 0007 (intentions), PLANNING §3.7
