# Bernie Fluid Meta-Grid — Conceptual Interaction Design

Date: 2026-07-20

Owner: Yuri / GPT Sol Extra High

Decision: `accepted_provider_neutral_meta_grid_concept`

Evidence: `conceptual_design_artifact`

## 1. Design thesis

The meta-grid is not a large Diary grid with clever filters. It is a typed
projection system that chooses the smallest truthful visual form for the
user's present intent.

The authoritative object remains the structured Diary. The visible object is a
temporary, reversible projection over a fresh, authorised read of that Diary.
Conversation, touch and keyboard are equivalent ways to ask for, refine or
select within a projection; none is a source of appointment truth or write
authority.

The product therefore has three layers:

1. **Diary truth** — FastAPI/PostgreSQL, scoped reads, command revalidation,
   idempotency, audit and receipts.
2. **Projection contract** — typed, non-authoritative intent, scope,
   provenance, items, state, affordances and history.
3. **Interaction surface** — the transient visual form most useful for the
   current task: lane, timeline, slot list, comparison, change context,
   proposal review or ordinary overview.

This preserves the mixed API Spine: GraphQL/scoped read models supply context,
while REST/OpenAPI proposal and confirmation commands retain every mutation.

The visual form may change. The scope, state and route back must never become
ambiguous.

## 2. The stable shell and fluid canvas

Fluid content requires a stable frame. The meta-grid keeps five regions in
predictable locations even when the projection family changes.

### 2.1 Request rail

The receptionist can type a request, choose an authored quick request, or use
a future separately authorised deliberate voice input. Submitting a new
top-level request creates a new root projection with a clean selection,
proposal and attention state.

### 2.2 Scope ribbon

The ribbon is the projection's compact orientation sentence. It always names
the minimum applicable dimensions:

`Margaret Thompson · Dr Shera · upcoming · Brisbane Clinic · as of 2:06 pm`

It also exposes intentionally omitted dimensions when omission could mislead:

`Only confirmed and booked appointments · cancelled appointments hidden`

The ribbon is data, not decoration. It must be available to assistive
technology and remain visible at tablet widths.

### 2.3 Answer and state header

The header says both what Bernie concluded and what kind of state it is:

- `Answer — 3 upcoming appointments`
- `Selection — 2:45 pm slot selected; nothing has been booked`
- `Proposal — ready for review; not committed`
- `Notice — committed change; current Diary re-read at 2:07 pm`
- `Blocked — patient identity needs clarification`
- `Receipt — committed by the Diary command path`

State is never conveyed by colour alone.

### 2.4 Projection canvas

The canvas hosts one projection family. It does not preserve unrelated rows,
columns, dates or selections merely because a previous view used them.

### 2.5 Projection trail

The trail records explicit view lineage:

`Overview → Dr Shera Friday afternoon → availability → 2:45 pm selected`

`Back` reverses one projection transition. `Overview` returns directly to the
ordinary Diary. A new root request starts a new trail while preserving the old
root only in session history.

## 3. Canonical projection model

A projection is a complete presentation contract rather than a loose set of
filters.

| Field | Meaning | Authority |
|---|---|---|
| `projection_id` | Stable identifier for this view instance | client/session coordinate only |
| `projection_revision` | Monotonic revision of the view | detects stale presentation state |
| `root_intent_id` | New top-level request boundary | prevents state hangover |
| `family` | Visual-semantic family | presentation hint, not backend truth |
| `state` | answer, clarification, selection, proposal, notice, block, receipt or overview | explicit user comprehension contract |
| `scope` | person, practitioner, time, place, status and resource constraints | derived from authorised intent/read context |
| `scope_summary` | Human-readable ribbon | must match structured scope |
| `omissions` | Deliberately hidden dimensions or statuses | orientation and minimum-disclosure evidence |
| `freshness` | observed time, expiry/stale state and read source | authoritative-read provenance |
| `items` | Chronological, scoped display items | supplied by fresh read, never event payload alone |
| `layout_hint` | timeline, lane, slots, comparison, change, proposal or overview | client may adapt without changing semantics |
| `affordances` | inspect/refine/broaden/compare/select/back/reset/explain | presentation capabilities only |
| `parent_projection_id` | Immediate reversible predecessor | history coordinate |
| `transition` | trigger, operation, changed dimensions and reason | explains why the view changed |
| `action_boundary` | write capability and required command posture | must default to no write authority |
| `evidence_mode` | exact evidence label | prevents fixture/live confusion |

