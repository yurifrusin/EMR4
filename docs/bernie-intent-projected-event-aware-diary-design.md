# Bernie Intent-Projected and Event-Aware Diary Design

Date: 2026-07-19

Refined: 2026-07-20 — tablet-first just-in-time projection and touch control

Owner: Yuri / GPT Sol Extra High

Decision: `foundational_product_design_accepted_runtime_not_authorized`

## 1. Foundational decision

The living Diary twin has two inseparable interaction planes from the outset:

1. an **intent-projected Diary** that refigures the visual Diary around the
   user's precise, current need; and
2. a **low-interruption proactive twin** with a carefully filtered nervous
   system connected to committed, typed Diary changes.

These are no longer optional ideas to consider only after conversational
booking. Every future Bernie experience, read model, session contract, event
contract, visual design, and evidence protocol should preserve a place for both.

“From the outset” is a design requirement, not present runtime authority. It
does not authorize Stage 3 execution, an event bus, background delivery,
participants, voice, providers, PII, production, deployment, release, a Claude
subscription, or any new mutation.

## 2. One twin, two directions of attention

### User-directed attention

The user asks *bernie* to answer, open, show, focus, compare, or refine. Bernie
returns a concise answer and, when useful, an authorised visual projection.

Examples:

- “Open Dr Shera's afternoon appointments on Friday week.”
- “Show me all of Margaret Thompson's upcoming appointments.”
- “Compare tomorrow morning's availability for Dr Shera and Nurse Chen.”

The fixed grid becomes one view among many. The underlying Diary remains
structured and authoritative while its presentation becomes fluid.

### Diary-directed attention

The authoritative system reports that something actually committed. Bernie
decides whether the change is relevant to the user's role, current task, active
projection, or recent request and whether it deserves attention now.

Examples include:

- a cancellation creates availability relevant to an active slot search;
- an appointment being viewed is moved or cancelled;
- a staged proposal expires or becomes stale;
- an authorised waiting-state change matters to the current reception task; or
- a roster or schedule change invalidates the visible projection.

Bernie may silently refresh a view, mark the changed area, offer a concise
notice, or ask whether the user wants to act. The event never acts for the user.

## 3. The low-interruption contract

Proactivity is valuable only when attention is treated as a scarce clinical
practice resource. The default hierarchy is:

1. **Silent reconciliation:** refresh authorised state with no interruption.
2. **Passive cue:** mark what changed and retain a “why” explanation.
3. **Concise notice:** one short, contextual message with a direct next-view
   option.
4. **Interruptive alert:** reserved for a separately defined, high-consequence
   condition; never inferred merely from model interest.

Every proactive surface must be:

- role- and practice-scoped;
- relevant to the current or explicitly retained task context;
- deduplicated, coalesced, rate-limited, and explainable;
- dismissible, snoozable, and muteable by event family where safe;
- visibly labelled with what changed, when, and why it was surfaced;
- narrow enough to avoid unnecessary disclosure;
- reversible when it changes the visual projection; and
- silent by default in shared spaces unless a future voice/privacy decision
  explicitly permits an audible form.

No automatic spoken PHI is part of this design. Event awareness is a backend
and user-attention property, not ambient microphone listening.

## 4. Committed typed events

### Committed

An event becomes visible to Bernie only after the authoritative PostgreSQL
transaction succeeds. Failed, provisional, rolled-back, or locally optimistic
state must not produce a user-visible committed-change notice.

A future implementation should use a transactional outbox or an equivalent
mechanism that cannot publish a committed event independently of its source
transaction. Transport may be at least once; user-visible effects must be
deduplicated by stable event identity.

### Typed

Every event uses a versioned, validated envelope. The minimum design fields are:

- event id and event type;
- schema version;
- occurred and received timestamps;
- practice and source-system identity;
- aggregate/resource id and revision where applicable;
- actor/principal, correlation id, and idempotency coordinate;
- evidence mode; and
- a minimal allowlisted payload of opaque ids, times, status codes, and reason
  codes.

Raw instructions, patient names, phone numbers, appointment notes, free-text
reasons, transcripts, provider output, credentials, and clinical content do not
belong in the event envelope.

### A signal to read, not a portable database

The event says that authoritative state changed. Before Bernie displays PHI,
answers a question, or refigures the Diary, the consumer must recheck the
current user's practice/role authority and fetch the current scoped read model.
The event payload is not a substitute for a fresh read and must not become a
shadow Diary.

## 5. Nervous-system sequence

The accepted design sequence is:

`authorised command → PostgreSQL commit → typed event → validation/deduplication → tenancy and role recheck → relevance/attention filter → fresh scoped read → answer or visual projection → optional user-confirmed command`

The sequence preserves the API Spine:

- GraphQL/read models provide current authorised context and never mutate;
- REST/OpenAPI commands remain the only route to state change;
- async events report committed change and never grant command authority;
- YAML capability manifests declare which event frames Bernie may receive;
- FastAPI/PostgreSQL remains authoritative; and
- any proposed follow-up action returns to explicit staff confirmation,
  revalidation, idempotency, audit, and receipt.

## 6. Relevance and attention filtering

The first filter should be deterministic. It should consider:

- exact practice, role, and resource authority;
- relationship to the active patient, practitioner, date, location, proposal,
  Diary projection, or retained task;
- event consequence and time sensitivity;
- novelty, aggregate revision, prior delivery, and supersession;
- whether a fresh read confirms the event remains relevant;
- the user's current mode, quiet state, recent dismissals, and event-family
  preferences; and
- whether the display context can reveal the information safely.

