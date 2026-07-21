# Reception One availability reconciliation closeout

**Result:** `reception_one_availability_reconciliation_pass`  
**Decision owner:** Yuri  
**Acceptance owner:** GPT Sol  
**Date:** 2026-07-21  
**Source head:** `e469fd60d37ab536152eda8e2cc4997431817110`  
**Reviewed candidate:** `41ecb386bcb0a6f25a56febbc9fe754ebd7af1d3`

## 1. Accepted product result

Reception One now reconciles the accepted combined patient, practitioner, date,
time and duration availability flow after an existing committed reschedule.
The client uses the patient-free event only as a signal, freshly reads the
affected appointment, verifies the one active practitioner, reruns the exact
existing slot search and compares canonical candidate coordinates.

The proved state rules are:

- a changed candidate set preserves a selected or proposed time that remains
  available and replaces its stored raw candidate with the fresh backend value;
- a time that becomes occupied clears selection and non-committing proposal,
  removes handoff, expires affected Back history and shows fresh alternatives;
- an unselected material availability change refreshes the current view;
- another practitioner's event and a same-practitioner event with no candidate
  consequence remain silent; and
- an async result cannot overwrite a newer root, close or interruption, while
  interruption also removes stale selected styling and Back state.

The visible cue is plain, nonmodal, polite, patient-free in the live region and
command-free. `Review current availability`, dismiss, five-minute snooze, mute,
privacy masking and Escape focus restoration remain memory-only controls.

## 2. Evidence

The final task-scoped Playwright run is correctly labelled
`live_local_browser_backend_postgres`. It drove real Chromium through the
ordinary visible Diary, real loopback FastAPI and real PostgreSQL with no route
interception or page-internal event invocation. A separately labelled
`live_local_backend_postgres` support client used only two existing signed
update confirmations and one idempotent replay.

Evidence under
`orchestration/prototypes/reception-one-availability-reconciliation/` proves:

- desktop 1440x900, tablet landscape 1024x768, tablet portrait 768x1024,
  smartphone portrait 390x844 and smartphone landscape 844x390;
- the exact combined request, Space selection, Enter proposal preparation,
  native Tab order, Escape dismissal, touch, normal Back restoration, stale-
  Back expiry, privacy, interruption and ordinary Diary fallback;
- a 3:30 proposal and selection surviving the first reschedule, then being
  cleared when the second reschedule occupies 3:30;
- no browser appointment write, proposal handoff or confirmation activation;
- zero horizontal overflow, no enabled control below 44 CSS pixels, complete
  painted width and clean console/network observations; and
- exactly 6 appointments, 2 update audits, 2 completed idempotency rows, 2
  correlated patient-free events, 0 booking sessions/events, RLS 2/0,
  append-only UPDATE/DELETE rejection and marker-verified database/role cleanup.

Machine evidence contains no patient name/id, date of birth, token, password,
credential or raw header. Screenshots contain only authored-synthetic identities.

## 3. Verification and independent veto

Final serial populations pass:

- 13/13 exact reconciliation artifact/evidence guards;
- 165/165 current Reception One, committed-event, functional/live-local,
  combined-scope, update-confirm route, API Spine, Stage 1 proposal, Stage 3A,
  accessibility, handover and Ariadne tests;
- 211/211 current `test_diary_*.py` tests; and
- 139/139 explicitly named Diary smoke cases.

Node syntax, Python compilation, Ruff, frontend asset-version integrity,
Alembic single-head, Ariadne validation and Git whitespace checks pass.

A deliberately broader Diary-plus-location sweep produced 227 passes and two
legacy location-create failures. Both exact nodes reproduce unchanged at the
untouched source head, and no backend route/schema/fixture involved changed.
The comparison is recorded without rewriting or calling those nodes passing.

Fresh Gemini 3.5 Flash (High), through a new Antigravity project bound to clean
candidate `41ecb386bcb0a6f25a56febbc9fe754ebd7af1d3`, returned `pass` with no
material finding. It independently reran 55 allowed tests plus Node and Ruff.

## 4. API, security and authority disposition

No `app/`, Alembic or OpenAPI file changed. The existing GET event feed,
appointment read, slot-search read and supervised non-committing proposal are
reused. The API Spine receives only the declared active-practitioner fresh-
candidate comparison refinement. No event automatically prepares, confirms,
recreates or repairs a proposal.

The implementation adds no event family, API route, database table/model,
migration, command, GraphQL mutation/subscription, external transport, broker,
background worker, persistent preference or retention scheduler. The accepted
event runtime remains false by default and enabled only in the exact disposable
local harness.

Providers, external prompts, PII/real data, protected holdouts, historical
Diary material, Stage 3B, representative participants, voice, push-to-talk,
ambient listening, high-fidelity design, external design models, production,
deployment, release and autonomous confirmation remain closed.

## 5. Ariadne and next decision

The `reception-one-availability-reconciliation` node now satisfies inherited
contract `committed-reschedule-availability-reconciliation` through focused
tests, real-local evidence, independent veto, Sol acceptance and this closeout.
The graph remains advisory and granted no authority or Git action.

Return the baton to Yuri. No next implementation is implied. The next product
decision may choose either the deferred Reception One visual/interaction
synthesis or a separately planned authority review for another typed Diary
event family. Other event families remain closed unless Yuri explicitly opens
one.

