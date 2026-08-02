# Sol acceptance: Raisa two-component OIDC runtime adapter

Date: 2026-08-02

Decision: accepted as `two_component_oidc_runtime_adapter_pass`

## Accepted claim

The default-off, route-free application adapter implements the reviewed MSAL
protocol/Authlib verification seam and passes its authored-synthetic provider-
free fault matrix. It stores one five-minute MSAL flow only in a bounded
authenticated-encryption envelope, consumes it before one exchange, rejects the
MSAL-claims shortcut, admits only independently verified immutable external
identity fields and releases no EMR4 authorization or session.

## Acceptance basis

- fresh five-source pre-acceptance receipt: passed;
- exploit reproduction before patch: missing adapter / no admissible shortcut;
- deterministic acceptance: 25/25 matched;
- focused runtime/architecture, inherited federation/auth/Office/API-spine and
  continuity tests: passed;
- Ruff and targeted application Bandit: passed with zero findings;
- dependency integrity and vulnerability audit: passed;
- full repository pytest parent-HEAD collection defect: reproduced and excluded
  from this tranche's claim; and
- no `docs/branding/` path entered staging or evidence.

## Not accepted

No provider network, real tenant/identity, durable attempt store, mounted route,
callback page, binding resolution, role, session, product read, deployment,
production or release is accepted. The next provider-free PostgreSQL attempt-
store candidate requires fresh authority.
