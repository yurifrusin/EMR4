# Ariadne agent error and correction register revision 100

Date: 2026-08-08

Status: accepted register correction

Revision 100 adds AER-0122 and brings the register to 122 bounded incidents.

## AER-0122 — expected verbose coordinate fields were unavailable

Failure evidence 006 retained `23502` and selected `coordinate_status=missing`.
The client path did not emit separate labelled schema/table/column lines, so the
first coordinate parser could not use them.

The bounded fallback matches only the fixed English PostgreSQL `23502` header
for a not-null violation, captures its lowercase quoted table and column tokens
and releases them only if the pair resolves through the existing bootstrap
allowlist. It is not a general error-message parser. Unmatched, ambiguous or
unlisted headers still release no identifier.

The fallback remains runtime-closed until deterministic checks and a fresh
exact-HEAD independent veto pass.
