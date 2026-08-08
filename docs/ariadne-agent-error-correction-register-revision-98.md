# Ariadne agent error and correction register revision 98

Date: 2026-08-08

Status: accepted register correction

Revision 98 adds AER-0119 and brings the register to 119 bounded incidents.

## AER-0119 — SQLSTATE lacked an allowlisted diagnostic coordinate

The SQLSTATE-only diagnostic behaved correctly and exposed `23502`, proving a
not-null violation without releasing raw PostgreSQL text. That class can still
arise from multiple fixed bootstrap relations and columns, so it was not yet
sufficient for a non-speculative repair.

The bounded extension admits `SCHEMA NAME`, `TABLE NAME` and `COLUMN NAME` only
when verbose psql supplies exactly one of each and the schema-qualified
relation/column pair belongs to the fixed bootstrap allowlist. An ambiguous or
unlisted coordinate releases only SQLSTATE. Raw messages, SQL and row values
remain discarded, and the evidence object remains recursively closed.

The next diagnostic run remains ineligible until deterministic tests and a
fresh exact-HEAD independent veto accept this narrower coordinate boundary.
