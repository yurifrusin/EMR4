# Threat-model delta: globally-disabled runtime-instrumentation scaffold

Date: 2026-08-12

Parent:
`docs/security/raisa-provider-free-default-off-runtime-instrumentation-architecture-threat-model-delta.md`

## New surface

This tranche adds dormant typed code, four post-helper route calls and one outer
ASGI middleware registration. It creates no enabled observer path.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A deployment enables shadowing through an environment setting | No setting exists; the generation type rejects enabled state, allowlists and key references. |
| A disabled route call still reads patient or user data | The call receives only the adapter ID and the generation check occurs before every supplier/cell access. |
| Middleware changes response ordering or content | Disabled middleware delegates with the original `scope`, `receive` and `send`; it allocates no wrapper or cell. |
| Stage failure changes command behavior | The stage has no return value, is invoked only after helper success and contains disabled-path failure. |
| A failed helper still produces evidence | Stage calls are textually and structurally after successful helper completion. |
| Context is inferred from a bearer token or client header | There is no application context-provider implementation; the protocol requires a server-owned value. |
| Projection factory accepts free text or response content | Its typed input exposes only closed structural fields; tests reject forbidden parameter names and verify the exact 24-field output. |
| Direct use of the offer port silently becomes a sink | The only concrete port raises; the finalizer contains that exception only after the original send succeeds. |
| Duplicate final frames replay a projection | The cell is single-assignment and take-and-clear; the second take returns empty. |
| Dormant code is mistaken for operational evidence | Closeout must report zero staged projections/offers and explicitly deny runtime, persistence, latency and monitoring claims. |

## Residual gates

The scaffold does not prove real server-session/correlation provenance, HMAC
key custody, enabled middleware cancellation/streaming behavior, queue
backpressure, observer isolation, diagnostic retention or operational cleanup.
Those remain separately reviewed gates; practice enablement is not the next
tranche.
