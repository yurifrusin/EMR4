# Ariadne Bounded Cognitive Work Cell and Proofreader Gate - Protocol Tranche Plan

Date: 2026-07-23

Owner: Yuri / GPT Sol Extra High

Decision: `approved_scope_frozen_for_non_executing_bounded_cognitive_work_cell_protocol`

## 1. Purpose

Yuri authorised a bounded, repository-local, non-executing protocol tranche
using authored-synthetic data only. The tranche will formalise a coarse-grained
cognitive work cell whose authority remains narrow: one declared agent-eligible
booking node may reason across a complete bounded request and emit several typed
draft frames, but no frame may leave its egress boundary until a deterministic
proofreader validates grounding, freshness, scope, authority and cross-output
consistency.

The proofreader may apply only lossless allowlisted canonical repairs. It emits
an immutable verification receipt and the control plane applies a frozen
disposition: release, release to a human gate, request a bounded later attempt,
await fresh context through supersession, or abort the affected edge. Human
escalation is a normal successful transition, not merely an error fallback.

Exact target result: `ariadne_bounded_cognitive_work_cell_protocol_pass`.

## 2. Authority and inherited boundaries

This tranche may:

- define a descendant operational-DAG protocol document and Draft 2020-12 JSON
  Schema using only authored-synthetic opaque practice, principal, patient-
  candidate, practitioner, slot, policy, context, node and attempt references;
- formalise node, topological leaf, execution class, container policy, agent
  eligibility, deterministic verifier, human gate and evidence sink as
  independent concepts;
- add one standard-library Python validator, deterministic proofreader,
  dry-run manifest compiler and Markdown trace renderer;
- represent an agent-eligible booking work cell with no attached model and no
  started container;
- represent multiple typed draft outputs from one coherent work-cell attempt;
- verify allowlisted canonical repair, bounded retry, repeated-failure edge
  abortion, fresh-read supersession, atomic output consistency and human-gate
  routing as inert authored-synthetic traces;
- add deterministic positive and negative artifact tests; and
- register a metadata-only Continuity descendant after all gates pass.

It may not:

- connect to PostgreSQL, any outbox, listener, event feed, broker, product API,
  GraphQL, REST/OpenAPI, FastAPI route or product module;
- invoke or select a model, provider, plugin, external service, browser, server,
  real container, worker, live mailbox, subprocess actuator or command adapter;
- execute a read, proposal, confirmation, appointment mutation, external call,
  deployment or release from a document, verifier result, gate or manifest;
- store PII, clinical content, real staff or patient text, prompts, transcripts,
  credentials, secrets, database rows, provider output, protected evidence or
  historical Diary material; or
- add product behaviour, a runtime scope registry, persistence, durable retry,
  retention, dead-letter handling, automatic action or human-approval UI.

The accepted Sandbox DAG and Synaptic Event Router artifacts remain immutable
predecessor evidence. This tranche is a descendant clarification, not a
retroactive reinterpretation of their accepted results.

## 3. Boundary classification and API Spine pattern

Boundary classification:
`non_executing_agent_context_egress_verification_and_human_gate_protocol`.

The API Spine remains unchanged:

- authenticated practice/principal scope precedes any future agent work;
- agents receive typed, minimal, source-labelled context rather than database
  or API access;
- authoritative identity, availability, policy and freshness remain external
  facts supplied as bounded frames;
- the work cell may emit interpretations, candidates, explanations and
  evidence, but never authoritative identity, availability, policy, approval
  or command frames;
- GraphQL remains read-only and is not called by this tranche;
- REST/OpenAPI remains the future command boundary and is not called or
  described as executable here;
- human approval remains signed evidence for later backend revalidation, not a
  mutation performed by the gate; and
- manifests are inert declarative inputs, not policy executors.

No `docs/api-spine/` artifact change is required. Existing API Spine tests will
be part of the combined gate.

