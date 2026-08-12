# Threat-model delta: default-off runtime-instrumentation architecture

Date: 2026-08-12

Parents:

- `docs/security/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-threat-model-delta.md`
- `docs/security/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-threat-model-delta.md`

## New design surface

This tranche identifies future route and ASGI seams but creates none. It adds a
source-hashed architecture contract and static validator only.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Observer runs after database commit but before the response is sealed | Route code may stage only; handoff is permitted only after the original final ASGI body send succeeds. |
| Shadow failure changes response bytes or headers | `send(message)` is awaited first, the projection is then atomically removed, and `offer_nowait` has no response/send capability or result channel. |
| Default-off code still reads product data | Global disabled state short-circuits before context or command projection; all other controls must intersect before the factory reads raw values. |
| Existing compatibility mode accidentally enables shadowing | Shadow generation is a distinct immutable configuration; `appointment_raw_compat_mode` has no shadow authority. |
| Actor/session identity is inferred from a token or caller input | Bearer-token hashing, inbound correlation authority and actor/practice session synthesis are explicitly forbidden; missing server-owned context denies. |
| Diagnostic digests leak free text | Free-text and response material are never projection inputs; shape and command digests use closed non-free-text canonicalizers and domain-separated HMAC. |
| Request-scoped state is replayed or emitted twice | The cell is single-assignment and atomically take-and-clear; only one successful final body frame may trigger one bounded offer. |
| Handoff reaches database, route or command capabilities | Route stage, finalizer and observer are distinct capability sets with closed import/argument rules. |
| Middleware failure creates request retries or server feedback | No retry or handler channel exists; handoff failure is contained after response send. Operational server-task isolation remains a later proof obligation. |

## Residual risks and unopened gates

The architecture does not prove Starlette/FastAPI version behavior, middleware
ordering in a running app, response-stream edge cases, request-cell lifecycle,
HMAC key custody, queue implementation, latency, cancellation, process shutdown,
diagnostic delivery, persistence or monitoring. The next scaffold must remain
globally disabled and use authored-synthetic local evidence before any enablement
or operational sink can be considered.
