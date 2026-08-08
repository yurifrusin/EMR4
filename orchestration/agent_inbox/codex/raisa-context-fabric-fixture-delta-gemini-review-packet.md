# Fresh Gemini veto: fixture/application catalogue delta separation

Role: independent safety and final repair veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r88`

Branch: `codex/review-context-fabric-fixture-delta-bfd9e2fd`

Baseline HEAD: `d59a6fe83bac6f8255e9a0be79140aae269805ef`

Candidate HEAD: `bfd9e2fd5f2c55535f4de8d4d7bd42f34e1d2472`

Read-only exact-worktree review through one fresh Antigravity project. Perform
the complete five-source rehydration required by `AGENTS.md`, including API
Steward, protected-evidence and no-runtime boundaries. Do not mutate files or
refs, start Docker/PostgreSQL, execute rehearsals, or write worktree-local
temporary state.

Review failure 008, AER-0128/AER-0129 and the exact diff. Establish that:

- failure 008 uniquely represents changed query ids
  `application_relations,relation_acl`, occurred after exact artifact/catalogue
  admission but before every scenario, and cleaned up exactly;
- bootstrap intentionally changes both the application-row projection and
  application relation privileges;
- the repaired bootstrap guard admits exactly those two query ids;
- the post-behavior guard admits exactly `application_relations`, while every
  schema/security catalogue query remains digest-stable;
- admitting `application_relations` cannot hide application data drift because
  each covered application relation remains enforced by exact per-scenario row
  count deltas and row-set snapshot digests;
- any extra catalogue query-id change still fails closed;
- no contract, scenario, fixture, SQL artifact, expected outcome, runtime
  containment or authority boundary changed; and
- the predecessor verifier's nonexistent path claim is rejected and not used.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r88 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py check
git diff --check d59a6fe83bac6f8255e9a0be79140aae269805ef..bfd9e2fd5f2c55535f4de8d4d7bd42f34e1d2472
git status --short --branch
git rev-parse HEAD
```

Additional checks remain read-only and value-free. Findings first; confirm
clean unchanged HEAD. A pass authorises exactly one fresh execution of the
fixed twenty-scenario behavior rehearsal in one newly owned contained
disposable PostgreSQL 16 container and nothing broader. Return exactly one
schema-constrained terminal decision.
