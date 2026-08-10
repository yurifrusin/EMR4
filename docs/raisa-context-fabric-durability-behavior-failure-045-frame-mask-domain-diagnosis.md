# Context Fabric behavior failure 045 — frame-mask domain diagnosis

Date: 2026-08-08

Immutable attempt 045 again stopped at `BTR-I02` with PostgreSQL SQLSTATE
`23502`. The new bounded parser correctly released `coordinate_status=missing`:
this was not a table-column not-null violation, and raw PostgreSQL text remained
sealed. The owned container was removed and exact-ID absence was verified.

Repository-only reconciliation proves the contradiction. The accepted
`frame_mask` domain is globally `NOT NULL`, while the admission relation and its
conflict-row shape deliberately require `affected_frame_mask` to be nullable.
Both conflict insert nodes therefore lower their intended value as
`NULL::emr4_context_fabric.frame_mask`; PostgreSQL rejects that typed null before
a table/column coordinate exists.

The bounded correction is analogous to the already accepted digest-domain
recovery: relax only the *effective* frame-mask domain nullability while retaining
the `0..3` range check and every required column-level `NOT NULL`. The immutable
structural and function-body parents remain unchanged. This diagnosis opens no
additional database run or product/runtime/provider authority.
