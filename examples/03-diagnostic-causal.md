---
id: accept-03
titre: Diagnostic causal — pourquoi ce scénario ne se déclenche pas ?
workflow: WF13
statut: ⏳ à valider sur cas réel PO
---

# Cas d'acceptation 03 — Diagnostic causal (WF13)

## Prompt utilisateur

> "Mon scénario Mode_Absent_on ne se déclenche plus depuis hier soir, pourtant la présence change bien. Qu'est-ce qui se passe ?"

## Prérequis

- Accès SSH+MySQL + accès logs (`logs_query.py` opérationnel)
- Scénario problématique identifiable par son nom
- Logs récents disponibles (`scenarioLog/`)

## Ce que la skill doit faire

1. Identifier le scénario par nom
2. Vérifier l'état du scénario (`isActive`, `isVisible`, `mode`)
3. Inspecter les déclencheurs (commandes trigger, conditions)
4. Vérifier l'état des commandes déclencheuses (valeur courante, historique récent)
5. Lire les derniers logs du scénario (`logs_query.py`)
6. Remonter la chaîne causale avec evidence à chaque saut

## Format de sortie attendu

```markdown
### Diagnostic — Mode_Absent_on

**Symptôme :** scénario actif mais non déclenché depuis [timestamp]

**Vérification 1 — État du scénario**
✅ isActive = 1, mode = provoke

**Vérification 2 — Déclencheurs**
⚠️ Aucun trigger configuré (mode provoke = appelé par un autre scénario)

**Vérification 3 — Appelants**
→ Scénario Présence_Géraud appelle Mode_Absent_on via action "start"
→ Vérification scénario Présence_Géraud...

**Vérification 4 — Logs**
[Dernières lignes logs scenarioLog/scenario_70.log]

**Conclusion**
Cause probable : [...]
Prochaine étape : [vérification UI recommandée]
```

## Critères de validation

- [ ] La skill remonte la chaîne causale (pas juste le scénario symptôme)
- [ ] Chaque affirmation est étayée par une donnée lue (pas d'hypothèse sans preuve)
- [ ] La conclusion propose une prochaine étape vérifiable par l'utilisateur
- [ ] Pas de modification de l'installation

## Note PO

Ce cas utilise la matière fournie par le PO à J3 (cas réel de scénario qui ne se déclenchait plus). La validation finale se fait sur cette matière réelle.

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| — | — | ⏳ à valider | Matière PO requise |
