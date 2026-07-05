# plan-codex-codex-sprint-r23-deepseek-frame-aware-validator-implementation

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `master` |
| Source Task | `codex-sprint-r23-deepseek-frame-aware-validator-implementation` |
| Status | integrated |
| Created | 2026-07-05 23:01 +1000 |
| Source HEAD | `b425002` |

## Plan Summary

Fake-provider-only frame-aware validator

## My Understanding

The current evaluate_manifest_response() checks for violation patterns in a flat dict (write keys, PHI, claimed actions, availability, invalid reason codes, ambiguity defaults) but does not validate structural frame shape. A response labeled frame_kind=proposal can be missing requires_staff_confirmation, a clarify frame can lack status, and a refusal frame can omit blocked/reason -- all without triggering existing violations. A frame-aware validator enforces per-frame_kind required keys, allowed keys, type constraints, and cross-field coherence, catching malformed safe-looking responses before live provider wiring.

## Intended Surface / Boundary

app/services/ai/evals/manifest_eval.py -- add FrameSchema, validate_response_frame_shape(), and integrate into evaluate_manifest_response() + scenario eval. tests/test_bernie_manifest_receptionist_scenarios.py -- add frame-shape validation tests. No diary UI, appointment slots, waiting room, booking status, or frontend code changes.

## Out Of Scope

Live Gemini/Vertex calls, production prompt wiring, frontend/Diary UI, database migrations, real appointment writes, status code changes, booking slot logic, waiting room panel, appointment geometry. No changes to capability_manifest.py or diary route code.

## Files I Expect To Edit

app/services/ai/evals/manifest_eval.py, tests/test_bernie_manifest_receptionist_scenarios.py

## Implementation Steps

1) Define FrameSchema dataclass with required_keys, optional_keys, forbidden_keys, type_constraints per frame_kind. 2) Write FRAME_SCHEMAS registry mapping proposal/clarify/refusal/read_request to schemas. 3) Implement validate_response_frame_shape() returning list of FrameShapeViolation records. 4) Add FrameShapeViolation to violation kind set (new violation kind: malformed_frame). 5) Integrate frame-shape check into evaluate_manifest_response() alongside existing checks. 6) Add receptionist scenario tests: missing required keys, extra forbidden keys, wrong types, wrong frame_kind values. 7) Add safe-response regression tests: all 5 existing safe scenarios pass shape validation. 8) Run py_compile + pytest.

## Visual / Behavioural Acceptance Checks

1) Proposal missing requires_staff_confirmation is flagged as malformed_frame. 2) Clarify response without status is flagged. 3) Refusal without blocked=True and reason is flagged. 4) Read_request missing requires_backend_check is flagged. 5) Unknown frame_kind value is flagged. 6) Proposal with unexpected confirmation envelope keys is flagged. 7) All 5 existing safe scenarios pass frame-shape validation. 8) All existing unsafe scenarios still caught. 9) No changes to production prompt wiring, routes, or UI.

## Risks / Ambiguities

1) Tightening schema constraints could conflict with legitimate variable prompt outputs if real model outputs use flexible key sets -- but this is fake-provider-only eval, so we can afford strictness. 2) Frame taxonomy may evolve when live prompts are wired; schemas may need updating. 3) Must ensure evaluate_manifest_response still runs all existing checks -- frame-shape validation is additive.

## Codex Plan Review

- Review result: Accepted. Ariadne implemented the fake-provider-only frame-shape validator locally from this plan.
- Required changes before implementation: Keep the seam test/eval-only and additive to existing output detectors.
- Approved to proceed: yes
