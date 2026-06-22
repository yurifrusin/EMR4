# claude-appointment-update-proposal-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 7a8d07d |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-appointment-update-proposal-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-update-proposal-contract --commit-message "Add appointment update proposal contract" --message "Appointment update proposal contract ready for Codex review"` |

## Mission

Plan first, then after approval implement the backend proposal contract for editing, rescheduling, cancelling, and/or status-changing an existing appointment without mutating until staff confirmation. Preserve the new command/proposal architecture and keep scope narrow enough for one sprint.

## Scope

### In Scope

app/schemas/appointments.py, app/routers/appointments.py, focused appointment proposal/update/status tests. Non-mutating proposal endpoint(s) for existing appointment changes; typed command payloads; warnings/blocks for conflicts, break overlaps, provisional identity, terminal/cancellation semantics, and waiting-area/status effects if touched.

### Out of Scope

Diary frontend, taskpane, Command Centre, Bernie runtime/LLM code, migrations unless truly necessary, patient demographics, room/location admin UI, drag/drop/resize, SMS/reminder confirmation, billing/finalisation.

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

Plan packet first. After approval: py_compile affected backend files; focused pytest for new proposal contracts plus existing booking/status/break tests touched by the change; git diff --check.

## Merge Criteria

Existing direct appointment mutation behaviour remains compatible; new proposal endpoint(s) are non-mutating, typed, practice-scoped, auth/role-gated, and clear about safe/proposal/blocked outcomes; tests prove conflict and warning paths.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/schemas/appointments.py` — added 6 new schemas before `ScheduleSlot`: `AppointmentUpdateProposalIn`, `AppointmentUpdateCommand`, `AppointmentUpdateProposalOut`, `AppointmentStatusProposalIn`, `AppointmentStatusCommand`, `AppointmentStatusProposalOut`
  - `app/routers/appointments.py` — updated import to include all 6 new schemas; inserted two new endpoints (`POST /proposals/update/{appointment_id}` and `POST /proposals/status/{appointment_id}`) between `propose_create_appointment` and `get_waiting_room` to satisfy static-before-dynamic route ordering
  - `tests/test_appointment_update_proposal.py` (new) — 12 tests: 7 update-proposal tests (auth gate, typed command without mutation, conflict block, terminal-status block, break-overlap warning, provisional-patient warning, current-value merging) and 5 status-proposal tests (auth gate, routine Booked→Confirmed returns `execute_with_report`, waiting-area-cleared warning, same-status block, already-terminal warning)

- Verification run:
  - `py_compile` on `app/routers/appointments.py`, `app/schemas/appointments.py`, `tests/test_appointment_update_proposal.py`: all OK
  - `pytest tests/test_appointment_update_proposal.py tests/test_appointment_proposals.py -q --tb=short -p no:randomly`: **17 passed**
  - Full `pytest tests -q --tb=short -p no:randomly`: running (result pending — see background task); focused suite clean
  - `git diff --check`: CRLF warning on the packet .md file only (same as Sprint 16, pre-existing), no whitespace errors in source

- Remaining risks:
  - `propose_update_appointment` does not call `_ensure_patient` when `patient_id` is `None` and the incoming body didn't set it — it falls through to the existing appointment's `patient_id`, which may itself be `None` (provisional). That is correct behaviour (provisional → warning already fired), but the `_ensure_patient` guard only runs if the body provides a new `patient_id`. Codex should verify this is the intended pattern vs. always re-validating the stored patient FK.
  - The update proposal merges `patient_id` from the incoming body over the appointment's existing value. If a caller sends `{"patient_id": null}` intending to clear the patient link, Pydantic's `Optional[uuid.UUID] = None` default means `exclude_unset=True` will exclude it (since `None` is the default). Clearing a linked patient via this endpoint is therefore not possible; the direct `PUT /{id}` must be used. This is intentional for a proposal endpoint but should be called out to Codex.
  - `autonomy_tier = "execute_with_report"` on the status proposal is metadata for Bernie tooling — the endpoint itself is always non-mutating. Codex should confirm this is the intended semantics before wiring Bernie's tool executor to this tier.
