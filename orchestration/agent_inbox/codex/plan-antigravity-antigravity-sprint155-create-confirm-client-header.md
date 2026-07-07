# plan-antigravity-antigravity-sprint155-create-confirm-client-header

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint155-create-confirm-client-header` |
| Status | pending_plan_review |
| Created | 2026-07-07 14:26 +1000 |
| Source HEAD | `9ffc9290` |

## Plan Summary

Implementation plan for EMR4 Sprint 155 to wire the HTTP `Idempotency-Key` header for create-confirm and confirm-Bernie client-side operations. This closes the key write-path gaps identified in Sprint 154 without modifying backend route logic, OpenAPI schemas, or database states.

## My Understanding

Based on the preflight analysis in [api_spine_appointment_idempotency_diary_header_gap_preflight.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md) and the current code in [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js):

1. **Staff Create-Confirm Gap**: When a staff member creates a booking in the modal, a proposal is requested (`POST /api/v1/appointments/proposals/create`). If warnings are triggered, the user clicks "Confirm & Save" which POSTs to the returned `confirm_endpoint` (typically `POST /api/v1/appointments/proposals/create/confirm`). Currently, the confirmation POST lacks the HTTP `Idempotency-Key` header.
2. **Bernie Create-Confirm Gap**: When Bernie stages an appointment and the user clicks "Confirm booking", the client POSTs to the `confirm_endpoint` (`POST /api/v1/appointments/proposals/create/confirm-bernie`). Currently, this call lacks the HTTP `Idempotency-Key` header.
3. **Scope and Limits**: Sprint 155 focuses strictly on the *creation confirmation* path for both staff and Bernie. Update-confirm, status-confirm, delete-confirm, and proposal-only routes remain deferred. No backend, database, or OpenAPI schema updates will be made.

## Intended Surface / Boundary

- **File**: [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js)
  - In `saveBooking()`, the create confirmation `apiFetch` block will be updated to include the `Idempotency-Key` header.
  - In `renderBernieReview()`, the click listener for `confirmBtn` will be updated to include the `Idempotency-Key` header in its `apiFetch` options.
  - In `resetProposalConfirmation()`, the new dataset confirmation key will be cleared.
- **File**: [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)
  - Replace the preflight `test_confirm_endpoint_lack_idempotency_header` with a positive test asserting the presence and stability of the header on `POST /api/v1/appointments/proposals/create/confirm`.
  - Add a Playwright smoke test verifying the presence and stability of the header on `POST /api/v1/appointments/proposals/create/confirm-bernie`.
- **File**: [test_api_spine_frontend_header_inventory.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_frontend_header_inventory.py)
  - Update static code blocks search to assert that the staff create-confirm block and the Bernie create-confirm block both contain `"Idempotency-Key"`, while the other confirm branches (update confirm, delete, status) do not.

## Out Of Scope

- Backend route handlers, DB transaction modifications, or OpenAPI parameters configuration.
- Wiring headers on update-confirm (`POST /proposals/update/confirm`), status-confirm, or delete-confirm routes.
- Enforcing `minLength: 8` validation on the backend.
- Modifying RAG, GraphRAG, providers, or H15/H-series runtime imports.

## Files I Expect To Edit

- [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)
- [test_api_spine_frontend_header_inventory.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_frontend_header_inventory.py)

---

## Responses to Focus Questions

### 1. Which exact create-confirm and confirm-Bernie call sites should receive headers?
1. **Staff Create-Confirm**: Inside `saveBooking()` (around lines 7571-7574 in [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js#L7571)), specifically in the `apiFetch(normalizeApiPath(confirmEndpoint), ...)` call for the create branch.
2. **Bernie Create-Confirm**: Inside `renderBernieReview()` (around lines 5169-5172 in [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js#L5169)), in the click handler for `#btn-bernie-confirm` when calling `apiFetch(normalizeApiPath(payload.confirm_endpoint), ...)`.

### 2. How should the key remain stable across retry/double-submit of the same staged confirmation?
- **Staff create-confirm**: 
  Instead of reusing the proposal-scoped key (to preserve clean API transaction separation), the client should lazily generate and store a dedicated confirmation key on the DOM element (`saveBtn.dataset.idempotencyKeyConfirm = generateClientIdempotencyKey();`) when the confirmation code is executed for the first time.
  Subsequent clicks (retries) will find the existing cached `idempotencyKeyConfirm` and reuse it.
  The key is deleted via `delete saveBtn.dataset.idempotencyKeyConfirm` in `resetProposalConfirmation()` when input fields are edited or the modal is closed/reset.
- **Bernie create-confirm**:
  Leverage the existing `BernieSession` instance. We can fetch or generate a cached key via `bernieSession.getServerRouteIdempotencyKey("create-confirm-bernie")`. This key will remain stable for the current turn/interpretation state and will automatically clear when the session is reset.

### 3. Which smoke/static tests best prove this without live backend calls?
- **Static**: [test_api_spine_frontend_header_inventory.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_frontend_header_inventory.py) will split its confirmation block checks. It will verify that the create-confirm blocks contain `"Idempotency-Key"` while update, status, and delete confirm blocks do not.
- **Smoke**: [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py) will assert that both the staff warning confirmation POST and the Bernie confirmation POST contain a valid `Idempotency-Key` header, and that retrying the confirm button POSTs the exact same key value.

### 4. What UI behavior should remain unchanged?
- The warning modal/alert presentation and warning flow styling.
- Disable/enable state transitions for save and confirm buttons during active fetch requests.
- All first-person wording and notices in the Bernie review/interpretation card.

---

## Risks / Ambiguities

- **Collision isolation**: Because proposal endpoints are non-mutating and confirmation endpoints are mutating, reusing the proposal key for confirmation is technically possible. However, generating a distinct stable confirm key ensures compliance with strict HTTP tracing guidelines and prevents any potential gateway caching side effects. We will proceed with generating separate confirm-scoped keys.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
