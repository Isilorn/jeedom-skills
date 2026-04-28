---
id: accept-08
titre: Plugin tier-générique — statut Discord Link
workflow: WF3/WF4 + tier-générique
statut: ✅ validé
---

# Cas d'acceptation 08 — Plugin tier-générique (WF3/WF4)

## Prompt utilisateur

> "donne-moi le statut du plugin Discord Link"

*(Plugin non couvert en tier-1 — pas de fiche `references/plugin-discordlink.md`)*

## Ce que la skill doit faire

1. Constater l'absence de fiche tier-1 pour ce plugin
2. Appliquer le pattern `plugin-generic-pattern.md` en 4 temps :
   - Identification de surface (eqType_name, nb eqLogics, structure DB)
   - Extraction d'échantillons (1-3 eqLogics + leurs commandes)
   - Inférence Claude assumée explicitement (pas de certitude feinte)
   - Intégration aux workflows standards (santé, daemon, logs, etc.)
3. Analyser les logs daemon du plugin

## Critères de validation

- [x] Plugin non tier-1 traité avec les données DB + API disponibles
- [x] Structure commandes inférée et expliquée (12 action + 3 info par équipement)
- [x] État daemon analysé via logs (absence de statut runtime API signalée)
- [x] Incidents historiques dans les logs identifiés et contextualisés
- [x] Conclusion actionnelle fournie avec recommandation de surveillance

## Résultats

| Date | Environnement | Résultat | Notes |
|---|---|---|---|
| 2026-04-28 | Jeedom 4.5.3 — Mac → SSH+MySQL | ✅ PASS | 11 équipements, daemon OK, incident jan. détecté, ~43 s |

## Sortie réelle (sanitisée)

```
> donne-moi le statut du plugin Discord Link

⏺ Je collecte l'état du plugin en parallèle.
  [api_call.py plugin::listPlugin + db_query.py eqLogics/commandes + logs_query.py]

---
Discord Link — Statut

Plugin

┌─────────────────┬────────────────────────┐
│    Attribut     │         Valeur         │
├─────────────────┼────────────────────────┤
│ Catégorie       │ Communication          │
├─────────────────┼────────────────────────┤
│ Daemon          │ Oui (propre daemon)    │
├─────────────────┼────────────────────────┤
│ Dépendances     │ Oui                    │
├─────────────────┼────────────────────────┤
│ Cron actif      │ Oui (cron + cronDaily) │
├─────────────────┼────────────────────────┤
│ Erreurs système │ 0                      │
└─────────────────┴────────────────────────┘
> Le statut runtime du daemon n'est pas exposé par l'API — l'état réel se lit
  dans les logs ci-dessous.

---
Équipements (11) — tous actifs ✅

┌─────────────────────┬───────────────┐
│     Équipement      │     Objet     │
├─────────────────────┼───────────────┤
│ Discord Alarme      │ Communication │
├─────────────────────┼───────────────┤
│ Discord Alertes     │ Communication │
├─────────────────────┼───────────────┤
│ Discord Chat        │ Communication │
├─────────────────────┼───────────────┤
│ Discord Fenêtres    │ Communication │
├─────────────────────┼───────────────┤
│ Discord Logs        │ Communication │
├─────────────────────┼───────────────┤
│ Discord Machines    │ Communication │
├─────────────────────┼───────────────┤
│ Discord Médicaments │ Communication │
├─────────────────────┼───────────────┤
│ Discord Modes       │ Communication │
├─────────────────────┼───────────────┤
│ Discord Monitoring  │ Communication │
├─────────────────────┼───────────────┤
│ Discord Poubelles   │ Communication │
├─────────────────────┼───────────────┤
│ Discord Test        │ Communication │
└─────────────────────┴───────────────┘

Structure identique sur chacun : 12 commandes action (Envoi message, Envoi message
évolué, Envoi TTS, Envoi fichier, Résumé général, Résumé par objet, Résumé des
batteries, État des démons, État des dépendances, Supprime les messages, Centre de
messages, Dernière Connexion utilisateur) + 3 commandes info (Dernier message,
Avant dernier message, Avant avant dernier message).

---
Logs daemon

3 événements :

┌──────────────────────────┬─────────────────────────────────────────────┬──────────────────────────────────────────────────────┐
│           Date           │                    Erreur                   │                      Analyse                         │
├──────────────────────────┼─────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ 2025-12-17 22:50         │ deamon_start — MySQL connection killed       │ Redémarrage MySQL. Ponctuel, normal.                 │
├──────────────────────────┼─────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ 2026-01-03 13:45 → 14:40 │ "démon relancé plus de 3 fois              │ ⚠️ Incident daemon : boucle de crash/restart          │
│                          │  consécutivement" (×12 sur 55 min)          │ pendant ~1 heure. Résolu spontanément ou manuellement.│
├──────────────────────────┼─────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
│ 2026-04-16 19:40         │ deamon_start — MySQL connection killed       │ Redémarrage MySQL. Ponctuel, normal.                 │
└──────────────────────────┴─────────────────────────────────────────────┴──────────────────────────────────────────────────────┘

---
Conclusion

✅ Discord Link est opérationnel à ce jour. Le daemon fonctionne (les scénarios
envoient activement des messages sur tous les canaux), aucune erreur système en
base, pas de log d'erreur depuis le 16 avril (redémarrage MySQL banal).

⚠️ Point à surveiller : l'incident du 3 janvier (daemon en boucle pendant 55 min)
n'a pas eu d'explication visible dans les logs. Si le phénomène se répète, vérifier
dans Plugins → Discord Link → Dépendances que toutes les dépendances Python sont à
jour, et consulter le log discordlink_dep.
```

## Observation technique

La skill ne dispose pas de fiche tier-1 pour Discord Link, mais applique le pattern
générique de façon fluide : API pour les métadonnées plugin, DB pour les eqLogics et
commandes, `logs_query.py` pour le daemon. L'incident du 3 janvier a été détecté et
contextualisé sans intervention manuelle. Exécution en ~43 s.
