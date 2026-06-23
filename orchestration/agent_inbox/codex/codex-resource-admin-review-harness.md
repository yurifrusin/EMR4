# codex-resource-admin-review-harness

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/resource-admin-review-harness` |
| Status | integrated |
| Created | d78659a |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-resource-admin-review-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-resource-admin-review-harness --commit-message "Resource admin review harness" --message "codex-resource-admin-review-harness ready for Codex review"` |

## Mission

Plan, then after explicit approval prepare the integration and user-review harness for Sprint 19 resource admin without duplicating backend or frontend implementation scopes.

## Scope

### In Scope

Orchestration review docs, API spot-check snippets, user-review checklist, closeout scaffolding, and vocabulary guardrails tied to orchestration/resource_admin_bernie_tool_design.md and orchestration/location_diary_view_review.md.

### Out of Scope

Production backend/frontend code, migrations, taskpane, Command Centre, appointment mutations, patient merge/delete, autonomous Bernie runtime, worker packet rewrites after launch unless Codex explicitly updates scope.

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

Plan packet first if launched as a worker. After approval: git diff --check and snippet sanity review against final backend API submitted for Sprint 19.

## Merge Criteria

Review harness names exact surfaces to test and not test; keeps room/resource/waiting-area/location/page-view/status/patient-identity language separate; preserves worker dissent and risks; gives the user clear post-integration review steps.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/resource_admin_review.md`
  - `orchestration/sprint_closeout.md`
  - `orchestration/protocol_alerts.md`
  - `AGENTS.md`
  - `orchestration/parallel_workstreams.md`
- Verification run:
  - `git diff --check` passed after integration whitespace cleanup.
  - Backend and diary UI verification are recorded in Sprint 19 closeout.
- Remaining risks:
  - Manual user review still needs live Admin/PracticeOwner and non-admin diary checks after deploy.
