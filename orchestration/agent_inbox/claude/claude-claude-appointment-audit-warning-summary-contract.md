# claude-claude-appointment-audit-warning-summary-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | a448194 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-claude-appointment-audit-warning-summary-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-claude-appointment-audit-warning-summary-contract --commit-message "Claude Appointment Audit Warning Summary Contract" --message "claude-claude-appointment-audit-warning-summary-contract ready for Codex review"` |

## Mission

Plan, then after approval persist safe warning metadata for confirmed appointment proposal mutations so audit history can prove when staff confirmed warnings.

## Scope

### In Scope

Plan packet first. After approval: appointment proposal/confirmation and audit-log backend surfaces only as needed, likely app/models/appointments.py, app/schemas/appointments.py, app/routers/appointments.py, Alembic migration if persistence requires one, and focused appointment audit/proposal tests. Preserve practice scoping and no-write proposal semantics.

### Out of Scope

Diary UI implementation, broad supervisor dashboard, Bernie runtime/tool execution, taskpane, Command Centre, SMS, billing, patient demographics, unrelated appointment flows, broad audit framework beyond appointment mutation warning metadata.

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

Plan packet first. After approval: py_compile touched backend modules, focused pytest for appointment proposal/audit warning-summary persistence, adjacent audit/proposal tests if touched, alembic upgrade head if migration added, and git diff --check.

## Merge Criteria

Codex can verify confirmed warning-bearing appointment mutations write/read bounded warning metadata in audit history; blocked/aborted proposals still do not write; existing audit actor/readability tests continue passing; no frontend or unrelated backend scope drift.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - EDIT app/models/appointments.py — added JSONB import; added `confirmed_warnings = Column(JSONB, nullable=True)` to `AppointmentAuditLog`
  - NEW alembic/versions/i9j0k1l2m3n4_add_confirmed_warnings_to_audit.py — ALTER TABLE ADD COLUMN confirmed_warnings JSONB NULL; downgrade drops it
  - EDIT app/schemas/appointments.py — added `confirmed_warnings: list[str] = Field(default_factory=list)` to `AppointmentCreate`, `AppointmentUpdate`, `AppointmentStatusUpdate`, `AppointmentDeleteIn`; added `confirmed_warnings: list[str] = Field(default_factory=list)` to `AppointmentAuditLogOut`
  - EDIT app/routers/appointments.py — `_write_audit()` accepts `confirmed_warnings: list[str] | None = None` and stores NULL when list is empty; `_canonical_create_values` and update values dict both exclude `confirmed_warnings` via `exclude={"confirmed_warnings"}` to prevent it leaking into Appointment constructor; all 4 mutation endpoints (create, update, status_change, delete) pass `body.confirmed_warnings or None` to `_write_audit()`; `get_appointment_audit` maps `entry.confirmed_warnings or []` to `AppointmentAuditLogOut.confirmed_warnings`
  - NEW tests/test_appointment_audit_warning_summary.py — 15 tests covering create/update/status_change/delete persistence, empty-list-to-NULL, GET /{id}/audit returns confirmed_warnings, codes-only assertion, proposal endpoint still writes no audit
- Verification run:
  - py_compile on all 5 touched/new Python modules: OK
  - pytest tests/test_appointment_audit_warning_summary.py tests/test_appointment_audit.py: 27 passed (15 new + 12 existing)
  - git diff --check: clean (CRLF note on coordination file only, not a code file)
- Remaining risks:
  - Migration adds nullable JSONB column — safe for existing table. Downgrade is destructive if confirmed_warnings data exists in production.
  - No allow-list validation on warning code strings; caller supplies any strings. A future sprint could enforce a `ConfirmedWarningCode` enum if canonical codes need locking down.

## Codex Integration Result

Integrated in Sprint 37 after Ariadne review, bounded warning-code sanitization, Alembic head repair, and verification.