## 4. Frozen protocol decisions

### 4.1 Node granularity and execution classes

The protocol adopts `coarse-cognition-fine-authority`:

- a DAG node is an immutable work/evidence/authority coordinate;
- a leaf is only a topological property;
- a container is an isolation mechanism, not a graph role;
- an agent is an adaptive reasoner that may later inhabit an eligible work
  cell; and
- deterministic functions, joins, gates and sinks need not be pre-containerised.

One coherent work cell may retain interpretation, candidate identity reasoning,
availability ranking, policy explanation, projection preparation and evidence
preparation when practice, principal, sensitivity, freshness, task intent and
authority ceiling remain the same. A split is required when practice/principal,
sensitivity/purpose, freshness/transaction, authoritative fact source, human or
clinical authority, irreversible action, persistence/idempotency lifecycle or
privacy co-presence changes.

Future conversion of a deterministic node into an agent-bearing node requires a
new implementation generation, higher policy revision and fresh authority. An
unused real container is not created merely because a node is agent-eligible.

### 4.2 Bounded context and multi-output work cell

The canonical work cell receives one synthetic request plus exact principal,
patient-candidate, practitioner, availability and evaluated-policy frames. It
has no capability to source additional data itself. A declared context request
can return only to the control plane.

The same work-cell instance may emit independently typed drafts through exact
ports for:

- reversible UX projection;
- human review;
- non-command audit evidence;
- orchestrator outcome; and
- advisory explanation to a human surface.

Each draft carries practice, principal, correlation, context revision, source
frame IDs, authority class, provenance and freshness. Output ports declare
exact frame type, destination, authority ceiling, required payload fields,
allowed payload fields, human-gate requirement and atomic-group membership.

### 4.3 Deterministic proofreader

The proofreader is a pure deterministic function. In fixed order it checks:

1. exact output-port and frame schema;
2. practice, principal and correlation equality;
3. declared source frames and sensitivity ceiling;
4. freshness and exact context revision;
5. authority ceiling and command/action exclusion;
6. referential grounding against supplied patient, practitioner and slot sets;
7. candidate-selection consistency; and
8. cross-output atomic-group consistency.

Allowlisted repair is restricted to stable sorting and duplicate removal for
opaque reference lists. Repair cannot create a reference, resolve ambiguity,
choose an unknown slot, refresh context, change meaning, elevate authority or
infer human approval. The original draft remains immutable; a repaired frame
and receipt record original hash, repaired hash and exact repair rules.

The proofreader emits verdict evidence only. It does not own retry, routing or
authority. The control plane applies the frozen verdict-to-disposition map.

### 4.4 Verdicts, retry and edge abortion

The canonical protocol represents:

- `pass_to_downstream`;
- `pass_to_human_gate`;
- `pass_with_canonical_repair`;
- `pass_with_repair_to_human_gate`;
- `retryable_schema_reject`;
- `retryable_grounding_reject`;
- `stale_context_reject`; and
- `authority_reject`.

Schema and grounding failures may request a later immutable attempt while the
same failure-code budget remains. The retry feedback is a minimal typed reason
frame; it does not expose hidden reasoning or expand context. Reaching the
budget aborts only the affected output edge. Authority rejection aborts the
edge immediately. No automatic loop or hidden mutation is representable.

### 4.5 Fresh context and supersession

A stale-context verdict cannot be repaired or retried as if the old facts were
current. It binds an inert fresh-read grant with `execution_enabled: false` and
`returns_data: false`, supersedes the stale attempt and records a later attempt
with exact practice, principal, instance, checkpoint, notice/grant binding,
incremented attempt/container generation and higher policy revision. The later
attempt remains `awaiting-fresh-context`; this tranche performs no read.

### 4.6 Human gate

Human routing is a valid release path when a draft is grounded and safe but
requires judgment or authority. The gate accepts only declared verified frame
types and names the required role plus typed actions: approve candidate, select
alternative, provide clarification, request fresh context, reject or cancel.

