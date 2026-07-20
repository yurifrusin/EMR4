# Reception One availability/selection/proposal reconciliation plan

**Status:** frozen for bounded implementation  
**Decision owner:** Yuri  
**Conductor and acceptance owner:** GPT Sol  
**Date:** 2026-07-21  
**Source head:** `e469fd60d37ab536152eda8e2cc4997431817110`  
**Task branch:** `codex/reception-one-availability-reconciliation`

## 1. Decision and purpose

Yuri authorises one bounded descendant of the accepted Reception One combined-
scope and committed-reschedule verticals. It must prove that the existing
patient, practitioner, date, time and duration availability interaction remains
truthful when another staff member commits a reschedule that changes the
candidate slots while the first receptionist is selecting or reviewing a
proposal.

The exact product path is:

`combined availability request -> staff selection or non-committing proposal -> existing committed reschedule signal -> deterministic active-practitioner filter -> fresh appointment and exact availability reads -> candidate-set comparison -> preserve valid state or clear invalid state -> plain-language Reception One cue`

The target result is
`reception_one_availability_reconciliation_pass`. The tranche reuses only the
already accepted `diary.appointment_rescheduled` producer and feed. It adds no
event family, command, API route, database model, migration, provider, broker or
background worker.

## 2. Exact visible interaction

1. A synthetic receptionist asks through the ordinary visible Reception One
   request field:

   > Show me all the available slots with Dr Shera for a half-hour appointment
   > with Margaret Thompson after 2 today.

2. The existing client freshly resolves the exact patient and practitioner and
   obtains current candidate slots through the existing non-mutating slot-search
   proposal route.
3. Staff selects one candidate and may prepare the existing supervised-booking
   proposal. Selection reserves nothing; proposal review commits nothing.
4. A second authenticated synthetic staff context uses only the existing signed
   update proposal and explicit update-confirm command to move another existing
   appointment. Its appointment, audit, idempotency completion and patient-free
   `diary.appointment_rescheduled` event commit atomically through the already
   accepted runtime.
5. Reception One polls the existing authenticated feed, obtains the current
   appointment, and treats a practitioner match only as permission to perform a
   fresh exact availability read. The event time is never treated as candidate-
   slot truth.
6. The client compares canonical slot coordinates from the previous and fresh
   candidate sets and applies the rules below.

### 2.1 Consequence rules

- **No candidate-set consequence:** update only internal freshness; show no cue
  and do not disturb selection or proposal state.
- **Candidate set changed, selected/proposed time remains available:** refresh
  the visible availability basis, retain the exact selected/proposed time, and
  say plainly that availability changed but that time remains available.
- **Selected time is no longer available:** clear the selection, show the fresh
  remaining candidates, and say: `That time is no longer available. Reception
  One refreshed the remaining options.`
- **Proposed time is no longer available:** discard the non-committing proposal
  and selected candidate, return to fresh availability, and use the same plain-
  language explanation. The stale proposal cannot be handed off.
- **No selection yet and candidate set changed:** silently reconcile the view,
  then show one passive cue that current availability changed.

The cue may offer `Review current availability`, dismiss, snooze for five
minutes, or mute until reload. It remains nonmodal, polite, does not autofocus
or speak, and never performs a command.

## 3. Deterministic relevance and state contract

The accepted event envelope does not contain the previous time. A move out of
the active window can therefore free availability without its new time
overlapping that window. The bounded deterministic prefilter is consequently:

- Reception One is open and visible;
- the current family is `availability_slots` or `proposal_review`;
- exactly one practitioner is in the current typed scope;
- the event passes the existing schema, identity, replay and revision checks;
- a fresh authorised appointment read confirms the event aggregate and current
  practitioner; and
- that practitioner equals the active scoped practitioner.

The prefilter grants only a fresh availability read. A visible effect requires
a confirmed difference between previous and fresh candidate sets or an invalid
selected/proposed slot. Reschedules for another practitioner remain suppressed.
Same-practitioner events with no candidate consequence remain silent.

Candidate identity is compared from date, local start, duration, practitioner
and location coordinates. A candidate freshness token alone is not used as
slot identity. When a selected slot survives reconciliation, its stored raw
candidate is replaced by the fresh backend candidate before later proposal
preparation.

