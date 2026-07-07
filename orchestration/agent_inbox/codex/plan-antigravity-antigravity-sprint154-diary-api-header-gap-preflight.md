# plan-antigravity-antigravity-sprint154-diary-api-header-gap-preflight

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint154-diary-api-header-gap-preflight` |
| Status | pending_plan_review |
| Created | 2026-07-07 14:15 +1000 |
| Source HEAD | `9d7f9bd` |

## Plan Summary

Preflight review mapping client-side gaps for EMR4 appointment command plane HTTP `Idempotency-Key` header emission, detailing the safest Sprint 155 implementation slice, and adding UI smoke tests to document the gap.

## My Understanding

Based on the inspection of [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js), [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py), [appointments.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/app/routers/appointments.py), and [appointment-commands.yaml](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/api-spine/openapi/appointment-commands.yaml):

1. **Frontend Call Coverage**:
   - Only `POST /api/v1/appointments/proposals/create` currently emits the client-generated HTTP `Idempotency-Key` header (added in Sprint 153).
   - All other mutating/proposal endpoints lack client-side header emission today.
2. **Expansion Rejection Risks**:
   - If backend idempotency checks are enforced for confirm routes before the client is updated, **all staff confirmation writes will fail**.
   - The backend `/proposals/create/confirm` and sibling confirm routes already require the header at runtime via `claim_appointment_command()`. The client currently succeeds only because enforcement is deferred, or they bypass header checks.
   - Non-mutating proposal routes (`/proposals/update/{id}`, `/proposals/status/{id}`, etc.) do not yet enforce the header at runtime, but are documented as requiring it in OpenAPI.
3. **Sprint 155 Implementation Recommendation**:
   - Target **Create-Confirm and Bernie Confirm** (`POST /proposals/create/confirm` and `POST /proposals/create/confirm-bernie`) header emission as the safest Sprint 155 slice.
   - This protects the critical mutating write path first, rather than expanding non-mutating proposal bindings.
4. **Sprint 154 Test Inventory**:
   - Added `test_confirm_endpoint_lack_idempotency_header` to [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py) to assert that the client currently fails to emit the `Idempotency-Key` header on create-confirm POST requests.

## Intended Surface / Boundary

- File: [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)
  - Appended `test_confirm_endpoint_lack_idempotency_header` to mock the warning-to-confirm transition and assert the missing header.
- File: [plan-antigravity-antigravity-sprint154-diary-api-header-gap-preflight.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/agent_inbox/codex/plan-antigravity-antigravity-sprint154-diary-api-header-gap-preflight.md) (This plan/review artifact).

## Out Of Scope

- Modifying `docs/diary/diary.js` runtime code (defer to Sprint 155).
- Modifying `app/routers/appointments.py` (defer to Sprint 155).
- Modifying database structures, FGA policies, GraphQL mutations, live provider interfaces, or historical trove parser logic.

## Files I Expect To Edit

- [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py) (already completed in Sprint 154).
- [plan-antigravity-antigravity-sprint154-diary-api-header-gap-preflight.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/agent_inbox/codex/plan-antigravity-antigravity-sprint154-diary-api-header-gap-preflight.md) (This file).

## Responses to Focus Questions

### 1. Which frontend calls are now covered by HTTP `Idempotency-Key` emission?
Only `POST /api/v1/appointments/proposals/create` (when `!editingAppointmentId` is true).

### 2. Which confirm/proposal/status/delete calls are likely to fail or drift if backend idempotency enforcement expands before the client is ready?
The following calls will fail because the client does not send the `Idempotency-Key` header:
- **Confirmations**: `/proposals/create/confirm`, `/proposals/update/confirm`, `/proposals/status-confirm`, `/proposals/delete-confirm`, and `/proposals/create/confirm-bernie`.
- **Proposals**: `/proposals/update/{appointment_id}`, `/proposals/status/{appointment_id}`, `/proposals/waiting-area/{appointment_id}`, and `/proposals/delete/{appointment_id}`.

### 3. Should Sprint 155 target create-confirm/confirm-Bernie/status/delete confirm header emission, or the next proposal-only backend binding?
Sprint 155 should target **create-confirm and Bernie confirm** header emission. Confirm routes are mutating writes, so they are the highest-leverage path for idempotency protection. Proposal-only bindings (which are non-mutating) should be deferred until the client is fully aligned.

### 4. What UI smoke/static tests should Sprint 154 add before implementation?
Sprint 154 has added `test_confirm_endpoint_lack_idempotency_header` to [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py), which sets up a warn-then-confirm workflow and verifies that the `POST` to `confirm_endpoint` does not carry the `Idempotency-Key` header yet.

## Visual / Behavioural Acceptance Checks

- Run `.venv\Scripts\pytest review/test_diary_smoke.py -k test_confirm_endpoint_lack_idempotency_header` to verify the preflight gap test passes.

## Risks / Ambiguities

- **Key Generation Strategy**: In Sprint 155, when adding confirmation headers, the client should generate a *new* unique key for each confirmation submit attempt rather than reusing the proposal key. This guards against duplicate clicks on the "Confirm & Save" button itself.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
