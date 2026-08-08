# Fresh Gemini veto: bounded snapshot-query diagnostic

Role: independent containment and final diagnostic veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r89`

Branch: `codex/review-context-fabric-snapshot-diagnostic-14a2b74d`

Baseline HEAD: `bfd9e2fd5f2c55535f4de8d4d7bd42f34e1d2472`

Candidate HEAD: `14a2b74d4a03125df2a1c2854a23c19de2b1c5b6`

Read-only exact-worktree review through one fresh Antigravity project. Perform
the complete five-source rehydration required by `AGENTS.md`. Do not mutate
files or refs, start Docker/PostgreSQL, execute rehearsals, or write worktree-
local temporary state.

Review failure 009, AER-0130 and the exact diff. Establish that:

- attempt 009 passed parent, catalogue, fixture and privilege closure, failed
  before its first scenario with raw exit-code-only evidence, and cleaned up;
- call ordering makes the first scenario snapshot the only next read-only query;
- the replacement helper preserves the same fixed `PSQL_FILE`, file-stdin,
  read-only transaction and closed timeout/cap transport;
- on failure it can emit only fixed query id `scenario_snapshot`, one
  unambiguous syntactically valid SQLSTATE and a digest of the closed metadata;
- stderr prose, query values, rows and caller-selected query ids remain closed;
- success parsing remains one JSON value with the existing exact snapshot shape
  validation; and
- no contract, scenario, fixture, SQL artifact, expected outcome, containment
  or authority surface changed.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r89 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py check
git diff --check bfd9e2fd5f2c55535f4de8d4d7bd42f34e1d2472..14a2b74d4a03125df2a1c2854a23c19de2b1c5b6
git status --short --branch
git rev-parse HEAD
```

Additional checks remain read-only and value-free. Findings first; confirm
clean unchanged HEAD. A pass authorises exactly one fresh execution of the
fixed contained behavior rehearsal for bounded diagnosis and nothing broader.
Return exactly one schema-constrained terminal decision.
