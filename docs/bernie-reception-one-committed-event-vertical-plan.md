# Reception One committed-event vertical plan

**Status:** frozen for bounded implementation
**Decision owner:** Yuri
**Conductor, architecture and acceptance owner:** GPT Sol Extra High
**Date:** 2026-07-21
**Source head:** `be5e01d00b23ef43f7aab8b30f6dbdfa6e858c45`
**Task branch:** `codex/reception-one-committed-event-vertical`

## 1. Decision and purpose

Yuri explicitly authorises one bounded provider-free committed-event runtime
vertical after accepting the Reception One combined patient, practitioner,
date, time and duration proof.

The tranche closes one precisely identified gap between the accepted fixture
concept and real local behaviour:

`signed appointment-reschedule confirmation -> one PostgreSQL transaction containing appointment, audit, idempotency and typed event -> authenticated practice-scoped event read -> deterministic relevance/deduplication -> fresh authorised appointment and Diary reads -> quiet Reception One change cue`

The target result is `reception_one_committed_event_vertical_pass`. It proves
only one authored-synthetic, loopback, development event type:
`diary.appointment_rescheduled`.

## 2. Exact visible vertical

1. A synthetic receptionist opens Reception One through the ordinary
   authenticated Diary and asks to see Margaret Thompson's upcoming
   appointments.
2. The active patient-timeline projection contains one existing appointment
   with Dr Alex Shera and retains its exact appointment id in the typed client
   projection.
3. A second authenticated synthetic staff context uses the already accepted
   update-proposal and signed update-confirmation command to move that
   appointment to a different time. The event system introduces no new
   appointment mutation command.
4. The appointment row, append-only appointment audit, completed idempotency
   record and one minimal `diary.appointment_rescheduled` row become visible
   only after the same PostgreSQL transaction commits.
5. Reception One receives the minimal event through the new authenticated
   read-only feed. It first checks practice, current projection membership,
   event identity, aggregate revision, mute/snooze state and novelty.
6. The client treats the event only as a signal. It obtains the current
   appointment by id and refreshes the exact patient timeline through existing
   authorised reads before displaying anything derived from Diary truth.
7. A non-modal, polite cue states that an appointment time in this view changed,
   shows the fresh old-versus-current time comparison, explains why it appeared
   and leaves the refreshed projection visible.
8. The user may show the changed appointment, dismiss the cue, snooze this
   event family for five minutes, or mute it until page reload. No control
   writes to the Diary or browser storage.

The cue never receives focus automatically, never speaks, never confirms, and
never makes a model/provider call.

## 3. Backend transaction and event-store contract

### 3.1 Existing command authority

The producer is limited to the existing command pair:

- `POST /api/v1/appointments/proposals/update/{appointment_id}`; and
- `POST /api/v1/appointments/proposals/update/confirm` with explicit staff
  confirmation, signed freshness evidence and `Idempotency-Key`.

The existing command continues to own role checks, practice scope, identity,
conflicts, freshness, confirmation, idempotency, appointment mutation and
audit. The event writer may run only after those checks pass and inside the
same transaction as the confirmed update.

The update audit is correlated to the exact command id, and the completed
idempotency record is correlated to that audit. An idempotent replay returns
the stored command response and creates no second appointment update, audit or
event.

### 3.2 Transactional committed-event table

One Alembic migration and one SQLAlchemy model add an append-only,
practice-scoped table for committed Diary signals. Each row contains:

- stable event id and `diary.appointment_rescheduled` type;
- schema version;
- practice, source system and appointment aggregate id;
- aggregate revision derived from the appointment's append-only audit count;
- occurred/created/expiry timestamps;
- actor user/role references retained for backend correlation;
- command, audit and correlation coordinates;
- evidence mode; and
- one validated JSON payload limited to appointment, practitioner, location,
  start/end timestamps and reason codes.

The payload must not contain patient id or name, date of birth, phone number,
Medicare number, appointment reason/notes, raw instruction, transcript,
provider output, credential, bearer token or free text.

The table has practice-qualified foreign keys, uniqueness over stable event id
and appointment aggregate revision, forced PostgreSQL RLS, and database-level
rejection of `UPDATE` and `DELETE`. The row is inserted before the command's
single final commit. Rollback removes appointment, audit, idempotency and event
together. Reading the same committed table is the bounded outbox-equivalent;
there is no independent publisher or commit/publication gap.

Rows expire from delivery eligibility after 24 hours. No retention scheduler or
deletion runtime is authorised; the disposable acceptance database is dropped
after evidence, and the feature remains disabled by default outside the exact
local harness.

## 4. Read-only delivery contract

The additive authenticated route is:

