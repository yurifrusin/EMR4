# Ariadne agent error and correction register — revision 329

Date: 2026-08-17

Timestamp: 2026-08-17T09:07:59.9420394+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 329 records 378 bounded known incidents. No incident is open.

- AER-0378 preserves four excluded closeout invocations with a wrong pytest
  envelope: two fixture-dependent appointment/API profiles used
  `--noconftest`, then the maintenance profile was run directly and once
  through the serial wrapper while still suppressing conftest. They supplied
  no candidate evidence.
- The exact current five-file API Spine/Diary profile was rerun through
  `scripts/ariadne_serial_pytest.py` with the repository conftest and shared
  PostgreSQL-schema lock. All 37 API Spine/Diary tests and all 130 maintenance
  tests passed.
- The post-closeout workflow review will assess a profile manifest carrying an
  explicit `conftest_required` property so the launcher can reject this misuse
  before pytest starts.

## Boundary

No candidate source, product state, database content, provider, deployment
state or protected ref changed. `docs/branding/` and every unrelated untracked
file remain preserved.