Every async reconciliation captures the initiating projection identity. If the
user changes root, refines, goes back, closes Reception One or is interrupted
before the fresh reads complete, that result must not overwrite the newer
state.

## 4. Existing API and authority boundary

Permitted browser operations remain:

- `GET /api/v1/appointments/{appointment_id}`;
- `GET /api/v1/diary/events/committed`;
- `GET /api/v1/patients/search`;
- the existing practitioner and Diary reads;
- `POST /api/v1/appointments/proposals/slot-search` as a command-shaped,
  non-mutating read; and
- `POST /api/v1/appointments/proposals/bernie/supervised-booking` as a
  non-committing proposal.

The external synthetic change may use only:

- `POST /api/v1/appointments/proposals/update/{appointment_id}`; and
- `POST /api/v1/appointments/proposals/update/confirm` with explicit staff
  confirmation and an `Idempotency-Key`.

The Reception One client does not call either update route. It receives no new
bridge operation. The event cannot automatically prepare, confirm, recreate or
repair a proposal and cannot call the existing booking-review handoff.

No OpenAPI, Pydantic, router, SQLAlchemy or Alembic change is authorised. The
API Spine async example and *bernie* capability charter may receive only the
declarative refinement from appointment-present membership to exact active-
practitioner availability reconciliation. GraphQL remains read-only and gains
no subscription.

`RECEPTION_ONE_COMMITTED_EVENT_RUNTIME_ENABLED` remains false by default and is
enabled only inside the exact disposable local harness.

## 5. Privacy, accessibility and interruption

- Patient, selected-slot, proposal, cursor, delivered-event, snooze, mute and
  reconciled-candidate state remain bounded in memory only.
- Privacy mode masks patient and time details in the projection and cue, keeps
  the live region patient-free, and disables detail-revealing show-context.
- The cue never announces the patient name through the live region.
- Escape dismisses the cue and restores focus to the request field.
- `Review current availability` moves focus only to the already refreshed
  visible context; it does not invoke a command.
- Existing 44 by 44 CSS pixel control, native keyboard, reduced-motion and
  horizontal-overflow requirements remain blocking.
- Blur or document hiding retains the accepted fail-closed interruption rule:
  selected and proposal state are removed and a manual fresh scoped recovery is
  required. An event result racing that interruption may not restore them.

## 6. Threat-model and API-steward disposition

Boundary classification:
`bounded_existing_event_consumer_relevance_plus_read_proposal_reconciliation`.

The required threat delta is
`docs/security/bernie-reception-one-availability-reconciliation-threat-model-delta.md`.
It must cover false relevance, event-payload trust, moved-out-of-window changes,
canonical slot comparison, stale proposal retention, async state races,
duplicate/coalesced attention, cross-practice isolation, shared-screen privacy
and event-to-command escalation.

API-steward invariants remain:

- async events observe committed state and never bypass commands;
- current availability comes only from the existing backend slot-search;
- proposal remains distinct from action;
- any future appointment mutation still requires explicit staff confirmation,
  backend revalidation, idempotency, audit and receipt; and
- broader proactive runtime, other events, providers and production stay
  blocked.

## 7. Implementation and review allocation

Sol retains implementation and the serial browser/database run. The change is a
small but tightly coupled client state machine over the exact event and
availability fixtures; a worker packet would not save a meaningful cycle. No
native subagent or implementation worker is assigned.

A fresh Gemini 3.5 Flash review through Antigravity is required after the clean
candidate, threat delta and evidence are complete. It is an independent veto
over state retention, relevance, privacy, evidence integrity and boundary
width. It receives no edit, acceptance, integration, baton or protected-ref
authority.

## 8. Deterministic acceptance

Focused tests must prove:

- the exact combined request and existing refinements still work;
- availability/proposal families are eligible only through one exact scoped
  practitioner and a fresh appointment read;
- event payload time is not used as availability truth;
- other-practitioner, invalid, replayed, equal/older and failed-read events are
  suppressed;
- a same-practitioner no-consequence reschedule remains silent;
- candidate-set change with a surviving selection preserves the selection and
  replaces it with the fresh raw candidate;
- an occupied selected slot clears selection;
- an occupied proposed slot clears selection and proposal, removes handoff and
  returns to fresh availability;
