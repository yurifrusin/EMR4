# Sol Extra High architectural review: model-required Bureau Gate zero

Date: 2026-08-04

Decision: `pass_for_fresh_independent_veto`

Candidate parent: `50dab5d66fc1401344fc47d7aa5ebd336b75e960`

## Findings

No blocking architectural or API Spine finding remains in the candidate.

During review, three fail-closed improvements were applied before this decision:

1. raw model-candidate labels are fixed to `untrusted_model`, proofreader-only
   visibility and candidate-only authority ceilings;
2. context fields are fixed to data-only authority and cannot originate as
   proof, backend-authority or actuator integrity; and
3. each candidate kind is mechanically tied to Bernie, Rayleen, Davida or
   controlled-recovery/update rather than merely appearing in one global enum.

The source and sink registries are also checked as exact associations, so a
schema-shaped swap of integrity, reader, ceiling or material-gate semantics
fails deterministic acceptance.

## Boundary classification

This is architecture, closed JSON Schema prototypes and provider-free
deterministic evidence. It creates no application route, resolver, provider
adapter, broker, cell, database object, worker, command handler or actuator.

## API Spine decision

- GraphQL remains named, practice-scoped read/context only and cannot invoke a
  provider or carry a command.
- REST/OpenAPI owns provider/external invocation and every state-changing or
  auditable command.
- Events remain hints that require a fresh authorized read.
- Manifests remain declarative inputs enforced by typed runtime code.
- Any future backend-owned command must bind exact command type, practice,
  actor, correlation, idempotency, target/revision, context/freshness, expiry,
  warnings, blocks, risk tier, confirmation/dual-review, audit and readback.
- Any future provider invocation must use the Access AI command boundary and
  bind capability, method, actor, practice, entitlement, context, data class,
  provider, model, region, cost, correlation and audit policy.

Both future boundaries remain explicitly closed.

## Containment decision

The candidate faithfully converts the accepted Gate −1 selections into one
versioned contract:

- five-dimensional, monotone label/capability flow with field- and sink-specific
  endorsement/declassification and typed denial receipts; and
- one fresh broker-mediated cell per attempt with one input, one output, no
  ambient authority bridge, exact byte/time/CPU/memory/process/descriptor quotas,
  hostile-byte parsing, kill conditions, teardown and zero-residue evidence.

The broker remains bounded transport, not an authority plane. Cognitive, proof,
authority and execution/readback principals remain distinct. Provider outage is
explicit and cannot be relabelled as equivalent agentic success.

## Deterministic evidence

- Gate-zero focused suite: 72 passed.
- Gate-zero plus API Spine suite: 101 passed.
- Ruff: passed.
- Six closed Draft 2020-12 schemas and five canonical authored-synthetic examples
  validate.
- Hostile duplicate-key, invalid-UTF-8, trailing-byte and over-budget cases deny.
- Stale, reader, integrity and authority-ceiling sink violations deny with stable
  typed reasons.
- Recorded candidate-runtime side effects are all zero.

## Claim and authority boundary

This review makes the candidate eligible for the required fresh independent
veto. It is not final Gate-zero acceptance. It records no product provider call,
patient/product data, runtime wiring, product command/write, actuator,
deployment, production, release, Pages rebuild or protected-ref movement.
`docs/branding/` and protected evidence remain excluded.
