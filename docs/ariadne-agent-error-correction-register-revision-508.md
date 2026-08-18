# Ariadne agent error and correction register — revision 508

Date: 2026-08-19

Timestamp: 2026-08-19T02:28:34.5235672+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0587 records four stale current-position sentinels after the valid
Continuity 324 / Compass 306 advance: live baton values, the previous-next-
tranche boundary and the global Compass node literal. All clockwork, broker,
latch and dedicated Continuity checks passed.

Revision 508 contains 587 bounded incidents. All are corrected or contained;
none is open.

## Prevention

Every valid Compass advance must derive the dedicated node, live baton and
global current-position fixtures from the prospective projection before
canonical publication.
