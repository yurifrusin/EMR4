# Raisa shared application-authentication and clinician-role boundary plan

Date: 2026-07-31

Owner: Yuri / GPT Sol

Status: `authorised_repository_local_provider_free`

## 1. Authority

This is the first descendant of
`raisa_word_online_authenticated_companion_verification_pass`. Yuri authorised
a repository-local, provider-free architecture and acceptance tranche before
any product-derived read is allowed across:

- Word desktop;
- Word Online; and
- the native Diary.

The tranche may define typed contracts, authored-synthetic cases, a
deterministic decision harness, threat controls and acceptance evidence. It may
not establish a live user session, contact Microsoft or another identity
provider, inspect an Office account, read product data, change a database,
deploy code or mutate cloud/IAM state.

## 2. Objective

Freeze one backend-owned authentication and authorization architecture that:

1. establishes an EMR4 application identity separately from Office identity;
2. binds one parent application session to surface-specific sessions;
3. authorizes the initial Clinician One read role from fresh EMR4 records;
4. exchanges cross-surface trust through a short-lived single-use backend grant
   rather than copying a bearer token;
5. expires and revokes sessions centrally;
6. audits identity, session, exchange and authorization outcomes;
7. fails closed before product-derived data is fetched or released; and
8. returns one backend authorization decision consumed by all three surfaces.

## 3. Current-state evidence and migration boundary

The existing backend already supplies useful foundations:

- `app.dependencies.get_current_user` verifies a signed token, reloads the
  active user and rejects a practice mismatch;
- `require_role` and the GraphQL context use the backend user record;
- practice scope is propagated into PostgreSQL request state; and
- `UserRole.GP` plus an optional `practitioner_id` already express the first
  doctor/practitioner relationship.

The following development mechanisms are explicitly insufficient for a
product-derived cross-surface read and are not grandfathered by this plan:

- JWT bearer material retained in browser `localStorage`;
- UI authorization derived by decoding a client-held role claim;
- a bearer token relayed through an Office dialog message;
- stateless expiry without a server-side session/revocation record; and
- Word or Microsoft signed-in state treated as EMR4 identity.

No current runtime is changed by this tranche. A later implementation must
remove or isolate those mechanisms on the protected product-data path before
that path can be accepted.

## 4. Frozen architecture choices

### 4.1 Canonical identity

The EMR4 backend is the only authority that can establish the application
principal. Microsoft/Office identity, host capability and client assertions are
untrusted context. A future federation may validate a Microsoft assertion, but
the backend must map it to an active EMR4 user, practice and role and create an
EMR4 session; the external assertion never becomes the authorization decision.

### 4.2 Sessions and cross-surface trust

The target architecture uses an opaque server-side parent application session
and a separate surface binding for each of `word_desktop`, `word_online` and
`native_diary`. Browser surfaces receive only Secure, HttpOnly, SameSite-bound
session cookies from an EMR4 application origin or same-origin BFF. Raw session
or bearer material is forbidden in URLs, Office messages and web storage.

A surface opens another surface only through a backend-issued exchange grant
that is:

- single-use and atomically consumed;
- valid for no more than 60 seconds;
- bound to the active parent session and its revocation generation;
- bound to the exact source surface, target surface, origin and audience;
- protected by state, nonce and PKCE S256; and
- free of patient, clinical, document and Office-account data.

### 4.3 Initial clinician role

The first Clinician One product-read role is deliberately narrow:

- the fresh backend user role must be `GP`;
- the user must be active;
- the linked practitioner must exist, be active and belong to the same
  practice; and
- the requested resource practice must match that same practice.

`Nurse`, `Receptionist`, `Admin`, `PracticeOwner`, Office sign-in and host
readiness do not imply this clinician read authority. Any later role expansion
is a new policy decision.

### 4.4 One authorization decision

Every protected REST command and GraphQL field maps to a server-owned
action/resource policy. The backend loads the active session, current user,
practice membership, role, practitioner link, surface binding and revocation
generation, then evaluates one decision before data access. A UI affordance or
cached decision is never a grant.

The decision is request-scoped, names its policy version and correlation ID,
and is audited. A command must re-evaluate at command time even if a preceding
read was allowed.

### 4.5 Expiry and revocation

The development acceptance baseline requires:

- parent session absolute lifetime no greater than the existing eight-hour
  ceiling;
- surface idle lifetime no greater than 30 minutes;
- surface expiry never later than parent expiry;
- immediate denial after session revocation, user deactivation, role or
  practitioner loss, practice change, or revocation-generation change; and
- no silent fallback to a token-only or Office-identity path.

These are maximums, not production promises. A later production/privacy review
may shorten them but may not lengthen them without explicit review.

## 5. Acceptance gates

### Gate A — five-source rehydration

- Start on the required clean task branch and exact checkpoint.
- Read the full live handover, active plan/evidence/acceptance, Continuity 180,
  Compass 161 and its rendered report.
- Fetch and record all protected refs without moving them.
- Produce a passing receipt naming all five mandatory sources.

### Gate B — typed architecture

- A closed policy contract names all three surfaces and one backend decision.
- Application identity is explicitly separate from Microsoft/Office identity.
- The initial clinician role is the fresh backend `GP` plus same-practice active
  practitioner linkage.
- Session, exchange, expiry, revocation, audit and failure rules are explicit.
- Current localStorage, client-role and token-relay mechanisms are classified
  as inadmissible for product-derived reads.

### Gate C — deterministic authorization

- Equivalent valid authored-synthetic GP contexts from all three surfaces
  receive the same allow decision and policy version.
- Client role/practice claims and Office signed-in state cannot create or
  change an allow decision.
- Inactive, expired, idle-expired, revoked, wrong-generation, wrong-practice,
  wrong-role, missing-practitioner and audit-unavailable contexts fail closed.
- Authorization is evaluated before data access and emits no product data.

### Gate D — deterministic cross-surface exchange

- Valid Word desktop and Word Online grants can bind the native Diary once.
- Expired, replayed, wrong-origin, wrong-audience, wrong-surface, wrong-PKCE and
  revoked-parent grants fail closed.
- No fixture or decision contains a credential, bearer token, cookie, password,
  Office identifier, patient identifier, document content or clinical text.

### Gate E — verification and evidence

- Validate all JSON schemas and fixtures.
- Generate deterministic provider-free evidence.
- Run the focused new tests plus existing auth, API Spine, dual-host, companion,
  Continuity and Compass regressions serially.
- Run Python compilation, Ruff, JSON validation and `git diff --check`.
- Verify the task branch and all protected refs remain unmoved.

## 6. Closed boundaries

Provider calls, patient or product-derived data, clinical authority, database
reads or writes, appointment commands, microphone capture, document mutation,
organisational Office deployment, external IAM/identity-provider/cloud changes,
production and release remain closed.

This plan does not authorize a login route change, session table or migration,
cookie issuance, Entra/WorkOS/Google configuration, Office manifest change,
taskpane/Diary runtime switch, public endpoint, data read or deployment.

## 7. Candid claim limit

A pass can prove that one repository-local policy and deterministic evaluator
express the intended identity/session/role/trust boundary and fail closed over
authored-synthetic metadata. It cannot prove live authentication, browser
cookie behavior, Microsoft federation, database-backed revocation, real-data
safety, organisational deployment, production fitness or release readiness.
