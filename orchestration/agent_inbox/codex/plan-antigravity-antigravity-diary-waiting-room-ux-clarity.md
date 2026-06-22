# plan-antigravity-antigravity-diary-waiting-room-ux-clarity

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-waiting-room-ux-clarity` |
| Status | pending_plan_review |
| Created | 2026-06-22 12:54 +1000 |
| Source HEAD | `e551706` |

## Plan Summary

Introduce collapsible sections, segmented area tabs, and compact card layouts for better Waiting Room scanability

## My Understanding

Receptionists need a cleaner, denser Waiting Room sidebar to scan active patient flows without horizontal wrapping clutter.

## Intended Surface / Boundary

Diary Waiting Room sidebar only

## Out Of Scope

Diary grid placement, taskpane, command centre, backend models/routes

## Files I Expect To Edit

docs/diary/diary.html docs/diary/diary.css docs/diary/diary.js

## Implementation Steps

1. Style area tabs as segmented controls. 2. Implement collapsible section headers. 3. Adjust card padding and hover opacity. 4. Wire collapse persistence.

## Visual / Behavioural Acceptance Checks

Section header clicks toggle expand/collapse; tabs align in one row; card actions fade in on hover; all states persist.

## Risks / Ambiguities

None, frontend-only changes with local state persistence

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
