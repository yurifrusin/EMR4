# Raisa shared application-auth operational hardening closeout

Date: 2026-08-01

Result: `raisa_shared_application_auth_operational_hardening_pass`

## Outcome

The separately authorised repository-local, provider-free, authored-synthetic
operational-hardening descendant passes. The accepted default-off shared-auth
transport now has one exact separation between an authenticating deployment
login and the NOLOGIN capability role, one strict proxy boundary, bounded
per-process abuse control, retained metadata-only denial audit and an explicit
finite SQLAlchemy pool.

This remains a synthetic local protocol proof. It adds no real identity,
Microsoft or Office federation, product-derived read, deployment credential
lifecycle, cloud control or production path.

## Durable boundary

- `emr4_application_auth_login_*` is a `LOGIN`, `NOINHERIT`, non-owner,
  non-superuser role with a finite connection limit, no direct auth-table
  grants and only membership in the exact `NOLOGIN` capability role. Repository
  SQL creates it with `PASSWORD NULL`; acceptance used one generated disposable
  password that was never recorded.
- The bounded engine factory accepts only a PostgreSQL URL whose username is
  the exact allowlisted deployment-login role. Each new physical connection
  executes exact `SET ROLE` to the allowlisted capability role. Pool size,
  overflow, checkout timeout, recycle, pre-ping, LIFO and rollback-on-return
  behavior are explicit, and pool capacity cannot exceed the role limit.
- Forwarded identity is accepted only from an explicit trusted peer and only as
  one canonical `X-Forwarded-For` address paired with
  `X-Forwarded-Proto: https`. Standard `Forwarded`, duplicate fields, chains,
  malformed values, incomplete trusted-proxy input and untrusted spoofing fail
  closed. The resolved address affects only an HMAC abuse key; it grants no
  authentication or origin authority.
- A bounded fixed-window limiter guards all seven routes before auth material is
  processed. Its live key set is finite. The first 429 per key/window requires
  audit, later blocks coalesce, and an audit failure releases its reservation so
  the next denial retries the required write.
- Malformed, origin/CSRF, authentication and first rate-limit denials retain one
  generic `auth.authorization_denied` row with fixed authored-synthetic
  metadata, a generated correlation ID and an HMAC client reference. Raw
  addresses, proxy/origin headers, credentials, cookies, bodies and exception
  text are excluded. A required audit outage remains denied as generic 503.
- The router now has two explicit default-off dependencies: neither the
  synthetic transport nor its operational guard is inferred from configuration.

## Acceptance evidence

One uniquely named loopback database, one uniquely named deployment-login role
and one uniquely named capability role passed the live-local acceptance:

- `session_user` remained the login role while `current_user` was the exact
  capability role after pool checkout;
- the login role had no direct application-auth table access, while both roles
  remained non-owner, non-superuser and unable to bypass RLS;
- pool capacity equalled the role connection limit and a third checkout failed
  inside the configured 0.25-second bound;
- direct peers, trusted one-hop forwarding, spoof, duplicate, chain and
  non-HTTPS proxy cases followed the frozen contract;
- a successful request, one origin denial, one proxy denial, one first rate
  denial, repeated rate coalescing and forced audit outage followed the generic
  HTTP contract without releasing raw material or cookies on errors;
- exactly three retained denial rows were visible only in the fixed synthetic
  practice context; no-context RLS exposed zero rows and audit update failed;
- raw/target-value scans across rows, responses and evidence found zero matches;
  and
- the exact disposable database and both roles were dropped and proved absent.

All 151 focused auth/API/security cases, 193 expanded no-`conftest` cases and
12 serial legacy database cases pass. The prior accepted runtime-role transport
runner passes unchanged after explicit operational-guard injection. Python
compilation, targeted Ruff, API YAML and JSON parsing, the exact Bandit baseline,
pip dependency audit, migration upgrade/drift/downgrade/re-upgrade cleanup and
whitespace checks pass.

Every recorded external and product side-effect count is zero: no provider,
external-identity or Microsoft/Office identity call; cloud/IAM mutation;
product, patient or clinical read; appointment/arrival command; microphone
capture; document mutation; deployment; or production change occurred.

## Security-finding tracking disposition

The point-in-time review in
`docs/security/security-finding-tracking-review-2026-08-01.md` confirms that
security detection is not laptop-only: GitHub hosts scheduled CodeQL and
Dependabot checks, while Python and Node security workflows run on pushes and
pull requests. It also confirms that EMR4 does not yet have a complete owned
finding lifecycle independent of the laptop automation.

The 14 stale Bandit gate candidates were traced, classified and bound to a
durable validation ledger; the blocking baseline gate now passes with only its
two existing reviewed B324 exceptions. No GitHub alert was dismissed. Nine
Dependabot alerts remain open, alerts 8-15 still need durable validation, and
three repository-validated CodeQL highs remain open in GitHub. A scheduled
GitHub Python/Node scan, a single alert register, ownership/SLAs and native
GitHub disposition are a fresh security-governance decision.

## Preserved closed boundaries

Protected holdouts and raw historical Diary material were not inspected. The
frozen Sydney development service remains unchanged at revision
`raisa-office-web-dev-00006-xf9` and digest
`sha256:8e06f07e4efd393f38275348d8bd7b136e664c2797c399a89207b66116839324`;
its zero-authority posture and resource limits were not broadened.

Real EMR4 identities or practices, external identity providers,
Microsoft/Office federation, product-derived or patient/health/clinical/
historical data, GraphQL and product reads, appointment or arrival commands,
microphone capture, document mutation, distributed rate limiting, production
retention/SIEM, deployment secret management, cloud/IAM changes, organisational
Office deployment, production and release remain closed.

No commit, push, pull request, staging operation or protected-ref movement was
performed. The non-PHI closeout notification was not attempted because this
tranche's frozen boundary prohibits network egress beyond disposable local
PostgreSQL.

## Claim limit and next gate

This result proves the exact repository-local authored-synthetic operational
contracts above. It does not prove internet-scale or distributed abuse
resistance, ingress configuration, credential rotation or secret management,
production monitoring/retention, real Office cookie behavior, real identity,
product-data safety, deployment, production fitness or release readiness.

The next safe candidates require separate authority:

- a repository-local security-finding governance descendant joining native
  GitHub alert IDs to a durable register, scheduled GitHub Python/Node scans,
  ownership and response-time rules, while native alert disposition and
  `SECURITY.md` changes remain approval-gated; or
- a supervised authored-synthetic Word desktop/Online cookie-compatibility
  exercise with real identity and every product read still closed.
