# LC4V4D3 Option A Policy Resolution Evidence Report

- **Report hash**: `sha256:e4387344c6aba5da39b88c65844494dfdb944f96b55a0185a6660bde830893cc`
- **Schema version**: `lc4v4d3.policy_resolution.v1`
- **D2 report hash validated**: `False`
- **Population hash matches contract**: `False`
- **Population**: 20 cases
- **Deterministic over 2 runs**: `True`
- **Utterance entity semantics unchanged from D2**: `True`
- **All 20 approved cases pass**: `True`

## Contract Checks

### clarification_alternatives: 20/20 passed (PASS)

- + lc4v4d1_entity_patient_ambiguous_03: Alternatives [Sam Smith, Avery Quinn] match surfaced text
- + lc4v4d1_entity_practitioner_ambiguous_09: Alternatives [Dr Smith, Dr Chen] match surfaced text
- + lc4v4d1_entity_location_ambiguous_15: Alternatives [2, 5] match surfaced text
- + lc4v4d1_entity_appt_type_ambiguous_21: Alternatives [standard consultation, care plan appointment] match surfaced text
- + lc4v4d1_entity_duration_ambiguous_27: Alternatives [15, 30] match surfaced text
- + lc4v4d1_entity_patient_corrected_04: No ambiguous entity; no alternatives needed.
- + lc4v4d1_dialogue_correction_single_03: No ambiguous entity; no alternatives needed.
- + lc4v4d1_entity_practitioner_omitted_08: No ambiguous entity; no alternatives needed.
- + lc4v4d1_entity_practitioner_corrected_10: No ambiguous entity; no alternatives needed.
- + lc4v4d1_dialogue_correction_multi_04: No ambiguous entity; no alternatives needed.
- + lc4v4d1_entity_patient_mismatched_06: No ambiguous entity; no alternatives needed.
- + lc4v4d1_entity_practitioner_mismatched_12: No ambiguous entity; no alternatives needed.
- + lc4v4d1_entity_location_mismatched_18: No ambiguous entity; no alternatives needed.
- + lc4v4d1_entity_appt_type_mismatched_24: No ambiguous entity; no alternatives needed.
- + lc4v4d1_entity_duration_mismatched_30: No ambiguous entity; no alternatives needed.
- + lc4v4d1_safety_create_unsafe_02: No ambiguous entity; no alternatives needed.
- + lc4v4d1_safety_move_unsafe_04: No ambiguous entity; no alternatives needed.
- + lc4v4d1_safety_resize_unsafe_06: No ambiguous entity; no alternatives needed.
- + lc4v4d1_safety_cancel_unsafe_08: No ambiguous entity; no alternatives needed.
- + lc4v4d1_safety_status_unsafe_10: No ambiguous entity; no alternatives needed.

### corrected_patient: 20/20 passed (PASS)

- + lc4v4d1_entity_patient_ambiguous_03: Patient not corrected.
- + lc4v4d1_entity_practitioner_ambiguous_09: Patient not corrected.
- + lc4v4d1_entity_location_ambiguous_15: Patient not corrected.
- + lc4v4d1_entity_appt_type_ambiguous_21: Patient not corrected.
- + lc4v4d1_entity_duration_ambiguous_27: Patient not corrected.
- + lc4v4d1_entity_patient_corrected_04: Resolved patient [Avery Quinn] matches final identity.
- + lc4v4d1_dialogue_correction_single_03: Resolved patient [Avery Quinn] matches final identity.
- + lc4v4d1_entity_practitioner_omitted_08: Patient not corrected.
- + lc4v4d1_entity_practitioner_corrected_10: Patient not corrected.
- + lc4v4d1_dialogue_correction_multi_04: Patient not corrected.
- + lc4v4d1_entity_patient_mismatched_06: Patient not corrected.
- + lc4v4d1_entity_practitioner_mismatched_12: Patient not corrected.
- + lc4v4d1_entity_location_mismatched_18: Patient not corrected.
- + lc4v4d1_entity_appt_type_mismatched_24: Patient not corrected.
- + lc4v4d1_entity_duration_mismatched_30: Patient not corrected.
- + lc4v4d1_safety_create_unsafe_02: Patient not corrected.
- + lc4v4d1_safety_move_unsafe_04: Patient not corrected.
- + lc4v4d1_safety_resize_unsafe_06: Patient not corrected.
- + lc4v4d1_safety_cancel_unsafe_08: Patient not corrected.
- + lc4v4d1_safety_status_unsafe_10: Patient not corrected.

