# antigravity-sprint-r10-reason-code-governance-policy

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 81fc8c6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r10-reason-code-governance-policy --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r10-reason-code-governance-policy --commit-message "Sprint R10 Reason-Code Governance Policy" --message "antigravity-sprint-r10-reason-code-governance-policy ready for Codex review"` |

## Mission

Use Gemini to review receptionist/admin copy and product policy for structured cancellation/status reason-code governance.

## Scope

### In Scope

docs/receptionist_review_r10.md only; reason-code taxonomy, staff copy, audit expectations, migration risk, and what should remain free text versus coded.

### Out of Scope

Production code, tests, migrations, UI/assets, live provider calls, temporal slot-write policy changes.

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

Documentation artifact only; verify docs/receptionist_review_r10.md exists and no code/test files changed.

## Merge Criteria

Policy gives a practical reason-code taxonomy and recommends a safe implementation path without changing temporal blocking semantics.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `docs/receptionist_review_r10.md`
- Verification run: Ariadne reviewed and integrated a cleaned policy artifact; focused backend audit suite passed.
- Remaining risks: Reason-code taxonomy still needs receptionist feedback before migration or strict enforcement.
