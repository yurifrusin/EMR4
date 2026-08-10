# Context Fabric frame-mask domain nullability recovery

Date: 2026-08-08

Status: bounded provider-free recovery candidate; no runtime acceptance yet

## Observed contradiction

Immutable behavior attempt 045 stopped at `BTR-I02` with SQLSTATE `23502` and
no table-column coordinate. Repository-only diagnosis proves that the effective
`frame_mask` domain was globally `NOT NULL`, while the admission relation and
its conflict-row invariant deliberately require a nullable
`affected_frame_mask`. Both conflict insert paths therefore evaluated an
intentional `NULL::emr4_context_fabric.frame_mask` that PostgreSQL rejected
before table insertion.

## Exact correction

Renderer version `2.0.19` adds the sealed
`RELAX_FRAME_MASK_DOMAIN_NULLABILITY` recovery operation. It changes only the
effective `frame_mask.not_null_values` flag from true to false. It preserves:

- the domain's exact `0..3` range check;
- every required relation column's explicit `NOT NULL` constraint;
- the admission conflict-row nullable field and exact shape check;
- the immutable structural and function-body parents; and
- all role, capability, RLS, transaction and command boundaries.

The regenerated inert SQL remains 424 statements and is bound as:

- byte count: `1437009`;
- SHA-256: `fc1c00ab7209a6689f4de29a14a134719a0110dfd3b556172781384332af41fa`.

The parse/catalogue contract is deterministically rebound so only the expected
type-catalogue digest changes, to
`sha256:b7244669f109b81a3907c2f7a5397a253e8a374e261177a7567042d064c25c90`.

## Remaining admission sequence

This candidate cannot inherit the prior PostgreSQL pass. It must pass a fresh
exact-HEAD independent veto, a fresh contained parse/catalogue rehearsal, and a
fresh behavior rehearsal. No application migration, operational database,
provider, patient/clinical/product data, runtime wiring, deployment, Pages,
release or protected-ref movement is authorised.
