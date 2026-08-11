# Ariadne agent error and correction register — revision 239

Date: 2026-08-11

Revision 239 closes AER-0272. The register remains at 272 bounded known
incidents.

## AER-0272 — CF-D1 used a non-native coordinator replay marker

A genuinely fresh Gemini 3.6 Flash/high review passed at exact source
`43f168f3d5d1f71ec0f9071c40fadf14b6107621` with 254 tests and zero Docker,
database, provider, product or external-network operations. It independently
confirmed that the accepted PostgreSQL enum, exact replay return branch and
serial behavior harness all use `RECEIPT_REPLAYED`; CF-D1 alone used the
misspelling.

The review found no change to accepted SQL, contracts, race topology, fixture,
role, isolation, transaction, overlap, wait proof, cleanup or claim boundary.
The exact vocabulary correction and attempt-004 isolation are accepted, so
AER-0272 is corrected.
