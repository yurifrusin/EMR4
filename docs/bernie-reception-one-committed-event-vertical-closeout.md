# Reception One committed-event vertical closeout

**Result:** `reception_one_committed_event_vertical_pass`
**Date:** 2026-07-21
**Decision owner:** Yuri
**Conductor and acceptance owner:** GPT Sol High under the frozen Extra High plan
**Source head:** `be5e01d00b23ef43f7aab8b30f6dbdfa6e858c45`
**Accepted candidate:** `705582b7719bce6f1c5fe5833c1703354b5fa1a3`

## 1. Outcome

The bounded provider-free committed-event vertical passes. Reception One can
now notice one externally committed appointment-time change in an active
patient timeline or focused practitioner view, refresh the exact authorized
Diary context, and show one quiet reversible cue. The browser never treats the
event payload as display truth and gains no command authority.

The path is exactly:

`existing signed update confirmation -> one PostgreSQL transaction for appointment + update audit + idempotency completion + event -> authenticated practice-scoped polling -> fresh appointment and projection reads -> quiet Reception One cue`

Only `diary.appointment_rescheduled` is opened, only for an actual start or
duration change, and only while
`RECEPTION_ONE_COMMITTED_EVENT_RUNTIME_ENABLED=true`. The setting remains
false by default. No new appointment command was added.

## 2. Backend and API result

Alembic head `n3o4p5q6r7s8` adds one append-only
`diary_committed_events` table. Database constraints enforce the fixed event
type/schema/source/evidence mode, positive aggregate revision, expiry after
occurrence, command correlation, exact six-key patient-free payload,
practice-qualified appointment/command/audit links, and unique command, audit
and appointment-revision coordinates.

PostgreSQL forced RLS permits only practice-scoped SELECT and INSERT. A trigger
rejects UPDATE and DELETE. Event, appointment, audit and idempotency completion
are flushed and committed by the same update-confirm transaction. Injected
event failure rolls the complete chain back; idempotent replay returns the
stored result without a second event.

The additive read-only endpoint is:

`GET /api/v1/diary/events/committed?cursor=<signed_opaque_cursor>&limit=<1..20>`

It is authenticated, practice scoped, default-off and batch bounded. A first
cursorless request establishes a signed practice-bound current-time baseline
without historical delivery, including when the event table is empty. Invalid,
foreign or expired cursors fail closed by re-baselining. The browser response
omits actor, practice, command and audit coordinates.

GraphQL remains read-only. No event acknowledgement, new mutation,
subscription, publisher, broker, background worker, WebSocket or autonomous
consumer exists.

## 3. Reception One client and plain-language behavior

The existing Diary bridge receives two reads only: current appointment by id
and committed-event feed. Polling runs only while Reception One is open and the
document is visible. Cursor, delivered identities, revisions, snooze and mute
remain bounded in memory; no event attention state is placed in browser
storage.

A signal must name an appointment already present in the active projection.
The client then obtains a fresh exact appointment and rebuilds the exact
patient-timeline or focused-practitioner projection. Only a confirmed old-time
versus current-time difference creates a cue. Unrelated, replayed, equal/older,
superseded, unauthorized, failed-read and non-material cases remain quiet.

The user-facing copy is intentionally plain:

- `Reception One change`;
- `An appointment time in this view changed`;
- the previous and current time after fresh reconciliation; and
- `Show changed appointment`, `Dismiss`, `Snooze 5 min`, and
  `Mute until reload`.

The cue is nonmodal, does not autofocus or speak, and coalesces rather than
stacking. Escape dismisses it and restores focus to the plain-language request.
Privacy mode masks both the time comparison and changed-item detail, disables
show-context, and leaves a patient-free polite live-region announcement.

## 4. Real browser and PostgreSQL evidence

The repeatable Playwright runner used real Chromium through the ordinary
authenticated Diary, real loopback FastAPI and the exact disposable PostgreSQL
database. It used no `page.route(...)`, API interception, mocked transport or
page-internal attention shortcut. Browser-driven traffic was read-only apart
from authentication; a separately labelled authenticated HTTP support client
used only the existing update proposal and signed update-confirm routes.

All five required viewports pass:

- desktop 1440x900;
- tablet landscape 1024x768;
- tablet portrait 768x1024;
- smartphone portrait 390x844; and
- smartphone landscape 844x390.

