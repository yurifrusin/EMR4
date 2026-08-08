# Ariadne agent error and correction register revision 108

Date: 2026-08-08

Status: accepted register correction

Revision 108 adds AER-0131 and brings the register to 131 bounded incidents.

## AER-0131 - PostgreSQL special form was schema-qualified

Behavior attempt 010 used the newly bounded query diagnostic and identified
the fixed `scenario_snapshot` site with SQLSTATE `42883`. Exact static readback
then found `pg_catalog.coalesce(...)` in the generated SQL. PostgreSQL treats
`COALESCE` as conditional SQL syntax, not as a namespace-callable function.

The repair removes only the invalid qualifier. All aggregate functions, row
conversion, ordering expressions, relations, digests and read-only transport
remain unchanged. An exact renderer test now forbids the invalid spelling and
requires one unqualified `COALESCE` for every snapshotted relation. Another run
remains ineligible pending deterministic checks and a fresh exact-HEAD veto.
