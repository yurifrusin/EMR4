# Bernie LC4V4D5R1 Exact-Four Remediation

Decision: `d5r1_taxonomy_valid`

## Result

- legacy-equivalent: 37
- accepted D4 versioned changes: 20
- expected versioned relations: 3
- remaining blockers: 0
- complete typed observations: 240
- report hash: `sha256:0cb444d1aeba82a80f5a16170b30b8ea203842dec4af81b768a688e5aae9bcdf`

## Gates

- exact_probe_count: `True`
- population_valid: `True`
- fixture_hash_exact: `True`
- population_hash_exact: `True`
- legacy_60_hash_exact: `True`
- d4_historical_report_valid: `True`
- d5_historical_report_valid: `True`
- d4_dynamic_gates_pass: `True`
- d4_cases_exact_to_committed_report: `True`
- exact_legacy_equivalent_count: `True`
- exact_d4_versioned_change_count: `True`
- exact_expected_versioned_relation_count: `True`
- zero_adoption_blockers: `True`
- zero_unexpected_differences: `True`
- zero_option_a_failures: `True`
- authoring_invalid_ids_exact: `True`
- authoring_invalid_legacy_equivalent: `True`
- repaired_move_safe_03_legacy_equivalent: `True`
- repaired_resize_safe_05_legacy_equivalent: `True`
- expected_relations_only_diary_relation_diffs: `True`
- exact_three_relation_selection_hash: `True`
- exact_four_target_selection_hash: `True`
- empty_blocker_selection_hash: `True`
- unsafe_cases_still_refused: `True`
- zero_legacy_variance: `True`
- zero_option_a_variance: `True`
- exact_observation_counts: `True`
- zero_forbidden_observations: `True`

## Boundary

Development-only replay evidence. Holdouts v1-v4 remain sealed; 
T3.1-T3.4 remain blocked and T3.5/provider/product/write authority remains deferred.
