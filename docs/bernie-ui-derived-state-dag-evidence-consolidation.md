# Bernie UI Derived-State DAG Evidence Consolidation

Date: 2026-07-09

Status: review-only consolidation. This packet summarizes evidence from the
D1-D5 Bernie UI derived-state DAG work. It does not approve backend response
delivery, route/schema changes, GraphQL delivery, provider wiring, memory/RAG/
GraphRAG wiring, H15/H-series runtime inputs, historical diary runtime inputs,
external patient clients, appointment writes, or model-to-database writes.

## API Spine Classification

The derived-state DAG is a read/display contract. It projects current Bernie
session state into receptionist-facing UI flags and copy. It is not command
authority.

The accepted API Spine remains unchanged:

- GraphQL/read models may expose context and display hints only.
- REST/OpenAPI confirm commands own appointment writes.
- `confirm_endpoint`, `confirm_payload`, freshness IDs, signed evidence, backend
  revalidation, and audit remain the authority for booking confirmation.
- A `BernieUiViewModel` field must never appear in a confirm payload or decide a
  database write.

## Proven Evidence

Pure selector evidence:

- `app/services/bernie/ui_view_model.py` is provider-free, route-free, DB-free,
  memory/RAG/GraphRAG-free, H15/H-series-free, and trove-free.
- `tests/test_bernie_ui_view_model.py` proves fixture projection,
  confirmation-state conditioning, backend-confirmed-only success copy,
  pre-confirm copy safety, unknown-enum fail-closed behavior, no write echo
  fields, and no production-route selector import while D5 is blocked.

Route-intercepted UI evidence:

- Every `ui_view_model` UI smoke test uses `response["evidence_label"] =
  "route_intercepted"` and a route-intercepted confirm handler. Non-confirmable
  states set the handler to report an unexpected write if called.
- `review/test_diary_smoke.py::test_bernie_ui_view_model_proposal_ready_drives_display_without_payload_leak`
  proves proposal-ready display and confirm-payload purity.
- `review/test_diary_smoke.py::test_bernie_ui_view_model_candidate_slots_win_over_legacy_blocked_status`
  proves candidate display can be driven by the view model over a conflicting
  legacy display status.
- `review/test_diary_smoke.py::test_bernie_ui_view_model_non_ready_states_do_not_show_confirm_or_success`
  proves pressed, awaiting-backend, stale, and failed states do not show confirm
  or success UI and preserve recovery affordances where appropriate.
- `review/test_diary_smoke.py::test_bernie_ui_view_model_clarification_blocks_legacy_confirmable_payload`
  proves clarification blocks a legacy confirmable payload and sends no confirm
  request.
- `review/test_diary_smoke.py::test_bernie_ui_view_model_identity_ambiguous_blocks_confirm_and_shows_choices`
  proves ambiguous identity shows staff choices while suppressing proposal,
  confirm, and success UI.

The committed UI view-model route-intercepted cluster currently covers:
proposal-ready, candidate-slots-available, pressed, awaiting-backend, stale,
failed, plain clarification, and ambiguous identity.

Gate evidence:

- `docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.json` keeps
  backend response delivery blocked by default.
- `docs/bernie-ui-derived-state-dag-d5-implementation-checklist.md` records the
  future delivery test matrix without authorizing delivery.
- `docs/bernie-ui-derived-state-dag-d5-router-import-guard-plan.md` preserves
  the broad router import ban until explicit D5 approval.

## Evidence Label

The UI evidence above is route-intercepted Playwright evidence. It uses fixture
payloads and browser route interception. It is deterministic and useful, but it
is not live backend evidence and not live provider evidence.

No current D4/D5 evidence proves production route emission of
`BernieUiViewModel`.

Any future test that delivers `BernieUiViewModel` from a production route must
change this evidence label posture and trigger the D5 gate review.

## Payload And Write Authority

The `BernieUiViewModel` is display-only state. It carries no write authority.

Confirm payloads continue to use existing signed fields such as
`confirm_endpoint`, `confirm_payload`, `turn_ref`, `candidate_freshness_id`,
`proposal_freshness_id`, `selection_proposal`, `create_proposal`, and signed
confirmation evidence. The view model schema explicitly excludes
`writes_authorized`, `confirm_payload`, `signed_confirmation_evidence`,
`proposal_freshness_id`, `appointment_id`, `patient_id`, and `practitioner_id`.

Pre-confirm display copy must continue to say no appointment has been made yet
and must not be treated as write-authority evidence.

## Unproven And Still Blocked

The following remain unapproved:

- production route emission of `BernieUiViewModel`;
- GraphQL resolver delivery;
- provider prompt or live-provider wiring;
- Access AI invocation;
- memory/RAG/GraphRAG runtime access;
- H15/H-series or historical diary runtime inputs;
- confirm payload changes;
- appointment write behavior changes;
- external patient-client exposure;
- model-to-database writes.

The expected readiness posture remains:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`
- `default_provider=disabled`
- `live_provider_enabled=false`
- `provider_calls_performed=false`

## Next Decision Posture

This packet supports three explicit options:

| Option | Posture | When to choose |
|---|---|---|
| Keep D5 blocked | Current posture remains correct; continue route-intercepted evidence only | Choose if review consolidation is the only sprint goal |
| Approve narrow D5 slice | After the Sprint 246-248 review block is clean, approve optional `bernie.ui_view_model.v1` delivery at one reviewed Bernie response assembly point | Pragmatic likely next real move if no hidden coupling appears |
| Approve D5 with extra readiness margin | Same narrow slice, plus mandatory pre-D5 readiness commands recorded immediately before implementation | Choose for maximum safety before touching route delivery |

The recommended next real move after Sprints 246-248, if those artifacts remain
clean, is the narrow D5 backend response-delivery first slice. That approval
should cover exactly one response assembly point and keep all provider, memory,
GraphQL, H15/H-series, historical diary, external client, and write gates
closed.

The remaining review block should first add a Sprint 246 approval-decision draft,
a Sprint 247 backend delivery test plan, and a Sprint 248 readiness snapshot,
then preserve the blocked posture until explicit approval exists.

Until that explicit approval exists, the broad production-route import ban and
the blocked D5 gate remain correct.
