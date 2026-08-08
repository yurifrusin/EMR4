# Provider-free durability body special-form recovery

Date: 2026-08-08

Status: deterministic recovery candidate; runtime closed pending fresh veto

Behavior attempt 017 admitted the reviewed artifact, reached `BTR-E01`, and
stopped with SQLSTATE `42883` at internal line 58 of
`register_observer_generation_v1`. Zero scenarios were admitted and exact
container cleanup was verified.

That coordinate reaches the first generated `COUNT` expression after the
complete stream-head read. The inert DDL renderer lowered the PostgreSQL
`COALESCE` special form as `pg_catalog.coalesce(...)`. PostgreSQL accepts the
function body definition without resolving that expression, but rejects it
when the path is first executed because `COALESCE` is conditional SQL syntax,
not a namespace-callable catalog function.

This is a recurrence of AER-0131. Its earlier correction covered the behavior
harness snapshot query but did not census the independently generated accepted
function and trigger bodies. Renderer 2.0.6 now emits unqualified
`COALESCE(...)` for count lowering and exact JSON-key checks, rejects any
schema-qualified spelling anywhere in the rendered artifact, and retains the
existing nullable-count invariant. Callable aggregate and array functions
remain explicitly catalog-qualified.

The typed body contract and its effects are unchanged. The rendered inert SQL
and manifest necessarily receive new hashes and must pass fresh deterministic
tests, exact PostgreSQL parse/catalogue rehearsal, descendant behavior-contract
rebinding, independent review, and a new behavior attempt before acceptance.
