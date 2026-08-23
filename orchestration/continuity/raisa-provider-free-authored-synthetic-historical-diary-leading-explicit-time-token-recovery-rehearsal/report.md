# Raisa provider-free authored-synthetic historical Diary leading explicit time-token recovery rehearsal — report

Date: 2026-08-24

Timestamp: 2026-08-24T07:59:22.5874518+10:00 (Australia/Brisbane)

Result: `accepted_parser_recovery_candidate`

Reviewed source: `5a3c589873a104e948e65eaadacd2397f0621a3b`

## Conclusion

The narrow parser works and is ready for one separately planned local
measurement. It recognizes only a complete valid time at the beginning of an
already separated cell segment, requires an allowlisted ASCII separator and a
non-empty payload, and rejects embedded, attached, invalid, date-like, phone
and email/contact cases.

The minute applies only to the payload in that same segment. A later segment is
not forward-filled. The time token and its separator are removed before
normalization and private HMAC token construction: clocked and unclocked
versions of the same authored-synthetic payload produce identical private
content and cell tokens.

## Integration clarification

Focused review found that the inherited aggregate decision still demanded
three main-story anchors even if valid leading tokens supplied sufficient
explicit time evidence. Before any historical access, the admission rule was
clarified so story anchors and valid leading tokens are the only two explicit
time-source forms. Distinct minutes, a positive interval, mapping ratio, stable
linkage, adjacent motion and zero leakage remain independently mandatory.

An authored-synthetic leading-token-only timeline then reached
`locally_restricted_candidate` with 11 token observations, four distinct
minutes, a 15-minute mode, four stable links and one adjacent change. This does
not predict that the historical slice will pass.

## Verification and boundaries

All 29 focused controls and all 219 controls across 23 historical-Diary test
files pass, together with Ruff, compileall, the filesystem-enumeration trap,
source checks and `git diff --check`. Historical archive enumerations, metadata
reads, content reads, retries, provider/model calls, product effects and source-
value leakage were all zero.

No historical-derived reusable artifact exists. The first-use gate remains
closed. The strongest result is this provider-free parser candidate, not an
anonymity, product, provider or production claim.

## Next work

Freeze one fresh fixed-slice local measurement at a new ignored attempt root.
It may perform one metadata bind and one 80-document content run with no retry,
using the accepted 1,800-second Word containment and cleanup boundary. It may
retain only generic aggregate evidence and cannot open first use.