`GET /api/v1/diary/events/committed?cursor=<signed_opaque_cursor>&limit=<1..20>`

Rules:

- ordinary authenticated internal staff only;
- current user's practice is applied in application filtering and PostgreSQL
  RLS;
- default-disabled capability returns `enabled: false` and no events;
- the first request without a cursor returns a signed, practice-bound current
  time coordinate, establishes a baseline even when no prior event exists and
  returns no historical notices;
- subsequent requests return only later, unexpired events for that practice;
- a forged, malformed, expired or foreign-practice cursor fails closed by
  establishing a new baseline without returning broadened history;
- response order is deterministic by occurrence time and event id;
- maximum batch size is 20;
- the response envelope is typed and excludes stored actor identifiers,
  command/audit ids and every prohibited payload field; and
- the route has no acknowledgement, mutation, deletion or command authority.

The default-off setting is
`RECEPTION_ONE_COMMITTED_EVENT_RUNTIME_ENABLED=false`. The exact disposable
local harness enables it. No deployment or production configuration changes.

## 5. Reception One consumer and attention rules

The existing Diary bridge receives only two new exact read operations:

- read the committed-event feed; and
- obtain a current appointment by id before reconciliation.

The client uses bounded recursive polling only while Reception One is open,
visible and the backend capability is enabled. It uses no WebSocket,
`EventSource`, service worker, local/session storage, cookies, telemetry or
external transport.

The in-memory attention state contains a bounded delivered-event set, latest
revision per appointment, one opaque cursor, an optional five-minute snooze and
an until-reload mute flag. New roots clear any visible cue but do not rewind the
cursor or delivered-event set.

A candidate event is relevant only when its appointment aggregate was already
present in the active projection. The client then performs the fresh appointment
read and refreshes the exact current projection. It computes old-versus-current
time from those authorised reads, not from the event payload. If the fresh read
fails, becomes unauthorised, no longer belongs to the current practice/scope, or
does not confirm a material time change, the event produces no patient-bearing
notice.

Replay, equal/older revision, unrelated appointment, foreign practice,
superseded state and muted/snoozed family produce no duplicate visible effect.
At most one cue is visible; later relevant changes coalesce rather than stack.

Privacy mode masks the time comparison and changed-item detail and leaves only
a generic change/reconciliation statement. The live region is polite and
patient-name-free. Show-context, dismiss, snooze and mute controls are semantic,
keyboard reachable, at least 44 by 44 CSS pixels and do not change Diary truth.

## 6. API Spine and security disposition

### Boundary classification

This tranche is an additive `async_event_runtime_plus_read_only_delivery`
change backed by the existing REST update command. GraphQL remains read-only
and gains no mutation or subscription. No new appointment command or write
authority is introduced.

The current API Spine async contract and *bernie* capability charter receive a
narrow exception labelled local/authored-synthetic/reschedule-only while their
broader proactive-event, provider, production and external-client gates remain
blocked. The OpenAPI prototype records the read-only event-feed response.

### Required threat-model delta

The tranche must record and mechanically test mitigations for:

- publish-before-commit and commit-without-event split brain;
- duplicate, replayed, reordered, expired and superseded delivery;
- forged/schema-downgraded event rows;
- cross-practice event or cursor leakage;
- event payload becoming a secondary PHI store;
- client trusting payload instead of a fresh authorised read;
- event consumer becoming a command tunnel;
- alert flooding, covert attention capture and shared-screen disclosure; and
- correlation loss between command, appointment, audit, idempotency and event.

The database is authoritative, event rows are append-only and practice-scoped,
the client rereads current state, attention is bounded and controllable, and no
event path accepts a mutation payload.

## 7. Deterministic, browser and database acceptance

### 7.1 Focused backend and contract tests

Exact ordinary-development tests must prove:

- disabled capability produces no event rows or delivery;
- signed confirmed reschedule creates exactly one correlated event in the same
  commit as one update audit and completed idempotency record;
- idempotent replay creates no second visible or database effect;
- proposal-only and non-time updates create no reschedule event;
- injected rollback exposes neither the appointment change nor event;
- direct event `UPDATE` and `DELETE` are rejected;
- practice filtering and forced RLS prevent foreign-practice reads;
- payload allowlisting and typed schema reject PHI/free text/unknown fields;
- baseline, cursor, expiry, order and maximum-batch semantics fail closed;
- GraphQL still contains no mutation or subscription authority; and
- all existing update-confirm, API Spine, Stage 1/2, functional meta-grid,
  live-local, combined-scope and Diary regression populations remain passing.

### 7.2 Real local browser evidence

