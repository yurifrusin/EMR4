# Ariadne agent error and correction register revision 125

Date: 2026-08-09

Status: bounded register correction candidate

Revision 125 adds AER-0150 and brings the register to 150 bounded incidents
with zero open incidents.

## AER-0150 — schema-qualified PostgreSQL special form in diagnosis wrapper

The first conjunct-level diagnosis wrapper derived an ephemeral PL/pgSQL body
that used `pg_catalog.coalesce(...)`. `COALESCE` is PostgreSQL expression
syntax, not a schema-qualified callable function. The disposable run therefore
did not preserve the expected BTR-E01/CF105 closure, and the wrapper correctly
refused to release any conjunct result.

No accepted SQL, contract, fixture or behavior evidence changed. Raw database
error text was not persisted. Docker daemon evidence identifies exact container
`a564b83a9b957a31a4f464c4d3e8fdc9158cf3a65f591c87fa22c0b797b0dee8`;
its destroy event is present, exact inspect reports absence and the owned
container population is zero.

The correction replaces only `pg_catalog.coalesce` with the valid `COALESCE`
special form and adds deterministic assertions over the derived diagnostic SQL
before any fresh execution. The failed attempt and its preexecution receipt
remain immutable. A distinct five-source preexecution receipt is required for
the corrected diagnosis.
