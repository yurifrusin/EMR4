# Raisa two-component OIDC verifier architecture revision

Date: 2026-08-02
Result class: architecture and dependency admission only

## Decision

We separate protocol mechanics from identity evidence. MSAL 1.37.0 is the sole Microsoft confidential-client protocol component. Authlib 1.7.2, backed by JOSE RFC 1.7.4, is the sole ID-token verification component. Neither component may silently substitute for the other, and there is no fallback verifier.

MSAL's returned `id_token_claims` is transport convenience, not verified identity evidence. The future adapter must extract the raw `id_token` from a successful token result, pass it transiently to the Authlib verifier, discard every access token, and admit no principal until the verifier and EMR4 postconditions both pass.

## Ownership contract

| Concern | Owner | Exact boundary |
|---|---|---|
| Authority, authorization request, state, nonce and PKCE | MSAL 1.37.0 | One server-selected tenant-specific v2 authority; S256; five-minute attempt |
| Callback and code redemption | MSAL 1.37.0 | `response_mode=form_post`; one stored flow; one token-endpoint exchange |
| Effective scopes | MSAL configuration | Construct client with `exclude_scopes=["offline_access"]`; call with `scopes=[]`; effective OIDC scopes are exactly `openid profile` |
| Signature and key selection | Authlib 1.7.2 / JOSE RFC 1.7.4 | RS256 only; tenant discovery JWKS; cached set; one forced refresh for unknown `kid` |
| Standard claims | Authlib | Exact issuer and audience, correlated nonce, `exp`, `nbf`, `iat`, nonempty `sub`; 60-second maximum leeway |
| EMR4 principal postconditions | Future adapter | Exact configured `tid`; nonempty `oid` and `sub`; no email, domain, group, role or scope authority |
| Product/application authority | Existing EMR4 boundary | Still closed; a verified external principal is not a binding, role or session |

## Coherent metadata set

One server-owned configuration supplies tenant ID, client ID, redirect URI, expected issuer and the exact tenant-specific v2 discovery URL to both components. We accept only the Microsoft login host and the discovery-provided Microsoft JWKS location. A response-level `jku`, an arbitrary issuer, a request-selected discovery URL, `common`, `organizations`, `consumers`, or a metadata mismatch fails closed.

Authlib owns parsed key selection and one immediate unknown-key refresh. The future verifier client must be recycled within 24 hours so discovery metadata is not immortal. An unavailable refresh, a second unknown key, a non-RS256 token, or metadata that does not advertise RS256 returns one generic authentication failure.

## Token handling

The raw ID token is accepted only from the in-process MSAL result and is rejected before parsing when its UTF-8 representation exceeds 16,384 bytes. It is never persisted, audited, logged, placed in an exception, browser response or URL, or retained after verification. The adapter must normalize library exceptions without including token, key or provider text.

We do not request `offline_access`. Any returned access token is discarded and cannot authorize Microsoft Graph or EMR4 product access. No refresh token is stored. Authlib is registered only behind a verifier port; it may not initiate or redeem this Microsoft flow.

## API-spine placement

The future start, callback and one-use session redemption remain REST commands. The callback changes from GET query parameters to POST `application/x-www-form-urlencoded` because `form_post` keeps the code out of URL history and referrer surfaces. The OpenAPI document remains non-mounted and declares no live route.

## Dependency admission

We pin `msal==1.37.0`, `Authlib==1.7.2` and `joserfc==1.7.4`. The direct JOSE pin prevents an unreviewed transitive verifier change. Existing `cryptography==48.0.1`, `PyJWT==2.13.0` and Requests satisfy the selected constraints. The package review records licences, hashes, maintenance and fixed advisory floors.

## Deferred implementation seam

A separately authorised adapter may expose only three internal operations: create the MSAL authorization flow, redeem the stored MSAL flow exactly once, and verify the transient raw ID token against the frozen Authlib policy. This tranche does not add those operations to `app/`, mount an endpoint, create persistence, or call a provider.