### 3.1 Scope dimensions

The scope object composes rather than assumes these dimensions:

- `practice_id` — always present internally and never broadened by a view;
- `patient_ids` — zero, one or an explicitly compared set;
- `practitioner_ids` — zero, one or an explicitly compared set;
- `date_from` / `date_to`;
- `time_from` / `time_to` and timezone;
- `location_ids`, room ids and waiting-area ids;
- appointment type and status allowlists;
- availability duration and resource requirements; and
- display limit plus continuation posture.

Missing scope is not silently filled when it could select another person,
practice, date, location, duration or command target. The projection instead
enters `clarification_required`.

### 3.2 Item order

Appointment, slot and event-reconciled items use one canonical order:

1. local date;
2. start time;
3. end time;
4. stable resource display order; and
5. stable opaque item id.

The DOM order, screen-reader order and visual order must agree.

## 4. Projection families

### 4.1 Focused schedule lane

Use for one practitioner, room or other Diary resource over a bounded time
window. The time axis remains visible, but unrelated columns disappear.

Examples:

- Dr Shera, Friday week, 12 pm–5 pm;
- treatment room 2 tomorrow morning; or
- Nurse Chen's vaccination clinic.

The lane shows booked blocks, breaks and free intervals needed to interpret the
window. It does not imply that blank space is bookable unless availability was
authoritatively checked.

### 4.2 Patient timeline

Use for a patient's past or upcoming appointments across dates. A chronological
list or timeline is primary; a practitioner-by-time grid is usually the wrong
shape.

Each item retains date, time, practitioner, location and status. The default is
future appointments within the authorised read horizon, with visible scope and
status omissions.

### 4.3 Availability slots

Use only after a deterministic availability read. Candidate slots are
touch-sized and chronological. Each displays its practitioner, location,
duration basis, warnings and freshness.

Selecting a slot changes the projection state to `selection_only`. It does not
reserve, propose or create an appointment by itself.

### 4.4 Aligned comparison

Use for two or a small number of practitioners/resources under an identical
date, time, location and duration basis. Comparison is invalid if those bases
do not match.

The surface may use aligned lanes, small multiples or a ranked slot list. It
must not add unrelated practice columns simply because the ordinary Diary has
them.

### 4.5 Change context

Use when a committed typed event survives deterministic attention filtering.
The event contributes identity, revision and reason codes only. A fresh scoped
read supplies every displayed Diary fact.

The projection distinguishes:

- previous visible value, when already authorised and retained;
- current read value;
- what changed;
- why this user was shown it; and
- whether the current task or proposal became stale.

### 4.6 Proposal review

Use after the existing proposal path has resolved the patient, practitioner,
slot, duration, location, warnings, blocks and freshness.

The surface must say `Proposal — not committed`, show the exact intended
change, and keep the relevant Diary context visible. The future confirm control
invokes the existing REST confirmation command; it is not a client-side state
transition. This concept lab disables that control because no runtime command
is in scope.

### 4.7 Ordinary overview

The grid remains a first-class spatial overview and escape route. Returning to
it is not failure. The meta-grid must preserve the user's date/location when
safe and useful, but it must not retain a stale selection or proposal.

## 5. Interaction grammar