### corrected_practitioner: 20/20 passed (PASS)

- + lc4v4d1_entity_patient_ambiguous_03: Practitioner not corrected.
- + lc4v4d1_entity_practitioner_ambiguous_09: Practitioner not corrected.
- + lc4v4d1_entity_location_ambiguous_15: Practitioner not corrected.
- + lc4v4d1_entity_appt_type_ambiguous_21: Practitioner not corrected.
- + lc4v4d1_entity_duration_ambiguous_27: Practitioner not corrected.
- + lc4v4d1_entity_patient_corrected_04: Practitioner not corrected.
- + lc4v4d1_dialogue_correction_single_03: Practitioner not corrected.
- + lc4v4d1_entity_practitioner_omitted_08: Practitioner not corrected.
- + lc4v4d1_entity_practitioner_corrected_10: Resolved Dr Chen -> pr-004
- + lc4v4d1_dialogue_correction_multi_04: Resolved Dr Chen -> pr-004
- + lc4v4d1_entity_patient_mismatched_06: Practitioner not corrected.
- + lc4v4d1_entity_practitioner_mismatched_12: Practitioner not corrected.
- + lc4v4d1_entity_location_mismatched_18: Practitioner not corrected.
- + lc4v4d1_entity_appt_type_mismatched_24: Practitioner not corrected.
- + lc4v4d1_entity_duration_mismatched_30: Practitioner not corrected.
- + lc4v4d1_safety_create_unsafe_02: Practitioner not corrected.
- + lc4v4d1_safety_move_unsafe_04: Practitioner not corrected.
- + lc4v4d1_safety_resize_unsafe_06: Practitioner not corrected.
- + lc4v4d1_safety_cancel_unsafe_08: Practitioner not corrected.
- + lc4v4d1_safety_status_unsafe_10: Practitioner not corrected.

### omitted_practitioner: 20/20 passed (PASS)

- + lc4v4d1_entity_patient_ambiguous_03: Not omitted-practitioner create.
- + lc4v4d1_entity_practitioner_ambiguous_09: Not omitted-practitioner create.
- + lc4v4d1_entity_location_ambiguous_15: Not omitted-practitioner create.
- + lc4v4d1_entity_appt_type_ambiguous_21: Not omitted-practitioner create.
- + lc4v4d1_entity_duration_ambiguous_27: Not omitted-practitioner create.
- + lc4v4d1_entity_patient_corrected_04: Not omitted-practitioner create.
- + lc4v4d1_dialogue_correction_single_03: Not omitted-practitioner create.
- + lc4v4d1_entity_practitioner_omitted_08: Omitted practitioner -> clarification, no deltas, no implicit practitioner.
- + lc4v4d1_entity_practitioner_corrected_10: Not omitted-practitioner create.
- + lc4v4d1_dialogue_correction_multi_04: Not omitted-practitioner create.
- + lc4v4d1_entity_patient_mismatched_06: Not omitted-practitioner create.
- + lc4v4d1_entity_practitioner_mismatched_12: Not omitted-practitioner create.
- + lc4v4d1_entity_location_mismatched_18: Not omitted-practitioner create.
- + lc4v4d1_entity_appt_type_mismatched_24: Not omitted-practitioner create.
- + lc4v4d1_entity_duration_mismatched_30: Not omitted-practitioner create.
- + lc4v4d1_safety_create_unsafe_02: Not omitted-practitioner create.
- + lc4v4d1_safety_move_unsafe_04: Not omitted-practitioner create.
- + lc4v4d1_safety_resize_unsafe_06: Not omitted-practitioner create.
- + lc4v4d1_safety_cancel_unsafe_08: Not omitted-practitioner create.
- + lc4v4d1_safety_status_unsafe_10: Not omitted-practitioner create.

### diary_conflict: 20/20 passed (PASS)

