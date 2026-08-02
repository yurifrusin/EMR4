# Threat-model delta: provider-free OIDC start/callback transport boundary

Date: 2026-08-02

Parent: `docs/security/raisa-postgresql-oidc-operational-connection-boundary-threat-model-delta.md`

## New trust boundaries

1. An unauthenticated browser/Office surface can reach a mounted start command.
2. A provider-shaped form POST can reach the exact callback endpoint.
3. A returned HTML document can message an opener or parent origin.

The path remains authored-synthetic and provider-free.

## Threats and controls

| Threat | Control | Failure |
|---|---|---|
| Login CSRF or surface swapping | Exact stored surface-origin map plus matching pre-auth CSRF cookie/header on start | 403 generic denial |
| Client chooses tenant, redirect or return URL | Strict two-enum body; adapter/server configuration owns every protocol endpoint | Validation denial |
| Start retry creates attempt fanout | Bounded HMAC-only idempotency replay to exact request tuple and expiry | Mismatch denied; capacity unavailable |
| Raw idempotency key leaks | Keyed digest only; fixed errors and sanitized evidence | Acceptance residue failure |
| Callback parser allocation/ambiguity abuse | 12 KiB byte bound, exact media type, four fields, unique keys, strict decoder | Generic authentication failure |
| Duplicate state/code changes parser meaning | Duplicate and extra fields rejected before adapter | No protocol completion |
| Callback replay | Accepted attempt store consumes state exactly once | Generic failure, no bridge |
| External identity leaks to browser | Transport discards verified tenant/object/subject; fixed enum-only message | No HTML emitted on mismatch |
| Bridge exfiltrates to attacker origin | Exact stored HTTPS origin passed as `postMessage` target and CSP frame ancestor | No wildcard/fallback target |
| Inline/third-party script injection | Fresh nonce-only static script, no external resource, no dynamic provider text | CSP blocks execution |
| Browser caches or refers callback | No-store/no-cache, no-referrer, nosniff, restrictive permissions | Acceptance header failure |
| Transport becomes session authority | No grant/session service import, no cookie header, no product dependency | Static/import and runtime failure |
| Provider accidentally contacted | Only injected authored-synthetic protocol/verifier in acceptance; no live client construction | Side-effect count fails |
| Detailed provider/parser error enumerates identity | Two generic response values; required internal audit retains bounded reason only | Fixed response asserted |

## Residual gates

This does not establish real provider interoperability, binding resolution,
admission-grant persistence, application-session redemption, Office dialog API
compatibility, distributed rate control, product authorization, production
credentials/keys, monitoring, deployment, production or release.