Language intelligence may later help explain or rank already authorised
notices if an observed need supports it. A model must not manufacture events,
override the deterministic safety filter, broaden scope, or turn relevance into
mutation authority.

## 7. Intent-projected meta-grid

An event-aware twin and a fluid Diary view reinforce each other. A relevant
event should not merely generate a notification; it should be able to update or
offer the precise visual projection needed to understand the change.

The projection must preserve orientation through:

- a persistent statement of patient/practitioner/date/time/location scope;
- visible changed-versus-unchanged cues;
- a reason the projection appeared or changed;
- reversible zoom, refinement, comparison, and return-to-overview controls;
- safe ambiguity and identity-resolution states; and
- keyboard, accessibility, density, responsiveness, and reduced-motion design.

### Tablet-first direct manipulation

The intent-projected Diary should make a tablet a first-class reception
workstation rather than compressing a desktop Diary onto a smaller screen. At
a word or a swipe, the surface should project exactly the practitioner,
patient, date, time window, availability, or change context needed for the
current task. The user can then act directly on that narrow visual context with
touch while remaining in control of Diary truth.

A canonical tablet booking sequence is:

`spoken or typed request → scoped availability projection → staff taps a slot → patient identity is resolved or clarified → proposal is displayed → explicit button or conversational confirmation → backend revalidation → idempotent commit → audit and receipt`

The interaction contract is:

- conversation determines or refines the authorised projection;
- a tap is an explicit staff selection, but selecting a slot does not write;
- typing or deliberately speaking a patient name supplies identity evidence,
  and ambiguity still requires clarification;
- a confirmation button and an explicit conversational confirmation are two
  interfaces to the same REST/OpenAPI confirmation command and authority
  checks;
- the backend rechecks current identity, practice scope, role, availability,
  conflict, freshness, and idempotency immediately before writing; and
- the projection reconciles from a fresh read and shows a committed receipt,
  rather than trusting optimistic client or model state.

This creates mobility without loss of visual control. A receptionist can work
away from a fixed multi-screen desk, yet summon spatial Diary context whenever
it helps and inspect the exact proposal before any mutation.

The full fluid UX meta-grid remains a dedicated design tranche, but its
conceptual work should be owned in-house and remain provider-neutral. Projection
grammar, orientation, refinement, attention, proposal, and confirmation
semantics come before high-fidelity styling. A later decision may evaluate
Claude Fable, Kimi, or another design resource as an optional tool, but no
subscription, model use, external transmission, or cost is authorized here and
none is a prerequisite.

## 8. Stage 3 binding

Stage 3 should no longer ask whether event awareness is valuable. Yuri has
accepted it as a foundational product property. Stage 3 should instead test the
safety and usability of representative synthetic attention patterns and gather
evidence for implementation order.

The protocol should include:

- correct answer plus correct intent-projected view;
- view refinement, comparison, and return-to-context;
- a relevant post-commit change surfaced at the appropriate interruption
  level;
- an unrelated event suppressed;
- an uncommitted or rolled-back change never surfaced;
- a replayed event producing no duplicate user-visible effect;
- an out-of-order or superseded event reconciled through a fresh read;
- a foreign-practice event remaining invisible;
- dismiss, snooze, mute, explain-why, and show-context controls; and
- a surfaced event offering a proposal without causing an appointment write.

Synthetic event evidence must retain exact labels: fixture/intercepted evidence
is not a live event backend, and a local committed backend path is not a
production event system.

## 9. Foundational invariants

1. No uncommitted or rolled-back change becomes a committed-event notice.
2. No event bypasses a practice/role/resource check or fresh scoped read.
3. No duplicate, stale, or out-of-order delivery causes a duplicate visible
   effect or action.
4. No event is command authority.
5. No proactive notice mutates the Diary.
6. No follow-up mutation occurs without the normal proposal/confirmation path.
7. No raw free text, unnecessary PHI, secret, provider output, or transcript is
   carried in the event envelope.
8. Every notice can explain the committed source, relevance, scope, and time.
9. Every projection is visibly scoped and reversible.
10. The user can control low-consequence attention without suppressing a future
    separately defined safety obligation.
11. Touch, typing, and conversation may select or confirm through different
    interfaces, but they never create parallel write authorities or bypass the
    single backend proposal/confirmation contract.

## 10. Threats a runtime tranche must address

- cross-practice event leakage or confused-deputy reads;
- event injection, forged principals, and schema downgrade;
- publication before commit or loss between commit and publication;
- duplicate, delayed, reordered, superseded, or replayed delivery;
- event metadata becoming a secondary PHI store;
- notification flooding, alert fatigue, and covert attention capture;
- shared-screen or audible disclosure;
- stale projections that appear current;
- model-generated false urgency; and
- an event consumer becoming a write tunnel.

A future runtime tranche therefore requires exact event producers, outbox and
delivery semantics, retention, dead-letter/recovery posture, consumer
authorization, audit, observability, privacy, performance, and incident gates.

## 11. Authority still closed

This accepted design does not open:

- Stage 3 execution or participants;
- an event broker, outbox migration, background worker, WebSocket/subscription,
  desktop notification, or proactive UI runtime;
- Claude Fable, a subscription, provider calls, or prompt transmission;
- voice capture, ambient listening, or audible PHI;
- real patient or practice data;
- production roles, retention, encryption, deployment, or release;
- GraphQL mutations;
- any new appointment action; or
- autonomous confirmation or model-to-database writes.

Those remain separately accepted tranches. This document ensures that, when
they are considered, the product is designed as a fluid and attentive Diary
twin rather than a chat box bolted onto a fixed grid.
