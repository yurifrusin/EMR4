# plan-codex-codex-sprint-g2-update-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-g2-update-confirm-invariants` |
| Status | integrated |
| Created | 2026-07-04 07:04 +1000 |
| Source HEAD | `85166f0` |

## Plan Summary

Adversarial invariant plan for G2 human diary update-confirm migration

## My Understanding

Sprint G2 should migrate human Diary appointment update interactions, especially edit-modal saves and drag/drop/resize move-resize writes, from proposal-then-raw-PUT to the G1 signed update-confirm route. The goal is not a new broad action grammar; it is to make human UI updates and Bernie update confirms share the same backend-owned evidence, freshness, revalidation, staff confirmation, and audit semantics while preserving the fast receptionist interaction. Raw PUT remains a bounded staff/API compatibility path, but the Diary confirm UI must not use it as the authoritative confirm path after this migration.

## Intended Surface / Boundary

Primary backend surface: existing appointment update proposal and signed update-confirm contracts in app/schemas/appointments.py and app/routers/appointments.py, plus focused tests around tests/test_appointment_update_proposal.py, tests/test_bernie_tool_intent.py, tests/test_appointment_audit.py, and warning/audit tests if needed. Primary frontend surface: docs/diary/diary.js update flows that currently call POST /appointments/proposals/update/{id} followed by PUT /appointments/{id}: edit modal saveBooking() and drag/drop/resize handleMoveResize(). Review surface: review/test_diary_smoke.py only for structural proof that human move/resize/edit confirms POST the confirm endpoint and no longer use raw PUT from the Diary UI. Nearby surfaces that must not change: diary grid layout/stacking/overlap geometry, appointment cards beyond their existing drag/resize behaviour, booking slot search, Waiting Room panels/cards, status/waiting-area controls, cancellation/delete flow, create-booking flow except shared helper compatibility if unavoidable, taskpane, Command Centre, GraphRAG/practice knowledge, and persisted session storage.

## Out Of Scope

No production code during this planning turn. No broad status/cancel/delete/create grammar migration, no raw PUT removal or breaking external staff/API compatibility, no persisted Bernie/session tables, no GraphRAG, no auto-mode, no UI redesign or new modal-heavy interaction, no diary grid geometry/stacking changes, no waiting-room/status/cancellation/taskpane/Command Centre work, no migration or schema table work unless a later approved implementation proves it is truly required.

## Files I Expect To Edit

Expected later implementation files: tests/test_appointment_update_proposal.py for human-update confirm evidence, replay, stale, mismatch, warning acceptance, and raw-PUT boundary tests; tests/test_appointment_audit.py and/or tests/test_appointment_audit_warning_summary.py for audit evidence/confirmed_warnings rows; tests/test_bernie_tool_intent.py as a regression guard that Bernie still uses the same signed route; app/schemas/appointments.py if the update-confirm input should be renamed/generalized from BernieUpdateProposalConfirmationIn to a neutral human/Bernie update-confirm payload while retaining compatibility aliases; app/routers/appointments.py if proposal output needs confirm_endpoint/confirm_payload for human flows or a helper to mint signed update-confirm payloads for all update proposals; app/services/bernie_turn_evidence.py only if evidence purpose/naming must be generalized without changing G1 verification semantics; docs/diary/diary.js for saveBooking() and handleMoveResize() to POST the signed confirm payload instead of raw PUT; review/test_diary_smoke.py for focused edit/drag/resize confirm-route assertions if docs/diary changes; docs/diary/diary.html or css only if an existing control id/test hook is missing, not for redesign.

## Implementation Steps

