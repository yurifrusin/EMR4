# Bernie Interpretation Harness Scaffold

Date: 2026-07-06

Sprint: H40

## Purpose

`app/services/bernie/interpretation_harness.py` is the first provider-free
Bernie Interpretation Harness scaffold after H39.

It maps authored synthetic receptionist utterances to native
`DiaryActionVerb` decisions, then uses the H37 route-authority inventory to
choose a non-executing dispatch class.

## Boundaries

The harness does not:

- Call LLM or provider clients.
- Import FastAPI routes or `TestClient`.
- Touch database models or sessions.
- Persist memory.
- Read raw historical diary files, ignored local outputs, H-series profiles, or
  H15 semantic fixtures.
- Create appointments, audits, proposals, signed evidence, or route calls.

## Dispatch Classes

- `route_to_confirm`: implemented mutating grammar verb with signed-confirm
  authority. The harness only labels it; it does not call the confirm route.
- `route_read_only`: implemented read-only grammar verb.
- `route_meta`: meta workflow control.
- `refuse_planned_not_implemented`: known planned grammar verb such as
  `check_in`, `waiting_area_move`, or `link_patient`.
- `refuse_unknown_utterance`: no deterministic authored rule matched.

## Verification

`tests/test_bernie_interpretation_harness.py` loads
all JSON fixtures under `tests/fixtures/bernie_interpretation_harness/` and
checks the expected grammar verb, route authority, and dispatch for each
synthetic utterance.

## H41 Adversarial Coverage

H41 adds `adversarial_utterance_actions.json` and the
`refuse_unsafe_instruction` dispatch class. The harness refuses unsafe wording
before grammar matching when an utterance attempts to:

- Bypass guardrails or staff confirmation.
- Call route endpoints directly.
- Write directly to a database/raw mutation path.
- Invoke a provider or LLM.

Mixed planned-action phrases remain planned. For example, "check in ... and
mark arrived" maps to `check_in` and dispatches
`refuse_planned_not_implemented`, not to the implemented `status_change` path.

## H42 Result Invariants

H42 adds `assert_interpretation_result_consistency()`. Every harness result must
preserve the dispatch/authority relationship:

- `route_to_confirm` requires `signed_confirm`.
- `route_read_only` requires `read_only`.
- `route_meta` requires `meta`.
- `refuse_planned_not_implemented` requires `planned_not_implemented`.
- Unsafe and unknown refusals must not carry a verb or route authority.

## H43 Frame-Shape Preparation

H43 adds `interpretation_result_to_frame()`, a deterministic projection from a
harness result to a fake-provider-compatible frame shape:

- Confirm-route labels become `proposal` frames with
  `requires_staff_confirmation: true` and `writes_authorized: false`.
- Read-only labels become `read_request` frames with
  `requires_backend_check: true` and `writes_authorized: false`.
- Meta, planned, unsafe, and unknown results become `refusal` frames with
  `blocked: true` and `writes_authorized: false`.

Tests validate every authored fixture output through the existing manifest
frame-shape and safety evaluators without making provider calls.

## H44 Fixture-Driven Frame Expectations

H44 makes `expected_frame_kind` part of every authored interpretation fixture
case and adds receptionist-phrase coverage from external review:

- Availability phrasing such as "gaps", "free times", and "squeeze them in".
- Short check-in phrasing such as "patient is here" and "arrived at the desk".
- Cancellation phrasing such as "patient cancelled" and "remove from the diary".
- Resize/move/create phrasing such as "double appointment", "30 minutes",
  "push back", "bring forward", and "put them in".
- Handoff wording that avoids treating every "receptionist" mention as handoff.

H44 also incorporates adversarial safety review fixes:

- Broader confirmation-bypass refusal phrases such as "no need for
  confirmation", "skip confirmation", and "auto-confirm".
- False-precondition refusals such as "pretend it is done" and "already
  confirmed".
- Narrower slot-search matching so generic "find/show" phrasing does not
  become availability search without an availability cue.
- Unicode normalization and removal of common zero-width/directional formatting
  controls before matching.
- `refusal_reason_kind` on projected frames to distinguish meta handoff,
  planned-not-implemented, unsafe, and unknown refusals.

