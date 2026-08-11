# Ariadne agent error and correction register — revision 238

Date: 2026-08-11

Revision 238 closes AER-0271, adds AER-0272 and brings the register to 272
bounded known incidents.

## AER-0271 — CF-D1 failure telemetry was not actionable

The corrected telemetry passed its fresh exact-HEAD review and attempt 003
proved the control: the failure evidence named the exact C05 replay coordinate,
principal, isolation, closed expected and observed marker sets, and actual
started transaction counts while excluding raw database output. AER-0271 is
corrected.

## AER-0272 — CF-D1 used a non-native coordinator replay marker

Attempt 003 failed closed after the C05 race because CF-D1 expected and
allowlisted `RECEIPT_REPLAY`. The accepted PostgreSQL enum, replay function
branch and serial behavior harness all use `RECEIPT_REPLAYED`. The valid native
scalar was therefore excluded by the closed parser and appeared as no admitted
marker.

The bounded correction changes only the CF-D1 closed vocabulary, both replay
expectations and evidence schema to the native value. An exact regression
rejects the misspelling. Attempt 003 and its cleanup evidence remain immutable;
a distinct attempt 004 requires a fresh clean exact-HEAD review.
