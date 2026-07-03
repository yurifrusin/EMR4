# plan-antigravity-antigravity-sprint106c-bernie-reception-ux-plan

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint106c-bernie-reception-ux-plan` |
| Status | integrated |
| Created | 2026-07-03 13:14 +1000 |
| Source HEAD | `61014e1` |

## Plan Summary

Sprint 106C Bernie reception UX plan

## My Understanding

Plan frontend/backend UX implications of typed context frames to prevent false no-slots, stale warnings, and false duplicate blocks.

## Intended Surface / Boundary

Bernie Panel UI (diary.js), Roster & Context Services (appointments.py, bernie_patient_context.py)

## Out Of Scope

Production code edits, DB schema tables/migrations, autonomous booking, XState

## Files I Expect To Edit

docs/diary/diary.js, app/routers/appointments.py, app/services/bernie_patient_context.py, tests/test_bernie_patient_context.py

## Implementation Steps

1. Format visible date/appointment frames in diary.js. 2. Exclude source_appointment_id from follow-up warning. 3. Pass patient name to backend warning message. 4. Clamp only on actual local calendar today. 5. Keep chat transcript clean on date navigations.

## Visual / Behavioural Acceptance Checks

Interpret call works without 422 errors; duplicate warning shows patient first name; moving same-day appointment does not trigger duplicate warning; navigations clear stale proposal cards but keep chat history.

## Risks / Ambiguities

Late-night timezone browser/server calendar day mismatches; correct parent turn IDs for suggestion clicks.

## Codex Plan Review

- Review result: Accepted with Ariadne amendments. The plan correctly identifies the affected Diary surfaces: Bernie transcript/composer, stale proposal/candidate clearing, warning rendering, and date/time boundary risks. It also correctly says the diary grid, booking modal, waiting room, taskpane, persisted sessions, autonomous booking, and broad redesign stay out of scope.
- Required changes before implementation: Treat the listed bug fixes as examples, not the whole Sprint 106C product shape. Implementation must follow the backend typed-context-frame contract once accepted: UI should render typed frame categories and reason codes rather than inventing special-case copy branches. Future-appointment warnings must be advisory-only unless a deterministic guardrail says otherwise. No "no matching times" message may render unless a valid slot search actually ran and returned zero usable candidates. Do not hardcode patient names or one-off Margaret/Billy cases.
- Approved to proceed: yes, after the backend context-frame contract plan is accepted and Ariadne releases implementation.
