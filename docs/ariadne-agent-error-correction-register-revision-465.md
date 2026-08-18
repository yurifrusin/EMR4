# Ariadne agent error and correction register — revision 465

Date: 2026-08-18

Timestamp: 2026-08-18T23:01:58.2603497+10:00 (Australia/Brisbane)

Status: accepted register correction

## Correction

AER-0544 preserves one read-only bounded-path failure caused by assuming a
generic `register.json` basename. The live canonical filename was discovered
with `rg --files` and the exact `agent-error-register.json` path was then read.

Revision 465 contains 544 bounded incidents. All are corrected or contained;
none is open. No product, provider, deployment or protected-ref authority moves.
