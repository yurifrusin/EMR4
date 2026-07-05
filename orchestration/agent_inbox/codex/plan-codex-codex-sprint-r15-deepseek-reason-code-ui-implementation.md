# plan-codex-codex-sprint-r15-deepseek-reason-code-ui-implementation

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-r15-deepseek-reason-code-ui-implementation` |
| Source Task | `codex-sprint-r15-deepseek-reason-code-ui-implementation` |
| Status | integrated |
| Created | 2026-07-05 20:25 +1000 |
| Source HEAD | `57d834d` |

## Plan Summary

Remove `PATIENT_UNWELL` from first-party selectable reason-code options, add context-aware future-vs-retrospective option filtering, and preserve display compatibility for stored legacy values.

## My Understanding

The Diary reason-code dropdown was statically rendered in `docs/diary/diary.html`, while `STATUS_REASON_CODE_LABELS` in `docs/diary/diary.js` is also used to render stored reason codes on flow cards. Sprint R11/R12 guidance says `PATIENT_UNWELL` is a clinical-privacy risk and should not be selectable by receptionists, but existing stored values still need to display safely.

## Intended Surface / Boundary

First-party Diary booking modal reason-code dropdown only. Preserve flow-card display, backend payload field names, audit display, cancellation note handling, Diary grid geometry, waiting room, Bernie panel, and backend routes.

## Out Of Scope

No backend schema, migration, validation, route, or API compatibility change. No removal of `PATIENT_UNWELL` from `STATUS_REASON_CODE_LABELS`.

## Files I Expect To Edit

`docs/diary/diary.html`, `docs/diary/diary.js`, and `review/test_diary_smoke.py`.

## Implementation Steps

1. Remove `PATIENT_UNWELL`, `DID_NOT_ATTEND`, and `LEFT_WITHOUT_SEEN` from static dropdown markup.
2. Add first-party and retrospective option arrays in `diary.js`, excluding `PATIENT_UNWELL`.
3. Populate the dropdown dynamically when terminal status changes.
4. Use appointment date/time to choose future vs retrospective context.
5. Preserve `STATUS_REASON_CODE_LABELS` for stored legacy display.
6. Add deterministic smoke coverage for future and retrospective option sets.

## Visual / Behavioural Acceptance Checks

- Future cancellation dropdown has an empty default and excludes `PATIENT_UNWELL`, `DID_NOT_ATTEND`, and `LEFT_WITHOUT_SEEN`.
- Retrospective terminal-status dropdown prioritizes `DID_NOT_ATTEND` and `LEFT_WITHOUT_SEEN`.
- Stored `PATIENT_UNWELL` can still be labelled by `statusReasonCodeLabel`.
- Reason-code payload threading and mandatory-selection validation remain unchanged.

## Risks / Ambiguities

DeepSeek's first implementation attempt produced useful structure but corrupted file encoding. Ariadne discarded the worker diff and reimplemented the approved plan surgically in the integration worktree.

## Codex Plan Review

- Review result: Accepted with future-vs-retrospective correction.
- Required changes before implementation: Do not remove `PATIENT_UNWELL` from stored-value label resolver; do not make backend changes.
- Approved to proceed: yes
