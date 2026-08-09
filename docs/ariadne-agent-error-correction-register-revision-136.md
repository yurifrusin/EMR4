# Ariadne agent error and correction register revision 136

Date: 2026-08-09

Status: bounded register correction candidate

Revision 136 adds AER-0161 and brings the register to 161 bounded incidents
with zero open incidents.

## AER-0161 — repeated undefined-symbol classifier undercoverage

The first attempt-025 diagnostic replay reached the exact closed BTR-E02
failure and behavior-harness cleanup, but the inherited failure-024 allowlist
did not contain the remaining repository symbol. It raised
`single_allowlisted_undefined_symbol_missing` before emitting a durable result.
No raw PostgreSQL text or conclusion was released, and no PostgreSQL 16
container remained.

The corrected classifier retains the fixed allowlist first, then admits one
function name only when that name is present as a call in the exact BTR-E02 SQL
or accepted inert artifact, or one operator signature constrained to safe
PostgreSQL type words and operator glyphs. Raw text remains in memory and only
its digest is durable. This is recorded as a recurrence of AER-0158; later
diagnostics must not treat a historical failure allowlist as exhaustive.
