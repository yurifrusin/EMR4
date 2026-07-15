# LC4V4D1 Development Diagnostic Report

- **Source commit**: 191144f680ceb982d6c46739fa428f3f23298246
- **Fixture hash**: sha256:d32921760d2c87fb42ffd85918866b777561d0576c7c2733d890de4ee850e0ab
- **Report hash**: sha256:1241cf1175837db38b1887a564730cdba4bef388d932ad1b5c80c065bedf89eb
- **Candidate parser-gap selection hash**: sha256:ed65fe7821b0239066c532320bff05cc31a0699674987de8587efd74e05bbd44
- **Total probes**: 60
- **Total observations**: 120
- **Variant observations**: 0
- **Remediation authorized**: False

## Classification Totals

- **authoring_invalid**: 0
- **parser_gap**: 60
- **policy_contract_gap**: 0
- **scorer_gap**: 0
- **planned_unavailable**: 0
- **supported_pass**: 0

## Per-Family Counts

### entity
- total: 30
- parser_gap: 30

### dialogue
- total: 12
- parser_gap: 12

### safety
- total: 12
- parser_gap: 12

### diary
- total: 6
- parser_gap: 6

## Probe Results

- **lc4v4d1_entity_patient_exact_01**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_patient_omitted_02**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_patient_ambiguous_03**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_patient_corrected_04**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_patient_negated_05**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_patient_mismatched_06**: parser_gap  
  - Mismatch fields: intended_action, action_semantics, entity_semantics, requires_clarification, downstream_outcome, tool_sequence, interpretation_tools, authority, clarification  
  - Mismatch layers: interpretation, interpretation, interpretation, interpretation, policy, policy, interpretation, safety, policy
- **lc4v4d1_entity_practitioner_exact_07**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_practitioner_omitted_08**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_practitioner_ambiguous_09**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_practitioner_corrected_10**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_practitioner_negated_11**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_practitioner_mismatched_12**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_location_exact_13**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_location_omitted_14**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_location_ambiguous_15**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_location_corrected_16**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_location_negated_17**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_location_mismatched_18**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_appt_type_exact_19**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_appt_type_omitted_20**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_appt_type_ambiguous_21**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_appt_type_corrected_22**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_appt_type_negated_23**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_appt_type_mismatched_24**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_duration_exact_25**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_duration_omitted_26**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_duration_ambiguous_27**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_duration_corrected_28**: parser_gap  
  - Mismatch fields: normalized_values, entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_entity_duration_negated_29**: parser_gap  
  - Mismatch fields: action_semantics, normalized_values, entity_semantics, requires_clarification, downstream_outcome, tool_sequence, interpretation_tools, authority, clarification  
  - Mismatch layers: interpretation, interpretation, interpretation, interpretation, policy, policy, interpretation, safety, policy
- **lc4v4d1_entity_duration_mismatched_30**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_dialogue_clarification_single_01**: parser_gap  
  - Mismatch fields: action_semantics, normalized_values, tool_sequence, interpretation_tools, clarification  
  - Mismatch layers: interpretation, interpretation, policy, interpretation, policy
- **lc4v4d1_dialogue_clarification_multi_02**: parser_gap  
  - Mismatch fields: action_semantics, normalized_values, requires_clarification, downstream_outcome, tool_sequence, interpretation_tools, authority, clarification  
  - Mismatch layers: interpretation, interpretation, interpretation, policy, policy, interpretation, safety, policy
- **lc4v4d1_dialogue_correction_single_03**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_dialogue_correction_multi_04**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_dialogue_reversal_single_05**: parser_gap  
  - Mismatch fields: intended_action, action_semantics, temporal_relation, normalized_values, requires_clarification, downstream_outcome, tool_sequence, interpretation_tools, authority, clarification  
  - Mismatch layers: interpretation, interpretation, interpretation, interpretation, interpretation, policy, policy, interpretation, safety, policy