| Operation | Effect | New read required | Write authority |
|---|---|---:|---:|
| `project` | Create a clean root projection from a top-level intent | yes | none |
| `refine` | Narrow one or more scope dimensions | normally yes | none |
| `broaden` | Expand an authorised dimension | yes and re-authorise | none |
| `pivot` | Change primary patient/practitioner/resource | yes | none |
| `compare` | Add aligned peers under one comparison basis | yes | none |
| `inspect` | Reveal detail for one item without replacing parent scope | when freshness requires | none |
| `select` | Mark an item as staff-selected presentation state | no appointment write | none |
| `prepare_proposal` | Hand selected input to an existing proposal path | backend command-style read | proposal only |
| `clarify` | Resolve missing or ambiguous dimensions | possibly | none |
| `reconcile` | Re-read current scoped state after staleness/event signal | always | none |
| `back` | Restore the immediate retained projection | re-read if stale | none |
| `reset` | Return to ordinary overview and clear transient state | yes | none |
| `explain` | Reveal scope, provenance and transition reason | no | none |

### 5.1 New-root rule

A top-level conversational request creates a new `root_intent_id`. The client
must clear:

- selected item;
- pending proposal presentation;
- prior grid date not named or inherited by the new request;
- prior event-delivery fixture state;
- disabled/enabled controls specific to the old view; and
- temporary clarification candidates.

The previous root remains reachable through history, but it is never
superimposed on the new root.

### 5.2 Refinement rule

A refinement changes only the dimensions it names. The transition record says
exactly what changed, for example:

`time: 12:00–17:00 → 14:00–17:00; reason: user_refinement`

If a refinement would broaden disclosure, switch patient, or change command
target, it requires the same identity and authorisation checks as a new read.

## 6. State machine

The view state is deliberately separate from backend appointment state.

```text
overview
   └─ project ─→ answer_view
                    ├─ refine / broaden / compare ─→ answer_view
                    ├─ inspect ─→ detail_view ─→ back
                    ├─ select ─→ selection_only
                    │              └─ prepare_proposal ─→ proposal_not_committed
                    │                                      └─ external REST confirm handoff
                    ├─ ambiguity ─→ clarification_required ─→ project
                    ├─ stale/event ─→ reconciliation_required ─→ answer/change_view
                    └─ blocked ─→ blocked

any non-committed view ── reset ─→ overview
successful external command ── fresh read + receipt ─→ committed_receipt
```

The concept lab can enter every state except a genuine `committed_receipt`. It
may show the receipt state's specification, but it cannot fabricate one.

## 7. Orientation invariants

1. The scope ribbon is never absent from a non-overview projection.
2. Patient identity is not inferred from a previous root intent.
3. A comparison states the shared basis once and differences per lane.
4. A narrow view states material omissions or offers an immediate broaden
   control.
5. Every view exposes as-of time and stale state.
6. Every view change has an explainable trigger and changed-dimensions record.
7. `Back` has one deterministic target; `Overview` has one deterministic
   meaning.
8. Changing projection family does not change Diary truth.
9. Selection is explicit and reversible.
10. Proposal and committed receipt use different nouns, verbs and controls.

## 8. Clarification, empty, stale and blocked states

### Clarification

Clarification precedes projection when patient, practitioner, date, duration,
location or command intent is ambiguous. Candidate display reveals only the
minimum authorised disambiguation fields. Choosing a candidate is staff input,
not proof of identity outside this workflow.

### Empty

An empty projection repeats its scope and says that the current read returned
no results. It offers safe refinements such as broaden time, change date or
return to overview. It does not reinterpret blank space as availability.

### Stale

Stale state disables proposal/confirmation affordances, preserves the last
visible context as explicitly stale, and offers `Refresh current Diary`. A
fresh read creates a new projection revision and explains any difference.

### Blocked

Blocked state names a typed reason without exposing unauthorised details. It
offers only safe recovery routes: clarify, change scope, return or inspect a
permitted explanation.

## 9. Committed-event attention inside the meta-grid

The event nervous system has three permitted concept effects:

1. **silent reconciliation** — update the current projection revision and mark
   a changed item without interrupting;
2. **passive cue** — add a non-modal change marker and an explain-why control;
3. **concise notice** — state what changed after a fresh read and offer the
   relevant projection.

The event cannot:

- replace a patient or practice scope;
- populate displayed patient facts directly;
- create a selection, proposal or command;
- create a second visible effect on replay;
- let an older revision replace a newer one; or
- become an interruptive alert in this tranche.

