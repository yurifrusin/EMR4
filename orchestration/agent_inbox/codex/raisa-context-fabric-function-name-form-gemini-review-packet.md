# Fresh Gemini veto: closed PL/pgSQL function-name forms

Role: independent containment and diagnostic-parser veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r94`

Branch: `codex/review-context-fabric-function-name-form-897835bc`

Baseline HEAD: `d9cca5f9375f6db85fe56e42500287d7b8b00938`

Candidate HEAD: `897835bc3fd0fe7a4af20cc4ecf91873057d3e6c`

Read-only exact-worktree review through one fresh Antigravity project. Perform
the complete five-source rehydration required by `AGENTS.md`. Do not mutate
files or refs, start Docker/PostgreSQL, execute the behavior rehearsal, or
write worktree-local temporary state.

Review the exact candidate diff and only these bounded surfaces:

- `scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/provider-free-behavior-transaction-failure-evidence-014.json`
- `tests/test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`
- `tests/test_ariadne_agent_error_register.py`
- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-function-name-form-recovery.md`
- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-implementation-recovery.md`
- `docs/ariadne-agent-error-correction-register-revision-114.md`

Establish that:

- attempt 014 remains immutable evidence for `BTR-E01`, SQLSTATE `22P02`, zero
  admitted scenarios and verified exact cleanup;
- no claim is made that the observed PostgreSQL context was definitely
  unqualified;
- the parser admits exactly the known `emr4_context_fabric` qualifier or no
  qualifier before a scenario-allowlisted function name, then normalizes both
  to the same schema-qualified evidence identifier;
- a foreign schema, unlisted function, malformed line, wrong scenario or
  ambiguity releases no coordinate;
- raw SQL, values, messages, statement text, paths, signatures and unrestricted
  identifiers remain sealed;
- no schema, parent SQL, scenario, SQLSTATE, principal, isolation, transaction,
  fixture, provider, product-data, command, deployment, Pages or authority
  surface changed; and
- protected refs remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r94 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal check
git diff --check d9cca5f9375f6db85fe56e42500287d7b8b00938..897835bc3fd0fe7a4af20cc4ecf91873057d3e6c
git status --short --branch
git rev-parse HEAD
```

Additional review is limited to exact-path read-only inspection of the listed
surfaces and named diff. Findings first; confirm clean unchanged HEAD. A pass
authorises exactly one fresh execution of the contained behavior rehearsal for
bounded diagnosis and nothing broader. Return exactly one schema-constrained
terminal decision.
