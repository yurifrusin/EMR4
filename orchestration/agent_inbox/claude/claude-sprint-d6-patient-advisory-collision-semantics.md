# claude-sprint-d6-patient-advisory-collision-semantics

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | eff7cdd |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-d6-patient-advisory-collision-semantics --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-d6-patient-advisory-collision-semantics --commit-message "Sprint D6 patient advisory collision semantics" --message "claude-sprint-d6-patient-advisory-collision-semantics ready for Codex review"` |

## Mission

Implement a narrow backend-domain fix so Bernie patient future-booking warnings are emitted only when compact patient context shows an appointment on the requested booking day/window, not merely any future appointment.

## Scope

### In Scope

Use existing app/services/bernie_patient_context.py helper has_existing_booking_on_requested_day where appropriate; update supervised booking and interpret/enrichment warning generation paths in app/routers/appointments.py; add focused tests proving unrelated same-day/today or other-day future bookings are advisory context but do not produce existing_future_follow_up warning for a different requested day. Preserve compact patient_booking_context output.

### Out of Scope

No frontend/UI copy changes. No GraphRAG. No persisted sessions/migrations. No broad API review. Do not suppress patient_booking_context itself; only narrow warning emission semantics.

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

py_compile touched files; focused pytest around bernie_patient_context and supervised booking wrapper/context frame/outcome tests; git diff --check.

## Merge Criteria

Ariadne can integrate only if existing_future_follow_up warning is date-collision based, patient context remains available, and no confirmation/write semantics change.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
