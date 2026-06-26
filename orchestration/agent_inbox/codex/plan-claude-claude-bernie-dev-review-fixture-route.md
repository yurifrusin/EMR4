# plan-claude-claude-bernie-dev-review-fixture-route

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-bernie-dev-review-fixture-route` |
| Status | integrated |
| Created | 2026-06-27 04:47 +1000 |
| Source HEAD | `de46e27` |

## Plan Summary

Add a dev-gated, non-PHI, deterministic backend fixture route under the appointments proposal surface that returns BernieStaffReviewPayload examples for the blocked, candidate_selection_required, and confirmation_ready states, so the dev launcher/review panel can fetch realistic payloads instead of hand-authored Playwright route payloads. No appointment writes, no audit writes, no LLM/provider calls.

## My Understanding

The supervised Bernie booking wrapper POST /api/v1/appointments/proposals/bernie/supervised-booking returns BernieSupervisedBookingOut whose staff_review is a BernieStaffReviewPayload with status one of blocked / candidate_selection_required / confirmation_ready. The diary dev review panel (docs/diary/diary.js renderBernieReview) currently consumes hand-authored mock fixtures (mockBernieReviewBlocked, mockBernieReviewCandidateSelection, mockBernieReviewConfirmationReady) injected via Playwright route stubs. The sprint wants a deterministic backend source of those three review payloads so dev tooling stops depending on hand-maintained frontend/Playwright payloads that can drift from the real schema/helper output.

## Intended Surface / Boundary

Backend-only. A new dev/test-gated read route on the existing appointments router (app/routers/appointments.py, prefix /api/v1/appointments), reusing the existing BernieStaffReviewPayload response schema and the existing _bernie_staff_review_payload helper. Auth via require_role(*MUTATING_APPOINTMENT_ROLES) and practice-scoped current_user, consistent with adjacent proposal routes. Gated so it only returns in dev (settings.environment lowercased equals dev) and returns 404 otherwise. Nearby surfaces that must NOT change: the live supervised-booking, slot-search, slot-selection, and confirm-bernie endpoints and their semantics; the diary review panel markup is unchanged in this packet.

## Out Of Scope

Diary UI, taskpane, Command Centre, live/autonomous booking, production default exposure, real patient data, Gemini/LLM parsing, migrations, appointment write semantics, audit writes, SMS, billing, resource admin, broad appointment router redesign, frontend wiring of the route (separate Antigravity sprint), and unrelated test hygiene.

## Files I Expect To Edit

app/routers/appointments.py (add dev-gated fixture route plus small deterministic fixture-builder helpers that reuse _bernie_staff_review_payload and existing schemas; import settings from app.config). tests/test_bernie_dev_review_fixture_route.py (new focused pytest). No app/config.py change expected: reuse settings.environment directly rather than adding a helper.

## Implementation Steps

1. Import settings from app.config into appointments.py. 2. Add module-level deterministic non-PHI constants (placeholder UUIDs, provisional patient name, fixed date/time/duration) and helper builders that construct the three BernieStaffReviewPayload values through the existing _bernie_staff_review_payload helper, mirroring real wrapper output for blocked / candidate_selection_required / confirmation_ready; build SlotCandidate, SlotSearchProposalOut, and SlotSelectionProposalOut inputs in memory with no DB reads or writes. 3. Add GET /api/v1/appointments/dev/bernie-review-fixtures returning the three payloads keyed by state, with an optional state query filter returning a single payload. 4. Gate the handler: when settings.environment lowercased is not dev, raise HTTP 404; keep require_role auth and practice scoping. 5. Guarantee no Session writes, no AppointmentAuditLog rows, no appointment creation, and no LLM/provider calls. 6. Add focused tests covering: dev returns deterministic payloads for all three states with correct status/confirmation_ready/confirm_endpoint/confirm_payload; non-dev returns 404; unauthenticated returns 401; no appointment or audit rows created; identical output across two calls. 7. py_compile touched modules, run focused pytest plus adjacent Bernie wrapper/review harness tests, then git diff --check.

## Visual / Behavioural Acceptance Checks

In dev, GET /api/v1/appointments/dev/bernie-review-fixtures returns three deterministic BernieStaffReviewPayload objects: blocked (confirmation_ready false, blocks non-empty, confirm_payload null), candidate_selection_required (confirmation_ready false, candidate_slots populated, confirm_endpoint null), confirmation_ready (confirmation_ready true, selected_slot present, confirm_endpoint = /api/v1/appointments/proposals/create/confirm-bernie, confirm_payload.confirmed false). Identical bytes on repeated calls. Non-dev environment returns 404. Unauthenticated returns 401. No appointment rows and no audit rows are created. Note on visually loaded words: review panel, candidate slots, selected slot, and status here refer only to the JSON data shape returned by this backend route; this packet renders no UI and must not alter the diary review panel markup, the diary grid, booking slots, or waiting room surfaces.

## Risks / Ambiguities

1. Determinism: confirm_payload embeds a model_dump of selection_proposal, so fixtures must use fixed module-level constants and avoid now()/uuid4 at request time. 2. Schema drift: hand-built payloads could diverge from real output; mitigated by reusing _bernie_staff_review_payload so fixtures track the live contract. 3. Dev gating: prefer in-handler 404 keyed on settings.environment so production never serves the route; confirm the pytest harness environment defaults to dev. 4. Response shape (mapping vs list) for the three states - will pick whichever the dev launcher consumes most directly; flag to Ariadne if a specific shape is preferred. 5. Auth role mirrors adjacent proposal routes; confirm dev reviewers hold a MUTATING_APPOINTMENT_ROLE in seed data.

## Codex Plan Review

- Review result: accepted after Ariadne specified the keyed-by-state response shape and exact helper-aligned confirmation semantics.
- Required changes before implementation: default response keyed by `blocked`, `candidate_selection_required`, and `confirmation_ready`; optional `?state=` returns one keyed payload; use the live confirm-Bernie route and keep `confirm_payload.confirmed` false.
- Approved to proceed: yes; implemented and integrated in Sprint 55.
