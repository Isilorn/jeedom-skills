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
5. Annoncer au PO : état du projet + validations en attente + proposition d'objectifs pour la session

---

## 4. Routine de fin de session significative

**Ordre strict :**
1. Mettre à jour `docs/state/PROJECT_STATE.md` (sections "Ce qui marche", "En cours", "Prochaines étapes", "En attente du PO")
2. Créer une entrée `docs/sessions/YYYY-MM-DD-<sujet>.md` avec les sections définies en §5
3. Créer les ADR(s) pour les décisions non triviales de la session (cf. critère §6)
4. Marquer les TODOs traçables dans le code : `# TODO(jalon-JX): <description>`
5. Commit avec message clair

---

## 5. Format d'une entrée de session

Fichier : `docs/sessions/YYYY-MM-DD-<sujet>.md`

```markdown
# Session YYYY-MM-DD — <sujet court>

## Objectif de la session
[1-2 phrases]

## Décisions prises pendant la session
- [Décision 1] : [rationale court]
- [Décision 2] : ...

## Découvertes / surprises
[Tout ce qui était inattendu ou qui a modifié la compréhension]

## Travail réalisé
- [Fichier ou fonctionnalité 1]
- ...

## Reste à faire (dans ce jalon)
- [Item 1]
- ...

## Pour la prochaine session
[Phrase claire sur par où commencer — ex. "Reprendre depuis logs_query.py:42 (TODO marqué)"]

## Pour le PO
[Actions requises du PO avant ou pendant la prochaine session]
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

## 7. Quand mettre à jour `docs/PLANNING.md`

Rare. Seulement pour un amendement stratégique : changement de périmètre, version Jeedom cible, décision architecturale majeure révisée. **Un amendement non trivial = ADR documentant le pourquoi du changement.**

---

## 8. Si Claude Code perd le fil entre sessions

**Ne pas inventer.** Demander explicitement au PO de récapituler plutôt que de combler les lacunes par conjecture. La discipline axe 2 (PROJECT_STATE.md + sessions/) est conçue pour éviter ce cas — si elle a été respectée, la relecture de début de session devrait suffire.

---

*Spécifié en PLANNING §0.2 et §7.3. Ce document est le contrat opérationnel du binôme — toute évolution nécessite l'accord explicite du PO.*
