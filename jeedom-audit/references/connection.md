# Connexion et credentials — jeedom-audit

Référence complète pour configurer l'accès SSH+MySQL et l'API Jeedom.

---

## Configuration initiale (setup interactif)

```bash
python3 scripts/setup.py
```

Le setup guide la création de tous les fichiers nécessaires et vérifie chaque étape.

---

## Fichier credentials local

**Chemin** : `~/.config/jeedom-audit/credentials.json` (perm 600)

```json
{
  "preferred_mode": "auto",
  "ssh_alias": "Jeedom",
  "db_name": "jeedom",
  "db_user": "jeedom_audit_ro",
  "db_password_source": "remote_mycnf",
  "api_url": "http://<ip-jeedom>",
  "api_key": "<clé-api-jeedom>"
}
```

| Champ | Description |
|---|---|
| `preferred_mode` | `auto` (SSH+MySQL puis API), `mysql`, `api` |
| `ssh_alias` | Alias SSH défini dans `~/.ssh/config` |
| `db_name` | Base de données Jeedom (typiquement `jeedom`) |
| `db_user` | User MySQL read-only dédié |
| `db_password_source` | Voir ci-dessous |
| `api_url` | URL HTTP de votre Jeedom |
| `api_key` | Clé API Jeedom (Réglages → Système → Configuration → API) |

**Overrides par variables d'environnement** (priorité sur le fichier) :
`JEEDOM_SSH_ALIAS`, `JEEDOM_DB_NAME`, `JEEDOM_DB_USER`, `JEEDOM_DB_PASSWORD_SOURCE`,
`JEEDOM_API_URL`, `JEEDOM_API_KEY`, `JEEDOM_PREFERRED_MODE`

---

## Stratégie `db_password_source`

### `remote_mycnf` (recommandé)

Le mot de passe MySQL vit dans `~/.my.cnf` **côté serveur Jeedom** (perm 600).
Claude Code ne connaît jamais le mot de passe — il exécute simplement `mysql jeedom -e '...'` via SSH.

**Création du `~/.my.cnf` sur la box :**
```ini
[client]
user=jeedom_audit_ro
password=<mot-de-passe>
host=localhost
```
```bash
chmod 600 ~/.my.cnf
```

### `client_file`

Fallback si le serveur n'autorise pas `~/.my.cnf`. Le password est lu via la variable
d'environnement `MYSQL_PWD` — jamais passé en argument CLI.

### `prompt`

Demandé à chaque session, jamais persisté. Usage ponctuel uniquement.

**Anti-patterns bannis :**
- `mysql -p<pass>` (visible dans `ps aux`)
- Password en argument SSH
- Fichier credentials sans `chmod 600`

---

## Création du user MySQL read-only

Connexion initiale en tant que root MySQL (une seule fois) :

```sql
CREATE USER IF NOT EXISTS 'jeedom_audit_ro'@'localhost' IDENTIFIED BY '<mot-de-passe>';
GRANT SELECT ON jeedom.* TO 'jeedom_audit_ro'@'localhost';
FLUSH PRIVILEGES;
```

```bash
sudo mysql jeedom -e "CREATE USER ..."
```

Vérification :
```bash
ssh Jeedom "mysql jeedom -e 'SELECT COUNT(*) FROM eqLogic;'"
```

---

## Alias SSH

L'alias `Jeedom` doit être défini dans `~/.ssh/config` :

```
Host Jeedom
    HostName <ip-ou-hostname>
    User <user-ssh>
    IdentityFile ~/.ssh/id_ed25519
```

Test :
```bash
ssh Jeedom "echo ok"
```

---

## Clé API Jeedom

**Dans l'UI** : Réglages → Système → Configuration → API → Clé API générale

La clé est stockée chiffrée dans la DB (`config` où `key='api'`).
Le setup la récupère automatiquement via PHP si l'accès SSH est disponible.

---

## Récupération automatique des credentials Jeedom

Si vous avez l'accès SSH, le setup peut lire la configuration directement depuis la box :

```bash
# Lecture de la config DB (user, password, db_name)
cat /var/www/html/core/config/common.config.php

# Décryptage de la clé API
php -r "define('ROOT','/var/www/html'); require_once('/var/www/html/core/php/core.inc.php'); echo config::byKey('api');"
```

Ces opérations sont effectuées automatiquement par `setup.py`.

---

## Vérification complète

```bash
# MySQL RO
ssh Jeedom "mysql jeedom -e 'SELECT COUNT(*) AS nb FROM eqLogic;'"

# API
curl -s -X POST http://<ip>/core/api/jeeApi.php \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","params":{"apikey":"<clé>"},"id":1}'
# Attendu : {"result":"pong"}

# db_query.py end-to-end
echo '{"query":"SELECT COUNT(*) AS nb FROM eqLogic"}' | python3 scripts/db_query.py
```
