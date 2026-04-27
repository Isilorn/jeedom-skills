# ADR 0004 : Stratégie credentials (remote_mycnf par défaut)

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D3.1, D3.3)

## Contexte

La skill doit accéder à la base MySQL Jeedom via SSH. Le password de la base de données doit être transmis au client `mysql` côté serveur sans jamais apparaître en clair dans les arguments CLI (visible dans `ps aux`), dans les logs SSH, ou dans un fichier côté client Claude Code.

## Options considérées

- **Option A — Password en argument CLI** (`mysql -p<pass>`) : ➕ Simple. ➖ **Anti-pattern critique** : visible dans `ps aux`, dans les logs du shell, historique bash. Banni.
- **Option B — `remote_mycnf`** : le password est stocké dans `~/.my.cnf` côté serveur Jeedom (permissions 600). La commande SSH transmet uniquement l'alias et la requête SQL. Le client Claude Code ne connaît jamais le password. ➕ Sécurité maximale, password jamais transmis. ➖ Nécessite une configuration initiale côté serveur.
- **Option C — `client_file`** : le password est lu via `MYSQL_PWD` (variable d'environnement), jamais en argument CLI. ➕ Compatible si `~/.my.cnf` n'est pas possible côté serveur. ➖ Le password doit être stocké quelque part côté client.
- **Option D — `prompt`** : le password est demandé à chaque session, jamais persisté. ➕ Sécurité maximale (rien stocké). ➖ Friction maximale à chaque session.

## Décision

**Option B (`remote_mycnf`) par défaut**, avec **Option C (`client_file`) en fallback**, **Option D (`prompt`) disponible**.

Fichier de configuration : `~/.config/jeedom-audit/credentials.json` (permissions 600 côté client), champ `db_password_source` avec valeurs `"remote_mycnf"` | `"client_file"` | `"prompt"`.

Override via variables d'environnement `JEEDOM_*` (priorité sur le fichier).

Sous-commande `setup` interactive pour la première configuration (J1).

## Conséquences

- ✅ Password MySQL jamais visible dans les logs ou `ps aux` (mode `remote_mycnf`)
- ✅ User MySQL read-only dédié fortement recommandé via `setup`
- ✅ Flexibilité : 3 modes selon les contraintes du serveur
- ⚠️ La configuration initiale nécessite une intervention côté serveur Jeedom (documentée dans `references/connection.md`)
- ⚠️ `credentials.json` en `.gitignore` absolu
- 🔗 ADR 0005 (modes d'accès), ADR 0006 (lecture seule)

## Alternatives écartées

**Option A (password CLI)** : banni absolument. Anti-pattern documenté, visible dans `ps aux`.
