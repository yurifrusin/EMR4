# Ariadne agent error and correction register — revision 359

Date: 2026-08-18

Timestamp: 2026-08-18T07:11:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 359 adds AER-0410. The fourth complete register-focused run failed one
residual-list equality because the population-fixture signature was filtered
from the actual side while its unchanged exact expected row remained. The next
displayed detached-verifier rows were identical; their apparent mismatch was
only the one-row shift.

The correction removes that one unpaired exclusion, advances final totals,
regenerates the report and requires a fresh complete run.

## Population

- incidents: 410;
- corrected or explicitly contained: 410;
- open: 0;
- latest id: `AER-0410`.

No product, data, provider, deployment or protected-ref authority changed.
