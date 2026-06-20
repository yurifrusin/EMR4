# review-codex-codex-patient-identity-duplicates

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/patient-identity-duplicates` |
| Source Task | `codex-patient-identity-duplicates` |
| Status | integrated |

## Review Request

Codex worker Avicenna completed the patient identity duplicate foundation in a
disposable worker checkout. The orchestrator reviewed local commit `95a3d59`,
applied it into the integration worktree, and added one prefilter-normalisation
regression before final verification.

## Worker Completion Notes

- Files changed:
  - `app/models/patients.py` adds `medicare_irn` and an index for `ihi_number`.
  - `app/schemas/patients.py` exposes `medicare_irn` and a duplicate candidate
    response shape.
  - `app/routers/patients.py` adds search support for Medicare IRN/IHI, validates
    patient responses before commit, and exposes `GET /patients/duplicate-candidates`.
  - `alembic/versions/d4e5f6a7b8c9_add_patient_medicare_irn.py` adds the schema
    migration.
  - `tests/test_patients.py` adds focused regression coverage.

## Codex Review Notes

- Review result: Integrated with one orchestrator repair. The SQL prefilter now
  normalises formatted IHI, Medicare, and phone identifiers before matching, so a
  value such as `2950 123 456` can find a stored `2950123456` candidate.
- Follow-up required: Add taskpane UI fields and an explicit duplicate-warning
  workflow before this becomes routine patient-entry behaviour.
