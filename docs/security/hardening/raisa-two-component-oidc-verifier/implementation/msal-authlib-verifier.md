# Implementation handoff: MSAL plus Authlib verifier

## Selected option

We selected `msal-authlib-verifier`. This file is a future implementation handoff, not implementation authority.

## Required ports

The adapter should expose three internal operations: create a bounded MSAL flow, redeem that exact stored flow once, and verify the returned raw ID token. MSAL remains the only code-flow client. Authlib remains verifier-only and must not initiate or redeem the Microsoft flow.

## Required sequence

1. Build both components from one server-owned tenant/client/redirect policy.
2. Create MSAL with `exclude_scopes=["offline_access"]`; initiate with `scopes=[]`, S256 and `response_mode=form_post`.
3. Persist only the encrypted bounded attempt record already described by the parent design.
4. Atomically consume the attempt before the sole token exchange.
5. Ignore `id_token_claims`; take only the raw `id_token`, reject it above 16,384 bytes, and pass it in process to the verifier.
6. Verify RS256 signature and exact issuer/audience/nonce/time claims through Authlib; permit one library-owned JWKS refresh for an unknown `kid`.
7. Enforce exact `tid` plus nonempty `oid` and `sub`, then discard raw ID token, access token and all provider material.
8. Emit only normalized audit fields and an external-principal result. Do not create a binding, role or session in this port.

## Tests and observability

Tests must cover tampered signatures, wrong algorithm/issuer/audience/nonce/tenant, expired and future tokens, missing identifiers, valid and invalid key rollover, refresh outage, metadata mismatch, token oversize and MSAL-claims bypass. Metrics may count normalized outcomes and refresh attempts but must never contain a token, claim value or provider exception.

## Rollout and rollback

The adapter must remain default-off and provider-free until a later live-provider authority. There is no permissive rollback: disabling the verifier disables federation. Package or metadata failure returns authentication unavailable and leaves application authentication unchanged.
