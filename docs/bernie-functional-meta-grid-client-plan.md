# Bernie Functional Meta-Grid Client Tranche Plan

Date: 2026-07-20

Owner: Yuri / GPT Sol Extra High

Decision: `approved_scope_frozen_for_functional_client_implementation`

## 1. Purpose

This tranche turns the accepted fluid meta-grid grammar into a bounded working
surface inside the native browser Diary. It tests whether one current Diary can
be projected into the smallest useful receptionist view while keeping scope,
freshness, omissions, state, history and the route back explicit.

The tranche includes plain-language root requests and refinements plus rendered
desktop, tablet, smartphone and native-keyboard evidence. It is local,
provider-neutral and development-only. It does not redesign or release the
Diary.

## 2. Exact client surface

The implementation is limited to:

- `docs/diary/diary.html` for one new script/style include and semantic
  meta-grid host;
- `docs/diary/diary.js` for a small read-only bridge, load-complete signal and
  explicit existing-review handoff;
- `docs/diary/diary.css` only where the existing Diary must yield or restore
  workspace space;
- new `docs/diary/meta-grid.js` and `docs/diary/meta-grid.css` for the typed
  projection state, deterministic plain-language grammar and renderers; and
- deterministic tests and tranche evidence documents.

The ordinary grid remains the initial view and direct fallback. Opening the
meta-grid hides, but does not destroy or replace, the current grid. Returning
to the Diary restores the same authoritative client surface and clears any
transient meta-grid selection or proposal presentation that is stale.

The first functional projection families are:

1. ordinary overview/fallback;
2. focused practitioner/date/time lane;
3. patient upcoming-appointment timeline;
4. availability and reversible slot selection;
5. aligned practitioner comparison, including sequential phone presentation;
6. proposal review labelled `Proposal — not committed`; and
7. clarification/empty/blocked states.

Committed-change context remains design-compatible but no event fixture or
runtime is implemented in this tranche.

## 3. Plain-language contract

The client uses a deliberately bounded deterministic grammar. It may recognise:

- practitioner focus such as `Show Dr Shera today`;
- patient timeline such as `Show Margaret Thompson's upcoming appointments`;
- availability such as `Find Dr Shera availability after 2 pm`;
- aligned comparison such as `Compare Dr Shera and Dr Patel tomorrow morning`;
- selection-to-proposal language such as `Add Margaret Thompson to the selected
  slot`; and
- refinements such as `after 3 pm`, `before 5 pm`, `morning`, `afternoon`,
  `whole day`, `only booked`, `show all`, `back` and `ordinary Diary`.

Every accepted refinement records the exact structured scope delta. Unknown or
ambiguous people, dates, command targets or scope changes enter clarification;
the client does not silently reuse an identity from another root. A new root
clears selection, proposal and attention state. The grammar performs no model
or provider call and retains no prompt or transcript.

## 4. Existing read-model inputs

No API, Pydantic, GraphQL, OpenAPI or database artifact changes.

| Projection need | Existing input | Client rule |
|---|---|---|
| current overview and focused day | loaded Diary appointment/template/roster state or `GET /api/v1/appointments` with date, practitioner and location filters | read-only, practice-scoped, chronologically sorted |
| patient timeline | `GET /api/v1/patients/search` followed by bounded `GET /api/v1/appointments?patient_id=...&date_from=...&date_to=...` | exact identity or clarification; two-year future maximum |
| practitioner resolution | existing GraphQL practitioner directory with its accepted REST fallback | GraphQL stays read-only; no new query or mutation |
| availability and comparison | existing `POST /api/v1/appointments/proposals/slot-search` | non-mutating command-style read; blank grid space never substitutes |
| proposal review | existing `POST /api/v1/appointments/proposals/bernie/supervised-booking` | proposal only; exact backend envelope supplies warnings, blocks and freshness |
| confirmation | existing Bernie review and `confirm-bernie` command family | reached only through an explicit handoff; never called by the meta-grid |

Authorised local smoke evidence uses the Diary's existing authored synthetic
fixtures plus tranche-scoped synthetic future-timeline data. It is labelled
`authored_synthetic_client_fixture_browser`, not live backend evidence.

## 5. Proposal and write boundary

Slot selection is presentation state only. `Prepare proposal` may call the
existing supervised-booking proposal surface when authenticated context is
available. The resulting view must retain patient, practitioner, date, time,
duration, location, warnings, blocks and freshness and must say that nothing
has been booked.

The meta-grid has no confirm control and rejects any confirm endpoint in its
own fetch allowlist. `Continue to booking review` is the only handoff. It makes
the already accepted Bernie review visible with the exact backend proposal
envelope; only that existing surface may expose the explicit staff
confirmation control and call the existing REST command. Backend identity,
practice, role, availability, conflict, freshness, idempotency, audit and
receipt checks remain unchanged.

In authored-synthetic smoke evidence the operational handoff is unavailable
and visibly labelled. No simulated receipt is permitted.

## 6. Responsive, keyboard and privacy contract

- Desktop uses a stable request/history rail and fluid canvas.
- Tablet landscape uses rail plus canvas; tablet portrait stacks the request
  area above the canvas.
- Smartphone uses one column. Comparison becomes an explicit sequential
  practitioner summary with next/previous controls rather than narrow lanes.
