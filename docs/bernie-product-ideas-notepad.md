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
tablet-first refinement in Entry 004 is integrated into the canonical product
design and north star without changing the frozen Stage 3A protocol. The
entries remain here as provenance and do not independently grant runtime
authority.

Yuri authorised the provider-neutral in-house concept tranche anticipated by
Entry 005 on 2026-07-20. Its accepted interaction grammar, projection contract,
tablet/browser evidence and implementation handoff are recorded in
`docs/bernie-fluid-meta-grid-concept-design.md` and
`docs/bernie-fluid-meta-grid-concept-closeout.md`. Yuri then authorised the
bounded functional client tranche, which passed on 2026-07-20 and is recorded
in `docs/bernie-functional-meta-grid-client-closeout.md`. That implementation
opens no confirmation/write, event-runtime, provider, PII, Stage 3B,
production, deployment or release authority.

The provider-free live-local integration/evaluation subsequently passed on
2026-07-20. Entry 006 preserves the leading provisional **Reception One** name,
the decision to retain **meta-grid** terminology, and the exact context to carry
into Yuri's next focused review. It grants no rename or trademark authority.

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

State: `superseded_by_entry_005_provider_neutral_in_house_sequence`

### Originating insight

The intent-projected Diary cannot be treated as a conventional grid with more
filters. Its fluid UX—the **meta-grid** that can become many precise views—will
need a substantial visual and interaction design effort in its own right.

Yuri’s current assessment is that Claude Fable is the preferred model for this
visual-design problem. The design tranche should therefore remain deferred
until EMR4 is ready to consider a dedicated one-month Claude subscription for
that purpose.

This records the view held on 2026-07-19. Yuri revised the sequencing decision
on 2026-07-20 in Entry 005: the conceptual interaction design is now intended
to proceed in-house and no named design model or subscription is a programme
dependency.

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

## Entry 004 — The tablet as a portable Diary projection console

Date: 2026-07-20

Source: Yuri, during the Stage 3A formative run

State: `integrated_product_refinement_fluid_ux_tranche_not_authorized`

### Originating insight

The just-in-time Diary makes the traditional multi-screen reception workstation
optional. A receptionist carrying a tablet could ask *bernie* to show Dr
Shera's available afternoon appointments, receive precisely that view, tap the
chosen slot, identify the patient, and explicitly confirm the booking without
losing direct visual control of the Diary.

The science-fiction reference is the transparent portable tablet that projects
exactly the view its user needs at a word or a swipe. The important design
lesson is not visual futurism for its own sake. It is that the interface has no
fixed home screen which the user must repeatedly navigate: intent summons the
right operational surface, and touch manipulates it immediately.

### Product refinement

The intent-projected Diary should be **tablet-first without becoming
tablet-only**:

- conversation summons and scopes the just-in-time view;
- the view contains touch-sized, directly manipulable appointments and slots;
- the receptionist may type a patient name or, in a separately authorised
  future voice mode, deliberately ask *bernie* to identify the patient;
- ambiguous identity always produces clarification rather than a guessed
  selection;
- tapping a slot produces or updates a proposal, not an appointment write;
- the receptionist can confirm through a visible button or an explicit
  conversational instruction; and
- both confirmation methods converge on the same backend revalidation,
  idempotency, audit, commit, and receipt path.

This is **mobility without surrendering control**. The user is freed from a
fixed desk and from constant grid scanning, but not from the ability to see,
touch, review, and deliberately confirm the exact Diary action.

### Design-tranche implication

The future fluid UX meta-grid tranche should treat tablet ergonomics as a core
constraint rather than a responsive afterthought. It should explore:

- rapid word-to-view and swipe-to-refinement transitions;
- touch targets, one-handed operation, orientation, density, and accessibility;
- how a selected slot visibly becomes a proposal;
- how patient clarification and confirmation appear without losing the scoped
  Diary context;
- handoff and continuity between desktop and tablet sessions; and
- fresh-read reconciliation after another user or committed event changes the
  visible Diary state.

The frozen Stage 3A study remains unchanged. This entry does not authorise a
tablet implementation, voice, Claude Fable, a subscription, provider calls,
new mutation routes, production, deployment, or release.

## Entry 005 — In-house, provider-neutral meta-grid design sequencing

Date: 2026-07-20

Source: Yuri, during Stage 3A final closeout

State: `promoted_to_completed_in_house_concept_tranche`

### Refinement

The fluid meta-grid should not depend on the availability, price, or reputation
of any named visual-design model. EMR4 should develop the important conceptual
abstractions in-house first: the projection grammar, persistent scope and
orientation, conversational and touch refinement, reversible navigation,
attention behaviour, proposal formation, and confirmation boundary.

High-fidelity styling can be refined after those semantics are stable. Claude
Fable, Kimi, or any later design-capable model may be evaluated as an optional
tool at that time, but none is selected, subscribed to, transmitted data, or
made a prerequisite by this decision. Any future external-model engagement
still requires its own exact product, cost, privacy, synthetic-context, and
transmission approval.

### Programme implication

The recommended sequence is now:

1. define and test the meta-grid's conceptual interaction language in-house;
2. validate that the abstractions preserve orientation, control, safety, and
   task usefulness with deliberately synthetic evidence;
3. implement the functional visual system without waiting for a named design
   provider; and
4. fine-tune visual styling later, optionally using whichever design resource
   is then demonstrably suitable and economical.

Yuri subsequently authorised and completed the bounded conceptual tranche. The
accepted result defines the typed projection grammar, stable orientation shell,
reversible state model, tablet constraints and non-authoritative proposal/event
boundaries. It does not authorize the recommended functional implementation,
a subscription, provider call, prompt transmission, runtime event system,
production, deployment or release.

## Entry 006 — Reception One and the unity of the meta-grid Diary

Date: 2026-07-20

Source: Yuri, after the provider-free live-local meta-grid integration closeout

State: `leading_provisional_name_focused_review_pending_no_rename_authority`

### Originating insight

**Reception One** may become the user-facing name of the meta-grid Diary
system. The name connects the historical Reception 1 station — where the real
Bernie served as an elder stateswoman of the reception team and where current
daily-booking truth was once operationally concentrated — with the modern
product's one authoritative Diary beneath many fluid projections.

The name does not replace **meta-grid**. Reception One names the possible
system identity and its unity; meta-grid names the interaction language that
can refigure that one Diary around a practitioner's, patient's, time window's,
availability search's or proposal review's immediate purpose.

### Product principle

`Many views. One diary.`

Each projection should feel like opening a real diary to the page or section
needed for the task. Attention and layout change, but authoritative truth does
not split. The ordinary fixed grid is one possible page and fallback rather
than the Diary's only real form.

### Next use

Carry this terminology and metaphor into Yuri's next focused review of the
accepted live-local working client. Test whether the name, retained meta-grid
language, persistent scope, reversibility and page metaphor help the system
feel unified rather than fragmented.

The detailed review context is
`docs/bernie-reception-one-focused-review-context.md`.

### Reserved decisions

This entry does not finalise the name, authorise interface or repository
renaming, approve trademark or business-name action, accept cost, or open
high-fidelity visual design. Formal clearance should precede material public
brand investment. Every implementation and authority boundary remains as
closed in the live baton.
