# claude-bernie-selected-instruction-safety-review

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 39e0f6c |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-bernie-selected-instruction-safety-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-bernie-selected-instruction-safety-review --commit-message "Submit Bernie instruction safety review" --message "claude-bernie-selected-instruction-safety-review ready for Codex review"` |

## Mission

Provide an independent read-only safety/contract review for Sprint 73 before implementation is integrated. Focus on how selected-appointment instruction affordances should preserve explicit staff submit, stale-context protection, no manual ID exposure, no browser/query persistence of free text, and confirmation gating.

## Scope

### In Scope

Read-only review of docs/diary/diary.js, review/test_diary_smoke.py, and relevant orchestration context; update this task packet Completion Notes and submit a Codex review packet with concrete acceptance criteria, edge cases, and any safety concerns. No production code edits.

### Out of Scope

Implementing UI changes, modifying app/backend/routes/schemas/models/migrations, changing tests unless explicitly asked later, dependency work, provider/Gemini changes, taskpane, Command Centre, billing, SMS, resource admin, and broad diary redesign.

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

No runtime tests required for read-only review; run git status --short --branch before submit and report if clean. If any file is edited, git diff --check must pass.

## Merge Criteria

Codex receives a concise submitted review packet with concrete acceptance criteria/edge cases and no production code changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
