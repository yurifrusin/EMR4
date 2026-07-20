# Bernie Fluid Meta-Grid — In-House Concept Tranche Plan

Date: 2026-07-20

Owner: Yuri / GPT Sol Extra High

Decision: `approved_scope_frozen_for_concept_design`

## 1. Purpose

This tranche defines the interaction language of the intent-projected Diary
before EMR4 invests in high-fidelity visual styling. It answers:

> How can one authoritative Diary become the smallest useful visual workspace
> for the receptionist's present intent, while preserving orientation, direct
> control, fresh-read truth, safe clarification, reversible navigation and one
> backend-owned proposal/confirmation path?

The result is a conceptual and low-fidelity design specification. It is not a
production Diary redesign, deployment, staff study or event runtime.
The lab has no appointment writes.

## 2. Authority

Yuri explicitly authorized this bounded, provider-neutral, in-house conceptual
meta-grid tranche on 2026-07-20.

The tranche may:

- define a typed, non-authoritative projection grammar;
- define projection families, orientation rules and state transitions;
- use deliberately authored synthetic people, appointments and events;
- build an isolated local low-fidelity interaction lab outside the published
  `docs/` site;
- simulate deterministic conversation, touch and keyboard inputs in memory;
- simulate proposal formation without confirming or writing an appointment;
- specify how a future client consumes authorised read models and hands an
  explicit action to existing REST proposal/confirmation commands;
- add deterministic artifact, accessibility and interaction tests; and
- produce an implementation and future-evidence handoff.

The tranche may not:

- call Claude, Kimi, OpenAI or another external design or language provider;
- transmit prompts, screenshots, code, patient data or practice data;
- use real patients, real practices, historical Diary material or protected
  evidence;
- add or alter a production FastAPI route, database schema, GraphQL mutation,
  appointment command, event producer/consumer, background worker or
  subscription;
- edit the production Diary implementation;
- perform an appointment write or simulate a receipt as though committed;
- deploy or release the concept lab;
- use voice, ambient listening, push notifications or automatic spoken PHI;
- retain prompt text, transcripts, telemetry, cookies or local storage; or
- begin Stage 3B or recruit representative staff.

## 3. API Spine classification

The meta-grid is a presentation projection over authorised read/context state.
It is not a new source of Diary truth.

- GraphQL or existing GET/read models may supply fresh, practice-scoped
  appointment, patient, practitioner, availability, session and audit context.
- A typed projection is non-authoritative client presentation state.
- A selected appointment or slot is staff input, not a write grant.
- Proposal formation returns to a typed command-style read/proposal surface.
- Every mutation remains an explicit REST/OpenAPI command with staff
  confirmation, backend revalidation, idempotency, audit and receipt.
- A committed event may request reconciliation; it never supplies displayed
  Diary truth or command authority.

No API Spine runtime artifact is changed by this tranche.

## 4. Required conceptual outputs

### 4.1 Projection grammar

Define a typed contract covering:

- projection identity and revision;
- intent and projection family;
- patient, practitioner, date, time, location, status and resource scope;
- fresh-read evidence and as-of time;
- explicit omitted or intentionally hidden dimensions;
- chronological result items;
- parent/previous projection and reversible history;
- supported inspect, refine, broaden, compare, select and return affordances;
- answer, proposal, block, notice and committed-receipt state labels; and
- a command boundary that cannot be mistaken for write authority.

### 4.2 Projection families

The first concept must cover:

1. practitioner/date/time focus;
2. patient-centred upcoming-appointment timeline;
3. availability and slot selection;
4. aligned practitioner or resource comparison;
5. committed-change reconciliation and changed-versus-current context;
6. proposal review before explicit confirmation; and
7. ordinary Diary overview/fallback.

Waiting-room, room, status and appointment-type views must fit the same grammar
even if they are not all fully demonstrated in the lab.

### 4.3 State and transition model

Define deterministic operations for:

- project a new root intent;
- refine or broaden scope;
- pivot the primary subject;
- compare aligned scopes;
- inspect one result without losing the parent view;
- select a candidate slot or appointment;
- form a proposal without committing;
- clarify identity or missing scope before disclosure;
- reconcile stale or committed-change signals through a fresh read;
- return to the previous projection; and
- reset to the ordinary overview.

### 4.4 Orientation contract

Every non-overview projection must visibly answer:

- what am I looking at;
- whose information is shown;
- what date/time/location is in scope;
- what has deliberately been left out;
- how current is this view;
- why did it appear or change;
- what state is this: answer, selection, proposal, block, notice or receipt; and
- how do I go back, broaden, refine or reach the ordinary Diary?

Starting a new top-level intent creates a clean root projection. Prior views
remain available only through explicit history; no visual or delivery-state
hangover is permitted.

## 5. Local concept-lab scenarios

The authored-synthetic interaction lab must demonstrate:

| ID | Scenario | Required concept evidence |
|---|---|---|
| MG-01 | Show Dr Shera's afternoon on Friday week | focused practitioner/time projection; persistent scope; chronological items |
| MG-02 | Show Margaret Thompson's upcoming appointments | patient timeline; multiple dates; broaden/refine/return |
| MG-03 | Find Dr Shera availability after 2 pm | touch/keyboard slot selection; selected state; no write |
| MG-04 | Add Margaret to the selected slot | proposal review; explicit `proposal_not_committed`; confirmation handoff disabled in the lab |
| MG-05 | Compare Dr Shera and Dr Patel tomorrow morning | aligned comparison; equal temporal basis; no unrelated columns |
| MG-06 | Ambiguous patient or practitioner | clarification before projection or sensitive detail |
| MG-07 | Relevant committed reschedule signal | low-interruption notice; fresh-read reconciliation; changed cue; no action |
| MG-08 | Unrelated, replayed or stale signal | suppression/deduplication; no duplicate visible effect |
| MG-09 | New intent after a prior view | clean root scope with explicit history and no state carryover |
| MG-10 | Return to ordinary overview | reversible fallback without treating grid use as failure |

All data is authored synthetic. Event interactions are fixtures only and must
be labelled `authored_synthetic_event_fixture`; they are not a live event
backend.

## 6. Accessibility and tablet constraints

The concept must include:

- semantic landmarks and headings;
- keyboard access to every interaction;
- visible focus and selected state;
- no drag-only, hover-only or colour-only meaning;
- live-region announcements limited to meaningful scope/state changes;
- chronological DOM order matching visual order;
- touch targets suitable for a tablet concept;
- landscape and portrait layouts without horizontal page overflow;
- reduced-motion behaviour; and
- explicit text labels for answer, proposal, block, notice and receipt states.

These are functional interaction requirements, not high-fidelity styling.

## 7. Acceptance gates

The tranche passes only when:

1. the typed grammar validates every demonstrated projection;
2. every supported transition is reversible or explicitly begins a new clean
   root projection;
3. all appointment and slot items are chronological within their scope;
4. comparison views use the same temporal and location basis;
5. ambiguous identity produces clarification before projection;
6. a slot tap/selection cannot create an appointment;
7. proposal review is visibly not committed and the lab has no operational
   confirmation path;
8. event fixtures cannot act, disclose from payload truth, create duplicate
   visible effects or broaden scope;
9. every event-backed visible change is attributed to a fresh synthetic read;
10. a new intent has no projection, selection, proposal or attention hangover;
11. desktop and tablet-sized browser checks pass the core scenarios;
12. the lab contains no network, persistence, telemetry, provider or runtime
    integration primitive;
13. deterministic artifact tests and `git diff --check` pass; and
14. the closeout identifies the exact next implementation and Stage 3 evidence
    decisions without opening them.

## 8. Evidence labels

- contract/design documents: `conceptual_design_artifact`;
- local browser lab: `authored_synthetic_local_static_prototype`;
- event examples: `authored_synthetic_event_fixture`;
- tests: `deterministic_artifact_test`.

No output may be called a live Diary, live event system, production prototype,
representative usability result or language-model result.

## 9. Deliverables

1. this frozen plan;
2. a canonical conceptual design and implementation handoff;
3. a machine-readable projection contract and valid authored examples;
4. an isolated local low-fidelity interaction lab;
5. deterministic artifact and interaction tests;
6. browser evidence at desktop and tablet dimensions;
7. an accessibility and API-boundary review; and
8. an Extra High Sol acceptance and live-baton update.

## 10. Stop conditions

Return to Yuri before any decision to add runtime API wiring, a production UI,
an event runtime, high-fidelity design, provider/model use, representative
participants, voice, PII, deployment, release or a new appointment action.
