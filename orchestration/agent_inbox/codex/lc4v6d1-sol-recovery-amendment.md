# LC4V6D1 Sol Recovery Amendment

Date: 2026-07-16

DeepSeek V4 Flash/high candidate commit `67f232a1` (integrated historically as
`565643f8`) returned `DECISION: pass` after 157 focused tests. Sol rejected that
self-pass as acceptance evidence and adopted the source only as an untrusted
candidate under the recovery lease.

The defects were conceptual, so no Flash correction loop was opened:

1. resize `duration_minutes` and normalized earliest/latest values were not
   observed or scored, despite lossless normalization being an explicit D1
   requirement;
2. the unknown-name mapping test looked for a non-existent
   `entity_semantics["practitioner_name"]` value and therefore passed
   vacuously;
3. the safety counter returned true for every non-clarifying case without
   requiring policy-contract compliance; and
4. the fixture hash covered only `cases`, not the schema/reference/provenance
   envelope, while fail-closed validation was weaker than the frozen contract.

Sol replaced the runner/tests with exact envelope validation, a whole-fixture
canonical hash, normalized time/duration observations, mismatch-field evidence,
non-vacuous final-practitioner mapping checks, and policy-exact safety. The
worker artifact and original candidate commit remain preserved. Parser and
policy runtime code were not changed.

Gemini's independent pre-baseline semantic review at `2f1c4e59` remains valid:
it reviewed the authored contract/fixture, not the rejected runner, and returned
`DECISION: pass` with no authoring corrections.
