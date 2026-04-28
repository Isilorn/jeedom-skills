---
id: accept-04
titre: Graphe d'usage d'une commande
workflow: WF6
statut: ✅ validé
---

# Cas d'acceptation 04 — Graphe d'usage (WF6)

## Prompt utilisateur

> "quels scénarios et équipements utilisent la commande Présence de Alice Shelly ?"

## Prérequis

- Accès SSH+MySQL configuré
- `usage_graph.py` opérationnel

## Ce que la skill doit faire

1. Résoudre le nom de commande en ID via `db_query.py`
2. Exécuter `usage_graph.py` avec `target_type=cmd`
3. Consolider : triggers, conditions, actions, dataStore
4. Présenter par catégorie (sections vides omises)

## Critères de validation

- [x] Commande identifiée automatiquement par nom (sans ID explicite)
- [x] Les 4 catégories cherchées (trigger, condition, action, dataStore)
- [x] Chaque référence cite le scénario par son nom
- [x] Sections vides omises explicitement ("aucun")
- [x] Auto-correction sur erreur de paramètre (robustesse)

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Jeedom 4.5.3 — Mac → SSH+MySQL | ✅ PASS | 1 scénario consommateur, auto-correction paramètre |
| 2026-04-28 | Jeedom 4.5.3 — Linux dev | ✅ PASS | Référence J2 |

## Sortie réelle (sanitisée)

```
> quels scénarios et équipements utilisent la commande Présence de Alice Shelly ?

⏺ Je lance le graphe d'usage sur #[Bluetooth][Présence Shelly Alice][present]# (ID 15663).

[usage_graph.py → résultat en 1 requête]

---
Graphe d'usage — #[Bluetooth][Présence Shelly Alice][present]#

Triggers (scénarios déclenchés par cette commande) :

┌──────────────────────────────────┬────────────────────────────────────────────┐
│             Scénario             │                    Rôle                    │
├──────────────────────────────────┼────────────────────────────────────────────┤
│ "Présence Alice Shelly" (ID 70)  │ Se déclenche à chaque changement de valeur │
└──────────────────────────────────┴────────────────────────────────────────────┘

Conditions (scénarios qui lisent cette commande dans un SI) :

┌──────────────────────────────────┬─────────────────────────────────────────────┐
│             Scénario             │                    Rôle                     │
├──────────────────────────────────┼─────────────────────────────────────────────┤
│ "Présence Alice Shelly" (ID 70)  │ Évalue la valeur dans une condition interne │
└──────────────────────────────────┴─────────────────────────────────────────────┘

Actions, plugins consommateurs, variables dataStore : aucun.

---
La commande est utilisée exclusivement par le scénario "Présence Alice Shelly"
(ID 70) — à la fois comme trigger et comme condition interne.
Aucun autre scénario ni équipement n'y fait référence.
```

## Observation technique

Claude a tenté `{"cmd_id": 15663}` avant de se corriger en `{"target_type": "cmd", "target_id": 15663}` après lecture du script. L'interface de `usage_graph.py` pourrait être mieux documentée dans SKILL.md §7 (WF6) pour éviter ce tâtonnement.
