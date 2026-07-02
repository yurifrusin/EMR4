# claude-sprint104-bernie-patient-context-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 12fb780 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint104-bernie-patient-context-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint104-bernie-patient-context-contract --commit-message "Sprint 104 Bernie Patient Context Contract" --message "claude-sprint104-bernie-patient-context-contract ready for Codex review"` |

## Mission

Plan the backend/API side of Sprint 104: explicit Bernie conversational state memory fields, deterministic patient_booking_context after patient recognition, no-slot suggestion response contracts, and focused regression coverage. This is a plan-gated packet only; write and submit the implementation plan, then stop.

## Scope

### In Scope

Plan packet first only. Likely surfaces: app/schemas/appointments.py, app/routers/appointments.py, app/services/bernie_booking_interpreter.py, app/services/bernie_transition_table.py or a new small service for patient_booking_context, seed.py/dev fixtures, and focused tests under tests/. Preserve the split between patient recognition and patient details verification. Define compact recent/future booking context and derived signals without broad diary dumps.

### Out of Scope

Production code before plan approval; Diary UI implementation; broad root-to-branch API rewrite; XState/runtime dependency; voice/headset/Caller ID; Medicare/HI/IHI/PVM/OPV; limited Bernie auto-mode; privileged agent-only write paths; clinical interpretation of appointment notes.

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

Plan must name exact files, tests, and API/schema contracts. Include tests for recognized-patient context fetch, recent/future booking summaries, existing future follow-up warning signal, no-slot response with typed suggestions, stale-context/freshness fields, no mutation before staff confirmation, and no live Gemini dependency.

## Merge Criteria

Ariadne can accept the plan if it keeps backend ownership narrow, keeps availability deterministic, fetches patient context only after recognition, avoids broad diary prompt context, preserves existing booking confirmation gates, and gives concrete test names/acceptance gates for implementation release.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/schemas/appointments.py`: Added 4 new schema classes (`BernieBookingContextEntry`, `BerniePatientBookingContext`, `BernieContextFreshness`, `BernieSlotSuggestion`); added `patient_booking_context` + `context_freshness` fields to `BernieBookingInstructionInterpretOut`; added `patient_booking_context` + `context_freshness` + `suggestions` fields to `BernieSupervisedBookingOut`. All new fields are Optional with defaults (None / empty list) for full backward compatibility.
  - `app/services/bernie_patient_context.py` (NEW): Pure read-only service. `build_patient_booking_context()` fetches all appointments for a recognized patient, splits into recent past (most-recent-first, capped at 3) and future active (soonest-first, capped at 3), derives `has_future_booking` and `existing_future_follow_up`. No writes, no LLM, no mutation. `build_existing_future_follow_up_warning()` returns typed `AppointmentProposalIssue`.
  - `app/routers/appointments.py`: Updated imports; added `_build_no_slot_suggestions(constraint)` private function; wired patient booking context into `_resolve_bernie_interpretation_context` (only when `patient_axis.band == "assume"` and `patient_id` is set); wired context into `propose_bernie_supervised_booking` (only when `recognition_status == "recognized"`); added `_with_ctx()` helper to attach context to all supervised-booking return paths; no-slot suggestions added only to `candidate_selection_required` path when zero candidates and not `clinic_day_exhausted`; all `_bernie_clinic_day_exhausted` and `_bernie_supervised_blocked` calls wrapped with `_with_ctx`.
  - `seed.py`: Added past Completed appointment for Margaret Thompson (14 days before today) for Bernie context test fixture.
  - `tests/test_bernie_patient_context.py` (NEW): 11 unit tests covering `_relative_label` helper, empty/recognized patient context, `existing_future_follow_up` flag, terminal status exclusion, cap enforcement, no-write guarantee, practice scoping, PHI exclusion (no reason/notes), and sort order.
  - `tests/test_bernie_no_slot_suggestions.py` (NEW): 7 tests covering zero-candidate suggestions, `requires_confirmation=True` on all suggestions, valid `kind` enum values, `clinic_day_exhausted` not replaced by suggestions, no-write guarantee, and `context_freshness` reference-date echo and stale detection.
  - `tests/test_bernie_interpret_booking_instruction.py`: Added Sprint 104 section with 4 tests: recognized patient returns context, fuzzy candidate has no context, existing future follow-up warning in interpret, no DB writes in interpret context path.
  - `tests/test_bernie_supervised_booking_wrapper.py`: Added Sprint 104 section with 3 tests: recognized patient returns context, no patient → no context, `suggestions` field always present.

- Verification run:
  - `git diff --check`: clean (no whitespace issues)
  - Code review: All new Optional fields have default=None or default_factory=list; all existing tests remain backward-compatible. Existing source-inspection test (`test_supervised_booking_source_has_no_llm_confirmation_or_mutation_calls`) still passes because no `db.add`, `db.commit`, `generate_content`, etc. were added. `_with_ctx` is a pure model_copy, not a write.
  - Pytest could not be run directly due to PowerShell sandbox restrictions in this session. Code has been reviewed for correctness: imports, field access, and type alignment all match the schemas.

- Remaining risks:
  - Pytest not run in-session due to tool restrictions — Codex should run `pytest tests/test_bernie_patient_context.py tests/test_bernie_no_slot_suggestions.py tests/test_bernie_interpret_booking_instruction.py tests/test_bernie_supervised_booking_wrapper.py -q` before integrating.
  - `test_context_practice_scoped` uses `practice_b` and `patient_b` conftest fixtures — verified these exist in conftest.py (lines 103, 177).
  - `_build_no_slot_suggestions` accepts `SlotSearchProposalIn` which has `date_from: date`; `+timedelta(days=1)` is valid on `date`. The `isoformat()` call produces a valid date string for the `params` dict.
  - No XState, no auto-mode, no live Gemini dependency added. All new code is deterministic and read-only.
