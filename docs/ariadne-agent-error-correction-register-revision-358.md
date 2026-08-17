# Ariadne agent error and correction register — revision 358

Date: 2026-08-18

Timestamp: 2026-08-18T07:00:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 358 adds AER-0409. The third complete register-focused run failed one
new recurrence assertion because the prior correction inferred grouping from
`recurrence_signature` alone. The report builder actually groups by origin,
category, role, resource ID and signature. AER-0407 and AER-0408 therefore do
not join the older composites whose resource IDs differ.

The correction reads and asserts the exact derived composites, retains only
the genuinely new asymmetric-peer group, advances final totals, regenerates
the report and requires a fresh complete run.

## Population

- incidents: 409;
- corrected or explicitly contained: 409;
- open: 0;
- latest id: `AER-0409`.

No product, data, provider, deployment or protected-ref authority changed.
