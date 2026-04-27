# ADR 0011 : Frontmatter en anglais, contenu en français

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D2.3, D12.1)

## Contexte

La skill cible la communauté francophone Jeedom. Mais le frontmatter YAML de SKILL.md (champs `name`, `description`) est lu par Claude Code pour le matching et la sélection de la skill — un contexte potentiellement multilingue. Il faut décider de la langue du frontmatter et du contenu.

## Options considérées

- **Option A — Tout en français** : cohérence avec le public cible. ➕ Lisibilité pour la communauté. ➖ Matching cross-langue potentiellement réduit si Claude Code tourne dans un contexte anglophone.
- **Option B — Tout en anglais** : cohérence avec l'écosystème Claude Code. ➕ Matching maximal. ➖ Friction pour les utilisateurs francophones qui lisent le SKILL.md.
- **Option C — Frontmatter en anglais, contenu en français** : séparation des préoccupations selon l'audience. Le frontmatter est pour Claude Code (matching, sélection) ; le contenu est pour l'utilisateur francophone. ➕ Meilleur des deux mondes. ➖ Convention à documenter.

## Décision

**Option C — Frontmatter en anglais, contenu en français.**

Matrice de langue :

| Élément | Langue | Raison |
|---|---|---|
| Frontmatter YAML (name, description) | Anglais | Convention écosystème, matching cross-langue |
| Corps SKILL.md | Français | Audience francophone |
| `references/` | Français | Audience francophone |
| `examples/` | Français | Audience francophone |
| Restitutions à l'utilisateur | Français | Audience francophone |
| Messages stderr scripts | Français | Lisibilité pour l'utilisateur |
| Clés JSON stdout | Anglais | Interopérabilité |
| `docs/` (ADRs, guides, sessions) | Français | Audience communauté francophone |
| ADRs | Français | Traçabilité pour le binôme PO/CC |

## Conséquences

- ✅ Description frontmatter en anglais assure le matching même en contexte anglophone
- ✅ Contenu entièrement en français pour la communauté cible
- ✅ Clés JSON en anglais pour l'interopérabilité potentielle
- ⚠️ Convention à respecter rigoureusement — risque de dérive si non documentée
- 🔗 PLANNING §3.8 (frontmatter), §3.25 (langue)
