# Ariadne agent error and correction register — revision 324

Date: 2026-08-17

Timestamp: 2026-08-17T08:32:15.8209574+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 324 records 373 bounded known incidents. No incident is open.

- AER-0373 records a stale maintenance-test contract found by the strengthened
  canonical profile. Three assertions still named the accepted route-readiness
  node at Continuity 307 / Compass 289 and expected HTTP convergence next,
  although HTTP route convergence is already accepted at Continuity 308 /
  Compass 290 and disposable PostgreSQL integration is next.
- Only `tests/test_current_baton_consistency.py` is corrected. It now binds the
  exact accepted HTTP node/source and current next-work boundary while retaining
  all historical lineage, protected-ref and closed-surface assertions.
- Future Continuity/Compass closeouts that advance the Current Baton must run
  this test and update its terminal-node expectations in the same candidate.

## Boundary

This repair changes no product source, API, schema, database behavior,
authority, provider posture, deployment state or protected ref.
`docs/branding/` and every unrelated untracked file remain preserved.
