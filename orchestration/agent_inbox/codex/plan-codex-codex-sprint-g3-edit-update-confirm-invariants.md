# plan-codex-codex-sprint-g3-edit-update-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-g3-edit-update-confirm-invariants` |
| Status | integrated |
| Created | 2026-07-04 07:25 +1000 |
| Source HEAD | `84a0934` |

## Plan Summary

Adversarial invariant plan for G3 edit modal signed update-confirm migration

## My Understanding

Sprint G3 should migrate only the edit modal appointment-detail Save path from raw PUT /appointments/{id} to the signed update-confirm route already introduced in G1 and consumed by drag/drop/resize in G2. The status dropdown is adjacent but separate: status changes must remain a distinct PATCH /appointments/{id}/status unless a future status-confirm grammar is explicitly added. The invariant I am planning for is that edit-mode detail updates use backend proposal evidence, explicit staff confirmation, freshness/revalidation, and bounded audit evidence, while raw PUT remains a compatibility API and the edit confirm UI cannot use it as confirmation authority.

## Intended Surface / Boundary

Primary frontend surface: docs/diary/diary.js saveBooking() when editingAppointmentId is set, specifically the appointment-detail update branch that currently calls PUT /appointments/${editingAppointmentId}. The existing status PATCH immediately after it is in scope only as a boundary to preserve and test separately, not to fold into update-confirm. Primary backend/test surface: app/schemas/appointments.py and app/routers/appointments.py only if a small contract adjustment is required; tests/test_appointment_update_proposal.py, tests/test_appointment_audit.py or tests/test_appointment_audit_warning_summary.py for signed update-confirm and audit invariants; review/test_diary_smoke.py for edit-modal network assertions. Nearby surfaces that must not change: drag/drop/resize behaviour, diary grid geometry/cards/stacking/slots, booking create flow, cancel/delete flow, status grammar semantics beyond the existing PATCH, waiting room panels/cards, Bernie panel, taskpane, Command Centre, GraphRAG/practice knowledge, and raw PUT endpoint availability.

## Out Of Scope

No production code during this planning turn. No drag/drop/resize migration work, no status-confirm grammar implementation, no cancel/delete/create changes, no raw PUT removal, no persisted sessions, no GraphRAG, no UI redesign or new modal copy beyond existing warning/confirm affordances, no diary grid/slot/card geometry changes, no taskpane/Command Centre work, no schema migration unless a later approved implementation proves it is unavoidable.

## Files I Expect To Edit

Expected later implementation files: docs/diary/diary.js for saveBooking() edit-mode update branch to consume proposal.confirm_endpoint/proposal.confirm_payload, set confirmed=true after the existing staff confirmation step, and POST the confirm endpoint instead of raw PUT; review/test_diary_smoke.py for edit-modal Save route-capture tests proving POST proposal then POST update/confirm and no raw PUT; tests/test_appointment_update_proposal.py for backend stale/tampered/mismatch/status-boundary update-confirm cases if gaps remain; tests/test_appointment_audit.py and/or tests/test_appointment_audit_warning_summary.py for single update audit row and bounded warning/evidence codes; app/routers/appointments.py or app/schemas/appointments.py only if the existing G2 confirm payload is missing detail-save fields or needs a tiny neutral naming/compatibility refinement. docs/diary/diary.html/css are not expected unless a missing stable test hook blocks the smoke test.

## Implementation Steps

