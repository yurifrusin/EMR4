# Sol acceptance: provider-free OIDC start/callback transport boundary

Date: 2026-08-02

Decision: `accepted`

Result: `provider_free_oidc_start_callback_transport_boundary_pass`

## Acceptance judgment

The implementation satisfies the frozen first descendant. Both HTTP routes are
mounted but default-off behind a fail-closed dependency. Start admission binds
exact origin, pre-authentication CSRF, enum-only request shape and bounded HMAC
idempotency to one existing encrypted authorization attempt. Callback admission
is byte-bounded before parsing and accepts only one unambiguous allowlisted
`form_post` shape.

The decisive proof used the ordinary FastAPI router over a real loopback HTTP
socket and the accepted least-authority PostgreSQL attempt runtime. It proved
exact start replay, one-use attempt consumption, generic callback replay and
malformed-input denial, fixed exact-origin bridge release, zero sensitive
response residue and complete server/database/two-role cleanup.

## Evidence reviewed

- frozen plan, design and threat-model delta;
- strict schemas, start/callback service, router/error integration, denial
  action mapping and versioned API Spine contract;
- successful provider-free live-local HTTP/backend/PostgreSQL evidence;
- focused parser, transport, router, documentation and evidence tests; and
- targeted lint, compilation and repository diff checks.

## Limits

This accepts only the authored-synthetic provider-free mounted transport. It
grants no live Microsoft/provider call, real identity, binding, admission grant,
application session, product read, persistent production secret, cloud/IAM,
deployment, protected integration, production, release, Pages or Dependabot
disposition authority. The next two user-preauthorised descendants still
require separate five-source rehydration and acceptance.

Reasoning level: High. Architecture and security meaning were frozen before
implementation; acceptance followed the exact live-local gates and did not
override a failure or broaden the user's authority.
