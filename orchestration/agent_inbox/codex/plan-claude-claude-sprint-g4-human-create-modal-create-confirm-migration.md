# plan-claude-claude-sprint-g4-human-create-modal-create-confirm-migration

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-g4-human-create-modal-create-confirm-migration` |
| Status | integrated |
| Created | 2026-07-04 07:47 +1000 |
| Source HEAD | `bd917e8` |

## Plan Summary

Migrate the Diary human create-booking modal final Save (create mode) from raw POST /appointments to a new signed create-confirm route, mirroring the G3 edit-modal update-confirm migration, while keeping create UX, the warning flow, and the post-create status PATCH unchanged.

## My Understanding

The create-booking modal saveBooking() in docs/diary/diary.js already POSTs to /appointments/proposals/create to fetch warnings/blocks, but the create-mode write path (diary.js ~7250-7303) then ignores the proposal confirmation evidence and writes with a raw POST /appointments followed by a separate status PATCH when status is not Booked. G3 already did this migration for the EDIT path: the update proposal (appointments.py ~1190-1221) emits confirm_endpoint /api/v1/appointments/proposals/update/confirm, confirm_payload, update_proposal_freshness_id, and signed_confirmation_evidence, and diary.js ~7207-7247 posts the signed confirm_payload to that endpoint, checks safe==true and autonomy_tier==confirmed_write, and falls back to raw PUT only when no confirm evidence is present. G4 is the create-side analog. The existing /proposals/create/confirm-bernie route is NOT reusable here: it is bound to the Bernie slot-selection flow (selection_proposal, selected_candidate, select_slot_for_create_proposal). The human create modal has no slot-selection step, so the clean design is a new human create-confirm route /proposals/create/confirm that mirrors /proposals/update/confirm, reusing the existing write/revalidation helpers _build_create_appointment_proposal, _same_create_command, _check_create_command_entities, _create_body_from_command, _create_appointment_from_body.

## Intended Surface / Boundary

Surface affected: (1) the Diary create-booking MODAL Save path in create mode only (docs/diary/diary.js saveBooking, the editingAppointmentId-falsy branch); (2) backend appointments create-proposal plus a new human create-confirm endpoint. The diary GRID rendering, booking-slot cards, stacking/lanes, waiting-room, status colour bar, and the EDIT-mode Save path (owned by G3) must NOT change. The visible create modal layout, fields, warning banner, and the two-step Confirm and Save affordance must look and behave exactly as today.

## Out Of Scope

Edit/update writes (G3, already migrated); drag/drop/resize proposals; status confirm grammar and the separate status PATCH semantics; cancel/delete migration; removal of the raw POST /appointments endpoint; any visual redesign of the modal or grid; Bernie persisted sessions; the confirm-bernie slot route; GraphRAG; taskpane and Command Centre.

## Files I Expect To Edit

app/schemas/appointments.py (add confirm_endpoint/confirm_payload/create_proposal_freshness_id/signed_confirmation_evidence[_required] to AppointmentCreateProposalOut; add a new AppointmentCreateProposalConfirmationIn mirroring BernieUpdateProposalConfirmationIn); app/routers/appointments.py (emit create-confirm evidence in _build_create_appointment_proposal when safe; add POST /proposals/create/confirm route plus confirm handler plus create-proposal freshness/signed-payload helpers); app/services/bernie_turn_evidence.py (add a distinct SIGNED_CREATE_PROPOSAL_CONFIRMATION_EVIDENCE_PURPOSE constant, re-export via app/services/bernie/__init__.py); tests under tests/ (create-confirm backend happy-path/blocks/staleness plus create modal writes-through-confirm smoke); no migration (no schema change).

## Implementation Steps

1. Backend schema: extend AppointmentCreateProposalOut with confirm_endpoint, confirm_payload, create_proposal_freshness_id, signed_confirmation_evidence, signed_confirmation_evidence_required (all optional/defaulted, non-breaking); add AppointmentCreateProposalConfirmationIn with confirmed, create_proposal (AppointmentCreateProposalOut), confirmed_warnings, optional turn_ref, optional create_proposal_freshness_id, optional signed_confirmation_evidence, signed_confirmation_evidence_required, optional session_binding. 2. Evidence: add SIGNED_CREATE_PROPOSAL_CONFIRMATION_EVIDENCE_PURPOSE distinct from the Bernie bernie_confirm_create_proposal purpose so human create-confirm cannot be confused with the slot flow, and re-export it. 3. Add _compute_create_proposal_freshness_id and a human create signed-payload helper keyed off the AppointmentCreateCommand (mirror the update variants; PHI-safe UUID/date/time normalisation). 4. In _build_create_appointment_proposal, when safe, mint signed evidence plus freshness and set confirm_endpoint /api/v1/appointments/proposals/create/confirm and confirm_payload (confirmed false, create_proposal evidence subset, confirmed_warnings, create_proposal_freshness_id, signed_confirmation_evidence, signed_confirmation_evidence_required true), mirroring lines 1190-1221. 5. Add POST /proposals/create/confirm gated by require_role MUTATING_APPOINTMENT_ROLES; handler requires confirmed true; validates intent create_appointment, proposal safe and autonomy_tier proposal and requires_confirmation; verifies signed evidence with expected_purpose the create purpose; checks freshness id; revalidates via _build_create_appointment_proposal plus _same_create_command plus _check_create_command_entities; writes exactly ONE appointment via _create_appointment_from_body with confirmed_warnings and audit_evidence; returns AppointmentConfirmCreateProposalOut autonomy_tier confirmed_write; does NOT set status. 6. Frontend diary.js: in the create branch, when proposal has confirm_endpoint and confirm_payload, POST the signed confirm_payload (confirmed true, merged confirmed_warnings) to normalizeApiPath(confirm_endpoint), verify safe true and autonomy_tier confirmed_write, use the returned appointment id; else fall back to raw POST /appointments. Keep the existing status-PATCH step (when statusToSend is not Booked, PATCH /appointments/{id}/status) exactly as-is and separate. 7. Ensure a fresh proposal (carrying confirm evidence) exists at write time: today needsProposal is false on the warning-confirm second click for create (editingAppointmentId falsy and isConfirmed true), so broaden the create path to re-fetch a fresh create proposal immediately before the write (mirroring how edit always re-proposes) so signed evidence is present and not stale; smoke-mode simulateProposal path unchanged, guarded by isConfirmed on the warning-return block to avoid a double prompt. 8. Bump docs/diary/diary.js cache-bust v param per deploy discipline. 9. Tests: backend create-confirm happy path, missing/blocked confirmation, tampered/stale evidence, and that status stays a separate PATCH; frontend create-modal review smoke that create writes through the confirm endpoint when evidence is available.

## Visual / Behavioural Acceptance Checks

Create modal looks and behaves identically (fields, warning banner, two-step Confirm and Save). Creating a booking with no warnings writes exactly one appointment via /proposals/create/confirm and any non-Booked status is applied by a SEPARATE status PATCH. A booking with a break-overlap or provisional warning still shows the warning and only writes after the explicit confirm click, then writes through the signed confirm route. Blocked (conflict) proposals still cannot write. If the backend lacks the confirm endpoint/evidence, the modal falls back to raw POST /appointments (bounded compatibility) with no visible behaviour change. node --check docs/diary/diary.js passes; py_compile of touched backend files passes; new backend create-confirm tests and review/test_diary_smoke.py pass.

## Risks / Ambiguities

1. Freshness/evidence availability on the confirm click: create currently skips re-fetching the proposal when already confirmed, so the plan must re-fetch a fresh proposal before writing or the signed evidence will be absent/stale; needs care to avoid a double warning prompt. 2. Distinct signed-evidence purpose vs reusing the Bernie purpose: reusing would blur the human vs slot-flow boundary; the plan adds a distinct purpose, which the no-broad-action-grammar merge criterion favours. 3. Status separation: must NOT fold status into create-confirm; the post-create PATCH stays separate to preserve G-series semantics. 4. Raw POST /appointments retained only as bounded fallback, justified for older-backend compatibility, not as a parallel write grammar. 5. Smoke mode must remain fully client-side; no live provider claims. 6. Confirm the create-confirm route writes exactly once (single _create_appointment_from_body call) and does not double-create across revalidation and write.

## Codex Plan Review

- Review result: Accepted as the primary create-confirm migration plan.
- Required changes before implementation: Use a neutral staff create-confirm route rather than reusing Bernie slot-selection confirmation; keep status-after-create separate.
- Approved to proceed: yes, implemented by Ariadne on `master`.
