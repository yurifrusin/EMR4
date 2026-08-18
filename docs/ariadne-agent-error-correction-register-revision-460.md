# Ariadne agent error and correction register — revision 460

Date: 2026-08-18

Timestamp: 2026-08-18T22:50:55.0803573+10:00 (Australia/Brisbane)

Status: accepted register correction

## Scope

Revision 460 adds AER-0530 through AER-0538 for the bounded read-only ordinary-
practice canonical check-in admission-readiness review. The register now
contains 538 preserved incidents; every incident is corrected or contained and
none is open.

## Added incidents

- AER-0530 preserves the stale completed-predecessor latch transition fixture.
- AER-0531 corrects a one-off canonical-LF hash projection that classified
  normal CRLF as bare CR before normalization.
- AER-0532 through AER-0534 preserve three fail-closed static evidence anchors
  that did not respect split Python strings or Markdown line wrapping.
- AER-0535 preserves two plan-test substring assertions that crossed intentional
  Markdown wraps; normalized semantic assertions now pass.
- AER-0536 through AER-0538 preserve three read-only `rg` invocations that used
  unverified nonexistent explicit path operands.

## Correction and claim boundary

The exact readiness reviewer now passes its no-write and release runs, rejects
at least 120 hostile mutations, and the focused review plus latch packet passes
66 checks. These corrections change no product source, configuration, route,
database, API contract or admission posture. They do not enable a practice,
open a provider or move protected refs.
