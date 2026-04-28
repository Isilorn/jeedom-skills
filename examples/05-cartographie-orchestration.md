---
id: accept-05
titre: Cartographie d'orchestration inter-scénarios
workflow: WF12
statut: ✅ validé
---

# Cas d'acceptation 05 — Cartographie d'orchestration (WF12)

## Prompt utilisateur

> "trace-moi la chaîne complète d'appels à partir du scénario Mode_Absent_off"

## Prérequis

- Accès SSH+MySQL configuré
- `scenario_tree_walker.py` avec `follow_scenario_calls` opérationnel

## Ce que la skill doit faire

1. Identifier le scénario par son nom
2. Exécuter `scenario_tree_walker.py` avec `follow_scenario_calls=3`, `max_depth=8`
3. Compter les nœuds : >10 → mermaid
4. Résoudre les IDs (scénarios, eqLogics, commandes)
5. Produire le diagramme + prose explicative

## Critères de validation

- [x] Règle >10 nœuds → mermaid appliquée
- [x] Diagramme mermaid syntaxiquement valide
- [x] Cycles détectés et signalés (aucun ici)
- [x] Arêtes conditionnelles labellisées
- [x] Profondeur limite mentionnée en bas de page

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Jeedom 4.5.3 — Mac → SSH+MySQL | ✅ PASS | Arbre très riche, extraction Python adaptée, ~3 min |
| 2026-04-28 | Jeedom 4.5.3 — Linux dev | ✅ PASS | Référence J6 |

## Sortie réelle (sanitisée)

```
> trace-moi la chaîne complète d'appels à partir du scénario Mode_Absent_off

⏺ [scenario_tree_walker.py — scenario_id=13, follow_scenario_calls=3, max_depth=8]
⏺ Arbre très riche → extraction Python des nœuds clés → résolution IDs

---
Cartographie d'orchestration — "Mode_Absent_off" (ID 13)

▎ Point d'entrée : Mode_Absent_off — provoke, trigger manuel ou via API
▎ Profondeur explorée : 2 niveaux — 4 scénarios au total
▎ Cycles détectés : aucun

graph TD
    S13["🎬 Mode_Absent_off\nID 13 · provoke · trigger manuel"]

    %% Bloc 1 — Désactivation inconditionnelle des agendas absents
    S13 -->|"Bloc 1 — inconditionnel"| DA["❌ Désactive Agenda_absent\nCuisine · Salon · Ch. Parents\nCouloir · SdB · Ch. Charlie"]
    S13 -->|"Si invités Bureau Carol == 1"| DA_Carol["❌ Désactive Agenda_absent\nBureau Carol"]
    S13 -->|"Si invités Bureau Alice == 1"| DA_Alice["❌ Désactive Agenda_absent\nBureau Alice"]

    %% Bloc 2 — Routage selon le mode maison
    S13 -->|"Bloc 2 — Mode == 'Normal'"| S10["🎬 Mode_Normal_on\nID 10 · tag GESTABS=1"]
    S13 -->|"Bloc 2 — Mode == 'Vacances'"| S8["🎬 Mode_Vacances_on\nID 8 · tag GESTABS=1"]

    %% Mode_Normal_on
    S10 -->|"invités Bureau Carol == 1"| N_inv_Carol["✅ Agenda_invites Bureau Carol"]
    S10 -->|"PAS invités Ch. Charlie"| N_norm_Char["✅ Agenda_normal Ch. Charlie"]
    S10 -->|"invités Ch. Charlie == 1"| N_inv_Char["✅ Agenda_invites Ch. Charlie"]
    S10 -->|"invités Bureau Alice == 1"| N_inv_Alice["✅ Agenda_invites Bureau Alice"]
    S10 -->|"inconditionnel"| N_norm_multi["✅ Agenda_normal\nCuisine · Couloir · Ch. Parents\nSdB · Salon"]

    %% Mode_Vacances_on
    S8 -->|"PAS invités Carol\n+ Bob présent"| V_cong_Carol["✅ Agenda_conges Bureau Carol"]
    S8 -->|"PAS invités Ch. Charlie"| V_cong_Char["✅ Agenda_conges Ch. Charlie"]
    S8 -->|"PAS invités Alice\n+ Alice présente"| V_cong_Alice["✅ Agenda_conges Bureau Alice"]
    S8 -->|"inconditionnel"| V_cong_multi["✅ Agenda_conges\nCh. Parents · Couloir\nCuisine · SdB · Salon"]

    %% Bloc 3 — Invités + Alarme
    S13 -->|"Bloc 3 — inconditionnel"| S14["🎬 Invites\nID 14 · tag GESTABS=1"]

    S14 -->|"invités Bureau Carol\n(ALORS/SINON + mode)"| I_Carol["Agenda_invites ou\nAgenda_normal/conges\nBureau Carol"]
    S14 -->|"invités Ch. Charlie\n(ALORS/SINON + mode)"| I_Char["Agenda_invites ou\nAgenda_normal/conges\nCh. Charlie"]
    S14 -->|"invités Bureau Alice\n(ALORS/SINON + mode)"| I_Alice["Agenda_invites ou\nAgenda_normal/conges\nBureau Alice"]
    S14 -->|"notification changement"| S20["🎬 Centre de notifications\nID 20"]
    S20 --> DISC["⚡ Discord Modes\nEnvoi message évolué"]

    S13 -->|"après Invites"| ALM_OFF["⚡ [Maison][Maison][Désactiver]\nalarme coupée"]
    S13 -->|"wait 300 s puis"| ALM_AG["✅ Active Agenda_alarme\nMaison"]

---
Lecture de la chaîne

Mode_Absent_off s'exécute en 3 blocs séquentiels :

Bloc 1 — Nettoyage
Désactivation inconditionnelle des Agenda_absent sur toutes les pièces
communes, puis conditionnelle sur les bureaux (si invités présents).

Bloc 2 — Activation selon le mode maison
- 'Normal' → Mode_Normal_on : Agenda_normal ou Agenda_invites par pièce
- 'Vacances' → Mode_Vacances_on : Agenda_conges (bureaux conditionnés
  par présence physique d'Alice et Bob)
Le tag GESTABS=1 force l'activation même si le virtuel maison est "Absent".

Bloc 3 — Invités + réarmement alarme
Invites (ID 14) ajuste les 3 espaces avec invités (ALORS/SINON + mode).
Chaque changement → Centre de notifications → Discord canal Modes.
Puis : alarme désactivée → attente 300 s → Agenda_alarme réactivé.

▎ Limite : profondeur 2 — sous-appels de "Centre de notifications" non explorés.
```

## Observation technique

Sur un arbre très riche, Claude a adapté sa stratégie : extraction Python directe
plutôt que lecture linéaire du JSON. Robuste mais entraîne une exécution de ~3 min.
Les sous-appels de scénarios très larges peuvent nécessiter une limite de profondeur
explicite de l'utilisateur pour rester dans un temps raisonnable.
