# Inert durability DDL rehearsal plan challenge

Date: 2026-08-07

Candidate HEAD: `57bb84a33a69e8a5471f8768c3c25783b11559ea`

Review worktree: `C:/Users/sarashera/EMR4-worktrees/r36`

Review branch: `codex/review-durability-inert-ddl-plan-57bb84a3`

Model allocation: one fresh Antigravity project, exact
`gemini-3.6-flash-high`, explicit high reasoning.

## Authority and containment

This is a read-only pre-implementation architecture veto. Do not edit, create,
stage, commit, fetch, push, install, write caches, access the main worktree,
open a database/source/outbox/feed/watcher/listener/product runtime, execute or
apply SQL/DDL, create a migration, touch credentials, call a provider product
path, or access patient/product/protected/historical-PHI data. Do not read prior
review conclusions. Sol retains plan meaning, recovery and acceptance.

## Exact allowlist

Read completely from `r36`:

- `AGENTS.md` sections 2-7 only;
- `docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-plan.md`;
- `docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-design.md`;
- `docs/security/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-threat-model-delta.md`;
- `tests/test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py`;
- the exact accepted structural and body contract JSON files;
- `docs/raisa-provider-free-unmounted-durability-migration-transaction-architecture-closeout.md`;
- `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-closeout.md`; and
- `orchestration/agent_inbox/codex/raisa-context-fabric-durability-migration-transaction-architecture-sol-acceptance.md` plus
  `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-sol-acceptance.md`.

Do not enumerate other paths.

## Required challenge

Independently determine whether the frozen plan is sufficiently exact and
feasible to hand to a mechanical implementation worker without forcing it to
invent security-critical semantics. In particular:

1. Verify the two parent source/hash bindings and whether the proposed
   `EffectiveCatalogueV1` can be fully derived and reconciled without mutating
   or interpreting parent prose.
2. Challenge the exact counts/populations and six-phase order, including the
   reference-only status of four `public.*` application relations, trigger
   declaration installation authority and revocation/grant ordering.
3. Determine whether every actual body instruction/expression form, nested
   flow, cardinality and terminal can be lowered from exact operands. Identify
   any accepted node whose executable meaning remains under-specified.
4. Check the canonical digest design. Verify that the named PostgreSQL-16 core
   primitives and qualification are real, that type/length/null/time encoding
   is unambiguous and implementable without a helper/extension, and that the
   Python/static vectors can meaningfully constrain the emitted SQL without a
   database.
5. Challenge `INSERT_OR_RELOAD_COMPARE`: the exact unique-violation scope,
   winner selection/comparison and rollback behavior must be renderable without
   `ON CONFLICT DO NOTHING`, no-op updates, broad exception swallowing or
   unmodelled effects.
6. Challenge constant-false `PROPAGATE_RETRYABLE` elimination: it must preserve
   the accepted no-catch/no-internal-retry semantics without making the renderer
   an optimizer that can erase arbitrary branches.
7. Check whether the proposed static recognizer has a calibrated claim and can
   actually detect hidden/extra top-level statements, malformed function
   bodies, search-path/identifier drift and privilege widening without claiming
   PostgreSQL server equivalence.
8. Check the fixed `.sql.inert` path, no-dependency/no-network/no-database
   boundary, deterministic two-render proof, hostile-mutation envelope and next
   disposable PostgreSQL gate separation.

Try at least three concrete counterexamples in memory. Report every P0-P3
finding with exact path/section and a minimal correction. Passing the six plan
tests does not override a conceptual gap.

## Allowlisted commands

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:RUFF_NO_CACHE='true'
git rev-parse HEAD
git status --short
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m ruff check tests/test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py
git diff --check HEAD^ HEAD
git status --short
git rev-parse HEAD
```

Read-only `Get-Content`, exact-path `rg`, `git show`, `git diff` and short
in-memory Python expressions over the two allowlisted contract JSON files are
also allowed. Do not create files or caches.

## Terminal response

Return one schema-constrained object only, with `decision` exactly `pass` or
`revision_required` and all evidence/findings in `review`. Report exact
postflight HEAD/status, six-test result, Ruff/diff result, concrete hostile
counterexamples and P0-P3 findings. Do not self-repair.