- Scope identity, time, location, omissions, freshness, state and route back
  remain visible at every supported width.
- The phone composer remains reachable when the software keyboard is present;
  visual-viewport changes adjust its safe bottom inset and focus scroll.
- Every action uses a native semantic control with a minimum 44 by 44 CSS pixel
  target, visible focus and no hover-, drag- or colour-only meaning.
- Enter submits a request; Enter or Space activates buttons through native
  semantics; Escape dismisses the explanation panel or returns focus without
  causing a command.
- DOM, visual and chronological order agree.
- A privacy control immediately masks patient-sensitive projection content.
  Window blur or page hiding masks automatically. Resume preserves only the
  in-memory non-authoritative projection, marks it stale and requires a fresh
  read before proposal preparation.
- No projection, prompt, history, selection or privacy state is written to
  local storage, session storage, cookies, telemetry or a backend endpoint.

## 7. Acceptance population

### Deterministic artifact and contract gates

Tests must prove:

- the functional contract version and all projection families validate;
- projection state always has `appointment_write_authority: false`;
- the meta-grid fetch allowlist contains only the exact existing read/proposal
  paths and rejects confirmation paths;
- new roots clear selection and proposal state;
- refinements change only named scope dimensions and are reversible;
- appointment/slot items are chronological;
- comparison inputs share date, time, location and duration basis;
- ambiguous identity precedes sensitive projection;
- smoke proposal review cannot hand off or fabricate a receipt;
- no provider, event-runtime, persistence, telemetry, WebSocket, EventSource,
  service-worker or confirmation primitive exists in the meta-grid client;
- phone CSS provides one column, sequential comparison, reachable composer,
  privacy masking and no page-level horizontal overflow; and
- the existing Diary confirmation allowlist and API Spine artifacts are
  unchanged.

### Browser evidence

The route is the real native Diary client in local smoke mode, with no API
interception added by this tranche. Evidence label:
`authored_synthetic_client_fixture_browser`.

Required viewports and flows:

| Viewport | Required flow |
|---|---|
| desktop 1440×900 | open meta-grid; practitioner root; plain-language time refinement; patient timeline; ordinary fallback |
| tablet landscape 1024×768 | availability; touch selection; proposal review; aligned comparison |
| tablet portrait 768×1024 | stacked stable shell; back/refine; no overflow; 44-pixel controls |
| phone portrait 390×844 | one-column focus, patient timeline, availability/selection, proposal review, clarification, privacy mask, interruption/resume and ordinary fallback |
| phone landscape 844×390 | sequential comparison, orientation preservation and reachable controls |
| keyboard at desktop and phone width | tab order; Enter request submit; Space/Enter selection; back; explanation focus; privacy; ordinary fallback |

Every viewport must have zero page-level horizontal overflow, no enabled
interactive target below 44 CSS pixels, no relevant console warning/error and
no framework/error overlay. Browser screenshots are synthetic-only acceptance
artifacts.

### API and regression gates

Run serially:

- `tests/test_bernie_functional_meta_grid.py`;
- `tests/test_api_spine_artifacts.py`;
- `tests/test_api_spine_confirm_client_surface_checkpoint.py`;
- `tests/test_bernie_meta_grid_concept_artifacts.py`;
- `tests/test_bernie_stage3a_study_artifacts.py`;
- `tests/test_bernie_ui_accessible_confirmation.py`;
- `tests/test_agents_handover_archive.py`; and
- `tests/test_ariadne_orchestrator_preflight.py`.

Also run JavaScript syntax checks, focused Ruff, `git diff --check` and exact
source scans for blocked primitives. Repository pytest processes that load
`tests/conftest.py` remain serial.

## 8. Evidence labels

- plan/design/contract: `functional_client_design_artifact`;
- local rendered smoke client: `authored_synthetic_client_fixture_browser`;
- exact API regression: `in_process_backend_contract`;
- browser-to-backend evidence, only if separately exercised without
  interception: `live_local_browser_backend_postgres`; and
- deterministic tests: `deterministic_artifact_test`.

No fixture result may be described as a live backend, committed event,
representative usability, production, deployment or release result.

## 9. Closed gates and stop conditions

This tranche must stop rather than add or alter:

- a FastAPI route, GraphQL field/mutation, Pydantic command, OpenAPI command,
  database table/migration, event producer/consumer, outbox, worker or
  subscription;
- any confirmation or appointment mutation path;
- providers, prompts, cloud services, external design models or subscriptions;
- PII, real patient/practice data, historical Diary material or protected
  evidence;
- Stage 3B, representative participants, voice, push-to-talk, ambient
  listening, production, deployment or release; or
- high-fidelity visual language beyond the functional responsive shell.

A material privacy, command-authority, identity-resolution or product-policy
fork returns to Yuri. Mechanical defects inside this frozen contract may be
corrected and rerun under Sol ownership.

## 10. Worker and reasoning disposition

Sol Extra High freezes the client/API/acceptance boundary. Implementation,
rendered evidence and correction share one stateful native Diary surface, so
Sol retains the tranche under the worker-lane economy rule. No worker,
provider or native subagent is dispatched. Sol High is sufficient for
mechanical implementation, deterministic tests, browser evidence and normal
check-gated closeout once this plan is frozen.