The attention record separates `event_received`, `event_suppressed`,
`fresh_read_completed` and `projection_effect`. This makes suppression and
reconciliation inspectable without turning the event stream into a second UI.

## 10. Tablet-first behaviour

The conceptual layout uses one stable shell with an adaptive canvas:

- landscape tablet: request/history rail beside the canvas;
- portrait tablet: compact request bar above the scope ribbon and canvas;
- touch selection has an equally available keyboard action;
- primary targets are at least conceptually 44 by 44 CSS pixels;
- important controls never depend on hover;
- the scope ribbon wraps rather than truncates identity or date;
- the projection trail may horizontally scroll within its own region but the
  page may not overflow;
- comparison collapses to stacked, explicitly aligned lanes in portrait; and
- proposal review keeps the chosen slot and relevant context visible together.

Desktop may show more context, but it must not introduce a different authority
or interaction model.

## 11. Concept component model

The future implementation can remain framework-neutral while using these
stable responsibilities:

- `MetaGridShell` — request, history, responsive regions;
- `ScopeRibbon` — structured scope, omissions and freshness;
- `StateHeader` — answer/proposal/notice/block/receipt language;
- `ProjectionCanvas` — family renderer chosen from typed contract;
- `FocusedLaneProjection`;
- `PatientTimelineProjection`;
- `AvailabilityProjection`;
- `ComparisonProjection`;
- `ChangeContextProjection`;
- `ProposalReviewProjection`;
- `OverviewProjection`;
- `ProjectionTrail` — parent/history navigation;
- `ClarificationPanel`;
- `EvidenceDrawer` — why, source and transition details;
- `AttentionCue` — quiet changed-state affordance; and
- `CommandHandoff` — explicit boundary to existing REST proposal/confirm paths.

Renderers consume one projection contract and emit user input events. They do
not fetch arbitrary data, infer policy or perform commands independently.

## 12. API/read-model mapping

| Projection need | Accepted source pattern | Known gap |
|---|---|---|
| focused practitioner day/window | `diary(date, locationId)` or bounded appointment/roster reads | full DiaryDay envelope remains partly assembled from existing reads |
| patient upcoming timeline | authorised `patient.futureAppointments` / patient booking context | runtime consumer shape may need a bounded appointment-first query |
| availability slots | deterministic slot/availability read | blank grid space must never substitute |
| comparison | repeated aligned scoped reads or a bounded comparison read model | query-cost and shared-freshness contract need later implementation design |
| session history | durable `bernieSession` read model | projection stack is not yet a canonical runtime field |
| event reconciliation | committed signal then fresh scoped read | producer/outbox/consumer runtime remains blocked |
| proposal review | existing proposal envelope/read state | visual contract needs later runtime adapter |
| receipt | existing REST confirm result and stored typed receipt | no change required in this concept tranche |

The principal schema gap revealed here is a typed **presentation projection
frame**: a non-authoritative response/session object connecting interpreted
intent, exact authorised scope, current read provenance and reversible client
view state. This tranche defines it as a concept artifact only; it does not add
the field to GraphQL or runtime Pydantic models.

## 13. Evidence and measurement handoff

A later implementation/evidence tranche should test:

- scope comprehension without facilitator explanation;
- correct differentiation of answer, selection, proposal, notice and receipt;
- task completion without manual grid reconstruction;
- chronological scanning burden;
- successful back/broaden/refine operations;
- absence of state carryover across new roots;
- tablet touch and keyboard parity;
- event-change understanding and interruption burden; and
- grid fallback reasons.

The Stage 3A wording finding should be resolved by asking plain operational
questions rather than abstract labels such as `State understood`.

## 14. Decisions deliberately deferred

- final typography, colour, illustration, animation and component styling;
- React or another production frontend framework;
- runtime GraphQL/read-model shape for projection frames;
- durable projection history across devices;
- event producer/outbox/consumer implementation;
- notification delivery outside the active Diary;
- voice or ambient modality;
- representative staff study and thresholds;
- external design-model use; and
- deployment or release.

These are not omissions in the concept. They are explicit boundaries that keep
the interaction language testable before its technology and visual treatment
are frozen.
