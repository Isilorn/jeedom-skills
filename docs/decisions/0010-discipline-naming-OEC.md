# ADR 0010 : Discipline `#[O][E][C]#` — chaîne 4 couches

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D6.3, D4.3)

## Contexte

Dans Jeedom, les commandes sont référencées en interne par des IDs numériques (`#15663#`). La restitution de ces IDs bruts à l'utilisateur est illisible et non actionnable. Il faut décider d'une convention de résolution systématique.

## Options considérées

- **Option A — IDs bruts** : restituer les IDs tels quels. ➕ Simple, aucun risque d'erreur de résolution. ➖ Illisible, non actionnable par l'utilisateur.
- **Option B — Noms courts** : résoudre vers le nom de la commande uniquement. ➕ Plus lisible. ➖ Ambigu si plusieurs commandes ont le même nom dans des équipements différents.
- **Option C — `#[Objet][Équipement][Commande]#`** : convention Jeedom native, chemin complet sans ambiguïté. ➕ Correspond exactement à ce que l'utilisateur voit dans l'UI Jeedom, non ambigu, réutilisable directement dans les expressions de scénario. ➖ Plus long, résolution nécessite une jointure SQL ou API.

## Décision

**Option C — Convention `#[Objet][Équipement][Commande]#`**, imposée via une chaîne de 4 couches :

1. **Instructions explicites SKILL.md §10** : "Toute restitution utilise `#[Objet][Équipement][Commande]#`. Aucun ID brut. Si un ID n'est pas résolu, mentionner explicitement."
2. **Script `resolve_cmd_refs.py`** : tout texte destiné à l'utilisateur passe par lui. Signale les `unresolved_ids`.
3. **Exemples disciplinés** dans `references/audit-templates.md` et `examples/` — pas un seul `#\d+#` brut.
4. **Validation post-hoc dans les évals** : test automatique — pas d'occurrence de `#\d+#` non encadrée dans la sortie attendue.

**Tags système préservés intacts** (`_common/tags.py`) : `#trigger_id#`, `#trigger_value#`, `#trigger_name#`, `#user_connect#`, `#sunset#`, `#sunrise#`, `#time#`.

## Conséquences

- ✅ Restitution toujours lisible et actionnable par l'utilisateur
- ✅ Correspond exactement à ce que l'utilisateur voit dans l'UI Jeedom
- ✅ Pas d'ambiguïté même si plusieurs commandes ont le même nom
- ⚠️ La résolution nécessite des requêtes SQL supplémentaires (batch pour minimiser l'impact)
- ⚠️ Les IDs non résolvables doivent être signalés explicitement (jamais ignorés)
- 🔗 PLANNING §3.15, `scripts/resolve_cmd_refs.py` (J2)
