# Ariadne Bounded Agent-Admission Design - Tranche Plan

Date: 2026-07-23

Owner: Yuri / GPT Sol High

Decision: `approved_scope_frozen_for_provider_neutral_non_executing_agent_admission_design`

## 1. Purpose

Yuri authorised the next design descendant of the accepted Bounded Cognitive
Work Cell, Scripted Rehearsal and Real-Isolation Rehearsal. This tranche
defines how generated cognition could later be presented with one bounded
context package and how its output would remain draft-only behind the accepted
deterministic proofreader.

The cognition adapter remains unoccupied. No model is selected, mounted or
called; no prompt or context is transmitted; no container is started; and no
product surface is connected.

Exact target result: `ariadne_bounded_agent_admission_design_pass`.

## 2. Authority and inherited boundaries

This tranche may:

- define a provider-neutral admission envelope, typed context package,
  instruction/evidence separation, resource posture, cancellation contract and
  mandatory proofreader egress;
- catalogue local-in-cell, host-brokered-local and remote-provider topologies
  as unselected future candidates;
- define deterministic authored-synthetic adversarial cases for instruction
  injection, false authority, scope drift, stale context, unknown frame types,
  oversized context, capability requests, cancellation and egress bypass;
- add a standard-library validator and dry-run manifest compiler which perform
  no admission or execution;
- add deterministic tests, evidence and metadata-only Continuity records; and
- update the Compass, handover and orchestration ledger after every gate passes.

It may not:

- select, name, download, mount, load, invoke, emulate or benchmark a model;
- select or call a provider, provider API, model gateway, local inference
  server, host broker, plugin, external worker or adaptive agent;
- transmit a prompt, context frame, embedding, token, output or secret;
- start, build, inspect or modify a container, image, process, server, browser,
  thread, timer, scheduler or network path;
- connect to PostgreSQL, a database, event feed, broker, product API, GraphQL,
  REST/OpenAPI, FastAPI, live mailbox, filesystem mailbox or command adapter;
- use PII, clinical text, credentials, provider output, protected evidence or
  historical Diary material; or
- add product behaviour, persistence, durable retry, human-gate UI, signed
  approval, deployment, release or autonomous action.

The three accepted predecessors remain immutable evidence. The consumed
one-container authority is not renewed.

## 3. Boundary classification and API Spine pattern

Boundary classification:
`provider_neutral_non_executing_generated_cognition_admission_design`.

The API Spine remains unchanged:

- an authenticated practice/principal decision must exist before any future
  context package can be assembled;
- context is typed, minimal, purpose-bound, source-labelled, revision-bound
  and non-authoritative;
- identity, availability, policy and freshness remain supplied facts;
- user-request text and evidence are data, never capability or policy input;
- generated output is `model_interpretation`-class draft evidence only;
- the accepted deterministic proofreader is the sole egress route;
- GraphQL remains read-only and unused;
- REST/OpenAPI remains the explicit command plane and is unused; and
- dry-run manifests are inert declarations, not runtime authorization.

No `docs/api-spine/` or product artifact changes.

## 4. Frozen design decisions

### 4.1 Unoccupied cognition-adapter slot

The work cell exposes one structural adapter slot with
`execution_enabled: false`, `agent_attached: false`, `model_selected: false`
and `transport_selected: false`. Admission validation can prove that a proposed
envelope is structurally bounded; it cannot start or authorize cognition.

Any occupied slot requires a new implementation generation, higher policy
revision, a concrete transport threat model and fresh Yuri authority.

### 4.2 Transport-neutral core and future topology catalogue

The admission contract is independent of transport. The catalogue records:

1. an in-cell local model, which could avoid network and provider secrets but
   would newly require model/image provenance, mounting or image inclusion,
   licence, device and resource decisions;
2. a host-brokered local model, which would add a narrow IPC or local-network
   trust boundary, broker identity and cancellation semantics; and
3. a remote-provider broker, which would add external networking, workload
   identity or secrets, data-processing, jurisdiction, cost and retention
   decisions.

All three are `selected: false` and `execution_enabled: false`. The design does
not guess that a topology is safe merely because it is local.

### 4.3 Instruction plane and evidence plane

Immutable policy codes, allowed frame types, output ports and proofreader
requirements form the instruction plane. User request text and every supplied
fact form the evidence plane. Evidence may ask for work, but it cannot add a
tool, alter policy, select a transport, change an output port, claim approval or
disable the proofreader.

An authored-synthetic request containing an `ignore policy` instruction is
retained as data while the independently hashed policy remains unchanged. This
proves structural separation, not model-specific resistance.

### 4.4 Minimal typed context

Every frame declares an allowlisted type, source label, purpose, practice,
principal, correlation, context revision, sensitivity, freshness and canonical
byte size. The complete frame set is fixed before a future attempt begins.

