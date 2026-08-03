# Raisa provider-free native-Diary application-session practitioner runtime plan

Date: 2026-08-03

Status: provider-free unmounted runtime + direct HTTP/PostgreSQL evidence (Diary lane step 2)

Parent: `provider_free_native_diary_application_session_practitioner_composition_architecture_pass`

## Outcome sought

Implement the next bounded Diary descendant as a new-file-only, provider-free,
unmounted/default-off native-Diary application-session composition wrapper plus
a direct loopback HTTP/PostgreSQL authored-synthetic acceptance harness.  The
accepted shared router is not strict enough by itself: it intentionally accepts
`practiceId`, display-safe field subsets and bounded pagination variations.  The
accepted native-Diary contract instead requires one fixed request with no
client-selected practice or projection.  This step therefore adds a stricter
outer pre-auth admission guard and reuses the accepted bridge/router unchanged
underneath it.

The feature is default-off.  When disabled, the factory returns an application
with no product route, no docs and no OpenAPI and opens no DB/session.  Only
literal explicit enablement constructs the accepted shared practitioner router
bound server-side to exactly `Surface.NATIVE_DIARY` beneath the bounded pre-auth
guard.

## Authority

This tranche inherits Yuri's standing authority for bounded logical descendants
of the accepted composition architecture and the Diary lane sequence.  It may
author the five owned implementation artifacts and publish them to the task
branch.  It may not edit `AGENTS.md`, `docs/branding/`, previously accepted
artifacts, shared auth/product-read/GraphQL modules, models, migrations, routes,
`app/main.py`, API Spine artifacts, workflows, harness settings, protected
evidence or other agents' files.  It may not mount in `app.main`, run a live
provider, read real identity, release a product row outside the exercised
authored-synthetic acceptance, write product state, deploy, rebuild Pages or
move a protected ref.  No runtime or usability claim beyond the exercised
provider-free authored-synthetic evidence is made.

## Frozen runtime contract

1. `create_native_diary_application_session_app(*, enabled, bridge)` exposes one
   task-local FastAPI/ASGI app.  Default disabled returns an app with no product
   route, no docs, no OpenAPI and opens no DB/session.
2. Only literal explicit enablement (`enabled is True`) constructs the accepted
   shared practitioner router bound server-side to exactly
   `Surface.NATIVE_DIARY`.
3. A bounded ASGI-level pre-auth guard protects the exact product path.  It
   buffers/replays at most 8192 bytes and requires POST, `application/json`,
   the fixed query constant, exact variables `{activeOnly: true, limit: 200,
   offset: 0}`, no `practiceId`, no alias, fragment, directive, introspection,
   mutation, field subset/extra field, pagination drift or extra JSON key.
   Any deviation is rejected generically with 403 and `Cache-Control: no-store`
   before bridge authentication.
4. The exact projection is `{id, displayName, roleLabel, active, defaultLocation
   {id, name}}`.  No policy/action/resource/surface/query argument is accepted
   from callers.
5. The shared bridge and current native Diary assets remain byte-for-byte
   unchanged.  No bearer/localStorage fallback and no REST fallback is added on
   the enabled application-session path.
6. The native Diary is a long-lived browser surface, not an Office one-use
   terminal.  Two sequential exact reads succeed on the same session with the
   same active rows, no-store and required allow audit before release.
7. Session revocation is backend-owned.  After revocation the next request is
   denied with 401 and no product row is released.

## Direct acceptance harness

- Use a unique allowlisted disposable PostgreSQL database; upgrade to current
  head and check it, with no migration change.
- Create unique finite auth LOGIN/NOLOGIN and product-read LOGIN/NOLOGIN roles
  using the accepted role builders; seed only authored-synthetic current,
  inactive and foreign-practice adversaries.
- Create a `Surface.NATIVE_DIARY` session at one exact synthetic HTTPS origin,
  separate auth/product pools, the accepted registry/bridge, and an explicitly
  enabled task app on a real loopback socket.
- Prove two sequential exact reads succeed on the same session with two active
  same-practice rows, exact projection, no-store and required allow audit before
  release.
- Revoke the session and prove the next request is 401 with no product row.
- Fail closed on wrong origin, missing/mismatched CSRF, Word-surface session,
  unknown/unmapped session, stale role, inactive user, required-audit outage,
  GET, mutation/introspection, practiceId, field subset/extra field,
  activeOnly/limit/offset drift and query/operation drift.
- Prove inactive/foreign/sensitive columns absent and direct role privilege
  escalation/writes denied.  Persist counts, booleans, safe reason/status codes
  and hashes only, never DSN, database/role names, passwords, UUIDs, names,
  cookie/session/CSRF values or authority envelopes.
- Stop listener/thread, dispose all engines, drop database and four roles in
  reverse order and verify complete absence even after failure.
- Evidence label is exactly `live_local_backend_postgres`; zero provider,
  browser, real identity, patient/clinical, product write, deployment or
  production claims.

## Deterministic acceptance cases

- The factory default-off posture is proven (no product route, docs, OpenAPI,
  DB/session).
- The exact `Surface.NATIVE_DIARY`, policy/action/resource and read/projection
  binding is proven.
- The pre-auth guard rejects every non-exact request before the bridge runs and
  admits the one fixed request.
- The long-lived native session behavior (two sequential reads) and
  post-revocation denial are proven by live loopback evidence.
- No forbidden dependency surface and no bearer/REST fallback is added.
- `git diff --check` passes and `docs/branding/` remains absent from the index.

## Residual risks

- The evidence does not prove rejection of an already-returned in-flight
  response before UI render; request-time freshness and post-revocation denial
  are not a UI reconciliation proof and that remains a later UI reconciliation
  obligation.
- Native-Diary UI wiring and browser rendering are separate later steps; this
  step claims no UI behavior.  There is no browser automation and no browser
  evidence here.
- There is no provider call, no real identity, no patient/clinical read and no
  product write.  Real identity, production and release suitability are not
  established.

## Implementation handoff

The owned files are the adapter module, this plan, the security threat-model
delta, the direct acceptance script and its focused deterministic test.  Every
write, provider, real identity, deployment and default-on switch remains closed.
The acceptance script writes its evidence only when root later runs it to
`orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-runtime/live-local-backend-postgres-evidence.json`; it is not created or committed now.
