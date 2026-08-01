# Threat-model delta: shared application-auth Office cookie compatibility

Date: 2026-08-01

Status: active acceptance boundary

Parent: `security_finding_governance_pass`

## Added surface

One task-owned HTTPS development origin may serve a provider-free,
authored-synthetic in-memory application-auth harness to task-specific
installed Word and Word Online taskpanes. The existing seven-route auth router
is injected explicitly; the product application and all product routers remain
unchanged and default-off.

The protected assets are the one-use synthetic bootstrap values, transient
session/CSRF cookies, exact host/surface binding and truthful sanitized
evidence. There is no real identity, product-derived, patient, health,
clinical, document-body or historical data in scope.

## Trust boundaries

1. **Office host to taskpane:** the Office-reported host/platform must match
   the manifest-bound `word_desktop` or `word_online` surface before login.
2. **Taskpane to exact origin:** all lifecycle requests are same-origin HTTPS,
   credentialed fetches to the existing auth prefix with exact Origin and CSRF
   enforcement.
3. **Development tunnel to local harness:** the reserved ngrok domain relays
   only to the task-owned local listener. It grants no proxy-derived auth and
   is stopped after the exercise.
4. **Harness page to one-use registry:** a raw bootstrap value exists only in
   process memory and its single no-store page response until the login
   attempt; only a hash and consumed state remain afterward.
5. **Runtime to evidence:** only closed status fields cross into durable JSON.
   Raw headers, origins beyond the frozen exact public origin, secrets,
   cookies, request bodies and Office identifiers are excluded.

## Threats and controls

| Threat | Required control and proof |
|---|---|
| A public caller steals or consumes a synthetic bootstrap | One bounded principal per surface, one-use hash registry, no real/product authority, no-store response, short supervised exposure, bounded rate admission and replay denial. A consumed-before-supervision value fails that surface closed and is not silently regenerated. |
| A credential leaks through URL, logs or evidence | No raw credential in manifest/query/path, no request-body logging, DOM/runtime deletion after the login attempt and recursive forbidden-value scans of evidence and responses. |
| Cookie blocking is hidden by a fallback | HttpOnly cookies are proven only by router validation. Authorization headers, query tokens, local/session storage, IndexedDB and second-origin exchange workarounds are prohibited and statically scanned. |
| Wrong Office host obtains a surface session | Taskpane verifies Office host class against the manifest-bound surface; backend Origin and declared surface remain exact; mismatch stops before bootstrap submission. |
| Cross-surface cookie collision creates a false pass | Each host has an independent principal/bootstrap and must complete login, validate, rotate, revalidate, logout and post-logout denial under its exact surface label. |
| CSRF or hostile embedding drives the auth routes | Existing exact Origin, double-submit CSRF, SameSite=None, Secure, HttpOnly and Partitioned behavior is unchanged. The operational guard runs before credential processing. |
| The ngrok relay broadens deployment authority | Use only the already configured reserved development domain, one task-owned local listener and no cloud/IAM/DNS/catalogue mutation. Record listener/tunnel cleanup; make no production claim. |
| Taskpane reads Office or document identity | Minimum manifest permission, no `Word.run`, document APIs, Office tokens, account/tenant/document URL/id capture, or browser storage inspection. Use blank authored-synthetic documents. |
| Evidence exposes network or authentication material | Closed schema permits surface, host class, bounded status/boolean fields, generic failure category and cleanup counts only. No free text, URL, account, document, header, cookie, token, secret or raw exception field. |
| A partial result is promoted | Each host has a separate terminal disposition. Cross-host pass requires both real-host results and complete cleanup. Deterministic or ordinary-browser testing alone is not a real Office-host pass. |
| The harness becomes product authentication | It uses only process-local authored-synthetic state, includes no product router/database/external identity adapter, and stays on a task branch behind explicit dependency injection. |

## Abuse and negative cases

Acceptance must cover bootstrap replay, wrong Origin, wrong surface, duplicate
execution, host mismatch, missing cookies, CSRF mismatch, rotation invalidating
the prior surface value, logout invalidation, post-logout validation denial,
evidence-schema extra fields, raw-value scans and task-owned process cleanup.

## Residual risks and closed decisions

- One supervised installed-Word and one Word Online result cannot cover every
  WebView, browser, Office update, privacy mode, tenant or enterprise cookie
  policy.
- The public development origin offers no real identity establishment; its
  synthetic bootstrap is intentionally zero-product-authority.
- The in-memory runtime does not prove PostgreSQL, multi-instance, restart,
  production credential, retention, monitoring or incident-response behavior.
- Real/live identity mapping, Microsoft/Office federation, product-derived
  reads, patient/health/clinical data, document mutation, appointment/arrival
  commands, provider calls, organisational deployment, production and release
  remain closed.
