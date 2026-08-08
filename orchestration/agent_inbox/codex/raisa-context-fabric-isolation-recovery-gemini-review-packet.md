# Fresh Gemini veto: behavior isolation recovery

Role: independent containment and final repair veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r92`

Branch: `codex/review-context-fabric-isolation-recovery-a9ca5fa6`

Baseline HEAD: `cc4b8c9a7481b8fdd007bd94ab02fa771da14c38`

Candidate HEAD: `a9ca5fa6b8ab80207e17b2eec96ac3d185b64fcd`

Read-only exact-worktree review through one fresh Antigravity project. Perform
the complete five-source rehydration required by `AGENTS.md`. Do not mutate
files or refs, start Docker/PostgreSQL, execute rehearsals, or write worktree-
local temporary state.

Review preserved failure 012, AER-0134 and the exact diff. Establish that:

- attempt 012 fixed the failing site as `BTR-E01` with SQLSTATE `CF303`, zero
  admitted scenarios and exact cleanup;
- accepted `register_observer_generation_v1` and
  `apply_durability_transition_v1` SQL explicitly require `SERIALIZABLE`;
- the parent SQL is not weakened or changed;
- exactly `BTR-E01`, `BTR-E04`, `BTR-I03` and `BTR-B03` now render and record
  `SERIALIZABLE`, while all other scenario isolation/read-only shapes remain
  unchanged;
- contract, plan, design, renderer, identity admission and evidence schema are
  mutually consistent on that exact isolation map;
- no retry, concurrency, savepoint, nested transaction, provider, product data,
  operational database, deployment, Pages or authority surface is opened; and
- protected refs remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r92 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py check
git diff --check cc4b8c9a7481b8fdd007bd94ab02fa771da14c38..a9ca5fa6b8ab80207e17b2eec96ac3d185b64fcd
git status --short --branch
git rev-parse HEAD
```

Additional checks remain read-only and value-free. Findings first; confirm
clean unchanged HEAD. A pass authorises exactly one fresh execution of the
contained behavior rehearsal for bounded diagnosis and nothing broader.
Return exactly one schema-constrained terminal decision.
