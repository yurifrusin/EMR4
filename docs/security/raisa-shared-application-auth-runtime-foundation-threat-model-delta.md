# Threat-model delta — Raisa shared application-auth runtime foundation

Date: 2026-07-31

Status: `repository_local_authored_synthetic_runtime_foundation`

## Overview

This delta narrows the accepted shared-authentication architecture threat model
to its first server-side implementation. It covers an unmounted service-layer
runtime and explicit in-memory authored-synthetic store only. The parent
architecture in
`docs/security/raisa-shared-application-auth-clinician-role-boundary-threat-model-delta.md`
remains authoritative for identity, clinician role, practice scope and
product-read authorization.

No route, cookie, database, external identity provider, Office identity,
provider call, product-derived data, patient or clinical data, command,
deployment, production or release is opened by this implementation.

## Threat Model, Trust Boundaries, and Assumptions

### Assets and privileges

- opaque parent and surface session material;
- principal revocation generation and session status;
- single-use cross-surface exchange material;
- exact surface, origin, audience, state, nonce and PKCE bindings;
- metadata-audit integrity; and
- the boundary between a validated session context and product authority.

### Trust boundaries

1. A future transport caller to the unmounted service API.
2. Raw opaque values to their hash-only server-side records.
3. The runtime coordinator to the authored-synthetic store lock.
4. The runtime coordinator to the required audit sink.
5. A Word source binding to a native-Diary exchange redemption.
6. Injected deterministic test time/tokens to cryptographic production
   defaults that remain unwired.

Method inputs are untrusted. The service's exact origin map, server principal,
store lock, clock and audit sink are trusted construction inputs. The in-memory
adapter is process-local, disposable and intentionally unsuitable for live or
distributed use.

Assumptions are a monotonic-enough timezone-aware UTC source, cryptographically
random default token material, no bypass around the store lock, and an audit
sink whose batch operation is atomic. A future durable adapter must re-establish
these properties transactionally rather than inheriting this evidence.

## Attack Surface, Mitigations, and Attacker Stories

### Stored token theft enables session takeover

An attacker reads process state, diagnostic output or audit events and obtains
a reusable parent, surface or exchange value.

Controls:

- store keys and record fields contain only SHA-256 hashes;
- audit records accept no arbitrary metadata and contain hash references only;
- raw values are excluded from exceptions and snapshots; and
- cryptographically random opaque values are the default when no deterministic
  test source is injected.

Residual risk: a live transport would still hold raw material transiently and
requires separately reviewed Secure HttpOnly cookie or same-origin BFF
handling.

### Exchange replay or concurrent double redemption

Two callers redeem the same Word-to-Diary exchange before either observes the
other.

Controls:

- verification, audit admission, consumed-state transition and target binding
  occur under one store lock;
- the consumed flag is terminal; and
- concurrency acceptance requires exactly one successful redemption.

Residual risk: a distributed or database-backed adapter needs a unique
constraint or compare-and-set transaction; the process-local lock is not proof
of that future behavior.

### Confused deputy through binding substitution

A caller changes the source/target surface, exact origin, audience, state,
nonce or PKCE verifier to redeem another context's grant.

Controls:

- every binding is stored in hashed or non-secret server-side grant state;
- all supplied values must match before consumption;
- secret-derived comparisons use constant-time comparison; and
- only Word desktop or Word Online to native Diary is admitted.

### Logout or role loss leaves another surface active

A principal generation changes while an old parent, surface or exchange still
appears unexpired.

Controls:

- parents, surfaces and grants bind the generation current at creation;
- every validation, issue and redemption compares it with centralized current
  generation; and
- logout-everywhere advances generation and revokes matching parents inside one
  critical section.

Residual risk: this tranche has no live user/role/practitioner reload or event
source. A future persistence adapter must advance generation transactionally
when those backend facts change.

### Audit failure creates unaudited authority

The audit sink rejects or partially records an event after the session store
has changed.

Controls:

- successful state changes call atomic `record_batch` before mutation;
- an audit exception maps to `required_audit_unavailable` without mutation; and
- tests compare complete before/after store snapshots for every audit-failure
  path.

Residual risk: the in-memory sink and store are separate objects. A durable
implementation requires one transaction or transactional outbox; this tranche
does not claim crash consistency between processes or storage systems.

### Time rollback extends a session or exchange

A faulty injected clock moves backward and refreshes idle expiry beyond the
previously established boundary.

Controls:

- all time values must be timezone-aware;
- refresh expiry is capped by parent absolute expiry; and
- the runtime rejects a clock observation earlier than the record's last
  observed time.

### Synthetic foundation is accidentally wired as live authentication

A developer imports the service into a router and passes real identifiers or
attaches a persistence/network adapter without a new review.

Controls:

- construction requires an adapter whose exact data class is
  `authored_synthetic`;
- identity references require a `synthetic-` prefix;
- there is no module-level runtime instance or router/dependency import; and
- static acceptance checks reject FastAPI, SQLAlchemy, database, HTTP, socket,
  subprocess, cookie and route wiring.

Residual risk: repository code can be changed later. Git review and a new
authority/acceptance tranche remain mandatory before integration.

## Severity Calibration (Critical, High, Medium, Low)

### Critical

- raw stored session/exchange material permits reusable account takeover;
- concurrent exchange redemption creates two valid target sessions; or
- the synthetic foundation is connected to product-derived clinical reads or
  appointment writes without the backend authorization gate.

### High

- generation revocation is not checked at validation or redemption;
- origin/audience/PKCE substitution binds an attacker-controlled Diary; or
- audit failure still changes session, grant or revocation state.

### Medium

- a clock rollback extends idle validity without exceeding the absolute parent
  expiry;
- detailed denial codes become a remote enumeration oracle after future route
  wiring; or
- an explicit surface logout leaves another surface active while the UI claims
  logout-everywhere.

### Low

- a malformed authored-synthetic identifier fails a local test;
- a safe snapshot shows a stale status while raw secrets and authority remain
  unavailable; or
- an invalid deterministic token source causes a collision and fails closed.

Repository: EMR4
Version: 8fa732592fbee4f57c322b13d9d8ff89fcc7fa33
