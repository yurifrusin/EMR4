# plan-antigravity-antigravity-bernie-supervised-review-live-adapter

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-bernie-supervised-review-live-adapter` |
| Status | integrated |
| Created | 2026-06-27 03:16 +1000 |
| Source HEAD | `97d7a33` |

## Plan Summary

Connect the diary Bernie review panel to the backend supervised-booking staff_review response behind an explicit feature/smoke gate, without posting confirmation or writing appointments.

## My Understanding

Connect the existing Bernie Supervised Booking Review panel in the diary UI to the backend endpoint /api/v1/appointments/proposals/bernie/supervised-booking when activated via a specific feature/smoke gate parameter. In this sprint, write paths must NOT be called; clicking confirmation should remain simulated.

## Intended Surface / Boundary

The Bernie review sidebar panel (#bernie-review-panel) inside the diary taskpane. Nearby surfaces like the diary grid, booking slots, cards, and modal windows must remain unchanged.

## Out Of Scope

Backend implementation (schemas, routes, database, or migrations); actual confirm-bernie booking confirmations or database writes; LLM or provider integration; taskpane search panel or other booking workflows; enabling the live adapter mode by default.

## Files I Expect To Edit

docs/diary/diary.js; review/test_diary_smoke.py

## Implementation Steps

1. In docs/diary/diary.js, update initBernieReview() to handle bernie_review=live. If active, call the backend /api/v1/appointments/proposals/bernie/supervised-booking with a deterministic input payload. 2. Handle the backend response by rendering the staff_review payload. 3. Ensure the confirm button remains simulated with no write path. 4. In review/test_diary_smoke.py, add deterministic Playwright tests that intercept the endpoint and assert proper rendering.

## Visual / Behavioural Acceptance Checks

Navigating with bernie_review=live performs a POST request; correct rendering of blocked, selection, and confirmation states; checking the box enables confirm button; clicking confirm simulates success without backend call.

## Risks / Ambiguities

Backend requires auth, solved by intercepting network calls in Playwright tests.

## Codex Plan Review

- Review result: Accepted by Ariadne. The plan was narrowly scoped to a smoke/feature-gated adapter, preserved all write boundaries, and used route-intercepted deterministic checks.
- Required changes before implementation: None.
- Approved to proceed: yes; implementation was released via Antigravity CLI with the exact phrase `complete sprint task`.