1. Preserve and characterize G1: keep /appointments/proposals/update/confirm as the single signed update write route, or generalize its schema/name without breaking Bernie payloads. Confirm the signed evidence purpose, current-state payload, update_proposal_freshness_id, command binding, revalidation, and _apply_appointment_update shared writer remain intact.
2. Teach the ordinary update proposal route to provide human-usable confirm evidence when safe: confirm_endpoint, confirm_payload, freshness id, signed_confirmation_evidence, and signed_confirmation_evidence_required. If these fields are already present in a shared helper, reuse it; if added, keep them optional/additive so existing proposal consumers do not break.
3. Add backend adversarial tests before relying on the UI: missing confirmed=true, missing signed evidence, wrong purpose/create evidence, tampered signature, stale current appointment state after someone else edits the appointment, command/proposal mismatch, appointment id mismatch between URL/proposal/evidence, cross-practice replay, replay against another appointment, replay after conflict appears, terminal status after proposal, warning acceptance mismatch, and no audit row on every blocked confirm.
4. Add successful human-confirm tests: a safe move, resize, and column/practitioner move confirm through the signed route updates exactly one appointment, reuses normal update conflict/tenant validation, creates exactly one update audit row tied to the authenticated staff user, and persists bounded code-only audit evidence/confirmed_warnings including accepted proposal warnings such as break_overlap/provisional_patient where applicable.
5. Keep raw PUT compatibility explicit: retain PUT /appointments/{id} for staff/API compatibility with existing RBAC, conflict validation, and audit. Add or preserve tests proving raw PUT does not accept signed-evidence authority fields, model/staff text, confirm_endpoint, confirm_payload, or audit_evidence as a shortcut, and document in tests/plan that Diary UI no longer uses raw PUT for drag/drop/resize confirm writes.
6. Migrate Diary edit modal saveBooking(): after the update proposal check, store/echo the backend confirm payload, set confirmed=true only after the current staff confirmation step, include accepted warning codes, POST normalizeApiPath(confirm_endpoint), and avoid the old raw PUT for editingAppointmentId update writes. Preserve current status PATCH behaviour only if status is actually a separate status change; do not smuggle status changes through update-confirm.
7. Migrate handleMoveResize(): proposal preflight stays; safe/no-warning moves may remain visually fast, but the network write should POST the signed confirm payload with confirmed=true. Warning/blocked proposals continue to use the existing confirmation dialog/revert behaviour. Cancel/reject reloads the diary and does not write. Smoke mode keeps local mock behaviour.
8. Add focused Diary smoke assertions if UI touched: edit modal update and drag/resize update capture POST /appointments/proposals/update/{id}, then POST /appointments/proposals/update/confirm; assert no PUT /appointments/{id} is emitted for those human update confirm paths; assert cancelled warning dialog writes nothing; assert stale/blocked confirm response reloads/reverts without changing local success copy.
9. Run verification in tiers: focused backend update-confirm/proposal/audit tests; py_compile touched backend files; node --check docs/diary/diary.js if touched; scripts/check_frontend_versions.py if diary asset versions change; focused review/test_diary_smoke.py human update-confirm fixtures, then full deterministic Diary smoke harness if docs/diary was touched; git diff --check.

## Visual / Behavioural Acceptance Checks

Acceptance checks: human edit, drag/drop, and resize update writes in the Diary UI use backend-signed update-confirm evidence instead of raw PUT; signed evidence cannot be replayed across appointments, practices, staff users, stale appointment states, wrong purposes, mismatched commands, or newly blocked conflicts; warning acceptance is explicit and bounded to code-only audit fields; successful confirms write once, audit once, and identify the authenticated staff user; failed/tampered/stale/conflicting confirms mutate nothing and write no misleading audit row; raw PUT remains available as a bounded compatibility endpoint but is not used by the Diary confirm UI and cannot be granted extra authority by confirm payload text or model/staff prose. Visually, normal safe drag/resize/edit should feel as fast as before, warning/blocked dialogs should behave as before, and diary grid cards, slots, stacking, waiting room panels, status controls, and booking-slot search should remain unchanged.

## Risks / Ambiguities

Main risk: the current update-confirm schema is Bernie-named, so implementation must choose between a minimal compatible reuse and a neutral rename/additive alias. Recommendation: keep route behaviour stable and, if renaming, preserve backward-compatible schema fields/tests so G1 Bernie confirms do not regress. Second risk: edit modal currently combines appointment detail update and status PATCH; G2 should avoid accidentally dragging status semantics into signed update-confirm. Third risk: safe drag/resize may feel slower if proposal plus confirm are serialized; preserve optimistic/reload behaviour carefully while keeping backend confirmation authoritative. Finally, raw PUT compatibility can be misunderstood as a bypass; tests and closeout should state it is retained for authenticated staff/API compatibility, not for Diary UI confirm authority or agent/model writes.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
