# Threat-model delta — Raisa shared-auth runtime role and secure transport

Date: 2026-08-01

Status: `repository_local_provider_free_authored_synthetic_transport`

## Overview

This delta covers the separately authorised least-privilege PostgreSQL
capability-role contract, token-reference bootstrap function and default-off
authored-synthetic browser session transport above the accepted EMR4
application-auth policy engine and PostgreSQL unit of work.

The repository security policy, shared-auth architecture, runtime-foundation
and PostgreSQL-persistence threat models remain authoritative. No live EMR4
identity, Microsoft/Office authority, product-derived read, patient or clinical
data, provider, command, deployment, production or release is opened.

## Assets, privileges and invariants

- raw synthetic bootstrap, surface-session, exchange, CSRF, state, nonce and
  PKCE values;
- hash-only durable session and exchange references;
- exact surface, origin, audience, practice, role and generation binding;
- the token-reference-to-principal bootstrap result;
- PostgreSQL role non-escalation and product-table separation;
- forced practice RLS after bootstrap;
- required metadata-audit/state atomicity;
- single-use bootstrap and exchange consumption;
- surface-bearer rotation and logout revocation; and
- generic external failure shapes and complete disposable cleanup.

The implementation must preserve one backend-owned authorization decision.
Microsoft/Office identity, route claims, cookie contents and client-supplied
surface/role/practice values confer no authority by themselves.

## Trust boundaries and attacker-controlled inputs

1. An untrusted browser/Office frame to exact HTTPS-origin FastAPI routes.
2. `Origin`, cookie, CSRF header and bounded JSON fields to the transport.
3. A one-use authored-synthetic bootstrap credential to an in-memory synthetic
   principal registry.
4. Raw opaque values to SHA-256 references before PostgreSQL.
5. The restricted database role to one security-definer hash resolver.
6. The resolved principal key to transaction-local RLS context and the locked
   principal-generation row.
7. The accepted runtime audit/state batch to one PostgreSQL transaction.
8. A Word source partition to one 60-second state/nonce/S256-PKCE exchange and
   a separate native-Diary cookie partition.

All request headers, cookies, JSON fields, bootstrap credentials, exchange
values and database rows are untrusted. The frozen origin map, role contract,
resolver source, accepted runtime/persistence code, injected synthetic registry
and PostgreSQL transaction semantics are trusted within this tranche.

Assumptions are high-entropy opaque values, TLS termination outside this local
proof, parameterized SQL, browser enforcement of `__Host-`, Secure, HttpOnly,
SameSite=None and Partitioned attributes, no arbitrary SQL execution through
the route layer, and no direct writer outside the coordinator. Real identity,
rate limiting, operational secrets, proxy header trust and deployed Office
cookie behavior are explicitly unproved.

## Attacker stories and controls

### A broad runtime role escapes auth scope

An injected query reads product users, practices, patients or appointments, or
updates/deletes auth audit evidence.

Controls:

- the capability role is NOLOGIN, non-superuser, non-creator,
  non-replicating and non-bypass-RLS;
- it receives exact grants only on the five auth tables, audit sequence and
  resolver;
- it has no schema CREATE, product-table or role-admin privilege;
- state tables omit DELETE/TRUNCATE/REFERENCES/TRIGGER; audit omits
  UPDATE/DELETE; and
- acceptance proves the positive and negative privilege matrix under the
  effective role.

Residual risk: local acceptance uses `SET ROLE` from a privileged connection
and does not prove deployment login credential isolation or pooler behavior.

### Token bootstrap becomes a tenant-enumeration oracle

Before practice context exists, an attacker calls a broad lookup or observes
different errors for unknown, expired and foreign sessions.

Controls:

- the role has no pre-context table SELECT result because forced RLS sees no
  rows;
- one security-definer function accepts only an exact kind and SHA-256
  reference, has empty search path and returns at most one synthetic principal;
- public execute is revoked and only the capability role receives execute;
- the function makes no validity or authorization decision; and
- every externally visible invalid-session or exchange condition maps to the
  same 401 body.

Residual risk: response-shape equality does not prove constant-time database
behavior or internet-scale resistance to high-volume random-token probing.

### Caller forges practice context after bootstrap

A compromised runtime sets `app.current_practice_ref` to another practice and
uses otherwise valid table privileges.

Controls:

- route code never accepts practice context;
- the coordinator sets context only from the synthetic principal selected by
  the injected one-use registry or exact resolver result;
- all ORM queries remain parameterized and every mutable operation first locks
  the corresponding composite principal row; and
- no product table is accessible even if the auth-role context is misused.

Residual risk: PostgreSQL custom settings are not secrets and a database role
with arbitrary SQL execution can set them. RLS is defense in depth against
application defects, not containment of a fully malicious runtime principal.
Live identity mapping needs a separately reviewed stronger tenant-binding
design before product data opens.

### Cross-site request uses an ambient cookie

A hostile page causes login, refresh, exchange, rotation or logout with the
victim's cookie.

