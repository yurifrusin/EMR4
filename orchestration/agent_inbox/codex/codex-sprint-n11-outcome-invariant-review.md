# codex-sprint-n11-outcome-invariant-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | e82a885 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-n11-outcome-invariant-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-n11-outcome-invariant-review --commit-message "Sprint N11 outcome invariant review" --message "codex-sprint-n11-outcome-invariant-review ready for Codex review"` |

## Mission

Produce an invariant plan for N11 ensuring schedule/roster explanations, typed outcomes, server-session transitions, and Diary affordances cannot contradict actual schedule/search facts.

## Scope

### In Scope

Plan first. Inspect app/services/diary, app/services/bernie, app/routers/appointments.py, app/schemas/appointments.py, docs/diary/diary.js, review/test_diary_smoke.py. Define adversarial tests and integration boundaries; no implementation until approved.

### Out of Scope

No production code before approval. No persisted session table, GraphRAG, auto-mode, broad UI redesign, or root-to-branch API review.

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

Plan must list adversarial cases: practitioner not rostered on requested day, roster unavailable distinct from searched zero slots, availability search not skipped into no-slot, advisory-only retrieval cannot set roster truth, stale session revision preserved, and confirmation stays evidence-gated.

## Merge Criteria

Plan is precise enough for Ariadne/worker implementation and preserves backend authority over search truth, schedule truth, policy, session binding, and confirm affordances.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Plan phase only in the Codex worker; Ariadne implemented the accepted invariant slice in backend outcome/gate tests and Diary smoke tests.
- Verification run: Ariadne ran focused and adjacent backend Bernie suites, full deterministic Diary smoke, py_compile, node --check, frontend version check, and git diff --check; see orchestration/sprint_closeout.md.
- Remaining risks: The worker did not submit via branch; Ariadne copied the coordination-only plan packet from the clean Codex mirror and integrated it manually.
