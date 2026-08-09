# Independent veto: subtransaction-xmin durability recovery and behavior rebind

Date: 2026-08-10

Decision required: exactly one terminal structured `pass` or
`revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r141`
- Branch: `codex/review-context-fabric-subtransaction-xmin-f087bd30`
- Previously accepted behavior candidate baseline:
  `09c3e445f6514293d1ee27011b687c402605bd47`
- Candidate: `f087bd30a1c64eb5c276302b3efc261df420c145`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First read `AGENTS.md` completely and perform its complete five-source
rehydration, naming `live_handover_current_baton`,
`current_authority_allocation`, `active_plan_and_acceptance`,
`protected_evidence_boundaries`, and `git_refs_and_worktree`.

## Purpose and authority

Independently veto the bounded recovery after behavior attempt 029. The
candidate preserves that failure, diagnoses a PostgreSQL subtransaction/xmin
identity mismatch, changes only renderer lowering for typed UPDATE nodes,
regenerates the inert artifact, records a distinct non-accepting catalogue
characterization and exact reproduction, creates an accepted-source ledger,
and rebinds the unchanged frozen twenty-scenario behavior contract.

This is review only. Do not inherit any earlier decision. Do not edit, format,
commit, push, start Docker/PostgreSQL, run either runtime harness, contact any
product/provider surface other than this one verifier invocation, access
patient/clinical/product or protected data, inspect `docs/branding/`, move refs
or accept your own output.

## Required substantive challenges

1. Verify the worktree is clean at exact candidate
   `f087bd30a1c64eb5c276302b3efc261df420c145` before and after review.
2. Inspect exact diff
   `09c3e445f6514293d1ee27011b687c402605bd47..f087bd30a1c64eb5c276302b3efc261df420c145`.
3. Verify immutable attempt-029 evidence has SHA-256
   `09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`,
   stopped at `BTR-E02` / SQLSTATE `CF603` with zero completed scenarios,
   and records verified exact cleanup. Confirm the newer mutable evidence alias
   cannot substitute for the immutable file.
4. Verify provider-free diagnosis evidence and tests map the failure to the
   stream-head UPDATE in `project_update_confirm_reschedule_v1`, record zero
   diagnostic database runs, and preserve no raw PostgreSQL error.
5. Challenge the diagnosis against PostgreSQL 16 semantics: an `EXCEPTION`
   block forms a subtransaction; a row version written there can carry that
   subtransaction identity in `xmin`; `pg_current_xact_id()` denotes the
   top-level transaction; therefore comparing the row's `xmin` to the
   top-level xid makes the positive transaction structurally fail CF603.
6. Verify renderer 2.0.15 moves all 39 typed UPDATE nodes outside any
   renderer-owned `EXCEPTION` block, uses a non-STRICT `INTO`, and immediately
   maps `NOT FOUND` to the unchanged stable CF004 failure.
7. Verify `_derive_conflict_constraint` proves each declared UPDATE key maps to
   exactly one primary or unique constraint before direct UPDATE lowering.
   Hostile tests must reject a non-unique key and a changed or missing immediate
   CF004 guard.
8. Verify the repair does not change typed structural/body contracts,
   predicates, effects, triggers, roles, grants, failure identities, output
   shapes, RLS policy or frozen behavior scenarios.
9. Verify structural and body contracts remain bound to source
   `958f8178c872854ab0f8e1c56dbb9fe46afbea22`, with SHA-256
   `6b2ec35d7be7cd33f683173f5ac12ef4c95b0d1bbf05bccf50d10e74c9ca00bc`
   and `b43ea059a3f424e268631228aa9606d30f1c9f082bc805e550788b01e7bd8e76`.
10. Verify the regenerated inert artifact has 413 statements, 1,416,483
    canonical LF bytes and SHA-256
    `03150dfec61944df8f26ca2473200afa49e88ddcf9d9fce950320a2a98bd96e0`;
    render-manifest file SHA-256 must be
    `bb91292d98fb34f576fa7bf6b5a196eccdcd42f087624b70b450933e36638597`.
