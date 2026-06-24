# claude-appointment-edit-proposal-contract-hardening

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 511eff0 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-appointment-edit-proposal-contract-hardening --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-edit-proposal-contract-hardening --commit-message "Dispatch Sprint 24 appointment edit proposal contract" --message "Appointment edit proposal contract hardening ready for Codex review"` |

## Mission

Plan, then after approval review and harden the backend non-mutating appointment update/reschedule proposal contract so the diary edit UI can safely preflight edits before writing.

## Scope

### In Scope

pp/routers/appointments.py, pp/schemas/appointments.py, focused tests around POST /api/v1/appointments/proposals/update/{appointment_id} and adjacent appointment update/reschedule edge cases; documentation notes only if needed for the UI contract.

### Out of Scope

Diary frontend implementation, taskpane/Command Centre, patient demographics, resource admin, migrations unless a proven schema issue exists, Bernie runtime, autonomous writes.

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

Plan packet first; after approval run scripts/check_backend.ps1, tests/test_appointment_update_proposal.py, adjacent booking create/edit or break-overlap tests if touched, and git diff --check.

## Merge Criteria

The update/reschedule proposal endpoint remains non-mutating, typed, practice-scoped, and clear for safe/warning/blocked UI handling; existing appointment update behaviour is not regressed.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/routers/appointments.py` — `propose_update_appointment` only, ~15 lines changed:
    1. Moved `warnings`/`blocks` list initialisation to before the `_ensure_*` entity calls.
    2. Added BLOCK for explicit null practitioner: if `"practitioner_id" in incoming and practitioner_id is None`, appends `practitioner_required` block and restores `practitioner_id = appt.practitioner_id` so subsequent conflict/break checks remain valid.
    3. Added BLOCK for null patient identity: if `patient_id is None and not patient_name_provisional`, appends `patient_identity_required` block. `_ensure_patient` was already guarded with `if patient_id is not None`; `_ensure_practitioner` now always receives the restored non-null value.
  - `tests/test_appointment_update_proposal.py` — added `Practitioner` import and 7 new tests:
    - `test_update_proposal_blocked_explicit_null_practitioner` — `{practitioner_id: null}` → BLOCK `practitioner_required`, row unchanged.
    - `test_update_proposal_blocked_clear_patient_id_with_no_provisional` — `{patient_id: null}` on linked appointment → BLOCK `patient_identity_required`, row unchanged.
    - `test_update_proposal_null_patient_id_with_provisional_is_safe` — `{patient_id: null, patient_name_provisional: "Walk-in"}` → safe=True, `provisional_patient` warning (valid downgrade).
    - `test_update_proposal_cross_practice_returns_404` — appointment in practice_b, authenticated as practice_a user → 404.
    - `test_update_proposal_nonexistent_appointment_returns_404` — random UUID → 404.
    - `test_update_proposal_empty_body_reflects_current_values` — `{}` → safe=True, command mirrors existing appointment, row unchanged.
    - `test_update_proposal_valid_practitioner_change` — explicit valid practitioner UUID → safe=True, command has new practitioner_id, row unchanged.

- Verification run:
  - `python -m compileall app/ tests/ -q` → exit 0, no errors.
  - `git diff --check` → exit 0, no trailing-whitespace issues.
  - Targeted: `python -m pytest tests/test_appointment_update_proposal.py -q --tb=short -p no:randomly` → **19 passed** (12 original + 7 new).
  - Full suite: `python -m pytest tests/ -q --tb=short -p no:randomly` → submitted while running; targeted file (19/19) and Tier-1 clean; no existing test touches the two new block paths.

- Remaining risks:
  - `patient_identity_required` also fires when a provisional appointment's own `patient_name_provisional` is explicitly cleared (patient_id already null, both become null). This is intentional — the invariant applies equally.
  - Blocked responses carry `appt.practitioner_id` in the command (not the null sent by the client) — correct, since blocked commands must not be executed and the command field in a blocked response is informational only.
