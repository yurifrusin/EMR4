# plan-claude-claude-appointment-edit-proposal-contract-hardening

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-edit-proposal-contract-hardening` |
| Status | pending_plan_review |
| Created | 2026-06-24 22:59 +1000 |
| Source HEAD | `bb006db` |

## Plan Summary

Block null-practitioner and null-patient-identity in update proposal; 7 new tests

## My Understanding

propose_update_appointment has two gaps where a safe=True response is returned but the corresponding PUT would fail: (1) explicit {practitioner_id: null} in body causes _ensure_practitioner(None, db) which queries WHERE id IS NULL, finds nothing, and raises 404 instead of a clean BLOCK; (2) {patient_id: null} on a linked appointment with no provisional name produces a command with patient_id=None and patient_name_provisional=None — proposal returns safe=True with provisional_patient warning, but PUT rejects with 422 'patient_id or patient_name_provisional is required'. Both break the UI contract that any safe proposal is safely executable.

## Intended Surface / Boundary

Backend only: propose_update_appointment in app/routers/appointments.py; tests/test_appointment_update_proposal.py. No diary frontend, taskpane, Command Centre, schemas, migrations, or other routes changed.

## Out Of Scope

proposals/create, proposals/status endpoints; PUT /{id} endpoint; AppointmentUpdateProposalIn schema changes; Bernie/autonomous execution; waiting_area_id handling in update proposal; migrations

## Files I Expect To Edit

app/routers/appointments.py (propose_update_appointment only, ~12 lines); tests/test_appointment_update_proposal.py (7 new tests appended)

## Implementation Steps

1. In propose_update_appointment, move warnings/blocks list init to BEFORE the _ensure_* calls (currently after). 2. After merge block (line 593), add BLOCK for null practitioner: if 'practitioner_id' in incoming and practitioner_id is None, append practitioner_required block and restore practitioner_id=appt.practitioner_id so subsequent conflict/break checks use valid practitioner. 3. After patient_name_provisional merge, add BLOCK for null patient identity: if patient_id is None and not patient_name_provisional, append patient_identity_required block. 4. _ensure_patient already guarded with 'if patient_id is not None'; _ensure_practitioner now always receives a non-null value (restored in step 2). 5. Add 7 tests to tests/test_appointment_update_proposal.py: (a) explicit null practitioner_id -> blocked practitioner_required; (b) null patient_id with no provisional -> blocked patient_identity_required; (c) null patient_id + provisional in body -> safe, provisional_patient warning (valid downgrade); (d) cross-practice appointment -> 404; (e) non-existent appointment UUID -> 404; (f) empty body {} -> safe, command echoes current appointment values; (g) explicit valid practitioner change -> safe, command has new practitioner_id.

## Visual / Behavioural Acceptance Checks

POST /proposals/update/{id} with {practitioner_id: null} returns 200 safe=False blocked practitioner_required; POST /proposals/update/{id} with {patient_id: null} on linked appointment returns 200 safe=False blocked patient_identity_required; cross-practice returns 404; non-existent returns 404; empty body returns safe=True with current values; valid practitioner change returns safe=True; all existing proposal tests still pass; python -m pytest tests/test_appointment_update_proposal.py -> all pass; scripts/check_backend.ps1 tier-1 clean; git diff --check clean; appointment row unchanged after every proposal call

## Risks / Ambiguities

Restoring practitioner_id on null-block means the command in the blocked response shows the existing practitioner — correct for a blocked response since it must not be executed. patient_identity_required block also fires when a provisional appointment's provisional name is explicitly cleared (patient_id already None, patient_name_provisional set to null in body) — this is intentional and correct.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
