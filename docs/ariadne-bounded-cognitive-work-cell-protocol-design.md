# Ariadne Bounded Cognitive Work Cell and Proofreader Gate - Protocol Design

Date: 2026-07-23

Status: bounded repository-local non-executing protocol

## Relationship to accepted Ariadne protocols

This protocol is a descendant of the accepted Sandbox DAG and Synaptic Event
Router designs. It changes neither predecessor result.

The Sandbox DAG proved immutable attempts, bilateral typed edges, direct peer
data exchange, forward-only context requests and a terminal human-authority
gate. The Synaptic Event Router proved deterministic staleness steering,
mailbox/checkpoint boundaries, inert fresh-read grants, supersession and dry-run
policy compilation. This descendant supplies the missing work-cell granularity
and deterministic egress semantics.

The earlier decomposition into identity, availability, policy and ranking
sandboxes was a canonical grammar exercise, not a requirement that every
function or leaf become a separate container.

## Node, leaf, container and agent are independent

The protocol separates four concepts:

- a **node** is an immutable work, evidence, coordination or authority
  coordinate;
- a **leaf** is only a node's current topological position;
- a **container** is a possible execution-isolation boundary; and
- an **agent** is an adaptive reasoner that might later inhabit an eligible
  work cell.

The canonical graph has seven nodes. Its booking work cell is an interior,
agent-eligible `agent-sandbox` node, but `agent_attached` and
`container_started` are both false. Three topological leaves - UX projection,
human gate and audit sink - have no container declaration. Deterministic
ingress, proofreader and control-plane roles likewise remain uncontainerised.

Agent eligibility is therefore a declarative future posture, not a runtime
side effect. Replacing deterministic code with an agent later requires a new
implementation generation, higher policy revision and fresh authority.

## Coarse cognition, fine authority

The cognitive unit is one coherent bounded task. A single work cell may
interpret the synthetic appointment-availability request, reason over patient
candidates, rank supplied availability, explain evaluated policy, prepare a
reversible projection and generate evidence when all of these share:

- one practice and principal;
- one correlation and task intent;
- one sensitivity and purpose boundary;
- one freshness horizon; and
- one non-authoritative candidate ceiling.

The node must split when practice/principal, sensitivity/purpose,
freshness/transaction, authoritative source, irreversible action,
persistence/idempotency lifecycle or privacy co-presence changes. Functional
nouns alone are not split triggers.

The work cell never sources facts. In the canonical example it receives six
authored-synthetic frames: request scope, authenticated principal scope,
patient candidates, selected practitioner, authoritative availability fixture
and evaluated appointment policy fixture. The opaque references and revision
form its complete evidence universe.

## Multi-output ports

One primary work-cell attempt emits five distinct drafts:

1. a reversible UX projection candidate;
2. a booking human-review candidate;
3. non-command audit evidence;
4. an orchestrator outcome; and
5. a grounded advisory explanation code.

Every output port fixes frame type, recipient, channel, authority ceiling,
required and allowed properties, human-gate posture and optional atomic group.
Drafts carry source frame IDs, practice, principal, correlation, context
revision, provenance and freshness. They are untrusted despite being typed.

The work cell cannot construct an authoritative identity, availability, policy,
human approval or command type. Candidate and advisory labels survive the
proofreader; verification does not promote their authority.

## The deterministic proofreader

The proofreader is a pure function and the only egress route. It acts like a
typewriter with a fixed character set and locked form plus a deterministic
proofreader. Its checks run in a fixed order:

1. exact port and frame schema;
2. practice/principal/correlation equality;
3. declared sources and sensitivity posture;
4. freshness and exact context revision;
5. authority ceiling;
6. patient, practitioner and slot grounding;
7. selected-candidate consistency; and
8. atomic cross-output consistency.

The proofreader issues evidence, not control authority. The control plane uses
the frozen verdict mapping to release, request a later attempt, require fresh
context or abort an edge.

### Safe repair

Only two repairs exist:

- remove duplicate opaque references; and
- stable-sort opaque references.

The canonical proof applies both to one UX draft and one human-review draft.
Each repair produces a new derived-frame hash and records the original draft
hash, exact rules and `original_immutable: true`. The original is never edited.

