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

## H52 Report Input Fail-Closed Guards

H52 hardens `build_harness_report()` so alternate fixture directories cannot
silently produce empty or meaningless reports. It now raises `ValueError` when:

- The fixture path is missing or not a directory.
- The directory contains no JSON fixtures.
- A case or contract fixture has an empty list.
- No case fixtures are present.
- No contract fixtures are present.

The tests use temporary synthetic directories and do not touch runtime routes,
providers, database access, or historical diary material.

## H53 Runtime/Provider Wiring Gate

H53 adds `docs/bernie-interpretation-harness-runtime-gate.json`, a
blocked-by-default gate for moving the provider-free interpretation harness
toward runtime/provider surfaces.

The gate keeps these scopes false:

- Runtime wiring.
- Provider dry-run wiring.
- Route integration.
- Database access.
- Memory/RAG access.
- Historical diary material access.

Current allowed uses remain provider-free fixture tests, safe aggregate reports,
contract validation, and bounded review artifacts. Any decision change away from
`blocked`, any scope value changing to `true`, or edits to the required/forbidden
lists require a sprint-engine pause and explicit review.

## H54 Runtime Gate Checker

H54 adds `scripts/bernie_interpretation_runtime_gate_check.py`, a provider-free
CLI/importable helper that validates the H53 runtime gate before emitting a safe
aggregate status.

The status includes only counts and state:

- Blocked scope count.
- Required review count.
- Forbidden use count.
- Pause trigger count.
- `sprint_engine_state: continuing`.
- `pause_required: false`.

The checker rejects unblocked decisions, true scope values, changed allowed or
forbidden use sets, missing required reviews, and missing pause triggers.

## H55 Combined Readiness Check

H55 adds `scripts/bernie_interpretation_readiness_check.py`, which combines the
safe aggregate report and runtime-gate checker into one provider-free command.

The command emits only aggregate status:

- Case, contract, dispatch, and frame-kind counts.
- Report schema version.
- Runtime gate status schema version.
- Runtime gate decision.
- `sprint_engine_state: continuing`.
- `runtime_or_provider_wiring_ready: false`.
- `raw_trove_access_ready: false`.

This is a "still boxed in" check. It proves the harness/report/gate surface is
coherent; it does not approve runtime routes, provider prompts, database access,
memory, RAG/GraphRAG, H15/H-series runtime imports, or raw trove access.

## H56 Release-Gate Hook