The task-scoped Playwright runner drives real Chromium through the ordinary
authenticated Diary UI and real local FastAPI/PostgreSQL without
`page.route(...)`, mocked transport, page-internal attention calls or fabricated
readback. A separate authenticated HTTP support client may execute only the
existing signed update proposal/confirm command that supplies the external
change; it is labelled `live_local_backend_postgres` inside the overall
`live_local_browser_backend_postgres` evidence.

Required viewports:

- desktop landscape 1440x900;
- tablet landscape 1024x768;
- tablet portrait 768x1024;
- smartphone portrait 390x844; and
- smartphone landscape 844x390.

Required visible evidence:

- current patient timeline before the command;
- one quiet in-scope time-change cue after commit and fresh reread;
- refreshed current time and visible old-versus-current comparison;
- no cue for an unrelated appointment event;
- no duplicate cue after polling/reload-like interruption of the same client
  session;
- explain-why/show-context, dismiss, five-minute snooze and until-reload mute;
- privacy masking, interruption/resume and fresh reconciliation;
- keyboard Tab/Enter/Space/Escape behaviour and focus restoration;
- Back and ordinary Diary fallback;
- correct page identity, nonblank content, no overlay, no console warnings or
  errors, zero horizontal overflow, complete painted width and no enabled
  control below 44 pixels.

Network evidence permits only loopback bootstrap/read/proposal/update-confirm
and committed-event routes. No session-event, create, cancel, delete, status,
provider, external, telemetry or other mutation route may occur.

### 7.3 Database readback and cleanup

The exact database is
`gp_pms_reception_one_event_runtime_5e2c91a7_20260721`. It must not pre-exist,
must be PostgreSQL on loopback, and contains only newly authored synthetic
people and appointments. The provider is disabled, fallback is false, cloud
credentials are blank and secrets/tokens are never recorded.

Readback must prove the exact authorised deltas and correlations rather than a
zero-write claim: two confirmed synthetic reschedules at most (one relevant,
one unrelated), with matching appointment state, update audits, completed
idempotency records and one event per command. No create/delete/status,
Bernie-session event or provider row may appear.

Cleanup verifies exact database and synthetic ownership markers, then drops only
that disposable database. Screenshots may contain authored-synthetic names;
machine evidence contains no patient name/id, date of birth, token, password,
credential or raw header.

## 8. Browser-driver and worker disposition

The Browser plugin is available and will be used for exploratory rendered
diagnosis after its skill is loaded. Yuri previously authorised Playwright to
economise repeatable browser control where efficacy is not diminished, and the
live handover declares a task-scoped real-browser script equivalent. Playwright
therefore owns the repeatable multi-viewport acceptance and sanitized evidence.

Sol retains implementation and the serial database/browser run. The migration,
transaction, feed, active projection and disposable database form one tightly
coupled stateful vertical; a worker packet would not save a meaningful cycle.
No native subagent or implementation worker is assigned.

A fresh Gemini 3.5 Flash/high Antigravity context is required as an independent
veto after the candidate, threat-model delta and evidence are complete. Gemini
cannot accept its own review, integrate, move the baton or push protected refs.

## 9. Acceptance and closeout gates

Final `reception_one_committed_event_vertical_pass` requires:

1. the frozen plan and threat-model delta are satisfied;
2. focused, inherited and API Spine tests pass serially;
3. real-browser responsive/keyboard/privacy/attention evidence passes;
4. transaction, rollback, correlation, RLS, append-only and exact database
   readback pass;
5. the disposable database is marker-verified and removed;
6. the fresh Gemini veto has no unresolved material finding;
7. Sol records accurately bounded acceptance and Continuity Engine evidence;
8. a check-gated PR integrates; and
9. local and origin `master` and `handoff/current` align cleanly.

## 10. Boundaries and stop conditions

This authorization does not open:

- any event type except local `diary.appointment_rescheduled`;
- appointment create, cancel, delete, status or waiting-area event production;
- a new appointment mutation or bypass of signed update confirmation;
- event acknowledgement, event-driven command execution or autonomous action;
- GraphQL mutation/subscription, external broker, background worker,
  WebSocket, desktop notification or service worker;
- persistent user attention preferences, general retention cleanup or
  production encryption/roles;
- provider calls, external prompts, model-generated relevance or explanation;
- PII, real patient/practice data, protected holdouts or historical Diary
  material;
- Stage 3B, representative participants, voice, push-to-talk or ambient
  listening;
- high-fidelity styling, public rename/trademark action, external design model
  or subscription; or
- production, deployment or release.

Any need to broaden the event family, delivery transport, retention policy,
participant population, data class, command authority or production posture
returns to Yuri. Mechanical corrections inside this frozen contract may be
completed and rerun under Sol ownership.
