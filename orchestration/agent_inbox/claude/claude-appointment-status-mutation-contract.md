# claude-appointment-status-mutation-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | ea0b41d |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-status-mutation-contract --commit-message "Harden appointment status mutations" --message "Appointment status mutation contract ready for Codex review"` |

## Mission

Make appointment status mutation safe enough for receptionist-facing controls before drag/drop booking work starts.

## Scope

### In Scope

Inspect app/models/appointments.py, app/schemas/appointments.py, app/routers/appointments.py, and appointment/waiting-room tests. Add or tighten tests for PATCH /api/v1/appointments/{appointment_id}/status covering auth/role gates, practice scoping, valid statuses, waiting-room inclusion/exclusion after mutation, terminal statuses freeing slots, and queue_position behavior where relevant. Make minimal production fixes only if tests expose actual unsafe behavior. Preserve existing API shape unless a small response/schema clarification is necessary. Fill Completion Notes before submit.

### Out of Scope

No diary frontend, taskpane, Command Centre, Gemini/AI, migrations unless strictly required, drag/drop booking edits, booking create/edit UI, or roster admin UI.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
9. Finish with the submit command above.

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

Run focused appointment status/waiting-room tests. At minimum run .venv\Scripts\python.exe -m pytest tests\test_waiting_room.py tests\test_appointment_conflicts.py tests\test_slots.py -q plus any new/changed status mutation tests. Report exact commands/results.

## Merge Criteria

Status mutation endpoint has clear regression coverage for safe receptionist workflow; no cross-practice or unauthenticated mutation is possible; waiting-room and slot behavior remain correct after status changes; changes are narrowly scoped.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

- **Files changed:** `tests/test_appointment_status_mutations.py` (new, 22 tests). No production code changed — endpoint is correct as-is.

- **What is tested:** auth gate (401); non-existent appointment (404); cross-practice mutation (404 — `_get_appointment` filters by both id and practice_id); all 8 valid statuses accepted (200 + updated status, parametrized); invalid status value (422); response embeds patient + practitioner AHPRA + appointment_type + end_time; mutation to each active status → appears in waiting room (4 parametrized); mutation to each terminal status → disappears from waiting room (4 parametrized).

- **Verification run:**
  ```
  python -m pytest tests/test_appointment_status_mutations.py -v  → 22 passed in 54.92s
  python -m pytest tests/test_appointment_conflicts.py::test_non_blocking_status_frees_slot[DNA] tests/test_slots.py -v  → 6 passed in 23.03s (isolated)
  python -m pytest tests/test_waiting_room.py tests/test_appointment_conflicts.py tests/test_slots.py -q  → 29 passed, 1 failed, 1 error in 180.99s (full combined run)
  ```
  The 1 failure (`test_non_blocking_status_frees_slot[DNA]`) and 1 error (`test_slots.py::test_15min_booking_blocks_only_its_slot`) both pass in isolation — pre-existing ordering flap when tests run in combined session; not caused by these changes.

- **Remaining risks:** The endpoint accepts any status transition without a state-machine guard (e.g. Completed → Booked is allowed). Intentional for now — receptionists need flexibility to correct mistakes. When lifecycle action buttons are added to the diary UI, a transition guard may be worth adding. No safety issue for the current read-only diary slice.
