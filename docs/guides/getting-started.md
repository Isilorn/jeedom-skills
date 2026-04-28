---
title: Guide de démarrage — jeedom-audit
audience: utilisateur novice (15 minutes)
---

# Guide de démarrage

Ce guide vous accompagne de l'installation jusqu'à votre premier audit complet. Durée estimée : 15 minutes.

---

## 1. Prérequis

Avant de commencer, vérifiez que vous avez :

- **Claude Code** installé ([téléchargement](https://docs.claude.ai/claude-code))
- **Mode run activé** dans Claude Code : Réglages → Avancé → Activer les commandes shell
- **Jeedom 4.5.x** accessible depuis votre machine
- **Python 3.10+** (`python3 --version` dans un terminal)
- **Accès SSH à votre box Jeedom** (recommandé) ou une **clé API Jeedom**

> Si vous n'avez que la clé API (pas SSH), la skill fonctionne en mode dégradé : pas d'accès aux logs, certains workflows sont limités. Voir [troubleshooting](troubleshooting.md#api-only).

---

## 2. Installer la skill

### Option A — Fichier `.skill` (le plus simple)

1. Télécharger `jeedom-audit-v1.0.0.skill` depuis les [GitHub Releases](https://github.com/Isilorn/jeedom-skills/releases/latest)
2. Placer le fichier :
   - macOS/Linux : `~/.claude/skills/`
   - Windows : `%APPDATA%\Claude\skills\`
3. Redémarrer Claude Code

### Option B — Clone du repo

```bash
git clone https://github.com/Isilorn/jeedom-skills.git ~/.claude/skills/jeedom-skills
```

Claude Code détecte automatiquement le dossier `jeedom-audit/` comme skill.

---

## 3. Préparer l'accès SSH (recommandé)

La skill accède à votre box via SSH. Si ce n'est pas déjà fait :

### 3a. Créer un alias SSH

Ajoutez dans `~/.ssh/config` (créez le fichier s'il n'existe pas) :

```
Host Jeedom
    HostName 192.168.1.10       # IP de votre box
    User jeedom                 # ou pi, debian, etc.
    IdentityFile ~/.ssh/id_rsa  # votre clé SSH
```

Testez : `ssh Jeedom "echo ok"` — doit répondre `ok` sans mot de passe.

### 3b. Créer un utilisateur MySQL en lecture seule

Sur votre box Jeedom (via SSH) :

```sql
-- En tant que root MySQL
CREATE USER 'jeedom_audit_ro'@'localhost' IDENTIFIED BY 'mot_de_passe_fort';
GRANT SELECT ON jeedom.* TO 'jeedom_audit_ro'@'localhost';
FLUSH PRIVILEGES;
```

Puis créez `~/.my.cnf` sur la box (dans le home de votre user SSH, pas `/root/`) :

```ini
[client]
user=jeedom_audit_ro
password=mot_de_passe_fort
database=jeedom
```

```bash
chmod 600 ~/.my.cnf
```

<!-- Capture : ~/.my.cnf correctement configuré — à fournir par le PO -->

---

## 4. Configurer la skill

Dans Claude Code, démarrez une nouvelle conversation et tapez :

> "Configure jeedom-audit pour ma box"

La skill lance l'assistant interactif `setup.py` qui demande :

1. L'alias SSH (ex. `Jeedom`)
2. L'URL de l'API Jeedom (ex. `http://192.168.1.10`)
3. La clé API (trouvable dans Jeedom : Réglages → Système → Configuration → API)

Les credentials sont sauvegardés dans `~/.config/jeedom-audit/credentials.json` (permissions 600).

<!-- Capture : assistant setup en cours — à fournir par le PO -->

---

## 5. Premier audit

Tapez simplement :

> "Fais un audit général de mon Jeedom"

Claude Code va :

1. Vérifier la connexion à votre box
2. Collecter les données (inventaire, plugins, scénarios, commandes problématiques)
3. Produire un rapport structuré avec les points d'attention

<!-- Capture : rapport d'audit complet — à fournir par le PO -->

---

## 6. Autres commandes pour démarrer

Une fois l'audit général fait, vous pouvez aller plus loin :

```
"Explique-moi le scénario [nom de votre scénario]"
"Qui utilise la commande [Objet][Équipement][Commande] ?"
"Pourquoi le scénario X ne se déclenche plus ?"
"Audite mes équipements jMQTT"
```

Consultez le [guide d'usage](usage.md) pour la liste complète des cas d'usage.

---

## En cas de problème

Consultez le [guide troubleshooting](troubleshooting.md) ou [ouvrez une issue](https://github.com/Isilorn/jeedom-skills/issues).
