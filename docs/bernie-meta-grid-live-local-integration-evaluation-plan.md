# Bernie Meta-grid Live-local Integration and Evaluation Plan

**Status:** frozen bounded plan

**Date:** 2026-07-20

**Authority:** Yuri's authorization to proceed with the next tranche recommended by the accepted functional meta-grid closeout

**Evidence target:** `live_local_browser_backend_postgres`

## 1. Decision and result sought

This tranche connects the accepted functional meta-grid client to the existing
local EMR4 FastAPI/PostgreSQL read and proposal-only surfaces and evaluates the
ordinary user-visible path in a real browser. It must show that a receptionist
can ask for, refine and act on a focused Diary view without the meta-grid
becoming a source of clinical or scheduling truth.

The result may be `meta_grid_live_local_integration_pass` only when the real
client, real local backend and one disposable authored-synthetic PostgreSQL
database pass the exact browser, API, database and boundary gates below.

This is integration and evaluation evidence. It is not Stage 3B,
representative usability, provider, committed-event, production, deployment or
release evidence.

## 2. Frozen authority

The tranche may:

- use the existing native Diary and accepted meta-grid files;
- create one explicitly named, disposable, loopback-only PostgreSQL database;
- seed only newly authored synthetic practice, staff, practitioner, patient,
  schedule, roster and appointment rows;
- authenticate one synthetic receptionist through the ordinary login route;
- drive the visible UI with task-scoped Playwright and use interactive browser
  control for diagnosis;
- call the existing read and non-mutating proposal surfaces named in section 4;
- make bounded client or harness corrections required to satisfy this frozen
  behavior; and
- add deterministic tests, screenshots, sanitized request observations,
  database readback, closeout and acceptance artifacts.

It may not add or alter an API, GraphQL schema, Pydantic command, OpenAPI
contract, database model/migration, provider integration, event producer or
consumer, confirmation route, appointment write, deployment or release
surface.

## 3. Runtime and authored-synthetic population

The harness owns the exact database
`gp_pms_meta_grid_live_local_7f3c2a91_20260720`. It must refuse a different
database name, a non-PostgreSQL backend, a non-loopback host, or reuse of an
existing database. Cleanup may drop only that exact database after verifying
its harness marker and terminating its connections.

The fixed Diary reference date is Monday 2026-07-27. The population contains:

- one synthetic Queensland practice and Main Clinic location;
- one allowlisted synthetic receptionist;
- three synthetic practitioners, including Dr Alex Shera and Dr Anika Patel;
- at least two synthetic patients, including Margaret Thompson;
- Monday schedules and matching Diary columns/roster entries;
- several booked/arrived/completed authored-synthetic appointments spanning
  focused-practitioner and patient-timeline views; and
- zero initial appointment audit, appointment-command idempotency, Bernie
  booking-session and Bernie session-event rows.

The child runtime must set the interpreter provider to `disabled`, clear cloud
credential environment variables, bind FastAPI and the static Diary server to
loopback, use an ephemeral JWT secret, and never record a password or bearer
token in committed evidence.

## 4. Existing route population

The browser may make the ordinary Diary bootstrap reads below:

- `POST /api/v1/auth/login`;
- `GET /api/v1/diary/locations`;
- `GET /api/v1/diary/template`;
- `GET /api/v1/appointments`;
- `GET /api/v1/appointments/types`;
- `GET /api/v1/diary/roster`;
- `GET /api/v1/diary/waiting-areas`;
- `POST /api/v1/graphql` for the existing practitioner directory read, with
  `GET /api/v1/practice/practitioners` allowed only as its existing fallback;
  and
- `GET /api/v1/appointments/bernie/pilot-eligibility`.

The meta-grid may additionally call only:

- filtered `GET /api/v1/appointments` for practitioner and patient timelines;
- `GET /api/v1/patients/search` for explicit patient resolution;
- `POST /api/v1/appointments/proposals/slot-search` for availability; and
- `POST /api/v1/appointments/proposals/bernie/supervised-booking` to prepare a
  backend-owned, non-mutating proposal envelope.

The local route must explicitly use `bernie_session=false` and the
loopback-only `standalone_diary=true` capability. That capability supplies only
the `Office.onReady` bootstrap needed by the unchanged native Diary scripts; it
prevents the browser-only evidence run from fetching Office.js externally and
is ignored off loopback. Normal Office dialog loading remains unchanged.
Requests to any
`/appointments/bernie/sessions` route, any confirmation route, raw appointment
mutation, WebSocket, EventSource, telemetry endpoint, external origin or
provider endpoint are stop conditions. Playwright must not use `page.route`,
mock responses, call page-internal functions in place of visible actions, or
invoke `Continue to booking review`.

## 5. Plain-language and interaction scenarios

All inputs are typed into the visible plain-language composer or activated
through visible native controls.

The authenticated browser begins on the ordinary Diary at the current local
date, uses its visible next-day control to reach the fixed 2026-07-27 synthetic
date, and opens the meta-grid with the visible `Project view` control. No page
state is assigned through script.

1. **Practitioner focus and refinement:** `Show Dr Shera today`, followed
   by `after 2 pm`, must retain practitioner/date context and change only the
   time boundary.
2. **Patient timeline:** `Show Margaret Thompson's upcoming appointments` must
   resolve the exact synthetic patient through the existing search/read path
   and show a chronological timeline.
