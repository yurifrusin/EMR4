# Raisa shared application-auth Office cookie-compatibility plan

Date: 2026-08-01

Status: frozen implementation and acceptance contract

Authority: Yuri, 2026-08-01

Parent result: `security_finding_governance_pass`, protected integration
`1af54ae31895e863b447479aeb3b2bbcf0e684b8`

## Decision and purpose

Yuri authorised the next product tranche identified by the accepted shared
application-auth programme: one supervised, provider-free, authored-synthetic
exercise of the accepted session-cookie transport in installed Word and Word
Online.

The exercise asks one narrow question: can the existing Secure, HttpOnly,
SameSite=None, Partitioned application-session and CSRF cookies complete their
ordinary same-origin lifecycle inside each real Office taskpane host?

This descendant may add a task-scoped repository harness, two task-specific
development manifests, deterministic tests, sanitized evidence and ordinary
task-branch commits/pushes. It may use the existing reserved development
tunnel `https://property-cinch-backfield.ngrok-free.dev` only to relay HTTPS to
the local harness. Starting and stopping that already configured tunnel is a
temporary development action, not a cloud, IAM, catalogue or product
deployment.

## API Spine classification

Application authentication and session lifecycle remain REST command
semantics. The existing seven routes under
`/api/v1/application-auth` are the only backend surface:

- issue CSRF;
- establish one authored-synthetic session;
- validate, rotate and log out that session; and
- issue/redeem exchange grants, which remain present but are not needed by the
  host-cookie exercise.

No GraphQL or product read model, appointment/arrival/document command, new
route, OpenAPI behavior change, database migration or second authorization
engine is authorised. The harness must inject the existing transport and
operational guard explicitly; the product application remains default-off.

## Frozen exercise

The two surface runs are independent and ordered:

1. installed Word with surface `word_desktop`;
2. Word Online with surface `word_online`.

For each surface, a task-specific manifest opens an exact same-origin HTTPS
taskpane. A visible user gesture triggers this sequence using ordinary
`fetch(..., {credentials: "include"})` requests:

1. `POST /csrf`;
2. `POST /synthetic/session` with that surface's runtime-only, one-use
   authored-synthetic bootstrap value;
3. `POST /session/validate`;
4. `POST /session/rotate`;
5. `POST /session/validate` again;
6. `POST /session/logout`;
7. obtain a fresh pre-auth CSRF token and prove the logged-out session no
   longer validates.

JavaScript cannot read the HttpOnly cookies. Successful validation and
rotation through the ordinary router are the proof that the Office host stored
and returned them. The browser must not inspect cookie stores, local storage,
session storage, Office credentials or profile state.

## Task-scoped harness

- Runtime state is process-local `authored_synthetic` memory only. PostgreSQL,
  product models and external identity adapters are absent.
- One bounded synthetic principal and one unique one-use bootstrap value are
  created per Office surface at process start. Raw values are never logged,
  persisted, placed in URLs, committed or included in evidence.
- A bootstrap may be rendered only into its exact no-store taskpane response,
  is removed from the DOM/runtime after the one login attempt, and cannot be
  reissued. A reload after consumption fails closed.
- The exact current HTTPS origin is configured for all three runtime surface
  slots because the accepted runtime requires a complete map; requests must
  still declare and match their manifest-bound Word surface.
- The operational guard remains deny-only, bounded and metadata-only. Its
  task-owned in-memory denial sink persists no network or authentication
  material.
- The harness exposes no product router, static product asset, database,
  provider, credential adapter, Microsoft identity endpoint or command
  capability.
- The taskpane sends no `Authorization` header and uses no localStorage,
  sessionStorage, IndexedDB, URL credential, postMessage credential or
  document API fallback.

## Office and manifest boundary

- Each manifest has a fresh development add-in identifier and the minimum
  taskpane permission compatible with Office manifest validation.
- Source locations use the exact reserved HTTPS development origin and encode
  only the expected surface, never an authentication value or Office
  identifier.
- Installed Word and Word Online must each report the expected host/platform
  class. A host/surface mismatch stops before bootstrap submission.
- The harness must not call `Word.run`, inspect or mutate the document body,
  filename, URL, document id, tenant id, account id or Office token.
- No tenant catalogue, central deployment, administrator consent or Office
  policy change is authorised. If either host requires one, stop for Yuri.
- Use a new blank document for each supervised run or independently establish
  an existing blank authored-synthetic document without reading its body.

## Acceptance gates

### Gate A - rehydration and protected transition

- Complete the five-source Ariadne rehydration and commit the protected PR 69
  integration receipt.
- Prove local and origin `master` and `handoff/current` align at the protected
  merge commit before starting this branch.
- Preserve and exclude the concurrently supplied Raisa branding files.

### Gate B - static and deterministic security

- Tests prove the exact route allowlist, host/surface binding, no-store pages,
  one-use bootstrap behavior and sanitized closed evidence schema.
- Tests reject query credentials, unsupported surfaces, host mismatches,
  unexpected origins and all unbounded evidence fields.
- Source scans prove absence of bearer fallback, browser storage APIs,
  document APIs, cookie reads and product/backend routes outside the existing
  auth prefix.
- Existing shared-auth transport, operational-hardening, API Spine and
  security tests remain green.

### Gate C - installed Word

- A real installed-Word taskpane loads from the exact HTTPS development
  origin, reports `word_desktop`, and completes the visible-gesture sequence.
- Evidence records only host class, surface, step/status booleans, generic
  failure category if any and cleanup state.

### Gate D - Word Online

- A real signed-in Word Online taskpane loads from the same exact HTTPS
  development origin, reports `word_online`, and completes the same
  visible-gesture sequence.
- Automation may interact only with the blank task document and taskpane. It
  must not inspect cookies, browser profile/storage, unrelated tabs, account
  identity or document identifiers.

### Gate E - failure-closed behavior

- Missing/blocked/partition-incompatible cookies produce a candid surface
  failure; no bearer, storage, query-string or second-origin workaround is
  permitted.
- Bootstrap replay, post-logout validation, wrong surface and wrong origin
  remain generic denials and release no authority.
- A failure in one host cannot be described as a cross-host pass.

### Gate F - verification and residue

- Validate both manifests, focused Python/JavaScript/API tests, JSON/schema
  evidence, repository security gates and `git diff --check`.
- Stop only task-owned harness/tunnel processes and prove their listeners are
  absent. Do not stop unrelated development processes.
- Record zero provider, external-identity, product/database read, document
  mutation, command, cloud/IAM mutation, deployment, production or release
  events.

## Branding permission

Yuri authorised the new Raisa branding assets for future UI renders. This
cookie-compatibility control may remain visually minimal; permission to use
the assets does not require modifying or absorbing the concurrently owned
files. Public rename, domain, ASIC, trademark, deployment and release remain
closed.

## Candid claim limit

A pass can prove only that the accepted authored-synthetic in-memory session
cookie lifecycle worked once in each supervised Office host through the exact
development origin. It does not prove real identity or Microsoft federation,
cross-tenant compatibility, every Office/browser policy, product-data safety,
distributed abuse resistance, PostgreSQL behavior, organisational deployment,
production fitness or release readiness.

Until all gates pass, the only truthful result is
`raisa_shared_application_auth_office_cookie_compatibility_in_progress`.
