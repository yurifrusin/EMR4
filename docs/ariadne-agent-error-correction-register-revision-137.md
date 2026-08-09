# Ariadne agent error and correction register revision 137

Date: 2026-08-09

Status: bounded register correction candidate

Revision 137 adds AER-0162 and brings the register to 162 bounded incidents
with zero open incidents.

## AER-0162 — UUID `MIN_FIELD` aggregate lowering defect

Attempt 025 proved the interval repair was reached but then failed BTR-E02 with
the same undefined-function SQLSTATE. The corrected repository-bounded
diagnosis identified `pg_catalog.min`; typed source reconciliation showed that
two renderer-owned `MIN_FIELD` nodes now operate on UUID stream IDs while the
generic lowering assumed the aggregate existed for every admitted type.

Renderer 2.0.12 retains aggregate minimum for the two bigint checkpoint uses,
lowers the two UUID uses to deterministic ascending `NULLS LAST LIMIT 1`
selection, rejects all other result types and adds a hostile recognizer rule
against UUID aggregate regression. Fresh parse characterization, exact proof,
behavior parent rebind and independent veto remain mandatory before attempt
026.
