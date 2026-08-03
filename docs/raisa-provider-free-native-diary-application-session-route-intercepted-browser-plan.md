# Raisa provider-free native-Diary application-session route-intercepted browser plan

Date: 2026-08-03

Status: bounded authored-synthetic browser-rehearsal candidate (Diary lane step 4)

Parent: `provider_free_native_diary_application_session_ui_composition_pass`

## Outcome

Exercise the accepted default-off native-Diary application-session practitioner
composition in real Chromium through the ordinary static Diary page. Serve the
published HTML, JavaScript, CSS and both accepted ES modules from an ephemeral
loopback static server. Intercept only a closed set of authored-synthetic API
routes and one already-published static hosting-policy fixture. Block every
other non-loopback request.

The exact evidence label is `route_intercepted_browser` and the data class is
`authored_synthetic`. This is browser/DOM evidence, but it is not live backend,
PostgreSQL, real application-session injection, usability, default-on,
production or release evidence.

## Frozen browser boundary

- Load `docs/diary/diary.html?standalone_diary=true` from an ephemeral loopback
  static server; do not import or mount `app.main`.
- Install only an authored-synthetic JWT-shaped receptionist token and the
  already accepted exact three-key application-session bootstrap before the
  page scripts execute. The token has no signer, account, practice or product
  authority and never leaves the browser context.
- Use the same no-argument reader identity across the enabled lifecycle. Its
  successful output is the accepted exact `{status, rows}` fixed-read shape.
- Fulfil only the exact Diary read route-and-method pairs needed to let the
  ordinary page reach the practitioner composition. A wrong method on an
  allowlisted path fails closed. The fixtures contain no patient, appointment,
  clinical, real identity, document or product-derived data.
- Exercise ordinary visible controls for booking-gap opening, modal closing and
  Diary refresh. Direct fixture-state mutation may only hold/release the reader
  result or toggle the trusted bootstrap before a visible refresh; it may not
  call page-internal load, reconcile, render or command functions.
- Record DOM state, module request paths, phase-specific practitioner network
  counters, unknown routes, external hosts and console errors. Screenshots are
  intentionally excluded after root review because the frozen behavior is
  fully established by deterministic DOM/state evidence.

## Deterministic acceptance

1. The ordinary page identity is `EMR — Diary`, the page renders meaningful UI,
   and its real `application-session-practitioner-directory.mjs` and
   `application-session-practitioner-reconciler.mjs` resources load in enabled
   cases.
2. Exact enabled success calls the fixed reader and the visible booking modal's
   practitioner select contains exactly Avery Browser Synthetic and Morgan
   Browser Synthetic.
3. The enabled-success request ledger, captured before any bootstrap transition,
   contains zero GraphQL practitioner requests and zero legacy REST practitioner
   requests.
4. A held enabled read followed by bootstrap disable and visible Refresh runs
   exactly one feature-off GraphQL practitioner request, invalidates the held
   result, and never renders its stale practitioner row.
5. After the stale result is released, one visible feature-off Refresh recovers
   the exact legacy directory; final transition totals remain separate from the
   pre-transition and post-disable counters.
6. Enabled reader rejection exposes only
   `application_session_practitioner_directory_failure`, leaves the grid
   container hidden with zero grid children, and makes no legacy GraphQL or REST
   practitioner request.
7. With no bootstrap property, the page loads no application-session ES module,
   makes exactly one GraphQL practitioner request, makes no REST fallback and
   renders the legacy authored-synthetic practitioner in the visible modal.
8. The API fixture allowlist has no unknown path or wrong method, no
   non-loopback request escapes interception, no provider host is contacted and
   Chromium records no console error.
9. The committed evidence reproduces exactly, the focused Python tests pass
   serially, Ruff passes and `git diff --check` is clean.

## Browser workflow decision

The in-app Browser was available and used first. It proved page identity,
non-blank standalone smoke rendering, console health and the visible Refresh
interaction. Its exposed API has no request-routing or pre-document init-script
surface, both of which are required by this frozen route-intercepted bootstrap
test. The repository's serial Playwright harness is therefore the explicit
permitted fallback and carries the acceptance evidence.

## API Spine classification

This remains a consumer test of the accepted fixed
`Query.practice.practitioners(activeOnly: true, limit: 200, offset: 0)` read.
GraphQL remains read-only. No schema, resolver, REST surface, command tunnel,
event actuator, manifest, audit authority or idempotency path changes.

## Closed gates and residual risk

No real application-session injection, backend, database, `app.main`, provider,
model, memory/RAG, real identity, patient/clinical/document data, product-derived
read, command/write, default-on, cloud/IAM, deployment, production, release,
protected evidence/ref or `docs/branding/` authority is added. The single-engine
rehearsal does not prove cross-browser behavior, cross-tab lifecycle delivery,
real cookie transport, backend authorization/audit, XSS or supply-chain
controls, accessibility, usability or production suitability.
