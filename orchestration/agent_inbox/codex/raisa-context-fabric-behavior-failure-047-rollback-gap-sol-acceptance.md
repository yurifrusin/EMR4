# Sol acceptance: behavior attempt 047 rollback-gap recovery

Date: 2026-08-08

Result: `accepted_for_exactly_one_behavior_attempt_048`

Sol accepts candidate `0cf41c25ea55d2533f185e7db6efabe91bb53e95`
after the fresh, clean, read-only Gemini 3.6 Flash/high veto returned `pass`.
The immutable attempt-047 failure remains sealed at SHA-256
`bc577de88b7acafac72828bb2ddae898181886d08676c8802acf84ef925ebd63`.

Accepted correction is harness-only: BTR-B03's rollback observer now uses the
first contiguous source position for its precondition, transition and retention
probe. The behavior contract remains SHA-256
`43b25bd7509439f069643dcb0ae8e62e27002834fe9903d84e7478486b452615`;
the inert SQL and manifest remain SHA-256
`dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`
and `2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`.

The first verifier's `revision_required` receipt is retained: it found a
worktree-local interpreter assumption and canonical-formatting defect. Both are
repaired in the accepted descendant and the second verifier repeated the full
suite successfully.

Authority is limited to exactly one no-argument execution of the existing
provider-free disposable PostgreSQL behavior harness as attempt 048, with
authored-synthetic fixtures, exact alias backup/restoration, bounded evidence,
owned-container cleanup and no same-attempt rerun. No operational database,
application/runtime wiring, patient/clinical/product data, provider call,
deployment, Pages rebuild or protected-ref movement is authorised.
