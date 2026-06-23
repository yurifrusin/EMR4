# review-claude-claude-patient-duplicate-review-api

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-patient-duplicate-review-api` |
| Status | integrated |

## Review Request

Patient duplicate review API ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/schemas/patients.py` — added `PatientRefCounts`, `PatientWithRefCounts`, `PatientDuplicateGroup` after the existing `PatientDuplicateCandidate` schema
  - `app/routers/patients.py` — added `Appointment` import; added `PatientRefCounts`, `PatientWithRefCounts`, `PatientDuplicateGroup` to schema import; inserted `GET /patients/duplicate-groups` endpoint between `duplicate-candidates` and `/{patient_id}` (static-before-dynamic ordering); encounter count query filters by `practice_id` (corrected from plan — `Encounter` does have a `practice_id` NOT NULL column)
  - `tests/test_patient_duplicate_review.py` (new) — 13 tests (plan stated 12; one extra read-only assertion test added)

- Verification run:
  - `py_compile` on `app/schemas/patients.py`, `app/routers/patients.py`, `tests/test_patient_duplicate_review.py`: all OK
  - `pytest tests/test_patient_duplicate_review.py -v --tb=short -p no:randomly`: **13 passed**
  - Full `pytest tests -q --tb=short -p no:randomly`: running in background (notified on completion)
  - `git diff --check`: CRLF warning on packet .md only (pre-existing), no whitespace errors in source

- Remaining risks:
  - Plan risk #4 was incorrect: `Encounter` DOES have a `practice_id` NOT NULL column. The endpoint now filters by `practice_id` in both the appointment and encounter count queries. This is more correct than the plan stated.
  - `same_phone_and_dob` criterion intentionally omitted from the scan (high false-positive rate for shared household phones). Codex confirmed this in the plan review.
  - In-Python bucketing: for practices with very large patient registries (>10k patients), loading all patients into memory could be slow. For a typical GP practice this is safe. A future optimisation could use SQL GROUP BY + HAVING COUNT(*) > 1 for each criterion and only load the candidate rows.
  - The `limit` parameter caps groups, not patients. A single group could contain many patients (e.g. a practice that entered the same patient 50 times). No per-group patient cap is applied; Codex should decide if one is needed.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-patient-duplicate-review-api.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
