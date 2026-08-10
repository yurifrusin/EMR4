# Context Fabric behavior failure 047 — rollback gap fixture diagnosis

Date: 2026-08-08

Status: repository-only diagnosis complete; corrected candidate remains runtime
closed

Immutable attempt 047 evidence SHA-256
`bc577de88b7acafac72828bb2ddae898181886d08676c8802acf84ef925ebd63`
records one bounded BTR-B03 failure. The scenario expected the final fixed
rollback injection `P0001`, but instead reached SQLSTATE `22012` in the
harness's typed result assertion. Cleanup of exact owned container
`4ff69a925106cf9d14c929d76173067d04feb4580e173e7c6d3c3240c8a7b2cc`
completed and exact-ID absence was independently confirmed. No rerun occurred.

The artifact behaved correctly. The failed fixture registered the rollback
observer at checkpoint zero, then precommitted only a primary admission at
source position two and immediately requested transition of position two. The
artifact's durable continuity rule correctly treated `2 > 0 + 1` as a coverage
gap and selected `REBASE_APPLIED`. The harness had asserted
`RECEIPT_APPLIED` by dividing by zero on any other result, so `22012` occurred
before the intended `P0001` injection.

The bounded recovery changes only the rollback fixture: precommit the primary
at the already available source position one, request transition of position
one and verify retention of that position-one primary after injected rollback.
This tests the original BTR-B03 contract—a successfully applicable coordinator
transition whose effects are wholly rolled back—without crossing a deliberate
coverage gap. The twenty-scenario behavior contract, expected result and
SQLSTATE, generated SQL, parse proof, roles, privileges, containment and claim
boundaries remain unchanged.

No new PostgreSQL run is authorised until this harness-only repair passes
deterministic tests and a fresh exact-HEAD independent veto.