Unknown types, mixed practice/principal, missing provenance, stale frames,
secret-class material, purpose drift or caps above the envelope fail closed.
The adapter has no read, retrieval or context-request capability.

### 4.5 Model-independent budgets

The design fixes frame-count, canonical-byte, draft-count, output-byte and
attempt caps. It does not invent a token limit while no model or tokenizer is
selected. Token policy is explicitly
`unresolved_until_model_and_tokenizer_selected`; a future topology decision
must add a concrete token accounting rule without weakening the byte caps.

### 4.6 No capabilities, secrets or ambient access

The envelope contains no tool, network, filesystem, process, product-read,
product-write, database, event, mailbox, secret or credential capability. A
future transport cannot infer one from request text or provider convention.
Capabilities must be separately declared and authorised; the default is deny.

### 4.7 Cancellation, supersession and late results

An attempt binds exact policy revision, container generation, context digest
and deadline coordinate. Cancellation is terminal. Any result labelled after
cancellation, deadline or supersession is rejected before proofreader entry.
Fresh context requires the already-accepted new-attempt and supersession path;
an old attempt cannot be refreshed in place.

### 4.8 Draft-only proofreader egress

The only allowed outputs are the five accepted work-cell draft ports. Every
output remains non-authoritative and must enter the accepted deterministic
proofreader. The adapter cannot emit a verified edge, command, approval,
authoritative fact, audit record or orchestrator control instruction. A direct
downstream or human-gate route is an egress-bypass rejection.

### 4.9 Minimal audit posture

Design evidence records hashes, fixed decision codes, policy/context revision,
declared budgets and topology-selection state. It excludes raw prompt bodies,
raw generated content, secrets and chain-of-thought. The authored-synthetic
canonical request exists only in the source fixture and is not echoed by the
CLI trace.

## 5. Exact implementation surface

- `scripts/ariadne_bounded_agent_admission.py`;
- this plan, design, threat-model delta and closeout;
- `orchestration/continuity/ariadne-bounded-agent-admission.schema.json`;
- `orchestration/continuity/ariadne-bounded-agent-admission-example.json`;
- `orchestration/continuity/ariadne-bounded-agent-admission-dry-run-manifests.json`;
- `orchestration/continuity/ariadne-bounded-agent-admission-evidence.json`;
- `tests/test_ariadne_bounded_agent_admission.py`;
- exact receipts, Sol acceptance and metadata-only node record; and
- mechanical Continuity, Compass, handover and ledger updates after pass.

No product source, API contract, runtime configuration, provider artifact,
container artifact or external-worker artifact is in scope.

## 6. Acceptance gates

The tranche passes only when:

1. schema and canonical document pass Draft 2020-12 and semantic validation;
2. predecessor work-cell, rehearsal and isolation source hashes match and
   their accepted evidence remains unchanged;
3. all topology candidates remain unselected, unconfigured and non-executing;
4. context frames are allowlisted, minimal, source-labelled, purpose-bound,
   scope-equal, freshness-bound and canonically byte-capped;
5. instruction-plane policy is independently hashed and cannot be changed by
   evidence-plane mutations;
6. embedded instruction text remains data and grants no policy, capability,
   transport or authority change;
7. cross-practice, cross-principal, stale, secret, unknown-frame and oversized
   context mutations fail closed;
8. tools, network, filesystem, process, database, event, mailbox, product,
   secret and command capabilities remain absent;
9. byte/frame/draft/attempt caps are fixed and token policy remains explicitly
   unresolved rather than guessed;
10. cancellation, expiry and supersession are terminal for the affected
    attempt and late output cannot reach the proofreader;
11. output ports exactly match the accepted draft ports and the proofreader is
    the sole egress route;
12. false authority and proofreader-bypass mutations fail immediately;
13. deterministic source-hashed dry-run manifests are default-deny and contain
    no endpoint, model, provider, image, command or secret;
14. static inspection proves no network, database, product, model, provider,
    subprocess, container, thread, timer, mailbox or command actuator import
    and exposes only `validate`, `compile-manifests` and `trace`;
15. focused and combined Ariadne/API Spine/handover tests, Ruff, compilation,
    JSON parsing and whitespace gates pass serially; and
16. closeout claims remain limited to a non-executing authored-synthetic design.

## 7. Allocation and reasoning

GPT Sol High owns architecture, implementation, tests, acceptance and protected
integration. No external worker, native subagent or model reviewer is assigned:
the authority semantics and negative cases are tightly coupled, and model or
provider connections remain expressly closed. Closeout will claim local
deterministic Sol acceptance, not an external veto.

## 8. Deferred decisions

Fresh Yuri authority remains required to choose a topology or model; set a
model-specific token budget; download or mount weights; build or run another
container; open IPC/networking; introduce provider credentials or cost; send a
prompt or context; accept a generated draft; connect product reads, databases,
events or mailboxes; add durable execution; build a human gate; call a command;
use PII or protected/historical evidence; or enter production, deployment,
release or autonomous action.
