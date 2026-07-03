# plan-codex-codex-sprint-g4-create-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-g4-create-confirm-invariants` |
| Status | integrated |
| Created | 2026-07-04 07:50 +1000 |
| Source HEAD | `bd917e8` |

## Plan Summary

Plan human create-booking modal migration to signed create-confirm with status boundary invariants

## My Understanding

G1-G3 moved update-style writes onto signed confirm evidence, but the human create-booking modal still builds a create payload, calls raw POST /appointments, then optionally PATCHes status. Sprint G4 should migrate only the signed-capable human create Save path so it first obtains backend create proposal evidence, posts explicit staff confirmation to the signed create-confirm route, and treats direct POST /appointments as a bounded compatibility endpoint/path rather than the normal UI authority. The create-confirm result must be the only source of a newly-created appointment id for any status-after-create PATCH, and accepted warnings must be code-only evidence carried through the confirm payload and audit rows.

## Intended Surface / Boundary

Primary surface: docs/diary/diary.js saveBooking() create-mode Save in the booking modal. Backend surface: app/schemas/appointments.py create proposal/confirm schemas and app/routers/appointments.py create proposal/confirm helpers/routes, reusing the existing /appointments/proposals/create and /appointments/proposals/create/confirm-bernie spine or a narrowly named neutral alias if Ariadne prefers. Test surface: focused appointment proposal/confirm/audit pytest plus deterministic review/test_diary_smoke.py route-intercepted modal Save checks. Nearby surfaces that must not change: G3 edit-modal update Save, G2 drag/drop/resize update confirm, status-only controls, cancel/delete flows, waiting-room panels/cards, diary grid layout/stacking/slot geometry, Bernie broad chat grammar, taskpane, Command Centre, migrations, and UI redesign.

## Out Of Scope

No production edits during this plan gate. No edit/update G3 changes except regression assertions. No drag/drop/resize, cancel/delete, status grammar migration, raw endpoint removal, persisted Bernie sessions, GraphRAG, database migration, broad API rewrite, copy/visual redesign, diary grid geometry/stacking change, waiting-room panel change, taskpane, or Command Centre work.

## Files I Expect To Edit

Expected implementation files after approval: app/schemas/appointments.py to add confirm_endpoint/confirm_payload/freshness/signed evidence fields to AppointmentCreateProposalOut or a sibling neutral human-create confirm input if needed; app/routers/appointments.py to mint signed create-confirm evidence for safe create proposals, add/alias a staff create-confirm route if the Bernie-named route is too coupled, validate purpose/freshness/entity/practice/revalidation/warning acceptance, and record bounded audit evidence; docs/diary/diary.js to make create-mode Save post proposal.confirm_payload with confirmed=true and accepted warning codes, never raw POST when confirm evidence is present, and PATCH status only after confirmed_write plus appointment.id; review/test_diary_smoke.py for modal Save network invariants; tests/test_appointment_proposals.py, tests/test_bernie_confirm_create_proposal.py or a new focused create-confirm invariant test file, tests/test_appointment_audit.py, and tests/test_appointment_audit_warning_summary.py for backend adversarial/audit coverage. Cache-bust docs/diary/diary.html only if diary.js changes during implementation.

## Implementation Steps

