# Session 2026-05-01 — J8 Réflexion stratégique + refonte roadmap

## Objectif de la session

Suite à un commentaire sur le forum Jeedom questionnant la relation entre la skill et le protocole MCP, engager une réflexion de fond sur la roadmap V2/V3 initialement planifiée. Aboutir à des décisions structurantes documentées en ADRs.

## Contexte déclencheur

Un utilisateur du forum (auteur de plugins MCP payants) a questionné la consommation de tokens de la skill et suggéré que le MCP était supérieur. L'échange a conduit à une réflexion sur la complémentarité skill/MCP plutôt qu'une opposition.

Un échange informel d'idéation avec Claude Opus 4.7 (2026-05-01) a produit trois décisions structurantes. Une session d'idéation formelle (avec modèle de raisonnement approfondi) est prévue pour définir l'architecture détaillée de holmesMCP.

## Décisions prises pendant la session

### 1. Lecture seule perpétuelle dans jeedom-audit (ADR-0006 amendé)

La roadmap V2/V3 modifiante est **définitivement retirée** de `jeedom-audit`. La lecture seule absolue devient une caractéristique identitaire permanente, pas une contrainte temporaire V1.

**Raison :** la proposition de valeur "la skill ne peut pas casser votre install" est trop forte pour être diluée. Les capacités modifiantes appartiennent à un autre paradigme (MCP) et à un autre projet.

### 2. holmesMCP — projet séparé, plugin Jeedom natif (ADR-0020)

Un nouveau projet `holmesMCP` sera créé comme plugin Jeedom natif distribué via le market. Il expose les données et commandes via le protocole MCP pour Claude Desktop, Cursor et tout client MCP.

**Raison :** cible un persona différent (Jeedomistes sans setup SSH/Python), architecture différente (outil fixe vs méthode adaptative), distribution différente (market vs skill).

### 3. jeedom-plugin-dev — second skill dans ce repo (ADR-0021)

La seconde skill du repo sera `jeedom-plugin-dev` — assistance au développement de plugins Jeedom. Implémentation reportée post-V1.1.

**Raison :** complète le repo "jeedom-skills" (pluriel), cible les développeurs de plugins, s'appuie sur l'architecture multi-skills prévue dès J0 (ADR-0003).

## Travail réalisé

- `docs/decisions/0006-lecture-seule-absolue.md` — amendement "lecture seule perpétuelle"
- `docs/decisions/0019-mcp-architecture.md` — statut → "Superseded by ADR-0020"
- `docs/decisions/0020-holmesmcp-projet-separe.md` — nouvelle ADR
- `docs/decisions/0021-jeedom-plugin-dev-skill.md` — nouvelle ADR
- `docs/sessions/2026-04-28-j7-release-v1.md` — session J7 documentée (reconstruction)
- `README.md` — roadmap V2 mise à jour (retrait écriture, ajout holmesMCP)
- `docs/PLANNING.md §10` — encadré de mise en contexte post-V1
- `docs/state/PROJECT_STATE.md` — mise à jour état post-refonte roadmap

## Reste à faire

- Session d'idéation formelle holmesMCP (prévue dans les prochains jours)
- Démarrage V1.1 : support Jeedom 4.6, nouveaux plugins tier-1

## Pour la prochaine session

**Commencer par :** lire `docs/state/PROJECT_STATE.md` + ce fichier de session.

**Prochaines étapes :** soit session d'idéation holmesMCP (nouveau repo, architecture plugin), soit démarrage V1.1 (support 4.6, fixtures, retours communauté). À décider par le PO.

## Pour le PO

- La réponse forum est disponible si besoin de la partager.
- La session d'idéation holmesMCP est à planifier quand tu es prêt.
