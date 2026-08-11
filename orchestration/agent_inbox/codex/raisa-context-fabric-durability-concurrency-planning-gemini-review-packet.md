# Independent veto packet — CF-D1 concurrency rehearsal planning

Review id: `raisa-context-fabric-durability-concurrency-planning-gemini-36-high-veto-001`

Model: Gemini 3.6 Flash/high in one fresh Antigravity project

Exact source: `bbb446c50e6c33e2e1079960d68dfe2e597b9cce`

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\cf-d1-planning-gemini-review`

Bound branch: `codex/cf-d1-planning-gemini-review`

## Start and scope

Read `AGENTS.md` completely first. Verify the exact root, clean branch and HEAD.
This is a read-only planning veto. Do not edit, create, delete, stage, commit,
switch, merge, push, start Docker/PostgreSQL, run an acceptance/evidence
generator, contact a provider/database/application route/credential/cloud
service/network destination, or inspect an unlisted path.

Inspect only these exact files:

- `AGENTS.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-plan.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-design.md`;
- `docs/security/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-threat-model-delta.md`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/concurrency-rehearsal-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/concurrency-rehearsal-contract.schema.json`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence-admission-replay-recovery-pass.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/behavior-transaction-rehearsal-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.schema.json`;
- `scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`;
- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-closeout.md`;
- `orchestration/agent_inbox/codex/raisa-context-fabric-durability-behavior-transaction-rehearsal-sol-acceptance.md`;
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert`; and
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json`.

Do not list or search repository roots, tests, orchestration, fixtures,
holdouts, reports, receipts or untracked paths. Do not inspect
`docs/branding/`. Do not open any other path. If an unlisted direct dependency
is necessary to decide, return `revision_required` and name it without opening
it.

## Required review

Decide whether this exact planning source safely and completely freezes the
narrowest provider-free concurrency implementation. Veto on any material
uncertainty. In particular:

1. verify this is a Context Fabric durability descendant, not AES-C6, and that
   it preserves all closed provider, data, command, runtime, deployment and
   protected-ref surfaces;
2. recompute all eight parent hashes and verify the accepted serial result and
   current parent artifacts are accurately distinguished;
3. examine the exact accepted function bodies needed for registration,
   producer projection, proofread admission and coordinator application, and
   decide whether each frozen concurrent outcome (`40001`, `CF004`, replay or
   commit) is justified by PostgreSQL isolation, row/unique locks and the
   function control flow;
4. verify the six scenarios are the smallest coherent set covering duplicate
   generation, lost stream-head update, identical/divergent admission,
   duplicate coordinator effect and rollback-with-waiter;
5. verify participant A's post-function `PgSleep` observation followed by
   participant B's `Lock` observation proves real overlap and does not rely on
   elapsed timing alone;
6. verify transactions are short and bounded, lock order is not modified,
   `40P01` is fail-closed, participant retry is zero and every post-race replay
   is a distinct fixed transaction;
7. verify least-privilege principal, practice/binding, forced-RLS, provenance,
   evidence-minimization and exact-ID cleanup requirements cannot be widened by
   scenario or database values;
8. verify the JSON Schema and tests close additional fields, scenario order,
   concurrency width, network/mount/port, retry, raw activity, isolation,
   SQLSTATE, grant and closed-surface mutations; and
9. identify any missing precondition, impossible expected outcome, race in the
   proposed observation method, overbroad claim or implementation ambiguity
   that could invalidate a one-run rehearsal.

## Allowed commands

Run only these commands from the bound worktree:

```powershell
git status --short --branch
git rev-parse HEAD
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py
git diff --check
git status --short --branch
```

Do not run the serial behavior harness or any Docker command.

Return `pass` only if there is no P0-P2 finding. In `review`, report exact HEAD,
reviewed paths, command results, findings with precise file/line support, and
explicit Docker starts, database operations, provider calls, product reads and
external operations performed by the review (all must be zero). Return
`revision_required` for any material defect, scope gap, command deviation or
uncertainty. Emit exactly one schema-constrained terminal decision.
