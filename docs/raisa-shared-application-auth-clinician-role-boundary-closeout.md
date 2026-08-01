# Raisa shared application-authentication and clinician-role boundary — closeout

## Result

Accepted architecture result:
`raisa_shared_application_auth_clinician_role_boundary_architecture_pass`.

This repository-local, provider-free tranche defines one EMR4-backend-owned
authentication and authorization boundary for desktop Word, Word Online and
the native Diary. It introduces no runtime authentication implementation and
does not authorize a product-derived read.

## Frozen boundary

EMR4 application identity is canonical. Microsoft or Office signed-in state
may become an authentication input only after a separately authorized identity
integration; it is never an application role, practice, clinician or resource
authorization decision.

Every protected request must reach the same backend decision function. That
function uses fresh server-side state and admits the initial clinician-read
policy only when all of the following are true:

- the EMR4 parent and surface sessions are active, unexpired and unrecalled;
- the current backend user is active and has the `GP` role;
- the user has an active practitioner link in the same practice;
- the requested resource belongs to that practice; and
- the required metadata-only audit record succeeds before data access.

Receptionist, Nurse, Admin and PracticeOwner roles do not imply the initial
clinician-read authority. Client, URL, Office-host and document claims are
non-authoritative.

## Session and cross-surface trust

The accepted design uses opaque server-side parent and surface sessions. The
architecture caps the parent at eight absolute hours and each surface at 30
idle minutes. Password reset, logout, deactivation, practice or role change,
practitioner unlink and administrative revocation advance centralized
revocation state so every surface fails closed on its next backend request.

Word-to-Diary handoff uses a 60-second maximum, single-use, atomically consumed
metadata grant bound to source surface, target surface, exact origins,
audience, state, nonce, parent-session generation and an S256 PKCE challenge.
No bearer token, cookie, Office identity or clinical data is transported.

## Evidence

The deterministic architecture harness evaluates 23 authorization cases and
13 cross-surface exchange cases. All expected results match. The same allow
policy is equivalent across desktop Word, Word Online and the native Diary;
expiry, idle expiry, revocation, role, practitioner linkage, practice scope,
audit, replay, origin, audience, state, nonce and PKCE failures close before
product-data access.

All 16 focused tests pass with repository `conftest.py` disabled. Consequently
the database engine and its autouse write fixture were not loaded. Recorded
provider, identity-provider, Microsoft/Office identity, cloud/IAM, backend,
database, product-data, patient/clinical-field, appointment-command,
microphone, document-mutation and deployment counts are all zero.

An expanded 165-test no-`conftest` suite also passes across the auth primitives,
API Spine, dual-host and Clinician One contracts, compact companion, accepted
Word desktop/Online gates, Continuity and Compass.

## Limits and next gate

The result proves a consistent, typed, testable authorization architecture. It
does not prove live EMR4 login, secure cookies, database-backed session or
revocation state, external identity federation, live audit persistence, any
product-derived read, real-data safety, organisational Office deployment,
production fitness or release readiness.

Any runtime implementation is a new descendant requiring explicit authority.
Its first safe increment should implement only backend-owned session,
revocation, exchange and audit primitives against authored-synthetic test data,
with product reads still closed.

## Notification

The required non-PHI closeout notification was attempted. Pushover returned
`no active devices to send to`, so delivery did not occur.
