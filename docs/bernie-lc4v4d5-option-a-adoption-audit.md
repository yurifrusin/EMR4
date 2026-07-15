# LC4V4D5 Option A Adoption Audit Evidence

- Source commit: `1ac0c71b929cff610f78d2ed8a803b057627d31e`
- Report hash: `sha256:350d7a2bca61320f6397e7ab15b333ec3ef0d247970e7365813886a9add9a94a`
- Fixture hash: `sha256:a81de0b5371d4fcc425c23f0da9560e29827e3e85cc22847990ea83518863269`
- All-60 population hash: `sha256:ed65fe7821b0239066c532320bff05cc31a0699674987de8587efd74e05bbd44`
- D2 report hash: `sha256:3220ac943659ae1449c5c285144b1fa980f659668a705ca7aef98f0aea6d317a`
- D3 report hash: `sha256:94b751aea657696329c6b6d394253aef3ef0dbe82316e7725efc1c16fac523a8`
- D4 report hash: `sha256:dd1ecc077a59bf05e777eda1f3a5450c0a1b97a4c8a3fd21dc0363d473abd653`
- D4 selection hash: `sha256:d3c6618cb586f5dc43824ec7a6e9e33957fee587a45c19f89e5a4bb425006e2a`
- Legacy 60-probe baseline hash: `sha256:665851ffe055efb40f2ba1e43291d6b945c4764b4f441837781d4fc964d6ff27`
- Five-difference selection hash: `sha256:b06da04e89b195b6de271b7ca4b8c22453426917b1d8c76389e4d41bf727aec7`
- Probes: 60
- Option A observations: 120
- Decision: `option_a_adoption_audit_valid_with_4_blockers`

## Gates

- all_60_population_valid: `True`
- all_60_population_hash_exact: `True`
- d1_fixture_hash_exact: `True`
- d2_report_valid: `True`
- d3_report_valid: `True`
- d4_report_committed_hash_valid: `True`
- d4_dynamic_gates_pass: `True`
- exact_d4_population: `True`
- d4_selection_hash_exact: `True`
- legacy_60_baseline_hash_exact: `True`
- all_option_a_ran: `True`
- exact_legacy_equivalent_count: `True`
- exact_d4_versioned_change_count: `True`
- exact_expected_versioned_relation_count: `True`
- exact_blocker_missing_mutation_count: `True`
- exact_blocker_target_field_conflict_count: `True`
- no_unexpected_differences: `True`
- exact_five_difference_ids: `True`
- five_difference_selection_hash_exact: `True`
- exact_four_blocker_ids: `True`
- zero_option_a_variance: `True`
- zero_forbidden_observations: `True`
- authoring_invalid_quarantined: `True`
- authoring_invalid_legacy_equivalent: `True`

## Classification Counts

- legacy_equivalent: 35 (expected 35) [OK]
- accepted_d4_versioned_change: 20 (expected 20) [OK]
- expected_versioned_relation: 1 (expected 1) [OK]
- adoption_blocker_missing_mutation_deltas: 3 (expected 3) [OK]
- adoption_blocker_target_field_conflict_and_missing_mutation_deltas: 1 (expected 1) [OK]

## Five New Differences

- lc4v4d1_diary_exact_duplicate_02
- lc4v4d1_safety_cancel_safe_07
- lc4v4d1_safety_move_safe_03
- lc4v4d1_safety_resize_safe_05
- lc4v4d1_safety_status_safe_09

## Four Adoption Blockers

- lc4v4d1_safety_cancel_safe_07: adoption_blocker_missing_mutation_deltas
  - Field difference: diary_relation
  - Field difference: replay.appointment_deltas
  - Field difference: replay.audit_deltas
  - Field difference: replay.is_simulated_confirmed_write
- lc4v4d1_safety_move_safe_03: adoption_blocker_missing_mutation_deltas
  - Field difference: replay.appointment_deltas
  - Field difference: replay.audit_deltas
  - Field difference: replay.is_simulated_confirmed_write
- lc4v4d1_safety_resize_safe_05: adoption_blocker_target_field_conflict_and_missing_mutation_deltas
  - Field difference: conflicting_fields
  - Field difference: diary_relation
  - Field difference: interpretation.authority_claim
  - Field difference: interpretation.requires_clarification
  - Field difference: interpretation.selected_tool_sequence
  - Field difference: replay.appointment_deltas
  - Field difference: replay.audit_deltas
  - Field difference: replay.downstream_outcome
  - Field difference: replay.is_simulated_confirmed_write
  - Field difference: replay.tools_used
- lc4v4d1_safety_status_safe_09: adoption_blocker_missing_mutation_deltas
  - Field difference: diary_relation
  - Field difference: replay.appointment_deltas
  - Field difference: replay.audit_deltas
  - Field difference: replay.is_simulated_confirmed_write

## Authoring-Invalid Cases (Quarantined)

- lc4v4d1_dialogue_ellipsis_multi_08 (legacy-equivalent)
- lc4v4d1_entity_duration_corrected_28 (legacy-equivalent)
- lc4v4d1_entity_duration_negated_29 (legacy-equivalent)

## Boundary

D5 is a development-wide diagnostic audit only.  No remediation, parser change, fixture rewrite, default-version switch, or product/write claim is authorized.  Four adoption blockers are recorded for a separate bounded policy/replay remediation plan after acceptance.

Holdouts v1-v4 remain sealed. T3.1-T3.4 remain blocked. T3.5/live providers, product runtime, API/UI/database/write authority, historical diary, deployment, and release remain deferred.
