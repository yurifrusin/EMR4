# claude-bernie-api-evidence-contract-plan

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 67f1c02 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-bernie-api-evidence-contract-plan --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-bernie-api-evidence-contract-plan --commit-message "Bernie API Evidence Contract Plan" --message "claude-bernie-api-evidence-contract-plan ready for Codex review"` |

## Mission

Plan the backend/API changes needed to make Bernie booking proposals receptionist-grade: structured evidence, calm frontend-enabling fields, strict non-mutating proposal semantics, explicit staff confirmation for writes, and clear auditability.

## Scope

### In Scope

Plan packet first only. Review app/schemas/appointments.py, app/routers/appointments.py, app/models/appointments.py, app/models/ai_audit.py, existing Bernie/appointment/audit tests, and relevant docs. Propose minimal schema/router/test changes so Bernie can return structured slot/patient/practitioner/identity/confirmation/action/audit evidence; confirmed writes remain the only appointment mutations. Decide whether existing AppointmentAuditLog plus Access AI audit are enough or whether a focused proposal/audit event is missing. Keep Caller ID, OPV/PVM/IHI, and phone-system integrations as optional empty context-frame/provider placeholders only.

### Out of Scope

Production code edits before plan approval; diary frontend implementation; live Caller ID, phone-system, Medicare, OPV, PVM, DVA, IHI, GCP, provider, or auth changes; taskpane, Command Centre, billing, SMS, broad implementation-plan rewrite, and broad dependency/security work.

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

Plan must name exact backend files/tests to touch, no-write/no-mutation assertions, audit assertions, focused pytest targets, migration/no-migration rationale, and edge cases around linked/provisional/ambiguous patient identity.

## Merge Criteria

Ariadne accepts the plan only if it preserves staff-confirmed writes, avoids live external integrations, gives the UI useful structured evidence rather than scary prose, and includes feasible focused verification.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
