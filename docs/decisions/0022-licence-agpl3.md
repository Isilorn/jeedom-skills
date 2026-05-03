# ADR-0022 — Bascule licence MIT → AGPL-3.0

- **Date** : 2026-05-03
- **Statut** : Accepté
- **Supersede** : ADR-0013 (Licence MIT)
- **Contexte de décision** : session d'idéation holmesMCP — alignement licences sphère jeedom-audit + holmesMCP

## Contexte

`jeedom-skills` a été publié sous licence MIT (ADR-0013, 2026-04-27). Depuis, le projet frère `holmesMCP` (plugin Jeedom natif MCP) a été initié directement sous AGPL-3.0. L'opportunité d'aligner les deux projets sous une licence commune se présente pendant que `jeedom-skills` est encore seul copyright holder (aucune contribution externe à ce jour).

**Condition préalable vérifiée** : `git log --all --format="%an <%ae>" | sort -u` → un seul auteur : `Isilorn`. La bascule est faisable sans consentement tiers.

## Décision

**Bascule de MIT vers AGPL-3.0** sur le repo `jeedom-skills`, à compter du commit de relicence. Les versions antérieures (v0.1.0 → v1.0.1) restent disponibles sous MIT — propriété intrinsèque des licences open source. Aucun code fonctionnel n'est modifié dans ce commit.

## Raisons

**1. Cohérence sphère jeedom-audit + holmesMCP**

`holmesMCP` démarre en AGPL-3.0 dès sa V1. Les deux projets sont appelés à se coupler étroitement (jeedom-audit basculera consommatrice MCP en V2+ via holmesMCP). Des licences hétérogènes (MIT pour jeedom-skills, AGPL pour holmesMCP) créeraient une confusion juridique pour les contributeurs et utilisateurs. L'alignement simplifie la gouvernance et clarifie la posture de toute la sphère.

**2. Alignement avec l'écosystème Jeedom officiel**

Le core Jeedom est sous AGPL-3.0. Les plugins publiés sur le market officiel sont massivement sous AGPL-3.0. Adopter cette licence inscrit `jeedom-skills` dans la continuité de l'écosystème dans lequel il opère — une question d'hospitalité communautaire.

**3. Garantie copyleft communautaire**

L'AGPL-3.0 garantit que toute dérivation distribuée (fork, adaptation, réutilisation dans un produit tiers, exposition comme service réseau) doit être publiée sous AGPL-3.0. Cela protège la communauté Jeedom contre une appropriation propriétaire d'un travail communautaire.

**4. Coût réel d'adoption tierce : négligeable**

`jeedom-skills` s'adresse à des utilisateurs Jeedom éclairés, pas à des intégrateurs commerciaux. Le périmètre fonctionnel est intrinsèquement lié à Jeedom et ne présente pas d'intérêt commercial autonome. Aucune adoption tierce significative n'est constatée ou anticipée. Le coût réel de la bascule est donc proche de zéro.

**5. Fenêtre d'opportunité**

La bascule est triviale aujourd'hui (seul copyright holder). Dans 18 mois, avec des contributions externes sous AGPL, elle nécessiterait le consentement de tous les contributeurs. La décision est prise pendant que la fenêtre est ouverte.

## Conséquences

- ✅ Sphère unifiée sous AGPL-3.0 : `jeedom-skills` + `holmesMCP` + futures skills
- ✅ Alignement avec l'écosystème Jeedom (core + plugins market)
- ✅ Protection copyleft : les dérivations restent communautaires
- ✅ Gouvernance simplifiée pour les contributeurs (une seule licence à connaître)
- ⚠️ Les versions antérieures (v0.1.0 → v1.0.1) restent sous MIT — c'est inévitable et acceptable
- ⚠️ Tout contributeur futur contribue sous AGPL-3.0 — à mentionner dans CONTRIBUTING.md
- 🔗 ADR-0013 (superseded), `LICENSE`, `holmesMCP`
