# Independent veto packet — CF-D2 restart and unknown-commit planning

Review id: `raisa-context-fabric-durability-restart-unknown-commit-planning-gemini-36-high-veto-001`

Model: Gemini 3.6 Flash/high in one fresh Antigravity project

Exact source: `a0797a17e99f4adfa65ce6bef96ffdcfcdf18c02`

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\cf-d2-planning-gemini-review`

Bound branch: `codex/cf-d2-planning-gemini-review`

## Start and scope

Read `AGENTS.md` completely first. Verify the exact root, clean branch and HEAD.
This is a read-only planning veto. Do not edit, create, delete, stage, commit,
switch, merge, push, start Docker/PostgreSQL, run an acceptance/evidence
generator, contact a provider/database/application route/credential/cloud
service/network destination, or inspect an unlisted path.

Inspect only these exact files:

- `AGENTS.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-plan.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-design.md`;
- `docs/security/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-threat-model-delta.md`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/restart-unknown-commit-rehearsal-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/restart-unknown-commit-rehearsal-contract.schema.json`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_plan.py`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/provider-free-durability-concurrency-evidence-attempt-004.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/concurrency-rehearsal-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/provider-free-durability-concurrency-evidence.schema.json`;
- `scripts/raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py`;
- `docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-closeout.md`;
- `orchestration/agent_inbox/codex/raisa-context-fabric-durability-concurrency-rehearsal-sol-acceptance.md`;
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert`; and
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json`.

Do not list or search repository roots, tests, orchestration, fixtures,
holdouts, reports, receipts or untracked paths. Do not inspect
`docs/branding/`. Do not open any other path. If an unlisted direct dependency
is necessary to decide, return `revision_required` and name it without opening
it.

## Required review

Decide whether this exact source safely and completely freezes the narrowest
provider-free CF-D2 implementation. Veto on any material uncertainty. In
particular:

1. verify CF-D2 is a Context Fabric durability descendant, not AES-C6, and all
   provider, real/product data, command, operational runtime, deployment,
   Pages and protected-ref surfaces remain closed;
2. recompute all eight parent hashes and verify accepted CF-D1 evidence,
   current CF-D1 artifacts and inert SQL are accurately distinguished;
3. inspect the accepted coordinator replay, anchor-fence and
   `append_recovery_anchor_v1` control flow and decide whether R01-R04's
   `RECEIPT_APPLIED`, `RECEIPT_REPLAYED`, fixed `P0001`, pending-anchor
   `CF303` and post-anchor continuation expectations are justified;
4. verify the four scenarios are the narrowest coherent population that
   distinguishes terminal commit, terminal rollback and both durable outcomes
   after a lost terminal result without guessing;
5. verify the one-shot client boundary, pre/post-commit `PgSleep` cutpoints and
   pure classifier input separation are honest, implementable and do not
   overclaim a literal crash inside WAL commit or protocol acknowledgement;
6. verify the same-container writable-layer `PGDATA` plus tmpfs shielding of
   the image-declared default volume can preserve one exact cluster across
   `SIGKILL`/start while proving zero bind/named/anonymous volumes and exact
   cleanup;
7. verify `fsync`, `synchronous_commit`, `full_page_writes`, checksums,
   least-privilege identities, four exact crashes, zero retries, evidence
   minimization and exact-ID lifecycle checks cannot be widened by inputs;
8. verify the JSON Schema and 38 hostile mutations close additional fields,
   parent drift, network/volume/storage/restart changes, weak durability,
   scenario order, classification swaps, partial acceptance, raw evidence,
   grants, claims and closed surfaces; and
9. identify any impossible expected result, false absence proof, mutable
   timestamp identity, restart race, Docker storage ambiguity, anchor gap,
   overbroad claim or implementation detail that could invalidate a one-run
   rehearsal.

## Allowed commands

Run only these commands from the bound worktree:

```powershell
git status --short --branch
git rev-parse HEAD
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_plan.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_plan.py
git diff --check
git status --short --branch
```

Do not run any behavior/concurrency harness or Docker command.

Return `pass` only if there is no P0-P2 finding. In `review`, report exact HEAD,
reviewed paths, command results, findings with precise file/line support, and
explicit Docker starts, database operations, provider calls, product reads and
external operations performed by the review (all must be zero). Return
`revision_required` for any material defect, scope gap, command deviation or
uncertainty. Emit exactly one schema-constrained terminal decision.
