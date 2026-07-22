# Ariadne Synaptic Event Router - Threat Model Delta

Date: 2026-07-22

Scope: repository-local, authored-synthetic, non-executing protocol only

## Boundary

The protocol accepts one checked-in JSON document and emits deterministic
in-memory validation, routing, trace and dry-run manifest projections. It has no
network, database, product, model, container, subprocess, credential or command
adapter. All represented principals, practices, resources, events, leases,
mailboxes and checkpoints are authored-synthetic inert identifiers.

The event is a non-authoritative committed-change signal. The steering notice
is a staleness cue. The fresh-read grant is a non-executing permission
descriptor. None is data truth or command authority.

## Threats and controls

| Threat | Protocol control |
|---|---|
| Cross-practice steering | Exact practice and principal equality across policy, event, lease, mailbox, grant and reconciliation trace; mismatch is suppressed. |
| Ambient or unilateral delivery | Exact event/frame rule and node lease must both permit the mapping; default decision is deny. |
| Scope amplification | Same-generation lease changes may only narrow; any expansion requires a later container generation, higher policy revision and exact restart lineage. |
| Stale-node overwrite | Only the current lease/container generation may receive or complete; superseded attempts and stale completions fail closed. |
| Replay or duplicate visible effect | Stable event identity plus lease/revision/generation/frame deduplication coordinate; duplicate routes are suppressed. |
| Revision rollback | Event aggregate revision must exceed both the lease minimum and the mailbox checkpoint. |
| Payload smuggling | Schema allowlists plus recursive forbidden-key/value checks reject free text, clinical content, direct identifiers, prompts, secrets, returned rows and command payloads. |
| Sensitivity escalation | Ordered sensitivity ceiling is enforced before routing; grants cannot broaden resource or sensitivity scope. |
| Fresh-read grant laundering | Exact practice/principal/role/action/resource/frame/event/revision linkage, expiry and `execution_enabled: false` are required. No returned data is representable. |
| Event-to-command escalation | Allowed states and actions exclude confirm/commit/dispatch/execute/write; forbidden execution keys and values fail validation. |
| Manifest execution | Compiled manifests require `dry_run: true`, `execution_enabled: false` and default deny; endpoint, DSN, topic, command and actuator fields are forbidden. |
| Hidden runtime coupling | Static AST tests forbid database, network, product, model, container and subprocess imports; CLI commands only read and render. |
| Evidence privacy leak | Routing evidence retains only authored-synthetic typed coordinates and reason codes; runtime retention design remains out of scope. |

## Residual limitations

This tranche cannot prove delivery reliability, authentication, operational
authorization, concurrency safety, durable deduplication, backpressure,
dead-letter handling, retention, RLS, encryption or incident recovery because
it starts no runtime and touches no real data. Those are future threat-model
decisions, not implied capabilities.

## Closed gates

PostgreSQL/outbox/feed connectivity, product APIs, operational registries,
mailbox persistence, workers, transports, models, containers, commands, PII,
protected evidence, historical Diary material, new event families, Stage 3B,
production, deployment, release and autonomous action remain closed.
