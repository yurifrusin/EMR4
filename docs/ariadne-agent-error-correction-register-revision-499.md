# Ariadne agent error and correction register — revision 499

Date: 2026-08-19

Timestamp: 2026-08-19T02:11:29.1303250+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0578 records a provider-free test command that incorrectly carried the
ordinary pytest `-q` flag. The launcher rejected it before collection; no test
or repository mutation ran. AER-0575 through AER-0577 remain the contained
UTF-8, enum and one-way-link closeout attempts.

Revision 499 contains 578 bounded incidents. All are corrected or contained;
none is open.

## Prevention

Verification commands must be generated from a typed launcher profile rather
than assembled from remembered pytest conventions. The profile owns its valid
arguments and rejects unsupported options before execution.
