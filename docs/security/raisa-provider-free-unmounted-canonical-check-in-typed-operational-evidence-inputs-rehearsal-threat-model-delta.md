# Canonical check-in typed operational-evidence inputs threat-model delta

Date: 2026-08-23

Timestamp: 2026-08-23T11:06:45.2591340+10:00 (Australia/Brisbane)

Status: `frozen_provider_free_unmounted_input_model_delta`

Operation:
`raisa-provider-free-unmounted-canonical-check-in-typed-operational-evidence-inputs-rehearsal`

## Boundary

One pure unmounted module converts an explicitly supplied authored-reference
object into immutable role, rotation/custody and deny-only break-glass evidence
inputs. It does not retrieve, authenticate or evaluate an external artifact
and has no product, secret, environment, database, route, deployment or
protected authority.

## Threats and controls

### Boolean authority substitution

Risk: a caller supplies `verified: true`, `attested: true` or another Boolean
and the repository mistakes it for independent operational evidence.

Control: the closed schema contains no Boolean field and recursively rejects
every Boolean before ordinary shape validation. Role observations use bounded
categorical readbacks bound to an evidence artifact and verifier reference.

### Shape validation becomes an operational claim

Risk: successful normalization is described as a proved role, current
rotation, safe custody, inactive break glass or satisfied admission gate.

Control: success is only `evidence_inputs_normalized`. Hostile but well-typed
observations and bindings remain representable. There is no `satisfied`,
`verified`, `admitted` or command field or method.

### Secret content enters evidence input

Risk: a readback embeds a password, token, private key, database URL,
secret-material digest, provider endpoint or resolution result.

Control: exact field sets exclude those values; the accepted recursive
secret-field aliases deny before shape validation. Artifact SHA-256 denotes
the evidence artifact only.

### Abbreviated or malformed immutable binding

Risk: a short Git abbreviation or malformed artifact digest gives weak
traceability.

Control: every authority object is exactly forty lowercase hexadecimal
characters and every evidence digest is exactly sixty-four. Resolution and
cross-binding are deliberately deferred to the evaluator; syntax alone makes
no truth claim.

### Input normalizer silently performs evaluation

Risk: the module compares against a manifest, checks current time, rejects an
owner observation or engaged break glass, or silently accepts a self-verifier.

Control: the typed layer performs only shape, syntax and within-record temporal
ordering. Tests require evaluator-hostile but structurally valid cases to
normalize unchanged. No clock/current-time source is imported.

### Ambient access or mount

Risk: evidence handling reads environment/configuration, follows a reference,
loads YAML, connects to a provider/database or enters a route.

Control: the public function accepts one in-memory object. Source/import guards
forbid filesystem, environment, settings, credential, YAML, network, database,
route and admission dependencies. Product source has no caller in this
tranche.

### Harness investigation resumes instead of product work

Risk: an incompatible DeepSeek worker shape triggers another runner/broker
qualification sequence.

Control: the accepted runner is not compatible unchanged, so the lane is
declined. No native session, provider call, new runner, broker/guard mutation,
fallback or diagnostic sequel is permitted.

## Explicitly closed

No operational manifest or fact; no external verifier selection; no evaluator
or admission seam; no secret/reference resolution; no `.env`, process
environment, configuration, credential store, database, Docker, route, API,
GraphQL, OpenAPI or client; no ordinary-practice enablement, feature flag,
allowlist, command, generic-status `Arrived`, grammar or waiting-area change;
no product, patient, appointment, clinical, historical or protected data; no
production, deployment, release, Pages or protected-ref movement.
