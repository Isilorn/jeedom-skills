---
title: Connexion HTTP à l'API Jeedom — jeedom-audit
description: Transport HTTP, SSL, authentification, test de connectivité — prérequis pour api_call.py
updated: 2026-04-27
---

# Connexion HTTP — API Jeedom

> **Ce fichier documente la couche transport.** Pour les méthodes JSON-RPC (ce qu'on peut appeler), voir `references/api-jsonrpc.md`.

---

## 1. Prérequis réseau

L'API Jeedom doit être accessible depuis la machine qui exécute la skill.

| Scénario | URL type | Prérequis |
|---|---|---|
| Réseau local (LAN) | `http://192.168.1.X` ou `http://jeedom.local` | Aucun — accès direct |
| Accès externe | `https://monsite.com` | Port 443 ouvert, DNS public |
| VPN | `http://10.X.X.X` | VPN actif sur la machine locale |
| DNS Jeedom | `https://X.dns.jeedom.com` | Clé API DNS (distincte de la clé locale) |

En accès LAN, HTTP non chiffré est acceptable. En accès externe, HTTPS obligatoire.

---

## 2. Clé API Jeedom

Jeedom expose la clé API dans **Réglages → Système → Configuration → onglet API**.

Deux clés existent :
- **Clé API locale** — accès depuis le LAN ou VPN, permissions complètes
- **Clé API DNS** — accès via le DNS Jeedom, mêmes méthodes disponibles

La skill utilise le champ `api_key` de `credentials.json`. **Jamais en clair dans un fichier versionné** — permissions 600 requises.

---

## 3. Configuration dans `credentials.json`

Champs relatifs à l'accès API :

```json
{
  "api_url": "http://192.168.1.50",
  "api_key": "votre_clé_api_ici",
  "verify_ssl": true,
  "preferred_mode": "auto"
}
```

| Champ | Requis | Défaut | Rôle |
|---|---|---|---|
| `api_url` | Oui (si mode API actif) | — | URL de base Jeedom — sans `/core/api/...` |
| `api_key` | Oui (si mode API actif) | — | Clé API Jeedom |
| `verify_ssl` | Non | `true` | Mettre `false` si certificat auto-signé |
| `preferred_mode` | Non | `"auto"` | `"auto"` / `"mysql"` / `"api"` |

---

## 4. SSL et certificats

Par défaut, `api_call.py` vérifie le certificat SSL (`verify_ssl: true`).

Si Jeedom utilise un **certificat auto-signé** (Let's Encrypt non configuré, LAN sans FQDN), ajouter dans `credentials.json` :

```json
{ "verify_ssl": false }
```

`api_call.py` applique alors `ssl.CERT_NONE` — hostname et certificat non vérifiés.

> `verify_ssl: false` est acceptable en LAN fermé. Ne jamais l'utiliser pour un accès internet ouvert.

---

## 5. Test de connectivité

```bash
# Test ping via curl — doit retourner {"jsonrpc":"2.0","result":"ok","id":1}
curl -s -X POST http://192.168.1.50/core/api/jeeApi.php \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"ping","params":{"apikey":"VOTRE_CLE"},"id":1}'

# Test avec SSL auto-signé (option -k)
curl -sk -X POST https://jeedom.local/core/api/jeeApi.php \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"version","params":{"apikey":"VOTRE_CLE"},"id":1}'

# Test via api_call.py
echo '{"method": "ping"}' | python3 scripts/api_call.py
```

---

## 6. Timeouts et retry

`api_call.py` applique par défaut :

- **Timeout :** 15 secondes par appel
- **Retry :** 1 retry unique sur erreur réseau ou timeout (pas sur erreur JSON-RPC applicative)
- **Pas de retry** sur méthode inconnue, paramètre invalide, ou blacklist

Sur box lente (Raspberry Pi sous charge) : passer `timeout=30` à `api_call.run()`.

---

## 7. Erreurs transport fréquentes

| Erreur `_transport_error` | Cause probable | Action |
|---|---|---|
| `HTTP 401: Unauthorized` | Clé API invalide ou absente | Vérifier `api_key` dans `credentials.json` |
| `HTTP 403: Forbidden` | IP non autorisée (pare-feu Jeedom) | Ajouter l'IP locale dans Jeedom → API → IP autorisées |
| `Connection refused` | Jeedom éteint ou port fermé | Vérifier que Jeedom est démarré et le port 80/443 accessible |
| `Name or service not known` | Hostname non résolu | Utiliser l'IP directement ou vérifier DNS |
| `Timeout (15s)` | Box surchargée ou réseau lent | Augmenter `timeout` ou vérifier la charge |
| `Réponse non-JSON` | Proxy ou page d'erreur Apache | Vérifier que l'URL pointe bien sur la box Jeedom |

---

## 8. Récupération de la clé API

Dans l'interface Jeedom :
1. **Réglages → Système → Configuration**
2. Onglet **API**
3. Copier la valeur du champ **Clé API**
4. Coller dans `credentials.json` → `api_key`

La même clé autorise toutes les méthodes JSON-RPC listées dans `api-jsonrpc.md`.

**Formats à bannir :** clé en variable d'environnement non chiffrée, argument CLI, fichier sans perm 600.
