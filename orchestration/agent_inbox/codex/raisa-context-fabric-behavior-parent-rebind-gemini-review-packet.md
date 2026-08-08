# Fresh Gemini veto: behavior rehearsal recovered-parent rebind

Role: independent parent-binding and final pre-runtime veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r87`

Branch: `codex/review-context-fabric-behavior-rebind-d59a6fe8`

Baseline HEAD: `7747092884b98efd14286f2f97c27ad3e964a812`

Candidate HEAD: `d59a6fe83bac6f8255e9a0be79140aae269805ef`

Read-only exact-worktree review through one fresh Antigravity project. Perform
the complete five-source rehydration required by `AGENTS.md`, including API
Steward, protected-evidence and no-runtime boundaries. Do not mutate files or
refs, start Docker/PostgreSQL, execute either rehearsal, or write worktree-local
temporary state.

Review the exact diff and establish independently that:

- the accepted recovery closeout binds the schema-validated parse/catalogue
  pass at runtime source HEAD `06b8f558...`, artifact `9407b8...`, contract
  `b1900c...`, exact catalogue match and exact cleanup;
- AER-0127 correctly rejects the earlier verifier receipt's obsolete artifact
  sentence, and no value from that sentence enters this rebind;
- all six behavior parent bindings recompute from canonical working-tree bytes,
  with exact `git show` blob equality for the recovered inert SQL and manifest;
- the behavior contract canonical digest `32d0608...` matches the harness;
- the twenty scenario objects, order, fixture namespace, privileges, runtime
  containment, expected failures and closed surfaces are byte-identical to the
  predecessor contract apart from the three recovered parent bindings;
- all parent and contract checks occur before Docker resolution; and
- historical predecessor behavior evidence remains immutable and the canonical
  behavior result is still unreleased.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r87 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py check
git diff --check 7747092884b98efd14286f2f97c27ad3e964a812..d59a6fe83bac6f8255e9a0be79140aae269805ef
git status --short --branch
git rev-parse HEAD
```

Additional checks remain read-only and value-free. Findings first; confirm
clean unchanged HEAD. A pass authorises exactly one execution of the fixed
twenty-scenario behavior rehearsal in one newly owned contained disposable
PostgreSQL 16 container and nothing broader. Return exactly one schema-
constrained terminal decision.