Controls:

- every endpoint requires an exact allowlisted HTTPS `Origin`;
- authority-changing endpoints require constant-time equality between the
  HttpOnly CSRF cookie and `X-EMR4-CSRF` header;
- login and unauthenticated exchange redemption first require a challenge
  fetched under CORS and retained in caller memory;
- cookies are `__Host-`, Secure, HttpOnly, Path=/, no-Domain, SameSite=None and
  Partitioned; and
- state/nonce/S256-PKCE and exact source/target origins additionally bind
  cross-surface redemption.

Residual risk: a script executing in an allowed origin can use the in-memory
CSRF value; content security policy and supply-chain controls remain necessary
at deployment.

### Login CSRF fixes the victim to an attacker session

An attacker submits their own synthetic bootstrap credential into another
browser partition.

Controls:

- bootstrap login requires a prior exact-origin CSRF challenge and custom
  header;
- bootstrap credentials are high entropy, hashed for comparison and consumed
  once;
- success replaces both session and CSRF cookies; and
- invalid and replayed bootstrap credentials share one external failure.

### Cookie theft or fixation preserves authority

A surface bearer is exposed to JavaScript, URLs, response JSON, logs or a
subdomain cookie, or the same value survives a requested rotation.

Controls:

- the raw bearer appears only in a Secure HttpOnly `__Host-` cookie;
- no Domain attribute or URL/query transport exists;
- parent bearers never leave the server;
- explicit rotation atomically revokes the old surface record and creates one
  replacement under the same parent/generation;
- login and exchange redemption always overwrite both cookies; and
- logout revokes before expiring cookies.

Residual risk: malware, browser compromise and TLS endpoint compromise remain
outside the repository proof.

### Third-party cookie behavior breaks Word Online

Word Online blocks or partitions the session cookie, causing silent fallback
or an unintended bearer in JavaScript.

Controls:

- Partitioned is explicit and each surface receives its own surface binding;
- Word-to-Diary trust uses the accepted short-lived single-use exchange rather
  than sharing a cookie;
- missing cookies fail closed with no local-storage or bearer-header fallback;
  and
- the claim is repository protocol evidence only until a supervised real
  Office compatibility gate is separately authorised.

### Detailed denial leaks identity or session state

An attacker distinguishes unknown user, wrong practice, revoked session,
expired session, consumed exchange or role change.

Controls:

- request validation emits bounded generic route errors;
- all `AuthRuntimeDenied` reasons collapse to one 401 response;
- CSRF/origin problems collapse to one 403 response;
- infrastructure/audit failure collapses to one 503 response; and
- internal reason codes remain typed metadata audit only and never appear in
  response bodies or headers.

### Audit failure diverges from cookie authority

The browser receives a new cookie after the database transaction failed, or
logout clears a cookie before revocation was durably audited.

Controls:

- the transport mutates response cookies only after the coordinator returns;
- required audit flushes before state in the same transaction;
- failure returns 503 without a replacement cookie;
- logout revokes first and clears only after success; and
- acceptance injects an audit outage and compares database and response-cookie
  state before and after.

### Pool exhaustion or held locks create denial of service

Slow clients or external work hold the principal lock, or a query runs without
a bound.

Controls:

- request parsing, origin/CSRF checks and bootstrap-registry work occur before
  database entry;
- transactions contain only resolver, local runtime, audit and state work;
- statement, lock and idle-in-transaction timeouts are set locally before
  bootstrap; and
- no network, provider, browser, Office, file, subprocess or human work occurs
  while locked.

Connection-pool capacity, proxy timeouts and load testing remain operational
decisions.

### Cleanup or role provisioning targets unrelated state

Acceptance drops an existing role/database or leaves a usable login behind.

Controls:

- database and roles use unique allowlisted task prefixes;
- the runner refuses any pre-existing target;
- the parameterised role contract never accepts an arbitrary identifier;
- cleanup targets only values created by that run; and
- final residue proves database, capability role and probe membership absent.

## Severity calibration

### Critical

- raw persisted or returned surface bearer permits reusable application-session
  takeover;
- the runtime role reads product or foreign-practice data; or
- two exchange consumers receive valid target cookies.

### High

- CSRF/origin bypass performs login, rotation, exchange or logout;
- old bearer remains valid after successful rotation/logout;
- audit failure still returns a new authoritative cookie; or
- resolver or response errors enumerate principals or exact session state.

### Medium

- role grants exceed the frozen auth-table operation matrix without reaching
  product data;
- unbounded locks allow a local denial of service; or
- Partitioned cookie incompatibility prevents Word Online while failing closed.

### Low

- malformed synthetic transport input is rejected before database entry;
- a deleted cookie repeats security attributes but a test client ignores an
  unknown Partitioned attribute; or
- evidence omits timing while all authority, state and cleanup claims remain
  intact.

Repository: EMR4
Version: 8fa732592fbee4f57c322b13d9d8ff89fcc7fa33
