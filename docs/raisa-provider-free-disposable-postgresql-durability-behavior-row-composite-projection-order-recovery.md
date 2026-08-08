# Disposable PostgreSQL row-composite projection-order recovery

Date: 2026-08-08

Status: provider-free recovery candidate; runtime closed pending fresh proof

## Observed failure

Behavior attempt 015 reached `BTR-E01` and stopped with PostgreSQL SQLSTATE
`22P02` at internal line 36 of the exact allowlisted function
`emr4_context_fabric.register_observer_generation_v1`. It admitted zero
scenarios and removed its uniquely owned container with absence verified.

The coordinate maps to the binding `SELECT ... INTO STRICT` statement. Static
reconciliation proves that two typed projection catalogues did not follow the
physical table-composite order established by the accepted structural
recovery. The binding projection placed UUID `stream_id` in the positional
slot occupied by bigint `binding_revision`; the aggregate-alias projection had
the same class of ordering drift. PostgreSQL assigns a selected row into a
table-composite variable positionally, so this ordering is not cosmetic.

## Exact correction

The function-body builder now orders the complete binding and aggregate-alias
projections exactly like their physical relation composites. No predicate,
cardinality, authority, RLS, lock, write, trigger, digest, idempotency or
failure contract changes.

Renderer `2.0.5` adds a deterministic positional-row invariant. Every
non-system-column `SELECT_EXACT` or `LOCK_EXACT`, and every row-returning
`INSERT`, `INSERT_OR_RELOAD_COMPARE` or `UPDATE`, must project the complete
relation columns in exact physical order. An authored hostile swap fails
closed before SQL rendering.

The corrected body contract is
`sha256:b3eaa041dc96a6117957b9dd9bde0205afd1023fc521b3183410e7b3c4b8b1b1`.
The regenerated inert SQL remains 1,404,420 LF bytes and 412 statements, with
SHA-256
`sha256:83359fbc0cf2fb8f7d147b5dc820aa28910129428c9727daa1e1dc0259ce73f5`.
Its render-manifest file SHA-256 is
`sha256:66c103adac8c9ba52440077e25d2f3fc58ed6d30005576034bb42115c746dd71`.

## Fresh-proof sequence

Historical parse/catalogue and behavior evidence remains immutable evidence
about its predecessor artifact. The corrected chain must pass:

1. deterministic builder, renderer, invariant and hostile-mutation tests;
2. a fresh clean exact-HEAD independent veto;
3. a newly hash-bound disposable parse/catalogue rehearsal with exact cleanup;
4. a separately rebound behavior contract; and
5. a fresh twenty-scenario behavior/transaction rehearsal with exact cleanup.

No application migration, product database, provider, patient or clinical
data, runtime wiring, deployment, Pages, release or protected-ref movement is
authorised.
