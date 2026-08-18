# Ariadne agent error and correction register — revision 381

Date: 2026-08-18

Timestamp: 2026-08-18T13:45:34.2675963+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 381 adds AER-0433 and AER-0434. The first continuity-updater run
omitted inherited contract paths from the new node's typed evidence buckets,
so Compass validation stopped after writing draft revision 317/299. The
updater was repaired and rerun idempotently; its built-in Compass validation
then passed.

Sol next guessed a nonexistent optional Compass-test filename. Pytest exited
before collection. That command is excluded from acceptance; the passing
updater validation and exact new continuity test are the admitted gates.

Neither incident changed product source, the accepted reviewed candidate, a
provider call or any ref.

## Population

- incidents: 434;
- corrected or explicitly contained: 434;
- open: 0;
- latest id: `AER-0434`.

No product data, deployment, release, Pages or protected-ref action occurred.
