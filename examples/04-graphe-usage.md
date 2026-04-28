---
id: accept-04
titre: Graphe d'usage d'une commande
workflow: WF6
statut: ✅ validé
---

# Cas d'acceptation 04 — Graphe d'usage (WF6)

## Prompt utilisateur

> "Quels scénarios et équipements utilisent la commande Présence de Géraud Shelly ?"

## Prérequis

- Accès SSH+MySQL configuré
- Commande `[Maison][Présence Géraud][Présence]` (ou équivalent) présente
- `usage_graph.py` opérationnel

## Ce que la skill doit faire

1. Résoudre le nom de commande en ID via `db_query.py`
2. Exécuter `usage_graph.py` avec `target_type=cmd` et l'ID trouvé
3. Consolider les références : triggers, conditions, actions, code scénario
4. Présenter un tableau structuré par catégorie

## Format de sortie attendu

```markdown
### Graphe d'usage — [Maison][Présence Géraud Shelly][Présence] (cmd_id: XXXX)

**Utilisée comme déclencheur dans :**
| Scénario | id | Mode |
|---|---|---|
| Présence Géraud | 70 | provoke |

**Utilisée dans des conditions :**
| Scénario | id | Expression |
|---|---|---|
| Mode_Absent_on | 45 | #[Maison][Présence Géraud Shelly][Présence]# == 0 |

**Utilisée dans des actions :**
(aucune)

**Total : 2 références dans 2 scénarios**
```

## Critères de validation

- [ ] Les 4 catégories sont cherchées (trigger, condition, action, code)
- [ ] Chaque référence cite le scénario par son nom (pas juste l'ID)
- [ ] Le total est cohérent avec les lignes du tableau
- [ ] Si la commande est introuvable : message clair, pas d'erreur Python

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Box réelle Jeedom 4.5.3 — SSH+MySQL | ✅ PASS | cmd 15663 → 3 références identifiées dans 2 scénarios |
