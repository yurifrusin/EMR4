# Ariadne Sandbox DAG — Protocol Design

Date: 2026-07-22

Status: bounded non-executing exploration

## Plain-language model

Ariadne can be thought of as a synaptic network of small, isolated workers.
The orchestrator decides which workers exist, what each is allowed to receive
and send, and where human authority is required. It does not need to carry every
message itself.

A worker may pass a typed result directly to a connected worker. That link is
not an open network connection: both workers must have been started with rules
that agree on the other worker, the channel and the exact frame type. If either
side does not agree, the message is invalid.

This yields two distinct planes:

- the control plane creates the graph, assigns bounded context and analytical
  capabilities, fixes communication policies and records restarts; and
- the data plane carries typed messages over already declared graph edges,
  including direct leaf-to-leaf “synapses”.

The current artifact only describes and validates those planes. It does not
start a container, attach a model, read EMR4 or execute a command.

## Why the history remains a DAG

A worker may discover that it lacks context. It returns a typed request. The
orchestrator may source, grant or deny that frame, but the continuation is a
later immutable attempt. The earlier attempt and request are never rewritten.

Likewise, a communication-policy amendment cannot mutate a running container.
It produces a later container generation with a higher policy revision and an
explicit `restarted_from` link. Messages sent by the earlier generation retain
their original policy evidence.

These two rules turn apparently backward conversation into forward history:

```text
orchestrator-v1 -> identity-attempt1 -> orchestrator-v2
orchestrator-v2 -> context-source -> orchestrator-v3 -> identity-attempt2
```

The logical conversation is bidirectional; the evidence graph is acyclic.

## Communication contract

Every message names:

- workflow and graph revision;
- immutable sender and recipient node IDs;
- channel and message kind;
- correlation ID;
- one declared frame type and bounded property bindings;
- provenance and source-message IDs; and
- an observed time, maximum age and freshness status.

The channels are deliberately different:

- `data` carries input, grants, results and join inputs;
- `control` carries requests, denials, candidate transitions and authority
  gates; and
- `evidence` carries non-command receipts.

Direct sandbox peers may use typed data links. They may not pass control or
authority messages to one another in v1. Context escalation therefore returns
to the orchestrator even though ordinary bounded results need not.

## Container start-up policy

Each sandbox descriptor has:

- an instance and attempt number;
- a container generation;
- a policy revision fixed for that generation;
- inbound rules naming peer instance, channels and frames;
- outbound rules with the same shape; and
- a subset of the fixed analytical capability catalogue.

A direct message passes only when the sender's outbound rule and recipient's
inbound rule agree. This bilateral test prevents a single over-permissive
container from creating a route on its own. Unknown peers, frames, channels and
capabilities fail closed.

The policy is static evidence, not a network firewall implementation. A later
runtime would have to compile it into container/network enforcement and prove
that the effective configuration matches the signed plan.

## Capability boundary

The only representable v1 capabilities are:

- inspect a received typed frame;
- request one declared context frame;
- evaluate a predicate;
- emit a candidate transition; and
- record non-command evidence.

No database, HTTP, filesystem-write, subprocess, provider, Git or EMR-command
capability exists in the catalogue. Adding one would change the architecture
and authority meaning and therefore requires a separate Yuri decision.

## Fan-out, peer work and convergence

The authored-synthetic example demonstrates three complementary patterns:

1. the orchestrator fans identity-derived scope into separate availability and
   policy leaves;
2. the availability leaf passes candidates directly to a declared ranking
   leaf; and
3. the ranked candidates and separately evaluated authority constraints meet
   at an explicit join.

The join produces two outputs. An evidence summary goes to an evidence sink. A
proposal-shaped candidate goes to a terminal human-authority gate. Neither
output is a command, and the final state remains `awaiting-human-authority`.

## Relationship to EMR4

This graph could eventually describe how a practice request is decomposed into
identity, availability, policy, document, clinical-safety or audit work without
placing the whole database or conversation into any one model context.

It does not yet prove that such a runtime should be built. In particular, it
does not decide:

- which leaves need models and which should be deterministic code;
- how real container identity, signing, network isolation and expiry work;
- how token and sensitivity budgets are compiled and enforced;
- how retries preserve idempotency and evidence;
- how practice-manager approval is represented in product UX; or
- whether any leaf should ever receive an EMR command capability.

The value of this fork is narrower: those later choices now have an explicit
message, peer-policy, restart and authority grammar to argue against instead of
being hidden in an imagined “agent swarm”.
