# Ariadne agent error and correction register revision 112

Date: 2026-08-08

Status: accepted register correction

Revision 112 adds AER-0135 and brings the register to 135 bounded incidents.

## AER-0135 - safe PL/pgSQL coordinate was not released

Attempt 013 passed the repaired serializable boundary and then stopped in
`BTR-E01` with PostgreSQL SQLSTATE `22P02`. The fixed scenario and SQLSTATE
proved a deeper data-format rejection but did not identify which internal
statement of the large accepted registration entry point failed.

The harness now admits only one uniquely parsed, scenario-allowlisted
schema-qualified function identifier and a bounded PostgreSQL internal line
number. Raw SQL, values, unrestricted identifiers and error prose remain
sealed. Another runtime attempt remains ineligible until deterministic checks
and a fresh exact-HEAD independent veto pass.
