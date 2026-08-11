# Sol acceptance: Raisa AES-C0 architecture contract

Date: 2026-08-11

Decision: `accepted`

Result: `raisa_agent_execution_surface_containment_gate_aes_c0_architecture_pass`

## Basis

I accept AES-C0 as the exact architecture-only Agent Execution Surface contract
over source baseline `01d355f42df5981341196f3aa0caec2cccce7a2d`.

The six closed message definitions, canonical cross-bindings and 37/37 hostile
rejections mechanically preserve the selected external-broker, immutable-
generation, no-ambient-authority, independent-budget, no-fallback, external-
revocation and minimized-evidence boundaries. The API Spine remains unchanged:
GraphQL reads, events signal fresh reads and separately authorized REST/OpenAPI
commands own mutations.

The 45-test focused contract/API packet, 105-test static CI packet and 111-test
canonical fast profile pass. The evidence made no provider call, started no
runtime and accessed no patient, product or protected evidence.

## Acceptance boundary

This acceptance admits architecture and deterministic authored-synthetic
evidence only. It grants no runtime broker, container, adapter, credential,
provider, product context, database/source, tool, command, deployment,
production, release, Pages or protected-ref authority.

AES-C1 provider-free admission rehearsal is the next safe planned descendant.
Work pauses before AES-C1 only because Yuri requested a fresh task-window
handoff at this tranche boundary.
