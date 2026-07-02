# EMR4 Event-Driven Architecture With Embedded Statecharts

Captured 2026-07-01 as the design guide for the post-Bernie root-to-branch
revision process.

## Purpose

EMR4 is becoming agent-facing as well as user-facing. Agents such as *bernie*,
*davida*, *scribe*, and future knowledge-base agents do not simply call screens
or endpoints. They observe context, interpret intent, propose transitions, ask
for clarification, and wait for human confirmation where required.

Flat UI flows and ad hoc endpoint calls are not enough for this. They allow
semantic state, visible UI state, and API state to leak into each other. The
current *bernie* live-diary failure is the practical example:

- the receptionist submits `tomorrow`;
- the UI navigates to the candidate day;
- the review flow reuses the mutated diary date as a new reference date;
- `tomorrow` can become tomorrow again.

The architectural response is not "state machines everywhere" as a single
model. The response is an event-driven domain architecture that uses
hierarchical statecharts inside bounded workflows.

## Modelling Stack

Use the following layers together.

1. Domain / bounded-context model
   - Defines the durable areas of EMR4: Diary, Appointments, Patient Identity,
     Consultations, Billing, Agents, Access AI, Audit, Practice Admin, and
     Knowledge Sources.
   - Answers: what part of the system owns this concept?

2. Event model
   - Defines what happens over time: `BookingInstructionSubmitted`,
     `IntentInterpreted`, `CandidateSlotOffered`, `SlotPreviewed`,
     `PatientIdentityChecked`, `BookingConfirmed`, `AppointmentCreated`.
   - Answers: what facts can other contexts react to?

3. Hierarchical statecharts
   - Define local workflow behaviour where state matters.
   - Examples: *bernie* booking session, appointment lifecycle, patient identity
     verification, scribe review/finalise, setup copilot progress.
   - Answers: which transitions are legal from here?

4. API contract model
   - Defines the executable boundary: GraphQL read/context graph, REST/command
     mutations, proposal endpoints, confirmation endpoints, and typed events.
   - Answers: how do clients and agents interact safely?

5. Permission and policy model
   - Defines which actor may initiate or confirm a transition.
   - Examples: *bernie* may propose a booking, a receptionist confirms it,
     *davida* may guide setup, a practice manager can use *davida* admin mode,
     *consultant* may synthesize advice but must not write clinical conclusions
     without GP review.

6. YAML operating layer
   - Defines declarative, machine-readable setup, capability, policy, and
     environment/profile documents.
   - YAML may describe statechart IDs, roles, required services, setup steps,
     evidence-source rules, and agent capabilities. It should not replace the
     typed API contracts or runtime state machines.

## Statecharts Are Local Behavioural Models

Statecharts should be used for workflows where the system must remember what
has already happened and must prevent illegal transitions.

Good candidates:

- *bernie* booking session
- Patient identity verification
- Appointment lifecycle
- Consultation draft -> review -> finalise
- Scribe audio/transcript/review workflow
- *davida* setup and practice-manager administration workflows
- Access AI provider invocation and audit lifecycle

Poor candidates:

- Static data shape
- Simple CRUD resources with no meaningful lifecycle
- Broad system architecture by itself

## Core Rule

State machines model behaviour. They do not replace the domain model, event
model, API contracts, or policy model.

The useful pattern is:

```mermaid
flowchart TD
    Domain["Bounded Contexts"]
    Events["Domain Events"]
    Contracts["API Contracts"]
    Policy["Permission / Policy"]
    Charts["Workflow Statecharts"]
    Agents["Agent Workflows"]
    Audit["Audit / Evidence"]

    Domain --> Events
    Domain --> Contracts
    Domain --> Policy
    Events --> Charts
    Contracts --> Charts
    Policy --> Charts
    Charts --> Agents
    Agents --> Contracts
    Contracts --> Audit
    Charts --> Audit
```

## Agent Design Consequences

Agents should not receive privileged write paths. They should operate through
the same API contracts as human-facing UI, with explicit actor attribution and
audit.

Agent runtime behaviour should usually look like:

1. Observe context.
2. Interpret natural language into typed intent.
3. Normalize into a typed command or query.
4. Enter a workflow statechart.
5. Ask clarification if confidence/policy requires it.
6. Produce a proposal or candidate list.
7. Wait for the authorized human transition.
8. Confirm through the normal API.
9. Emit audit/evidence events.

## Cross-Chart Links

Statecharts can link horizontally or across layers, but only through events and
typed contracts.

Examples:

- *bernie* `BookingConfirmed` emits into Appointment lifecycle as
  `AppointmentCreated`.
- Patient identity state can block or warn in *bernie* without being owned by
  the *bernie* chart.
- Access AI invocation state can wrap *consultant* and knowledge-base agent
  calls without those agents owning provider credentials directly.
- *davida* setup state can produce YAML/environment configuration that later
  shapes runtime API profiles.

## Invariants For Future Design

