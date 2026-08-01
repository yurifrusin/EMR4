# Threat-model delta: shared application-auth operational hardening

Date: 2026-08-01
Status: active acceptance boundary
Parent: `raisa_shared_application_auth_runtime_role_secure_transport_pass`

## Assets and attacker-controlled inputs

The protected assets are authored-synthetic session/exchange state, append-only
auth audit evidence, the runtime capability role, database availability and the
generic transport error boundary. Attacker-controlled inputs include the direct
network peer address supplied by the ASGI server, proxy headers, request rate,
path/body/header/cookie values and all opaque authentication material.

No real identity, patient, health, clinical or product-derived data is in
scope. A test value that resembles such data is prohibited.

## Trust boundaries

1. ASGI server to exact trusted proxy: only explicitly allowlisted networks may
   supply the one-hop forwarded-client contract.
2. Request to operational guard: proxy resolution and rate admission occur
   before auth body or credential processing.
3. Deployment login to PostgreSQL capability: the authenticating role has no
   direct table capability and must enter the exact NOLOGIN role.
4. Auth/denial code to bounded pool: checkout, statement, lock and idle
   transaction waits are finite.
5. Denial metadata to append-only audit: only fixed classifications and keyed
   references cross this boundary.

## Threats and required controls

| Threat | Required control and proof |
|---|---|
| Spoofed client address bypasses a limit | Ignore no forwarded value implicitly. Reject forwarded headers from untrusted peers, non-HTTPS forwarding, malformed addresses and multi-hop chains. Prove exact trusted-peer behavior. |
| A permissive proxy parser changes origin/auth authority | Resolver output is used only for abuse keys; exact request `Origin` and existing runtime bindings remain independently enforced. |
| Distributed or key-churn traffic exhausts memory | Validate limits, cap live keys, prune expired keys, evict at capacity and document that multi-instance/edge limiting remains unproved. |
| Rejected traffic amplifies database writes | Persist the first 429 per key/window only; keep later denials bounded and prove the audit count. |
| Unauthenticated attacks leave no durable evidence | Required generic audit for request/origin/CSRF/auth failures and first rate block; forced sink failure remains denied and becomes generic 503. |
| Audit leaks authentication or network material | HMAC reference with an unpersisted process key; fixed category/action/surface; no raw headers, IPs, bodies, exception text or credentials in rows, evidence or responses. |
| Audit outage creates an auth success | A required audit failure cannot release any successful state or cookie and must return generic unavailable. |
| Deployment credential directly owns data privileges | Separate LOGIN/NOINHERIT role from NOLOGIN capability role; no direct table grants; prove `session_user != current_user` and role-only access. |
| Connection or transaction exhaustion stalls workers | Explicit pool size/overflow/timeout/recycle/reset, role connection limit, pre-ping and accepted PostgreSQL timeouts; prove checkout failure inside the bound. |
| Pool reuse retains tenant/role state | Rollback on return and exact role setup on physical connect; transaction-local practice context and existing RLS remain mandatory. |
| New middleware becomes a second authorization engine | The guard may deny only. It never authenticates, maps identity, evaluates product permissions or invokes commands. |

## Abuse and negative cases

Acceptance must include untrusted forwarded-header spoofing, trusted proxy with
multiple addresses, IPv4/IPv6 canonicalization, missing peer identity, window
boundary, concurrent requests at the limit, key-capacity churn, denial-audit
outage, pool exhaustion, login-role direct access, wrong capability-role name,
RLS cross-practice access, audit update/delete, raw-value scans and complete
database/role cleanup.

## Residual risks and closed decisions

- The limiter is in-process and cannot coordinate multiple workers or regions.
- The trusted-proxy list is architecture configuration only; no ingress or
  Cloud Run setting is changed or proved.
- The deployment credential lifecycle, secret manager, rotation, revocation,
  backup, retention, telemetry and paging path are not implemented.
- Retained denial rows are authored-synthetic acceptance evidence, not a
  production SIEM or incident-response system.
- Existing GitHub security-alert backlog and workflow governance are assessed
  separately; this tranche does not dismiss or remediate those findings.
- Real identity, Office federation, product data, deployment, production and
  release remain closed.
