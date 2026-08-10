# Independent veto 2: behavior attempt 047 rollback-gap recovery

Date: 2026-08-08

Decision required: exactly one schema-constrained `pass` or
`revision_required`.

Review clean worktree
`C:\Users\sarashera\EMR4-worktrees\raisa-context-fabric-durability-behavior-r181`
at exact `0cf41c25ea55d2533f185e7db6efabe91bb53e95`. Protected refs remain
exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform complete five-source AGENTS.md rehydration. Review only AGENTS.md;
the original recovery diff
`5f4067340be0958612b0dad351222f32f13900d1..3e73606a0b451d02d2bb3d4d9d22eee161aa084f`;
the verifier-defect correction diff
`3e73606a0b451d02d2bb3d4d9d22eee161aa084f..0cf41c25ea55d2533f185e7db6efabe91bb53e95`;
first review receipt SHA-256
`38a599b8e5932a0cc8497cce75521e5782ca40d36fb89afab57bd6c56bc69d2b`;
the immutable attempt-047 failure evidence; diagnosis note/script/test;
behavior contract/harness/test; AER-0237; and tracked exact parent files needed
to reconcile their hashes. Do not inspect mutable evidence aliases, holdouts,
historical Diary data, `docs/branding/`, patient/clinical/product data or
unrelated paths.

Verify:

1. exact clean candidate and protected refs before/after;
2. the first review's substantive diagnosis, failure seal, cleanup, unchanged
   behavior contract and unchanged artifact conclusions remain valid;
3. test portability is repaired with `sys.executable`, not a worktree-local
   `.venv` assumption;
4. the behavior test file is canonically formatted and no semantic assertion
   changed in that formatting-only hunk;
5. immutable attempt-047 evidence remains SHA-256
   `bc577de88b7acafac72828bb2ddae898181886d08676c8802acf84ef925ebd63`;
6. canonical behavior contract remains SHA-256
   `43b25bd7509439f069643dcb0ae8e62e27002834fe9903d84e7478486b452615`;
   its twenty scenarios and category counts `6/4/3/4/3` are unchanged;
7. inert SQL and manifest remain exact SHA-256
   `dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`
   and `2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`;
8. all commands below pass cleanly; and
9. no Docker/PostgreSQL run, operational database, watcher/feed,
   application/API/Diary wiring, provider/product data, deployment, Pages or
   protected refs open.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r181 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_047_rollback_gap_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_047_rollback_gap_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_047_rollback_gap_diagnosis.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_047_rollback_gap_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_047_rollback_gap_diagnosis.py
git diff --check 5f4067340be0958612b0dad351222f32f13900d1..0cf41c25ea55d2533f185e7db6efabe91bb53e95
git status --short --branch
git rev-parse HEAD
git rev-parse master
git rev-parse handoff/current
git rev-parse origin/master
git rev-parse origin/handoff/current
```

Do not edit, commit, push, start Docker/PostgreSQL, run either database harness,
contact another provider/product, inspect forbidden data, move refs or
self-accept. Return `revision_required` for any P0-P2 finding, drift, failed
check or dirty postcondition; otherwise return exact `pass`.
