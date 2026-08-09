# Independent veto packet: admission-row-shape clean-checkout repair

Date: 2026-08-10

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r148`
- Branch: `codex/review-context-fabric-admission-row-shape-fb2fd645`
- Original baseline: `df5352fb6964cad6e15195cfe8c9e17346a061b4`
- Rejected parent candidate: `094368904acb79b214c68e8521f789709a832db6`
- Replacement candidate: `fb2fd6451d13bedc93b2bf4b1ec102ba7ab9f9eb`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete `AGENTS.md` five-source rehydration and name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently decide whether the replacement preserves the accepted database
repair from rejected candidate `09436890` and correctly repairs the sole P2
clean-checkout test defect found by the first Gemini veto.

Read the committed first review receipt at
`orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-admission-row-shape-parent-recovery-review-receipt.json`.
It affirmed the row-shape/null-winner repair but returned `revision_required`
because the new failure-034 diagnosis test unconditionally opened intentionally
untracked mutable behavior evidence. A clean checkout therefore ran 319/320.

## Required challenges

Verify and report:

1. exact replacement HEAD, clean worktree, both exact diffs and protected refs;
2. the first veto remains immutable, schema-constrained, clean-postcondition
   evidence bound to rejected candidate `09436890`;
3. AER-0191 and register revision 165 accurately preserve that veto, 191 total
   incidents are corrected, and zero IDs remain open;
4. the failure-034 test still requires immutable failure and diagnosis evidence
   but accesses the protected mutable evidence only inside `if mutable.exists()`;
5. when mutable evidence exists, the test still checks both non-reuse of attempt
   034 and exact accepted restoration SHA-256
   `09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`;
6. the parent database repair is unchanged from `09436890`: canonical body
   SHA-256 `d60eb4bd018a5f9180985db10f9b18c92d797b45844fbba345871085da4834c3`,
   inert SQL SHA-256
   `ca22e47e847409f1ae8a81f62dd7f5f8402a43176d9015211f657204460fbdbb`,
   disjoint PRIMARY/CONFLICT row shapes, and `IS_NULL` for all typed-null
   insert-or-reload winner predicates;
7. no structural constraint, scenario, SQLSTATE, role, RLS, privilege,
   transaction fence, authority or containment boundary changed in the narrow
   `09436890..fb2fd645` repair;
8. builder and inert checks, the exact 321-test packet, scoped Ruff and diff
   checks all pass from this clean worktree; and
9. HEAD and worktree remain exact and clean after review.

Run this exact packet using the main-worktree interpreter and a unique basetemp:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder --check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r148 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_context_fabric_durability_behavior_failure_034_admission_row_shape_diagnosis.py tests\test_ariadne_agent_error_register.py
git diff --check df5352fb6964cad6e15195cfe8c9e17346a061b4..fb2fd6451d13bedc93b2bf4b1ec102ba7ab9f9eb
git diff --check 094368904acb79b214c68e8521f789709a832db6..fb2fd6451d13bedc93b2bf4b1ec102ba7ab9f9eb
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, contact any product
surface, access patient/clinical/product or protected data, inspect
`docs/branding/`, move refs or accept your own output. Do not use any provider
other than this one exact Gemini verifier call.

## Decision rule

Return `fail` for any P0-P2 finding, missing clean-checkout guard, weakened
mutable-evidence check, database artifact drift, incomplete packet, invalid
Ariadne evidence or dirty postcondition. Otherwise return one exact `pass` with
findings, commands/counts, HEAD and post-review cleanliness.
