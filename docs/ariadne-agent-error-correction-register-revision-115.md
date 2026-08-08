# Ariadne agent error and correction register revision 115

Date: 2026-08-08

Status: accepted register correction

Revision 115 adds AER-0138 and brings the register to 138 bounded incidents.

## AER-0138 - table-composite projection order diverged from relation order

Attempt 015 released the exact allowlisted function coordinate for the
continuing `BTR-E01` / `22P02` failure and again proved exact cleanup. Static
reconciliation then found that the complete binding projection assigned a UUID
stream coordinate into the positional bigint binding-revision slot. The same
class of ordering drift existed in aggregate-alias projections.

The authoritative function-body projection lists now follow the physical
relation-composite order. Renderer `2.0.5` independently compares every
non-system positional row assignment with the complete physical user-column
order and rejects an authored hostile swap before rendering. Historical
runtime evidence remains unchanged; fresh review and both disposable
PostgreSQL rehearsals are required for the corrected chain.
