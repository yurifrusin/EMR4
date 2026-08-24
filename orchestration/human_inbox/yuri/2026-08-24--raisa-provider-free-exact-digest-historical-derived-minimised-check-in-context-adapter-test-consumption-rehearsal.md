# Yuri closeout — historical-derived check-in adapter-test consumption

Date: 2026-08-24

Timestamp: 2026-08-24T14:17:06.1781891+10:00 (Australia/Brisbane)

Attention required: `no`

## Lay summary

We have now used one small piece of the historical Diary trove in actual
development work, but only after it had already been reduced to a six-change
structural time-lapse with no names, notes or real dates. The file was checked
against its fingerprint, read once, and turned into an entirely synthetic
check-in test. That test arrived the synthetic booking, produced its audit and
event, committed once and confirmed the result.

The source file is now locked against reuse by a local terminal marker. No
part of it was sent to DeepSeek, Gemini or any external service, and no private
row or replacement mapping was committed.

The honest limitation is that this first scenario mostly supplied traceable
provenance and timing. It exercised the existing check-in path successfully,
but it did not yet reveal a new check-in rule or drive several different
behavioral branches.

## Technical summary

- occupied source `517fda26c5c7f46397acc91976bc97b0be3778ef`;
- result SHA-256
  `48f12096fc319a896b7ef70e8dddbd99f8ea3151aa90212cfb030d710d5dad71`;
- one digest-before-parse read, no retry, zero archive reads;
- structural utility `6 events / 4 minutes / span 19 / 2 kinds / 1 subject / 1 resource`;
- one ten-step in-memory check-in adapter invocation;
- `Booked -> Arrived`, waiting area unchanged, one audit/event/commit/readback;
- 11 focused, 123 adapter/API Spine and 174 clockwork controls pass; and
- all four protected refs remain at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Four workflow lapses were caught and contained: an over-broad receipt evidence
field, PowerShell not stopping after one cached-diff warning, one wrong drafted
full commit ID caught by Git readback, and a direct latch edit rejected by the
clockwork owner. None touched the fixture twice or changed protected state.

## Place in Raisa and next work

This is the first evidence that an empirically derived scheduling time-lapse
can pass through the clockwork and exercise a real Raisa command adapter while
remaining private, local and non-authoritative.

Next I am conducting a read-only utility-and-gap review over the committed
sanitised result. It will establish which scenario axes actually influence
check-in behavior and freeze the smallest useful authored-synthetic matrix
before we consider any further historical-derived consumption. It will not
open the fixture or archive and needs no decision from you.