- no stale async result overwrites a new root or interruption state;
- privacy, cue controls and keyboard focus remain safe;
- no new route, browser persistence, transport, provider, voice, confirmation
  or write primitive is introduced; and
- API Spine and Ariadne inherited contracts remain mechanically enforced.

Repository pytest processes that load `tests/conftest.py` run serially. Exact
focused, inherited functional/live-local/combined-scope/committed-event, API
Spine, Stage 1 proposal and complete Diary regression populations must pass.
Historical protected or immutable evidence is not regenerated.

## 9. Real local browser/backend/PostgreSQL evidence

The repeatable task-scoped Playwright runner drives real Chromium through the
ordinary visible Diary and real loopback FastAPI/PostgreSQL with no
`page.route(...)`, mocked transport, page-internal attention call or fabricated
readback. Browser-driven Reception One traffic remains read/proposal-only. A
separately labelled authenticated support client performs at most two existing
signed reschedules.

The exact disposable authored-synthetic database is
`gp_pms_reception_one_availability_reconcile_7c8e4f21_20260721`. It must not
pre-exist. The provider is disabled, deterministic fallback is false, cloud
credentials are blank, and only the exact marker-verified database and any exact
probe role may be removed after the run.

Required viewports:

- desktop landscape 1440x900;
- tablet landscape 1024x768;
- tablet portrait 768x1024;
- smartphone portrait 390x844; and
- smartphone landscape 844x390.

The evidence label is `live_local_browser_backend_postgres`; the external
support confirmations are `live_local_backend_postgres`. Evidence must cover:

- the exact combined patient/practitioner/date/time/duration scope;
- selection and non-committing proposal preparation;
- one committed reschedule that changes other availability while the chosen
  time remains available;
- one committed reschedule that occupies the chosen time and clears the stale
  selection/proposal;
- fresh remaining alternatives and the exact plain-language cue;
- no duplicate visible effect on idempotent replay;
- other-practitioner and no-consequence suppression;
- dismiss, snooze, mute, review-context, privacy and interruption;
- native Enter, Space, Tab and Escape behavior;
- Back and ordinary full-Diary fallback;
- correct page identity, nonblank content, no overlay, clean console/network,
  zero horizontal overflow, complete painted width and no enabled control below
  44 pixels; and
- exact appointment/update-audit/idempotency/event correlations, cross-practice
  RLS, append-only event behavior, no browser-side mutation, and marker-verified
  database cleanup.

Machine evidence must contain no patient name/id, date of birth, token,
password, credential or raw header. Screenshots may contain only newly authored
synthetic identities.

## 10. Ariadne continuity gates

The new node is `reception-one-availability-reconciliation`. It builds on
`reception-one-committed-event-vertical`, thereby inheriting the accepted
combined-scope contract. The graph adds
`committed-reschedule-availability-reconciliation` as an inherited contract
originating at the event node.

During implementation, the new node records that contract as `gap`. It may be
changed to `satisfied` only when the focused tests and live-local browser/
database evidence are both linked. Ariadne validation and node audit must pass
before acceptance. The engine remains advisory and cannot grant authority,
accept the tranche, create agents, mutate product data or move Git refs.

## 11. Acceptance and closeout

Final `reception_one_availability_reconciliation_pass` requires:

1. the frozen plan and threat delta are satisfied;
2. focused, inherited, API Spine and Diary regressions pass;
3. real-browser responsive, keyboard, privacy and state evidence passes;
4. exact database correlation, RLS, append-only and cleanup evidence passes;
5. no API/database/producer or broader event-family change exists;
6. a fresh Gemini veto has no unresolved material finding;
7. Sol records bounded acceptance, closeout and Ariadne satisfaction;
8. a check-gated pull request integrates; and
9. local/origin `master` and `handoff/current` realign cleanly.

## 12. Boundaries that remain closed

This plan opens no event type beyond `diary.appointment_rescheduled`, no new
appointment action, event acknowledgement, automatic proposal preparation,
confirmation, autonomous repair, GraphQL mutation/subscription, external
broker/worker, WebSocket, persistent attention preference or retention
scheduler. Provider calls, external prompts, PII/real data, protected holdouts,
historical Diary material, Stage 3B, representative participants, voice,
push-to-talk, ambient listening, high-fidelity design, external design models,
production, deployment and release remain closed. Dependabot alert 5 remains
untouched.
