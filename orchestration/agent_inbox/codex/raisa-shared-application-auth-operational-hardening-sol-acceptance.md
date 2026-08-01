# Sol acceptance — Raisa shared application-auth operational hardening

Date: 2026-08-01

Decision: `accepted`

Result: `raisa_shared_application_auth_operational_hardening_pass`

Coordinates after closeout: Continuity graph revision 185 / Compass map
revision 166, sourced from graph revision 185.

## Independent evidence review

Sol reviewed the frozen plan and threat delta, implementation, API contract,
tests, disposable PostgreSQL evidence and raw-value/residue assertions without
relying on the acceptance runner's final boolean. The evidence establishes:

- the exact deployment login authenticates but owns no direct auth-table
  capability, and every pool connection enters the exact NOLOGIN capability
  role;
- proxy identity is fail-closed, one-hop and abuse-key-only;
- the limiter has finite time/key bounds and coalesces retained 429 audit;
- denial audit is fixed-metadata and HMAC-only, with generic 503 on required
  audit failure;
- pool checkout and transaction waits are finite, RLS and append-only audit
  remain enforced, and the exact database and both roles are absent after the
  run; and
- zero external/product side effects and zero raw/target evidence matches are
  recorded.

All 151 focused, 193 expanded no-`conftest` and 12 serial legacy database tests
pass. Ruff, compilation, JSON/YAML, exact Bandit baseline, pip audit, migration
and whitespace gates pass. The prior accepted runtime-role transport acceptance
also passes.

## Security-tracking review

The answer to Yuri's security question is accepted as a point-in-time inventory,
not as remediation: GitHub CodeQL and Dependabot provide laptop-independent
detection, but EMR4 lacks one durable owner/SLA/disposition register and its
Python/Node security workflows are not scheduled. Fourteen Bandit candidates
now have exact validation receipts and the gate passes. Nine Dependabot alerts
and GitHub disposition drift remain open. No GitHub alert or setting changed.

## Veto and non-claims

Acceptance is vetoed from being described as real authentication, external
identity or Office federation, production ingress/credential/pool/limiter/SIEM
readiness, distributed abuse resistance, product-data authority, deployment,
production or release. Protected holdouts and raw historical Diary material
remain unopened. No provider, external worker or subagent ran.

No commit, staging, push, pull request or protected-ref movement occurred.
