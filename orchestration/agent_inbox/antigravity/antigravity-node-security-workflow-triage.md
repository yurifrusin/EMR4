# antigravity-node-security-workflow-triage

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | fca99d2 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-node-security-workflow-triage --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-node-security-workflow-triage --commit-message "Node security workflow triage" --message "antigravity-node-security-workflow-triage ready for Codex review"` |

## Mission

Plan and then implement the smallest safe Node/Office security workflow follow-up after Sprint 20: inspect current Node/Office security workflow and devDependency audit state, distinguish production risk from build-tool/devDependency risk, and fix only low-risk workflow/package metadata issues that improve CI signal quality.

## Scope

### In Scope

.github/workflows/node-security.yml; EMR4 Sidebar/package.json and package-lock.json only if a safe package-manager metadata/update change is justified by the plan; orchestration notes if needed to document devDependency treatment.

### Out of Scope

No diary/taskpane runtime UI changes, no backend changes, no forced major build-tool upgrade unless the plan explicitly proves it is safe, no implementation before plan approval, no manual GitHub settings changes.

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

Before submit, run npm run validate and npm audit --omit=dev from EMR4 Sidebar; run full npm audit as non-blocking visibility if feasible; include exact commands/results and any remaining devDependency risk in Completion Notes.

## Merge Criteria

Production npm audit remains clean; CI signal is clearer; devDependency/build-tool risks are documented or safely reduced; no runtime app assets change unless specifically justified.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
