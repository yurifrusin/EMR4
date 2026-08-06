# Raisa Practice Context Fabric

Date: 2026-08-05

Status: accepted direction through occupied authored-synthetic model-required intent shaping

## Purpose

Raisa should become responsive to the working life of a general practice without
turning a provider model into the practice's memory or giving any Bureau a broad
database view. The accepted direction is a backend-owned **Practice Context
Fabric**: a temporal, permissioned substrate that assembles the smallest useful
set of typed context frames for a particular request, Bureau and moment.

The fabric metaphor is deliberate. Authoritative records and events are the
threads; deterministic policy and retrieval form the loom; the user's purpose
selects the pattern; and a response, projection or proposal is a temporary shape
made from those threads. Like clothing, shelter, carpet or a tapestry, the same
material can be composed into many useful forms without becoming an undifferentiated
cloud. Every released shape must retain its weave trace: provenance, scope,
freshness, redaction and expiry.

This is one way to knit Rayleen, Bernie, Davida, Consultant and future Bureaus
into a coherent Raisa intelligence while preserving their distinct roles and
authority ceilings.

## Architectural proposition

The Context Fabric is not a single prompt, vector store, global transcript or
agent memory. It is a deterministic backend service family that turns a scoped
`ContextNeed` into an expiring `ContextFrameSet` from authoritative sources.

```mermaid
flowchart LR
    U["User request and visible product state"] --> I["Model-required intent and ContextNeed candidate"]
    I --> P["Deterministic purpose, role, tenant and data-scope policy"]
    P --> A["Backend Context Assembler"]
    A --> D["Current Diary and waiting-room reads"]
    A --> E["Committed event and temporal snapshot reads"]
    A --> S["Session and recent-work context"]
    A --> C["Later authorised clinical and evidence-source reads"]
    D --> F["Typed expiring ContextFrameSet"]
    E --> F
    S --> F
    C --> F
    F --> B["One authorised Bureau work cell"]
    B --> G["Deterministic grounding, privacy, freshness and authority proofreader"]
    G --> O["Response, intent projection or proposal"]
    O --> H["Separate human-confirmed backend command, when authorised"]
```

The probabilistic layer may interpret the user's request and propose which
context is useful. It cannot decide what the principal may see, retrieve data
directly, extend retention, certify freshness or convert context into command
authority. Those remain deterministic backend decisions.

## Core objects

### `ContextNeed`

A closed, non-authoritative candidate describing the information required to
answer the current request. It should include:

- requesting Bureau, user intent and purpose code;
- tenant/practice and session bindings supplied by the backend, not the model;
- requested entity kinds and tentative identifiers or search features;
- temporal window, such as now, this morning, the last two hours or yesterday;
- source classes, precision requirements and maximum result cardinality;
- freshness requirement and whether historical state is necessary; and
- an explicit `command_authority: false` ceiling.

### `ContextScopeGrant`

A short-lived backend decision that intersects the need with the current
principal, role, practice, location, purpose, consent and source policy. It
records allowed frame types, fields, time windows, row/card limits, redactions,
expiry and reasons for every denied or reduced request. A provider-model output,
UI selection or prior grant cannot substitute for it.

### `ContextFrame`

One typed, source-labelled read projection. Existing EMR4 frame distinctions
remain controlling: live API fact, staff selected, caller signal, manifest
policy, model interpretation and fixture/intercepted evidence must not be
collapsed. Each frame should carry at least:

- frame type and schema version;
- opaque frame and source references;
- practice, purpose and authorised-reader bindings;
- `observed_at`, `assembled_at`, `expires_at` and source revision/event cursor;
- provenance and evidence mode;
- field-level redaction/minimisation disposition;
- content digest and supersession state; and
- `read_only: true` and `command_authority: false`.

### `ContextFrameSet`

The immutable, request-shaped bundle admitted to one Bureau turn. It binds the
need, grant, frames, exact source revisions, omissions, ambiguity state, expiry,
maximum disclosure and a digest. The model and deterministic proofreader must
see the same admitted bundle or an explicitly declared proofreader superset.
Responses and projections cite the frame ids and source revisions that ground
them. A stale or superseded set is reassembled, not patched in place.

### `ContextWeaveTrace`

A patient-safe audit record of how the bundle was produced: requester, purpose,
policy version, source classes queried, scope reductions, frame digests,
freshness, model/proofreader disposition and released output reference. Raw
provider reasoning is not required, and sensitive values should not be copied
into an operational audit merely to prove that they were read.

## Temporal practice memory

The Context Fabric needs several kinds of time-aware backend truth, kept
distinct:

1. **Current operational truth** — current Diary, appointments, waiting-room
   state, practitioner/location directories and other authorised read models.
2. **Committed event memory** — typed facts that a change occurred, used as a
   signal to perform a fresh authorised read. Events are not current truth or
   commands.
