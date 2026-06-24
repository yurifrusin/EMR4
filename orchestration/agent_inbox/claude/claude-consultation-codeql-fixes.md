# claude-consultation-codeql-fixes

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | in_progress |
| Created | fca99d2 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-consultation-codeql-fixes --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-consultation-codeql-fixes --commit-message "Consultation CodeQL fixes" --message "claude-consultation-codeql-fixes ready for Codex review"` |

## Mission

Plan and then implement a focused backend fix for the open high/medium CodeQL alerts in app/routers/consultation.py: path-injection around audio_url cleanup, clear-text logging of sensitive consultation/transcription content, stack-trace exposure, and the silent exception noted by baseline review.

## Scope

### In Scope

app/routers/consultation.py; focused backend tests if an adjacent test location exists; minimal helper functions needed to safely validate local temp-file cleanup paths and return bounded error/log messages.

### Out of Scope

No diary/taskpane/UI changes, no migrations, no auth/RBAC redesign, no Gemini prompt or model behaviour changes beyond preserving existing behaviour with safer logging/error handling, no broad route refactor.

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

Before submit, run python -m py_compile app/routers/consultation.py and the most relevant focused pytest tests you can identify; run Bandit focused on app/routers/consultation.py if available. Include exact commands/results in Completion Notes.

## Merge Criteria

All targeted consultation CodeQL issues are addressed without changing successful API behaviour; errors are bounded and user-safe; logs avoid raw consultation/transcription content; verification passes or any blocker is documented.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
