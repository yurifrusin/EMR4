# Behavior/transaction JSON key-set order parent rebind

Date: 2026-08-09

Status: six-parent behavior candidate rebound; behavior runtime closed pending
deterministic gate and fresh Gemini 3.6 Flash/high veto

## Preserved predecessor

Behavior attempt 026 remains immutable failure evidence. It stopped at
`BTR-E02` with exact repository SQLSTATE `CF103` after zero of twenty scenarios
completed. The accepted recovery changes only deterministic expected-array
ordering for seven fixed `JSON_KEYS_EXACT` guards. It does not weaken exact key
membership or alter any scenario.

## Exact six-parent rebind

The behavior contract now binds:

1. accepted parse evidence source
   `19cc3fd6e79588605e3a315236cdd1e688433e17` through the exact accepted-source
   ledger;
2. renderer source `f620f31e4576003855afe824a385a86badf77120` and inert
   artifact
   `sha256:f4479c772f144973c1a1f373e16e0bcb3543fea6128c8054a282316ce5d02714`;
3. the same renderer source and render-manifest file SHA-256
   `sha256:d414fb3f0c9d5b8075e913f5608b6146b7b9ee43eb849c9272ccf48df3a2c706`;
4. unchanged structural contract source
   `338c30ddb01561ce97a4b9837317e771b555c221` at SHA-256
   `sha256:648acf79c86d16bf7fcd9ad1f88dcab5bc4aded01c4e0084f66c6c36b4adeca1`;
5. unchanged function/trigger body source
   `987f64a9f68c8dec2b99d5d39aa74e28411a82fa` at SHA-256
   `sha256:78721338810c87df825bdf3a9d1e010cb3cdd04dcb7898badd127b76fec174d2`;
   and
6. the unchanged synthetic prerequisite contract at SHA-256
   `sha256:313d283b4a53c08a34b65f7c932457010cc9317c87a3bfe6a1b9dc218ba220b7`,
   now source-bound to the accepted parse evidence commit.

The resulting canonical behavior contract SHA-256 is
`sha256:073f30dd7725bcc9a4ee0da53793535b843b16c05326cbb7e5ff16fcfd6836cc`.

## Scenario and authority invariants

The scenario order, scenario objects and category coverage remain exactly
twenty ordered cases in `6/4/3/4/3`. Their canonical population SHA-256 remains
`sha256:eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`.
No role, fixture, SQLSTATE, effect, readback, containment, cleanup or claim
boundary changed.

Attempts 001-026 remain immutable. Only after the complete deterministic and
hostile packet plus one fresh exact-HEAD Gemini 3.6 Flash/high veto pass may
attempt 027 run once in a newly owned `postgres:16-bookworm` container with
`--pull=never`, `--network=none`, no ports or mounts and exact-ID cleanup.

## Deterministic packet recovery

The first complete packet correctly stopped on one repository test defect:
the historical attempt-025 preservation test compared its immutable bytes to
the optional mutable current-evidence path merely because that path existed.
The mutable path correctly held newer attempt 026, so existence could not
establish equality. AER-0165 preserves the failure. The test now parses the
mutable evidence and compares bytes only when the exact attempt identity also
matches.

The repaired complete inherited-plus-current packet collects and passes 495
tests. Ruff check, Ruff format and Git diff checks also pass. This repair
changes no SQL, contract, scenario or runtime behavior.

## Independent veto

Fresh Gemini 3.6 Flash/high review at exact clean source
`e44740c0c626b9c5daccafbfbf9ce4994ad92f4e` passed all twenty-one substantive
challenges and independently passed all 495 tests. Review receipt SHA-256 is
`sha256:8cf05c4e575f41cd5d59fb80971a71850e4de722d6e4469081357406ed32130a`.
The review worktree remained clean and unchanged before and after review, and
no Docker or runtime harness was executed.

The first predispatch receipt had already failed closed before any model call
because Sol incorrectly used handoff-alignment fields for the non-protected
review worktree. AER-0166 preserves that zero-call orchestration error. The
replacement five-source receipt and separate exact-worktree preflight passed
before the one accepted verifier launch.

## Closed surfaces

No applied migration, operational credentials or persistence,
outbox/feed/watcher/listener/source access, application/API/Diary wiring,
patient, clinical, product or protected data, provider/model call,
command/product write, deployment, production, release, Pages, protected-ref
movement or `docs/branding/` access is opened.
