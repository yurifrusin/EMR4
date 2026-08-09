# Threat-model delta: durability UUID minimum recovery

Date: 2026-08-09

Status: bounded provider-free renderer recovery; behavior runtime closed

## Scope change

Behavior attempt 025 exposed one type-unsound generic renderer lowering:
`MIN_FIELD` used the `min` aggregate for UUID as well as bigint. This change is
limited to type-directed lowering and independent recognition of that opcode.
It changes no authority, database principal, policy, trigger, entry point,
scenario or product interface.

## Threats and controls

| Threat | Control | Required evidence |
|---|---|---|
| A UUID-only patch changes bigint retention semantics | Bigint retains exact `pg_catalog.min`; UUID alone uses ordered selection | Artifact contains two bigint aggregates and two UUID ordered selections |
| Ordered UUID selection changes null handling | Explicit ascending `NULLS LAST LIMIT 1` mirrors aggregate minimum's non-null preference | Exact renderer fragment and hostile mutation tests |
| A broad text rewrite hides unsupported future types | Renderer branches on exact result type and rejects every type other than UUID/bigint | Direct unsupported-type unit test |
| UUID aggregate defect returns | Independent recognizer rejects `pg_catalog.min(s.stream_id)` | Hostile resealed SQL is invalid with `uuid_min_aggregate` |
| Repair changes body or structural authority | Immutable source hashes remain exact; only renderer source/artifact lineage changes | Parent binding and semantic diff proof |
| Failed evidence is overwritten | Attempt 025 has an immutable byte-identical copy; mutable evidence stays unstaged | SHA-256 and byte equality test |
| Diagnostic leaks PostgreSQL text | Only repository-bounded function/operator identifier, raw digest and cleanup are durable | Receipt has `raw_error_persisted: false` |
| Recovery is mistaken for runtime readiness | Fresh parse proof, parent rebind, veto and full behavior pass remain mandatory | No behavior execution before all gates pass |

## Residual risk

Passing this repair will not prove concurrent execution, crash/unknown-commit
recovery, retention behavior, operational storage or credentials, performance,
watcher/listener integration or product wiring. Parse/catalogue installation
still does not execute every stored branch; the frozen twenty behavior
scenarios remain the next bounded execution proof.