Every viewport has zero page/host horizontal overflow, no error overlay and no
enabled control below 44 CSS pixels. Console, page-error, failed-response and
forbidden-request collections are empty. Evidence covers fresh reconciliation,
unrelated suppression, no duplicate visible effect, show-context, dismiss,
five-minute snooze, mute-until-reload, privacy, interruption/resume, native Tab,
Escape focus restoration and ordinary Diary fallback.

Database readback records six synthetic appointments, two update audits, two
completed command rows and two committed events. Exactly two synthetic
reschedules occurred, one relevant and one unrelated, plus one idempotent
replay and no other mutation. All two event/audit/command correlations match;
payload keys are exact and contain no prohibited patient/free-text fields.
The non-bypass probe role read two own-practice and zero foreign-practice
events, and direct UPDATE and DELETE were rejected.

Cleanup verified the exact synthetic ownership marker, dropped only
`gp_pms_reception_one_event_runtime_5e2c91a7_20260721`, removed the exact probe
role, and then verified both were absent. The cleanup is irreversible but
affected only the authorized disposable database and role.

Canonical evidence is under
`orchestration/prototypes/reception-one-committed-event-vertical/`.

## 5. Verification and review

Final current populations passed serially:

- 20/20 committed-event runtime, client and evidence tests;
- 213/213 current committed-event, functional/live-local/combined-scope,
  update-confirm, API Spine, Stage 3A, accessibility, handover and continuity
  tests; and
- 139/139 complete Diary smoke tests on the final clean rerun.

The first complete Diary run had the previously documented three-second
visible-date reanchor timeout. The exact node passed immediately and the full
unchanged rerun passed 139/139. No failure was overridden.

A deliberately broader historical sweep found obsolete pre-idempotency and
pre-raw-compat test assumptions. A detached clean run at the untouched baton
commit reproduced the same preflight/import observations and the same 14
legacy audit/delete/slot failures exactly. They are recorded in
`reception-one-committed-event-vertical-baseline-regression-comparison.md`; no
historical test was rewritten or called passing.

Node syntax, Python compilation, Ruff, frontend asset-version integrity,
Alembic single-head, new-code blocked-primitive and Git whitespace checks pass.

Fresh Gemini 3.5 Flash (High), through a new Antigravity project bound to clean
candidate `705582b7719bce6f1c5fe5833c1703354b5fa1a3`, returned `pass` with no
material finding. It independently reran all 20 focused tests plus Node and
Ruff. Its immutable receipt and extracted decision are under
`orchestration/agent_inbox/antigravity/`.

## 6. API steward and authority disposition

The API-steward classification is
`bounded_async_event_runtime_plus_read_only_delivery`. The one database/event
addition and one authenticated read endpoint are exactly the exception Yuri
authorized. The existing REST update-confirm command remains the only producer
entry, identity/conflict/freshness/write/audit authority remains backend-owned,
and the browser remains a read/reconciliation consumer.

No provider, external prompt, PII, protected holdout, historical Diary material,
Stage 3B participant, voice, push-to-talk, ambient listening, new appointment
action, GraphQL mutation/subscription, external transport, background worker,
persistent preference, general retention scheduler, production configuration,
deployment or release surface was opened. Dependabot alert 5 was untouched.

## 7. Worker mix, unresolved gates and next tranche

Sol retained implementation and the serial browser/database run under the
worker-economy rule. No native subagent or implementation worker contributed.
Gemini supplied the required fresh independent veto only and received no edit,
acceptance, integration, baton or protected-ref authority.

The exact result is `reception_one_committed_event_vertical_pass`. Remaining
gates are intentionally explicit:

- event families beyond appointment reschedule remain closed;
- availability/selection/proposal invalidation from a newly occupied or freed
  slot is not claimed by this appointment-present projection proof;
- high-fidelity visual/interaction design and representative staff validation
  remain later Yuri decisions; and
- production delivery, retention, encryption/roles, deployment and release
  remain closed.

The recommended next product tranche, if Yuri wishes to continue the nervous
system before visual synthesis, is a separately authorized bounded
committed-reschedule reconciliation proof for the combined
availability/selection/proposal flow: refresh current availability after a
relevant commit, clear any invalid selected proposal state, and remain
read/proposal-only. Otherwise the baton should return to Yuri for the planned
Reception One design synthesis. Neither path is authorized by this closeout.

Reasoning level: Extra High froze the first event-runtime architecture and
privacy semantics; High completed the fixed implementation, deterministic/live
evidence, independent-veto reconciliation and mechanical closeout.
