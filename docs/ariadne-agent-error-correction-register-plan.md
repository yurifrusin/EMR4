# Ariadne agent error and correction register plan

Date: 2026-08-03

Status: authorised and frozen

## Objective

Create one durable, schema-validated register of evidence-backed agent,
transport, harness, repository and operator incidents so recurring workflow
failures can be detected and corrected. The initial seed is deliberately
bounded to known incidents with preserved repository evidence through
2026-08-03; it is not an exhaustive reconstruction of every historical attempt.

## Classification boundary

An incident records its origin separately from its category and role. A model
claim error, command-scope breach or invalid output envelope is
`agent_behavior`; a timed-out provider transport with no worker closeout is
`transport`. Harness defects, repository defects and operator mistakes have
their own origins and must not be silently attributed to an agent.

Every row records an immutable attempt identity, expected invariant, direct
observation, detection method, exact preserved evidence, a closed candidate
state, workflow disposition, correction and a normalized recurrence signature.
Split rows may describe distinct invariant breaches in one attempt, but every
row in that attempt must cross-reference every peer. Historical failures remain
immutable evidence even after a correction passes. Version 1 admits observation
only; a causal claim needs a future schema with a separate causal evidence
contract.

## Pattern use

The deterministic report groups incidents by the exact composite of origin,
category, role, resource and normalized recurrence signature. A composite is
called recurring only when it appears at least twice. Counts are operational signals for improving
packets, wrappers and gates; they do not prove a model, provider or role is the
cause and must not be used as a comparative model-quality score.

## Privacy and authority

The register contains no raw prompts, secrets, credentials, patient, clinical,
document or product-derived values. Evidence paths must be repository-relative,
must exist, and may not enter `docs/branding/`. The tranche changes no product
runtime, API Spine, identity, provider, cloud, deployment, production, release,
protected evidence or protected Git ref.

## Deterministic acceptance

- The JSON register validates against the closed Draft 2020-12 schema.
- Incident IDs are unique, ordered and internally referentially complete.
- Every evidence and correction path exists inside the repository.
- Origin/category consistency fails closed, including transport timeout rows.
- Pattern output is canonical UTF-8 LF JSON and byte-identical across repeats.
- Mutated duplicates, missing evidence, branding paths, invalid classification,
  unknown fields and forbidden sensitive/raw-prompt keys are rejected.
- The bounded seed includes the preserved verifier and transport incidents only;
  no unsupported causal claim or unpreserved anecdote is admitted.

## Next work

After closeout and Pushover notification, resume the already authorised pair:
the route-intercepted provider-free Diary browser rehearsal and the
architecture-only Davida proposal-to-confirm boundary.
