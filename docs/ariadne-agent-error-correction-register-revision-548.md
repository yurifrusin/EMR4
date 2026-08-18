# Ariadne agent-error and correction register — revision 548

Date: 2026-08-19
Timestamp: 2026-08-19T08:41:24.0023767+10:00 (Australia/Brisbane)

## Revision scope

Revision 548 preserves AER-0636. The complete register suite reached its final new assertion and found that the test searched for the near-synonym `blocked` while the incident said `rejected by the desktop policy`. The exact control had worked; duplicated current prose caused the rerun.

The assertion now uses the preserved phrase. The register contains 636 incidents, all corrected or contained and none open. This is construction rerun seven and is reported separately from the zero-rerun steady-state replay.

## Prevention

Future adopted clockwork tests must validate structural incident fields and generated digests rather than repeating mutable current prose. Until adoption, exact current-register assertions are read back against the incident before the full suite runs.
