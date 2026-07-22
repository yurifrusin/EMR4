# Ariadne Sandbox DAG — First Fork Plan

Date: 2026-07-22

Owner: Yuri / GPT Sol Extra High

Decision: `approved_scope_frozen_for_non_executing_sandbox_dag_fork`

## 1. Purpose

Yuri authorised the first deliberate `forked_from` branch in the Ariadne
Continuity Engine so that EMR4 can explore a DAG of sandboxed reasoning leaves
without changing the accepted Compass or Reception One product line.

This tranche will prove a small architectural proposition: an orchestrator can
send typed, least-context inputs into isolated leaves; explicitly connected
leaves can exchange typed frames without routing every value through the
orchestrator; a leaf can return a typed result or request more context; the
orchestrator can grant or deny that request; and fan-out work can converge at
an explicit join. A conversational
exchange that appears to travel backwards is represented as a later immutable
orchestrator and leaf attempt, so the execution history remains acyclic.

The output is a repository-local protocol validator and trace renderer over one
authored-synthetic example. It is not a workflow executor, model harness,
database watcher or EMR command surface.

## 2. Authority and inherited boundaries

The continuity node will be `ariadne-sandbox-dag-fork`, related to
`ariadne-compass-increment2` by `forked_from`. This records a genuine branch and
inherits all globally closed boundaries. It does not move the Compass current
product position or add the branch to the Reception One product journey.

This tranche may:

- define one versioned JSON protocol for immutable nodes and typed exchanges;
- add a standard-library Python validator and deterministic JSON/Markdown trace;
- add one generic authored-synthetic appointment-proposal example containing no
  person names, clinical facts or real identifiers;
- model declared analytical capabilities and bilateral peer communication
  policies as inert descriptors;
- model context requests, grants and denials, fan-out/fan-in, evidence messages
  and a terminal human-authority gate;
- register and accept one metadata-only Continuity Engine exploration node;
- make the mechanical Compass graph-revision compatibility update without
  changing its programme, journey, current position or decision horizon; and
- update the existing Ariadne continuity skill with the reusable safe-use rule.

It may not:

- call or select an LLM, provider, plugin, external service or model transport;
- spawn an agent, task, subprocess, worktree, browser or server;
- execute an EMR command, call a product API, access PostgreSQL or inspect a
  runtime event feed;
- change GraphQL, REST/OpenAPI, FastAPI, Diary, database, migration, event,
  provider, PII, Stage 3B, production, deployment or release code;
- grant capabilities, mutate authority, accept work, move the baton or alter a
  protected Git ref;
- store prompts, transcripts, model reasoning, credentials, secrets, PII,
  historical diary content or protected-evidence content; or
- let a sandbox discover or contact an undeclared peer, use an undeclared
  channel or frame, amend a live container policy, or read shared mutable
  memory outside a typed exchange.

The descriptors in the example are documentation of a possible future
capability lease. They are not executable leases and grant nothing.

## 3. Exact implementation surface

Implementation is limited to:

- `scripts/ariadne_sandbox_dag.py`;
- `docs/ariadne-sandbox-dag-protocol-design.md`;
- `orchestration/continuity/ariadne-sandbox-dag.schema.json`;
- `orchestration/continuity/ariadne-sandbox-dag-example.json`;
- `tests/test_ariadne_sandbox_dag.py`;
- `orchestration/continuity/emr4-continuity-graph.json`;
- the graph-revision fields in `orchestration/continuity/emr4-compass.json` and
  the generated revision footer in `docs/ariadne-compass-current.md`;
- `orchestration/plugins/ariadne-continuity-engine/skills/ariadne-continuity/SKILL.md`;
- this plan, exact receipts, plan review, independent review, evidence,
  closeout and acceptance artifacts; and
- `AGENTS.md` plus the continuity ledger only after every acceptance gate passes.

No product source, product test, API contract, database fixture or runtime
configuration is in scope.

## 4. Frozen protocol

### 4.1 Immutable nodes

Every node has a stable ID, role, instance name, monotonically increasing
attempt number, lifecycle state, accepted/emitted frame types and an inert
capability descriptor. A sandbox also names its container generation and its
immutable communication policy revision. Allowed roles are orchestrator,
sandbox, join, human-context-source, human-authority-gate and evidence-sink.

Nodes do not share mutable memory. A repeated attempt is a new node. A context
request from `sandbox-attempt-1` therefore leads to `orchestrator-v2`, which may
lead to `sandbox-attempt-2`; no graph edge is reversed.

The orchestrator is the control plane, not a compulsory data relay. A sandbox
may send a typed data frame directly to another sandbox only when the sender's
outbound rule and recipient's inbound rule both name the peer instance, channel
and frame. The policy is fixed for a container generation. A changed policy
requires a later container generation, a higher policy revision and an explicit
`restarted_from` reference; the earlier container and messages remain intact.
The v1 artifact validates this restart contract but does not start or restart a
real container.

### 4.2 Typed exchanges

