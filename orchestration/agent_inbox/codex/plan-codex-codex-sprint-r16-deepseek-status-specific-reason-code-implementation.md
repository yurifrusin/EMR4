# plan-codex-codex-sprint-r16-deepseek-status-specific-reason-code-implementation

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-r16-deepseek-status-specific-reason-code-implementation` |
| Source Task | `codex-sprint-r16-deepseek-status-specific-reason-code-implementation` |
| Status | integrated |
| Created | 2026-07-05 20:39 +1000 |
| Source HEAD | `e432c3b` |

## Plan Summary

Implement status-specific reason-code filtering for first-party Diary terminal statuses.

## My Understanding

Sprint R15 filtered reason-code options by future-vs-retrospective context. Sprint R16 narrows the UI by selected terminal status: `Cancelled`, `DNA`, and `NoShow`. `PATIENT_UNWELL` remains display-only via `STATUS_REASON_CODE_LABELS`.

## Intended Surface / Boundary

The booking modal's `#booking-status-reason-code` dropdown only. Nearby surfaces that must not change: Diary grid, waiting room flow cards, Bernie panels, audit history, backend payload shape, and cancellation note handling.

## Out Of Scope

No backend, schema, migration, audit model, stored-value label, or inline status-control changes.

## Files I Expect To Edit

`docs/diary/diary.js`, `docs/diary/diary.html`, `review/test_diary_smoke.py`, and coordination docs.

## Implementation Steps

1. Add `STATUS_SPECIFIC_REASON_CODE_OPTIONS` keyed by `Cancelled`, `DNA`, and `NoShow`.
2. Refactor dropdown population to prefer status-specific options, with the R15 context fallback retained.
3. Keep `PATIENT_UNWELL` absent from option arrays but present in `STATUS_REASON_CODE_LABELS`.
4. Bump `diary.js` cache-bust version.
5. Tighten reason-code smoke checks for status-specific option lists.

## Visual / Behavioural Acceptance Checks

- `Cancelled` shows cancellation/admin options only.
- `DNA` and `NoShow` show non-attendance/walkout/admin options.
- `PATIENT_UNWELL` never appears as a selectable first-party option.
- Empty default and validation remain unchanged.

## Risks / Ambiguities

`LEFT_WITHOUT_SEEN` belongs under `DNA`/`NoShow` because EMR4 has no separate terminal appointment status for arrived-but-left-before-seen. This was confirmed by Gemini's R16 domain review.

## Codex Plan Review

- Review result: Accepted.
- Required changes before implementation: Keep the implementation local under Ariadne because prior worker UI diffs caused encoding corruption.
- Approved to proceed: yes
