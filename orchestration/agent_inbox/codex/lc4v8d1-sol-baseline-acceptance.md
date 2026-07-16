# LC4V8D1 Sol Baseline Acceptance

Date: 2026-07-16

Decision: `baseline_valid_empty_selection_no_remediation_authorized_pending_final_veto`

## Frozen evidence

The recovered runner is frozen at exact Sol source head `8823bf0d`. Two
independent invocations reproduce complete report hash
`sha256:e7507a4333316012449168f4e11ab93e0b8b60b29c1495b1864eb932bd5fa0bd`.
The raw fixture hash is
`sha256:ebcfe4bbbd9c89dff00f1ff30643f2b9dc21f5cfba5febf62fd22e041f76269c`
and canonical fixture hash is
`sha256:a15a9ad47cd576679ac393c758216a3257ad1f67aa4b4455ef8c6b574c5f376e`.

All 24 fresh inspectable ordinary-development cases pass normalization,
extraction, independently derived semantic policy behavior, exact 14-field
policy projection, composition, and safety across 48 observations with zero
variance. Each of the four families passes 6/6. Authoring-invalid,
normalization-gap, parser-gap, policy-behavior-gap, and policy-projection-gap
counts are all zero.

The non-pass selection is empty, with hash
`sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
No parser, normalizer, policy, or projection runtime repair is authorized.

## Interpretation

The fresh evidence demonstrates that the ordinary typed `PolicyResolution`
behavior and one explicit JSON-safe canonical projection agree across all six
actions, identity/clarification/refusal/no-action/diary boundaries, numeric and
spoken time forms, lower/upper bounds, cross-turn composition, and correction.

This does not reveal or rescore V8. It supports the aggregate-first hypothesis:
V8's policy-resolution `0/576` is not evidence of a general resolver failure or
an unavoidable representation problem. It is most consistent with a V8-specific
Gold/evaluator contract mismatch. V8's 48 temporal/normalization misses also do
not reproduce in this independent 12-case temporal sample, so no broad parser
repair is justified; the exact sealed-case cause remains unknowable.

## Provenance and remaining gate

Gemini passed the frozen authorship before baseline. Flash's uncommitted
self-pass was rejected for conceptual provenance and fail-open evidence defects;
Sol recovered under the recorded lease without a correction loop. The recovered
focused/preservation command passes 291 selected nodes with the two documented
immutable LC4V4D3 equality nodes deselected.

Final acceptance remains pending a fresh Gemini exact-head veto of the recovered
runner, tests, recovery record, baseline hashes, and no-remediation conclusion.
Holdouts v1-v8 remain sealed. T3.1-T3.4 remain blocked; T3.5/providers and all
product/write surfaces remain deferred.
