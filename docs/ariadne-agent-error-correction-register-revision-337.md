# Ariadne agent error and correction register — revision 337

Date: 2026-08-17

Timestamp: 2026-08-17T15:20:00+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 337 retains 384 bounded known incidents. No incident is open.

- AER-0384 records a recurrence of AER-0378: Sol chained a failed register
  validation to direct repository pytest, allowing tests to start without the
  required explicit serial launcher.
- The run was stopped and excluded. It grants no passing evidence.
- Register validation and the exact register tests are now separate commands;
  pytest runs only through `scripts/ariadne_serial_pytest.py` after validation
  succeeds.

## Boundary

The correction changes only local verification sequencing. It grants no
product, data, provider, database, deployment, release, Pages or protected-ref
authority.
