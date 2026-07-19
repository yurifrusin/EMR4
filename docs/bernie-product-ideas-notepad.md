# Bernie Product Ideas Notepad

Date opened: 2026-07-19

Status: `living_product_notepad_no_implementation_authority`

Purpose: preserve product insights in a durable, easy-to-rehydrate form before
they are promoted into an acceptance plan, architecture decision, or
implementation tranche.

Promotion record: Yuri completed review of Entries 001-002 on 2026-07-19. They
are integrated, together with Entry 003, into
`docs/bernie-intent-projected-event-aware-diary-design.md`, the product north
star, the reshaped Stage 3 decision, and the implementation blueprint. The
entries remain here as provenance and do not independently grant runtime
authority.

## Notepad convention

- Give every entry a stable sequential identifier and date.
- Preserve the originating insight and concrete examples.
- Distinguish product direction from implementation authority.
- Append new entries. Correct an existing entry only to remove ambiguity or
  factual error, and record any material change.
- No entry opens provider, participant, PII, production, deployment, release,
  database-write, GraphQL-mutation, or Stage 3 authority by itself.

## Entry 001 — The intent-projected Diary

Date: 2026-07-19

Source: Yuri, developed in conversation from Experience Principle 1 of the
conversational Diary north star

State: `integrated_into_canonical_product_design_stage3_not_authorized`

### Originating insight

The death of the fixed Diary grid should not mean the loss of visual Diary
information. It should mean that users no longer have to navigate, scan, and
mentally filter one monolithic grid. *bernie* should be able to refigure the
Diary into the precise view needed for the present request.

Examples:

> “Bernie, open the Diary page for Dr Shera’s afternoon appointments on Friday
> week.”

The client should resolve the intended date and time window, open the Diary,
and focus on Dr Shera’s column for that period.

> “Show me all of Margaret Thompson’s upcoming appointments.”

The client should present a patient-centred future-appointment view. That view
need not resemble a conventional practitioner-by-time grid if a timeline or
compact appointment list better serves the request.

### Product principle

Every authorised Diary request may produce two coordinated results:

1. a concise conversational answer; and
2. an immediately useful, reversible visual projection of the same authorised
   live Diary facts.

The grid becomes one projection among many. Date, time range, practitioner,
patient, location, appointment state, availability, conflict, and waiting-room
context can be composed into just-in-time views around the user’s intent.

This is the **intent-projected Diary**: destroy the fixed grid into a myriad of
possible reconfigurations while preserving the structured Diary beneath it.
The user asks for the operational view they need rather than manually
constructing that view through navigation and filtering.

### Experience contract

- If the user asks a factual question, *bernie* should answer it directly.
- If a visual view would help, *bernie* should also construct or offer the
  corresponding projection.
- If the user asks to open, show, focus, compare, or zoom, the requested visual
  projection is the primary result rather than explanatory prose alone.
- The projection should be narrow enough to reduce scanning but retain enough
  surrounding context to prevent misleading interpretation.
- Every projection should be reversible, visibly scoped, and easy to broaden,
  refine, or return to the ordinary Diary view.
- Ambiguous identity, date, time, location, or practitioner references require
  clarification before sensitive information is displayed.

### API Spine boundary

This idea concerns authorised reads and reversible client presentation state.
It does not itself create, move, resize, cancel, confirm, or otherwise mutate
an appointment.

Potential typed presentation intents include:

- `focus_practitioner`
- `focus_date`
- `focus_time_range`
- `show_patient_appointments`
- `show_availability`
- `show_waiting_context`
- `compare_diary_views`
- `reset_diary_view`

These names are product-design vocabulary, not an approved schema. A later
design tranche must decide whether a presentation intent is represented in a
typed *bernie* response, session read model, or local client view contract.
GraphQL remains a scoped read/context graph with no mutation root. Authoritative
scheduling changes remain explicit REST/OpenAPI commands with staff
confirmation, backend revalidation, idempotency, and audit where applicable.

The backend must still enforce practice scope, role/action/resource access,
identity resolution, freshness, and minimum necessary disclosure. A visual
projection cannot broaden what the user or *bernie* is authorised to read.

### Stage 3 implication

The reshaped Stage 3 evidence design should eventually measure three distinct
outcomes:

1. *bernie* supplies the correct answer;
2. *bernie* constructs the correct, safely scoped just-in-time Diary view; and
3. the user completes the task without manually navigating or reconstructing
   the fixed grid.

Candidate synthetic tasks should include practitioner/date/time focusing,
patient-centred upcoming-appointment views, ambiguity recovery, view refinement,
and return-to-context behaviour. Any such addition remains subject to Yuri’s
fresh Stage 3 scope and threshold decision.

### Deeper direction

