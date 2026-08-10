# Independent veto packet: parse exact evidence and routing recovery

Date: 2026-08-10

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r151`
- Branch: `codex/review-context-fabric-parse-exact-evidence-58538b3b`
- Accepted source parent: `c8ab7602e16e24453dbf909597b4f702a2388416`
- Candidate: `58538b3b98de4bf4f62a0eef898439d674f3f987`
- Protected refs: exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform and name the complete five-source `AGENTS.md` rehydration.

## Purpose

Independently decide whether the candidate immutably preserves the successful
non-accepting admission-row-shape characterization, binds its exact catalogue
digests for a distinct reproduction, and repairs evidence routing without
altering protected accepted or historical failure evidence.

## Required challenges

Verify and report:

1. exact candidate HEAD, clean worktree, protected refs and the exact
   `71064767fd91676ff5e3e6706b8340c840784912..58538b3b98de4bf4f62a0eef898439d674f3f987`
   diff;
2. immutable characterization evidence SHA-256 is exactly
   `fc2268693334c03d6aed78efca8f58d1ba654c1cd0f32709a1ef2d24fd1a5c63`,
   attempt is `2fb9bbacbd4cd172aec49c51`, result is
   `catalogue_characterization_required`, parent contract is `a34fb467...`,
   inert artifact is `ca22e47e...`, and cleanup binds exact container
   `6515210c07830a7d6df037d12887ecf05961b5c34323e378a3186a9a2f4cd600`;
3. current contract is `exact_digest_bound`, canonical SHA-256 is exactly
   `b81be9b783ba102a663fd3244ee4d1a81c4a2320745aa6f6eac537821b6e1e79`,
   and its 15 values equal the characterization query digests after excluding
   only `server` and `extensions`;
4. the accepted source head resolves exactly as a commit, the inert SQL remains
   exactly 1,435,142 LF bytes, 421 statements and SHA-256 `ca22e47e...`;
5. pass, characterization-required and all other failures have three distinct
   evidence targets; mutation-oriented tests prove no target aliasing and no
   cross-overwrite;
6. AER-0194 and revision 168 accurately preserve the temporary routing defect,
   byte-exact restoration, zero second run and correction without overstating
   acceptance;
7. mutable accepted evidence remains SHA-256 `97d1385c...`, protected
   historical failure remains `3bf66870...`, and neither is tracked, modified
   nor staged by this candidate;
8. the exact 462-test packet, twelve-file Ruff check/format, builder and inert
   checks pass;
9. no Docker/PostgreSQL run, applied migration, operational database,
   source/watcher/listener/feed, product/patient/clinical data, app/API/Diary
   command, deployment, production, release, Pages or protected-ref action is
   opened; and
10. exact HEAD and clean worktree remain unchanged after review.

Run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder --check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r151 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py
git rev-parse --verify c8ab7602e16e24453dbf909597b4f702a2388416^{commit}
git diff --check 71064767fd91676ff5e3e6706b8340c840784912..58538b3b98de4bf4f62a0eef898439d674f3f987
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, inspect branding,
access product/protected data, move refs or accept your own output. No provider
other than this exact Gemini verifier call is allowed.

## Decision rule

Return `fail` for any P0-P2 finding, digest mismatch, evidence-path alias,
protected-evidence mutation, incomplete 462-test packet or dirty postcondition.
Otherwise return one exact `pass` with commands, counts, HEAD and cleanliness.
