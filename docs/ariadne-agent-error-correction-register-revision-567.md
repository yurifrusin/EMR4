# Ariadne agent-error and correction register — revision 567

Date: 2026-08-20

Timestamp: 2026-08-20T00:31:00+10:00 (Australia/Brisbane)

## Revision scope

Revision 567 preserves AER-0657. The first check-in relay-free cleanup Gemini
manifest put a database-backed A5.1 runtime suite inside the provider-free
`--noconftest` runner. The suite's `practice` fixture therefore could not be
resolved, C03 returned 36 setup errors and the otherwise substantive passing
review correctly returned `revision_required`. The candidate remained unchanged
and clean.

The corrected manifest removes that suite, substitutes provider-free pure
route-convergence and continuity tests, passes the exact corrected command
locally and receives one fresh corrected Gemini `pass` on the unchanged
candidate. The register now contains 657 incidents, all corrected or contained
and none open.

## Prevention

Every provider-free verifier manifest now requires a complete fixture-graph
portability classification before dispatch. A test depending on
`tests/conftest.py` or database fixtures is rejected from the provider-free
command, not silently admitted into a no-database tranche.
