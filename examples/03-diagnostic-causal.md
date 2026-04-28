---
id: accept-03
titre: Forensique causale — agendas bureau actifs simultanément
workflow: WF13 + WF5 + WF12
statut: ✅ validé
---

# Cas d'acceptation 03 — Forensique causale (WF13)

## Prompt utilisateur

> "Les agendas du bureau de Bob et du bureau Alice sont "indépendants" des autres.
> Je m'explique, les autres agendas sont tous passés en mode "absent" quand la maison
> elle-même passe en mode "absent" et présent quand le mode "absent" de la maison est
> désactivé. Le passage de l'agenda du bureau de Bob et celui du bureau Alice en mode
> "absent" ne dépend que de nos absences respectives. J'ai remarqué que j'arrivais à
> des cas où pour l'un des bureaux j'avais l'agenda absent et l'agenda présent activés
> simultanément."

Description comportementale pure — aucun ID ni nom de scénario fourni.

## Prérequis

- Accès SSH+MySQL configuré
- Scénarios de présence/absence Alice et Bob, scénarios mode Absent, scénario Invités

## Ce que la skill doit faire

1. Partir de la description comportementale (pas d'ID fourni)
2. Identifier les scénarios candidats par leur nom
3. Explorer les chaînes d'appel pour tracer quand les agendas bureau sont activés
4. Comparer les conditions d'activation entre les deux bureaux
5. Trouver le point de couplage involontaire
6. Étayer chaque affirmation par une donnée DB lue

## Critères de validation

- [x] La skill part du symptôme décrit et identifie les scénarios pertinents sans aide
- [x] La chaîne d'appel complète est explorée (Mode_Absent_off → Invités → bureaux)
- [x] Le point de bug est identifié avec evidence DB (IDs element, conditions exactes)
- [x] Même bug détecté sur les deux bureaux
- [x] Chaque affirmation étayée par une donnée lue
- [x] Correction UI pas-à-pas avec les conditions exactes à saisir
- [x] Observation annexe bonus (message log incorrect)
- [x] Pas de modification de l'installation

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Jeedom 4.5.3 — Mac → SSH+MySQL | ✅ PASS | Cause racine trouvée, 2 bugs identifiés, ~11 min 41 s |

## Sortie réelle (sanitisée)

```
> Les agendas du bureau de Bob et du bureau Alice sont "indépendants" des autres.
  [...]
  J'ai remarqué que j'arrivais à des cas où pour l'un des bureaux j'avais l'agenda
  absent et l'agenda présent activés simultanément.

⏺ C'est une investigation de cohérence d'état — je vais cartographier tous les
  scénarios qui touchent ces agendas pour identifier les chemins qui peuvent laisser
  deux agendas actifs simultanément.

  [Exploration multi-étapes : recherche dans scenarioExpression → remontée
   scenarioSubElement → scenarioElement → scenario → analyse Mode_Absent_off
   → analyse scénario Invités → résolution commandes présence]

---
WF13 — Forensique causale : bureaux Alice et Bob, agendas simultanément actifs

Cause racine identifiée

Scénario Invités (14), éléments 71 (Bureau Alice) et 65 (Bureau Bob) —
condition incomplète.

Ces blocs activent Agenda_normal des bureaux en vérifiant uniquement le mode maison,
sans vérifier la présence individuelle.

---
Chemin d'exécution qui provoque le bug

Mode_Absent_off (scénario 13)
  └─ élément 431 : désactive agendas absents des autres pièces
  │    ├─ élément 527 : SI #[Maison][Invites Bureau Alice][Etat] == 1
  │    │               → désactive Agenda_absent(Bureau Alice)
  │    │   ↳ si Alice est individuellement absente et sans invités :
  │    │     condition ÉCHOUE → Agenda_absent reste ACTIF  ←  le verrou tient
  └─ élément 74 : démarre scénario Invités (14)  ← ici ça déraille

Scénario Invités (14)
  └─ élément 68 : SI #[Maison][Invites Bureau Alice][Etat] == 1
       SINON (pas d'invités dans le bureau) :
         └─ élément 71 : SI #[Maison][Modes][Mode] == 'Normal'  ← CONDITION INCOMPLÈTE
              ALORS : active Agenda_normal(Bureau Alice)
              ↑ BUG : Alice peut être absente individuellement

Résultat : Agenda_absent activé par Absence Alice + Agenda_normal activé par le
scénario Invités → les deux simultanément actifs.

---
Conditions des scénarios de présence

┌──────────┬────────────────────────────────────────────────────────────┐
│ Personne │                   Commandes de présence                    │
├──────────┼────────────────────────────────────────────────────────────┤
│ Alice    │ #[Maison][Presence Alice][Shelly]# OU #[Maison][...][Réseau]# │
├──────────┼────────────────────────────────────────────────────────────┤
│ Bob      │ #[Maison][Presence Bob][Shelly]# OU #[Maison][...][Réseau]# │
└──────────┴────────────────────────────────────────────────────────────┘

---
Même bug pour Bureau Bob

Scénario Invités (14)
  └─ élément 64 : SI #[Maison][Invites Bureau Bob][Etat] == 1
       SINON :
         └─ élément 65 : SI #[Maison][Modes][Mode] == 'Normal'  ← même condition incomplète
              ALORS : active Agenda_normal(Bureau Bob)           ← BUG idem

---
Actions recommandées (UI uniquement)

🔴 Correction principale — scénario "Invités" (14)

Modification 1 — Bloc IF élément 71 (Bureau Alice)

1. Aller dans Outils → Scénarios → Invités
2. Localiser le bloc IF dont la condition est
   #[Maison][Modes][Mode]# == 'Normal'
   dans la branche SINON du bloc "Invités Bureau Alice"
3. Remplacer la condition par :
   #[Maison][Modes][Mode]# == 'Normal'
   ET (#[Maison][Presence Alice][Shelly]# == 1 OU #[Maison][Presence Alice][Réseau]# == 1)
4. Sauvegarder

Modification 2 — Bloc IF élément 65 (Bureau Bob)

1. Même scénario "Invités", localiser le bloc IF #[Maison][Modes][Mode]# == 'Normal'
   dans la branche SINON du bloc "Invités Bureau Bob"
2. Remplacer par :
   #[Maison][Modes][Mode]# == 'Normal'
   ET (#[Maison][Presence Bob][Shelly]# == 1 OU #[Maison][Presence Bob][Réseau]# == 1)
3. Sauvegarder

Vérification : après correction — Alice quitte la maison (Agenda_absent actif)
→ invités arrivent puis repartent de son bureau → Agenda_normal ne doit PAS s'activer.
Seule la présence physique d'Alice doit déclencher Agenda_normal.

---
Observation annexe

Dans Mode_Normal_on (scénario 10), un message de log est incorrect : la condition
teste #[Maison][Invites Bureau Alice][Etat]# == 1 (invités présents) mais le log dit
"Pas d'invités dans le bureau de Alice, activation de l'agenda normal" — c'est l'inverse.
Ce n'est pas un bug fonctionnel, mais il masque la logique lors d'un débogage.
```

## Observation technique

La skill a remonté la chaîne causale sur 4 niveaux d'imbrication (Mode_Absent_off →
Invités → élément IF → condition) en multipliant les requêtes SQL de remontée
(`scenarioExpression → scenarioSubElement → scenarioElement → scenario`). Exécution
longue (~11 min 41 s) due à la profondeur de l'exploration par tâtonnements successifs.

L'observation annexe (log incorrect dans Mode_Normal_on) n'avait pas été demandée —
détectée comme sous-produit de l'analyse. Signe que la skill lit réellement les données
plutôt que de se contenter de répondre à la question posée.
