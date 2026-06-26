# claude-appointment-audit-actor-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | pending_plan_review |
| Created | 8e36c52 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-appointment-audit-actor-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-audit-actor-contract --commit-message "Appointment audit actor contract" --message "claude-appointment-audit-actor-contract ready for Codex review"` |

## Mission

Sprint 34 / Programme 2D readiness: plan and, after approval, make appointment audit history human-readable by adding a bounded backend contract for the confirming staff actor display metadata without widening audit scope or exposing PHI.

## Scope

### In Scope

Plan packet first. After approval, app/schemas/appointments.py, app/routers/appointments.py, tests around GET /api/v1/appointments/{appointment_id}/audit, and backend code needed to return a safe actor display field such as confirmed_by_display or confirmed_by_role/name for staff users. Preserve existing audit writes and practice scoping.

### Out of Scope

Diary UI, taskpane, Command Centre, Gemini/AI provider code, full user directory API, patient/clinical PHI in audit rows, warning-code persistence, broad supervisor dashboard, Bernie execution, billing, SMS, migrations unless a verified backend contract gap requires one.

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

Plan packet first. After approval, py_compile touched backend modules, focused pytest for audit actor display/readability and existing appointment audit tests, adjacent appointment mutation tests if touched, and git diff --check.

## Merge Criteria

Audit endpoint remains authenticated and practice-scoped, confirmed mutations still write audit rows, proposal endpoints remain non-mutating, actor display is safe and stable, focused tests pass, and no out-of-scope surfaces change.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
