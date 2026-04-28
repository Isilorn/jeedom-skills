---
id: eval-015
titre: Lecture rapide multi-questions — WF8-11
jalon: J6
---

# Eval 015 — Lecture rapide multi-questions (WF8-11)

## Contexte

Les workflows 8-11 (valeur courante, historique, variable dataStore, recherche)
doivent répondre en une ou quelques lignes, sans passer par un audit complet.
Cette éval couvre les 4 cas en séquence pour vérifier la concision et la pertinence.

---

## Cas A — WF8 : Valeur courante

### Input utilisateur

> "Quelle est la valeur actuelle de la commande Température Bureau ?"

### Comportement attendu

- Requête SQL ou API (`cmd::byId`) pour récupérer `cmd.currentValue` et `cmd.datetime`
- Sortie sur **une ligne** : `[Bureau][Thermostat bureau][Température] = 21.3 °C, mis à jour il y a 4 minutes`
- Pas de tableau, pas d'audit complet
- Si valeur NULL : le dire explicitement avec `cmd.datetime` si disponible

### Comportement non attendu

- Audit général lancé
- Tableau avec plusieurs colonnes
- Valeur sans unité ni horodatage relatif

---

## Cas B — WF9 : Historique

### Input utilisateur

> "Montre-moi l'historique des 10 dernières valeurs de la commande Température Bureau"

### Comportement attendu

- API `cmd::getHistory` ou SQL `history` sur les 10 dernières entrées
- Sortie : **tableau** (`datetime` | `value`) si ≤50 lignes
- Format datetime lisible (`2026-04-27 14:32:00`)
- Si aucune valeur historisée : message explicite

### Comportement non attendu

- Plus de 50 lignes retournées sans résumé statistique
- Absence de tableau pour ≤50 lignes
- Tentative de modifier l'historique

---

## Cas C — WF10 : Variable dataStore

### Input utilisateur

> "Quelle est la valeur de la variable globale 'mode_maison' ?"

### Comportement attendu

- SQL : `SELECT * FROM dataStore WHERE key = 'mode_maison'` (ou API `dataStore::byKey`)
- Préciser la portée : globale (`link_id = -1`) ou locale (lien vers objet/scénario)
- Sortie concise : `mode_maison = "absent"  [variable globale]`
- Si variable inexistante : le dire clairement

### Comportement non attendu

- Confusion entre variable locale et globale
- Omission de la portée
- Sortie en tableau pour une seule variable

---

## Cas D — WF11 : Recherche

### Input utilisateur

> "Liste-moi tous les équipements du plugin jMQTT qui sont actifs"

### Comportement attendu

- SQL filtré : `eqLogic` avec `eqType_name = 'jMQTT'` et `isEnable = 1`
- Sortie : **tableau** `Nom | Objet | Actif` trié par objet puis nom
- Maximum 50 lignes — si plus, annoncer le nombre total et proposer de filtrer
- Noms d'objet résolus (jointure `object.name`) — pas d'ID brut

### Comportement non attendu

- Équipements désactivés inclus
- IDs bruts sans nom d'objet
- Tableau non trié
- Dépassement silencieux de 50 lignes

---

## Critères de succès globaux

- Chaque cas répond en ≤3 échanges (idéalement 1)
- Aucune confusion entre les workflows (pas d'audit complet lancé pour une simple valeur)
- Données sensibles filtrées (passwords, apikey) même en lecture rapide

## Résultat sur box réelle

| Date | Cas | Résultat | Notes |
|---|---|---|---|
| — | A (valeur courante) | à valider | Session J6 |
| — | B (historique) | à valider | Session J6 |
| — | C (dataStore) | à valider | Session J6 |
| — | D (recherche) | à valider | Session J6 |
