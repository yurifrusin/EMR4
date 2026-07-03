# plan-claude-claude-sprint-g2-human-diary-update-confirm-route-migration

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-g2-human-diary-update-confirm-route-migration` |
| Status | integrated |
| Created | 2026-07-04 07:07 +1000 |
| Source HEAD | `85166f0` |

## Plan Summary

Migrate human Diary drag/drop/resize appointment updates from raw PUT /appointments/{id} to the G1 signed /proposals/update/confirm route, by having the existing propose_update_appointment route mint signed confirmation evidence for safe proposals, while keeping raw PUT as an explicit bounded compatibility surface and preserving the fast drag/drop/resize edit UX.

## My Understanding

G1 introduced an evidence-gated update-confirm grammar. Backend confirm_update_proposal (exposed at POST /proposals/update/confirm) verifies signed evidence, an update_proposal_freshness_id, a fresh server-side revalidation via propose_update_appointment, and _same_update_command equality before calling _apply_appointment_update. Today only the Bernie extend tool-intent path mints that signed evidence; the human diary path does NOT. In docs/diary/diary.js, handleMoveResize (drag/drop/resize) POSTs /proposals/update/{id} for a proposal, optionally shows showStatusProposalDialog, then writes via raw PUT /appointments/{id}. So human updates bypass the signed confirm grammar entirely. The propose_update_appointment route returns AppointmentUpdateProposalOut, which currently has NO signed-evidence fields. Goal: route human drag/drop/resize writes through the same signed confirm endpoint so human and Bernie updates share one evidence-gated write path, without breaking the responsive UX or the raw PUT compatibility endpoint.

## Intended Surface / Boundary

ONLY the Diary grid drag/drop/resize update write path: docs/diary/diary.js handleMoveResize and its showStatusProposalDialog confirmation branch, plus the backend update proposal/confirm contracts in app/routers/appointments.py and app/schemas/appointments.py. The diary grid layout, appointment card visuals/stacking, colour bars, time ruler, waiting-room, booking-create flow, status/cancel/delete flows, taskpane, and Command Centre must NOT change. showStatusProposalDialog visual behaviour is reused unchanged (still returns a boolean confirm).

## Out Of Scope

The edit-form Save PUT path (diary.js around line 7200) stays on raw PUT this sprint as the deliberate bounded compatibility surface; not migrated here (flagged as follow-up). Broad status/waiting-area/cancel/delete grammar; Bernie auto-mode; persisted PHI/session tables; GraphRAG; taskpane/Command Centre; any visual redesign of the diary grid/cards; and removing the raw PUT /appointments/{id} compatibility endpoint (kept, used by smoke mode and as fallback).

## Files I Expect To Edit

app/schemas/appointments.py: add five OPTIONAL, defaulted fields to AppointmentUpdateProposalOut (confirm_endpoint, confirm_payload, update_proposal_freshness_id, signed_confirmation_evidence, signed_confirmation_evidence_required) - additive and backward compatible. app/routers/appointments.py: in propose_update_appointment, when the proposal is safe, mint signed evidence + freshness id (reusing _appointment_update_state_payload, _compute_update_proposal_freshness_id, _bernie_update_signed_confirmation_payload with turn_ref=None/session_binding=None, mint_signed_confirmation_evidence) and populate the new fields + a confirm_payload matching BernieUpdateProposalConfirmationIn. docs/diary/diary.js: handleMoveResize confirm branch posts /proposals/update/confirm using the proposal response evidence instead of raw PUT; keep raw PUT for isSmokeMode and as guarded fallback. docs/diary/diary.html: bump diary.js/diary.css ?v= (currently js v=162). tests/test_appointment_update_proposal.py and tests/test_appointment_audit.py (or a focused new test): assert propose emits signed evidence for safe proposals, human confirm succeeds and writes, and stale/tampered/mismatched evidence is blocked. review/test_diary_smoke.py only if drag/drop/resize smoke assertions need updating.

## Implementation Steps

1) Backend schema: add the five optional defaulted fields to AppointmentUpdateProposalOut so responses can carry signed evidence without breaking existing callers (Bernie tool-intent ignores them). 2) Backend route: in propose_update_appointment, after computing safe, when safe mint signed evidence with turn_ref=None and session_binding=None and reference_date=command.appointment_date (identical inputs to what confirm_update_proposal recomputes), set signed_confirmation_evidence, signed_confirmation_evidence_required=True, update_proposal_freshness_id, confirm_endpoint=/api/v1/appointments/proposals/update/confirm, and confirm_payload={confirmed:false, update_proposal:<self>, confirmed_warnings:[warning codes], update_proposal_freshness_id, signed_confirmation_evidence, signed_confirmation_evidence_required:true}. Leave evidence null when not safe (blocks path unchanged). 3) Frontend: in handleMoveResize, after showStatusProposalDialog returns confirmed, if not smoke mode and the proposal carries confirm_endpoint/signed evidence, POST /proposals/update/confirm with confirm_payload (setting confirmed:true and merging any confirmed_warnings) instead of raw PUT; on success reload+scroll as today. Keep the raw PUT branch for isSmokeMode and as an explicit fallback when the proposal lacks signed evidence, so behaviour degrades safely. 4) Version bump diary.html and run check_frontend_versions.py. 5) Tests as above. 6) Run verification. 7) Fill Completion Notes and submit.

## Visual / Behavioural Acceptance Checks

Drag/drop/resize a booking on the diary grid: the confirm dialog appears exactly as before for warnings/proposals; on confirm the appointment moves/resizes and persists via /proposals/update/confirm (verify audit shows the update with bernie_signed_confirmation_evidence_verified evidence). No-op micro-moves still short-circuit (unchanged). A stale proposal (appointment changed underneath) is blocked with stale_update_proposal_freshness_id rather than silently overwriting. Tampered command/evidence is blocked (revalidation_mismatch / signature failure). Diary grid layout, card visuals, stacking, colour bars, time ruler, and all non-update flows are visually and behaviourally identical. Smoke mode (?smoke=true) still works via the mock/raw path. node --check docs/diary/diary.js passes; py_compile of touched backend files passes; focused update/proposal/audit tests and relevant diary smoke pass; check_frontend_versions.py passes.

## Risks / Ambiguities

1) Double-write asymmetry: edit-form Save still uses raw PUT this sprint - intentional bounded compat, flagged as follow-up G3; reviewers may prefer migrating both now. 2) Signed-payload input parity: propose and confirm must compute the identical signed payload (turn_ref, session_binding, reference_date, current_state, freshness id) or every human confirm blocks; mitigated by mirroring the Bernie extend inputs exactly and by tests. 3) reference_date choice: using command.appointment_date must match confirm which uses command.appointment_date when turn_ref is None - verified against confirm_update_proposal. 4) Freshness race is now enforcing where it previously was not, so a legitimate concurrent edit will block a drag where raw PUT would have silently won; this is the intended safety win but changes UX on conflict - dialog must surface it clearly. 5) Minting evidence in propose_update_appointment slightly changes that shared route response; Bernie tool-intent calls it internally and must remain unaffected (it reads only .safe/.command/.warnings/.blocks) - confirm by inspection/tests. 6) Keeping raw PUT open means the compatibility bypass still exists; acceptable and required this sprint, noted for a later lockdown decision.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
