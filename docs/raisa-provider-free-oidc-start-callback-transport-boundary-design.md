# Raisa provider-free OIDC start/callback transport boundary design

Date: 2026-08-02

Result class: default-off mounted external REST protocol boundary

## API Spine placement

Start is an external REST protocol command and callback is a provider protocol
endpoint. Neither is GraphQL, a product read, an async actuator or a session
command. Both remain under the existing application-auth operational admission
guard and a separate dependency whose default implementation returns 404.

## Start boundary

`OIDCStartCallbackTransport` owns the exact surface-origin map, CSRF comparison,
bounded HMAC-only idempotency registry and accepted `TwoComponentOIDCAdapter`.
The request supplies only surface and return-target enums. Tenant, authority,
redirect URI, origin and destination remain server configuration.

Idempotent replay is limited to the five-minute attempt lifetime. The raw
idempotency key is not retained; one keyed digest selects a record and another
keyed digest binds the exact origin/surface/return tuple. A replay with a
different tuple denies and no active record is silently evicted.

## Callback boundary

The callback reads a bounded byte body before decoding. It accepts only exact
URL-encoded content, at most four unique allowlisted fields and strict UTF-8.
The adapter then consumes the server-side attempt and runs the authored-
synthetic protocol/verifier pair exactly once. The transport never serializes
the returned tenant, object or subject.

## Bridge page

The successful bridge contains only fixed status, surface and return-target
enums. A fresh validated CSP nonce permits one inline script. The script chooses
an opener or non-self parent, calls `postMessage` with the exact stored HTTPS
origin and closes. Absence of a parent changes no server decision and releases
no authority.

Headers require `Cache-Control: no-store`, `Pragma: no-cache`,
`Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, a restrictive
Permissions Policy and CSP with `default-src 'none'`, nonce-only script,
`base-uri 'none'`, `form-action 'none'`, and the exact frame ancestor.

## Closed descendants

The bridge intentionally carries no admission grant yet. Provider-key HMAC
resolution, binding/audit capability, admission-grant persistence, session
redemption/cookies, fresh internal principal truth, product access, live
Microsoft, deployment and production remain separate boundaries.