1. Characterize current edit modal behaviour: proposal preflight POST /appointments/proposals/update/{editingAppointmentId}; warning branch uses Confirm & Save via saveBtn.dataset.confirmed; final edit update uses raw PUT; status dropdown always follows as separate PATCH /appointments/{id}/status. Record current status value comparison if available so implementation can avoid unnecessary status PATCH when status has not changed.
2. Reuse the G2 signed proposal evidence contract. For safe edit proposals, require confirm_endpoint, confirm_payload, update_proposal_freshness_id, signed_confirmation_evidence, and signed_confirmation_evidence_required. If an old backend omits evidence, decide whether the edit modal may keep the same explicit old-backend fallback as drag/resize or should fail closed; the plan preference is fail closed for confirm-grade UI unless Ariadne deliberately preserves a compatibility fallback with clear tests.
3. Plan frontend migration: when editingAppointmentId is set and proposal is safe, clone proposal.confirm_payload, set confirmed=true only after the existing confirmation path is satisfied, merge accepted warning codes into confirmed_warnings, POST normalizeApiPath(proposal.confirm_endpoint), and treat a response with safe!==true or autonomy_tier!==confirmed_write as a failed update without success copy. Do not include status in the update-confirm payload.
4. Preserve status boundary: after a successful detail update confirm, issue PATCH /appointments/{editingAppointmentId}/status only if the requested status differs from the original appointment status and only with the status payload. A failed/stale/tampered update confirm must prevent the status PATCH to avoid partial update/status divergence unless implementation explicitly proves the detail update was unnecessary and the user only changed status.
5. Add backend adversarial tests if coverage is missing: tampered signed evidence, wrong purpose, stale current appointment state, mismatched command fields, appointment id mismatch, cross-practice replay, newly conflicting appointment at confirm time, terminal status after proposal, warning acceptance with break_overlap/provisional_patient, and no mutation/no audit row on every blocked confirm. Confirm successful edit-detail update writes exactly one update audit row tied to authenticated staff and bounded code-only confirmed_warnings/audit evidence.
6. Add frontend smoke tests for edit modal Save: route-intercept POST /appointments/proposals/update/{id} returning signed confirm payload; click Save/Confirm & Save; assert captured POST /appointments/proposals/update/confirm has confirmed=true and accepted warning codes; assert no PUT /appointments/{id} is emitted from edit confirm UI; assert status PATCH remains separate and is sent only when the status field changes. Add stale/blocked confirm response fixture proving no success message, no status PATCH, and modal/error state is visible or diary reloads safely.
7. Keep create booking, delete/cancel, status controls outside the migration. Create still uses POST /appointments and status-after-create if non-Booked. Delete/cancel still follows its proposal/delete path. Drag/drop/resize remains covered by G2 tests and should not be touched except shared helper reuse if unavoidable.
8. Verification for later implementation: focused update-confirm/proposal/audit pytest; py_compile touched backend files if any; node --check docs/diary/diary.js; scripts/check_frontend_versions.py if diary assets change; focused review/test_diary_smoke.py edit-modal update-confirm tests; full review/test_diary_smoke.py if docs/diary is touched; git diff --check.

## Visual / Behavioural Acceptance Checks

Acceptance checks: edit modal appointment-detail Save uses signed update-confirm evidence and does not emit raw PUT from the confirm UI; stale/tampered/wrong-purpose/mismatched/cross-practice/replayed/newly-conflicting evidence fails closed without appointment mutation, status PATCH, or misleading audit row; successful detail update writes once and creates exactly one bounded update audit row for the authenticated staff user; accepted proposal warning codes are persisted as code-only evidence; status changes remain separate PATCH calls and are not smuggled into update-confirm; unchanged status should not create an unnecessary status audit if implementation can reliably detect it; raw PUT remains available for authenticated compatibility clients but is not used by the edit confirm UI. Visually, the existing edit modal Save / Confirm & Save flow should feel unchanged, with no diary grid/card/slot/stacking/waiting-room/status-control redesign.

## Risks / Ambiguities

Main risk: saveBooking currently updates details and then patches status in one user action, so a failed signed detail confirm must not leave a status-only mutation behind. Implementation should compare original versus requested status and sequence status PATCH only after confirmed detail success, or explicitly split pure-status saves from detail saves. Second risk: old-backend raw PUT fallback could undermine the purpose of G3 if left on the normal confirm path; if retained, it needs an explicit compatibility branch and smoke test proving signed-evidence-capable proposals do not use it. Third risk: the schema is still Bernie-named even though ordinary human proposals use it; renaming should be deferred unless necessary, and any neutralization must preserve G1/G2 compatibility. Finally, warning acceptance must not duplicate or admit arbitrary PHI/text in confirmed_warnings.

## Codex Plan Review

- Review result: Accepted and integrated by Ariadne.
- Required changes before implementation: Keep raw PUT as compatibility only, prove signed-confirm-capable edit saves do not use it, and prove failed detail confirms stop before status PATCH.
- Approved to proceed: yes
