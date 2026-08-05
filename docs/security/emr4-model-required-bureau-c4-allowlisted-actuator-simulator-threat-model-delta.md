# Threat-model delta: C4 allowlisted-actuator simulator

Date: 2026-08-05

Status: frozen provider-free authored-synthetic plan candidate

Parent:
`docs/security/emr4-model-required-bureau-c3-d3-threat-model-delta.md`

## New assets and trust boundaries

C4 adds an immutable synthetic runbook catalog entry, server-held one-use
execution evidence, a backend-owned simulator command envelope, an in-memory
synthetic service state, immutable simulated audit, and fresh-readback receipt.
Plan candidate, authority decision, reviewer identity, evidence issuer,
single-purpose handler, state store and readback verifier are separate
principals even though the test implementation is one local process.

No real actuator, process manager, database, filesystem, network, cloud,
credential or product principal exists in this descendant.

## Threats and controls

### Candidate or reviewer becomes command authority

Controls: the C3 candidate and decision retain `execution_authorized: false`.
Only the deterministic issuer can create a distinct opaque evidence record and
only after exact plan, policy, catalog, actor, reviewer, scope, freshness and
target revalidation. Model text, plan hashes and reviewer assertions cannot be
submitted as evidence.

### Runbook id becomes a generic command injection surface

Controls: one exact runbook id maps in code to one fixed pure callable. Closed
schemas contain no shell, SQL, URL, path, cloud, template, module, executable or
callable-name field. No interpolation, reflection, dynamic import, `eval`,
`exec`, subprocess, socket or generic tool dispatcher exists.

### Empty parameters are widened after review

Controls: the catalog and command schemas require the exact empty object with
`additionalProperties: false`; the envelope fingerprint covers canonical
parameters and catalog digest; any unknown parameter or schema drift rejects
before evidence resolution.

### Scope expansion reaches a live or broader target

Controls: environment, target kind/id, revision, operation class and blast
radius are constants for one isolated synthetic service. Multi-environment,
database, security, data-supply, production and unknown targets are rejected.
The implementation has no ambient capability with which to reach them.

### Stale review or evidence survives plan/state drift

Controls: issuer and handler both bind and revalidate canonical plan hash and
revision, decision/policy/catalog versions, target revision, observation
digests, reviewer role, supersession and earliest expiry. Evidence cannot be
renewed or patched; any drift requires a complete new chain.

### Replay or concurrency produces two effects

Controls: opaque evidence is one-use, server-held and locked in the same
critical section as idempotency and state. Same-key exact replay returns the
stored receipt, changed fingerprints conflict, different-key reuse rejects and
concurrent requests admit at most one handler attempt.

### Handler receipt is mistaken for success

Controls: the transition return is non-authoritative. A distinct fresh state
read must match exact expected health and revision before success releases.
Fault injection proves a handler return, audit record or consumed evidence
cannot stand in for readback.

### Rollback failure is hidden

Controls: failed postcondition invokes only the exact bound rollback and a
second fresh read. Verified restoration and unverified rollback have distinct
terminal receipts. Neither is success; unverified rollback is incident-locked
and cannot reuse evidence.

### Transaction failure silently reopens evidence

Controls: the attempt record is sealed before handler invocation. State/audit
may restore from the immutable snapshot, but evidence consumption is monotone
for any admitted attempt. Retrying requires a fresh authority chain.

### Simulator evidence is inflated into live-actuator assurance

Controls: the evidence label is exactly
`provider_free_authored_synthetic_allowlisted_actuator_simulation`; zero-effect
counters and source checks prove no external capability. Claims of live
recovery, real database, deployment, production or release are forbidden.

## Residual closed risks

C4 does not prove provider diagnosis, real reviewer identity infrastructure,
database-backed one-use evidence, cross-process locking, durable audit, real
runbook catalog signing, actual service-manager isolation, OS/container/cloud
least privilege, live rollback, operational incident response or production
readback. A mounted command route, external actuator or C5 live development
target is a separate exact material descendant.

Provider calls, patient/product/protected data, real credentials, shell/SQL/
cloud/IAM, real database, external effect, deployment, production, release,
Pages and protected refs/evidence remain closed.
