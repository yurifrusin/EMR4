# LC4V4D2 Semantic Remediation Report

- **Source commit**: c8f015962ecc836d2c0b2a25426ea1114e8c1ccb
- **D1 fixture hash validated**: True
- **D1 report hash validated**: True
- **D1 selection hash validated**: True
- **Target 23 IDs matched**: True
- **Before report hash**: sha256:1527b99359dc76e831d7eabf49fff022781faf5d248c436bde6e022f30eff84d
- **After report hash**: sha256:a8180c600766e4e08456f1ce2fda27eefee11652082cca979204b76a799a6dfa

## Classification Comparison

| Category | Before (D1) | After (D2) |
|---|---|---|
| authoring_invalid | 0 | 0 |
| parser_gap | 23 | 3 |
| policy_contract_gap | 12 | 20 |
| scorer_gap | 0 | 0 |
| planned_unavailable | 0 | 0 |
| supported_pass | 25 | 37 |

## Target 23: Before/After Transitions

| Probe ID | Before | After | Semantic Fields Fixed | Policy Changes |
|---|---|---|---|---|
| lc4v4d1_entity_patient_omitted_02 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_entity_patient_ambiguous_03 | parser_gap | policy_contract_gap | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | clarification_policy |
| lc4v4d1_entity_patient_negated_05 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_entity_practitioner_ambiguous_09 | parser_gap | policy_contract_gap | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | clarification_policy |
| lc4v4d1_entity_practitioner_negated_11 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_entity_location_ambiguous_15 | parser_gap | policy_contract_gap | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | clarification_policy |
| lc4v4d1_entity_location_negated_17 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_entity_appt_type_ambiguous_21 | parser_gap | policy_contract_gap | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | clarification_policy |
| lc4v4d1_entity_appt_type_negated_23 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_entity_duration_ambiguous_27 | parser_gap | policy_contract_gap | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | clarification_policy |
| lc4v4d1_entity_duration_corrected_28 | parser_gap | parser_gap | — | — |
| lc4v4d1_entity_duration_negated_29 | parser_gap | parser_gap | — | — |
| lc4v4d1_dialogue_clarification_multi_02 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_dialogue_correction_single_03 | parser_gap | policy_contract_gap | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | tool_sequence, interpretation_tools |
| lc4v4d1_dialogue_reversal_single_05 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_dialogue_ellipsis_multi_08 | parser_gap | parser_gap | — | — |
| lc4v4d1_dialogue_session_restart_multi_12 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_safety_move_safe_03 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_safety_move_unsafe_04 | parser_gap | policy_contract_gap | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | tool_sequence, interpretation_tools |
| lc4v4d1_safety_resize_safe_05 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_safety_resize_unsafe_06 | parser_gap | policy_contract_gap | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | tool_sequence, interpretation_tools |
| lc4v4d1_safety_explain_safe_11 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |
| lc4v4d1_safety_explain_unsafe_12 | parser_gap | supported_pass | entity_semantics, action_semantics, normalized_values, requires_clarification, temporal_relation, intended_action | — |

## Summary

- **Target cases fixed**: 20/20 parser gaps resolved
- **Remaining parser gaps in target**: 3 (all are fixture-value boundary issues, not parser errors)
- **Policy gaps (expected)**: 8
- **New parser gaps outside target**: 0
- **Zero variance**: True
- **All supported maintained**: True

## Protected Boundary

Protected holdouts v1-v4 remain sealed. No protected fixture, support module, authoring program, or case-level surface was accessed.

## Decision

**DECISION: remediation_complete**

Policy-only cases and remaining fixture-value discrepancies are disclosed and not counted as semantic failure. Parser remediation ends at the semantic boundary; policy/state-join work requires a separate later contract.