1. Add backend create proposal evidence for safe proposals: confirm_endpoint, confirm_payload, proposal_freshness_id and/or candidate_freshness_id where applicable, signed_confirmation_evidence with create-confirm purpose, and default confirmed=false. Preserve blocked proposals as non-confirmable. 2. Keep confirm authoritative: require confirmed=true, verify signed evidence purpose and payload, recompute proposal freshness from command/reference state, validate practice-scoped patient/practitioner/type/location, re-run create proposal conflict/break/provisional checks against current state, require the revalidated command to match submitted evidence, and fail closed without writes/audit rows on stale/tampered/mismatched/cross-practice/cross-entity inputs. 3. Carry accepted warnings as codes: merge proposal warnings, revalidated warnings, and staff-confirmed codes through the confirm payload into create audit evidence; sanitize to known codes and keep PHI/human text out. 4. Update diary create-mode Save only after approval: use the existing proposal returned before warning confirmation, set confirmPayload.confirmed=true, merge accepted warning codes, POST normalizeApiPath(confirm_endpoint), require safe=true and autonomy_tier=confirmed_write, use returned appointment.id for any subsequent status PATCH, and remove direct POST /appointments from the signed-capable create path. 5. Preserve status-after-create as separate: if requested status is not Booked, issue PATCH /appointments/{newId}/status only after create confirm succeeds and returns an appointment id; do not include status in create-confirm evidence and do not PATCH on blocked, stale, 4xx/5xx, missing-id, or non-confirmed_write results. 6. Preserve compatibility boundary: keep raw POST /appointments authenticated for external/API/old-client compatibility and possibly as an explicit old-backend fallback only when no confirm_endpoint/confirm_payload is returned; document and test that current signed-capable UI fixtures do not use it. 7. Add adversarial tests before/with implementation: missing confirmed=true, missing evidence when required, tampered signature, wrong purpose, changed command fields, stale freshness/reference date, cross-appointment or mismatched selection/create evidence if the route still uses SlotSelectionProposalOut, cross-practice patient/practitioner/type/location, newly inserted conflict between proposal and confirm, warning acceptance mismatch, no audit row on block, one create audit row on success, and separate status audit only after successful create. 8. Add deterministic Diary smoke: route intercept modal create Save with proposal confirm_payload, assert confirm endpoint called once and raw POST /appointments not called; warning path requires Confirm & Save and sends warning codes; non-Booked status PATCH runs after confirm success only; failed/stale confirm prevents status PATCH and success copy.

## Visual / Behavioural Acceptance Checks

Backend: safe create proposals expose signed confirm evidence; blocked proposals expose no confirmable payload; confirmed create writes exactly one appointment with bounded audit evidence; stale/tampered/wrong-purpose/mismatched/cross-practice/new-conflict confirmations return blocked or error without mutation or audit; accepted warning codes persist and are code-only. Frontend: create-modal Save in non-smoke signed-capable mode calls /appointments/proposals/create then signed create-confirm, never raw POST /appointments; warning UI still requires staff confirmation; status-after-create remains a separate PATCH only after confirmed_write and returned appointment.id; failure leaves the modal open with an error and no status PATCH. Regression: edit-modal update confirm, drag/drop/resize update confirm, status controls, cancel/delete, waiting room panels, diary grid layout, and smoke fixtures keep current behaviour. Verification target: focused pytest for create proposal/confirm/audit invariants; node --check docs/diary/diary.js; review/test_diary_smoke.py focused G4 modal tests plus adjacent G3 status-boundary checks; scripts/check_frontend_versions.py if assets changed; git diff --check.

## Risks / Ambiguities

The existing confirm route name is Bernie-specific and expects SlotSelectionProposalOut; reusing it for human create may be expedient but semantically awkward, while adding a neutral alias/input risks duplication. Decide during implementation whether to create a thin neutral staff-confirm wrapper over the same validator. Existing create proposal evidence lacks slot-selection candidate freshness for freehand modal inputs, so freshness should be command/proposal-state based and tied to current conflict/roster-revalidation rather than pretending a slot-search candidate exists. Old-backend fallback may be useful for compatibility but weakens the no-raw-POST invariant if not tightly gated and tested. Status-after-create can produce two audit rows on successful non-Booked create; tests should assert that separation is intentional, and that no status audit appears when create confirm fails.

## Codex Plan Review

- Review result: Accepted as invariant guidance for the G4 implementation.
- Required changes before implementation: Bound raw create fallback to missing confirm envelopes; prove failed create-confirm does not trigger status PATCH.
- Approved to proceed: yes, implemented by Ariadne on `master`.