The long-term product is not merely a conversational layer over a traditional
Diary screen. It is a Diary whose visual form is fluid: authoritative structure
below, conversational intent above, and purpose-built views assembled between
them. The fixed grid survives as a useful overview and fallback—not as the
required starting point for every task.

## Entry 002 — A dedicated fluid UX meta-grid design tranche

Date: 2026-07-19

Source: Yuri

State: `integrated_deferred_programme_dependency_pending_explicit_claude_fable_decision`

### Originating insight

The intent-projected Diary cannot be treated as a conventional grid with more
filters. Its fluid UX—the **meta-grid** that can become many precise views—will
need a substantial visual and interaction design effort in its own right.

Yuri’s current assessment is that Claude Fable is the preferred model for this
visual-design problem. The design tranche should therefore remain deferred
until EMR4 is ready to consider a dedicated one-month Claude subscription for
that purpose.

This is a sequencing preference and product note. It does not authorize a
subscription, cost, provider call, external prompt, content transmission,
account change, or implementation tranche.

### Why this deserves its own tranche

The design must solve more than visual styling. It must establish how a user
remains oriented while the Diary changes shape in response to conversation.
That includes:

- a coherent grammar for practitioner-, patient-, time-, location-, status-,
  availability-, and comparison-centred projections;
- transitions that explain what changed and why;
- persistent scope cues so a narrow projection is never mistaken for the whole
  Diary;
- reversible zoom, refinement, comparison, and return-to-overview behaviour;
- safe ambiguity and identity-resolution states before sensitive information
  appears;
- coordination between Bernie’s answer and the visual projection;
- accessibility, keyboard operation, density, responsiveness, and reduced
  motion;
- graceful fallback to an ordinary overview or grid; and
- an implementation handoff precise enough that the interaction model survives
  translation into the product.

This is the design of a new Diary interaction language, not a cosmetic redesign.

### Candidate tranche outputs

When explicitly authorized, the bounded tranche could produce:

1. a visual and interaction design brief grounded in the north star;
2. a typed projection grammar mapped to representative receptionist intents;
3. wireframes and high-fidelity states for the core projection families;
4. transition, orientation, ambiguity, empty, stale, error, and fallback states;
5. an interactive synthetic-data prototype;
6. an accessibility and usability review;
7. implementation-ready component and behaviour specifications; and
8. a Stage 3/next-stage evidence protocol for testing whether the meta-grid
   actually reduces scanning and manual navigation.

### Possible programme sequence

A future plan may separate the work into:

1. conversational intent and read/projection-contract evidence;
2. the dedicated Claude Fable fluid UX meta-grid design tranche; and
3. implemented visual-projection usability evidence.

That sequence is a candidate only. The relationship between the current Stage
3 decision and the future design tranche must be frozen when Yuri is ready to
authorize the work.

### Decisions reserved for that time

- exact Claude/Fable product, availability, subscription, duration, and budget;
- the permitted synthetic design context and external-transmission boundary;
- whether Claude supplies concepts, an interactive prototype, implementation
  specifications, or some combination;
- ownership of critique, acceptance, and translation into production code;
- the relationship between the design tranche and Stage 3 participant work;
  and
- the exact implementation and release gates after design acceptance.

## Entry 003 — The committed-event nervous system is foundational

Date: 2026-07-19

Source: Yuri

State: `integrated_foundational_product_design_runtime_not_authorized`

### Originating insight

Low-interruption event awareness is invaluable and should be part of Bernie's
Diary-twin design from the outset, rather than a conditional feature considered
only if Stage 3 later rediscovers its value.

The defining metaphor is a **carefully filtered nervous system connected to
committed Diary changes**. The system can notice authoritative change and bring
it into the user's current conversation or intent-projected view without
requiring a manual grid scan.

### Accepted boundary

- Only committed, typed, versioned, practice-scoped events may enter the
  awareness path.
- Failed, provisional, uncommitted, and rolled-back state produces no
  committed-change notice.
- An event signals that current state should be read; it is not a portable
  Diary record, remembered truth, or command grant.
- Before display, the consumer rechecks current role/practice/resource
  authority and fetches the current scoped read model.
- Delivery is deduplicated, relevance-filtered, explainable, dismissible,
  snoozable, and quiet by default.
- A notice may update or offer a visual projection or lead to a proposal. It
  may never perform an appointment mutation.
- Event awareness is not ambient audio and does not authorize automatic spoken
  PHI.

### Promotion

This decision is integrated into:

- `docs/bernie-conversational-diary-north-star.md`;
- `docs/bernie-intent-projected-event-aware-diary-design.md`;
- `docs/bernie-stage3-conversational-diary-decision.md`;
- the appointment-first API Spine event/capability prototypes; and
- `implementation_plan.md` and the live handover.

Stage 3 should test safe attention patterns and implementation priority, not
ask whether the foundational product property is valuable. Runtime event
production, delivery, consumption, notification, and UI authority remain a
separate future tranche.
