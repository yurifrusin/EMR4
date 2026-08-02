# Raisa two-component OIDC runtime-adapter design

Date: 2026-08-02

Result class: route-free provider-free runtime foundation

## Placement

`app/services/application_identity_oidc_adapter.py` is a dormant application
service. It is not imported by `main.py` or an application router. The existing
authored-synthetic federation-admission and persistence services are not
imported by this adapter, so a verified provider principal cannot silently
become an EMR4 binding, role or session.

This remains a REST command/protocol concern under the API Spine. It does not
create a GraphQL mutation or an asynchronous identity actuator.

## Component ownership

| Operation | Owner | Adapter postcondition |
|---|---|---|
| Create authorization flow | MSAL 1.37.0 | Exact tenant authority, redirect, `openid profile`, S256 and `form_post` |
| Redeem stored flow | MSAL 1.37.0 | One invocation after atomic attempt consumption; raw result remains transient |
| Verify raw ID token | Authlib 1.7.2 / JOSE RFC 1.7.4 | RS256, pinned metadata/JWKS, standard claims and one unknown-key refresh |
| Release external principal | EMR4 adapter | Exact `tid`, bounded nonempty `oid`/`sub`, no authorization or session |

The adapter never reads `id_token_claims`. It copies only the raw `id_token`
from the transient MSAL result into the verifier call and clears the result map
after the attempt. Access and refresh tokens have no output, persistence or
audit field.

## Server-owned configuration

One immutable configuration supplies a canonical lowercase tenant ID, client
ID, exact HTTPS callback, exact origin for each of Word desktop, Word Online
and native Diary, a five-minute attempt lifetime, 16 KiB token bound, 60-second
claim leeway and at-most-24-hour verifier-client lifetime. It derives:

- `https://login.microsoftonline.com/{tenant}`;
- the tenant-specific v2 issuer and discovery URL;
- exact tenant authorization and token endpoints; and
- `https://login.microsoftonline.com/common/discovery/v2.0/keys`.

`common`, `organizations`, `consumers`, request-selected discovery, redirect or
JWKS locations, redirects from metadata requests and non-RS256 metadata fail
closed.

## Attempt lifecycle

The provider-free store implements the future persistence port without changing
database truth. It stores at most 128 attempts. State and nonce appear outside
the encrypted envelope only as separate HMAC-SHA256 digests. The authenticated
Fernet envelope contains the exact bounded MSAL flow, surface, configured
origin and return-target enum. The raw PKCE verifier is therefore absent from
logs, URLs, audit and plaintext residue.

Callback lookup uses the submitted state HMAC. Under one lock, an exact live
attempt is removed before its encrypted flow is returned for the sole token
exchange. Provider failure, verification failure, audit failure after
completion, replay and concurrent completion cannot reuse it. Wrong state or a
malformed callback invokes no exchange and does not consume an unrelated
attempt.

The store is intentionally process-local and non-durable. It is sufficient for
provider-free proof, not multi-process or deployed operation.

## Verification and metadata

The Authlib verifier rejects the raw token before parsing above 16,384 UTF-8
bytes. Its pinned transport admits only the exact discovery and JWKS URLs,
forbids redirects, enforces timeouts and bounds a streamed metadata/JWKS
response to 128 KiB. Metadata must match the derived issuer, authorization,
token and JWKS locations and advertise exactly RS256.

Authlib/JOSE RFC parses the JWK set, selects the key, verifies the signature and
validates exact issuer, audience, nonce, `exp`, `nbf`, `iat` and nonempty `sub`
with at most 60 seconds' leeway. Authlib owns its single forced JWKS refresh for
an unknown `kid`. EMR4 then enforces exact `tid` and bounded nonempty `oid` and
`sub`. A verifier client is recreated after at most 24 hours.

## Errors and audit

External error text is one of `authentication_failed` or
`authentication_temporarily_unavailable`. Provider, token, key and exception
text never crosses the adapter. Required audit records only time, typed
operation, allow/deny/error, bounded reason code, HMAC attempt reference,
surface/return target, whether a token exchange was attempted and whether a
principal was released. Audit failure releases nothing; on start it also
removes the newly stored attempt.

## Exact reconciliation

MSAL 1.37.0 emits a 22-character state. The non-mounted OpenAPI callback schema
previously required at least 43 characters, so it would have rejected the
selected library's own output. The schema now accepts opaque state from 16 to
256 characters while the adapter still requires high-entropy URL-safe syntax
and exact keyed-digest correlation.

## Closed boundaries

There is no route, browser response, callback page, durable attempt store,
database role, binding lookup, admission grant, cookie or application session.
There is no live client credential configuration, provider call, real identity,
Graph/product scope, GraphQL mutation, product read, deployment or release.
