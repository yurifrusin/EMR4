# Reception One Word compact companion shell closeout

Status: **accepted provider-free local development result**
Closed: 2026-07-31
Result: `reception_one_word_compact_companion_shell_pass`

## Outcome

The first compact Reception One companion inside Word passes its bounded
provider-free contract.

- Word offers one short authored-synthetic request field and one warm
  `Prepare in Diary` action.
- The existing Office dialog opens the authoritative native Diary/Bureau.
- Authentication, zero-authority launch context and companion request remain
  three separate typed messages.
- The native Diary verifies the requested date before processing the request.
- Detailed appointments and the submitted request remain in the native Diary.
- The native deterministic proofreader admits only a closed generic summary.
- Word validates that summary again and derives the visible sentence locally.
- The ordinary Diary and contextual Reception One launch paths remain
  available.

No provider, backend, database, appointment command or write path was added.

## Typed exchange

`reception.one.word-companion-request.v1` is an exact closed request with:

- one authored-synthetic string of at most 280 characters;
- fresh request and correlation identifiers;
- exact reference-date binding;
- deterministic view-only mode; and
- explicit false patient-context, appointment-context, provider, command and
  write authority.

`reception.one.word-companion-summary.v1` is an exact closed return envelope
containing only request/date bindings, projection family, result count,
allowlisted status/disposition codes, deterministic planner/proofreader
labels, the native detail-surface identifier and explicit false authority and
detail-release flags. It has no free-text, patient, appointment, request,
provider-draft or command field.

## Evidence

The repeatable route-intercepted Chromium exercise passed:

- message order: `auth`, zero-authority launch context, companion request;
- the dialog URL contains only the non-sensitive local capability flag;
- initial Diary date `2026-07-27`;
- admitted request date `2026-07-31`;
- `diary_read_complete` before request admission and projection release;
- three detailed authored-synthetic appointments visible only in the native
  Diary;
- exact generic Word summary: `3 results are ready in the Diary.`;
- deterministic proofreader disposition `admit`;
- no request text or person name in the returned summary;
- zero provider calls, credential reads, backend calls, database reads or
  writes, confirmations, commands or appointment writes; and
- no browser console error or unexpected external host.

Durable evidence:

- `orchestration/continuity/reception-one-word-compact-companion-shell/browser-acceptance-evidence.json`
- `orchestration/continuity/reception-one-word-compact-companion-shell/word-companion-empty.png`
- `orchestration/continuity/reception-one-word-compact-companion-shell/native-diary-detail.png`
- `orchestration/continuity/reception-one-word-compact-companion-shell/word-companion-admitted.png`
- `orchestration/continuity/reception-one-word-compact-companion-shell/final-residue-evidence.json`
- `orchestration/continuity/reception-one-word-compact-companion-shell/word-companion-request.schema.json`
- `orchestration/continuity/reception-one-word-compact-companion-shell/word-companion-summary.schema.json`

The focused companion tests and the inherited Hybrid, Bureau, projection,
availability, functional/live-local meta-grid and API Spine test population
pass. Source and published taskpane HTML, CSS and JavaScript are byte-identical.

## Security and authority disposition

The shell is default-off. Both Word and Diary require loopback plus the exact
`reception_one_companion_demo=true` capability. The request, identifiers,
names, token and launch context are absent from the dialog URL. Duplicate
request identifiers, correlation/date mismatches, unknown fields, stale or
authoritative projections and malformed return summaries fail closed.

No live provider call, ADC or API-key access, protected fixture, historical
Diary material, real/product-derived/patient/health/clinical data, database
access, command, confirmation, voice, production, deployment or release
occurred.

## Candid limit

This proves a local provider-free shell and typed cross-window exchange using a
stubbed Office host, authored-synthetic route-intercepted fixtures and the
existing deterministic native Diary projection. It does not prove
authenticated Word Online interoperability, tenant popup behavior, live
backend authorization, provider interpretation, representative receptionist
usability, real-data safety, production readiness or release readiness.

## Next bounded decision

The next useful product exercise is a supervised authenticated Word Online
dialog check with authored-synthetic data and no provider or write path. A
model-connected companion, live backend context, product-derived data, voice
or appointment authority each require a fresh explicit boundary.
