# plan-antigravity-antigravity-sprint-k1-advisory-retrieval-ux-boundary

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-k1-advisory-retrieval-ux-boundary` |
| Status | accepted |
| Created | 2026-07-03 21:04 +1000 |
| Source HEAD | `416fcc5` |

## Plan Summary

Plan Sprint K1 Diary/Bernie UI review for consuming advisory practice knowledge without making it look like deterministic diary truth.

## My Understanding

Ensure retrieved practice facts (opening hours, policies) are displayed strictly as advisory guidance, visually distinct from deterministic roster/availability status and confirmation gates, preserving the backend's confirm-affordance gate as the sole authority.

## Intended Surface / Boundary

Affected surface: Bernie Review sidebar in docs/diary/diary.js and docs/diary/diary.css. Nearby surfaces (diary grid, booking slots, waiting room) will not be affected.

## Out Of Scope

No implementation of production code before approval, no backend schema/logic changes, no slot search modifications, no write paths, no persisted session DB tables.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.css, docs/diary/diary.html, review/test_diary_smoke.py

## Implementation Steps

1. Add neutral advisory-specific CSS classes in diary.css. 2. Implement parsing and rendering of knowledge/advisory context frames in diary.js, with distinct labeling and provenance display. 3. Enforce confirm-gate authority so advisory facts do not block confirmation unless explicitly instructed by the backend. 4. Write Playwright smoke tests in test_diary_smoke.py for rendering, confirm-gate non-interference, and deterministic schedule explanation preservation.

## Visual / Behavioural Acceptance Checks

Advisory facts render neutrally with provenance, do not block confirmation when allowed by backend, and do not override deterministic schedule explanations when slot search fails.

## Risks / Ambiguities

Defensively support both generic frame types and specialized payload fields to prevent mismatch with Claude's backend implementation.

## Codex Plan Review

- Review result: Accepted as a future UI consumption lane, not released for K1
  implementation yet.
- Required changes before implementation: do not add UI rendering until backend
  route/session wiring exposes a typed advisory envelope. When that later
  happens, the UI must label retrieved practice facts as advisory guidance and
  must not let them override schedule explanations, no-slot authority, or
  confirm-affordance state.
- Approved to proceed: no for this K1 implementation slice; defer until route
  wiring exists.
