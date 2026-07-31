# Reception One authenticated Word desktop dialog check plan

Date: 2026-07-31

Owner: Yuri / GPT Sol

Status: `closed - accepted`

## 1. Authority and purpose

Yuri selected Word desktop after the authenticated Word Online descendant
failed closed before taskpane code: Chromium blocked the Microsoft-owned
cross-origin Word editor frame from navigating to the strictly loopback
development host under Local Network Access subframe policy.

This replacement descendant may:

- use one new blank document in the existing Word desktop application;
- temporarily sideload the validated task-specific development manifest;
- serve the add-in and native Diary from the existing trusted HTTPS loopback
  development origin; and
- submit one short authored-synthetic receptionist request through the
  accepted typed Word-to-Diary exchange.

It may not inspect existing document contents, Office credentials, account
identifiers or unrelated windows. It grants no provider, backend, database,
appointment, command, product-data, deployment, tenant, catalogue, IAM or
release authority.

## 2. Frozen contract

The desktop exercise preserves the accepted compact-companion contract
unchanged:

1. authentication, zero-authority launch context and authored-synthetic
   companion request remain separate messages;
2. the request carries deterministic view-only mode and explicit false
   patient-context, appointment-context, provider, command and write authority;
3. the Office dialog starts at exact `https://localhost:3000`;
4. the dialog URL carries only
   `reception_one_companion_demo=true` and `smoke=true`;
5. the native Diary verifies the requested date before processing;
6. detailed authored-synthetic appointments and request text remain in the
   Diary; and
7. only the existing closed generic proofreader-admitted summary returns to
   Word, where visible copy is derived locally.

No retry, fallback, provider or product write is introduced. No backend or
database access and no appointment command or write authority are granted.

## 3. Desktop host boundary

- Use the already installed Word desktop application only.
- Use a newly created blank document and never call Word APIs that read or
  write its body.
- Do not inspect Office authentication, account, licence or tenant material.
- Use the task-specific disposable manifest, not the canonical manifest.
- Sideload only for the local development session and remove the sideload at
  cleanup.
- Use the existing trusted localhost certificate; do not install or replace a
  certificate.
- Bind the development server only to `127.0.0.1`.
- Do not bypass a security interstitial, change Trust Center, Windows security,
  browser policy, tenant catalogue or deployment settings.

## 4. Acceptance gates

### Gate A - rehydration and authority

- Restore the five mandatory Ariadne sources and protected boundaries.
- Verify HEAD, master, handoff/current and both origin refs.
- Preserve every unrelated worktree change.
- Produce a passing pre-plan receipt.

### Gate B - manifest and loopback

- The task manifest is schema-valid, disposable and distinct from the
  canonical product id.
- Every taskpane, command, icon and dialog origin is HTTPS loopback.
- The server listens on `127.0.0.1` only and does not advertise or bind a LAN
  address.

### Gate C - safe desktop host

- Word desktop opens one new blank document.
- The taskpane loads from the exact localhost capability URL.
- No existing document is opened or inspected.
- No Office account, credential, tenant, filename or document identifier is
  retained in evidence.

### Gate D - typed exchange and proofreader

- One bounded authored-synthetic request is sent.
- Message order, request/correlation/date binding and single-consumption rules
  pass.
- The Diary uses `authored_synthetic_client_fixture`.
- The deterministic proofreader admits only the exact generic summary, or the
  exercise fails closed with no detail returned.

### Gate E - zero authority and cleanup

- Provider, credential, backend, database, confirmation, command and
  appointment-write counts remain zero.
- The dialog closes and Word focus is restored.
- The disposable desktop sideload, task-owned server and owned temporary
  processes are removed.
- Independent listener, browser, container and process residue checks pass.

### Gate F - verification

- Run focused desktop/companion/Hybrid/Bureau/API Spine tests.
- Run manifest, JSON/schema, Python and JavaScript checks.
- Run the repository-only Ariadne verifier, Compass validation, rendered
  Compass validation and `git diff --check`.

## 5. Candid evidence limit

A pass proves only that one local provider-free authored-synthetic companion
exchange works in the installed Word desktop host against the strictly
loopback native Diary. It does not prove authenticated Word Online
interoperability, provider interpretation, live backend authorization,
real/product-derived/patient/health-data safety, representative usability,
production fitness, deployment or release readiness.
