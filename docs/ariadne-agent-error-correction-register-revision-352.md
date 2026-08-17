# Ariadne agent error and correction register — revision 352

Date: 2026-08-18

Timestamp: 2026-08-18T05:24:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 352 adds AER-0403. The second final closeout packet passed every
structural closeout and latch assertion but one newly authored baton fixture
expected “11 new checks” while the accepted Current result row says “Eleven
new checks.” After that correction, the same still-unaccepted fixture exposed
one more wording assumption: it required “arrival/check-in” while the row
described generic `Arrived` plus A5.1 check-in without the compound label.
Publication remained stopped after both packets.

The correction uses the exact durable count wording and makes the accepted row
explicitly name the already-described arrival/check-in seam before
regenerating the report and rerunning the same packet.

## Population

- incidents: 403;
- corrected or explicitly contained: 403;
- open: 0;
- latest id: `AER-0403`.

No product, data, provider, deployment or protected-ref authority changed.
