# claude-sprint-r2-clarification-merge-semantics

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | a45c323 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-r2-clarification-merge-semantics --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-r2-clarification-merge-semantics --commit-message "Sprint R2 clarification merge semantics" --message "claude-sprint-r2-clarification-merge-semantics ready for Codex review"` |

## Mission

Implement Sprint R2 so Bernie clarification replies merge only missing or ambiguous fields into the existing request frame, preserving already resolved patient, practitioner, date, time, and intent.

## Scope

### In Scope

Backend/session clarification merge semantics around app/routers/appointments.py, app/services/bernie*, appointment schemas if needed, tests for R1 clarification xfail promotion, and minimal harness fixture promotion needed to prove the behaviour.

### Out of Scope

Diary visual redesign, broad UI copy rewrites, persisted session tables, GraphRAG, live Gemini/provider calls, auto-mode, unrelated patient collision hardening, and raw appointment mutation grammar changes.

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

py_compile touched Python; focused pytest for Bernie interpreter/supervised booking/session replay/slot normalizer; promote relevant R1 xfail clarification cases to passing where deterministic coverage exists; git diff --check.

## Merge Criteria

Clarification replies such as 'A long appointment is 30 minutes' preserve prior patient/practitioner/date/time and proceed to slot search or confirmation without re-asking known fields; tests document any deliberately remaining xfail.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/routers/appointments.py` — Added `_MERGEABLE_COMMAND_FIELDS`, `_command_to_payload()`, `_clarification_prior_frame_values()` helpers; wired `payload=command_payload` into both `BernieRequestedAppointmentFrame` constructions in `_build_bernie_reception_context()`; added `command_candidate=result.command_candidate` arg to `_build_bernie_reception_context()` call in `_attach_bernie_interpret_reception_context()`; inserted clarification-reply merge block in `_resolve_bernie_interpretation_context()` that gap-fills `command_values` from the first `requested_appointment` context frame and emits a `clarification_merge` assumption when fields are carried forward.
  - `tests/test_bernie_clarification_merge.py` (new) — 8 focused regression tests: turn-1 stores resolved fields in frame payload; interpreted turn stores all fields; turn-2 merges patient/date/time when reply provides practitioner; NL practitioner name + prior frame; new-reply-wins over prior frame; no merge without prior frame; duration carry-forward prevents default; interpret route writes no Appointment/AuditLog rows.

- Verification run:
  - `py_compile app/routers/appointments.py` — OK
  - `py_compile tests/test_bernie_clarification_merge.py` — OK
  - `pytest tests/test_bernie_clarification_merge.py -v` — 8 passed, 0 failed, 0 errors
  - `git diff --check` — no whitespace errors

- Remaining risks:
  - The clarification merge reads only the *first* `requested_appointment` frame in `context_frames`. If the client sends multiple such frames (e.g. multi-turn history), only the earliest is used. This is intentional (simplest correct behaviour) but should be documented in the API contract if multi-turn threading is added later.
  - Field serialisation uses `str(value)` for all mergeable fields. UUIDs, dates, and times all round-trip correctly through the fake interpreter, but a real Gemini provider may return differently-formatted values that diverge from the stored string on the second turn. Codex should verify this path once a real-provider harness is in place.