- Relative time is resolved against an immutable request reference, not the
  current visible page.
- UI navigation is a side effect, not semantic input, unless the user explicitly
  starts a new request using that context.
- State machine memory is explicit. The system stores the active request
  reference date, visible diary date, turn history, patient/practitioner
  recognition, candidate snapshot, selected proposal, freshness flags, and
  confirmation evidence instead of rediscovering them from the DOM or prompt.
- Candidate lists are snapshots. Selecting or revisiting a candidate must not
  reinterpret the original natural-language prompt.
- Human confirmation is a transition with evidence, not a boolean flag hidden
  inside UI state.
- Agent confidence has separate axes. Do not collapse patient identity,
  temporal meaning, practitioner matching, intent, speech quality, and slot
  validity into a single scalar gate.
- Agent context should be precise and staged. Prefer deterministic, typed
  context frames fetched after the relevant entity is recognised over broad
  "dump the system state into the prompt" context.
- Audit records should capture the event, actor, agent/session, confidence
  axes, proposal evidence, and final transition.
- Omitted booking dates are resolved by an explicit transition table:
  selected proposal context first, selected diary appointment context second,
  visible diary page third, and ask if none exists. The old "time present means
  today" rule is deliberately invalid.
- No-slot states are real states, not failed candidate-list states. They should
  produce direct copy plus typed next-action suggestions.
- Patient recognition and patient details verification are separate workflows.
  Recognition can be sufficient for an ordinary booking; Medicare/HI/IHI/PVM/OPV
  verification is a later or parallel details-verification statechart.

## Immediate Application: Bernie

The next implementation step should formalize the *bernie* booking session as a
state machine before more tactical UI fixes. This provides a concrete training
ground for the wider API-spine redesign.

The same modelling discipline should later guide the root-to-branch EMR4 API
review: bounded contexts first, events second, statecharts for workflows, API
contracts for executable boundaries, policy for authorization, and YAML for
declarative operating plans.

The recommended order is now deliberately practical:

1. Continue a few agentic Diary/Taskpane sprints where statecharts and API
   contracts are tested against concrete reception and clinical workflows.
2. Extract the repeated patterns into the root-to-branch API-spine review.
3. Only then decide whether to introduce a statechart runtime such as XState.

The immediate next sprint candidate is *bernie* conversational state memory:
fresh clarification turns, stale-state clearing on diary navigation/refresh,
patient-specific appointment context, no-slot suggestions, and tighter
reception-facing copy.

## Bernie Context-Enrichment Subchart

The *bernie* booking session should treat context gathering as its own nested
statechart, not as incidental prompt assembly. This keeps natural-language
interpretation, diary navigation, patient recognition, and slot search from
bleeding into each other.

```mermaid
stateDiagram-v2
    [*] --> instruction_entry
    instruction_entry --> recognition: BookingInstructionSubmitted
    recognition --> needs_clarification: low confidence or ambiguous entity
    recognition --> context_enrichment: patient recognised or provisional entity accepted
    needs_clarification --> recognition: StaffClarificationProvided

    state context_enrichment {
        [*] --> patient_context_pending
        patient_context_pending --> patient_context_ready: PatientBookingContextFetched
        patient_context_ready --> availability_context_pending: SlotSearchRequested
        availability_context_pending --> availability_context_ready: AvailabilitySnapshotFetched
        availability_context_ready --> [*]
        patient_context_ready --> context_stale: DiaryOrPatientStateChanged
        availability_context_ready --> context_stale: DiaryOrRosterStateChanged
        context_stale --> patient_context_pending: RefreshContext
    }

    context_enrichment --> interpreted: ContextReady
    interpreted --> slot_search
    slot_search --> candidate_selection
    candidate_selection --> proposal_preview
    proposal_preview --> confirmation
    confirmation --> confirmed: StaffConfirmed
    confirmation --> candidate_selection: ChooseAnotherTime
```

Context-enrichment rules:

- Patient recognition comes before patient appointment-history enrichment.
- Once a patient is recognised, fetch a compact deterministic appointment
  context for that patient, such as the previous 2 months and next 2 years of
  bookings, plus derived signals like usual practitioner and existing future
  follow-up.
- Do not feed the LLM every appointment in the diary merely because the context
  window is large. Feed it the small, relevant appointment context that a strong
  receptionist would actually use.
- Day availability is a separate context frame from patient appointment history.
  Availability answers "what slots exist"; patient appointment history answers
  "what should *bernie* know about this patient and this request?"
- Refreshing the diary keeps the *bernie* panel open but clears stale response,
  candidate, and proposal state. Any visible candidate or proposal is tied to
  the context snapshot that produced it.
- Date resolution is now the first concrete transition-table implementation.
  The LLM may extract an explicit date, but if it omits the date, deterministic
  workflow code decides whether the current UI state is strong enough to supply
  it. This pattern should be reused for practitioner inference, patient booking
  history, voice confidence, and proposal freshness.
