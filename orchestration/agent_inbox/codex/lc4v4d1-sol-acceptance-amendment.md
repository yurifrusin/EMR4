# LC4V4D1 Sol Acceptance Amendment

Date: 2026-07-15

Decision: `diagnostic_invalid_after_audit`

This amendment supersedes the decision and interpretation in
`lc4v4d1-sol-acceptance.md` and
`docs/bernie-lc4v4d1-development-diagnostic-closeout.md`. It does not rewrite
or delete those historical artifacts.

## Corrected adjudication

The frozen D1 report remains exactly bound by:

- fixture hash
  `sha256:a81de0b5371d4fcc425c23f0da9560e29827e3e85cc22847990ea83518863269`;
- report hash
  `sha256:1527b99359dc76e831d7eabf49fff022781faf5d248c436bde6e022f30eff84d`;
- raw 23-case selection hash
  `sha256:1b254ae627e26b1b301b660628d90f39dce5e0364afc0cfcf4c4855fb6531f02`.

That report's raw `0 authoring_invalid / 23 parser_gap / 12
policy_contract_gap / 25 supported_pass` interpretation is no longer accepted.
The audited interpretation is `3 / 20 / 12 / 25`. The three quarantined IDs
are:

- `lc4v4d1_entity_duration_corrected_28`;
- `lc4v4d1_entity_duration_negated_29`;
- `lc4v4d1_dialogue_ellipsis_multi_08`.

The valid 20-case parser target hash is
`sha256:0badec28ad533b630786d245e5ab47dee5655b83239869f7d0a2d12a8935d105`.
Only that independently reviewable selection is eligible for D2 semantic
remediation. The 12 policy/state-join cases remain outside parser repair.

## Accountability

Sol's earlier acceptance was wrong because it treated successful fixture
validation and independent report reproduction as sufficient evidence that all
authored semantic labels were internally consistent. Gemini's earlier pass did
not catch the same gap. The incident and corrective invariants are documented
in `docs/bernie-lc4v4d1-authoring-defect-incident.md`.

This amendment does not weaken the value of D1's remaining inspectable evidence:
the 20 valid parser gaps, 12 policy gaps, and 25 supported passes remain useful.
It does require all later evidence to disclose the invalid rows and to fail
closed if the frozen report is interpreted as an unqualified 23-case parser
population.

Holdouts v1-v4 remain sealed. T3.1-T3.4 remain blocked; T3.5, providers,
historical-diary expansion, routes/APIs, database and UI work, deployment,
release, and all runtime write authority remain deferred.
