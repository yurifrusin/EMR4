# Ariadne agent error and correction register — revision 198

Date: 2026-08-08

Revision 198 adds AER-0232 and brings the register to 232 bounded incidents.

## AER-0232 — frame-mask domain contradicted nullable conflict semantics

Immutable behavior attempt 045 again stopped at `BTR-I02` with SQLSTATE
`23502`, but the accepted bounded parser correctly found no table-column
coordinate. Static reconciliation proves that the effective `frame_mask` domain
is globally `NOT NULL` while the admission relation, conflict-row invariant and
both conflict insert nodes require a typed null affected-frame mask. The bounded
correction relaxes only effective domain nullability, retaining the range check
and required column-level presence.
