# Threat-model delta — Raisa shared application authentication and clinician role

Date: 2026-07-31

Status: `repository_local_architecture_only`

## Overview

This scoped delta covers the planned application-authentication boundary shared
by desktop Word, Word Online and the native Diary. It preserves the repository
security policy: the FastAPI/PostgreSQL backend remains authoritative for
identity, authorization, practice scope, clinical/Diary truth and audit.

No runtime identity system is added by this tranche. Its assets are typed
policy, deterministic authored-synthetic decisions and acceptance evidence.
Patient or product-derived data, live sessions, databases, identity providers,
cloud/IAM changes, providers, writes, production and release remain closed.

## Threat Model, Trust Boundaries, and Assumptions

### Assets and privileges

- EMR4 user and practice identity;
- clinician role and same-practice practitioner linkage;
- parent and surface sessions;
- product-derived clinical/Diary read authority;
- cross-surface exchange grants;
- authorization and audit integrity; and
- the separation between read authority and command/write authority.

### Trust boundaries

1. Human/browser/Office host to EMR4 authentication endpoint.
2. Microsoft/Office identity and host state to EMR4 application identity.
3. Word taskpane to native Diary through Office dialog messaging.
4. Each surface to the EMR4 backend authorization function.
5. Backend decision to database query and protected response release.
6. Backend decision to durable audit admission.

The browser, URL, Office message, client role/practice claim, host profile and
Microsoft signed-in state are attacker-controlled or untrusted. The EMR4
session store, current user/practice/role/practitioner records, endpoint policy
and audit writer are trusted backend inputs. Developer fixtures are
authored-synthetic and grant no runtime authority.

Assumptions for the future implementation are TLS, exact application-origin
allowlists, HttpOnly cookie transport or a same-origin BFF, cryptographically
random opaque identifiers, atomic grant consumption and trusted server time.

## Attack Surface, Mitigations, and Attacker Stories

### Office identity is mistaken for EMR4 identity

An attacker signs into any Microsoft account or loads the manifest and is
treated as an EMR4 clinician.

Controls:

- Office identity and host readiness are explicit non-authority inputs;
- only the EMR4 backend maps an authenticator to an active user/practice; and
- Microsoft federation, if later added, terminates in an EMR4 session and does
  not supply the authorization result.

### Client role or practice claims escalate authority

A modified taskpane changes a JWT/UI role, practice ID or button state to gain
clinical access.

Controls:

- the backend reloads the active user and current role;
- the endpoint selects a server-owned action/resource policy;
- `GP` plus active same-practice practitioner linkage is required; and
- client claims and affordances cannot influence the decision.

### Token theft through web storage, URL or dialog relay

Script injection, browser history, logs or a malicious dialog origin steals a
bearer token currently copied through client surfaces.

Controls:

- raw session/bearer material is forbidden in local/session storage, URLs and
  Office messages on the protected path;
- future surfaces use Secure HttpOnly cookies or same-origin BFF transport; and
- dialog messages carry only a 60-second single-use PKCE-bound opaque code.

### Cross-surface exchange replay or confused deputy

A grant issued by Word Online is redeemed by another origin, another surface,
after logout or more than once.

Controls:

- exact source/target surface, origin and audience binding;
- state, nonce and PKCE S256;
- atomic single-use consumption and 60-second maximum lifetime; and
- fresh parent-session generation check at redemption.

### Stale role or session survives revocation

A removed GP, inactive practitioner or logged-out user keeps an unexpired
stateless token and continues reading product data.

Controls:

- server-side parent and surface session records;
- current user/role/practice/practitioner reload on every protected request;
- revocation-generation mismatch denial; and
- surface expiry bounded by parent absolute and idle expiry.

### Cross-practice data disclosure

A valid clinician substitutes another practice/resource identifier.

Controls:

- practice is taken from the current backend principal, not the client;
- session, user, practitioner and resource practice must all agree;
- the authorization decision runs before the protected query; and
- PostgreSQL practice scoping/RLS remains an independent downstream control.

### Audit bypass releases an untraceable clinical read

An audit outage or partial failure causes data to be returned without the
required read record.

Controls:

- required audit admission is part of the clinician-read decision;
- unavailable audit returns 503 and releases no product data; and
- a later implementation should use a durable transactional outbox or
  equivalent atomic boundary.

### UI allow state is reused as a capability

One surface caches an allow decision and forwards it to another surface or a
later command.

Controls:

- decisions are current-request-only and not bearer capabilities;
- every REST handler/GraphQL field invokes the same backend function; and
- commands re-evaluate independently with their own confirmation, freshness,
  idempotency and audit controls.

### Availability failure weakens security

The session store, policy, time source or audit writer is unavailable and the
client falls back to Office sign-in, cached JWT role or anonymous synthetic
mode.

Controls:

- unknown or unavailable state is deny;
- no fallback path exists for product-derived data; and
- hosted authored-synthetic regression capability remains separately labelled
  and cannot be promoted to product authority.

## Severity Calibration (Critical, High, Medium, Low)

### Critical

- a client-controlled role/practice value authorizes cross-practice clinical
  data at scale;
- a reusable dialog token or exchange code permits account/session takeover;
- Office sign-in alone grants clinician product access; or
- a compromised surface can bypass the backend and perform clinical or
  appointment writes.

### High

- revoked or inactive clinicians retain product-read access until a long token
  expires;
- cross-surface origin/audience confusion exposes another user's session; or
- required clinical-read audit can be bypassed while data is released.

### Medium

- denial reasons leak role/practice membership sufficient for targeted
  enumeration;
- logout revokes one surface but misleadingly leaves another active contrary
  to the stated user action; or
- a bounded same-practice operational read uses a stale affordance but is still
  independently denied for clinical data and commands.

### Low

- a redacted session-status projection shows an incorrect surface label without
  changing backend authorization;
- a malformed authored-synthetic fixture causes only a fail-closed local test
  error; or
- an unavailable host capability hides a button while all backend policy and
  product data remain untouched.

This delta does not assess a live session implementation, because none is
authorized or created here. The existing localStorage/token-relay mechanisms
remain development history and are explicitly not accepted for a protected
product-read path.

Repository: EMR4
Version: 8fa732592fbee4f57c322b13d9d8ff89fcc7fa33