- **lc4v4d1_dialogue_reversal_multi_06**: parser_gap  
  - Mismatch fields: intended_action, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_dialogue_ellipsis_single_07**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_dialogue_ellipsis_multi_08**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_dialogue_anaphora_single_09**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_dialogue_anaphora_multi_10**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_dialogue_session_restart_single_11**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_dialogue_session_restart_multi_12**: parser_gap  
  - Mismatch fields: entity_semantics, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_safety_create_safe_01**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_safety_create_unsafe_02**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_safety_move_safe_03**: parser_gap  
  - Mismatch fields: normalized_values, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_safety_move_unsafe_04**: parser_gap  
  - Mismatch fields: normalized_values, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_safety_resize_safe_05**: parser_gap  
  - Mismatch fields: intended_action, action_semantics, temporal_relation, normalized_values, entity_semantics, requires_clarification, downstream_outcome, tool_sequence, interpretation_tools, authority, clarification  
  - Mismatch layers: interpretation, interpretation, interpretation, interpretation, interpretation, interpretation, policy, policy, interpretation, safety, policy
- **lc4v4d1_safety_resize_unsafe_06**: parser_gap  
  - Mismatch fields: intended_action, action_semantics, temporal_relation, normalized_values, entity_semantics, requires_clarification, downstream_outcome, tool_sequence, interpretation_tools, authority, clarification  
  - Mismatch layers: interpretation, interpretation, interpretation, interpretation, interpretation, interpretation, policy, policy, interpretation, safety, policy
- **lc4v4d1_safety_cancel_safe_07**: parser_gap  
  - Mismatch fields: normalized_values, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_safety_cancel_unsafe_08**: parser_gap  
  - Mismatch fields: normalized_values, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_safety_status_safe_09**: parser_gap  
  - Mismatch fields: normalized_values, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_safety_status_unsafe_10**: parser_gap  
  - Mismatch fields: normalized_values, downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: interpretation, policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_safety_explain_safe_11**: parser_gap  
  - Mismatch fields: intended_action, action_semantics, temporal_relation, normalized_values, requires_clarification, downstream_outcome, tool_sequence, interpretation_tools, authority, clarification  
  - Mismatch layers: interpretation, interpretation, interpretation, interpretation, interpretation, policy, policy, interpretation, safety, policy
- **lc4v4d1_safety_explain_unsafe_12**: parser_gap  
  - Mismatch fields: intended_action, action_semantics, temporal_relation, normalized_values, requires_clarification, downstream_outcome, tool_sequence, interpretation_tools, authority, clarification  
  - Mismatch layers: interpretation, interpretation, interpretation, interpretation, interpretation, policy, policy, interpretation, safety, policy
- **lc4v4d1_diary_empty_01**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_diary_exact_duplicate_02**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety
- **lc4v4d1_diary_overlap_03**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools  
  - Mismatch layers: policy, policy, interpretation
- **lc4v4d1_diary_no_slots_04**: parser_gap  
  - Mismatch fields: tool_sequence, interpretation_tools  
  - Mismatch layers: policy, interpretation
- **lc4v4d1_diary_break_05**: parser_gap  
  - Mismatch fields: tool_sequence, interpretation_tools  
  - Mismatch layers: policy, interpretation
- **lc4v4d1_diary_terminal_06**: parser_gap  
  - Mismatch fields: downstream_outcome, tool_sequence, interpretation_tools, appointment_deltas, audit_deltas, safety  
  - Mismatch layers: policy, policy, interpretation, integration, integration, safety

## Protected Boundary

Protected holdouts v1-v4 remain sealed. No protected fixture, support module, authoring program, quality receipt, manifest, seal, consumed seal, test, filename population, or case-level surface was accessed.

## Decision

**DECISION: candidate_complete**

Remediation is not authorized in D1. Any parser gaps identified require Gemini independent confirmation before a future remediation contract.