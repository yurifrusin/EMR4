# codex-sprint-r15-deepseek-reason-code-ui-implementation

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | queued |
| Created | 828c3ee |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r15-deepseek-reason-code-ui-implementation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r15-deepseek-reason-code-ui-implementation --commit-message "Sprint R15 DeepSeek reason-code UI implementation" --message "codex-sprint-r15-deepseek-reason-code-ui-implementation ready for Codex review"` |

## Mission

Implement first-party Diary reason-code UX polish: hide clinical-risk PATIENT_UNWELL from the selectable UI, add contextual option filtering for future cancel/delete versus retrospective status housekeeping, and preserve backend/API compatibility for existing stored codes.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.js, docs/diary/diary.css, review/test_diary_smoke.py as needed.

### Out of Scope

No backend schema/migration changes. Do not remove backend recognition/display of existing PATIENT_UNWELL values. Do not alter unrelated Diary flows.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Run or specify node syntax checks and focused review smoke tests covering reason-code dropdown options, hidden future-only housekeeping options, and stored legacy code label display.

## Merge Criteria

Submit an implementation plan packet only at plan gate; after approval, submit a narrow diff and verification notes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
