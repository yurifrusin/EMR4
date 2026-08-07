# Disposable PostgreSQL durability plan recovery veto

Date: 2026-08-07

Candidate HEAD: `009395ac28eb7ac05017fe5fbd1ae1439ecf948d`

Review worktree: `C:/Users/sarashera/EMR4-worktrees/r41`

Review branch: `codex/review-disposable-pg-plan-recovery-009395ac`

Model allocation: one genuinely fresh Antigravity project, exact
`gemini-3.6-flash-high`, explicit high reasoning.

## Authority and containment

This is a read-only replacement veto after Sol rejected the first reviewer
pass. Do not edit, create, stage, commit, fetch, push, install, write caches,
access the primary worktree, contact Docker or any database, inspect/list Docker
state, execute/apply SQL, create a migration, touch credentials, call any other
provider product path, or access patient/product/protected/historical-PHI data.
Sol retains recovery, runtime ownership, acceptance and integration.

## Exact allowlist

Read completely from `r41` only:

- `AGENTS.md` sections 2-7;
- the disposable PostgreSQL plan, design, plan recovery and threat-model delta;
- the focused disposable PostgreSQL plan test;
- the first review receipt and Sol rejection receipt;
- the parent inert-DDL plan, closeout and Sol acceptance;
- the parent `render-manifest.json` and `lowering-contract.json`; and
- the exact migration/transaction contract's four `existing_model_contract`
  relation entries only when needed for prerequisite analysis.

Do not enumerate or read any other path. Do not access protected evidence.

## Mandatory recovery challenge

The prior reviewer pass has no authority. Reproduce rather than inherit its
claims.

1. Verify PostgreSQL roles are cluster-scoped and prove the corrected order is
   sufficient: rollback database/prerequisites, invalid artifact transaction,
   database-local fabric absence plus cluster-wide accepted-role absence,
   then and only then success database/prerequisites and canonical admission.
   Look for any earlier command that could create an accepted role.
2. Verify PostgreSQL 16 psql semantics for `--single-transaction`: every
   artifact stream must use exact `--file=-`, `ON_ERROR_STOP=1` and
   `--single-transaction` on one argv. Plain implicit stdin, split calls,
   wrapper transaction text and caller-selected files must be impossible.
3. Identify whether any accepted top-level statement is nontransactional or
   any psql meta-command/internal transaction control could defeat rollback.
4. Challenge the fixed invalid suffix. It must be reached after earlier DDL,
   fail with an expected syntax SQLSTATE, roll back role/schema/object creation,
   and never modify the canonical artifact.
5. Re-run the full parent binding, Docker no-pull/no-network/no-port/no-mount,
   image-ID, tmpfs, synthetic prerequisite, catalogue completeness, bounded
   evidence and exact-owned-cleanup challenges independently.
6. Try at least ten hostile mutations, including success-before-rollback,
   database-local-only role check, plain stdin, omitted `--file=-`, separate
   `BEGIN` wrapper, ignored psql exit 3, image fallback, host mount, broad
   cleanup and behavior/claim widening.
7. Confirm the recovery addresses only the rejected mechanics and does not
   open behavior, application migration/runtime/source/data/provider-product,
   deployment, Pages or protected refs.

Report every P0-P3 finding with exact path/section and the smallest sufficient
correction. Passing tests do not override a conceptual defect. Do not repair.

## Allowlisted commands

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:RUFF_NO_CACHE='true'
git rev-parse HEAD
git status --short
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m ruff check tests/test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
git diff --check HEAD^ HEAD
git status --short
git rev-parse HEAD
```

Read-only `Get-Content`, exact-path `rg`, `git show`, `git diff` and short
in-memory expressions over exact allowlisted JSON are also allowed. Do not
create files or caches.

## Terminal response

Return one schema-constrained object only, with `decision` exactly `pass` or
`revision_required` and all evidence/findings in `review`. Include exact
rollback/success ordering, cluster-role proof, psql `--file=-` atomicity,
hostile mutations, unchanged boundaries, tests and clean exact-HEAD postflight.
Do not self-repair.