3. **Historical operational state** — bitemporal change records or periodic
   immutable snapshots sufficient to answer questions about what the waiting
   room or Diary looked like at a prior time. Retention and access must be
   purpose-specific.
4. **Recent collective work** — a bounded, practice-owned index of relevant
   recent user-visible events and completed actions, separated from private
   per-user conversation state and filtered by role and purpose.
5. **Session state** — the current user's selected entities, visible projection,
   unresolved ambiguity and proposal freshness. It is explicit state-machine
   memory, not a model transcript treated as truth.
6. **Durable domain threads** — later objects such as Consultant's
   `DiagnosticThread`. The domain object owns longitudinal reasoning and
   obligations; the Fabric may carry a scoped frame that references it.
7. **Knowledge-source evidence** — Cochrane and complementary evidence packets
   remain cited source frames with their own licence, version, retention and
   clinical-authority rules. They are not mixed invisibly with practice facts.

Where both "what was known then" and "what was later corrected" matter, the
source should support valid-time and transaction-time semantics rather than
overwriting history.

## Bureau Memory Bank

Recent collective work should be available through a named **Bureau Memory
Bank**, but only as another Context Fabric frame. It is not a new source of
truth, a second audit ledger, a provider-model memory, a global transcript or a
standalone search API.

The compliance audit and the Memory Bank serve different purposes:

- the audit is complete, immutable, compliance-oriented and independently
  retained;
- the Memory Bank is derived, lossy, minimal, purpose-filtered, expiring and
  rebuildable;
- a Bureau never queries or receives raw audit records;
- memory items are historical references, not evidence of current truth,
  identity, present authority or command success; and
- correction or supersession rebuilds or omits a projection rather than
  patching an already released frame.

The first contract should place `bureau_memory_item_set` under the existing
`recent_collective_work` source class. A closed `BureauMemorySelector` may name
originating Bureaus, allowlisted action families, the actor relation (`self`,
`same_practice_staff` or `system`), outcome codes, a temporal hint and a maximum
result count. It must not support free-text audit search, SQL-like predicates,
wildcard sources or model-selected identity scope.

Each released `BureauMemoryItem` should carry only a bounded request label,
action family, outcome code, initiator relation, target kind, policy-permitted
opaque target reference, start/completion times, source receipt/revision/digest,
supersession state, relevance reasons and an
`authority_ceiling: read_context_only`. Raw prompts and responses, before/after
payloads, secrets, IP addresses, user agents, database keys, unrestricted actor
identities and command material are forbidden.

The model may propose one named horizon: `current_turn`, `current_session`,
`current_practice_day`, `previous_practice_day`, `recent_operational`,
`explicit_interval` or `durable_thread_link`. Backend policy converts the hint
into an effective interval by intersecting it with practice timezone, role,
purpose, source availability and the authorised cap. It can only preserve or
narrow the request. Fixture durations used in the first descendant set no
production retention period.

## Example: “Who was that person called George?”

A request such as “Who was the person who came in this morning, probably
George, and was looked after by Priya?” should not cause a whole-day patient or
Diary dump.

The intent layer may propose a need for recent arrivals, a bounded morning time
window, approximate first-name evidence and a staff-attendance relation. The
deterministic scope layer decides whether the requester may perform that lookup
and which identifiers may be disclosed. The assembler queries current and, if
needed, historical waiting-room/event projections, then returns a small ranked
candidate frame with explicit match bases and ambiguity. Raisa can say that one
candidate fits or ask for another discriminator. She must not silently assert
identity, reveal unrelated patients or turn the match into a write.

This exact example requires later product/patient-data, identity, privacy,
retention and runtime authority. Its inclusion here specifies intended
behaviour; it grants none of those authorities.

## Bureau relationship

- **Bernie** receives prospective Diary, patient-booking, availability,
  visible-view, session and recent committed-event frames.
- **Rayleen** receives present and, when authorised, bounded historical
  arrival/waiting-room frames. Queue state and elapsed time remain backend
  calculations.
- **Davida** receives practice profile, directory, capability, policy, audit and
  dry-run frames, never unrestricted administration state.
- **Consultant** receives curated patient/encounter, Diagnostic Thread and cited
  evidence-source frames. The clinician remains the clinical authority.
- **Requests/referrals, prescribing/medicines and billing/claims Bureaus** will
  receive only the task-specific encounter, correspondence, medication,
  eligibility or financial frames independently authorised for their purpose.
  Each retains its own proofreader and command gate.
- **Proofreaders and command services** receive the exact grounding and
  authority bindings needed for their task, not a Bureau's private narrative.

Bureaus may share the Fabric but do not share private model memory or authority.
A cross-Bureau handoff is a new typed request with bilateral scope and provenance,
not an informal transcript transfer.

