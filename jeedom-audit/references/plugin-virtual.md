# Référence plugin — Virtuel (`virtual`)

**Version testée** : compatible Jeedom ≥ 4.3 — testé sur Jeedom 4.5.3 (box réelle, 2026-04-27)
**Catégorie** : Programming — Daemon : aucun — Dépendances système : aucune

---

## 1. Identification

Le plugin Virtuel permet de créer des équipements et commandes sans matériel physique. Usages typiques sur la box de référence (35 eqLogics) :

- **Interrupteurs virtuels** — états On/Off pilotés par scénarios (présence, modes)
- **Agrégateurs** — commandes info dont la valeur est calculée (`calcul`) à partir d'autres commandes
- **Consignes** — valeurs numériques ou texte modifiées manuellement ou par scénario
- **Objets de mode** — état binaire représentant un mode de la maison (Absent, Vacances, etc.)

Identification DB : `eqLogic.eqType_name = 'virtual'`

---

## 2. Structure eqLogic

| Champ DB | Valeurs typiques | Signification |
|---|---|---|
| `eqType_name` | `virtual` | type plugin |
| `isEnable` | `1` (tous actifs sur box de réf.) | actif/inactif |
| `isVisible` | `0` ou `1` | visible dans le dashboard |
| `object_id` | référence pièce | objet Jeedom parent |

Pas de configuration plugin spécifique dans `eqLogic.configuration` — tout est dans les commandes.

---

## 3. Structure des commandes

### Pattern interrupteur (le plus fréquent)

```
cmd info/binary    "Etat"       logicalId=""   configuration.virtualAction=1
cmd action/other   "On"         logicalId=""   configuration.virtualAction="1", infoId=<id Etat>, value="1"
cmd action/other   "Off"        logicalId=""   configuration.virtualAction="1", infoId=<id Etat>, value="0"
cmd action/other   "Rafraichir" logicalId="refresh"
```

### Champs clés dans `cmd.configuration` (JSON)

| Champ | Rôle |
|---|---|
| `virtualAction` | `1` = commande liée à une action virtuelle |
| `infoId` | id de la commande info mise à jour par cette action |
| `value` | valeur écrite sur `infoId` lors de l'exécution |
| `calcul` | expression de calcul pour les commandes info agrégées (ex: `#[O][E][cmd1]# + #[O][E][cmd2]#`) |
| `returnStateValue` | valeur retournée après exécution d'une action (rarement renseigné) |
| `updateCmdId` | id d'une commande externe mise à jour en cascade |

### Pattern commande calculée

```
cmd info/numeric   "Consigne"   logicalId=""
  configuration.calcul = "#[Maison][Config][consigne_base]# + 0.5"
```

La valeur est recalculée à chaque `Rafraichir` ou mise à jour de la commande source.

---

## 4. Points d'audit

**Anti-patterns fréquents :**
- Commande `Etat` sans `infoId` renseigné dans les actions On/Off → les actions n'écrivent nulle part
- `calcul` référençant un `#ID#` d'une commande supprimée → valeur bloquée ou erreur silencieuse
- eqLogic virtual sans aucune commande info → dashboard vide, inutile

**Requête utile — virtuels sans commande info :**
```sql
SELECT e.id, e.name
FROM eqLogic e
LEFT JOIN cmd c ON c.eqLogic_id = e.id AND c.type = 'info'
WHERE e.eqType_name = 'virtual'
GROUP BY e.id
HAVING COUNT(c.id) = 0
```

**Requête utile — actions virtuelles sans infoId :**
```sql
SELECT c.id, c.name, e.name AS eqLogic_name
FROM cmd c
JOIN eqLogic e ON e.id = c.eqLogic_id
WHERE e.eqType_name = 'virtual'
  AND c.type = 'action'
  AND c.logicalId != 'refresh'
  AND (c.configuration NOT LIKE '%"infoId"%'
       OR c.configuration LIKE '%"infoId":""%')
```

---

## 5. Interactions scénarios

Les commandes action virtual sont les cibles les plus courantes dans les scénarios :
- `#[Maison][Absence][On]#` — déclenche l'action On
- `#[Maison][Absence][Etat]#` — lit l'état

Dans WF5 (arbre scénario), les références `#[O][E][C]#` vers des commandes virtual apparaissent fréquemment dans les conditions et les blocs action.

---

## 6. Daemon

Aucun daemon — le plugin est purement en mémoire. Pas de statut daemon à vérifier.

---

## 7. Sécurité / lecture seule

Aucune donnée sensible dans `cmd.configuration` pour le plugin virtual. `filter_rows` ne redacte rien sur ce type.

---

## 8. Patterns de log

Les virtuels n'ont pas de fichier log dédié. Les actions sur commandes virtuelles apparaissent dans `/var/www/html/log/scenario` lors des exécutions de scénarios qui les déclenchent.

---

## 9. Liens

- Documentation officielle : https://doc.jeedom.com/fr_FR/plugins/programming/virtual/
- Changelog : https://doc.jeedom.com/fr_FR/plugins/programming/virtual/changelog
