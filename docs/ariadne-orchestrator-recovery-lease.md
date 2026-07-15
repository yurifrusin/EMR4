# Ariadne Orchestrator Recovery Lease

Date: 2026-07-11

A failed worker must not be able to deadlock a sprint, but the orchestrator
must not rewrite a worker closeout and present it as worker evidence.

Closeout provenance is non-transferable. A failed, missing, contradictory, or
scope-breaching worker artifact remains recorded under that worker's identity.
The orchestrator cannot repair or replace that attestation.

Implementation repair is transferable through an explicit recovery lease. The
orchestrator may adopt worker source as an untrusted candidate, amend it under
the orchestrator's own identity, run verification, and produce a separate
integration record. The record distinguishes submitted source from
orchestrator changes and preserves every worker failure or scope breach.

For low-risk documentation, focused tests, and non-runtime harness code,
deterministic tests plus ownership/diff review can close the lease. Runtime,
security-boundary, database, deployment, and release work additionally require
an independent verifier. A recovery lease cannot expand sprint scope or
silently reassign a role.

For DeepSeek Flash lanes, classify the rejection before redispatch. Mechanical
omissions may receive one bounded correction. Conceptual errors involving
taxonomy, frozen-set meaning, corpus-wide versus adjudicated populations,
acceptance semantics, provenance, or authority transfer immediately to this
lease. If a bounded correction also fails, no further same-lane Flash revision
is permitted. Cached-token volume and elapsed time are recorded as efficiency
evidence but are not themselves capability or failure verdicts.

The protected OpenAI primary orchestrator is currently GPT Sol. The stable
resource identity is `openai-primary-orchestrator`; model changes are runtime
state that must trigger context rehydration rather than resource renaming.
