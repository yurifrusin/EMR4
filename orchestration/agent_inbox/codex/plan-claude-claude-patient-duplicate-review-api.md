# plan-claude-claude-patient-duplicate-review-api

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-patient-duplicate-review-api` |
| Status | pending_plan_review |
| Created | 2026-06-23 10:15 +1000 |
| Source HEAD | `0456387` |

## Plan Summary

GET /patients/duplicate-groups: practice-wide scan returning all duplicate patient groups with ref counts; in-Python bucketing by IHI/Medicare+IRN/name+DOB; frozenset deduplication so a pair matching multiple criteria appears once; 2 SQL batch queries for appointment and encounter counts; 3 new schemas; 12 tests; no migration, no mutation

## My Understanding

existing duplicate-candidates endpoint is a point-in-time check against supplied fields; this task needs a practice-wide audit that finds ALL duplicate groups across the entire patient registry in one call, with reference counts to help admin decide which record to keep

## Intended Surface / Boundary

app/schemas/patients.py (3 new schemas) + app/routers/patients.py (1 new GET endpoint before /{patient_id}) + tests/test_patient_duplicate_review.py (new, 12 tests); no taskpane, diary, command centre, migration, or existing endpoint changes

## Out Of Scope

patient merge/delete mutations, frontend UI, migrations, existing duplicate-candidates endpoint, billing/clinical/letter data, scheduled background scan

## Files I Expect To Edit

app/schemas/patients.py, app/routers/patients.py, tests/test_patient_duplicate_review.py

## Implementation Steps

1. Add PatientRefCounts/PatientWithRefCounts/PatientDuplicateGroup to schemas. 2. Add GET /patients/duplicate-groups router function before /{patient_id}: load all practice patients selecting key fields; bucket by IHI-norm, (medicare_norm+irn_norm), (first_lower+last_lower+dob); collect buckets with len>1; merge by frozenset(patient_ids) accumulating match_reasons; batch-count appointments and encounters for all group patient_ids in 2 queries; apply limit; return list[PatientDuplicateGroup]. 3. Write 12 tests.

## Visual / Behavioural Acceptance Checks

GET without token -> 401; empty practice -> []; two patients share IHI -> one group reason same_ihi; two share Medicare+IRN -> same_medicare_card_and_irn; two share name+DOB case-insensitively -> same_name_and_dob; practice B patients invisible to practice A; ref_counts reflect actual appointment and encounter rows; a pair matching IHI and Medicare+IRN appears in exactly one group with both reasons; limit caps output; a single patient with unique identifiers does not appear in any group

## Risks / Ambiguities

1. Large-practice performance: loading all patients in-Python is safe for typical GP practices (<3000 patients); 2. frozenset deduplication handles pairs correctly but a 3-way group (A,B,C) all sharing name+DOB is one group not three pairs; 3. same_phone_and_dob omitted from scan (high false-positive rate for shared household phones) — Codex should confirm this is correct; 4. encounter count query does not filter by practice_id (Encounter has no practice_id column — scoped implicitly via patient_id FK); confirmed this is safe

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
