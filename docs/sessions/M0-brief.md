# Brief jalon M0 — Baseline Phase 0

**Branche** : `main` (aucune modification de code)
**Pré-requis** : aucun — premier jalon de la migration
**Référence** : `docs/state/migration-jeedom-audit-brief.md` §10

## Contexte

Avant toute modification du repo, documenter le comportement réel des 13 workflows sur
`main` (SSH + MySQL). Ce baseline sert de référence pour démontrer, en M8, qu'aucune
régression n'a été introduite par la migration vers Holmes MCP.

Les tests sont exécutés depuis Claude Code sur la box réelle (alias SSH `Jeedom` configuré,
`~/.my.cnf` présent). Le PO valide chaque résultat.

## Document de sortie

`docs/sessions/2026-05-06-M0-baseline.md` — tableau 13 WF × Phase 0.

Structure du tableau :

```markdown
| WF | Prompt utilisé | Résultat (résumé) | Verdict | Anomalie |
|---|---|---|---|---|
| WF1 | ... | ... | ✅/⚠️/❌ | ... |
```

Verdicts : ✅ réponse cohérente sans erreur · ⚠️ réponse partielle ou dégradée · ❌ erreur ou absence

---

## M0-1 — WF1 à WF7

**Objectif** : exécuter et documenter les 7 premiers workflows sur `main`.

**Prompts de test** (adapter avec des noms réels de la box) :

| WF | Prompt |
|---|---|
| WF1 | "Fais un audit général de mon installation Jeedom" |
| WF2 | "Diagnostique le scénario [nom d'un scénario actif]" |
| WF3 | "Diagnostique l'équipement [nom d'un équipement actif]" |
| WF4 | "Diagnostique le plugin [nom d'un plugin installé]" |
| WF5 | "Explique-moi ce que fait le scénario [nom]" |
| WF6 | "Où est utilisée la commande [nom d'une commande info réelle] ?" |
| WF7 | "Quelles améliorations peux-tu suggérer pour mon installation ?" |

**Livrable** : `docs/sessions/2026-05-06-M0-baseline.md` créé, lignes WF1–WF7 remplies.

**Gate qualité** : 7 lignes remplies avec verdict, aucune ligne vide.

---

## M0-2 — WF8 à WF13 + fin de jalon

**Pré-requis** : M0-1 terminée, fichier baseline existant.

**Objectif** : compléter le tableau avec les 6 workflows restants, puis clore le jalon.

**Prompts de test** :

| WF | Prompt |
|---|---|
| WF8 | "Quelle est la valeur actuelle de [nom d'une commande info] ?" |
| WF9 | "Montre-moi l'historique de [nom d'une commande historisée]" |
| WF10 | "Liste les variables dataStore de mon installation" |
| WF11 | "Cherche tout ce qui concerne [mot-clé présent dans l'installation]" |
| WF12 | "Cartographie les scénarios orchestrés depuis [nom d'un scénario maître]" |
| WF13 | "Pourquoi [équipement ou scénario] s'est-il déclenché hier soir ?" |

**Livrable** : `docs/sessions/2026-05-06-M0-baseline.md` complété (13/13 WF).

**Gate qualité** : 13 lignes remplies, tous les verdicts notés.

---

## DoD — Jalon M0

- [ ] `docs/sessions/2026-05-06-M0-baseline.md` existe et contient 13 WF documentés
- [ ] Chaque WF a : prompt exact utilisé, résumé de la réponse, verdict
- [ ] Aucun WF sans verdict (même ❌ est acceptable — documenter l'anomalie)
- [ ] Fichier commité sur `main`
