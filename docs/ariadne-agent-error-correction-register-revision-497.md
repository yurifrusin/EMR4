# Ariadne agent error and correction register — revision 497

Date: 2026-08-19

Timestamp: 2026-08-19T02:08:27.5517949+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0575 records the recurring omitted UTF-8 decoding on a one-off read. AER-0576
records the first correction record's use of a descriptive stage that was not in
the canonical register enum. Both candidates failed before publication and no
canonical state changed.

Revision 497 contains 576 bounded incidents. All are corrected or contained;
none is open.

## Prevention

Closeout reads use the typed UTF-8 path. Incident-entry construction must source
constrained vocabulary from the canonical schema; the planned clockwork must
present enum choices instead of asking an orchestrator to reproduce them as free
text.
