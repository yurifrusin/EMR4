# Ariadne agent error and correction register — revision 511

Date: 2026-08-19

Timestamp: 2026-08-19T03:14:56.1441530+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0590 records a repeated direct-path invocation of a repository Python
validator in the first Gemini verifier manifest. The verifier-worktree preflight
rejected the command before any provider call. The manifest was corrected to
the package-module launcher, the same preflight passed, and the exact candidate
then received a clean Gemini 3.7 Flash/high veto review.

Revision 511 contains 590 bounded incidents. All are corrected or contained;
none is open.

## Prevention

Generate verifier commands from the typed clockwork command vocabulary. Until
that projection becomes authoritative, every Python file under `scripts/` must
be invoked with `python -m`, and verifier preflight must reject any exception
before provider dispatch.
