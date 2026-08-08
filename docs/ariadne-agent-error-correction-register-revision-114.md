# Ariadne agent error and correction register revision 114

Date: 2026-08-08

Status: accepted register correction

Revision 114 adds AER-0137 and brings the register to 137 bounded incidents.

## AER-0137 - alternate PL/pgSQL function-name form was not admitted

Attempt 014 repeated `BTR-E01` / `22P02` with zero admitted scenarios and exact
cleanup, but the reviewed coordinate parser released no coordinate. The parser
required the schema prefix even though PostgreSQL may display a called
function unqualified in its PL/pgSQL context.

The parser now admits only the exact allowlisted function name with either the
explicit `emr4_context_fabric` prefix or no prefix, normalizing both to the
same schema-qualified evidence identifier. It still rejects every other
schema, function and ambiguous shape. Another attempt remains closed until
fresh deterministic and independent acceptance.
