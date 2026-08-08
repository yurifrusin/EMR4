# Fresh Gemini veto: snapshot special-form and evidence-schema repair

Role: independent containment and final repair veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r90`

Branch: `codex/review-context-fabric-snapshot-coalesce-94463dd3`

Baseline HEAD: `14a2b74d4a03125df2a1c2854a23c19de2b1c5b6`

Candidate HEAD: `94463dd340192955913e15fee11f262348b564a4`

Read-only exact-worktree review through one fresh Antigravity project. Perform
the complete five-source rehydration required by `AGENTS.md`. Do not mutate
files or refs, start Docker/PostgreSQL, execute rehearsals, or write worktree-
local temporary state.

Review preserved failure 010, AER-0131, AER-0132 and the exact diff. Establish
that:

- attempt 010 passed parent, catalogue, fixture and privilege closure, failed
  before its first scenario at fixed `scenario_snapshot` with SQLSTATE `42883`,
  and proved exact cleanup;
- the renderer's sole SQL semantic change is invalid
  `pg_catalog.coalesce(...)` to valid PostgreSQL special form `COALESCE(...)`;
- aggregate functions, row conversion, ordering, relations, digests, snapshot
  shape and read-only transport remain unchanged;
- the evidence schema admits `query_id` only as literal `scenario_snapshot`,
  remains closed to additional properties, and a negative test rejects every
  other identifier;
- failure evidence contains no stderr prose, query text, query values or rows;
- no contract, scenario, fixture, SQL artifact, expected outcome, provider,
  product-data, authority, deployment, Pages or protected-ref surface changed;
  and
- exact protected refs remain at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r90 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py check
git diff --check 14a2b74d4a03125df2a1c2854a23c19de2b1c5b6..94463dd340192955913e15fee11f262348b564a4
git status --short --branch
git rev-parse HEAD
```

Additional checks remain read-only and value-free. Findings first; confirm
clean unchanged HEAD. A pass authorises exactly one fresh execution of the
contained behavior rehearsal for bounded diagnosis and nothing broader.
Return exactly one schema-constrained terminal decision.
