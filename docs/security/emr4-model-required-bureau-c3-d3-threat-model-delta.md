# Threat-model delta: controlled-recovery C3 and update-supply D3

Date: 2026-08-04

Status: provider-free, non-executing architecture/schema candidate

Parent:
`docs/security/emr4-model-required-bureau-provider-free-successor-lanes-threat-model-delta.md`

## New assets and trust boundaries

The new assets are recovery-plan candidates, deterministic risk decisions,
review requirements, staged-promotion plans, last-known-good bindings and
postcondition/readback definitions. Candidate data, backend policy, reviewer
evidence, a future command handler and authoritative readback remain distinct
trust boundaries. No handler or live evidence exists in this tranche.

## Threats and controls

### A candidate assigns itself a safer risk tier

Controls: candidate risk is advisory; deterministic policy derives the tier
from closed operation, target, control/data-plane, blast-radius and
reversibility fields; the result is monotone; mismatch or an unknown value
rejects; candidate text and model output cannot satisfy authority.

### A reversible label hides a dangerous or unbounded operation

Controls: an exact rollback type, signed runbook/LKG digest, maximum blast
radius and deterministic postconditions are mandatory; unknown rollback,
multi-environment scope, database/security/data-supply work or generic
instructions cannot enter a lower tier; irreversible or unknown work is
forbidden by this contract.

### Human review becomes a rubber stamp or self-approval

Controls: backend policy fixes minimum counts and roles; reviewers are
authenticated, current, scope- and expiry-bound; required reviewers are
distinct and separated from candidate generation and execution where the tier
requires it; model, proofreader and candidate cannot review themselves.

### Plan fields become an executable side channel

Controls: closed schemas contain no command, shell, SQL, URL, path, cloud,
credential or template fields; bounded strings remain inert data and are
screened for executable tokens; authority decisions have
`execution_authorized: false`; no command route or actuator exists.

### Promotion collapses four update classes into one privileged updater

Controls: update class, future command family, canary kind, review authority
and rollback kind are cross-bound by deterministic policy; mismatches reject;
generic update is forbidden; actual endpoints remain separately closed.

### Shadow or canary evidence is mistaken for activation

Controls: stages and their evidence are distinct; shadow content is quarantined
from authoritative reads; canary scope is class-specific; neither produces an
activation receipt; source/current-target/expiry/review/LKG bindings must be
revalidated immediately before any future class-specific command.

### Review, activation or audit suffers a time-of-check/time-of-use race

Controls: the future command envelope binds immutable plan/provenance hashes,
expected target revision, actor, correlation, idempotency, review evidence and
expiry; the backend revalidates all values immediately before an atomic effect;
supersession or drift invalidates the plan.

### Activation success is claimed from a receipt rather than current truth

Controls: only fresh authoritative readback against closed postconditions may
set success; inconclusive or failed readback remains a failure; provider prose,
reviewer belief, audit append and handler receipt cannot replace readback.

### Rollback targets a stale or attacker-selected artifact

Controls: the last-known-good artifact is fixed before activation by class,
source/provenance digest and authoritative target revision; deterministic
eligibility rechecks current lifecycle, withdrawal, compatibility and policy;
a previously active but now expired or withdrawn dataset/policy is ineligible;
rollback is a separate authorized atomic command with its own expiry, audit,
idempotency and fresh readback; model output cannot rewrite the target.

### Schema evidence is inflated into runtime assurance

Controls: authored-synthetic fixtures and deterministic tests use only
`provider_free_c3_d3_architecture_and_proof`; every side-effect counter is zero;
no provider, product, importer, migration runner, actuator or deployment path
is exercised.

## Residual closed risks

These contracts do not prove reviewer identity, runtime authorization,
transactional activation, migration safety, backup restoration, real canary
isolation, immutable operational audit, provider behavior or actuator least
privilege. Provider/model/data/cost, product and technical reads, commands,
actuators, external downloads, licence acceptance, imports, migrations,
activation, cloud/IAM, deployment, production, release, Pages, protected refs
and protected evidence remain separately closed material gates.
