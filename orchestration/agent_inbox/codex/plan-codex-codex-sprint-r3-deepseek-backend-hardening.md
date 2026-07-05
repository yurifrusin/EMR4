# plan-codex-codex-sprint-r3-deepseek-backend-hardening

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-r3-deepseek-backend-hardening` |
| Source Task | `codex-sprint-r3-deepseek-backend-hardening` |
| Status | pending_plan_review |
| Created | 2026-07-05 15:10 +1000 |
| Source HEAD | `c0c37a8` |

## Plan Summary

Shen-2 DeepSeek backend review finds no production code change needed; existing stale session/revision guards appear fail-closed.

## My Understanding

R3 asks for fail-closed stale Bernie session/revision handling while Claude quota is unavailable. Shen-2 reviewed the store, route, and confirm seams and found existing guards already cover stale/future revision rejection, HTTP 409 route rejection, stale_reason_code, and check_staleness candidate/proposal freshness handling.

## Intended Surface / Boundary

Backend review/proof lane only: app/services/bernie/session_store.py, app/routers/appointments.py confirm/session seams, app/services/bernie_turn_evidence.py, and existing session/confirm tests. No visible UI surface changes.

## Out Of Scope

Production edits unless a real gap is proven, Diary UI/taskpane/Word changes, Antigravity fixtures/docs, global model/config switching, master/handoff movement by worker.

## Files I Expect To Edit

No production files expected. Optional follow-up would add 2-3 focused tests to tests/test_bernie_confirm_create_proposal.py or tests/test_bernie_session_store.py if Ariadne wants extra proof.

## Implementation Steps

1. Accept no-code-needed if Ariadne verification confirms existing guards. 2. Otherwise add minimal focused tests only. 3. Ariadne runs the relevant focused pytest because DeepSeek sandbox lacks Python on PATH.

## Visual / Behavioural Acceptance Checks

Existing fail-closed stale guards are confirmed by source and focused tests; no stale session/revision path can merge, confirm, or write appointment/audit rows without current coordinates.

## Risks / Ambiguities

Evidence is review-based until Ariadne reruns focused tests. Additional confirm-endpoint stale freshness tests may still be valuable, but no production gap is apparent.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
