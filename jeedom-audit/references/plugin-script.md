# Référence plugin — Script (`script`)

**Version testée** : compatible Jeedom ≥ 4.3 — non présent sur la box de référence (0 eqLogic)
**Catégorie** : Programming — Daemon : aucun — Dépendances système : selon le type de script

---

## 1. Identification

Le plugin Script permet d'exécuter des scripts shell, PHP ou de récupérer des données via des URLs (HTTP/HTTPS). Il est utilisé pour intégrer des sources de données ou des actionneurs non couverts par d'autres plugins.

Usages typiques :
- **Appel d'API externe** — récupération de données météo, prix énergie, etc. via URL JSON/XML
- **Script shell** — exécution de commandes système ou de scripts sur la box
- **Script PHP** — logique métier embarquée côté Jeedom

Identification DB : `eqLogic.eqType_name = 'script'`

**Note** : absent de la box de référence (0 eqLogics). Ce document est basé sur la documentation officielle et la structure attendue du plugin.

---

## 2. Structure eqLogic

| Champ DB | Valeurs typiques | Signification |
|---|---|---|
| `eqType_name` | `script` | type plugin |
| `isEnable` | `0` ou `1` | actif/inactif |
| `isVisible` | `0` ou `1` | visible dans le dashboard |
| `object_id` | référence pièce | objet Jeedom parent |

### Champs clés dans `eqLogic.configuration` (JSON)

| Champ | Valeurs | Rôle |
|---|---|---|
| `autorefresh` | cron (`*/5 * * * *`) ou vide | fréquence de rafraîchissement automatique |

---

## 3. Structure des commandes

Le plugin Script n'a pas de structure de commandes fixe — chaque commande est définie manuellement par l'utilisateur.

### Champs clés dans `cmd.configuration` (JSON)

| Champ | Valeurs | Rôle |
|---|---|---|
| `scriptSyntax` | `script`, `url`, `html`, `xml`, `json` | type de source |
| `script` | chemin ou URL | commande shell, URL ou chemin de script PHP |
| `returnType` | `info`, `action` | type de retour |
| `scriptArgs` | chaîne | arguments passés au script |
| `jsonPath` | expression JSON (ex: `$.temperature`) | extraction dans une réponse JSON |
| `xmlPath` | XPath | extraction dans une réponse XML |
| `htmlPath` | sélecteur CSS | extraction dans une réponse HTML |
| `regexp` | expression régulière | extraction par regex sur la sortie brute |

### Types `scriptSyntax`

| Valeur | Comportement |
|---|---|
| `script` | exécute un fichier shell ou PHP sur la box — `cmd` = chemin absolu |
| `url` | effectue une requête HTTP GET vers une URL — `cmd` = URL |
| `html` | parse la réponse HTML d'une URL via sélecteur CSS |
| `xml` | parse la réponse XML d'une URL via XPath |
| `json` | parse la réponse JSON d'une URL via `jsonPath` |

### Commandes action

Les commandes de type `action` exécutent le script avec les arguments définis. Elles n'ont pas de valeur de retour stockée.

---

## 4. Points d'audit

**Anti-patterns fréquents :**
- Scripts référençant des chemins absolus qui n'existent plus sur le filesystem
- URLs cibles devenues injoignables (API tierce disparue, IP changée)
- `autorefresh` cron très fréquent (ex: `* * * * *`) sur des scripts lents → accumulation de processus zombie
- Scripts shell avec credentials en clair dans les arguments (`scriptArgs`)

**Requête — eqLogics script actifs :**
```sql
SELECT e.id, e.name, e.configuration
FROM eqLogic e
WHERE e.eqType_name = 'script'
  AND e.isEnable = 1
```

**Requête — commandes script avec leur source :**
```sql
SELECT c.id, c.name, c.type,
       JSON_UNQUOTE(JSON_EXTRACT(c.configuration, '$.scriptSyntax')) AS syntax,
       JSON_UNQUOTE(JSON_EXTRACT(c.configuration, '$.script')) AS source
FROM cmd c
JOIN eqLogic e ON e.id = c.eqLogic_id
WHERE e.eqType_name = 'script'
```

---

## 5. Interactions scénarios

Les commandes info du plugin Script peuvent être utilisées comme déclencheurs ou conditions dans les scénarios (mise à jour de valeur → déclenchement). Les commandes action peuvent être appelées depuis les blocs action d'un scénario.

---

## 6. Daemon

Aucun daemon — le plugin exécute les scripts à la demande ou via le cron Jeedom selon `autorefresh`. Pas de statut daemon à vérifier.

---

## 7. Sécurité / lecture seule

**Attention** : le champ `cmd.configuration.script` peut contenir des credentials en clair (URL avec token, chemin de script avec mot de passe dans les arguments). Ce champ doit être inclus dans le filtrage `filter_rows` si des scripts sensibles sont présents.

`filter_rows` signale le champ `script` de `cmd.configuration` comme potentiellement sensible pour ce plugin.

---

## 8. Patterns de log

Fichier : `/var/www/html/log/script`

Patterns observés :
```
[TIMESTAMP][INFO] : Début d'activation du plugin
[TIMESTAMP][INFO] : Info sur le démon : {"launchable":"nok","state":"nok"}
[TIMESTAMP][ERROR] : Erreur lors de l'exécution du script <chemin> : <message>
[TIMESTAMP][ERROR] : Impossible de joindre l'URL : <url>
```

Le log `script` est principalement alimenté lors des activations/désactivations et des erreurs d'exécution. Les exécutions normales sont silencieuses.

---

## 9. Liens

- Documentation officielle : https://doc.jeedom.com/fr_FR/plugins/programming/script/
- Changelog : https://doc.jeedom.com/fr_FR/plugins/programming/script/changelog
