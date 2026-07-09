# Sprint 287 Next Block Reorientation

Date: 2026-07-09

Decision: pause the practitioner-directory GraphQL default-on track before any
deployment, production, telemetry, or global readiness work.

Preceded by Sprint 286 publication-state correction, commit
`7e2dd6e71a5ff6d5d1aadc9fa6f137e1beedb833`.

## Recommendation

The next safe block is the Bernie UI derived-state non-D5 checkpoint block:

- Sprint 288: post-D5 next-slice inventory.
- Sprint 289: checkpoint review packet.

Both should be documentation/tests-only unless Yuri separately approves a
runtime implementation step.

## Why

The GraphQL practitioner selector path has enough post-default-on evidence for
now: publication state, local backend smoke, rollback packet, and monitoring
boundary. The next GraphQL moves would be readiness, deployment, telemetry, or
broader exposure, and those require explicit approval.

The Bernie UI derived-state DAG D5 first slice is also complete and should not
expand by default. A checkpoint block can preserve its lessons without opening
D5, provider, memory, historical diary, GraphQL, external-client, or write
gates.

## Stop Conditions

Stop before any work that adds telemetry, claims deployment or production
readiness, expands GraphQL, expands D5 delivery, touches provider/memory/H15/
historical diary runtime paths, changes confirm payloads, exposes external
clients, or changes write behavior.
