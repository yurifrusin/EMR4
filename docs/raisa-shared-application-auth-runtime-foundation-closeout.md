# Raisa shared application-authentication runtime foundation closeout

Date: 2026-07-31

Result: `raisa_shared_application_auth_runtime_foundation_pass`

## Outcome

The separately authorised repository-local runtime foundation passes. An
unmounted EMR4 service now implements the frozen parent-session,
surface-binding, expiry, centralized generation-revocation, single-use
Word-to-Diary exchange and required metadata-audit primitives using only an
explicit authored-synthetic in-memory store.

This is not live authentication. No FastAPI or GraphQL route imports the
service, no cookie is issued, no database or persistence adapter is present,
and no external identity, Office account or product data is touched.

## Implemented boundary

- Each parent and surface session is an opaque value whose store record retains
  only a SHA-256 reference.
- `word_desktop`, `word_online` and `native_diary` each require the exact
  configured HTTPS origin and the `emr4-api` audience.
- Parent absolute lifetime cannot exceed eight hours; parent and surface idle
  lifetime cannot exceed 30 minutes; surface expiry cannot exceed the parent.
- Explicit surface/parent revocation and centralized principal-generation
  advancement fail closed on the next validation, issue or redemption.
- Word desktop and Word Online may issue only a native-Diary exchange, valid
  for at most 60 seconds and bound to parent/generation, source and target,
  exact origins, `emr4-session-exchange`, state, nonce and S256 PKCE.
- Exchange verification, required-audit admission, single-use consumption and
  target-surface creation are serialized in one in-memory critical section.
- Successful mutations admit a typed audit batch before changing state. Audit
  failure returns `required_audit_unavailable` with the store unchanged.
- Synthetic principal, practice and practitioner references and correlation
  IDs are bounded slugs; Microsoft/Office identity and client claims do not
  exist in the runtime inputs.

## Acceptance evidence

The deterministic provider-free evidence records:

- three admitted surface-session cases;
- three fail-closed explicit/generation revocation cases;
- two exact Word-to-Diary admissions, each consumed once;
- eight binding-mismatch denials with unchanged store state;
- one two-thread redemption in which exactly one caller succeeds and the other
  receives `exchange_already_consumed`;
- three audit-outage cases—create, redeem and revoke—with unchanged state; and
- static absence of FastAPI, GraphQL, SQLAlchemy, database, HTTP/provider,
  socket/process, cookie and router wiring.

All 32 focused tests pass with repository `conftest` disabled. The corrected
expanded 145-case no-`conftest` auth, API Spine, dual-host, Clinician One, Word
companion, Continuity and Compass suite also passes. An initial expanded
selection named seven tests that intentionally require the disabled database
fixtures; those were unavailable at setup and produced no runtime assertion
failure.

Python compilation and Ruff pass for the runtime, evidence generator and test.
Provider, identity-provider, Microsoft/Office identity, cloud/IAM, route,
cookie, database read/write, product-data, patient/clinical-field,
appointment-command, microphone, document-mutation and deployment counts are
all zero.

## Security disposition

The implementation-specific threat-model delta preserves the accepted parent
model. Hash-only storage reduces persistence/log theft exposure; exact binding
and constant-time secret-derived comparison close confused-deputy paths; the
store lock closes same-process replay races; and audit-before-mutation closes
the tested audit outage paths.

The accepted residual risk is deliberate: process-local locking is not evidence
of distributed atomicity, and separate in-memory store/audit objects are not
evidence of crash-consistent durable transactions. A database-backed adapter
must use a unique/compare-and-set redemption boundary plus a transaction or
transactional outbox. A future route must map detailed internal denials to a
non-enumerating external response and transport opaque values only in a
separately reviewed Secure HttpOnly cookie or same-origin BFF design.

## Preserved closed boundaries

The frozen Sydney development service remains unchanged at revision
`raisa-office-web-dev-00006-xf9` and digest
`sha256:8e06f07e4efd393f38275348d8bd7b136e664c2797c399a89207b66116839324`.
Its zero-authority posture and resource limits were not broadened.

Provider calls, patient or product-derived data, clinical authority, database
reads or writes, appointment commands, microphone capture, document mutation,
organisational Office deployment, external IAM/identity-provider/cloud changes,
production and release remain closed. Protected holdouts were not inspected.

## Claim limit and next gate

This result proves one route-free authored-synthetic in-memory implementation
of the frozen primitives. It does not prove live login, secure browser-cookie
behavior, durable/database-backed or distributed revocation, external
federation, live audit persistence, product-read safety, organisational
deployment, production fitness or release readiness.

The next safe candidate is a separately authorised PostgreSQL persistence and
transaction tranche for parent/surface sessions, generation revocation,
single-use exchange and metadata-only audit using disposable authored-synthetic
fixtures. It should still add no login route, cookie, external identity or
product-derived read. That candidate requires fresh authority because it opens
database schema/migration and test-write boundaries.

## Notification

The required non-PHI sprint-closeout Pushover notification was attempted with
the engine marked paused for fresh PostgreSQL schema/migration and disposable
test-write authority. Delivery failed with `no active devices to send to`; no
push notification was delivered.
