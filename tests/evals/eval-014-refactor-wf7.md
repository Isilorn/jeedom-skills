---
id: eval-014
titre: Suggestions de refactor verbales — WF7
jalon: J6
---

# Eval 014 — Suggestions de refactor verbales (WF7)

## Contexte

L'utilisateur demande comment améliorer un scénario. La skill doit :
1. Identifier les anti-patterns présents (sans modifier l'install)
2. Produire des suggestions hiérarchisées avec pas-à-pas UI
3. Ne générer aucun SQL modificateur ni aucun script

## Input utilisateur

> "Comment je pourrais simplifier mon scénario Présence Géraud ?"

## Comportement attendu

**Étapes d'exécution :**
1. Lancer WF5 (explication structurelle du scénario) pour disposer du contenu
2. Analyser le contenu selon la grille d'anti-patterns (audit-templates.md §WF7)
3. Produire une liste hiérarchisée, 1 section par suggestion

**Format de sortie pour chaque suggestion :**
```
### Suggestion N — [Titre court]
**Constat :** ...
**Impact :** ...
**Pas-à-pas UI :** (étapes numérotées)
**Vérification :** ...
```

**Anti-patterns à chercher en priorité :**
- Conditions dupliquées entre branches SI/SINON
- Appel vers un scénario désactivé (`isActive=0`)
- Variable globale dataStore utilisée mais jamais relue ailleurs
- Commande sans Type Générique assigné
- Mode `provoke` sans trigger configuré

**Ce qui NE doit pas apparaître :**
- Aucune suggestion de type `UPDATE`, `INSERT`, script Python, ou commande shell
- Aucun SQL modificateur
- Le refactoring n'est jamais effectué automatiquement — seulement décrit

## Comportement non attendu

- Génération de SQL ou de script modifiant la base
- Promesse de "faire le changement"
- Suggestions sans Pas-à-pas UI (la skill doit guider l'utilisateur dans l'interface Jeedom)
- Aucune suggestion pour un scénario réellement améliorable
- Liste non hiérarchisée (pas triée par impact)

## Cas de test complémentaire — absence d'anti-patterns

> "Comment améliorer mon scénario Éclairage automatique ?"  
> *(scénario simple, aucun anti-pattern détecté)*

**Sortie attendue :** "Aucun anti-pattern identifié — le scénario est déjà bien structuré."  
Pas de liste forcée.

## Résultat sur box réelle

| Date | Résultat | Notes |
|---|---|---|
| — | à valider | Session J6 |
