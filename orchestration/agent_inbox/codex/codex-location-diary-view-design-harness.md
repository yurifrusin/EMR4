# codex-location-diary-view-design-harness

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/location-diary-view-design-harness` |
| Status | integrated |
| Created | 32f1577 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-location-diary-view-design-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-location-diary-view-design-harness --commit-message "Add location diary view design harness" --message "Location/diary view design harness ready for Codex review"` |

## Mission

Plan first, then after approval prepare the design guardrails, user-review checklist, and future Bernie tool vocabulary for practice vs location vs room/resource vs waiting area vs diary page/view group.

## Scope

### In Scope

Orchestration docs, implementation-plan notes, sprint closeout/review harness, API/user-test snippets if useful.

### Out of Scope

Production backend/frontend implementation, migrations, taskpane/Command Centre, autonomous Bernie runtime, drag/drop/resize.

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

Plan packet first. After approval: git diff --check.

## Merge Criteria

The project has a clear review harness and vocabulary that prevents workers from modelling screen real estate as physical location or waiting-area flow as appointment state.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/location_diary_view_review.md` added;
  `orchestration/sprint_closeout.md` updated with a Sprint 16 harness pointer;
  `implementation_plan.md` updated with the Sprint 16 location review harness
  guardrail; `orchestration/agent_inbox/codex/plan-codex-codex-location-diary-view-design-harness.md`
  captured the approved plan; source task packet updated with completion notes.
- Verification run: `git diff --check` passed.
- Remaining risks: API spot-check snippets are review aids only because final
  route and payload names depend on the submitted backend/UI branches. The
  harness deliberately avoids production code and does not prove runtime
  location scoping by itself.
