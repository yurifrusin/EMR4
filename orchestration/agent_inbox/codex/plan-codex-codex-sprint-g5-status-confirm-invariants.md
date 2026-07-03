# plan-codex-codex-sprint-g5-status-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-g5-status-confirm-invariants` |
| Status | integrated |
| Created | 2026-07-04 08:11 +1000 |
| Source HEAD | `06ea955` |

## Plan Summary

Adversarial invariant plan for signed status-confirm migration

## My Understanding

Migrate status-only Diary writes from the direct PATCH /api/v1/appointments/{id}/status UI path to a backend-owned signed status-confirm flow. The existing raw PATCH remains an authenticated staff/API compatibility endpoint, but signed-capable diary controls should first obtain a status or waiting-area proposal carrying confirm_endpoint, confirm_payload, status freshness evidence, and signed evidence, then post confirmed=true to the status confirm endpoint. The invariants must prove evidence purpose binding, current appointment state binding, practice scoping, waiting-area semantics, failed-confirm no-write behavior, and audit evidence. The affected visible surface is the Diary appointment status and patient-flow/waiting-area controls; nearby booking cards, appointment slots, stacked/overlap grid layout, edit/create detail confirm routes, Bernie booking grammar, taskpane, and Command Centre must not change.

## Intended Surface / Boundary

Backend schema/router contract plus deterministic Diary status-control network path. Backend boundary: app/schemas/appointments.py and app/routers/appointments.py only for status/waiting-area proposal/confirm types, signed evidence payload helpers, status confirm route, and shared status-apply behavior. Frontend boundary: docs/diary/diary.js status-only paths, especially setAppointmentStatus and edit/create-modal status follow-up PATCH calls. Test boundary: tests/test_appointment_status_mutations.py, tests/test_appointment_audit.py, tests/test_waiting_area_checkin_contract.py, and review/test_diary_smoke.py. The Diary grid layout, booking slot rendering, card stacking, panels, patient-flow list visuals, and waiting-room scan surface should remain visually unchanged apart from using the signed confirm network route after staff confirmation.

## Out Of Scope

No create/edit detail confirm redesign, no cancel/delete confirm migration, no broad Bernie action grammar, no persisted sessions, no GraphRAG, no taskpane or Command Centre changes, no visual redesign, no removal of the raw PATCH compatibility endpoint in this sprint, and no changes to appointment slot layout or diary card stacking.

## Files I Expect To Edit

Expected later implementation edits: app/schemas/appointments.py; app/routers/appointments.py; docs/diary/diary.js; tests/test_appointment_status_mutations.py; tests/test_appointment_audit.py; tests/test_waiting_area_checkin_contract.py; review/test_diary_smoke.py. Plan gate changed only coordination packet files.

## Implementation Steps

1. Add status-confirm schema fields parallel to create/update: extend AppointmentStatusProposalOut and AppointmentWaitingAreaProposalOut or introduce shared status-confirm output/input models with confirm_endpoint, confirm_payload, status_proposal_freshness_id, signed_confirmation_evidence, and signed_confirmation_evidence_required. 2. Add backend helpers for appointment status state payload and status proposal freshness binding that include appointment_id, practice_id, current status, waiting_area_id, terminal/active semantics as needed, target status, target waiting_area_id with explicit absent/null distinction, clears_waiting_area, and staff user/practice binding. 3. Mint signed evidence from /proposals/status/{id} and /proposals/waiting-area/{id} only for safe proposals, using a new status-confirm purpose rather than reusing create/update purpose. 4. Add POST /appointments/proposals/status/confirm that requires confirmed=true, verifies signed evidence purpose and payload, recomputes freshness against the current appointment state, revalidates waiting_area_id in the caller practice, blocks stale/tampered/cross-practice evidence, applies exactly one status/waiting-area mutation through a shared internal helper, and writes bounded audit evidence. 5. Keep PATCH /appointments/{id}/status as authenticated compatibility, ideally delegating to the same internal apply helper, but do not let the signed-capable Diary flow use it after proposal evidence is available. 6. Migrate docs/diary/diary.js setAppointmentStatus so non-smoke proposals with confirm_payload post to confirm_endpoint with confirmed=true and confirmed warning codes; preserve smoke-mode simulation and old-backend/raw PATCH fallback only when confirm evidence is absent. 7. Migrate edit/create modal status-only follow-up writes to the same proposal/confirm helper where they are status-only; keep detail update/create confirm routes separate and do not mix appointment detail status semantics into update/create evidence. 8. Add backend adversarial tests for missing confirmed, missing evidence, wrong-purpose create/update evidence, tampered command/status/waiting_area_id, stale current appointment status or waiting_area_id, cross-practice appointment/evidence/area, inactive area, no audit row/no state change after failed confirm, terminal status clearing waiting_area_id, waiting-area-only reassignment/removal, and raw PATCH compatibility. 9. Add audit tests proving successful status confirm records status_change with status_before/status_after, confirmed warning codes, and signed status evidence, while failed confirm writes no audit. 10. Add deterministic Diary smoke route-intercept tests proving signed-capable status buttons and waiting-area selectors call proposal then status confirm, do not call raw PATCH, set confirmed=true, preserve warning confirmation behaviour, and fall back only in smoke/unsigned compatibility cases.

## Visual / Behavioural Acceptance Checks

Backend: safe status and waiting-area proposals expose confirm_endpoint/confirm_payload/freshness/signed evidence; confirm succeeds once when evidence matches the current appointment and practice; confirm fails closed for stale, tampered, wrong-purpose, missing evidence, cross-practice, inactive-area, and blocked proposal cases; failed confirm leaves appointment status/waiting_area_id/audit unchanged; successful terminal status clears waiting_area_id when absent/null semantics require it; raw PATCH remains covered as compatibility. Frontend: Diary status dropdowns, patient-flow Check In/Start Consult buttons, and waiting-area selectors use the confirm endpoint when proposal evidence is present; route-intercept smoke observes no PATCH /appointments/{id}/status from signed-capable paths; visible diary cards, slots, panels, waiting-room lists, and stacking do not visually change. Verification later: focused appointment status/audit/waiting-area pytest suites, node --check docs/diary/diary.js, pytest review/test_diary_smoke.py -q or targeted status-confirm smoke, and git diff --check.

## Risks / Ambiguities

Key ambiguity: waiting_area_id currently relies on Pydantic model_fields_set to distinguish omitted from explicit null, so status confirm evidence must preserve that absent/null distinction or terminal-status clearing and area preservation can regress. Edit/create modal status follow-up paths may need careful sequencing so a failed status confirm does not leave users thinking the whole edit/create failed after details already succeeded; keep status PATCH semantics separate from update/create confirm evidence. Raw PATCH compatibility is a deliberate residual risk, but the sprint should make signed-capable UI avoid it and keep adversarial tests around both routes. Naming should avoid confusing status confirm with update confirm; evidence purpose must be distinct.

## Codex Plan Review

- Review result: Accepted as the G5 invariant plan.
- Required changes before implementation: Keep status-confirm evidence purpose distinct from create/update; preserve waiting_area_id omitted-vs-null semantics; keep raw PATCH as compatibility only.
- Approved to proceed: yes, implemented by Ariadne on `master`.
