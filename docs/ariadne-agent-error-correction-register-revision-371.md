# Ariadne agent error and correction register — revision 371

Date: 2026-08-18

Timestamp: 2026-08-18T09:47:05+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 371 adds AER-0423. After the latch was correctly shortened below its
500-character bound, one focused assertion still expected the former prose
ordering `canonical fast profile passes 200` rather than the compact equivalent
`200-test canonical fast profile`.

The first correction retained `AER-0422/0423`, which failed the same fixture's
exact `AER-0423` prefix check. The final correction binds the valid compact
profile phrase, spells both incident prefixes explicitly within the bound and
reruns the complete register, latch, baton, plan and adapter packet before
staging.

## Population

- incidents: 423;
- corrected or explicitly contained: 423;
- open: 0;
- latest id: `AER-0423`.

No product route, database, provider, deployment or protected ref opened.
