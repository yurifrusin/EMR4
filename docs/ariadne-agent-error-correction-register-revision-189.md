# Ariadne Agent Error and Correction Register — Revision 189

Date: 2026-08-08

Revision 189 appends `AER-0218` and does not rewrite any earlier incident.

`AER-0218` records that attempt 042 reached the BTR-I03 replay path and exposed
a forced-row-security policy gap. The coordinator could ordinarily read the
existing classified observation receipt, but PostgreSQL required UPDATE-policy
visibility for its contracted `FOR UPDATE` lock and therefore reported the row
as absent.

The correction adds an exact COORDINATOR lock-visibility policy whose
`WITH CHECK` repeats the bound predicate and ends in `AND FALSE`. It preserves
append-only receipt truth, empty coordinator direct-table DML, the typed body,
twenty behavior scenarios, authority, provider and product boundaries.