An exchange is both the message envelope and the directed graph edge. It binds
the workflow and graph revisions and names sender, recipient, channel, message
kind, correlation ID, typed frame, bounded property values, provenance,
freshness and source-message evidence.

The channels are:

- data — input, context grant, result and join input;
- control — context request, context denial, candidate transition and authority
  gate; and
- evidence — non-command evidence receipt.

Every property must be declared in the frame catalogue. Unknown properties,
undeclared frames, stale or unproved context grants, duplicate messages and
inconsistent sender/recipient declarations fail closed.

### 4.3 Context and capability discipline

A sandbox may request only a declared input frame and must state why it is
needed. Context grants and denials come only from a later orchestrator node,
carry the request correlation, and are represented by a new sandbox attempt.
Every grant has explicit provenance and freshness.

An undeclared sandbox-to-sandbox exchange is prohibited. Declared peer exchange
is bilateral and frame-specific; it cannot carry command or authority-control
messages. Fan-out may therefore flow through authorised leaf edges before an
explicit join. A node's capability descriptor must be a subset of the
document's fixed analytical capability catalogue; no child can invent or
amplify a capability.

The v1 catalogue contains only inert analytical verbs: inspect a typed frame,
request typed context, evaluate a predicate, emit a candidate transition and
record evidence. Human decision is represented only by the human-authority
gate role. No command, network, filesystem-write, subprocess, provider, Git or
database capability is representable.

### 4.4 Authority termination

The example may end with a `proposal_ready` candidate delivered to a
human-authority gate. The terminal state must remain
`awaiting_human_authority`; there is no confirmed, committed, dispatched or
executed state. Evidence exchanges remain observational and cannot become
commands.

## 5. Example proof

The authored-synthetic trace demonstrates:

1. an orchestrator sends a typed 30-minute, after-14:00 request scope;
2. an identity leaf requests a missing synthetic patient reference;
3. a human context source supplies it only to a later orchestrator version;
4. that orchestrator grants the bounded frame to a second identity attempt;
5. a later orchestrator fans out typed availability and policy work;
6. the availability leaf sends a bounded candidate frame directly to an
   explicitly connected ranking leaf under bilateral start-up policies;
7. the ranked result and policy result converge at an explicit join; and
8. the join emits a non-committing proposal candidate to a terminal human gate.

The example contains generic synthetic identifiers only. It neither queries
availability nor confirms an appointment.

## 6. Acceptance gates

The tranche passes only when:

1. the schema and canonical example pass JSON Schema and semantic validation;
2. the trace is a DAG with a deterministic topological order;
3. the context-request/grant exchange unfolds through new immutable node
   versions rather than a cycle;
4. unknown frames/properties, missing required bindings, duplicate IDs,
   mismatched revisions and unsafe repository references fail closed;
5. undeclared or unilateral sandbox peer exchange, undeclared capability
   amplification and peer control messages fail closed;
6. a communication-policy amendment within the same container generation, or
   without a higher revision and `restarted_from` record, fails closed;
7. a grant without matching request, provenance or fresh status fails closed;
8. a candidate command without a terminal human-authority gate fails closed;
9. forbidden executable capabilities, execution states, sensitive keys and
   sensitive value markers fail closed;
10. static source inspection proves the tool imports no networking, subprocess,
   product application or database modules and exposes no write command;
11. the first real `forked_from` continuity relationship exists, validates and
    audits cleanly without altering the Compass product journey/current node;
12. Compass validation and its generated report remain deterministic after the
    graph-revision compatibility update;
13. the plugin and skill validators, focused and inherited Ariadne tests,
    compilation, Ruff, JSON parsing and `git diff --check` pass;
14. a fresh Gemini 3.5 Flash veto finds no material authority, provenance,
    isolation, privacy or evidence-integrity defect; and
15. Sol records exact acceptance, closeout and protected integration evidence.

No browser, backend or PostgreSQL evidence is required because this tranche
has no UI or runtime. Its evidence label is
`repository_local_authored_synthetic_protocol_trace`.

## 7. Allocation and reasoning

Sol Extra High owns the protocol semantics and acceptance meaning because this
design may inform future workflow authority. Sol implements the small,
tightly-coupled schema/validator/trace directly under the worker-lane economy
rule. No implementation worker or native subagent is assigned.

A fresh Gemini 3.5 Flash review through Antigravity is required over the clean
candidate. Gemini receives no edit, acceptance, integration, baton or
protected-ref authority.

## 8. Deferred decisions

This fork does not authorise:

- a Plan Compiler or workflow executor;
- a modest or frontier model in an orchestrator or leaf;
- real capability leases, container creation/restart or token-budget enforcement;
- automatic context retrieval from PostgreSQL or any product read model;
- EMR command execution or practice-manager approval UI;
- retries, queues, concurrency, durable workflow state or event subscriptions;
- external product data, PII, provider transport, production, deployment or
  release; or
- merging this exploration into the Reception One product journey.

Those are later evidence-led forks. This tranche exists to make their message,
isolation and authority semantics inspectable before any actuator is attached.