H56 adds the readiness command to `orchestration/bernie_release_gates.md`.
Before interpretation harness work can propose runtime route wiring, provider
prompt/dry-run wiring, memory/RAG/GraphRAG use, H15/H-series runtime imports, or
historical diary material access, Ariadne must run:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
```

The expected current values are `runtime_or_provider_wiring_ready=false`,
`raw_trove_access_ready=false`, and `runtime_gate_decision=blocked`. A changed
value or failing command requires a sprint-engine pause and explicit review.

## H57 Runtime Isolation Guard

H57 adds `tests/test_bernie_interpretation_runtime_isolation.py`, which scans
production `app/` Python sources and proves they do not import or reference:

- Interpretation harness report/readiness/gate tooling.
- Bernie interpretation harness fixture paths or projected-frame contracts.
- H15 semantic candidate fixtures.
- H-series profile fixtures.
- Historical diary candidate builders, `local_data`, or trove paths.

This keeps the interpretation harness as a provider-free test/review artifact
until a future explicitly reviewed gate changes that boundary.

## H58 Readiness/Gate Review

H58 adds `docs/adversarial/h58_interpretation_readiness_gate_review.md`, a local
adversarial review of the report/gate/readiness stack.

Verdict: the stack is suitable as a blocked-by-default preflight for continued
provider-free harness work. It is not evidence that runtime routes, provider
prompts, live provider dry-runs, memory/RAG/GraphRAG, H15/H-series runtime
imports, or historical diary material access are ready.

The review preserves the recommendation to pause the sprint engine if
`runtime_or_provider_wiring_ready` or `raw_trove_access_ready` ever changes away
from `false`.

## H59 Blocked-Readiness Snapshot

H59 adds
`tests/fixtures/bernie_interpretation_readiness/blocked_readiness_status.json`.
The generated readiness status must match this committed blocked snapshot
exactly.

The snapshot preserves:

- 44 authored cases.
- 7 projected-frame contracts.
- 7 dispatches and 4 frame kinds.
- `runtime_gate_decision: blocked`.
- `sprint_engine_state: continuing`.
- `runtime_or_provider_wiring_ready: false`.
- `raw_trove_access_ready: false`.

It is aggregate-only and contains no utterance text, payload fields, route
fragments, local-data paths, H15 fragments, or H-series fragments.

## H60 Protocol Alert

H60 adds a short worker-facing alert to `orchestration/protocol_alerts.md`.
The alert requires the readiness command before any worker or Ariadne sprint
proposes runtime route wiring, provider prompt/dry-run wiring,
memory/RAG/GraphRAG use, H15/H-series runtime imports, or historical diary
material access from the provider-free interpretation harness.

Expected values remain `runtime_or_provider_wiring_ready=false`,
`raw_trove_access_ready=false`, and `runtime_gate_decision=blocked`. Any command
failure or changed value pauses the sprint engine for explicit review.

## H61 Combined Readiness Fail-Closed Tests

H61 strengthens the combined readiness check tests. The command layer now has
direct negative coverage for:

- An unblocked runtime gate decision.
- A missing fixture directory.
- An empty fixture directory.

These duplicate key lower-level safeguards at the command future agents are
expected to run before any runtime/provider/trove proposal.

## H62 Readiness Snapshot Assertion

H62 makes the readiness CLI load
`tests/fixtures/bernie_interpretation_readiness/blocked_readiness_status.json`
and assert generated readiness matches it before printing.

If the snapshot is missing or generated readiness differs from the committed
blocked status, the command fails closed. This turns the H59 snapshot from a
pytest-only guard into part of the operational readiness command.

## H63 Independent Review Brief

H63 adds `docs/adversarial/h63_interpretation_independent_review_brief.md`, a
bounded review handoff for the provider-free interpretation readiness/gate stack.

The brief requires the readiness command first and preserves the expected
blocked values:

- `runtime_or_provider_wiring_ready: false`.
- `raw_trove_access_ready: false`.
- `runtime_gate_decision: blocked`.
- `sprint_engine_state: continuing`.

Its scope is review-only. Runtime routes, frontend changes, provider prompts or
dry-runs, database access, memory/RAG/GraphRAG, H15/H-series runtime imports, and
historical diary trove access remain out of scope unless Yuri explicitly opens a
future implementation sprint.

## H64 Independent Review

H64 records a DeepSeek Flash independent adversarial review in
`docs/adversarial/h64_interpretation_readiness_independent_review.md`, guarded by
`tests/test_bernie_interpretation_h64_review_artifact.py`.

The review found no critical or high issues and kept the sprint engine
continuing. It accepted three medium hardening follow-ups before any future
runtime/provider/trove proposal:

- Derive readiness booleans from runtime-gate scope instead of explicit blocked
  constants.
- Add more mechanical enforcement that the readiness command is run before
  runtime/provider/trove proposal surfaces.
- Make interpretation result/frame helpers self-validating.

## H65 Gate-Derived Readiness Booleans

H65 addresses H64-M1. `scripts/bernie_interpretation_runtime_gate_check.py` now
derives `runtime_or_provider_wiring_ready` and `raw_trove_access_ready` from the
runtime-gate scope keys, and
`scripts/bernie_interpretation_readiness_check.py` consumes those derived values
instead of using standalone constants.

The external combined readiness output remains blocked and unchanged, but the
blocked values now come from the gate scope. Focused tests prove the runtime-gate
status derives true values from drifted scope when the gate assertion is
intentionally monkeypatched away, and that combined readiness consumes the
runtime-gate status fields.

## H66 Self-Validating Projection Frames

H66 addresses H64-M3 and H64-L4. `interpretation_result_to_frame()` now validates
each result before projection and each projected frame before returning it.

Clarification frame invariants now require exactly one active subtype:
patient-context clarification or reason-code clarification, never neither and
never both. Focused tests cover mixed clarify-frame rejection and projection
self-validation of an inconsistent result.

## H67 Derived Report Text Safety

H67 addresses H64-L1. `scripts/bernie_interpretation_harness_report.py` now
derives forbidden report text from every committed fixture `utterance` in the
fixture directory instead of relying on a small hand-picked substring list.

The derived utterance text is used only for local validation and is not emitted
in the aggregate report. `scripts/bernie_interpretation_readiness_check.py`
passes the active fixture directory into the report-safety assertion so custom
fixture directories receive the same text-leakage protection.

## H68 Proposal Surface Guard

H68 addresses H64-M2 with
`scripts/bernie_interpretation_proposal_surface_guard.py`. The guard scans new
markdown proposal artifacts for runtime/provider/trove proposal trigger phrases
and requires the readiness command plus the expected blocked values:

- `runtime_or_provider_wiring_ready=false`.
- `raw_trove_access_ready=false`.
- `runtime_gate_decision=blocked`.

This is a mechanical preflight for proposal artifacts, not approval to wire
runtime routes, providers, memory, H15/H-series runtime imports, or historical
diary material access.
