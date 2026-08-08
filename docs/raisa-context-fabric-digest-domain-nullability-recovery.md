# Context Fabric digest-domain nullability recovery

Date: 2026-08-08

Status: bounded provider-free recovery candidate; no runtime acceptance yet

## Observed failure

Disposable behavior failure evidence 007 stopped before all twenty scenarios
with PostgreSQL SQLSTATE `23502`; cleanup was complete. The previously accepted
column-coordinate and fixed not-null-header diagnostics both remained closed
because PostgreSQL was rejecting a domain value rather than a table column.

The accepted inert DDL declared `emr4_context_fabric.digest_sha256` itself as
`NOT NULL`. The same DDL also:

- permits nullable digest-bearing columns such as
  `context_durability_checkpoint.last_observation_digest`;
- requires that value to be `NULL` when `last_contiguous_position = 0`; and
- has `register_observer_generation_v1` deliberately insert that typed null at
  a zero-position stream head.

Those constraints cannot all be represented simultaneously in PostgreSQL.

## Exact correction

Renderer version `2.0.4` adds one sealed recovery operation,
`RELAX_DIGEST_DOMAIN_NULLABILITY`. It changes only the effective
`digest_sha256.not_null_values` flag from true to false. It does not weaken the
digest format check. Required digest fields continue to carry column-level
`NOT NULL`; nullable fields remain governed by their explicit table invariants.

The immutable structural and function-body parents are unchanged. The freshly
rendered inert SQL remains 412 statements and is bound as:

- byte count: `1404420`;
- SHA-256: `9407b8b641488b8c48ad51ef58c7ca2c3c15e83dca89da58de8f5726aef69f65`.

## Admission sequence

This candidate cannot silently inherit the old PostgreSQL evidence. It must:

1. pass deterministic renderer, recognizer and continuity checks;
2. pass a fresh exact-HEAD independent veto;
3. rebind the disposable parse/catalogue and behavior contracts to the new
   artifact and manifest digests;
4. pass a fresh contained parse/catalogue rehearsal; and
5. only then return to the twenty-scenario behavior rehearsal.

No application migration, product database, provider, patient/clinical data,
runtime wiring, deployment, Pages, release or protected-ref movement is
authorised.
