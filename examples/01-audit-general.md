---
id: accept-01
titre: Audit général de santé
workflow: WF1
statut: ✅ validé
---

# Cas d'acceptation 01 — Audit général de santé (WF1)

## Prompt utilisateur

> "Fais-moi un audit général de mon installation Jeedom"

## Prérequis

- Skill `jeedom-audit` installée et skill active
- Accès SSH+MySQL **ou** clé API configurée (`setup.py` exécuté)
- Jeedom 4.5.x

## Ce que la skill doit faire

1. Exécuter `db_query.py` pour collecter :
   - Inventaire global (eqLogics actifs/inactifs, scénarios, plugins, commandes)
   - Commandes info historisées sans valeur en base
   - Variables dataStore déclarées
   - État des daemons (via API si disponible)
2. Appliquer les seuils `health-checks.md` (✅/⚠️/❌)
3. Produire un rapport structuré en sections

## Format de sortie attendu

```markdown
## Audit général — [Nom installation] — [Date]

### Inventaire
| Catégorie | Total | Actifs | Inactifs |
|---|---|---|---|
| Équipements | … | … | … |
| Scénarios | … | … | … |
| Commandes | … | … | … |

### Points d'attention
⚠️ X commandes info historisées sans valeur en base
⚠️ Y équipements désactivés depuis > 30 jours

### Plugins
[Liste des plugins distincts avec eqType_name]
```

## Critères de validation

- [ ] Le rapport contient au moins : inventaire, points d'attention, plugins
- [ ] Les seuils ✅/⚠️/❌ sont présents
- [ ] Aucune modification de la base (lecture seule)
- [ ] Données filtrées signalées explicitement si credentials absents

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Box réelle Jeedom 4.5.3 — SSH+MySQL | ✅ PASS | 217 eqLogics, 62 scénarios, 36 plugins — rapport complet en ~20s |
