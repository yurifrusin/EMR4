# Ariadne agent error and correction register — revision 350

Date: 2026-08-18

Timestamp: 2026-08-18T04:46:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 350 adds AER-0401. The first complete revision-349 register suite
passed 307 tests and failed only a newly authored assertion that required the
literal schema field name `recurrence_signature` inside correction prose that
already expressed the invariant as “recurrence grouping.”

The correction changes only that test to assert the stable semantic phrase,
then regenerates the derived report and reruns the complete register suite.

## Population

- incidents: 401;
- corrected or explicitly contained: 401;
- open: 0;
- latest id: `AER-0401`.

No product, data, provider, deployment or protected-ref authority changed.
