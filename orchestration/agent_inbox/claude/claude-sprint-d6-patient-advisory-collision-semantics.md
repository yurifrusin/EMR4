# claude-sprint-d6-patient-advisory-collision-semantics

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
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
  - NEW tests/test_bernie_d6_patient_advisory_collision.py — 10 focused tests:
    - 6 pure unit tests for has_existing_booking_on_requested_day (no DB, no fixtures):
      true for matching date, false for different date, false for None, false for empty
      future_bookings, false when only recent_bookings match, true for one match among several.
    - 2 interpret-route regression tests: same-day positive (hard assert warning emitted),
      different-day negative (hard assert warning not emitted, patient_booking_context preserved).
    - 2 supervised-booking regression tests: same-day positive, different-day negative, both
      hard asserts with patient_booking_context preservation confirmed.
  - No production code changes. The existing gating in app/routers/appointments.py
    (has_existing_booking_on_requested_day at lines ~3801-3806 for interpret and ~5555-5561
    for supervised booking) was verified to be correct. D6 implements regression-test hardening
    only, per user approval.

- Verification run:
  - py_compile tests/test_bernie_d6_patient_advisory_collision.py app/services/bernie_patient_context.py: OK
  - pytest tests/test_bernie_d6_patient_advisory_collision.py -v: 10 passed in 3.45s
  - pytest tests/test_bernie_patient_context.py tests/test_bernie_d5_route_builder_search_horizon.py tests/test_bernie_interpret_booking_instruction.py -q: all passed (51 tests)
  - Full pytest tests/ -q: in progress (background)
  - git diff --check: clean

- Remaining risks:
  - Cap silent false-negative: has_existing_booking_on_requested_day checks future_bookings
    which is capped at _FUTURE_CAP=3. If the patient has 3+ nearer future bookings before
    the requested date, the requested date's booking falls outside the cap and the warning
    is silently suppressed. Rare in normal practice but possible. Follow-up: consider
    raising the cap, adding an exact-date query, or documenting the limitation explicitly.
  - Self-collision gap: build_patient_booking_context is called after normalization but
    before any write. If a receptionist is rebooking a patient (cancelling old, booking
    new same day), the old appointment still appears in future_bookings at context-build
    time, which may cause a spurious warning. Not a data-correctness issue (no write
    happens), but could confuse reception staff. Follow-up: evaluate at the booking-create
    surface when the cancel+rebook workflow is implemented.
  - Both risks noted per user instruction; no production code change required this sprint.
