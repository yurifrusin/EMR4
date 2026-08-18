# Ariadne agent error and correction register — revision 501

Date: 2026-08-19

Timestamp: 2026-08-19T02:14:20.9518461+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0580 records the remaining stale whole-report fixture: AER-0577 created a
new recurring peer-link pattern that required both explicit classification and
exclusion from a second exhaustive fixture. All other revision-500 checks had
passed. AER-0575 through AER-0579 remain contained.

Revision 501 contains 580 bounded incidents. All are corrected or contained;
none is open.

## Prevention

The clockwork reducer must emit recurrence classification and exhaustive
residual checks from the same generated pattern set, so one new recurrence
cannot require two manually synchronized fixtures.