## H45 Projected Frame Invariants

H45 adds `assert_interpretation_frame_consistency()`, a harness-local guard on
top of the broader manifest frame validator. It checks that:

- Every projected frame has `writes_authorized: false`.
- `route_to_confirm` frames are `proposal` frames with staff confirmation.
- `route_read_only` frames are `read_request` frames with backend checks.
- Refusal frames carry the expected `refusal_reason_kind`.
- Unsafe and unknown refusals do not carry `refused_action`.

This is deliberately narrower than the global manifest validator: it protects
the interpretation harness's own dispatch/frame contract before any future
fake-provider layer consumes it.

## H46 Provider-Style Copy Contract

H46 adds safe receptionist-facing `copy` strings to projected frames:

- Proposal frames say the harness can stage a diary proposal for staff review.
- Read-request frames say the backend must check the diary before options are
  shown.
- Refusal frames say the harness cannot complete the request.

The copy is intentionally bland and authority-limited. Harness tests now assert
that projected fixture frames do not claim a diary action has already happened,
do not assert live availability, do not include confirmation-bypass language,
and still pass the fake-provider manifest safety evaluator without provider
calls.

## H47 Clarify-Frame Dispatch

H47 adds `request_clarification` as a provider-free dispatch class for
authored synthetic utterances that explicitly describe ambiguity:

- Patient-context ambiguity projects to a `clarify` frame with synthetic display
  choices and no IDs.
- Reason-code ambiguity projects to a `clarify` frame with valid reason-code
  options and no selected/defaulted reason.

Clarification runs after unsafe-instruction refusal and before ordinary action
matching. It carries no verb, no route authority, no writes, and no database or
provider dependency. The purpose is to exercise the remaining fake-provider
frame kind while preserving the native backend as the authority for real
patient matching and status/reason-code validation.

## H48 Fixture-Backed Frame Contract Matrix

H48 adds
`tests/fixtures/bernie_interpretation_harness/projected_frame_contracts.json`.
The matrix records the expected frame kind and key-level contract for each
interpretation dispatch:

- Required `true`, `false`, and `null` fields.
- Fields that must be absent from projected frames.
- Expected refusal reason kinds where relevant.
- Required safe copy fragments.

The tests now prove every dispatch has a contract, every contract is observed by
at least one authored fixture, and every projected frame satisfies the matching
contract before it is passed through the broader fake-provider manifest
evaluator. The contract fixture stays payload-free and avoids route, endpoint,
patient/practitioner/appointment ID fragments.

## H49 Bounded Contract Review

H49 records a local adversarial contract review in
`docs/adversarial/h49_interpretation_harness_contract_review.md`.

The review found one small consistency issue: a malformed frame with an unknown
`interpretation_dispatch` raised `ValueError` through the enum constructor
instead of failing through the harness assertion contract. The invariant helper
now converts that case to `AssertionError`, and the drifted-frame regression
matrix covers the failure. This does not add any new interpretation behavior or
runtime authority.

## H50 Safe Aggregate Report

H50 adds `scripts/bernie_interpretation_harness_report.py`, a provider-free CLI
and importable helper that summarises the authored synthetic harness corpus
without printing utterance text.

The report includes:

- Case and contract counts.
- Dispatch and frame-kind counts.
- Fixture-level case counts.
- Contract dispatch coverage.
- Explicit omitted-field declarations.
- Boundary posture: providers, routes, database access, raw trove access, and
  runtime memory are prohibited.

The current report summarises 44 authored cases across 4 case fixture files and
7 projected-frame contracts. Tests assert that representative utterance text and
payload/ID fields are omitted from the serialized report.

## H51 Report Safety Assertion

H51 adds `assert_harness_report_safety()` and runs it before CLI output. The
assertion checks:

- Report schema and source schema.
- Non-empty aggregate counts.
- No-provider/no-route/no-database/no-raw-trove/no-memory boundary posture.
- Omitted-field declarations.
- Contract dispatches matching dispatch counts.
- Representative forbidden payload, ID, local-data, H15/H-series, and utterance
  text fragments are absent from searchable report values.

Negative tests cover embedded utterance text, weakened provider boundaries, and
contract-dispatch drift.
