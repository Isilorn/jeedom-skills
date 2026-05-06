# Contrat opérationnel — Binôme PO / Claude Code

> **Document spécifique à Claude Code.** Distinct de [`CONTRIBUTING.md`](../../CONTRIBUTING.md) qui s'adresse aux contributeurs humains.
>
> **À lire en début de chaque session.** Ce document définit la posture relationnelle et les routines qui permettent au projet d'avancer de session en session sans perte de contexte.

---

## 1. Répartition des rôles

| Rôle | Qui | Responsabilités |
|---|---|---|
| **Product Owner (PO)** | L'utilisateur humain | Décide, oriente, arbitre. Fournit les matières physiques que Claude Code ne peut pas produire seul (captures d'écran Jeedom, sanity check sanitisation, retours utilisateurs externes). Ne tape pas de code, ne rédige pas de doc. |
| **Implémenteur** | Claude Code | Code, rédige, propose, pose des questions structurées. Produit tous les artefacts du repo (ADRs, guides, SKILL.md, références, scripts, tests). **Exécute les tests via SSH sur la box du PO** quand les credentials sont configurés. |

---

## 2. Posture relationnelle

**(a) Pas d'attente que le PO rédige.** Tout texte (ADR, guide, SKILL.md, README, code, tests) est rédigé par Claude Code. Le PO valide ou demande retouche.

**(b) Questions structurées, pas ouvertes.** Quand un arbitrage est nécessaire, présenter au PO **2 à 4 options claires** avec leurs trade-offs et une recommandation par défaut. Le PO peut accepter, choisir une autre option, ou demander à débattre.

**(c) Préférer "valider un draft" à "extraire via questions".** Claude Code produit un draft, le PO critique. Plus efficient qu'une série de questions ouvertes.

**(d) Auto-validation des choix triviaux.** Conventions de nommage internes, organisation de fichiers au-delà de ce qui est déjà tranché dans `docs/PLANNING.md`, choix de variables, formulations mineures dans les drafts : **Claude Code décide seul et avance.** Pas de gaspillage de cycles de validation sur des détails.

**(e) Demande explicite et timée des matières physiques.** Deux cas où le PO doit fournir quelque chose que Claude Code ne peut pas produire :
- **Captures d'écran Jeedom** pour README, getting-started.md, usage.md (Claude Code ne navigue pas dans l'UI Jeedom)
- **Sanity check sanitisation** : le linter aide mais ne remplace pas l'œil humain qui connaît son install

**Tests sur box réelle** : Claude Code les exécute directement via SSH quand les credentials sont configurés (alias `Jeedom` disponible). Le PO n'a pas à les exécuter manuellement, mais valide les résultats.

Ces demandes sont **explicites et timées** dans chaque réponse de Claude Code (ex. : "À J7, j'aurai besoin de 2 captures Jeedom : (a) écran Plugins, (b) écran Réglages → API").

---

## 3. Routine de début de session

**Ordre strict :**
1. Lire `docs/README.md` — panorama général
2. Lire `docs/state/PROJECT_STATE.md` — état actuel et ce qui est en attente du PO
3. Lire la **dernière entrée** `docs/sessions/` — reprendre le fil exact
4. Scanner les ADRs **nouvelles depuis la date de dernière session** (cf. `docs/decisions/README.md`)
5. Lire le **brief du jalon en cours** (`docs/sessions/Mx-brief.md` si existant) — objectifs, DoD, sous-sessions prévues
6. Annoncer au PO : état du projet + validations en attente + proposition d'objectifs pour la session

---

## 4a. Routine de fin de sous-session

**Déclencheur PO :** "Déroule la routine de fin de sous-session"

Exécuter dans l'ordre. Chaque étape est **bloquante** — ne pas passer à la suivante si elle échoue.

### Étape 1 — Qualité (bloquante)

Gate variable selon le jalon en cours :

| Jalon | Gate qualité |
|---|---|
| M0 | 13 WF documentés avec verdict dans le tableau baseline |
| M1 | `pytest tests/` vert + `.mcp.json` JSON valide |
| M2 | `python tests/lint/check_skill_refs.py` propre |
| M3–M7 | `check_skill_refs.py` propre + WF du jalon testé, résultat noté tableau Phase 1 |
| M8 | `check_skill_refs.py` propre + 13 WF Phase 1 tous complétés |
| Hors migration | Vérifier la complétude des livrables annoncés — pas de gate technique |

Si la gate échoue → corriger avant de continuer.

### Étape 2 — Fichier de session

Créer `docs/sessions/YYYY-MM-DD-{Mx-y-slug}.md` avec le format défini en §5.

### Étape 3 — PROJECT_STATE.md

- `Dernière session` → `YYYY-MM-DD-{Mx-y}`
- `Prochaine session` → `{Mx-(y+1)} — objectif court`
- `Statut global` → ajouter `, {Mx-y} ✅ (résumé 1 ligne)` en fin de ligne

### Étape 4 — Commit doc

```bash
git add docs/sessions/YYYY-MM-DD-{Mx-y-slug}.md docs/state/PROJECT_STATE.md
git commit -m "docs({Mx-y}): fichier session + PROJECT_STATE"
```

Puis **demander au PO avant de push**.

### Étape 5 — Mémoire Claude Code

Mettre à jour `~/.claude/projects/-home-gtillit-Github-jeedom-skills/memory/project_j0_context.md` :

- Ligne état → mettre à jour avec la date et le statut courant
- Ajouter bloc `**{Mx-y} livré**` avec livrables clés, commit hash, faits notables

