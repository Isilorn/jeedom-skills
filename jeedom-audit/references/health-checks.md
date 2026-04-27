---
title: Critères de santé — jeedom-audit
description: Seuils, indicateurs et anomalies pour WF1 (audit général). Définit ce qui est "normal", "à surveiller" et "critique".
updated: 2026-04-27
---

# Critères de santé — jeedom-audit

> **Usage :** chargé par WF1 pour qualifier chaque indicateur (✅ / ⚠️ / ❌).  
> Les seuils sont des valeurs raisonnables pour une installation domestique Jeedom 4.5.  
> Adapter si l'installation est atypiquement grande ou petite.

---

## 1. Système

| Indicateur | ✅ OK | ⚠️ Surveiller | ❌ Critique |
|------------|-------|------------|------------|
| Version Jeedom | 4.5.x | 4.4.x | < 4.4 |
| Version ≥ 4.6 | — | Avertir (schéma peut différer) | — |

---

## 2. Plugins

| Indicateur | ✅ OK | ⚠️ Surveiller | ❌ Critique |
|------------|-------|------------|------------|
| Statut plugin | `ok` | `update` disponible | `error` / `ko` |
| Plugin désactivé | — | Si référencé dans scénario | — |
| Démon plugin | running | — | stopped + erreurs log |

---

## 3. Équipements

| Indicateur | ✅ OK | ⚠️ Surveiller | ❌ Critique |
|------------|-------|------------|------------|
| Ratio actifs / total | ≥ 80 % | 60-80 % | < 60 % |
| Équipements en warning | 0 | 1-3 | > 3 |
| Équipements en danger | 0 | — | ≥ 1 |
| Équipements désactivés référencés en scénario | 0 | — | ≥ 1 |

---

## 4. Scénarios

| Indicateur | ✅ OK | ⚠️ Surveiller | ❌ Critique |
|------------|-------|------------|------------|
| Scénarios inactifs / total | ≤ 20 % | 20-40 % | > 40 % |
| Scénarios désactivés appelés en action | 0 | — | ≥ 1 |
| Scénarios sans trigger valide (mode provoke, trigger vide) | 0 | ≥ 1 | — |

> Un trigger vide `[""]` en mode `provoke` signifie que le scénario ne peut se déclencher qu'à la main ou via l'API — ce n'est pas forcément une erreur (cas "Centre de notifications"), mais mérite d'être noté.

---

## 5. Commandes

| Indicateur | ✅ OK | ⚠️ Surveiller | ❌ Critique |
|------------|-------|------------|------------|
| Commandes mortes (eqLogic absent/désactivé) | 0 | 1-5 | > 5 |
| Commandes info sans Type Générique | ≤ 10 | 10-30 | > 30 |
| Commandes historisées sans valeur récente (>7j) | 0 | 1-3 | > 3 |

---

## 6. Variables dataStore

| Indicateur | ✅ OK | ⚠️ Surveiller | ❌ Critique |
|------------|-------|------------|------------|
| Variables orphelines (non référencées) | 0 | 1-3 | > 3 |
| Total variables globales | ≤ 20 | 20-50 | > 50 (risque de confusion) |

---

## 7. Messages système

| Indicateur | ✅ OK | ⚠️ Surveiller | ❌ Critique |
|------------|-------|------------|------------|
| Erreurs récentes (7 derniers jours) | 0 | 1-5 | > 5 |
| Erreurs répétées même plugin | 0 | 2-3 occurrences | > 3 occurrences |

---

## 8. Historique

| Indicateur | ✅ OK | ⚠️ Surveiller | ❌ Critique |
|------------|-------|------------|------------|
| Commandes info historisées sans aucune donnée | 0 | ≥ 1 | — |
| Commandes sans valeur depuis > 7 jours | 0 | 1-3 | > 3 |
| Commandes sans valeur depuis > 30 jours | 0 | — | ≥ 1 |

---

## 9. Mises à jour

| Indicateur | ✅ OK | ⚠️ Surveiller | ❌ Critique |
|------------|-------|------------|------------|
| Plugins avec update disponible | 0 | 1-3 | > 3 |
| Core Jeedom avec update disponible | — | — | Toujours signaler |

---

## 10. Calcul de l'état global

Règle de décision pour `§1 — Synthèse exécutive` :

```
❌ Critique si :
  - ≥ 1 équipement en danger
  - ≥ 1 scénario désactivé appelé en action
  - > 5 commandes mortes
  - > 5 erreurs système récentes
  - Plugin en état 'error'

⚠️ Surveiller si :
  - ≥ 1 équipement en warning
  - Commandes historisées sans données récentes
  - Variables orphelines
  - Mises à jour disponibles
  - Scénarios désactivés > 20 %

✅ Sain si :
  - Aucune des conditions ci-dessus
```

En cas de doute : signaler et laisser le PO décider.

---

## 11. Points spécifiques installation domestique

Ces points ne sont pas des erreurs mais méritent d'être mentionnés si présents :

- **Scénarios en mode `provoke` avec trigger vide** : ne se déclenchent qu'à la main. Confirmer si c'est intentionnel (ex. "Centre de notifications", "Audit migration").
- **Équipements désactivés anciens** : souvent des équipements remplacés. Proposer un nettoyage uniquement si le PO demande.
- **Variables locales vs globales** : une variable locale (`link_id > 0`) n'est accessible que depuis son scénario. Si elle ressemble à une globale orpheline mais est locale, ce n'est pas une anomalie.
- **Historique archivé** : `historyArch` contient les données compressées anciennes — ne pas confondre une commande "sans données récentes" avec une commande sans historique du tout.
