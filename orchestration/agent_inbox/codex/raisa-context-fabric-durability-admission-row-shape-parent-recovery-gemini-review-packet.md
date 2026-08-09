# Independent veto packet: admission-row-shape parent recovery

Date: 2026-08-10

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r147`
- Branch: `codex/review-context-fabric-admission-row-shape-09436890`
- Baseline: `df5352fb6964cad6e15195cfe8c9e17346a061b4`
- Candidate: `094368904acb79b214c68e8521f789709a832db6`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently decide whether behavior attempt 034 correctly exposed a parent
body defect and whether the candidate repairs that defect without weakening
the accepted structural constraint, authority, isolation, transaction,
scenario or evidence boundaries.

Attempt 034 reached `BTR-E03`; PostgreSQL rejected the first PRIMARY admission
insert with SQLSTATE `23514` and admitted zero scenarios. Deterministic
diagnosis asserts two defects in the accepted generator:

1. one shared binding population contradicted `ck_cf_04_02` by placing
   `attempted_admission_digest` on PRIMARY rows and five PRIMARY-only outcome
   fields on CONFLICT rows; and
2. five insert-or-reload winner predicates used ordinary `EQ` against typed
   null values rather than `IS_NULL`.

## Required challenges

Verify and report:

1. exact candidate HEAD, clean review worktree, exact baseline-to-candidate
   diff and protected refs;
2. immutable failure 034 validates, records `BTR-E03`, SQLSTATE `23514`, zero
   observed scenarios and verified cleanup, and has file SHA-256
   `68d61a9c55c800ca1670c6e0e7cde3e720486a82e2125649f64375844c09262a`;
3. diagnosis is bound to historical source HEAD `df5352fb`, the historical
   body/structural/entry-program/inert sources, and opens no additional
   database run;
4. `ck_cf_04_02` remains unchanged: PRIMARY has exactly five non-null outcome
   fields and null attempted digest/conflict reason; CONFLICT has null outcome
   fields and non-null attempted digest/conflict reason;
5. the generator emits those disjoint row projections for all PRIMARY and
   CONFLICT branches and cannot select kind or fields from runtime data;
6. every typed-null winner binding lowers to `IS_NULL`, no winner predicate
   uses `EQ` against typed null, and non-null comparisons remain exact `EQ`;
7. hostile tests enumerate both row shapes and every null-bound winner column;
8. regenerated canonical body SHA-256 is
   `d60eb4bd018a5f9180985db10f9b18c92d797b45844fbba345871085da4834c3`;
   inert SQL has 421 statements, 1,435,142 LF bytes and SHA-256
   `ca22e47e847409f1ae8a81f62dd7f5f8402a43176d9015211f657204460fbdbb`;
9. the expression population legitimately falls from 14,488 to 14,397 only
   because forbidden opposite-kind values are no longer constructed; 756
   nodes, 23 effective programs, 21 insert-or-reload operations and all
   structural/catalogue populations remain coherent;
10. AER-0189 records the repository defect, AER-0190 records and corrects the
    masked builder-command failure, register revision is 164 with 190 corrected
    incidents and zero open IDs;
11. no scenario, SQLSTATE, role, privilege, RLS policy, transaction fence,
    operational database, watcher/feed, patient/product/clinical data,
    provider product path, application/API/Diary command, deployment, release,
    Pages or protected-ref boundary widened;
12. builder and inert checks, the exact 320-test packet, scoped Ruff checks and
    diff checks pass; and
13. HEAD and review worktree remain exact and clean after review.

Run this deterministic packet with the main-worktree interpreter and a unique
basetemp:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder --check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r147 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py
git diff --check df5352fb6964cad6e15195cfe8c9e17346a061b4..094368904acb79b214c68e8521f789709a832db6
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, contact any product
surface, access patient/clinical/product or protected data, inspect
`docs/branding/`, move refs or accept your own output. Do not use any provider
other than the one exact Gemini verifier call made by the orchestrator.

## Decision rule

Return `fail` for any P0-P2 finding, row-shape mismatch, remaining null-equality
bug, unjustified population drift, weakened database guard, incomplete packet,
invalid Ariadne evidence or dirty postcondition. Otherwise return one exact
`pass` with findings, commands/counts, HEAD and post-review cleanliness.
