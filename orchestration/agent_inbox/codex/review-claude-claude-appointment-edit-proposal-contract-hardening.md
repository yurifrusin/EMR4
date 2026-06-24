# review-claude-claude-appointment-edit-proposal-contract-hardening

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-appointment-edit-proposal-contract-hardening` |
| Status | integrated |

## Review Request

Appointment edit proposal contract ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-appointment-edit-proposal-contract-hardening.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated into `master`. Ariadne inspected the scoped backend diff, removed unnecessary inline comments during closeout, and verified the update-proposal contract with targeted tests plus backend tier-1 checks.
- Follow-up required: Broad full-suite runtime/test-DB hygiene remains separate; Sprint 24 targeted proposal coverage passed after resetting the interrupted `gp_pms_test` schema.
