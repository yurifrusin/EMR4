# Fresh Gemini veto: expected-success scenario diagnostic

Role: independent containment and final diagnostic veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r91`

Branch: `codex/review-context-fabric-expected-success-diagnostic-cc4b8c9a`

Baseline HEAD: `94463dd340192955913e15fee11f262348b564a4`

Candidate HEAD: `cc4b8c9a7481b8fdd007bd94ab02fa771da14c38`

Read-only exact-worktree review through one fresh Antigravity project. Perform
the complete five-source rehydration required by `AGENTS.md`. Do not mutate
files or refs, start Docker/PostgreSQL, execute rehearsals, or write worktree-
local temporary state.

Review preserved failure 011, AER-0133 and the exact diff. Establish that:

- attempt 011 passed the repaired snapshot and fixture/privilege closure,
  reached the first expected-success scenario, admitted zero scenarios, and
  proved exact cleanup;
- fixed contract ordering makes `BTR-E01` the only attempted scenario;
- expected-success rejection now emits only that current closed scenario id,
  one unambiguous valid SQLSTATE when available and their metadata digest;
- the evidence schema enumerates exactly the twenty contract scenario ids;
- stderr prose, SQL text, values, rows and caller-selected ids remain closed;
- success and expected-failure behavior, scenario SQL, fixtures, contract,
  artifact, snapshot logic, authority and containment remain unchanged; and
- protected refs remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r91 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py check
git diff --check 94463dd340192955913e15fee11f262348b564a4..cc4b8c9a7481b8fdd007bd94ab02fa771da14c38
git status --short --branch
git rev-parse HEAD
```

Additional checks remain read-only and value-free. Findings first; confirm
clean unchanged HEAD. A pass authorises exactly one fresh execution of the
contained behavior rehearsal for bounded diagnosis and nothing broader.
Return exactly one schema-constrained terminal decision.
