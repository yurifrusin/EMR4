# plan-codex-codex-sprint-g1-update-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-g1-update-confirm-invariants` |
| Status | integrated |
| Created | 2026-07-04 06:36 +1000 |
| Source HEAD | `5eb771b` |

## Plan Summary

Adversarial invariant plan for unified appointment update confirmation grammar

## My Understanding

Sprint G1 should make appointment updates converge on one deterministic proposal/confirm/write grammar for both human Diary UI updates and Bernie-authored update proposals. The core invariant is that a write cannot be confirmed from model text, staff prose, browser state, or a copied command alone: confirmation must be backed by current backend proposal evidence, explicit staff confirmation, tenant/practice scoped appointment state, and an auditable write path. My role in this packet is planning the adversarial invariant/test lane only; no production code until explicit approval.

## Intended Surface / Boundary

Primary surface: backend appointment update proposal and confirmed update contract, including Bernie tool-intent update proposals and audit evidence. Test surface: focused pytest coverage around update proposals, Bernie tool-intent proposals, stale/tampered/mismatched evidence, raw PUT compatibility boundaries, and audit rows. UI surface only if implementation changes the visible Diary confirm affordance: the Ask Bernie appointment-change proposal card and its Confirm change button. Nearby surfaces that must not change: diary grid geometry, booking slot search, waiting room panels/cards, status controls, create-booking flow, cancellation/delete flow, taskpane, Command Centre, GraphRAG/practice knowledge, and persisted Bernie session storage.

## Out Of Scope

No production code during planning. No persisted session tables, GraphRAG, auto-mode, broad API rewrite, booking-slot search rewrite, diary grid/stacking/card layout redesign, waiting-room changes, status mutation grammar, cancellation grammar, taskpane/Command Centre, or live PHI handling. Raw existing update APIs should not be broken abruptly; compatibility must be explicit and bounded if the implementation touches them.

## Files I Expect To Edit

Expected later implementation files: tests/test_appointment_update_proposal.py for proposal/evidence/freshness/adversarial update cases; tests/test_bernie_tool_intent.py for Bernie-authored update proposal authority boundaries; tests/test_appointment_audit.py and/or tests/test_appointment_audit_warning_summary.py for confirmed update audit rows and evidence-code persistence; tests/test_diary_confirm_gate.py if shared confirm gating is extended to update proposals; app/schemas/appointments.py and app/routers/appointments.py only if a typed update-confirm payload/evidence contract is added; app/services/bernie_turn_evidence.py or app/services/bernie/evidence.py only if signing/freshness helpers are generalized from create-confirm evidence to update-confirm evidence; review/test_diary_smoke.py and docs/diary/diary.js only if the visible Confirm change affordance needs to echo/submit the new backend evidence. No docs/diary CSS/layout edits expected unless UI implementation actually changes rendered controls.

## Implementation Steps

1. Inventory the existing update path: /appointments/proposals/update/{id}, Bernie /appointments/proposals/bernie/tool-intent, raw PUT /appointments/{id}, audit row creation, and current Diary Confirm change submission. Record which fields are currently backend-authored versus browser/model/staff-authored.
2. Define the minimum unified update-confirm grammar: proposal command plus backend evidence envelope, evidence purpose/action=update_appointment, appointment id, practice id, current appointment state fingerprint or freshness id, proposed patch, warning/block codes, expiry or freshness binding, and explicit staff confirmation fields.
3. Add fail-closed adversarial tests before or with implementation: missing evidence, malformed evidence, wrong purpose, tampered signature, stale/current-state mismatch after appointment changed, command/proposal mismatch, appointment-id mismatch, practice/tenant mismatch, warning list mismatch where audit must preserve accepted warnings, and replay against a different appointment/date/practitioner/duration.
4. Add no-bypass tests: model/staff text that says â€œconfirmedâ€, frontend-supplied safe=true, copied proposal.command without evidence, or arbitrary confirmed_warnings/audit_evidence cannot create confirmation authority. Bernie tool-intent remains non-mutating and must not return confirm-grade evidence unless the new update-confirm contract explicitly prepares it server-side.
5. Preserve raw update compatibility deliberately: either keep PUT as the staff/manual write boundary with existing RBAC/audit and prove it does not accept model/proposal authority fields, or introduce an evidence-gated confirm endpoint while documenting/tests proving legacy raw PUT is not a Bernie/model bypass. Do not silently weaken conflict, terminal-status, break, provisional-patient, or tenancy checks.
6. Add staff-confirmation/audit tests: successful confirmed update writes exactly one update audit row, confirmed_by_user_id is the authenticated staff user, practice_id is scoped, bounded evidence codes are code-only/no PHI, warnings accepted by staff are persisted, blocked/tampered/stale proposals write no appointment and no misleading audit row.
7. If Diary UI changes, gate Confirm change on backend-owned confirm affordance/evidence, not on visible copy; clear stale proposal state after a new Bernie turn/date/appointment-context change; assert with review/test_diary_smoke.py that clarification/blocked/stale/tampered fixtures show no Confirm change.
8. Run focused backend tests first, then py_compile for touched backend files, node --check and deterministic Diary smoke only if docs/diary is touched, scripts/check_frontend_versions.py only if assets change, and git diff --check.

## Visual / Behavioural Acceptance Checks

Acceptance checks: proposal endpoints remain non-mutating; update confirmation cannot succeed without current backend proposal evidence unless the path is the explicitly bounded raw staff PUT; tampered/stale/mismatched/cross-practice/replayed evidence fails closed without appointment mutation; Bernie tool-intent cannot mutate and cannot bootstrap confirm authority from language alone; staff confirmation is explicit and tied to the authenticated user; successful writes create one scoped audit row with bounded code-only evidence/warnings; blocked proposals and failed confirms create no misleading audit rows; any visible Diary Confirm change button appears only for backend-confirmable update evidence and disappears for clarification, blocked, stale, or text-only states. Visual checks, if needed, are limited to the Ask Bernie appointment-change proposal card/button; diary grid appointment cards, booking slots, waiting room panels, and status controls should look and behave unchanged.

## Risks / Ambiguities

Main ambiguity: whether G1 should add a new update-confirm endpoint/evidence envelope or harden the existing raw PUT as the staff-confirmed write boundary while keeping Bernie proposals evidence-gated only at the UI/review layer. Recommendation: prefer a native update-confirm payload if Ariadne wants true unification; otherwise explicitly document raw PUT as human-staff compatibility and prove Bernie/model text cannot reach it as confirmation authority. Watch for overfitting to extension-only Bernie tool intent; the grammar should be update-shaped enough for move/resize/duration changes without accidentally taking on status/cancel/create semantics. Also watch test fragility around clock/freshness expiry; use deterministic freshness ids/state fingerprints where possible.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
