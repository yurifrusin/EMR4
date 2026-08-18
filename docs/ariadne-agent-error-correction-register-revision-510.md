# Ariadne agent error and correction register — revision 510

Date: 2026-08-19

Timestamp: 2026-08-19T02:36:52.6931250+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0589 records a latch-transition patch containing delete and add operations
for the same path. The patch engine rejected the whole payload before changing
the latch; one in-place update then passed.

Revision 510 contains 589 bounded incidents. All are corrected or contained;
none is open.

## Prevention

The clockwork publisher owns one target operation per projection. Until its
adoption, reject any patch manifest containing the same path more than once.
