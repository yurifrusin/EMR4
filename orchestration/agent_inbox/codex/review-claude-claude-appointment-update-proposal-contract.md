# review-claude-claude-appointment-update-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-update-proposal-contract` |
| Status | integrated |

## Review Request

Appointment update proposal contract ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-appointment-update-proposal-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated. Focused tests passed after merge; proposal endpoints are non-mutating, route ordering is safe, and update/status proposal semantics are documented as proposal metadata rather than execution.
- Follow-up required: Decide later whether clearing a linked patient should be proposal-supported or remain direct-edit only.
