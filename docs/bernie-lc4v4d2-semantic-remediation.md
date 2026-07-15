# LC4V4D2 Semantic Remediation Report

- Source commit: `862c34bbda6d2544c63263155d9e3915d5b557df`
- Report hash: `sha256:3220ac943659ae1449c5c285144b1fa980f659668a705ca7aef98f0aea6d317a`
- Frozen D1 report hash: `sha256:1527b99359dc76e831d7eabf49fff022781faf5d248c436bde6e022f30eff84d`
- Valid 20-case selection hash: `sha256:0badec28ad533b630786d245e5ab47dee5655b83239869f7d0a2d12a8935d105`
- Valid parser targets fixed: 20/20
- Two-repeat variance: 0
- Decision: `semantic_remediation_valid_with_d1_quarantine`

## Classification reconciliation

| View | Authoring invalid/quarantine | Parser gap | Policy gap | Supported |
|---|---:|---:|---:|---:|
| D1 raw | 0 | 23 | 12 | 25 |
| D1 adjudicated | 3 | 20 | 12 | 25 |
| D2 raw | 3 | 0 | 20 | 37 |
| D2 adjudicated | 3 | 0 | 20 | 37 |

## D1 authoring quarantine

- `lc4v4d1_entity_duration_corrected_28`: final corrected duration contradicts the frozen normalized value.
- `lc4v4d1_entity_duration_negated_29`: excluded duration is retained as the frozen normalized value.
- `lc4v4d1_dialogue_ellipsis_multi_08`: explicit second-turn duration is labelled omitted.

The three frozen cases remain unchanged and are not counted as parser failures. A future versioned fixture correction requires a separate contract.

## Valid target transitions

- `lc4v4d1_entity_patient_omitted_02`: parser_gap -> supported_pass; fixed semantic fields: action_semantics, requires_clarification
- `lc4v4d1_entity_patient_ambiguous_03`: parser_gap -> policy_contract_gap; fixed semantic fields: action_semantics, entity_semantics, requires_clarification
- `lc4v4d1_entity_patient_negated_05`: parser_gap -> supported_pass; fixed semantic fields: action_semantics, entity_semantics, requires_clarification
- `lc4v4d1_entity_practitioner_ambiguous_09`: parser_gap -> policy_contract_gap; fixed semantic fields: action_semantics, entity_semantics, requires_clarification
- `lc4v4d1_entity_practitioner_negated_11`: parser_gap -> supported_pass; fixed semantic fields: action_semantics, entity_semantics, requires_clarification
- `lc4v4d1_entity_location_ambiguous_15`: parser_gap -> policy_contract_gap; fixed semantic fields: action_semantics, entity_semantics, requires_clarification
- `lc4v4d1_entity_location_negated_17`: parser_gap -> supported_pass; fixed semantic fields: action_semantics, entity_semantics, requires_clarification
- `lc4v4d1_entity_appt_type_ambiguous_21`: parser_gap -> policy_contract_gap; fixed semantic fields: action_semantics, entity_semantics, requires_clarification
- `lc4v4d1_entity_appt_type_negated_23`: parser_gap -> supported_pass; fixed semantic fields: action_semantics, requires_clarification
- `lc4v4d1_entity_duration_ambiguous_27`: parser_gap -> policy_contract_gap; fixed semantic fields: action_semantics, normalized_values, entity_semantics, requires_clarification
- `lc4v4d1_dialogue_clarification_multi_02`: parser_gap -> supported_pass; fixed semantic fields: action_semantics, requires_clarification
- `lc4v4d1_dialogue_correction_single_03`: parser_gap -> policy_contract_gap; fixed semantic fields: entity_semantics
- `lc4v4d1_dialogue_reversal_single_05`: parser_gap -> supported_pass; fixed semantic fields: action_negated
- `lc4v4d1_dialogue_session_restart_multi_12`: parser_gap -> supported_pass; fixed semantic fields: entity_semantics
- `lc4v4d1_safety_move_safe_03`: parser_gap -> supported_pass; fixed semantic fields: normalized_values
- `lc4v4d1_safety_move_unsafe_04`: parser_gap -> policy_contract_gap; fixed semantic fields: normalized_values
- `lc4v4d1_safety_resize_safe_05`: parser_gap -> supported_pass; fixed semantic fields: intended_action, action_semantics, requires_clarification
- `lc4v4d1_safety_resize_unsafe_06`: parser_gap -> policy_contract_gap; fixed semantic fields: intended_action, requires_clarification
- `lc4v4d1_safety_explain_safe_11`: parser_gap -> supported_pass; fixed semantic fields: entity_semantics
- `lc4v4d1_safety_explain_unsafe_12`: parser_gap -> supported_pass; fixed semantic fields: entity_semantics

## Boundaries

Policy/state-join remediation is not authorized. Holdouts v1-v4 remain sealed; no protected content, provider, route, database, UI, deployment, or write surface was opened.
