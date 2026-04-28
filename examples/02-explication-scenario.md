---
id: accept-02
titre: Explication pas-à-pas d'un scénario complexe
workflow: WF5
statut: ✅ validé
---

# Cas d'acceptation 02 — Explication de scénario (WF5)

## Prompt utilisateur

> "Explique-moi ce que fait le scénario Présence Géraud étape par étape"

## Prérequis

- Accès SSH+MySQL configuré
- Scénario "Présence Géraud" (ou équivalent) présent dans l'installation
- `resolve_cmd_refs.py` opérationnel (résolution `#ID#` → `#[Objet][Équipement][Commande]#`)

## Ce que la skill doit faire

1. Identifier le scénario par son nom (`LIKE '%Présence%Géraud%'`)
2. Exécuter `scenario_tree_walker.py` avec `max_depth=5`
3. Résoudre tous les `#ID#` via `resolve_cmd_refs.py`
4. Produire un pseudo-code lisible par un non-développeur

## Format de sortie attendu

```
### Scénario — Présence Géraud (id: 70)

**Déclencheurs :** commande info [Présence][Géraud Shelly][Présence] change

**Logique :**
SI #[Présence][Géraud Shelly][Présence]# == 1 ALORS
  → Action : [Chauffage][Bureau][On]
  → Scénario : Mode_Présence_on (appel immédiat)
SINON
  → Attendre 5 min
  → SI #[Présence][Géraud Shelly][Présence]# == 0 ALORS
      → Scénario : Mode_Absent_on (appel immédiat)
```

## Critères de validation

- [ ] Tous les `#ID#` sont résolus en `#[Objet][Équipement][Commande]#`
- [ ] La structure SI/SINON/ALORS est respectée
- [ ] Les appels de scénarios sont identifiés (pas juste les commandes)
- [ ] Aucun ID brut (numérique) dans la sortie
- [ ] Le scénario est lisible par un utilisateur non-développeur

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Box réelle Jeedom 4.5.3 — SSH+MySQL | ✅ PASS | sc70 résolu avec 17 refs #ID# → 0 ID brut résiduel |
| 2026-04-28 | Box réelle Jeedom 4.5.3 — API only | ✅ PASS | WF5 opérationnel en API-only (router.py, sans logs) |
