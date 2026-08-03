# Raisa provider-free Office practitioner-directory consumer closeout

Date: 2026-08-03

Result: `provider_free_office_practitioner_directory_consumer_pass`

## Outcome

The supervised provider-free Office consumer passes in installed Word and Word
Online. Each real Office host received an independent authored-synthetic
application session, admitted only its manifest-bound surface, issued the fixed
active-practitioner GraphQL read after one visible user action, rendered exactly
two display-safe rows, logged out, and proved that the same session was denied
after logout.

The consumer remains a separate task-scoped FastAPI application. The accepted
GraphQL factory is not mounted in `app.main`; no product command, patient or
clinical field, document access, provider call, real identity, deployment or
production authority was added.

## Implemented boundary

- two fresh development manifests bind independent `word_desktop` and
  `word_online` surfaces to one exact reserved HTTPS development origin;
- the delivered page holds CSRF and result nonce material only in memory,
  removes it from DOM attributes immediately, and receives only Secure,
  HttpOnly, SameSite=None, Partitioned `__Host-` cookies;
- the visible action sends one compile-time `Directory` query with exactly
  `activeOnly=true`, `limit=200`, and `offset=0`;
- the renderer admits only `id`, `displayName`, `roleLabel`, `active`, and
  `defaultLocation { id name }`, creates text nodes, and rejects malformed,
  inactive, broader or error-bearing responses without partial rendering;
- successful rendering is followed by the accepted REST logout command and a
  direct backend post-logout denial; and
- application-auth and product access retain separate finite LOGIN/NOLOGIN
  capability pairs, exact-column read authority, required authorization audit,
  and four direct PostgreSQL privilege denials.

## Supervised evidence

Installed Word rendered Avery Desktop Synthetic and Morgan Desktop Synthetic,
then displayed `Directory shown · session ended`. Word Online rendered Avery
Online Synthetic and Morgan Online Synthetic and reached the same terminal
state. Durable evidence retains only surface classes, counts, booleans and
failure codes; it contains no practitioner/product UUID, account, document,
cookie, CSRF, nonce, database target or role name.

The final backend readback records two active rows per host, two committed
authorization-allowed audits, two revoked sessions, two post-logout denials,
zero raw-secret or target matches, zero provider/Microsoft identity/patient/
clinical/document/write side effects, and complete disposal of the database,
four task roles, pools, server, relay, listeners and desktop developer session.

## Diagnose-repair evidence

Three exact development-host defects were preserved rather than overwritten:

1. the first installed-Word logout was rejected because Uvicorn interpreted
   forwarded headers before the application-owned strict one-hop proxy guard;
   disabling Uvicorn proxy-header rewriting restored the accepted guard;
2. valid numeric icon paths returned 422 because a path string was compared to
   integer `Literal` values; exact string allowlisting now serves only 16, 32,
   64 and 80 pixel assets and returns 404 otherwise; and
3. Word Online reached the backend but its outer personal OneDrive ancestor was
   absent from CSP. Adding only `https://onedrive.live.com` to
   `frame-ancestors` admitted the observed nested Office host without broadening
   scripts, connections, forms or data authority.

Focused tests pass after every repair, and the final fresh two-host run—not a
reused partial run—supplies the accepted evidence.

## Verification

- focused consumer tests: 5 passed;
- focused plus inherited practitioner-directory, application-auth and API Spine
  gates: 115 passed;
- Ruff on the task harness and tests: passed;
- Bandit on the task harness and continuity runner: passed with zero findings;
- route-intercepted local browser preview: passed for both host classes, with
  desktop/tablet/narrow layout, keyboard focus and sanitized terminal-state
  evidence; it is not labelled real Office;
- supervised installed Word and Word Online: passed;
- live local Office/backend/PostgreSQL evidence and cleanup: passed; and
- final API Spine, inherited application-auth/GraphQL/security and continuity
  gates passed.

## Limits and next safe work

This proves only two supervised authored-synthetic Office renders of the
active-practitioner directory through one disposable development origin. It
does not prove real identity, patient or clinical safety, document access,
general endpoint mounting, broader product reads, product writes, distributed
abuse resistance, organisational Office deployment, production or release.

The next safe descendant is provider-free taskpane reload and terminal-state
reconciliation: make repeated Office navigation visibly inert, preserve the
one-use session boundary, and prove that no reload, retry or stale taskpane can
reissue product authority.
