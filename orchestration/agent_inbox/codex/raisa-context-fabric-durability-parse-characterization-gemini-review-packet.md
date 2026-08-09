# Independent veto packet: parse/catalogue characterization rebind

Date: 2026-08-10

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r149`
- Branch: `codex/review-context-fabric-parse-characterization-2e59f606`
- Accepted parent: `c8ab760220bc40863a18feaa3fc13a3d6ba04ba6`
- Candidate: `2e59f606098b55e88bb2fbea0f0fdccaeb521193`
- Protected local/origin `master` and `handoff/current`: exact
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete `AGENTS.md` five-source rehydration and name all five
required sources.

## Purpose

Independently decide whether the candidate safely rebinds the disposable
PostgreSQL 16 parse/catalogue rehearsal to the accepted regenerated inert SQL
without allowing characterization to accept itself or disturbing historical
evidence.

## Required challenges

Verify and report:

1. exact candidate HEAD, clean review worktree, exact parent-to-candidate diff
   and protected refs;
2. contract parent source is `c8ab7602`, inert SQL is exactly 1,435,142 LF
   bytes, SHA-256
   `ca22e47e847409f1ae8a81f62dd7f5f8402a43176d9015211f657204460fbdbb`,
   421 statements, PostgreSQL 16 and six phases;
3. contract mode is exactly `characterization_only`, expected query digests
   are exactly `{}`, and canonical contract SHA-256 is
   `ce85174653dfbadc0f15124dd9f26a8ab83ba68c4192ced21569fdcb3efe0efc`;
4. schema, harness constant, tests and ledger bind those exact values before
   any Docker resolution;
5. a characterization result can only return
   `catalogue_characterization_required`; it cannot produce the parse pass;
6. historical support-grant, binding-RLS and input-namespace evidence tests
   derive their immutable expected digest maps from their own accepted evidence
   rather than the current intentionally empty map;
7. committed accepted mutable parse evidence and the protected historical
   failure evidence are not modified or staged by this candidate;
8. no Docker/PostgreSQL run, provider product call, applied migration,
   operational database, data, watcher/feed, behavior execution, app/API/Diary
   command, deployment, release, Pages or protected-ref authority is opened;
9. the exact 456-test packet, twelve-file Ruff, builder/inert checks and diff
   checks pass; and
10. HEAD and review worktree remain exact and clean after review.

Run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder --check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r149 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py
git diff --check c8ab760220bc40863a18feaa3fc13a3d6ba04ba6..2e59f606098b55e88bb2fbea0f0fdccaeb521193
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, access any product
surface or protected data, inspect `docs/branding/`, move refs or accept your
own output. Do not use any provider other than this exact Gemini verifier call.

## Decision rule

Return `fail` for any P0-P2 finding, accepting characterization, stale parent
binding, historical evidence coupling, incomplete packet or dirty
postcondition. Otherwise return one exact `pass` with commands/counts, HEAD and
cleanliness.
