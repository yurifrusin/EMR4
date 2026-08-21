# DeepSeek Harness controller convergence — lay and technical closeout

Date: 2026-08-21

## Lay summary

The diagnostic gear is now shaped for the bounded DeepSeek worker controller.
Good structured evidence produces the richer v2 diagnosis; missing or suspect
evidence preserves the safe older terminal and stops acceptance. No Harness or
provider was run in this tranche.

An important safety detail emerged: directly editing the old controller would
invalidate historical source-bound evidence. I kept it untouched and made the
new controller gear a clean descendant adapter for the next fresh attempt.

## Technical summary

- Candidate: `ba2e8b1c06acfe88f9f11afa1a58c1371d0cfa3c`.
- Exact valid sidecar selects v2; absent/invalid sidecars retain v1 and fail
  closed on closed coordinates.
- Wrapper and sidecar are confined beneath the disposable root; validated safe
  terminal is outside it and precedes cleanup.
- Consumed attempts 001-003 and the historical controller are byte-identical.
- 43 focused tests pass; all provider/process counts are zero.
- A pre-existing historical validator coupling remains and is the next narrow
  provider-free repair before attempt-004 admission.

No product, patient, appointment or clinical data was used. No production,
deployment, release, Pages or protected ref changed.
