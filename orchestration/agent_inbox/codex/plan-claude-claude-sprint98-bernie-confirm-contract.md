# plan-claude-claude-sprint98-bernie-confirm-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint98-bernie-confirm-contract` |
| Status | integrated |
| Created | 2026-07-01 12:14 +1000 |
| Source HEAD | `ca8b293` |

## Plan Summary

Fix three Bernie confirm-contract leaks: resolved practitioner_id must never surface as missing; confirm-ready staff_review payload must round-trip end to end into confirm-bernie; and confirm-bernie must return precise structured blocks instead of a generic HTTP 404 for a valid staged proposal whose referenced entity is unresolvable. Backend/API + focused tests only; no frontend, no autonomous booking, staff confirmation preserved.

## My Understanding

Sprint 98 targets three staff-visible defects in the supervised (non-mutating) Bernie booking chain. (1) A receptionist prompt like 'Make an appointment for Margaret Thompson after 3 today with Dr Shera' should resolve 'Dr Shera' to a practitioner_id; interpret-booking-instruction already resolves names in _resolve_bernie_interpretation_context and recomputes missing_fields, but there is no regression test proving practitioner_id is present and never listed in missing_fields for this canonical case, and propose_bernie_supervised_booking does not resolve names so a dropped id re-blocks as missing_practitioner. (2) The confirm-ready staff_review.confirm_payload embeds the entire selection_proposal (the evidence/'token'); no test proves that payload round-trips (flip confirmed=true) back through /proposals/create/confirm-bernie to a real write. (3) confirm_bernie_create_proposal revalidates through _build_create_appointment_proposal, which calls _ensure_patient/_ensure_practitioner/_ensure_appointment_type/_ensure_location; each raises a bare HTTPException(404, '...not found'). So a staged proposal whose referenced entity is missing/out-of-scope at confirm time fails with a generic 404 Not Found instead of a structured AppointmentConfirmCreateProposalOut carrying precise blocks and no write.

## Intended Surface / Boundary

Backend only: app/routers/appointments.py (Bernie interpret/resolve, supervised-booking wrapper, confirm-bernie revalidation, entity-existence helpers) and app/schemas/appointments.py only if a precise block-code or evidence field proves strictly necessary (AppointmentProposalIssue.code is already a free string, so likely no schema change). New focused pytest module tests/test_bernie_sprint98_confirm_contract.py. No diary UI, taskpane, or Command Centre surfaces are touched; 'staff_review', 'confirm_payload', 'candidate_slots', and 'confirmation_ready' are API response fields, not visual diary components, and their shapes stay stable.

## Out Of Scope

No frontend/diary/taskpane/Command Centre edits; no GraphQL/API-spine work; no Caller ID, Medicare/OPV/PVM/IHI, SMS, billing; no live provider/Gemini/GCP changes; no autonomous booking or weakening of explicit staff confirmation; no broad appointment/audit redesign; no migrations unless a model actually changes (not expected). Do not change the meaning of existing block codes consumed elsewhere; only add new precise codes and a non-raising revalidation path.

## Files I Expect To Edit

EDIT app/routers/appointments.py — add a non-raising entity-existence check (e.g. _missing_entity_blocks) and route confirm-bernie revalidation through it so missing patient/practitioner/appointment_type/location become structured blocks (patient_not_found/practitioner_not_found/appointment_type_not_found/location_not_found) in AppointmentConfirmCreateProposalOut instead of a bare 404; keep the raising _ensure_* helpers for the direct create/edit routes unchanged. Confirm resolved practitioner_id remains authoritative and missing_fields is always recomputed post-resolution. NEW tests/test_bernie_sprint98_confirm_contract.py — the focused proofs below. Possibly EDIT app/schemas/appointments.py only if a precise field is unavoidable (aim: none).

## Implementation Steps

1) Add a non-raising existence helper that returns AppointmentProposalIssue blocks for any missing/out-of-scope patient, practitioner, appointment_type, or location (practice-scoped), mirroring the _ensure_* queries. 2) In confirm_bernie_create_proposal, before/around the _build_create_appointment_proposal revalidation, run the non-raising check on create_proposal.command entities; if any block, return _block_bernie_create_confirmation(blocks, ...) with audit_evidence and zero writes — never a bare 404. Ensure the happy path still writes exactly one appointment + bounded audit. 3) Guarantee resolved practitioner_id is authoritative end to end: verify _resolve_bernie_interpretation_context sets practitioner_id and recomputes missing_fields; if the supervised-booking wrapper is the actual leak point, thread the resolved id through rather than re-blocking. 4) Add end-to-end token round-trip: drive supervised-booking to confirmation_ready, take staff_review.confirm_payload, set confirmed=true, POST confirm-bernie, assert 200 + one write. 5) Run focused + adjacent Bernie pytest and py_compile.

## Visual / Behavioural Acceptance Checks

pytest proofs: (a) canonical prompt 'Make an appointment for Margaret Thompson after 3 today with Dr Shera' via interpret-booking-instruction yields command_candidate.practitioner_id == practitioner.id, emits practitioner_name_resolved, and missing_fields excludes 'practitioner_id'; (b) supervised-booking confirmation_ready staff_review.confirm_payload, resubmitted with confirmed=true, confirms and writes exactly one appointment; (c) a staged-then-invalidated entity (e.g. practitioner removed/out-of-scope) at confirm time returns HTTP 200 with a precise block code (not 'Not found'), and zero appointment/audit rows; (d) unconfirmed/blocked/mismatch/stale-conflict paths still write nothing; (e) audit trail remains staff-confirmed with bounded evidence. Behavioural: no bare 404 for a valid staged proposal; confirm remains explicit-staff-gated; no LLM/provider calls in confirm path.

## Risks / Ambiguities

Root-cause hypothesis for the 'Not Found' is the raising _ensure_* helpers inside the revalidation path; will confirm by reproducing in a test before changing code. Must not alter the direct POST '' / PUT /{id} routes that legitimately 404. Adding new block codes must not collide with codes asserted elsewhere. Bug 1 may already be correct in interpret; if so the fix is regression tests plus (only if reproduced) threading the resolved id through supervised-booking. Whether to introduce an explicit compact confirmation token vs. keep the full selection_proposal as the evidence bundle: default is to keep the existing bundle (round-trips already, smaller change) and only add a token if the round-trip test reveals a serialization break. Keep the change small enough to finish before Sprint 99 API-spine planning.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
