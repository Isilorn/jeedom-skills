---
id: eval-013
titre: Cartographie d'orchestration mermaid — WF12
jalon: J6
---

# Eval 013 — Cartographie d'orchestration mermaid (WF12)

## Contexte

L'utilisateur demande la cartographie complète d'une chaîne à partir du scénario "Présence Géraud".
La chaîne implique plusieurs scénarios appelants et appelés, générant >10 nœuds au total.
La sortie attendue est un diagramme mermaid `graph TD` (règle : >10 nœuds → mermaid).

## Input utilisateur

> "Trace-moi la chaîne complète d'appels à partir du scénario Présence Géraud"

## Comportement attendu

**Étapes d'exécution :**

1. Identifier le scénario "Présence Géraud" (recherche par nom → id=70 ou équivalent)
2. `scenario_tree_walker.py` avec `follow_scenario_calls=3`, `max_depth=3`
3. Compter les nœuds (scénarios + commandes action terminaux) → >10 → sortie mermaid
4. Résoudre les `#ID#` via `resolve_cmd_refs.py`
5. Produire un bloc mermaid `graph TD` annoté

**Format de sortie :**

- En-tête : point d'entrée, profondeur explorée, nombre total de scénarios
- Bloc mermaid valide syntaxiquement (`graph TD`, nœuds `SN["🎬 ..."]`, arêtes avec libellé SI condition présente)
- Pied de page : mention des limites (profondeur max, éventuels cycles)
- Pas de prose dupliquant le diagramme

**Ce qui doit apparaître dans le mermaid :**

- Scénario racine (point d'entrée) comme premier nœud
- Arêtes conditionnelles labellisées (ex : `-->|"#[O][E][C]# == 1"|`)
- Nœuds scénario distincts des nœuds commande
- Nœuds tronqués si profondeur max atteinte (`"… (tronqué)"`)

## Comportement non attendu

- Sortie en prose indentée alors que >10 nœuds
- Mermaid syntaxiquement invalide (guillemets non fermés, arêtes malformées)
- Résolution `#ID#` omise (IDs bruts dans le diagramme)
- Diagramme sans le scénario racine
- Erreur fatale si un scénario appelé est introuvable (doit être ignoré avec warning)

## Script de vérification (fixture)

```bash
# Vérifier que scenario_tree_walker accepte follow_scenario_calls
echo '{"scenario_id": 70, "follow_scenario_calls": 3, "max_depth": 3}' \
  | python3 jeedom-audit/scripts/scenario_tree_walker.py \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('scenario:', data['scenario']['name'])
print('tree nodes (root):', len(data['tree']))
print('warnings:', data['warnings'])
"
```

## Résultat sur box réelle

| Date | Résultat | Notes |
|---|---|---|
| 2026-04-28 | ✅ PASS | sc13 "Mode_Absent_off" → 4 appels suivis (sc10, sc8, sc14, sc20), 0 warning, 0 cycle |
