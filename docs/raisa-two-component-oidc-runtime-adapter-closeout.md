# Raisa two-component OIDC runtime-adapter closeout

Date: 2026-08-02

Result: `two_component_oidc_runtime_adapter_pass`

## Outcome

The separately authorised provider-free implementation candidate passes. The
new default-off route-free application service gives MSAL 1.37.0 sole ownership
of tenant-specific confidential-client flow creation and code redemption, and
gives Authlib 1.7.2 with JOSE RFC 1.7.4 sole ownership of raw ID-token signature,
key and OIDC-claim verification.

The first security regression failed at collection because the adapter did not
exist. After the patch, a forged raw ID token still denies even when the MSAL
result supplies apparently admissible `id_token_claims`; no shortcut principal
is released.

## Implemented boundary

- exact tenant/client/redirect/origin configuration, default off;
- minimal `openid profile`, `offline_access` excluded, S256 and `form_post`;
- five-minute, maximum-128 process-local attempt store containing only
  state/nonce HMACs and a Fernet-authenticated encrypted MSAL-flow envelope;
- atomic attempt removal before one token-exchange invocation;
- transient raw ID token only, bounded to 16 KiB and cleared with the provider
  result; access/refresh tokens have no output or persistence;
- pinned Microsoft discovery/JWKS transport, RS256 only, 128 KiB streamed
  response bound, short timeouts, no redirects and 24-hour client recycle;
- Authlib-owned one-refresh key rollover plus exact issuer, audience, nonce,
  `exp`, `nbf`, `iat`, `tid`, `oid` and `sub` enforcement;
- normalized required audit and only two public error values; and
- output limited to verified `tid`/`oid`/`sub`, frozen surface/origin/return
  context and explicit false authorization/session/product flags.

The non-mounted callback schema was reconciled from a 43-character minimum to
16 because the selected MSAL version emits 22-character state. Exact keyed
correlation and the 256-character maximum remain unchanged.

## Evidence

- 25/25 deterministic provider-free cases match their expected pass, deny or
  unavailable result;
- actual MSAL start and one rejected redemption run over intercepted in-memory
  HTTP only;
- valid Authlib signature admission, tampering, HS256, claim/time/tenant faults,
  valid/invalid rollover, refresh outage, metadata mismatch and oversize all
  behave as frozen;
- wrong state performs zero exchange, exchange failure consumes the attempt,
  and two concurrent callbacks perform exactly one exchange;
- plaintext state, nonce, PKCE verifier and redirect are absent from attempt
  store residue;
- the adapter is absent from `main.py` and all routers;
- targeted Ruff and Bandit report no application-code findings;
- `pip check` reports no broken requirements and `pip-audit` reports no known
  vulnerabilities; and
- focused and inherited suites pass after three stale historical terminal-node
  assertions were reconciled to immutable-presence assertions.

Full repository pytest retains the parent-HEAD collection error in
`tests/test_api_spine_confirmation_family_idempotency_integration.py`, which
imports the removed uppercase `_BERNIE_SESSION_STORE`. Neither the failing test
nor the missing uppercase symbol is changed by this tranche.

## Side effects

Outbound network calls, Microsoft provider calls, real identities, identity
bindings, mounted routes, database writes, sessions, product reads and
deployments are all zero. The concurrent user-owned `docs/branding/` directory
was not modified, read into evidence, staged, tested, committed or removed.

## Residual gates

The process-local attempt store is not durable or distributed. A provider-free
PostgreSQL authorization-attempt store with exact transaction atomicity,
encryption-key abstraction, least-privilege roles/RLS and disposable acceptance
is the next safe candidate and requires fresh authority.

Routes, callback HTML, CSRF/origin checks, admission-grant/session bridging,
live Microsoft, real identity governance, binding resolution, product reads,
cloud/IAM, deployment, protected integration, production and release remain
separately closed.
