# ADR 0008 : Helpers Python factorisés vs SQL cookbook

- **Date** : 2026-04-27
- **Statut** : Accepté
- **Contexte de décision** : idéation initiale (D2.5, D7.5)

## Contexte

Les accès à la base de données Jeedom peuvent être réalisés de deux façons : (A) des helpers Python dédiés par cas d'usage, ou (B) un cookbook SQL que Claude Code utilise pour composer des requêtes ad-hoc. Les deux approches peuvent coexister.

## Options considérées

- **Option A — Helpers Python pour tout** : chaque opération = un script Python mono-responsabilité. ➕ Testable unitairement, capitalisation, réutilisabilité. ➖ Prolifération possible si les opérations sont trop atomisées.
- **Option B — SQL cookbook uniquement** : Claude Code compose les requêtes SQL à partir d'un cookbook de templates. ➕ Pas de code à maintenir, flexibilité. ➖ Requêtes non testées unitairement, risque d'erreurs sur les cas limites (ex. `trigger` mot réservé MySQL).
- **Option C — Hybride** : helpers pour les opérations récurrentes et complexes (tree-walker, resolve refs, usage graph, db_query wrapper), cookbook SQL pour les requêtes simples et ponctuelles (audit général, lecture rapide). ➕ Meilleur des deux mondes. ➖ Frontière à définir clairement.

## Décision

**Option C — Hybride**, avec une règle claire :

- **Helpers Python** (`jeedom-audit/scripts/`) : opérations récurrentes, multi-étapes ou sensibles (gestion des credentials, requêtes paramétrées, résolution des `#ID#`, tree-walker, usage graph)
- **SQL cookbook** (`references/sql-cookbook.md`) : templates de requêtes simples pour les workflows ad-hoc que Claude compose directement (audit général, valeurs courantes, recherches)

**Anti-pattern banni** : `audit_everything.py` ou tout helper omnibus. Chaque helper = une responsabilité.

## Conséquences

- ✅ 7 helpers définis avec I/O documentées (spec PLANNING §3.13)
- ✅ Helpers testables unitairement (`tests/unit/`)
- ✅ SQL cookbook permet à Claude de composer des requêtes ad-hoc sans code Python
- ⚠️ La frontière hybride doit être respectée — risque de dérive vers trop de helpers
- ⚠️ Le cookbook doit documenter les gotchas critiques (`trigger` mot réservé, etc.)
- 🔗 ADR 0005 (modes d'accès), PLANNING §3.11-3.13
