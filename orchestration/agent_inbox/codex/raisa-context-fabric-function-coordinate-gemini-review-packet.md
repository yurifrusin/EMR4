# Fresh Gemini veto: bounded PL/pgSQL function coordinate

Role: independent containment and diagnostic-correction veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r93`

Branch: `codex/review-context-fabric-function-coordinate-3c170e00`

Baseline HEAD: `a9ca5fa6b8ab80207e17b2eec96ac3d185b64fcd`

Candidate HEAD: `d9cca5f9375f6db85fe56e42500287d7b8b00938`

Read-only exact-worktree review through one fresh Antigravity project. Perform
the complete five-source rehydration required by `AGENTS.md`. Do not mutate
files or refs, start Docker/PostgreSQL, execute the behavior rehearsal, or
write worktree-local temporary state.

Review only the exact candidate diff and these bounded surfaces:

- `scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.schema.json`
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/provider-free-behavior-transaction-failure-evidence-013.json`
- `tests/test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`
- `tests/test_ariadne_agent_error_register.py`
- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-function-coordinate-diagnostic-recovery.md`
- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-implementation-recovery.md`
- `docs/ariadne-agent-error-correction-register-revision-112.md`

Establish that:

- attempt 013 remains immutable evidence for `BTR-E01`, SQLSTATE `22P02`, zero
  admitted scenarios and verified exact cleanup;
- the parser admits only one uniquely parseable PostgreSQL verbose PL/pgSQL
  context coordinate, only for the fixed scenario's closed function allowlist;
- the released identifier is schema-qualified, the line is a bounded integer,
  and missing, malformed, ambiguous, wrong-scenario or unlisted functions
  release no coordinate;
- raw SQL, values, messages, statement text, paths, signatures and unrestricted
  identifiers remain sealed;
- the closed evidence schema rejects arbitrary function identifiers, noninteger
  lines and added properties;
- no parent SQL, scenario, expected SQLSTATE, principal, isolation, transaction,
  fixture, runtime, provider, product-data, command, deployment, Pages or
  authority surface changed; and
- protected refs remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r93 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal check
git diff --check a9ca5fa6b8ab80207e17b2eec96ac3d185b64fcd..d9cca5f9375f6db85fe56e42500287d7b8b00938
git status --short --branch
git rev-parse HEAD
```

Additional review is limited to exact-path read-only inspection of the listed
surfaces and the named diff. Findings first; confirm clean unchanged HEAD. A
pass authorises exactly one fresh execution of the contained behavior rehearsal
for bounded diagnosis and nothing broader. Return exactly one
schema-constrained terminal decision.