3. **Availability and selection:** `Find Dr Shera availability today after 2
   pm` must show backend candidate slots. Pointer/touch or native keyboard
   selection changes only transient client selection state and visibly says
   that nothing is booked.
4. **Proposal review:** `Add Margaret Thompson to the selected slot` must call
   the existing supervised proposal surface and render `Proposal — not
   committed`, warnings/evidence in plain language, and the statement that no
   appointment has been created. The handoff control may be visible but is not
   activated.
5. **Aligned comparison:** `Compare Dr Shera and Dr Patel today morning`
   must preserve one date/time/location/duration basis; narrow landscape uses
   sequential next/previous navigation.
6. **Privacy and interruption:** privacy masking must cover sensitive cards;
   a browser blur/visibility transition must mark the projection stale, clear
   transient selection/proposal state and require a fresh read. Foreground page
   switching is preferred. Because headless Chromium does not always emit blur
   when foreground pages change, the runner may dispatch the standard DOM
   `blur` event as a labelled fallback; it must never call the meta-grid's
   interruption function directly.
7. **Ordinary fallback:** `Return to full Diary grid` must restore the existing
   Diary without a write or fabricated receipt.

## 6. Viewport and keyboard evidence

The repeatable Playwright run records:

| Surface | Size | Required evidence |
|---|---:|---|
| desktop landscape | 1440×900 | practitioner root, refinement, patient timeline, ordinary fallback, full painted width |
| tablet landscape | 1024×768 | availability, pointer/touch selection, proposal review, aligned comparison |
| tablet portrait | 768×1024 | stacked shell, refinement, exact Back restoration |
| smartphone portrait | 390×844 | one-column timeline, availability, Space selection, proposal review, privacy, interruption and fresh-read recovery |
| smartphone landscape | 844×390 | one visible comparison lane with usable next/previous controls |

Keyboard evidence covers native Tab order, Enter submission, Space/Enter slot
selection, Back, explanation opening and Escape dismissal with focus return,
privacy, and ordinary fallback at desktop and smartphone widths.

Every viewport must have zero page and host horizontal overflow, no enabled
interactive control smaller than 44 CSS pixels in either dimension, no error
overlay, and no console warning/error. Patient details must not appear in
sanitized JSON evidence.

## 7. Desktop capture integrity gate

The previous accepted desktop PNG contained a capture artifact: its 1440-pixel
canvas was black after approximately x=768 even though a fresh real-browser
reproduction measured the rendered document, header and meta-grid host at the
full 1440-pixel width with zero overflow.

This tranche does not rewrite the historical artifact. It records a new
1440×900 live-local screenshot and checks both DOM geometry and raster content:

- `window.innerWidth`, document/body client width and meta-grid host width must
  reach the requested viewport;
- the rightmost 20% of the screenshot must contain sufficient non-black,
  non-transparent painted pixels; and
- a painted-content bounding box must extend beyond 95% of image width.

Failure is a capture failure even when DOM geometry passes. The evidence
package and deterministic artifact test both enforce the guard.

## 8. Database and network readback

Before the first scenario and after the final scenario, the harness records
sanitized counts and canonical SHA-256 snapshots for:

- `appointments` truth rows;
- `appointment_audit_log`;
- `appointment_command_idempotency`;
- `bernie_booking_sessions`; and
- `bernie_session_events`.

Every before/after count and hash must be identical. The last four tables must
remain at zero rows. The browser trace must contain only the loopback static
origin and the exact route population in section 4, with no confirmation,
session-runtime or mutation method/path.

## 9. Deterministic and regression gates

Run serially where PostgreSQL-loading tests share the test schema:

- focused live-local harness/artifact guards;
- the existing functional meta-grid tests;
- exact slot-search and supervised-booking proposal tests, including provider
  disabled and zero-write cases;
- API Spine route/inventory/drift guards;
- Stage 3A and Diary regression populations selected by the previous
  acceptance;
- JavaScript syntax checks, focused Ruff, `git diff --check`, and blocked
  primitive/route scans; and
- the task-scoped Playwright run against the disposable runtime.

No route-intercepted test is relabelled as live. The Playwright result is
`live_local_browser_backend_postgres` only after its browser request trace and
PostgreSQL readback both pass.

## 10. Independent veto and acceptance

Sol owns planning, execution, acceptance and protected integration. The shared
serial browser/database run remains Sol-owned because dispatch would not save a
meaningful cycle. Near acceptance, a fresh Gemini Flash/Antigravity context
receives a bounded read-only packet covering this plan, the implementation
diff, sanitized evidence and closed boundaries. Gemini returns `pass`,
`revision_required` or `blocked` and cannot accept its own work, move the baton
or push protected refs.

## 11. Stop conditions and closed gates

Stop and return to Yuri rather than expanding into:

- any API, GraphQL, OpenAPI/Pydantic, database or migration change;
- confirmation, appointment mutation, autonomous action or receipt authority;
- Bernie session/event runtime, outbox, worker, subscription or committed-event
  claim;
- provider calls, external prompts, design-model subscriptions or costs;
- PII, historical Diary material or protected evidence;
- Stage 3B, representative participants, voice, push-to-talk or ambient
  listening;
- production, deployment or release; or
- a material product, privacy, identity, authority or visual-language fork.

Mechanical client, harness, evidence or test defects inside this exact plan may
be corrected and rerun. A failed database delta, forbidden request, external
network attempt or ambiguity about write/event authority is not waived.
