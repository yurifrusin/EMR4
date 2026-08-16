# Ariadne agent error and correction register — revision 326

Date: 2026-08-17

Timestamp: 2026-08-17T08:52:23.3569291+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 326 records 375 bounded known incidents. No incident is open.

- AER-0375 preserves the corrected occupied delete-confirm HTTP/PostgreSQL
  harness stop after catalogue admission. DHI-S01 through DHI-S06 had run, but
  DHI-S07's manual cross-practice helper called the evidence minter through the
  delete adapter module even though that module does not export the primitive.
- The released failure evidence remained sanitized and schema-valid. Both the
  occupied lifecycle and one bounded traced diagnostic lifecycle verified
  exact container/network cleanup; independent label-filtered postflight found
  zero surviving owned resources.
- The repair imports the minter directly from the already source-bound
  `bernie_turn_evidence` module and adds a provider-free regression that
  constructs the complete cross-practice body before another occupied run.

## Boundary

No product source, API, schema, command meaning, database authority, provider,
deployment state or protected ref changes. `docs/branding/` and every unrelated
untracked file remain preserved.
