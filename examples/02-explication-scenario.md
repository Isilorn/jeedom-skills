---
id: accept-02
titre: Explication pas-à-pas d'un scénario complexe
workflow: WF5
statut: ✅ validé
---

# Cas d'acceptation 02 — Explication de scénario (WF5)

## Prompt utilisateur

> "explique-moi ce que fait le scénario Présence Alice étape par étape"

## Prérequis

- Accès SSH+MySQL configuré
- Scénario de présence avec triggers et appels de scénarios imbriqués

## Ce que la skill doit faire

1. Identifier le scénario par son nom (désambiguïsation si plusieurs résultats)
2. Exécuter `scenario_tree_walker.py`
3. Résoudre tous les `#ID#` via requêtes DB
4. Produire un pseudo-code lisible + tableau des effets de bord

## Critères de validation

- [x] Désambiguïsation présentée avec triggers pour choisir
- [x] Tous les `#ID#` résolus en `#[Objet][Équipement][Commande]#`
- [x] Structure SI/SINON/ALORS correcte et lisible
- [x] Appels de scénarios identifiés par nom (pas juste l'ID)
- [x] Aucune référence `#123#` brute dans la sortie
- [x] Tableau des effets de bord en fin de réponse

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Jeedom 4.5.3 — Mac → SSH+MySQL | ✅ PASS | 3 scénarios trouvés → désambiguïsation → pseudo-code complet |
| 2026-04-28 | Jeedom 4.5.3 — Linux dev | ✅ PASS | Référence J2 |

## Sortie réelle (sanitisée)

```
> explique-moi ce que fait le scénario Présence Alice étape par étape

⏺ Trois scénarios correspondent à "Présence Alice". Lequel souhaitez-vous ?

┌───┬──────────────────────────────────┬────────────────────────────────────────────────────┐
│ # │               Nom                │                   Déclenché par                    │
├───┼──────────────────────────────────┼────────────────────────────────────────────────────┤
│ 1 │ "Presence Alice" (ID 4)          │ #[Maison][Presence Alice][Shelly]#                 │
│   │                                  │ ou #[Maison][Presence Alice][Réseau]#              │
├───┼──────────────────────────────────┼────────────────────────────────────────────────────┤
│ 2 │ "Présence Alice Shelly" (ID 70)  │ #[Bluetooth][Présence Shelly Alice][present]#      │
├───┼──────────────────────────────────┼────────────────────────────────────────────────────┤
│ 3 │ "Presence bureau Alice" (ID 74)  │ #[Owon][Owon bureau Alice][Présence]#              │
│   │                                  │ ou #[Aqara][Presence2Alice][presence]#             │
└───┴──────────────────────────────────┴────────────────────────────────────────────────────┘

> 1

⏺ Je parcours l'arbre complet du scénario.
  [scenario_tree_walker.py + résolution des IDs]

---
Scénario "Presence Alice" (ID 4)

Mode : provoke — se déclenche sur changement de valeur
Triggers :
- #[Maison][Presence Alice][Shelly]# (détection Shelly)
- #[Maison][Presence Alice][Réseau]# (détection réseau)

Vue d'ensemble
Ce scénario est le chef d'orchestre de la présence d'Alice à domicile.
À chaque changement d'un capteur, il décide si Alice vient d'arriver
ou de partir : mise à jour du virtuel de présence, notification Discord,
gestion de l'agenda bureau.

Pseudo-code

DÉCLENCHEUR : [Maison][Presence Alice][Shelly] change
           OU [Maison][Presence Alice][Réseau] change

SI [Maison][Presence Alice][Shelly] == 1
OU [Maison][Presence Alice][Réseau] == 1
│
│  ── Alice est détectée présente ──
│
│  SI [Maison][Presence Alice][Presence] == 0   ← elle était absente
│  │
│  │  1. Action  → exécute [Maison][Presence Alice][Present]
│  │  2. Variable → PresentAlice = date et heure courante
│  │  3. Variable → message = "Alice présente à HH:MM. (XX m)"
│  │  4. Scénario → "Centre de notifications" [start]
│  │
│  │  SI [Bureau Alice][Invites Bureau Alice][Etat] == 0   ← pas d'invités
│  │  │  5. Équipement → désactive "Agenda_absent" (Bureau Alice)
│  │  │  SI [Maison][Modes][Mode] == 'Vacances'
│  │  │  │   6. Équipement → active "Agenda_conges"
│  │  │  SINON
│  │  │      6. Équipement → active "Agenda_normal"
│  │
│  SINON   ← Alice était déjà présente → rien

SINON
│  ── Alice est détectée absente ──
│  1. Variable → NbAbsAlice = 0
│  2. Scénario → "Absence Alice" [start]

Effets de bord

┌────────────────────────────────────────┬──────────────────────────────────────────────────┐
│           Élément modifié              │                    Condition                     │
├────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ [Maison][Presence Alice][Present]      │ Arrivée + était absente                          │
│ Variable PresentAlice                  │ Arrivée + était absente                          │
│ Discord canal "Logs"                   │ Arrivée + était absente                          │
│ Agenda_absent désactivé                │ Arrivée + était absente + pas d'invités          │
│ Agenda_conges ou Agenda_normal activé  │ Arrivée + était absente + pas d'invités + mode   │
│ Variable NbAbsAlice = 0               │ Départ détecté                                   │
│ Scénario "Absence Alice" démarré      │ Départ détecté                                   │
└────────────────────────────────────────┴──────────────────────────────────────────────────┘
```
