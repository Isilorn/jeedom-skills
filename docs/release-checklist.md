---
description: Checklist de release — à suivre dans l'ordre exact avant chaque publication
---

# Checklist de release

À utiliser pour toute release (majeure, mineure, patch). Chaque étape dépend de la précédente — ne pas sauter.

---

## 1. Préparer le code

- [ ] Tous les commits du périmètre de la release sont sur `main`
- [ ] `CHANGELOG.md` à jour avec les changements de cette version
- [ ] `docs/state/PROJECT_STATE.md` reflète l'état courant

## 2. Bumper la version

- [ ] Mettre à jour `pyproject.toml` → `version = "X.Y.Z"`
- [ ] Committer : `git commit -m "chore: bump version A.B.C → X.Y.Z"`
- [ ] Pusher : `git push`

## 3. Packager la skill

```bash
python3 build/package_skill.py
```

- [ ] Vérifier que le fichier produit s'appelle **`dist/jeedom-audit-vX.Y.Z.skill`**
- [ ] La version dans le nom correspond bien au tag prévu

## 4. Créer le tag git

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

- [ ] Vérifier que le tag pointe sur le bon commit (`git log --oneline -1`)

## 5. Créer la release GitHub

```bash
gh release create vX.Y.Z dist/jeedom-audit-vX.Y.Z.skill \
  --title "jeedom-audit vX.Y.Z" \
  --notes "..."
```

- [ ] Le nom de l'asset dans la commande est **`jeedom-audit-vX.Y.Z.skill`**
- [ ] Les notes de release mentionnent **`unzip -o jeedom-audit-vX.Y.Z.skill`** (pas une version précédente)
- [ ] La release est publiée (pas draft) — ou draft intentionnel si on attend

## 6. Vérifier sur GitHub

Ouvrir https://github.com/Isilorn/jeedom-skills/releases/tag/vX.Y.Z et vérifier :

- [ ] Le tag est associé au bon commit (le dernier de `main`)
- [ ] L'asset téléchargeable s'appelle `jeedom-audit-vX.Y.Z.skill`
- [ ] Les notes de release sont cohérentes (version, nom du fichier, liens)
- [ ] Les issues fermées par cette release sont bien closes sur GitHub

---

## Patch rapide (hotfix)

Pour un correctif urgent sur une release existante :

1. Committer le fix sur `main`
2. Bumper vers le patch suivant (ex. 1.0.1 → 1.0.2) — reprendre depuis l'étape 2
3. Ne jamais déplacer un tag déjà publié — créer un nouveau tag

---

## Commande de vérification finale

```bash
gh release view vX.Y.Z --json tagName,targetCommitish,assets \
  --jq '{tag: .tagName, assets: [.assets[].name]}'
```

Doit retourner :
```json
{
  "tag": "vX.Y.Z",
  "assets": ["jeedom-audit-vX.Y.Z.skill"]
}
```
