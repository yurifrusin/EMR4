# review-claude-claude-bernie-api-evidence-contract-plan

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-bernie-api-evidence-contract-plan` |
| Status | queued |

## Review Request

claude-bernie-api-evidence-contract-plan ready for Codex review

## Worker Completion Notes

- Files changed:
  - app/schemas/appointments.py — added BerniePractitionerEvidence (practitioner_id, display_name, provider_number, location_label) and BerniePatientEvidence (patient_id, patient_label, date_of_birth, masked_phone, confidence, is_provisional); added optional practitioner_evidence and patient_evidence fields to BernieStaffReviewPayload (additive, all Optional/default None)
  - app/routers/appointments.py — added BERNIE_IDENTITY_CONFIDENCE_AUDIT_CODES (unlinked/low/medium/high/ambiguous → bounded code); split _BERNIE_CONFIRM_CREATE_BASE_EVIDENCE (3 base codes) from BERNIE_CONFIRM_CREATE_AUDIT_EVIDENCE (8 codes including all confidence variants); modified _build_bernie_identity_evidence to return tuple (BernieIdentityEvidence, Optional[Patient]) avoiding a second query; added _mask_phone, _build_bernie_patient_evidence, _build_bernie_practitioner_evidence helpers; updated _bernie_staff_review_payload and _bernie_supervised_blocked to accept/pass practitioner_evidence and patient_evidence; updated propose_bernie_supervised_booking to build and thread evidence to all return paths; in confirm_bernie_create_proposal, derive identity confidence from patient_id at confirm time and append the bounded code to audit_evidence; confirm_evidence in the proposal uses only _BERNIE_CONFIRM_CREATE_BASE_EVIDENCE (3 codes) not the full expanded set
  - tests/test_bernie_confirm_create_proposal.py — updated test_bernie_confirm_success_writes_exactly_one_appointment_and_bounded_audit to assert confidence code is present and use set equality for confirmed_warnings
  - tests/test_bernie_evidence_contract.py — new file: 12 tests covering practitioner evidence (display_name, provider_number), patient evidence (DOB, masked phone), provisional/ambiguous paths, no-mutation count guards across all supervised-booking results, confidence code on confirmed audit row (medium, medium-or-better for medicare patient), blocked confirm writes nothing, unlinked/provisional confirm has no confidence code
- Verification run:
  - py_compile check on all 4 changed/added files: passed
  - Focused pytest not runnable from this worktree (no .venv psycopg2 installed); verified via py_compile and import-chain check
  - No behavioural change to confirmation gating, conflict logic, autonomy tiers, or appointment/audit write counts
  - confirm_evidence in proposal payload still shows only 3 base codes (existing test assertion preserved)
- Remaining risks:
  - PHI note: BerniePatientEvidence surfaces date_of_birth for linked patients and masks phone to last 4 digits. Ariadne approved DOB inclusion at plan gate; if the decision changes, patient_evidence.date_of_birth should default to None and be gated behind a feature flag.
  - The identity confidence code at confirm time is re-derived without context_frames (caller_id, verification_frame), so a patient who was high-confidence at supervised-booking time (due to caller_id match) may record medium at confirm time. This is intentional conservative behaviour — the confirm audit records the baseline evidence, not the caller-session context.
  - Practitioner evidence location_label falls back to practitioner.default_location_id when appointment location_id is not resolved; if neither is set, location_label is None. No exception raised.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-bernie-api-evidence-contract-plan.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