The proofreader cannot invent or infer missing references, resolve ambiguity,
select an unknown slot, refresh stale facts, change meaning, elevate authority
or infer human approval. A draft that needs such work is rejected.

## Verdict and transition grammar

The proof proves eight verdicts:

- `pass_to_downstream`;
- `pass_to_human_gate`;
- `pass_with_canonical_repair`;
- `pass_with_repair_to_human_gate`;
- `retryable_schema_reject`;
- `retryable_grounding_reject`;
- `stale_context_reject`; and
- `authority_reject`.

Passing verdicts create only hashed verified-edge envelopes. Schema and
grounding rejection request a later immutable attempt while the exact reason
budget remains. Stale context cannot be repaired and follows fresh-read
supersession. Authority rejection aborts its edge immediately.

## Bounded retry

Retry feedback contains only the declared correction frame type and reason
codes. It carries no draft body, hidden reasoning or scope expansion.

The same-generation schema example moves from attempt 4 to attempt 5 while
preserving container generation, policy revision and checkpoint. The corrected
draft then passes to the human gate.

The grounding example repeats the same unknown slot failure. Its second
failure reaches the fixed budget of two and aborts the affected edge. There is
no attempt 8 retry loop hidden behind the evidence.

## Fresh context and supersession

The stale draft names context revision 6 while the proofreader requires 7. It
receives `stale_context_reject`, not a repair. An inert grant describes the
exact practice/principal/role/resources and future context-frame type while
declaring `execution_enabled: false` and `returns_data: false`.

The later attempt increments attempt, container generation and policy revision,
names the stale attempt in `superseded_from`, retains its checkpoint and remains
`awaiting-fresh-context`. No read is performed. Any earlier completion is
`rejected-stale-generation`.

## Atomic output groups

UX projection and human review belong to `booking-review`. Their patient,
practitioner, selected slot, duration and context revision must agree. The
negative case supplies individually grounded frames with different selected
slots. Both are changed to `retryable_grounding_reject` and neither edge is
released.

The all-or-none rule also applies when one presented group member fails an
earlier check: any otherwise passing sibling is withheld and receives an
`atomic-group-member-rejected` reason. A failed member can therefore never
leave the proofreader beside a partially released candidate group.

Audit and orchestrator evidence are not members of that atomic candidate group;
a future runtime could still record the failed attempt without presenting an
incoherent candidate.

## Human gate as a normal success path

Human escalation is not proofreader failure. A grounded candidate or advisory
frame may successfully route to the declared reception-staff gate. The gate
accepts only `pass_to_human_gate` or `pass_with_repair_to_human_gate` and offers
typed conceptual actions: approve, select an alternative, clarify, request
fresh context, reject or cancel.

This artifact provides no UI and performs none of those actions. The gate has
`execution_enabled: false`, `command_authority: false` and
`rejected_frame_can_be_rehabilitated: false`. Any future approval is
confirmation evidence only and still needs a separately authorised backend
command with fresh revalidation.

## Dry-run manifests

The compiler emits source-hashed manifests for:

- execution classes and node/container posture;
- exact work-cell context and output ports;
- proofreader checks, repair allowlist and verdict mapping;
- retry budget and stale supersession;
- human-gate role, accepted frames and allowed actions; and
- atomic output consistency.

The manifests are byte-deterministic, default-deny and explicitly set
`agent_attached: false`, `container_started: false`,
`adapters_configured: false` and `execution_enabled: false`. They contain no
endpoint, DSN, topic, image, credential or command.

## API Spine result

Boundary classification:
`non_executing_agent_context_egress_verification_and_human_gate_protocol`.

The protocol keeps context frames minimal and source-labelled. It treats
availability and policy as supplied facts, not work-cell inventions. Advisory
material reaches only a human surface. GraphQL remains read-only and unused;
REST/OpenAPI remains the future command boundary and unused; audit output is
evidence, not a persisted audit record. No `docs/api-spine/` change is needed.

## What remains unproved

This protocol does not prove a model, real container, prompt boundary, token
budget, model interruption, live context sourcing, authorization, product
read, PostgreSQL, event-feed connection, live mailbox, persistent retry,
concurrency, retention, human-gate UI, signed approval, backend command,
clinical correctness, PII handling, production enforcement or product
behavior. Every such surface remains a separate decision.
