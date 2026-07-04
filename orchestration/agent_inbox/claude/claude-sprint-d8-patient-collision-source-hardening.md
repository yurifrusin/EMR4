# claude-sprint-d8-patient-collision-source-hardening

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 23b93f1 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-d8-patient-collision-source-hardening --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-d8-patient-collision-source-hardening --commit-message "sprint-d8-patient-collision-source-hardening" --message "claude-sprint-d8-patient-collision-source-hardening ready for Codex review"` |

## Mission

Add direct requested-day DB lookup for patient collision detection and source-appointment exclusion for reschedule/extend flows. Currently has_existing_booking_on_requested_day() in bernie_patient_context.py only checks the capped future_bookings field (max 3 entries), which means collisions outside the compact cap can be missed. Also, reschedule/extend flows trigger self-collision because the appointment being edited is not excluded from the check.

## Scope

### In Scope

1) Add a direct DB query function in bernie_patient_context.py that checks the Appointment table for any non-terminal booking on the exact requested date (bypassing the capped future_bookings compact context). 2) Add an optional source_appointment_id parameter to the collision check so reschedule/extend flows can exclude the appointment being edited. 3) Wire the hardened check into the interpret route (~line 3801) and supervised booking route (~line 5555) in appointments.py. 4) Preserve the existing compact-context check as a fast path; add the direct DB lookup as an authoritative fallback when the compact cap might miss collisions. 5) Add focused regression tests proving: cap overflow detection (patient with 4+ future bookings where the collision is #4), source-appointment exclusion prevents self-warning on reschedule, and the warning is still emitted for genuine same-day collisions.

### Out of Scope

No frontend/UI changes. No Bernie copy/text changes. No schema migrations. No GraphRAG or persisted session changes. No changes to the warning severity (warning, not block).

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

py_compile on changed files, focused pytest on new + D6 regression tests, git diff --check

## Merge Criteria

All existing D6 tests still pass, new D8 tests pass, no production code regressions, no hardcoded patient names

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
