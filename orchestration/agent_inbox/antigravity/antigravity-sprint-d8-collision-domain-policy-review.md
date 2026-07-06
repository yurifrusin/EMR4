# antigravity-sprint-d8-collision-domain-policy-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 23b93f1 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-d8-collision-domain-policy-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-d8-collision-domain-policy-review --commit-message "sprint-d8-collision-domain-policy-review" --message "antigravity-sprint-d8-collision-domain-policy-review ready for Codex review"` |

## Mission

Independent domain-policy review of Sprint D8 patient collision source hardening. Review the planned changes: direct requested-day DB lookup (bypassing the capped future_bookings compact context) and source-appointment exclusion for reschedule/extend flows. Do NOT implement code changes.

## Scope

### In Scope

1) Review app/services/bernie_patient_context.py for correctness of the collision detection logic. 2) Identify edge cases the current capped-context approach misses. 3) Review whether source-appointment exclusion semantics are correct (should the edited appointment be excluded from all collision checks, or only same-day?). 4) Check whether the warning severity (warning, not block) is appropriate for same-day collisions. 5) Consider multi-day windows, timezone edge cases, and terminal-status filtering. 6) Write findings in a review packet and submit.

### Out of Scope

No implementation. No code changes. No frontend/UI. No schema changes.

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

Review packet submitted with specific edge cases and correctness concerns

## Merge Criteria

Review packet is clear, specific, and identifies at least one edge case the current capped context misses

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