`RECEPTION ONE™` and the candidate `Clinician One` are user-facing workspace and
projection families, not authorisation domains. The Fabric may knit several
independently granted Bureaus into either experience, including capabilities
that legitimately cross reception and clinical work. The user's current
atomic capability grants determine which Bureaus and actions are present; the
brand, screen or occupational label grants nothing by itself.

## Implementation sequence

The direction should be implemented through narrow descendants rather than one
large “memory” feature:

1. **Fabric and Memory Bank contract** — **accepted** at exact independently
   reviewed source HEAD `cb1b0a712f8ee5340e73d8adde19103af0d9ed97`;
   provider-free authored-synthetic schemas for `ContextNeedCandidate`, backend
   `ContextAuthorityBinding`,
   `ContextNeed`, deterministic `ContextScopeGrant`, `BureauMemorySelector`,
   `BureauMemoryItem`, `ContextFrame`, `ContextFrameSet`, selector/weave trace
   and same-packet proofreader trace, aligned with the API Spine and existing
   Bureau frame contracts. The GraphQL surface remains documentation-only and
   unmounted.
2. **Current operational weave** — **accepted** at exact independently reviewed
   source HEAD `d8bc059212e65a6ed2d7ac8d57734096d14b9139`; four existing
   authorised Diary, waiting-room, directory and private-session read shapes
   compose into one typed expiring bundle without a new product route or data
   source.
3. **Patient-free temporal weave** — **accepted** at exact independently
   reviewed source HEAD `f32004a2f39ac769ba746afe2663813f7c422d8a`;
   immutable parent-bound frame sets are invalidated rather than patched,
   sealed watcher transitions preserve their committed checkpoint before any
   later read, continuity gaps fail closed, and purpose-scoped bitemporal
   snapshots remain historical context rather than current truth. This proves
   no live watcher, persistence or production retention.
4. **Intent-shaped retrieval rehearsal** — **accepted** at exact independently
   reviewed source HEAD `b24b56bda296f3713b5e2c0e52545c749e71540a`;
   five closed authored-synthetic intents deterministically select the minimum
   Current, recent-work and historical components, preserve the four-source
   Current coherence packet, require bilateral Memory sharing, return bounded
   opaque alternatives instead of guessed identity, reject invalidated Current
   state and recompute every upstream and same-packet proofreader.
5. **Occupied model-required intent shaping** — **accepted** at exact
   independently reviewed source HEAD
   `44f341481b55f99a18a47838da0f2b7e43a2f73e`; one primary Sydney Vertex
   `gemini-2.5-flash` call proposed the exact closed comparison intent, and the
   deterministic parent retrieval proofreader alone admitted it. One call and
   USD 0.25 were consumed, no correction or post-success call occurred, no raw
   provider/credential material was retained and owned cleanup completed. The
   controlling frozen plan is
   `docs/raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal-plan.md`.
6. **One-source provider-free adapter** — derive and freeze an unmounted
   authored-synthetic adapter over exactly one existing authorised current
   operational read shape, without a new product route, provider or real-data
   execution. This is the next safe candidate.
7. **Real product read descendants** — open one source and one role/purpose at a
   time with privacy, identity, audit, retention and database acceptance.
8. **Cross-Bureau and clinical descendants** — introduce typed handoffs,
   Diagnostic Thread frames and licensed evidence frames only after their own
   clinical, data and provider gates.

Each descendant must preserve GraphQL/query services as read-only, use REST or
OpenAPI command paths for mutations, revalidate fresh authority at execution,
and release no success based on a context frame alone.

## Permanent boundaries

- No global context dump, ambient unrestricted query or provider-held memory.
- No model-chosen tenancy, role, purpose, retention, source access or field
  disclosure.
- No vector similarity result treated as identity, current truth or clinical
  evidence without authoritative resolution.
- No event treated as current state; every consequential use requires a fresh
  authorised read.
- No stale frame, transcript, prior projection or Bureau output used as command
  evidence.
- No cross-user or cross-Bureau sharing without an explicit typed scope decision.
- No raw audit access, transcript replay, unrestricted actor lookup or standalone
  Memory Bank endpoint; memory is requested only through an ordinary scoped
  `ContextNeed`.
- No patient, product, provider, historical-PHI, clinical, production,
  deployment or release authority is created by this direction.

## Relationship to existing architecture

This direction extends, and does not replace, the API Spine's minimal context
frame rule, Bernie's patient-specific booking frame, Rayleen's freshness-bound
waiting-room projection, Davida's deterministic context desks, the Synaptic
Event Router's typed bilateral scope, the Bounded Cognitive Work Cell's context
admission and Consultant's backend-owned Diagnostic Thread. It supplies the
shared weaving architecture through which those distinct pieces can become one
coherent, responsive Raisa system.
