# Raisa shared application-authentication runtime foundation plan

Date: 2026-07-31

Owner: Yuri / GPT Sol

Status: `authorised_repository_local_authored_synthetic_implementation`

## 1. Authority

This is the first implementation descendant of
`raisa_shared_application_auth_clinician_role_boundary_architecture_pass`.
Yuri authorised the Compass candidate for a repository-local server-side
session, revocation, single-use exchange and metadata-audit foundation while
product-derived reads remain closed.

The authority permits one route-free service-layer implementation, an explicit
authored-synthetic in-memory adapter, deterministic tests, threat controls and
provider-free acceptance evidence. It does not permit a FastAPI or GraphQL
route, cookie issuance, a database table or migration, external identity,
Microsoft/Office account access, cloud/IAM mutation, deployment or product
data access.

## 2. Objective

Implement the frozen architecture as reusable backend-owned primitives that:

1. create an opaque parent application session and a separate opaque binding
   for one of `word_desktop`, `word_online` or `native_diary`;
2. enforce the eight-hour maximum parent lifetime, 30-minute maximum idle
   lifetime and the rule that a surface cannot outlive its parent;
3. invalidate existing sessions through a centralized principal generation as
   well as explicit parent and surface revocation;
4. issue a 60-second maximum, single-use Word-to-Diary exchange bound to the
   parent generation, source/target surfaces, exact origins, audience, state,
   nonce and S256 PKCE challenge;
5. consume the exchange atomically and create only the target surface binding;
6. retain only cryptographic hashes of opaque session and exchange material;
7. record bounded metadata audit events before every successful mutation; and
8. fail closed without changing state whenever required audit is unavailable.

## 3. Implementation boundary

The runtime foundation lives in `app/services` but has no module-level
instance, router import, dependency injection binding, cookie behavior,
database dependency, provider dependency, network client or process actuator.
Construction requires all of:

- an explicit authored-synthetic in-memory store;
- an explicit audit sink;
- an exact origin for each of the three surfaces; and
- optional injected clock and token source for deterministic verification.

The accepted architecture evaluator remains the source of the
`clinician_workspace.read` policy. This tranche returns only a freshly
validated synthetic server principal snapshot; it neither reads a resource nor
turns that snapshot into a product authorization capability.

## 4. Frozen runtime choices

### 4.1 Secret handling

Parent, surface and exchange values use cryptographically random opaque
material by default. The in-memory store and audit sink retain only
`sha256:`-prefixed hashes. PKCE uses RFC 7636 S256 with constant-time comparison.
Raw values exist only in the one-time return object and method input needed by
a future transport layer, which is outside this tranche.

### 4.2 Authored-synthetic isolation

The adapter accepts only the exact data class `authored_synthetic`, and all
principal, practice and practitioner references must use a `synthetic-`
prefix. This intentionally prevents the foundation evidence from being
mistaken for a live identity or product session store.

### 4.3 Atomicity and required audit

The in-memory store serializes every check-and-mutate sequence. An audit sink
must accept each operation's event batch atomically. For successful creation,
refresh, issue, redemption or revocation, audit admission happens before the
state change. If audit admission raises, the service returns
`required_audit_unavailable` and makes no state change. Redemption marks the
grant consumed and installs the target surface inside the same critical
section.

### 4.4 Failure closure

Unknown, missing, expired, idle-expired, revoked, wrong-generation,
wrong-surface, wrong-origin, wrong-audience, wrong-state, wrong-nonce and
wrong-PKCE conditions are typed denials. They do not create or refresh a
session, consume a grant, call a fallback or release product data.

## 5. Acceptance gates

### Gate A — five-source receipt

- Restore the full live baton, authority allocation, active acceptance,
  protected boundaries and exact Git/worktree state.
- Record a passing receipt with worker dispatch disabled.
- Preserve the accepted uncommitted architecture artifacts and every unrelated
  user change.

### Gate B — session and revocation primitives

- Only hashes are stored; raw parent and surface values are absent from state
  and audit.
- All three surfaces can be bound only to their exact configured origin and
  audience.
- Absolute, idle, explicit and generation revocation fail closed.
- A refreshed surface never outlives its parent.

### Gate C — cross-surface exchange

- Word desktop and Word Online can each create one native-Diary binding.
- Concurrent redemption admits exactly one consumer.
- Expiry, replay and every frozen binding mismatch deny without target-session
  creation.
- Raw code, verifier, state and nonce are absent from stored and audited state.

### Gate D — metadata audit

- Every successful mutation is preceded by an admitted typed audit batch.
- Audit failure leaves store counts and record states unchanged.
- Audit records contain the frozen required metadata fields and none of the
  forbidden credential, Office, document, patient or clinical fields.

### Gate E — non-wiring and provider-free verification

- Focused tests run with `--noconftest` so database fixtures are disabled.
- Static checks prove no FastAPI, SQLAlchemy, database, provider, HTTP, socket,
  subprocess, route or cookie integration in the runtime module.
- Existing shared-auth, legacy auth, dual-host, Word companion, Continuity and
  Compass regressions pass without database fixtures.
- Python compilation, Ruff, JSON validation and `git diff --check` pass.

## 6. Closed boundaries

Provider calls, patient or product-derived data, clinical authority, database
reads or writes, appointment commands, microphone capture, document mutation,
organisational Office deployment, external IAM/identity-provider/cloud changes,
production and release remain closed.

No result from this tranche authorises a route, cookie, persistence adapter,
Office message integration, product read or live identity. Each is a later
explicit gate.

## 7. Candid claim limit

A pass can prove that the frozen session, generation-revocation, one-use
exchange and required-audit rules work atomically in a route-free
authored-synthetic in-memory service. It cannot prove live login, cookie
security, durable or distributed revocation, database transaction behavior,
external federation, browser behavior, product-data safety, deployment,
production fitness or release readiness.
