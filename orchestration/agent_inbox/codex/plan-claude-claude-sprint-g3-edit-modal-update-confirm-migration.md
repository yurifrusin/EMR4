# plan-claude-claude-sprint-g3-edit-modal-update-confirm-migration

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-g3-edit-modal-update-confirm-migration` |
| Status | integrated |
| Created | 2026-07-04 07:26 +1000 |
| Source HEAD | `84a0934` |

## Plan Summary

Migrate the diary edit modal Save (appointment-detail update) onto the signed /appointments/proposals/update/confirm route, mirroring the G2 drag/resize path, while keeping the status change a separate PATCH and keeping raw PUT as a bounded fallback.

## My Understanding

Edit-mode saveBooking() already POSTs /appointments/proposals/update/{id} for warning-gating, but commits the detail change via raw PUT /appointments/{id} then a separate PATCH /appointments/{id}/status. G2 already migrated drag/drop/resize (diary.js ~7680-7711) to commit through proposal.confirm_endpoint + proposal.confirm_payload (signed_confirmation_evidence, update_proposal_freshness_id), setting confirmed=true and confirmed_warnings, then validating the response is safe===true and autonomy_tier==='confirmed_write', with raw PUT as fallback when no confirm envelope. Backend already exposes the confirm route, signs evidence, and computes freshness; the update command payload (_appointment_update_command_payload) contains NO status field, so status is legitimately outside the confirm write and must stay a separate PATCH. G3 = bring the edit modal detail Save onto that same signed confirm path without disturbing the status PATCH or the two-click Confirm-and-Save warning UX.

## Intended Surface / Boundary

docs/diary/diary.js saveBooking() edit branch only (editingAppointmentId truthy), inside the existing booking/edit modal. The proposal fetch already present at diary.js:7114 is reused. No change to the create branch write semantics beyond shared proposal handling, no change to the drag/resize reschedule path, the status dropdown, the diary grid, appointment cards, booking slots, stacking, waiting room, break rendering, or the Command Centre / taskpane.

## Out Of Scope

Drag/drop/resize (already G2); status confirm grammar; cancel/delete/create migration; raw PUT endpoint removal; any visual redesign of the modal or grid; persisted PHI/session tables; GraphRAG; taskpane and Command Centre surfaces; introducing any broad action grammar.

## Files I Expect To Edit

docs/diary/diary.js (saveBooking edit branch commit path); docs/diary/diary.html (cache-bust ?v=N bump); review/test_diary_smoke.py (edit-modal update-confirm smoke assertion + status PATCH separateness); app/schemas/appointments.py or app/routers/appointments.py ONLY if a small contract gap surfaces during implementation (not expected — confirm route already serves G2).

## Implementation Steps

1) Refactor saveBooking so the update proposal fetch runs on every invocation of the edit branch (not only when !isConfirmed), so the signed evidence used at commit is always fresh for the exact payload; keep the warning-gating early-return guarded by !isConfirmed so the two-click Confirm-and-Save UX is unchanged. 2) In the edit-branch commit (currently diary.js:7200-7231), replace the raw PUT /appointments/{id} with the G2 confirm pattern: read proposal.confirm_endpoint and proposal.confirm_payload, deep-clone the payload, set confirmed=true and confirmed_warnings=union of existing + proposal.warnings codes, POST to normalizeApiPath(confirm_endpoint); fall back to raw PUT only when confirm_endpoint/confirm_payload are absent (e.g. simulateProposal in smoke mode, which returns no envelope). 3) Validate the confirm response like G2: require safe===true and autonomy_tier==='confirmed_write', else throw the first block/summary message. 4) Keep the subsequent PATCH /appointments/{id}/status call exactly as-is and AFTER a successful detail confirm, so appointment-detail update and status mutation stay two distinct calls. 5) Leave the smoke-mode mock mutation branch (diary.js:7179-7199) unchanged. 6) Bump the diary cache-bust ?v=N in diary.html and run scripts/check_frontend_versions.py. 7) Add/extend a review smoke test asserting the edit modal detail Save issues a POST to /appointments/proposals/update/confirm (or the confirm endpoint) and that a status change still issues a separate PATCH .../status.

## Visual / Behavioural Acceptance Checks

Editing an appointment's time/duration/practitioner/type/reason/patient-link and clicking Save (or Confirm and Save after a warning) writes the detail change through /appointments/proposals/update/confirm and succeeds only when the response is safe + confirmed_write. Changing the status dropdown still results in a separate PATCH /appointments/{id}/status. Modal opens, shows warnings, and closes identically to before; grid/cards/slots/waiting-room visuals unchanged. Smoke mode (?smoke=true) still mutates the mock cache without hitting the network. Stale/blocked confirm surfaces an error in the existing booking-error element rather than silently failing.

## Risks / Ambiguities

R1: the proposal object was previously scoped inside the !isConfirmed block, so on the second (Confirm and Save) click it was undefined; the fix must guarantee a fresh proposal+evidence at commit — mitigated by always fetching the proposal in the edit branch and only gating warnings on !isConfirmed. R2: freshness — signed evidence is bound to current_state+command; if the appointment changed server-side between proposal and confirm the confirm will reject as stale (correct, by design) and must show a clear error and reload. R3: ensure confirmed_warnings carries the proposal warning codes so a warned-but-accepted update is not re-blocked by the confirm route. R4: status must NOT be added to the confirm command payload (backend command excludes it); keep status PATCH separate. R5: smoke-mode simulateProposal returns no confirm envelope, so the raw-PUT fallback path must remain for that case only. Ambiguity: whether any backend change is needed — expected none since G2 uses the same route; will flag to Codex if a gap appears rather than expanding scope.

## Codex Plan Review

- Review result: Accepted and integrated by Ariadne.
- Required changes before implementation: Preserve the status/update boundary and add an adversarial smoke case proving a failed detail confirm does not patch status.
- Approved to proceed: yes