11. Verify non-accepting characterization attempt
    `25b98f1da5c8de4d06188a70` has evidence SHA-256
    `4d140704d33624e90737022e5f9d095559152bd56554514ccebc73222d845750`,
    reproduced all seventeen predecessor catalogue digests, and records exact
    container `8e351be5609f7d01eb18919321eb42ff02736ef64c68c8affa422356ed1eb9d9`
    removed and absent.
12. Verify distinct exact attempt `4ec417dfc5e16ad6e462e66d` uses canonical
    parse contract SHA-256
    `3dc318e64b9c30817c0e2cdca650fc284ae3d2f35e93e697d0cac5368fecbd03`,
    reproduces every characterized digest, and passes in evidence SHA-256
    `cb439eefe9eb243eb4eccda144ac51218d9e26ba71c0dd14402ee066b7c1fb14`
    with distinct container
    `f784718297efd8d11250a2a34bbf7a25627036d2fcb9c745fb6c56e954f6e517`
    removed and absent.
13. Verify the accepted-source ledger accurately binds evidence source commit
    `426fd229a96b7a34787dd0d0610a926808fd9961`, has file SHA-256
    `8273baa138a8302677ca76244bccdf6b4be511aa41400c12c0e7b625cce0e972`,
    and claims parse/catalogue, rollback, atomic install, privileges and cleanup
    only.
14. Verify all six behavior parents are exact: accepted-source ledger and
    parse prerequisite at `426fd229`; artifact/manifest at `561f5c89`; and
    unchanged structural/body contracts at `958f8178`.
15. Verify canonical behavior contract SHA-256 is
    `a7278f6d87a69e9c5c9daef0a5b3640bcd22d27a3aac597ee228584dcc06d740`.
16. Verify scenario order, objects and category coverage remain exactly twenty
    in `6/4/3/4/3`, with canonical population SHA-256
    `eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`.
17. Verify AER-0170 coherently records the subtransaction/xmin defect and
    bounded renderer repair; register revision 145 must contain 170 incidents
    and zero open. The behavior-plan continuity assertion must bind revision
    145 and the current final twelve incident IDs without rewriting history.
18. Verify historical attempt-025 through attempt-028 tests still validate
    immutable bytes/digests before consulting any optional mutable alias.
19. Verify GraphQL remains read-only, REST/OpenAPI command boundaries are
    unchanged, all Fabric outputs retain `command_authority: false`, and no
    application, Alembic, API Spine, Diary, provider or deployment code gained
    authority.
20. Verify any future behavior run remains fixed authored-synthetic,
    provider-free, `--pull=never`, `--network=none`, with no ports/mounts and
    exact-ID cleanup. Do not run it in this review.
21. Verify no patient, clinical, product-derived, historical-PHI or protected
    evidence enters the candidate or review.
22. Run the exact packet below and require exactly **525 tests**, all passed;
    run Ruff check and format over exactly **30 files**, and both diff checks.
23. Verify no Docker command or behavior/parse harness ran during review and
    exact protected refs remain unchanged.

## Exact test and static packet

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r141 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\ariadne_agent_error_register.py scripts\ariadne_antigravity.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\ariadne_agent_error_register.py scripts\ariadne_antigravity.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
git diff --check 09c3e445f6514293d1ee27011b687c402605bd47..f087bd30a1c64eb5c276302b3efc261df420c145
git diff --check
git status --short --branch
git rev-parse HEAD
```

Return `revision_required` for any P0-P2 finding, authority widening, evidence
mismatch, scenario drift, incomplete 525-test packet, invalid dispatch receipt
or dirty postcondition. Otherwise return one exact structured `pass`, stating
findings, commands/counts, exact HEAD and post-review cleanliness.
