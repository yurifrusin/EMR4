# Replacement independent veto: UUID minimum and behavior parent rebind

Date: 2026-08-09

Decision required: exactly one terminal structured `pass` or
`revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r137`
- Branch: `codex/review-context-fabric-uuid-minimum-behavior-795a0872`
- Accepted pre-failure baseline: `9d8c0ad9c62da749ff7331ebd9cb94f07ed142e2`
- Rejected predecessor candidate: `6672c547fe46bf304e7dceddb0dd01704bf68064`
- Replacement candidate: `795a0872d78bb6174a1038e29f24a4ba76f4ce0e`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Replacement-review rule

The predecessor review receipt
`orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-uuid-minimum-behavior-review-receipt.json`
is immutable `revision_required` provenance. It found no substantive
renderer, SQL, contract, scenario, API or containment defect. It correctly
rejected the candidate because one test unconditionally read a deliberately
untracked mutable behavior evidence file, producing `FileNotFoundError` in the
clean checkout: 483 passed and 1 failed.

The replacement candidate makes only the bounded clean-checkout verification
repair and records AER-0163. The diagnosis test still always hashes and
validates tracked immutable attempt-025 evidence; it compares the optional
mutable evidence only when that file exists. The mutable file is not admitted,
tracked or required. No renderer, SQL artifact, parse contract, behavior
contract, scenario, API surface or runtime boundary changed in this repair.

Do not inherit the predecessor's decision. Independently re-run the complete
review against the replacement candidate.

## Required review

Read and apply every purpose, allowed-surface restriction, challenge and
forbidden-action rule in the tracked predecessor packet:

`orchestration/agent_inbox/codex/raisa-context-fabric-durability-uuid-minimum-behavior-gemini-review-packet.md`

All twenty-one substantive challenges remain mandatory, with these exact
replacement adjustments:

1. use worktree `r137`, its replacement branch and exact candidate
   `795a0872d78bb6174a1038e29f24a4ba76f4ce0e`;
2. inspect both `9d8c0ad9..795a0872` and the bounded repair diff
   `6672c547..795a0872`;
3. verify the predecessor receipt remains `revision_required` and is not
   represented as acceptance;
4. verify AER-0163 accurately records recurrence key
   `repository.clean_checkout_mutable_fixture_dependency`, the clean-checkout
   `FileNotFoundError`, repository-defect attribution and closed correction;
5. verify register revision 138 has 163 incidents and zero open incidents;
6. verify the test always validates immutable tracked attempt-025 evidence at
   SHA-256
   `b963933df05c418456fdc1e101a7254a617ba743a4cb4b03888caf0aac547ba2`,
   while absence of mutable evidence cannot weaken that assertion;
7. run the exact packet below in the clean checkout and require exactly **485
   tests**, all passed; and
8. require clean exact HEAD before and after review, with no Docker or runtime
   harness execution.

A `pass` only makes one later Sol-owned disposable behavior attempt 026
eligible. It does not accept that future run. No behavior runtime is authorized
by this review.

## Exact test and static packet

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r137 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\ariadne_antigravity.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\ariadne_antigravity.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py
git diff --check 9d8c0ad9c62da749ff7331ebd9cb94f07ed142e2..795a0872d78bb6174a1038e29f24a4ba76f4ce0e
git diff --check 6672c547fe46bf304e7dceddb0dd01704bf68064..795a0872d78bb6174a1038e29f24a4ba76f4ce0e
git diff --check
git status --short --branch
git rev-parse HEAD
```

Do not edit, format, commit, push, start Docker/PostgreSQL, run either runtime
harness, contact any product/provider surface other than this one verifier
invocation, access patient/clinical/product or protected data, inspect
`docs/branding/`, move refs or accept your own output.

Return `revision_required` for any P0-P2 finding, invalid UUID lowering,
evidence mismatch, scenario drift, incomplete 485-test packet, API/authority
widening, invalid dispatch receipt or dirty postcondition. Otherwise return one
exact structured `pass`, stating findings, commands/counts, exact HEAD and
post-review cleanliness.
