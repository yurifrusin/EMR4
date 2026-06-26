# claude-appointment-proposal-audit-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | pending_plan_review |
| Created | 4aaf8e7 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-appointment-proposal-audit-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-proposal-audit-contract --commit-message "Appointment proposal audit contract" --message "claude-appointment-proposal-audit-contract ready for Codex review"` |

## Mission

Sprint 33 / Programme 2D readiness: design and implement the backend contract for recording confirmed high-risk appointment proposal decisions as an audit trail. Preserve proposal-first safety while giving future supervisors and Bernie tooling a deterministic history surface.

## Scope

### In Scope

Backend appointment audit/proposal-history data model and API only; likely app/models.py, app/schemas/appointments.py or a bounded audit schema, app/routers/appointments.py, migrations if needed, and focused pytest coverage. Capture who confirmed, appointment id/practice id, action type/status target, warnings/blocks summary where appropriate, cancellation reason if relevant, and timestamp for confirmed writes only.

### Out of Scope

Diary UI, taskpane, Command Centre, Gemini/AI provider code, receptionist free-text messaging, restore/reactivation, billing, SMS, broad audit framework beyond appointment proposal decisions, and any direct model-to-database Bernie execution.

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

Focused pytest proving proposals remain non-mutating, confirmed create/update/status/waiting-area/delete paths create scoped audit entries, blocked/aborted proposals do not create audit entries, cross-practice access is denied, and existing appointment mutation tests still pass.

## Merge Criteria

Plan packet first with Role convention; implementation may proceed only after Ariadne approval. Merge only if audit writes are practice-scoped, deterministic, non-PHI-minimising where feasible, and existing mutation semantics remain unchanged.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
