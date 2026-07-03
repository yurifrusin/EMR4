# plan-antigravity-antigravity-sprint-s1-confirm-evidence-ui-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-s1-confirm-evidence-ui-review` |
| Status | pending_plan_review |
| Created | 2026-07-03 21:41 +1000 |
| Source HEAD | `8659e7d` |

## Plan Summary

Establish a hardened UI boundary in `docs/diary/diary.js` that strictly echoes server-signed evidence and renders confirm-grade UI based on backend-owned `confirm_affordance` decisions, with no client-side authority over slot freshness.

## My Understanding

Sprint S1 focuses on hardening the Bernie booking proposal confirmation path. The backend `/proposals/create/confirm-bernie` endpoint implements a fail-closed staleness check when the client echoes the `candidate_freshness_id` and `proposal_freshness_id`. 
The UI must safely transport these signed evidence strings from the backend review payloads (returned from `/proposals/bernie/supervised-booking` after selection or during auto-preview) through to confirmation:
1. **No Client-Side Authority**: The UI must not decide if confirmation is allowed or if slot evidence is fresh. It must render confirmation ready controls if and only if the server returns `confirm_affordance.confirm_grade_allowed === true` (or the legacy alias `confirm_affordance.can_show_confirm_ui === true`).
2. **Fail-Closed Semantics**: If the `confirm_affordance` object is missing, malformed, or has `confirm_grade_allowed: false`, the UI must default to a blocked/inactive confirm state and suppress confirmation actions.
3. **Preserving State Integrity**: The client must cleanly clear all active proposal state (`stagedBookingPreview`, `selectedCandidateIndex`, and `turnRef`) when the input textarea (composer) is updated or suggestions clicked. This ensures stale session data is never re-used for subsequent booking attempts.

## Intended Surface / Boundary

- **Surface Affected**: 
  - The Bernie review content area (`#bernie-review-content`), status badge (`.bernie-status-badge`), confirmation ready details card (`.bernie-selected-slot-card`), and the "Confirm booking" button (`#btn-bernie-confirm`).
  - Active staged booking preview visual indicator in the diary column/roster grid.
- **Boundaries Preserved (Must NOT Change)**:
  - The main diary column grid layout, roster headers, and slot blocks.
  - The manual booking modal dialog (`#booking-modal`) and search workflows.
  - The backend endpoints and database schemas.

## Out Of Scope

- No implementation of production code during the plan-gate phase.
- No backend route, database schema, or audit-log changes.
- No visual or styling redesign of the taskpane.
- No GraphRAG/practice knowledge UI wiring.
- No client-side auto-confirmation (auto-mode) without explicit staff interaction.

## Files I Expect To Edit

- `docs/diary/diary.js`: Refine rendering logic, evidence echo path, fail-closed handling, and state clearing.
- `review/test_diary_smoke.py`: Add test scenarios to assert correct suppression of confirm UI under missing/malformed evidence.

## Implementation Steps

1. **Refine Gating in `docs/diary/diary.js`**:
   - Update `isBernieConfirmReady(payload)` to verify `confirm_affordance` is strictly valid and permits confirmation. If `confirm_affordance` is missing or has `confirm_grade_allowed` set to false, return `false`.
   - Update `enrichBernieConfirmPayload` to carry `candidate_freshness_id` and `proposal_freshness_id` directly from the server payload nested model without client-side mock fallback.
2. **State Clearing Verification**:
   - Verify `clearResponse` resets `turnRef`, `candidate_freshness_id`, and `proposal_freshness_id` to `null` to ensure absolute staleness protection.
   - Verify `chooseAnotherTime` resets the index and staged preview while setting `suppressAutoPreview = true`.
3. **Add Test Mock Scenarios**:
   - In `docs/diary/diary.js` mock data, add `confirmation_ready_missing_affordance` and `confirmation_ready_malformed` fixtures.
4. **Implement Smoke Tests**:
   - Add Playwright assertions in `review/test_diary_smoke.py` asserting that the confirm button is hidden and state transitions to `blocked` when `confirm_affordance` is missing or indicates confirmation is blocked.

## Visual / Behavioural Acceptance Checks

- **Verification checks**:
  - Run `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q` to verify all checks pass.
  - Run `node --check docs/diary/diary.js` to ensure syntax is valid.
  - Run `py scripts/check_frontend_versions.py` to assert version integrity.
- **Visual Checks**:
  - `?smoke=true&bernie_review=confirmation_ready` renders the confirm button and highlights the provisional booking card.
  - `?smoke=true&bernie_review=confirmation_ready_stale` suppresses the confirm button, renders the status badge as "Needs details", and lists the stale block reason.
  - `?smoke=true&bernie_review=confirmation_ready_missing_affordance` suppresses the confirm button and defaults to the blocked state.

## Risks / Ambiguities

- **Risk**: Interoperability with legacy backends that do not return `confirm_affordance`.
  - **Mitigation**: The backend Sprint S1 contract is fully updated to include this field, and the client will enforce it strictly in pilot mode. For safety, the client fail-closes if it is missing.
- **Risk**: Auto-preview triggering select-candidate requests in the background might lead to race conditions if the user rapidly types while an auto-preview is resolving.
  - **Mitigation**: Standard composer input clears the active session/response and sets `suppressAutoPreview = true`, preventing background resolving requests from overriding user inputs.


## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
