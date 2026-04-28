---
title: Troubleshooting — jeedom-audit
audience: utilisateur en difficulté
---

# Troubleshooting

## Connexion SSH

### "Permission denied" ou "Connection refused"

- Vérifiez que l'alias SSH est correct dans `~/.ssh/config`
- Testez manuellement : `ssh Jeedom "echo ok"`
- Vérifiez que votre clé SSH est autorisée sur la box (`~/.ssh/authorized_keys` côté box)

### "Host key verification failed"

```bash
ssh-keyscan -H <IP-box> >> ~/.ssh/known_hosts
```

---

## Connexion MySQL

### "Access denied for user 'jeedom_audit_ro'"

- Vérifiez que l'utilisateur MySQL existe : `mysql -u jeedom_audit_ro -p`
- Vérifiez que `~/.my.cnf` est dans le home de votre user SSH (pas `/root/`)
- Vérifiez les permissions : `chmod 600 ~/.my.cnf`

### "Can't connect to MySQL server"

- Le daemon MySQL est-il démarré ? `sudo systemctl status mysql`
- L'utilisateur est-il autorisé depuis `localhost` ? (pas depuis une IP distante en V1)

### "Table 'jeedom.XXX' doesn't exist"

La skill cible Jeedom 4.5.x. Si votre version est différente, le schéma DB peut diverger. Ouvrez une [issue GitHub](https://github.com/Isilorn/jeedom-skills/issues) avec votre version Jeedom exacte.

---

## Mode API-only {#api-only}

Si vous n'avez pas SSH, la skill fonctionne en mode API-only mais avec des limitations :

| Ce qui est limité | Raison | Contournement |
|---|---|---|
| Logs indisponibles (WF2, WF13) | Logs sur disque — non accessibles via API | Configurer SSH |
| WF13 (forensique) | Requiert les logs | Configurer SSH |
| Résolution `#ID#` partielle | `cmd::byId` seul disponible | Configurer SSH pour accès DB complet |

Pour activer le mode API-only explicitement :

> "Configure jeedom-audit en mode API uniquement"

---

## La skill ne se charge pas

- Vérifiez que le mode `run` est activé dans Claude Code
- Vérifiez que le fichier `.skill` est dans le bon dossier (`~/.claude/skills/`)
- Redémarrez Claude Code

---

## "Je ne trouve pas le scénario / l'équipement"

La recherche est par nom approché (`LIKE '%terme%'`). Si plusieurs résultats, Claude demande une désambiguïsation.

Conseils :

- Utilisez le nom exact de l'équipement tel qu'il apparaît dans Jeedom
- Évitez les abréviations — le nom doit correspondre à ce qui est dans la DB
- Si l'équipement est dans un objet spécifique, précisez : "l'équipement Thermostat dans l'objet Bureau"

---

## "Les `#ID#` ne sont pas résolus"

Si des IDs numériques bruts apparaissent dans la sortie :

1. Vérifiez que `resolve_cmd_refs.py` est accessible (mode SSH+MySQL recommandé)
2. En mode API-only, la résolution est partielle (seule `cmd::byId` est disponible)
3. Ouvrez une issue si le problème persiste en mode SSH+MySQL

---

## "La skill refuse de faire une modification"

C'est le comportement attendu — la skill est en lecture seule absolue. Elle propose toujours une alternative en pas-à-pas via l'interface Jeedom.

Si vous pensez que le refus est incorrect (ex. la skill refuse une lecture), ouvrez une [issue bug](https://github.com/Isilorn/jeedom-skills/issues).

---

## "Les logs ne remontent pas"

- Vérifiez que `scenarioLog/` est accessible depuis votre user SSH
- Sur certaines installations, les logs sont dans `/var/log/jeedom/` — la skill détecte automatiquement les deux emplacements
- En cas de sous-dossier non détecté, précisez : "les logs sont dans /chemin/vers/scenarioLog/"

---

## Erreur Python

Si vous voyez une traceback Python dans la réponse :

1. Vérifiez que Python 3.10+ est installé : `python3 --version`
2. Installez les dépendances si nécessaire : `pip install mysql-connector-python requests`
3. Copiez le message d'erreur complet et ouvrez une [issue bug](https://github.com/Isilorn/jeedom-skills/issues)

---

## Jeedom version < 4.5

La skill V1 cible uniquement Jeedom 4.5.x. Sur des versions antérieures :

- Le schéma DB peut différer (ex. champs `scenarioElement` absents ou renommés)
- Certaines méthodes API peuvent ne pas exister

Ouvrez une [issue divergence de version](https://github.com/Isilorn/jeedom-skills/issues) si vous souhaitez contribuer à la compatibilité d'une version antérieure.

---

## Vous ne trouvez pas votre problème ici ?

[Ouvrez une issue](https://github.com/Isilorn/jeedom-skills/issues) avec :

- Votre version Jeedom exacte
- Le mode d'accès utilisé (SSH+MySQL / API)
- Le prompt exact envoyé à Claude
- Le message d'erreur ou la réponse inattendue
