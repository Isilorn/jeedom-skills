# ADR 0016 : Tests sur box réelle exécutés par Claude Code via SSH

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : clarification PO en session J0 — amendement à PLANNING §0.2.e

## Contexte

Le brief initial (PLANNING §0.2.e) listait "Validation sur box réelle" comme une matière physique que le PO devait fournir, avec la mention "tests live impossibles côté Claude Code". Cette formulation supposait que Claude Code ne pouvait pas exécuter de commandes SSH.

En pratique, Claude Code dispose d'un accès bash et peut exécuter des commandes SSH si l'alias est configuré. Le PO a confirmé vouloir que Claude Code réalise les tests directement sur sa box, et non simplement les décrire pour que le PO les exécute.

## Options considérées

- **Option A — PO exécute les tests** (formulation du brief) : Claude Code produit les scripts, le PO les exécute sur sa box et rapporte les résultats. ➕ Claude Code ne touche pas directement la box. ➖ Friction, cycle de validation plus long, informations filtrées via le rapport PO.
- **Option B — Claude Code exécute via SSH** : Claude Code exécute directement les commandes SSH quand l'alias est configuré. ➕ Tests plus rapides, résultats directs, moins de friction. ➖ Nécessite que les credentials SSH soient disponibles dans l'environnement Claude Code.

## Décision

**Option B — Claude Code exécute les tests via SSH sur la box du PO.**

Prérequis : alias SSH `Jeedom` configuré dans `~/.ssh/config` côté machine Claude Code, credentials MySQL via la stratégie ADR 0004 (`remote_mycnf` recommandé).

La posture reste lecture seule absolue (ADR 0006) : aucune écriture, toutes les commandes exécutées sont des SELECT ou des lectures de fichiers via SSH.

**Ce qui reste à fournir par le PO** :
- Captures d'écran Jeedom (UI — Claude Code ne navigue pas dans l'interface graphique)
- Sanity check de sanitisation des fixtures (l'œil humain qui connaît son install)
- Validation des résultats des tests (confirmation que le comportement observé est correct)

## Conséquences

- ✅ Cycle de tests plus court : Claude Code exécute, PO valide les résultats
- ✅ Résultats directs sans filtrage par le rapport PO
- ⚠️ Nécessite une configuration SSH opérationnelle avant J1 (checklist à préparer)
- ⚠️ La lecture seule reste absolue — aucune commande modifiante via SSH
- 🔗 ADR 0004 (credentials), ADR 0006 (lecture seule)

## Amendement au PLANNING

PLANNING §0.2.e mentionnait "tests live impossibles côté Claude Code" — formulation incorrecte. Ce document fait foi ; le PLANNING n'est pas modifié (la décision ici le supersède pour ce point).
