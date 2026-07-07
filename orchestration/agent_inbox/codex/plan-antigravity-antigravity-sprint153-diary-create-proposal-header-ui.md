# plan-antigravity-antigravity-sprint153-diary-create-proposal-header-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint153-diary-create-proposal-header-ui` |
| Status | pending_plan_review |
| Created | 2026-07-07 13:53 +1000 |
| Source HEAD | `82ae0106` |

## Plan Summary

Tangible plan for adding Idempotency-Key header to diary create-proposal client path

## My Understanding

- Currently, the diary client code in [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js) sends `POST` requests to `/appointments/proposals/create` without passing an `Idempotency-Key` header.
- The backend has a split-contract posture: it enforces `non-blank-only` at runtime but documents `minLength: 8` in OpenAPI. The backend currently rejects missing/blank keys with `400 Bad Request` (`idempotency_key_required`).
- In Sprint 153, the client must be updated to pass a valid `Idempotency-Key` header with length >= 8 characters.
- The key must be stable/reused for retries of the *same* payload (e.g., when confirming after warnings or after transient failures) but reset when the user changes form inputs (which mutates the proposal payload).

## Intended Surface / Boundary

- File: [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js)
  - `saveBooking()`: In create mode, retrieve or generate a unique client-side idempotency key, store it on the Save button's dataset, and pass it in the `headers` option to `apiFetch`.
  - `resetProposalConfirmation()`: Clear the saved key from the Save button's dataset when form fields are modified.
- File: [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)
  - Assert that mock endpoints capturing `/appointments/proposals/create` receive the `Idempotency-Key` header and that it meets the `minLength: 8` requirement.

## Out Of Scope

- Any changes to backend routes/validators (`app/`).
- OpenAPI schema modifications.
- Adding idempotency headers to update/status/delete proposal endpoints (deferred for future sprints).
- Any modifications to the database models, providers, RAG/GraphRAG, or clinical memory.
- Modifying the taskpane UI.

## Files I Expect To Edit

- [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)

## Implementation Steps

1. **Client-side UUID Helper**:
   - Utilize a robust generator for the client-side key. We can define `generateClientIdempotencyKey()` returning a string (using `crypto.randomUUID()` when available, or a fallback string starting with `evt-` that meets the 8-character minimum).
2. **Bind Key to Modal lifecycle and input changes**:
   - In `saveBooking()`, if it is a new proposal (`!editingAppointmentId`), check if `saveBtn.dataset.idempotencyKey` already exists.
   - If not, generate a new key and assign it: `saveBtn.dataset.idempotencyKey = generateClientIdempotencyKey();`.
   - Pass this key in the fetch options:
     ```javascript
     const propRes = await apiFetch(url, {
       method: "POST",
       headers: {
         "Idempotency-Key": saveBtn.dataset.idempotencyKey
       },
       body: JSON.stringify(payload)
     });
     ```
3. **Reset on change**:
   - Update `resetProposalConfirmation()` to delete the dataset attribute:
     ```javascript
     delete saveBtn.dataset.idempotencyKey;
     ```
   - This ensures a fresh key is generated if the user changes any field (date, time, practitioner, duration, reason, patient, etc.) before saving again.
4. **Smoke Test Updates**:
   - Enhance the mock handlers for `/appointments/proposals/create` in [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py) to assert:
     - The `Idempotency-Key` header is present in the request headers (checked in case-insensitive fashion).
     - The header value is at least 8 characters long.

## Visual / Behavioural Acceptance Checks

- Run `node --check docs/diary/diary.js` to ensure syntactical correctness.
- Run `pytest review/test_diary_smoke.py` to verify that Playwright-routed smoke tests pass with the new header verification.
- Verify in network inspection that proposal create requests contain the `Idempotency-Key` header.
- No changes to visual layout, styling, panels, or grid structures.

## Risks / Ambiguities

- None. The key generation reuse pattern exactly matches the backend's expectations and preserves idempotency during confirmation warnings and retries.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
