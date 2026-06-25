# claude-appointment-cancellation-reason-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 24c76b4 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-appointment-cancellation-reason-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-cancellation-reason-contract --commit-message "Appointment cancellation reason contract" --message "claude-appointment-cancellation-reason-contract ready for Codex review"` |

## Mission

Plan first, then after approval add a minimal backend contract so receptionist cancellation/delete can capture a short cancellation reason or note without weakening proposal-first safety semantics.

## Scope

### In Scope

app/routers/appointments.py; app/schemas/appointments.py; app/models/appointments.py only if a separate persisted cancellation field is justified; Alembic migration only if a new field is chosen; focused appointment cancellation/proposal tests; minimal seed/test helpers if needed

### Out of Scope

Diary frontend implementation; taskpane; Command Centre; patient demographics; billing; SMS/reminders; broad audit logging; proposal review history; changing non-cancel appointment reason semantics unless required by the plan

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

Plan packet first; after approval run py_compile touched appointment router/schema/model, focused cancellation/delete proposal pytest, migration checks if added, adjacent status/update proposal tests if contract touched, git diff --check

## Merge Criteria

Codex can verify cancellation reason/note is represented consistently in proposal command and final mutation, terminal status safety remains intact, waiting_area clearing still works, tests cover auth/practice scope/abort-safe proposal/no stranded waiting area, and no frontend files are changed by this workstream

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

- Files changed:
  - `app/models/appointments.py` — added `cancellation_reason = Column(String(500), nullable=True)` to `Appointment`.
  - `alembic/versions/274919209522_add_cancellation_reason_to_appointments.py` — new migration; additive ADD COLUMN only (unrelated autogenerate drift stripped).
  - `app/schemas/appointments.py` — added `AppointmentDeleteIn` (with `cancellation_reason: Optional[str] = Field(None, max_length=500)`); added `cancellation_reason: Optional[str] = None` to `AppointmentDeleteCommand` and `AppointmentOut`.
  - `app/routers/appointments.py` — added `Body` to FastAPI imports and `AppointmentDeleteIn` to schema imports; updated `cancel_appointment` (DELETE) to accept optional `AppointmentDeleteIn` body and write `cancellation_reason` to the row; updated `propose_delete_appointment` (POST /proposals/delete) to accept same body and echo `cancellation_reason` in the returned command.
  - `tests/test_appointment_status_mutations.py` — added 4 tests: `test_delete_with_reason_persists`, `test_delete_without_reason_is_null`, `test_delete_proposal_echoes_reason_in_command`, `test_delete_reason_too_long_returns_422`.

- Verification run:
  - `alembic upgrade head` — applied cleanly (`g7h8i9j0k1l2 -> 274919209522`).
  - `py_compile app/models/appointments.py app/schemas/appointments.py app/routers/appointments.py` — OK.
  - `pytest tests/test_appointment_status_mutations.py -q --tb=short -p no:randomly` — **34 passed, 0 failed** (30 pre-Sprint-29 + 4 new).
  - `git diff --check` — OK.

- Remaining risks:
  - HTTP DELETE with a request body is RFC 9110-legal; FastAPI handles it. Starlette `TestClient.delete()` does not expose a `json=` kwarg, so body-bearing DELETE tests use `client.request("DELETE", ...)` — a minor test-ergonomics note, no production risk.
  - `PATCH /status` to Cancelled does not capture `cancellation_reason`; this is intentional (quick status flip vs deliberate cancellation path). A future sprint can align if needed.
  - Migration is additive nullable column — zero data risk to existing rows.
