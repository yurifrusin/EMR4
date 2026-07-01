# claude-sprint97-bernie-interpreter-readiness

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 89fb530 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint97-bernie-interpreter-readiness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint97-bernie-interpreter-readiness --commit-message "Sprint 97 Bernie interpreter readiness contract" --message "claude-sprint97-bernie-interpreter-readiness ready for Codex review"` |

## Mission

Plan the backend/API fix so a simple receptionist prompt such as 'Make an appointment for Margaret Thompson after 3 today with Dr Shera' does not fail merely because the live interpreter provider is unavailable. Define a deterministic/local fallback or explicit provider readiness contract that remains non-mutating and staff-confirmed.

## Scope

### In Scope

Plan packet first only. Inspect app/services/bernie_booking_interpreter.py, app/routers/appointments.py, app/schemas/appointments.py, app/services/ai provider setup, scripts/smoke_bernie_interpreter.py, tests/test_bernie_interpret_booking_instruction.py, and related appointment proposal tests. Propose exact minimal backend changes for provider readiness, deterministic fallback for common receptionist prompts, clearer blocked issue codes, and no-write/audit assertions.

### Out of Scope

Production code edits before plan approval; diary frontend; live phone system, Caller ID, Medicare/OPV/PVM/IHI, GCP console setup, new paid provider integration, taskpane, Command Centre, broad implementation-plan rewrite, or weakening human confirmation gates.

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

Plan must name focused pytest targets, a non-mutating prompt smoke for the Margaret Thompson/Dr Shera case, provider-unavailable/fallback tests, no appointment write assertions, audit expectations, and migration/no-migration rationale.

## Merge Criteria

Ariadne can approve only if the plan makes the simple prompt path pass without using raw practitioner/patient IDs in ordinary UI, keeps confirmed writes behind confirm endpoint, and makes provider-unavailable impossible to miss in release checks.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - EDIT app/config.py — added `bernie_booking_interpreter_fallback_to_deterministic: bool = False`
  - EDIT app/schemas/appointments.py — extended `BernieBookingInterpreterMetadata.mode` Literal to include `"deterministic_fallback"`
  - EDIT app/services/bernie_booking_interpreter.py — natural time phrase parsing (_parse_time_fragment, _extract_natural_time_constraints), interpreter_is_ready(), enhanced _extract_fake_command(), GeminiVertex deterministic fallback on live failure
  - NEW tests/test_bernie_sprint97_interpreter_readiness.py — 18 focused tests covering all required scenarios
- Verification run:
  - py_compile on all 4 changed/new Python files: OK
  - pytest tests/test_bernie_sprint97_interpreter_readiness.py -v: 18 passed
  - pytest tests/test_bernie_interpret_booking_instruction.py tests/test_bernie_slot_normalizer.py -v: 44 passed (no regressions)
  - git diff --check: clean
- Remaining risks:
  - bernie_booking_interpreter_fallback_to_deterministic defaults False (safe, fail-closed); production must opt in
  - Business-hours pm assumption for bare hours 1–11 is a heuristic appropriate for AU GP clinic context
  - Schema mode Literal change is backward-compatible; no migration needed
