# LC4V4D4 Composed Integration Evidence

- Source commit: `4218d2ee3aca321fe8169a0f27567945e5fa04ca`
- Report hash: `sha256:dd1ecc077a59bf05e777eda1f3a5450c0a1b97a4c8a3fd21dc0363d473abd653`
- D2 report hash: `sha256:3220ac943659ae1449c5c285144b1fa980f659668a705ca7aef98f0aea6d317a`
- D3 report hash: `sha256:94b751aea657696329c6b6d394253aef3ef0dbe82316e7725efc1c16fac523a8`
- D3 selection hash: `sha256:d3c6618cb586f5dc43824ec7a6e9e33957fee587a45c19f89e5a4bb425006e2a`
- Legacy 60-probe baseline hash: `sha256:665851ffe055efb40f2ba1e43291d6b945c4764b4f441837781d4fc964d6ff27`
- Cases: 20
- Complete observations: 40
- Decision: `versioned_composed_integration_valid`

## Gates

- d2_report_valid: `True`
- d3_report_valid: `True`
- selection_hash_valid: `True`
- exact_20_case_population: `True`
- accepted_d3_case_population: `True`
- legacy_60_baseline_hash_exact: `True`
- legacy_runner_equivalence: `True`
- all_20_option_a_pass: `True`
- zero_variance: `True`
- utterance_semantics_preserved: `True`
- replay_fields_exact: `True`
- incompatible_d1_recorded: `True`
- no_forbidden_mutation: `True`

## Categories

- clarification_alternatives: 5 passed, 0 failed
- corrected_patient: 2 passed, 0 failed
- corrected_practitioner: 2 passed, 0 failed
- diary_state_join: 5 passed, 0 failed
- omitted_practitioner: 1 passed, 0 failed
- unsafe_bypass: 5 passed, 0 failed

## Incompatible D1 cases (versioned overlay differences)

- lc4v4d1_entity_appt_type_mismatched_24
- lc4v4d1_entity_duration_mismatched_30
- lc4v4d1_entity_location_mismatched_18
- lc4v4d1_entity_patient_mismatched_06
- lc4v4d1_entity_practitioner_mismatched_12
- lc4v4d1_entity_practitioner_omitted_08

## Boundary

D4 is an explicitly versioned overlay on the composed deterministic
development harness. Frozen D1/D2/D3 evidence is unchanged.
Holdouts v1-v4, T3, providers, product runtime, and write authority
remain closed. The evidence overlay maps only the exact 20 accepted
development IDs.
