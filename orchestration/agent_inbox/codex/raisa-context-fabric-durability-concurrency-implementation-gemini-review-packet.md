# Independent veto packet — CF-D1 concurrency rehearsal implementation

Review id: `raisa-context-fabric-durability-concurrency-implementation-gemini-36-high-veto-001`

Model: Gemini 3.6 Flash/high in one fresh Antigravity project

Exact source: `46b220284467fb3a3d5a440d7d3fa9839d4f8c28`

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\cf-d1-implementation-gemini-review`

Bound branch: `codex/cf-d1-implementation-gemini-review`

## Start and scope

Read `AGENTS.md` completely first. Verify the exact root, clean branch and HEAD.
This is a read-only pre-runtime implementation veto. Do not edit, create,
delete, stage, commit, switch, merge, push, start Docker/PostgreSQL, run either
rehearsal harness, generate runtime evidence, contact a provider, database,
application route, credential, cloud service or network destination, or inspect
an unlisted path.

Inspect only these exact files:

- `AGENTS.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-plan.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-design.md`;
- `docs/security/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-threat-model-delta.md`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/concurrency-rehearsal-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/concurrency-rehearsal-contract.schema.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/provider-free-durability-concurrency-evidence.schema.json`;
- `scripts/raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py`;
- `orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-concurrency-planning-review-receipt.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence-admission-replay-recovery-pass.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/behavior-transaction-rehearsal-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.schema.json`;
- `scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`;
- `scripts/raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py`;
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert`; and
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json`.

Do not list or search repository roots, tests, orchestration, fixtures,
holdouts, reports, receipts or untracked paths. Do not inspect
`docs/branding/`. Do not open another path. If an unlisted direct dependency is
necessary to decide, return `revision_required` and name it without opening it.

## Required review

Decide whether this exact implementation safely executes the already-approved
narrow CF-D1 plan once. Veto on any material uncertainty. In particular:

1. verify exact parent hashes, frozen scenario order and zero authority widening;
2. trace all six rendered leader/contender transactions against the accepted
   PostgreSQL functions and fixtures, including registration replay, contiguous
   positions 1/2, identical primary, divergent `CF004`, coordinator `40001`,
   injected `P0001`, fresh conflict and receipt replays;
3. verify each participant has one fixed least-privilege session authorization,
   one short transaction, bounded local timeouts, no savepoint/role switch,
   no retry and no participant superuser use;
4. verify the post-function leader hold is genuinely observed as
   `Timeout/PgSleep` before contender launch, the contender is then genuinely
   observed with `wait_event_type=Lock`, and no PID, query or lock key is
   retained;
5. verify threading, subprocess deadlines, polling ceiling, connection width,
   exception paths and result parsing cannot create an unnoticed participant,
   false overlap, timing-only claim, raw-text release or unbounded wait;
6. verify before/after digest and count checks cover all 22 relations, distinguish
   zero-count digest changes, and make each required replay inert;
7. verify the evidence schema accepts the exact pass shape, rejects additional
   or raw fields, orders all six scenarios, binds six preconditions, requires
   zero retries/provider/product/external operations and requires verified
   exact-ID cleanup;
8. verify container creation remains networkless, unmounted, unexposed,
   resource-bounded and newly nonce-owned, and cleanup targets only the captured
   exact container ID after ownership revalidation;
9. verify no Docker/database operation occurs during review and that the harness
   cannot pull an image, inspect globally, access an operational database,
   contact a provider, read product data or mutate application/source state; and
10. identify any schema/runtime mismatch, impossible result marker, SQLSTATE
    ambiguity, stale snapshot assumption, missing precondition, evidence
    miscount, cleanup gap or overbroad claim that should stop the one runtime
    attempt.

## Allowed commands

Run only these commands from the bound worktree:

```powershell
git status --short --branch
git rev-parse HEAD
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile scripts\raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py
git diff --check
git status --short --branch
```

Do not execute either rehearsal script and do not run any Docker command.

Return `pass` only if there is no P0-P2 finding. In `review`, report exact HEAD,
reviewed paths, command results, findings with precise file/line support, and
explicit Docker starts, database operations, provider calls, product reads and
external operations performed by the review (all must be zero). Return
`revision_required` for any material defect, scope gap, command deviation or
uncertainty. Emit exactly one schema-constrained terminal decision.
