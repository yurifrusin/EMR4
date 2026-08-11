# Independent veto packet — CF-D2 restart and unknown-commit implementation

Review id: `raisa-context-fabric-durability-restart-unknown-commit-implementation-gemini-36-high-veto-001`

Model: `gemini-3.6-flash-high` with explicit high effort in one fresh Antigravity project

Exact source: `a5b1107736ce64c0ee3861cb51b231d861b12764`

Bound worktree: `C:\Users\sarashera\EMR4-worktrees\r242`

Bound branch: `codex/cf-d2-implementation-veto-r242`

## Start and authority

Read `AGENTS.md` completely first. Verify the exact root, clean branch and HEAD.
This is a read-only implementation veto before any Docker contact. Do not edit,
create, delete, stage, commit, switch, merge, push, start or inspect Docker or
PostgreSQL, run the CF-D2 harness, generate evidence, contact a provider,
application route, database, credential, cloud service or network destination,
or inspect an unlisted path.

Inspect only these exact files:

- `AGENTS.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-plan.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-design.md`;
- `docs/security/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-threat-model-delta.md`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/restart-unknown-commit-rehearsal-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/restart-unknown-commit-rehearsal-contract.schema.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/provider-free-durability-restart-unknown-commit-evidence.schema.json`;
- `scripts/raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_plan.py`;
- `scripts/raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py`;
- `scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/behavior-transaction-rehearsal-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/provider-free-disposable-postgresql-evidence-admission-replay-winner-exact-reproduction.json`;
- `docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-admission-replay-winner-rebind.md`;
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert`;
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json`;
- `docs/ariadne-agent-error-correction-register-revision-242.md`;
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`;
- `orchestration/continuity/ariadne-agent-error-register/pattern-report.json`;
- `tests/test_ariadne_agent_error_register.py`;
- `orchestration/agent_inbox/codex/raisa-context-fabric-durability-restart-unknown-commit-postcompaction-implementation-resume-runtime-state.json`;
- `orchestration/agent_inbox/codex/raisa-context-fabric-durability-restart-unknown-commit-postcompaction-implementation-resume-receipt.json`;
- `orchestration/agent_inbox/codex/raisa-context-fabric-durability-restart-unknown-commit-implementation-precommit-runtime-state.json`; and
- `orchestration/agent_inbox/codex/raisa-context-fabric-durability-restart-unknown-commit-implementation-precommit-receipt.json`.

Do not list or search repository roots, tests, orchestration, fixtures,
holdouts, reports, receipts or untracked paths. Do not inspect
`docs/branding/`. Do not open any other path. If an unlisted direct dependency
is necessary to decide, return `revision_required` and name it without opening
it.

## Required review

Decide whether exact source `a5b1107736ce64c0ee3861cb51b231d861b12764`
safely implements the frozen provider-free CF-D2 contract and is eligible for
exactly one four-scenario disposable run. Veto on any P0-P2 finding or material
uncertainty. In particular:

1. verify every parent path and hash binds the accepted CF-D1/serial/SQL
   lineage, and verify the AER-0275 correction changes only three stale
   duplicated test tuples to match the already accepted behavior contract;
2. verify the run topology has one `postgres:16-bookworm` container,
   `--pull=never`, `--network=none`, zero ports/bind/named/anonymous volumes,
   tmpfs only at the image-declared default data path, and the real checksum-
   enabled `PGDATA` in the exact container writable layer outside that path;
3. verify every kill/start/remove operation is constructed from the captured
   exact ID after name/nonce/image/storage/network/state reverification, each
   crash is `SIGKILL`, PostgreSQL starts against the same PGDATA, cluster and
   settings are exact, startup is bounded, and cleanup proves exact-ID plus
   exact nonce/label absence without global enumeration;
4. verify each participant gets one fresh connection, one `SET SESSION
   AUTHORIZATION` before `BEGIN`, the correct least-privilege role and
   isolation, fixed timeouts and zero retry, with no superuser participant,
   `SET ROLE`, savepoint, prepared transaction or direct Fabric DML;
5. verify the one-shot R03/R04 clients place `pg_sleep` respectively after and
   before `COMMIT`, require observed `Timeout/PgSleep`, discard and never parse
   partial output, and treat a nonzero process exit only as absence of a
   terminal result—not commit or rollback evidence;
6. verify `classify_recovery` accepts only the complete nine-member canonical
   pre/post packets, accepts no scenario/cutpoint/timing/output/expected branch,
   returns committed only for the full atomic delta, returns rolled back only
   for exact equality, and fails every mixed/partial packet as unresolved;
7. verify R01-R04 implement the exact expected commit/rollback/restart paths,
   replay is inert, pending-anchor position two fails exact `CF303`, lifecycle
   authority alone appends the anchor, and the later contiguous transition
   coalesces its obligation without reactivating a retired frame;
8. verify whole-relation snapshots, coordinate packets, settings and identity
   are minimized to counts, closed labels and SHA-256 digests; no raw SQL,
   query, PID, client fragment, server log, WAL, credential, patient/product
   value or timestamp is released as semantic identity;
9. verify the evidence schema plus semantic validator reject extra fields,
   wrong order/classification, fewer than four crashes, retries, provider or
   product operations, cleanup failure, mixed recovery, restart mismatch,
   forbidden output and parent drift; and
10. identify any impossible SQL result, Docker-inspect mismatch, process race,
    stale postmaster behavior, timeout hole, cleanup ambiguity, wrong relation
    delta, evidence-schema mismatch or broader claim that could invalidate the
    single run.

## Allowed commands

Run only these commands from the bound worktree, serially and without changing
environment state:

```powershell
git status --short --branch
git rev-parse HEAD
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py::test_all_parent_paths_heads_and_hashes_are_exact
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_ariadne_agent_error_register.py::test_register_is_valid_after_durability_schema_recovery tests\test_ariadne_agent_error_register.py::test_aer_0275_records_the_stale_behavior_parent_test_correction tests\test_ariadne_agent_error_register.py::test_committed_pattern_report_matches_fresh_build
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile scripts\raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py
git diff --check
git status --short --branch
```

Do not run the harness, Docker, PostgreSQL or any other command.

Return `pass` only with zero P0-P2 findings. In `review`, report the exact HEAD,
reviewed paths, command results, findings with precise file/line support, and
explicit counts of Docker starts, database operations, provider calls, product
reads and external-network operations performed by the review (all must be
zero). Return `revision_required` for any material defect, command deviation,
scope gap or uncertainty. Emit exactly one schema-constrained terminal
decision.