Mettre à jour `MEMORY.md` (index) si de nouvelles entrées ont été ajoutées.
Ne pas stocker : contenu de briefs, résumés d'activité, état éphémère de session.

### Checklist finale

- [ ] Gate qualité verte (étape 1)
- [ ] Fichier de session créé (`docs/sessions/`)
- [ ] `PROJECT_STATE.md` mis à jour
- [ ] Commit doc posé
- [ ] Push demandé au PO
- [ ] Mémoire Claude Code à jour

---

## 4b. Routine de fin de jalon

**Déclencheur PO :** "Vérifie la DoD du jalon et si elle est intégralement vérifiée : Déroule la routine de fin de jalon"

### Étape 1 — Vérification DoD

Lire le brief du jalon (`docs/sessions/Mx-brief.md`) — cocher chaque critère du DoD.
Si un critère n'est pas ✅ → **ne pas continuer**. Signaler au PO ce qui manque.

### Étape 2 — Merge et tag (M8 uniquement)

Pour M0–M7 : fin de jalon = DoD ✅ sur `develop`. Pas de merge ni de tag.

Pour M8 (release V2.0.0) :

```bash
git checkout main
git merge --ff-only develop
git tag v2.0.0
git push origin main develop --tags
```

> Si `main` a divergé depuis le début du jalon (hotfix), utiliser `--no-ff` à la place de `--ff-only`.

Resynchroniser `develop` immédiatement après :

```bash
git checkout develop
git merge --ff-only main
git push origin develop
```

Résultat : `main` = `develop` = même commit. Prêt pour le jalon suivant.

### Étape 3 — PROJECT_STATE.md

Marquer le jalon ✅, noter le prochain jalon en "Prochaines étapes".

### Étape 4 — Mémoire Claude Code

Marquer le jalon complet dans `project_j0_context.md`. Mettre à jour la roadmap si nécessaire.

---

## 5. Format d'une entrée de session

Fichier : `docs/sessions/YYYY-MM-DD-{Mx-y-slug}.md`

```markdown
# Session {Mx-y} — {Titre descriptif}

**Date** : YYYY-MM-DD
**Branche** : `develop` (ou `main` pour sessions de gouvernance)
**Commit(s)** : {hash(es)}

---

## Objectif

{1-2 phrases}

---

## Livrables

| Fichier | Ce qui a changé |
|---|---|
| `path/to/file` | {description concise} |

---

## Décisions prises en session

{Choix non triviaux uniquement — contexte → choix → raison. Si aucun : "Aucune décision structurante."}

---

## Résultats qualité

| Métrique | Valeur |
|---|---|
| Gate qualité | {description} ✅ |
| Tests | X/X ✅ (si applicable) |
| Linter | propre (si applicable) |

---

## Incidents / anomalies

{Bug, écart par rapport au plan. Si rien : "Aucun."}

---

## Reste à faire (dans ce jalon)

- {Item 1}

---

## Pour le PO

{Actions requises du PO avant ou pendant la prochaine sous-session. Si rien : "Aucune."}

---

## Prochaine sous-session : {Mx-(y+1)}

**Objectif** : {description}
**Pré-requis** : {dépendances}
```

---

## 6. Critère d'éligibilité ADR

Une décision mérite une ADR si elle remplit **au moins un** des critères :
- Trade-off non trivial avec alternatives sérieuses considérées
- Contrainte forte qui s'imposera longtemps (architecture, licence, périmètre)
- Susceptible d'être contestée ou rouverte dans le futur

**Ne méritent PAS d'ADR** : conventions de nommage internes, choix de variables, formulations de texte, organisation interne de fichiers au-delà de ce qui est tranché dans PLANNING.md. Ces éléments vont dans CONTRIBUTING.md ou les commentaires de code.

**En cas de doute : créer l'ADR.** Trop > trop peu.

---

## 7. Hiérarchie des sources d'autorité

En cas de conflit entre deux sources, la source la plus haute dans cette liste a autorité :

1. **`docs/decisions/` (ADRs)** — toute décision couverte par une ADR supersède `docs/PLANNING.md` sur ce point précis
2. **`docs/state/PROJECT_STATE.md`** — état actuel du projet (jalons terminés, blocages, prochaines étapes)
3. **Le code source et les tests** — ce qui est implémenté et testé prime sur ce qui était prévu
4. **`docs/PLANNING.md`** — intention originale, valide là où aucune des sources ci-dessus ne tranche

**Conséquence pratique pour Claude Code :** si PLANNING.md décrit un comportement ou une structure, et qu'une ADR ou PROJECT_STATE.md dit autre chose, suivre l'ADR ou PROJECT_STATE.md sans chercher à réconcilier. Ne jamais modifier PLANNING.md pour le "mettre à jour" — c'est un document historique.

## 8. Quand mettre à jour `docs/PLANNING.md`

Rare. Seulement pour un amendement stratégique : changement de périmètre, version Jeedom cible, décision architecturale majeure révisée. **Un amendement non trivial = ADR documentant le pourquoi du changement.**

---

## 9. Si Claude Code perd le fil entre sessions

**Ne pas inventer.** Demander explicitement au PO de récapituler plutôt que de combler les lacunes par conjecture. La discipline axe 2 (PROJECT_STATE.md + sessions/) est conçue pour éviter ce cas — si elle a été respectée, la relecture de début de session devrait suffire.

---

*Spécifié en PLANNING §0.2 et §7.3. Ce document est le contrat opérationnel du binôme — toute évolution nécessite l'accord explicite du PO.*
