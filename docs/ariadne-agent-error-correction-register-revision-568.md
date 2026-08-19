# Ariadne agent-error and correction register — revision 568

Date: 2026-08-19

Timestamp: 2026-08-19T22:05:00+10:00 (Australia/Brisbane)

## Revision scope

Revision 568 preserves AER-0659 and AER-0660 from the static repair closeout.
The first verification invocation combined report generation, pytest, status
and diff inspection despite the existing one-process-per-gate control. A later
narrow diagnostic supplied an invalid compound regular expression and failed
before reading any file.

Both lapses were read-only and caused no candidate, provider, Docker or product
state change. Their failed outputs are non-evidence. The correction freezes one
process result per remaining gate and fixed-string-only text search, regenerates
the deterministic report explicitly, and reruns the complete register test as
an isolated process.

## Population

- incidents: 660;
- corrected or explicitly contained: 660;
- open: 0;
- latest id: `AER-0660`.

Attempt 001 remains consumed. No occupied proof rerun is authorised, and no
product, ordinary-practice, provider, deployment, Pages or protected-ref
surface opened.
