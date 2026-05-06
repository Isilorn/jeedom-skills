# Brief jalon M1 — Infrastructure

**Branche** : créer `develop` depuis `main` dans cette session
**Pré-requis** : M0 terminé (baseline 13 WF commité sur `main`)
**Référence** : `docs/state/migration-jeedom-audit-brief.md` §3

## Contexte

Poser toute l'infrastructure de la migration avant de toucher au code :
branche de travail, configuration Holmes MCP, décisions ADR, roadmap mise à jour.
Après ce jalon, toutes les sous-sessions suivantes travaillent sur `develop`.

---

## M1-1 — Setup complet *(unique sous-session)*

### 1. Branche develop

```bash
git checkout main
git checkout -b develop
git push -u origin develop
```

### 2. Fichier `.mcp.json`

Créer `.mcp.json` à la racine du projet (scope projet uniquement — ne pas toucher `~/.claude/`).
Contenu :

```json
{
  "mcpServers": {
    "holmes": {
      "type": "http",
      "url": "http://<ip-box>:8765/mcp",
      "headers": {
        "Authorization": "Bearer <TOKEN_A_RENSEIGNER>"
      }
    }
  }
}
```

Le token est généré dans Jeedom → page plugin Holmes MCP → section "Tokens d'accès".
**Ne pas committer de token réel** — le placeholder `<TOKEN_A_RENSEIGNER>` est intentionnel.
Ajouter `.mcp.json` au `.gitignore` si ce n'est pas déjà le cas (le token est une donnée sensible).

### 3. ADR-0020 — Amendement

Ajouter un bloc amendement à la fin de `docs/decisions/0020-holmesmcp-projet-separe.md` :

```markdown
---

## Amendement — 2026-05-06

**Décision** : `jeedom-audit` V2 utilise Holmes MCP comme couche d'accès aux données.

Les scripts Python (SSH + MySQL + API JSON-RPC) sont remplacés par des appels aux
27 outils Holmes MCP v1.2.0. Cette décision ne contredit pas l'ADR-0020 initial
(holmesMCP reste un projet séparé) — elle ajoute que jeedom-audit en est un consommateur.

**Conséquences** :
- Nouveau pré-requis utilisateur : Holmes MCP installé sur la box Jeedom
- Suppression de la couche Python (scripts + _common/ + tests unitaires associés)
- Setup simplifié : Bearer token uniquement, pas de SSH ni de credentials MySQL côté client
- Périmètre lecture seule inchangé (ADR-0006)
```

### 4. PLANNING.md §10 — Amendement roadmap

Ajouter un bloc amendement au début de la section `## 10. Roadmap post-V1` :

```markdown
> **⚠️ Amendement stratégique — 2026-05-06**
>
> - **V1.5 — Obsolète** : les scripts prévus (`dead_cmds.py`, `history_query.py`,
>   `unused_variables.py`, `generic_plugin_inspector.py`) sont couverts nativement
>   par Holmes MCP v1.2.0. V1.5 est annulée.
> - **V2.0.0 — Migration Holmes MCP** : remplacement de la couche d'accès aux données
>   par Holmes MCP (jalons M0–M8). Branche `develop`. Cible : 2026-Q2.
> - **V2.1** : ex-V1.1 — support Jeedom 4.6, fixtures DB synthétiques, retours communauté.
>   Reportée après V2.0.0.
> - **jeedom-plugin-dev** (second skill) : inchangé, horizon V3.
>
> En cas de conflit, cet amendement et les ADRs associés font autorité sur les lignes
> V1.5/V2/V3 ci-dessous.
```

### 5. PROJECT_STATE.md — Mise à jour

- `Jalon en cours` → `Migration Holmes MCP — M1 Infrastructure`
- `Prochaines étapes` → `M2 Nettoyage structurel (develop)`
- Ajouter dans `Jalons post-release` : `- **M0 (2026-05-06)** : baseline Phase 0 — 13 WF documentés sur main`

**Gate qualité** : `.mcp.json` présent et JSON valide (`python -c "import json; json.load(open('.mcp.json'))"`),
`.mcp.json` dans `.gitignore`, ADR-0020 amendé, PLANNING.md amendé, PROJECT_STATE.md à jour.

---

## DoD — Jalon M1

- [ ] Branche `develop` créée et poussée sur origin
- [ ] `.mcp.json` présent à la racine, JSON valide, dans `.gitignore`
- [ ] ADR-0020 amendé (bloc 2026-05-06)
- [ ] `PLANNING.md §10` amendé (V1.5 obsolète, V2.0.0, V2.1)
- [ ] `PROJECT_STATE.md` mis à jour (jalon en cours, prochaines étapes)
- [ ] Aucun token réel commité
