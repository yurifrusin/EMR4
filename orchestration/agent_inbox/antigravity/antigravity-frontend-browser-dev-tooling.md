# antigravity-frontend-browser-dev-tooling

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | bd13038 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-frontend-browser-dev-tooling --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-frontend-browser-dev-tooling --commit-message "Dispatch Sprint 22 frontend dev tooling" --message "antigravity-frontend-browser-dev-tooling ready for Codex review"` |

## Mission

Plan, then after approval improve diary/taskpane frontend development and browser-feedback loops so UI affordance regressions are caught by tools before Yuri is asked to test.

## Scope

### In Scope

Frontend/dev tooling only: diary/taskpane smoke commands, browser/check scripts, deployed/local asset version checks, npm script ergonomics, docs for Antigravity/Gemini-assisted UI QA, and small non-runtime test harness improvements. May touch docs, package scripts/config, smoke utilities, and orchestration notes if needed.

### Out of Scope

Changing diary/taskpane product behaviour, visual redesign, backend API contracts, migrations, patient/clinical flows, production WhatsApp notification sending, and broad forced dependency upgrades.

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

Plan packet first. After approval: node syntax/build/validate or smoke commands proposed in the plan, local/deployed asset URL checks where feasible, git diff --check, and exact command outputs plus any browser/visual observations in Completion Notes.

## Merge Criteria

Ariadne gets a repeatable frontend/browser check path that would have caught recent affordance/state regressions earlier; scripts/docs are clear for agents; no product UI changes land unless explicitly scoped and justified as tooling-only.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