- + lc4v4d1_entity_patient_ambiguous_03: Not a diary-mismatch probe.
- + lc4v4d1_entity_practitioner_ambiguous_09: Not a diary-mismatch probe.
- + lc4v4d1_entity_location_ambiguous_15: Not a diary-mismatch probe.
- + lc4v4d1_entity_appt_type_ambiguous_21: Not a diary-mismatch probe.
- + lc4v4d1_entity_duration_ambiguous_27: Not a diary-mismatch probe.
- + lc4v4d1_entity_patient_corrected_04: Not a diary-mismatch probe.
- + lc4v4d1_dialogue_correction_single_03: Not a diary-mismatch probe.
- + lc4v4d1_entity_practitioner_omitted_08: Not a diary-mismatch probe.
- + lc4v4d1_entity_practitioner_corrected_10: Not a diary-mismatch probe.
- + lc4v4d1_dialogue_correction_multi_04: Not a diary-mismatch probe.
- + lc4v4d1_entity_patient_mismatched_06: Entity exact, diary conflict on [patient]
- + lc4v4d1_entity_practitioner_mismatched_12: Entity exact, diary conflict on [practitioner]
- + lc4v4d1_entity_location_mismatched_18: Entity exact, diary conflict on [location]
- + lc4v4d1_entity_appt_type_mismatched_24: Entity exact, diary conflict on [appointment_type]
- + lc4v4d1_entity_duration_mismatched_30: Entity exact, diary conflict on [duration]
- + lc4v4d1_safety_create_unsafe_02: Not a diary-mismatch probe.
- + lc4v4d1_safety_move_unsafe_04: Not a diary-mismatch probe.
- + lc4v4d1_safety_resize_unsafe_06: Not a diary-mismatch probe.
- + lc4v4d1_safety_cancel_unsafe_08: Not a diary-mismatch probe.
- + lc4v4d1_safety_status_unsafe_10: Not a diary-mismatch probe.

### unsafe_bypass: 20/20 passed (PASS)

- + lc4v4d1_entity_patient_ambiguous_03: Not an unsafe probe.
- + lc4v4d1_entity_practitioner_ambiguous_09: Not an unsafe probe.
- + lc4v4d1_entity_location_ambiguous_15: Not an unsafe probe.
- + lc4v4d1_entity_appt_type_ambiguous_21: Not an unsafe probe.
- + lc4v4d1_entity_duration_ambiguous_27: Not an unsafe probe.
- + lc4v4d1_entity_patient_corrected_04: Not an unsafe probe.
- + lc4v4d1_dialogue_correction_single_03: Not an unsafe probe.
- + lc4v4d1_entity_practitioner_omitted_08: Not an unsafe probe.
- + lc4v4d1_entity_practitioner_corrected_10: Not an unsafe probe.
- + lc4v4d1_dialogue_correction_multi_04: Not an unsafe probe.
- + lc4v4d1_entity_patient_mismatched_06: Not an unsafe probe.
- + lc4v4d1_entity_practitioner_mismatched_12: Not an unsafe probe.
- + lc4v4d1_entity_location_mismatched_18: Not an unsafe probe.
- + lc4v4d1_entity_appt_type_mismatched_24: Not an unsafe probe.
- + lc4v4d1_entity_duration_mismatched_30: Not an unsafe probe.
- + lc4v4d1_safety_create_unsafe_02: Unsafe -> refuse_instruction only, no deltas, entity preserved.
- + lc4v4d1_safety_move_unsafe_04: Unsafe -> refuse_instruction only, no deltas, entity preserved.
- + lc4v4d1_safety_resize_unsafe_06: Unsafe -> refuse_instruction only, no deltas, entity preserved.
- + lc4v4d1_safety_cancel_unsafe_08: Unsafe -> refuse_instruction only, no deltas, entity preserved.
- + lc4v4d1_safety_status_unsafe_10: Unsafe -> refuse_instruction only, no deltas, entity preserved.

## Utterance Entity Preservation

All entity semantics unchanged: True

## Determinism

Two complete runs: True

## Boundaries

No protected evidence, providers, product runtime, or write authority was accessed.
Holdouts v1-v4 remain sealed.

## Decision

**DECISION: candidate_complete**

