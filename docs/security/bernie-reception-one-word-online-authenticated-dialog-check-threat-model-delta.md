# Threat model delta: authenticated Word Online dialog check

Date: 2026-07-31

Status: `active`

Parent boundaries:

- Reception One Word compact companion shell;
- Word Hybrid contextual launch;
- Reception One Bureau post-admission hardening; and
- EMR4 API Spine read/context and command separation.

## Assets

- the user's existing authenticated Word Online browser session;
- a new blank test document;
- repository-local add-in and Diary assets;
- one authored-synthetic request;
- exact launch/request/summary messages; and
- bounded platform-behavior evidence.

## New trust edges

1. Word Online hosts the HTTPS loopback taskpane through temporary development
   sideloading.
2. The live Office Dialog API hosts the same-origin loopback Diary and carries
   the already accepted typed parent/child messages.

These edges grant no document-content, Office-token, backend, provider or
command authority.

## Threats and controls

### Existing Word content is treated as synthetic

Threat: an already open patient or personal document is inspected or used as
request context.

Controls:

- create a new blank document for the check;
- never call Word APIs that read or write document content;
- keep patient and appointment context authority false; and
- record no document URL, id, title, tenant or account identifier.

### Office credentials or unrelated browser state are exposed

Threat: browser automation inspects credentials, cookies, storage, account
details or unrelated tabs.

Controls:

- reuse only the visible authenticated session;
- do not inspect cookies, local/session storage, passwords or network auth
  headers;
- do not claim or navigate unrelated tabs; and
- redact Office document/account identifiers from evidence.

### Companion escapes the synthetic Diary

Threat: the real Office dialog opens the local Diary without smoke isolation
and therefore reaches backend or product data.

Controls:

- require both `reception_one_companion_demo=true` and `smoke=true`;
- use the same HTTPS loopback origin as the taskpane;
- reject unexpected backend/provider hosts during the exercise;
- require `authored_synthetic_client_fixture` evidence; and
- retain false backend/write/provider authority in the typed exchange.

### Sideload becomes a tenant or deployment change

Threat: the check modifies the tenant catalogue, central deployment or
production add-in.

Controls:

- use a task-specific repository-local manifest;
- use a fresh disposable development product id so Word cannot substitute a
  cached installed EMR add-in with a different source location;
- leave the canonical manifest unchanged;
- use development sideload only;
- do not change tenant settings, catalogue entries or deployment state; and
- stop for user intervention if tenant policy prevents temporary sideload.

### Dialog-origin or popup confusion

Threat: Office redirects the first dialog page to a different origin, opens an
untrusted popup or loses the user-gesture chain.

Controls:

- taskpane and first dialog page use exact
  `https://localhost:3000`;
- request and identifiers are absent from the URL;
- `displayDialogAsync` remains synchronous within the click gesture;
- bounded known Office error handling remains fail closed; and
- unexpected host or popup behavior aborts the exercise.

### Live host evidence overclaims product readiness

Threat: one successful Word Online session is described as proof of production
or real-data safety.

Controls:

- evidence labels the Office host as authenticated and the Diary as local
  authored-synthetic;
- record only platform events, exact typed field manifests and generic summary;
- exclude raw request, appointment detail and Office identifiers; and
- closeout states the evidence limits explicitly.

## Protected evidence boundary

Protected holdouts, historical Diary material, real/product-derived
patient/health/clinical data, Office credentials, application tokens, provider
material, hidden reasoning and unrelated browser state remain excluded.

## Residual risk

The check depends on one current browser/tenant configuration and a local
development certificate. It cannot establish behavior for other tenants,
browsers, policies or deployment channels. The existing taskpane contains
broader clinical capabilities, but this exercise touches only its default-off
companion and must not activate patient, document-body, backend or command
flows.
