# plan-antigravity-antigravity-sprint109-live-smoke-ux-readiness

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint109-live-smoke-ux-readiness` |
| Status | integrated |
| Created | 2026-07-07 00:24 +1000 |
| Source HEAD | `f5e16705` |

## Plan Summary

Sprint 109 live-smoke UX readiness plan/review

## My Understanding

Assessment of staff-visible UX and acceptance implications for a future no-write live-provider smoke test, without enabling live providers or changing runtime behavior.

## Intended Surface / Boundary

Proposed additions to the Bernie Review Panel (docs/diary/diary.js, docs/diary/diary.html) for debug labels, warnings, and Playwright tests in review/test_diary_smoke.py.

## Out Of Scope

No runtime code modifications, no provider enablement, no live external calls, no backend changes, no database writes, no H15/trove or memory/RAG/GraphRAG.

## Files I Expect To Edit

docs/diary/diary.js, review/test_diary_smoke.py, and closeout docs (as proposals/plans only).

## Implementation Steps

1. Analyze current Sprint 108 debug labels in docs/diary/diary.js. 2. Propose copy and visual warnings for live-provider smoke tests. 3. Design Playwright test coverage for visual warnings and no-write enforcement. 4. Document findings and proposals in the plan/review packet.

## Visual / Behavioural Acceptance Checks

Verification that the plan/review packet is complete, maintains a strict no-write posture, and separates UX acceptance from gate approval.

## Risks / Ambiguities

Distinguishing fake/mocked provider flows from live-provider smoke tests in the UI without confusing staff; ensuring the gate remains strictly closed until approved.

## Codex Plan Review

- Review result: accepted for UX/staff-copy criteria and synthesized into
  `docs/bernie-band2-provider-gate-criteria.md`.
- Required changes before implementation: no UI implementation in Sprint 109.
- Approved to proceed: no separate Antigravity implementation required.
