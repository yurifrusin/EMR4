# Independent veto packet: source-membership fixture recovery

Date: 2026-08-10

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r146`
- Branch: `codex/review-context-fabric-source-membership-5d8c460c`
- Baseline: `b980fe2d0b4dc9a318c820f388a0e9fad34cfa6f`
- Candidate: `5d8c460c1ff5bda22dccf2036f96f021eabf664f`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name:

1. `live_handover_current_baton`;
2. `current_authority_allocation`;
3. `active_plan_and_acceptance`;
4. `protected_evidence_boundaries`; and
5. `git_refs_and_worktree`.

## Purpose

Independently decide whether behavior attempt 033 was correctly diagnosed as
an authored-synthetic source-membership fixture defect and whether the
candidate repairs only that defect without weakening the accepted database
body, transaction, authority, isolation, scenario or evidence contracts.

Attempt 033 reached `BTR-E03` and the accepted admission body rejected the
packet with SQLSTATE `CF201` at line 100 of
`emr4_context_fabric.admit_proofread_observation_v1`. The candidate asserts
that the fixture incorrectly substituted `outbox.source_contract_digest` for
the distinct canonical `source_membership_digest_v1` over the complete eleven-
field same-locator immutable outbox row.

## Allowed review surface

Review the exact baseline-to-candidate diff and these files:

- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-source-membership-fixture-recovery.md`
- `docs/security/raisa-provider-free-disposable-postgresql-durability-behavior-source-membership-fixture-recovery-threat-model-delta.md`
- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-plan.md`
- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-design.md`
- `docs/ariadne-agent-error-correction-register-revision-160.md`
- `docs/ariadne-agent-error-correction-register-revision-161.md`
- `docs/ariadne-agent-error-correction-register-revision-162.md`
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`
- `orchestration/continuity/ariadne-agent-error-register/pattern-report.json`
- the behavior contract and schema under the behavior-rehearsal continuity directory;
- immutable failure and diagnosis evidence 033 in that directory;
- the accepted function/trigger body contract, inert DDL and render manifest;
- `scripts/raisa_context_fabric_durability_behavior_failure_033_source_membership_fixture_diagnosis.py`
- `scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`
- the four changed tests; and
- the exact Ariadne provenance files in the baseline-to-candidate diff.

You may read directly imported repository modules and the exact design/threat
paragraphs cited by the recovery ledger. Do not open, enumerate or search any
protected holdout, historical Diary, branding, patient, product-derived or
unrelated path. Do not use repository-wide search outside this exact packet.

## Required challenges

Verify and report:

1. candidate HEAD, exact baseline-to-candidate diff, clean checkout and exact
   protected refs;
2. immutable failure 033 validates against its evidence schema, records
   `BTR-E03`, `CF201`, the exact admission function and line 100, zero admitted
   scenarios, verified exact cleanup, and has file SHA-256
   `5a6d5bcc18cd23f0fa528e5cdd33e53e9f0b90c0415a8f86ca326cf47980c8ad`;
3. diagnosis evidence has SHA-256
   `08eaac2d10b3dd4488251056cdd6fd0d73ba674dd423d2205ff5bc245215110b`,
   binds the accepted unique digest node/profile and proves the eleven ordered
   same-locator outbox operands rather than one component digest;
4. the accepted body contract, inert DDL and render manifest are byte-identical
   to baseline; no accepted database function, trigger, grant, role, RLS,
   SQLSTATE, isolation or rollback behavior changed;
5. before any Docker contact, the harness now loads the accepted body contract,
   requires exactly one canonical source-membership digest node and profile,
   verifies the exact relation/operand tuple, renders that expression through
   the accepted inert renderer and requires the expression in the bound inert
   artifact;
6. the authored-synthetic BTR-E03 packet obtains its source-membership digest
   from the complete same-locator outbox row and its readback independently
   recomputes the same full-row digest; `source_contract_digest` remains a
   separately bound component rather than being conflated with membership;
7. the only behavior-contract meaning change is the corrected
   `canonical_digest_of_complete_same_locator_outbox_row` fixture rule; all
   twenty scenario objects, their order, and category counts `6/4/3/4/3`
   retain canonical population SHA-256
   `eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`;
8. hostile tests reject profile, operand-order, relation and bound-artifact
   drift before runtime contact;
9. AER-0186 through AER-0188 are coherent, register revision is 162, incident
   count is 188, every incident is corrected, and the generated pattern report
   has zero open incident IDs; the original attempt-033 preexecution `passed`
   receipt is explicitly rejected because exact deterministic reproduction
   returns `revision_required`;
10. no Docker profile, credential, network, mount, port, product/provider/data,
    watcher/listener/feed, API/command, deployment, release, Pages or
    protected-ref boundary widened;
11. the exact 572-test packet, Ruff lint/format checks on the 38 scoped Python
    files, and diff checks pass; and
12. HEAD and worktree remain exact and clean after review.

Run the following exact deterministic packet using the main worktree
interpreter and a unique basetemp:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r146 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_030_support_execute_grant_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_031_admission_receiver_binding_rls_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_032_input_column_ambiguity_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_033_source_membership_fixture_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_030_support_execute_grant_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_031_admission_receiver_binding_rls_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_032_input_column_ambiguity_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_033_source_membership_fixture_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\ariadne_agent_error_register.py scripts\ariadne_antigravity.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_030_support_execute_grant_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_031_admission_receiver_binding_rls_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_032_input_column_ambiguity_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_033_source_membership_fixture_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_030_support_execute_grant_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_031_admission_receiver_binding_rls_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_032_input_column_ambiguity_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_033_source_membership_fixture_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\ariadne_agent_error_register.py scripts\ariadne_antigravity.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_026_json_keys_order_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_027_alias_lock_visibility_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_028_dml_name_ambiguity_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_029_subtransaction_xmin_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_030_support_execute_grant_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_031_admission_receiver_binding_rls_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_032_input_column_ambiguity_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_033_source_membership_fixture_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
```

Also run:

```powershell
git diff --check b980fe2d0b4dc9a318c820f388a0e9fad34cfa6f..5d8c460c1ff5bda22dccf2036f96f021eabf664f
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run the behavior
harness, contact a product surface, access patient/clinical/product or
protected data, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `fail` for any P0-P2 finding, wrong evidence hash/coordinate, component-
digest substitution, accepted body/SQL/role/RLS/scenario drift, widened
containment, incomplete deterministic packet, invalid Ariadne acceptance or
dirty postcondition. Otherwise return one exact `pass`. State findings,
commands/counts, HEAD and post-review cleanliness.
