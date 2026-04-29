# jeedom-audit — skill Claude Code

**Audite, diagnostique et explique une installation Jeedom 4.5 — sans jamais la modifier.**

`jeedom-audit` est une [skill Claude Code](https://docs.claude.ai/claude-code) pour la communauté francophone Jeedom. Elle donne à Claude Code une connaissance structurelle de Jeedom 4.5 (base de données, scénarios, plugins, logs) pour produire des audits, diagnostics et explications détaillées, en **lecture seule absolue**.

---

## Aperçu en 30 secondes

> *"fais un audit général de mon Jeedom"*

```
⚠️ Quelques points à surveiller — installation fonctionnelle, aucune erreur système.

┌──────────────────────────────────────────────┬────────────────────┐
│                  Indicateur                  │       Valeur       │
├──────────────────────────────────────────────┼────────────────────┤
│ Équipements actifs                           │ 177 / 217 (81,5 %) │
│ Scénarios actifs                             │ 57 / 62 (92 %) ✅  │
│ Commandes sans Type Générique                │ 4 869              │
│ Erreurs système                              │ 0 ✅               │
│ Variables orphelines                         │ 14                 │
└──────────────────────────────────────────────┴────────────────────┘

🔴 Urgent — Investiguer NbFailRAID = 15 949
   UI : Outils → Scénarios → chercher "RAID" → vérifier les logs

🟡 À faire — Vérifier les trackers Tile (3 équipements sans historique)
🟢 Optionnel — Supprimer les agendas désactivés (200+ commandes inutiles)
```

> *"explique-moi ce que fait le scénario Présence Alice"*

```
### Scénario — Présence Alice (id: 70)
Déclencheurs : #[Présence][Alice Shelly][Présence]# change

SI #[Présence][Alice Shelly][Présence]# == 1 ALORS
  → Action : #[Chauffage][Bureau][On]#
  → Scénario : Mode_Présence_on (immédiat)
SINON
  → Attendre 5 min
  → SI #[Présence][Alice Shelly][Présence]# == 0 ALORS
      → Scénario : Mode_Absent_on (immédiat)
```

---

## Prérequis

- **Claude Code** avec le mode `run` activé (Réglages → Avancé → Activer les commandes shell)
- **Jeedom 4.5.x** — testé sur 4.5.3 (MariaDB 10.5, Debian)
- **Python 3.10+** sur votre machine locale
- **Accès SSH à la box** (recommandé) ou **clé API Jeedom** (accès partiel)

---

## Installation

### Option 1 — Fichier `.skill` (recommandé)

1. Télécharger `jeedom-audit-v1.0.0.skill` depuis les [GitHub Releases](https://github.com/Isilorn/jeedom-skills/releases/latest)
2. Placer le fichier dans votre dossier skills Claude Code :
   - macOS/Linux : `~/.claude/skills/`
   - Windows : `%APPDATA%\Claude\skills\`
3. Redémarrer Claude Code

### Option 2 — Clone du repo

```bash
git clone https://github.com/Isilorn/jeedom-skills.git
# Puis symlinker ou copier jeedom-audit/ dans votre dossier skills Claude Code
```

---

## Configuration

Au premier appel, la skill propose un assistant de configuration :

```
> "configure jeedom-audit"
```

L'assistant `setup` demande :

- L'alias SSH de votre box (ex. `Jeedom`)
- L'URL de l'API Jeedom (ex. `http://192.168.1.10`)
- La clé API (optionnel si SSH+MySQL disponible)

Les credentials sont stockés localement (jamais transmis à Anthropic) :

- macOS/Linux : `~/.config/jeedom-audit/credentials.json`
- Windows : `C:\Users\<vous>\.config\jeedom-audit\credentials.json`

> **Windows** : la skill requiert OpenSSH (inclus dans Windows 10 1809+ et Windows 11) ou WSL. Les commandes SSH du guide supposent un terminal Unix-compatible (PowerShell ou WSL).

---

## Démarrer

Quelques exemples de phrases pour commencer :

| Ce que vous dites | Ce que fait la skill |
|---|---|
| "Fais un audit général de mon Jeedom" | Rapport de santé complet (WF1) |
| "Pourquoi le scénario X ne se déclenche plus ?" | Diagnostic avec logs (WF2/WF13) |
| "Explique-moi ce que fait le scénario Présence" | Pseudo-code lisible (WF5) |
| "Qui utilise la commande Température Salon ?" | Graphe d'usage (WF6) |
| "Trace la chaîne d'appels depuis Mode_Absent_off" | Cartographie mermaid (WF12) |
| "Audite mes équipements jMQTT" | Audit plugin (WF3/WF4) |
| "Comment simplifier mon scénario X ?" | Suggestions de refactor UI (WF7) |

---

## Ce que fait la skill

- Audit général de santé (équipements, scénarios, plugins, commandes problématiques)
- Diagnostic de scénarios qui ne se déclenchent plus ou se comportent mal
- Explication pas-à-pas de ce que fait un scénario (pseudo-code `#[Objet][Équipement][Commande]#`)
- Graphe d'usage : quels scénarios dépendent d'une commande ou d'un équipement ?
- Cartographie d'orchestration inter-scénarios avec détection de cycles (diagramme mermaid)
- Suggestions de refactor verbales avec pas-à-pas dans l'interface Jeedom
- Support tier-1 : Virtual, jMQTT, Agenda, Script, Alarme, Thermostat

## Ce que la skill ne fait pas

- **Aucune modification** — lecture seule absolue (pas d'INSERT, UPDATE, DELETE, pas d'API modifiante)
- Jeedom < 4.5 non supporté en V1
- Autres systèmes domotiques (Home Assistant, Domoticz) hors périmètre

---

## Limites V1

- Accès API seul : logs indisponibles, WF2 et WF13 sont limités — voir [troubleshooting](docs/guides/troubleshooting.md)
- 6 plugins en couverture complète (tier-1) ; les autres sont analysés par inférence
- Testé sur Jeedom 4.5.3 — les versions 4.4.x et antérieures peuvent présenter des divergences

---

## Confidentialité

Zéro télémétrie par défaut. Aucune donnée de votre installation n'est transmise à des services tiers. Les credentials restent sur votre machine. Les données sensibles (mots de passe, IPs) sont filtrées avant d'apparaître dans les réponses.

---

## Contribuer

Retours, bugs et propositions de nouveaux plugins bienvenus — voir [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Roadmap

### V1.1 — correctifs + retours communauté

- Fixtures DB synthétiques pour tests sans box réelle
- Support Jeedom 4.4.x (divergences de schéma à documenter)

### V2

- **Couche MCP** — exposer les scripts comme outils MCP (portabilité Claude Desktop, Cursor, et autres clients MCP)
- Nouveaux plugins tier-1 (Zigbee2MQTT natif, Z-Wave JS, Philips Hue...)
- Tests d'intégration automatisés
- Opérations API réversibles (write-once, avec confirmation explicite)

Voir le [CHANGELOG](CHANGELOG.md) pour le détail des versions.

---

## Aller plus loin

- [Guide de démarrage](docs/guides/getting-started.md) — première session pas-à-pas (15 min)
- [Référence des cas d'usage](docs/guides/usage.md) — les 13 workflows en détail
- [Troubleshooting](docs/guides/troubleshooting.md) — erreurs courantes et solutions
- [Architecture](docs/guides/architecture.md) — comment la skill est conçue
- [CHANGELOG](CHANGELOG.md) — historique des versions

---

## License

MIT — [Isilorn](https://github.com/Isilorn)

> Testé sur Jeedom 4.5.3 (MariaDB 10.5, Debian) — 2026-04-28
