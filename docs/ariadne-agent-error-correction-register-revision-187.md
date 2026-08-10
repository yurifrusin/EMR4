# Ariadne Agent Error and Correction Register — Revision 187

Date: 2026-08-08

Revision 187 appends `AER-0216` and does not rewrite any earlier incident.

`AER-0216` records that behavior attempt 040 correctly localized BTR-E04 to
its pending-obligation predicate. The predicate filtered only on an
authored-synthetic observer identifier that the closed bootstrap deliberately
reuses in a beta-practice isolation fixture. It therefore counted the beta
preseed together with BTR-E04's newly admitted alpha obligation.

The correction binds the BTR-E04 and BTR-I03 obligation readbacks to the exact
alpha practice and stream. It preserves the cross-practice isolation fixture,
database artifact, body, behavior contract, scenario population, relation
allowlist, provider boundary, product boundary and protected refs.
