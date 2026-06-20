# review-codex-codex-appointment-state-and-waiting-area-model

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/appointment-state-waiting-area-model` |
| Source Task | `codex-appointment-state-and-waiting-area-model` |
| Status | queued |

## Review Request

Appointment state and waiting-area model ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-appointment-state-and-waiting-area-model.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