The gate is inert. It cannot turn a verifier rejection into approval, mutate
state or call a command. Any future approval would be confirmation evidence
only and would still require the existing separately authorised backend command
and full revalidation.

### 4.7 Dry-run manifests

The compiler emits deterministic source-hashed manifests for:

- node/execution-class and agent-eligibility posture;
- work-cell context and typed output ports;
- proofreader checks, repair allowlist and verdict mapping;
- bounded retry and supersession;
- atomic output groups; and
- human-gate role, actions and authority stop.

Every manifest declares `dry_run: true`, `execution_enabled: false`,
`default_decision: deny`, `agent_attached: false`, `container_started: false`
and no endpoint, DSN, topic, credential, provider, image or command.

## 5. Exact implementation surface

Implementation is limited to:

- `scripts/ariadne_bounded_cognitive_work_cell.py`;
- this plan, the protocol design, security threat-model delta and closeout;
- `orchestration/continuity/ariadne-bounded-cognitive-work-cell.schema.json`;
- `orchestration/continuity/ariadne-bounded-cognitive-work-cell-example.json`;
- `orchestration/continuity/ariadne-bounded-cognitive-work-cell-dry-run-manifests.json`;
- `orchestration/continuity/ariadne-bounded-cognitive-work-cell-evidence.json`;
- `tests/test_ariadne_bounded_cognitive_work_cell.py`;
- exact orchestration receipts, Sol acceptance and metadata-only node record;
- mechanical Continuity/Compass orientation updates after acceptance; and
- the live handover and orchestration ledger after every gate passes.

No product source, API contract, database fixture, runtime configuration,
frontend, provider artifact or external-worker artifact is in scope.

## 6. Acceptance gates

The tranche passes only when:

1. schema and canonical document pass Draft 2020-12 and semantic validation;
2. predecessor Sandbox DAG and Synaptic Event Router proofs remain unchanged;
3. node topology, execution class, container posture and agent eligibility are
   orthogonal and deterministic leaves are not forced into containers;
4. one work-cell attempt emits at least four distinct typed output ports;
5. the proofreader is deterministic and proves every frozen verdict path;
6. all released factual references are exact subsets of supplied context;
7. repairs are lossless, allowlisted, separately hashed and never rewrite the
   original draft;
8. cross-output atomic inconsistencies fail before any grouped edge releases;
9. retry is immutable and bounded; repeated failure and authority violation
   abort the affected edge;
10. stale context follows inert fresh-read supersession and stale completion is
    rejected;
11. human escalation is a successful verified path but cannot rehabilitate a
    rejected frame or become command authority;
12. dry-run manifests are exact, source-hashed, default-deny and non-executing;
13. static inspection proves no database, network, product, model, provider,
    subprocess, container or command actuator import and exposes only
    `validate`, `verify`, `compile-manifests` and `trace`;
14. focused and combined Ariadne/API Spine/handover tests, Ruff, Python
    compilation, JSON parsing and whitespace gates pass serially; and
15. closeout claims remain limited to an authored-synthetic protocol proof.

## 7. Allocation and reasoning

GPT Sol Extra High owns architecture, implementation, tests, acceptance and
protected integration. No external worker, native subagent or model reviewer is
assigned because the authority semantics, schema, verifier and negative traces
are tightly coupled and Yuri explicitly closed model/provider connections.
Closeout will claim deterministic local Sol acceptance, not an independent
external veto.

## 8. Deferred decisions

Fresh Yuri authority remains required for a fake-agent executor, real model or
provider, real container, sandbox/network enforcement, token broker, product
context read, PostgreSQL, event-feed adapter, persistent mailbox, retry worker,
retention/dead-letter system, human-gate UI, signed approval bridge, appointment
command, PII, protected/historical evidence, Stage 3B, production, deployment,
release or autonomous action.
