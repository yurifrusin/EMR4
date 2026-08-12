# Threat-model delta: pure route-adapter differential rehearsal

Date: 2026-08-12

Status: `provider_free_unmounted_authored_synthetic`

## Assets protected

- command authority and current database truth;
- separate user confirmation evidence;
- backend-minted freshness evidence;
- durable command idempotency identity;
- honest route provenance and minimized audit attribution; and
- the accepted operation, outcome, precedence and lock-order contract.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Authentication or request arrival is relabelled as confirmation | confirmation mode and reference are a separately required group |
| A same-transaction read is relabelled as the user's prior fresh view | precondition version and digest must be echoed from backend-minted evidence |
| Correlation identity is relabelled as idempotency | key digest and canonicalization version form a distinct required group |
| Caller changes operation or provenance | adapter specification injects both fields and input structure forbids them |
| A partial candidate escapes after several gaps | any gap produces `adapter_rejected` and a null candidate |
| Differential comparison hides meaningful differences | only `route_adapter_id` is excluded; all eighteen remaining fields are exact |
| Complete synthetic raw mapping is mistaken for route eligibility | every result records runtime authorization false and current raw remains ineligible |
| Create mapping is mistaken for a schedule fence | the contract preserves the separate unproved database-owned fence gate |
| Event or Context Frame supplies command evidence | both remain forbidden and are absent from every input shape |
| Synthetic evidence is mistaken for product proof | all identifiers are `syn-`; no app route, source or product data is opened |

## Residual boundary

This rehearsal cannot prove HTTP parsing, authentication integration, response
compatibility, a production token, database locking, RLS, persistence,
rollback, client parity, shadow safety or deployment suitability. Those remain
separate gates.
