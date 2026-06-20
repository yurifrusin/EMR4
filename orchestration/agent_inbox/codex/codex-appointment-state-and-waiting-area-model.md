# codex-appointment-state-and-waiting-area-model

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/appointment-state-waiting-area-model` |
| Status | integrated |
| Created | c96c637 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-appointment-state-and-waiting-area-model --commit-message "Document appointment state and waiting area model" --message "Appointment state and waiting-area model ready for Codex review"` |

## Mission

Produce a concrete implementation note and review harness for the appointment identity/status/waiting-area model before drag/drop/resize work. Clarify linked identity, provisional identity, attendance states, future SMS confirmation, completion/billing guard concerns, physical waiting areas, and what user/API review should prove after Sprint 12.

## Scope

### In Scope

orchestration review docs, implementation_plan.md or focused docs under docs/design if appropriate, sprint_closeout additions, exact PowerShell API snippets for user review, and very small non-production checklist helpers only if useful.

### Out of Scope

Production backend/frontend implementation, migrations, diary JS/CSS feature work, taskpane UI feature work, Gemini/AI work, billing implementation, real ADHA/IHI integration.

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

Run git diff --check. If any script/checklist helper is added, run its focused syntax/check command. Completion Notes must include design decisions, open risks, and exact user-review commands.

## Merge Criteria

The project has a concise but explicit appointment-state/waiting-area design note and Sprint 12 review checklist; it distinguishes patient identity confirmation from attendance and future SMS confirmation; it gives Codex enough review criteria to integrate backend/frontend Sprint 12 submissions.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - Added `orchestration/appointment_state_waiting_area_review.md`, a Sprint 12 design/review harness that separates linked patient identity, provisional identity, attendance workflow, legacy `Confirmed`, future SMS/reminder confirmation, completion/billing guard concerns, and physical waiting-area modelling.
  - Updated `implementation_plan.md` Phase 2 backlog with a waiting-area model note.
  - Updated `orchestration/sprint_closeout.md` to point Sprint 12 integration and user review to the new harness.
  - Updated this task packet's status/completion notes.
- Verification run:
  - `git diff --check` after adding the new review note to the diff with intent-to-add -> passed.
  - No helper script was added, so no script syntax check was required.
- Design decisions:
  - `patient_id`/embedded `patient` is linked patient-record identity, not arrival or SMS confirmation.
  - `patient_name_provisional` with `patient_id = null` is a provisional diary identity, not a patient record.
  - Attendance state remains `Appointment.status`; routine workflow should use `Booked`, `Arrived`, `InConsult`, `Completed`, `Cancelled`, `NoShow`, and `DNA`, while legacy `Confirmed` remains compatible/readable but should not be promoted as the identity-link or SMS-confirmation action.
  - Future SMS confirmation belongs to reminder/SMS response metadata, not the appointment identity or attendance field.
  - `appointments.waiting_room` is a temporary physical-area string/override. Later room/resource/roster entries should map to default physical waiting areas and the waiting-room panel should support area tabs/filters.
  - Completion should stay correction-friendly for now, but billing/finalisation must later guard against accidental duplicate billing when `Completed` is toggled.
- Exact user-review commands:
  - See `orchestration/appointment_state_waiting_area_review.md` section "PowerShell API Review" for login/discovery, provisional create, patient link, status mutation, waiting-room inclusion/exclusion, identity-clearing rejection, and SMS-out-of-scope checks.
- Remaining risks:
  - This is documentation/review harness only; Claude and Antigravity submissions may intentionally differ and Codex should reconcile the checklist during integration.
  - Current schema still has legacy `Confirmed`; UI/API should continue to tolerate it until a later migration or explicit deprecation plan.
  - Real physical waiting-area tables/IDs, check-in events, SMS replies, ADHA/IHI verification, and billing guards remain future implementation work.
