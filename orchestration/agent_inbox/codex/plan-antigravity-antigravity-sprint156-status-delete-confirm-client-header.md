# plan-antigravity-antigravity-sprint156-status-delete-confirm-client-header

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint156-status-delete-confirm-client-header` |
| Status | pending_plan_review |
| Created | 2026-07-07 14:42 +1000 |
| Source HEAD | `dfbd507e` |

## Plan Summary

Implementation plan for EMR4 Sprint 156 to wire the HTTP `Idempotency-Key` header for status-confirm and delete-confirm client-side operations. This extends the pattern established in Sprint 155 (which wired create-confirm client headers) to the dedicated status and delete confirmation helpers without modifying backend route logic, OpenAPI schemas, or database states.

## My Understanding

Based on the preflight analysis in [api_spine_appointment_idempotency_diary_header_gap_preflight.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/api_spine_appointment_idempotency_diary_header_gap_preflight.md) and the current code in [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js):

1. **Staff Status-Confirm Gap**: When a status change triggers warnings or terminal checks, the client displays a confirmation dialog. Upon clicking "Confirm & Save", it POSTs to the `confirm_endpoint` (typically `POST /api/v1/appointments/proposals/status-confirm`) in `applySignedStatusProposal()`. This call currently lacks the HTTP `Idempotency-Key` header.
2. **Staff Delete-Confirm Gap**: When cancelling an appointment, the client shows a confirmation dialog. Upon approval, it POSTs to the `confirm_endpoint` (typically `POST /api/v1/appointments/proposals/delete-confirm`) in `applySignedDeleteProposal()`. This call currently lacks the HTTP `Idempotency-Key` header.
3. **Scope and Limits**: Sprint 156 focuses strictly on status-confirm and delete-confirm paths. Update-confirm, proposal-only routes, raw compatibility writes, backend routes, database states, and OpenAPI schemas remain unchanged.

## Intended Surface / Boundary

- **File**: [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js)
  - Define `ensureProposalConfirmIdempotencyKey(proposal)` to lazily generate and store a cached client idempotency key directly on the `proposal` object (`proposal._confirmIdempotencyKey`).
  - Update `applySignedStatusProposal()` to retrieve this key and pass it under the `headers` option of `apiFetch()`.
  - Update `applySignedDeleteProposal()` to retrieve this key and pass it under the `headers` option of `apiFetch()`.
  - Define `isStatusConfirmEndpoint(endpoint)` and `isDeleteConfirmEndpoint(endpoint)` to mirror `isCreateConfirmEndpoint(endpoint)`.
- **File**: [test_api_spine_frontend_header_inventory.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_frontend_header_inventory.py)
  - Remove `applySignedStatusProposal` and `applySignedDeleteProposal` from `test_frontend_remaining_confirm_callers_are_explicitly_tracked_as_missing_headers()`.
  - Create a new static test `test_frontend_status_and_delete_confirm_emit_http_idempotency_headers()` validating that both `applySignedStatusProposal` and `applySignedDeleteProposal` contain `"Idempotency-Key"`.
- **File**: [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)
  - Add integration tests intercepting `POST /appointments/proposals/status-confirm` and `POST /appointments/proposals/delete-confirm` to verify the header is present and remains stable for retries of the same proposal.

## Out Of Scope

- Backend route handlers, DB transaction modifications, or OpenAPI parameters configuration.
- Wiring headers on update-confirm (`POST /proposals/update/confirm`) or Bernie tool-intent confirmation routes.
- Enforcing `minLength: 8` validation on the backend.
- Modifying RAG, GraphRAG, providers, or H15/H-series runtime imports.

## Files I Expect To Edit

- [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)
- [test_api_spine_frontend_header_inventory.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_frontend_header_inventory.py)

---

## Responses to Focus Questions

### 1. Which exact status/delete confirm call sites should receive headers?
1. **Status Confirm**: Inside `applySignedStatusProposal()` (around line 8121 in [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js#L8121)), specifically in the `apiFetch(normalizeApiPath(confirmEndpoint), ...)` call.
2. **Delete Confirm**: Inside `applySignedDeleteProposal()` (around line 8165 in [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js#L8165)), specifically in the `apiFetch(normalizeApiPath(confirmEndpoint), ...)` call.

### 2. How should keys remain stable for the same proposal object?
- Because the `proposal` object returned by the proposal endpoints is passed directly as an argument to the confirmation functions, the client should lazily generate and attach a confirmation key directly on the `proposal` object (e.g. `proposal._confirmIdempotencyKey = generateClientIdempotencyKey();`) on the first confirmation fetch attempt.
- Subsequent retries of the same confirmation action using the same `proposal` object will find and reuse `proposal._confirmIdempotencyKey`.

### 3. Which route-intercepted/static tests should prove the behavior?
- **Static**: [test_api_spine_frontend_header_inventory.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_frontend_header_inventory.py) will verify that both `applySignedStatusProposal` and `applySignedDeleteProposal` blocks contain `"Idempotency-Key"`, while update-confirm still does not.
- **Smoke**: [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py) will assert that both status warning confirmation POSTs and delete warning confirmation POSTs contain a valid `Idempotency-Key` header, and that retrying/double-submitting the confirm action transmits the identical key.

### 4. What UI behavior should stay unchanged?
- The warning dialog presentation, styling, and backdrop.
- Disable/enable state transitions for action buttons during active fetch requests.
- All first-person wording and notices in the Bernie review/interpretation card.

---

## Risks / Ambiguities

- **Lifetime of Proposal Objects**: In the staff flow, if an action fails and the user must start the action again (e.g. re-selecting a status in the dropdown), a new proposal object is fetched from the server. This will correctly result in a fresh `_confirmIdempotencyKey` being generated, which conforms with standard transaction boundary definitions (different user action = different transaction). If the user retries within the same dialog confirmation lifecycle, the key is preserved.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
