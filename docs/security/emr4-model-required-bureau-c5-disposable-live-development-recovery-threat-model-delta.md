# Threat-model delta: C5 disposable live-development recovery

Date: 2026-08-05

Status: frozen plan candidate; no live action authorised

Parent:
`docs/security/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-threat-model-delta.md`

## New assets and boundaries

C5 adds one disposable loopback process, an ephemeral port, a task-private
directory, a provider-bound technical frame set, a model diagnosis candidate,
human approval evidence, a local one-use execution capability, real process-
lifecycle effects and cleanup evidence. The provider cell, deterministic
proofreader, authority store, controller, actuator, child process, readback
observer and cleanup verifier are distinct principals.

The target contains no PHI, product data, database, EMR4 import, cloud control,
credential or ordinary service. The provider call and local process action are
separate trust boundaries and share no credential.

## Threats and controls

### A disposable target is confused with an EMR4 or ordinary service

Controls: exact environment and target constants; task-created artifact and
nonce; loopback-only bind; no `app` import; no product settings; no service
discovery; exact controller-owned child handle; source and runtime assertions
that refuse any other target; claim label excludes product recovery.

### Model or prompt content becomes an executable process command

Controls: the model schema has no command, executable, path, URL, port, PID,
module, callable or environment field. The fixed runbook id maps to one code-
level callable and one constant argument-vector builder. No shell, string
interpolation, reflection, dynamic import or generic runner is reachable.

### Provider receives credentials or sensitive runtime detail

Controls: the admitted frame contains opaque target and observation ids, enums,
digests and bounded timestamps only. It excludes token, nonce, PID, port,
filesystem path, credential, environment, stdout/stderr and product data. Raw
provider content and thoughts are not persisted.

### Existing Bernie provider identity becomes actuator authority

Controls: the provider identity can call only the accepted development model
through Access AI. The actuator receives a separate local one-use capability,
no ADC and a minimal credential-free child environment. C5 explicitly does not
prove the future production technical-control-plane identity boundary.

### Standing programme authority is inflated into generic execution authority

Controls: deterministic approval issuance binds Yuri's recorded human decision
to one committed C5 plan hash, exact target, fault, runbook, rollback, provider/
cost envelope, expiry and one rehearsal. Any changed field rejects and no
approval renewal or transfer is possible.

### PID reuse or handle confusion terminates another process

Controls: the controller retains the exact child-process handle, launch nonce,
generation and artifact digest; it never accepts caller-supplied PID and never
enumerates or discovers processes. Termination and cleanup operate only through
the owned handle and fail closed if ownership cannot be proved.

### Ephemeral port race reaches or replaces another listener

Controls: the controller owns the socket allocation handoff, binds only
`127.0.0.1`, carries an opaque target nonce in the exact health response, and
binds port, generation and nonce into observations and evidence. Address-in-use,
nonce mismatch or unexpected listener is a terminal denial, never a retry
against another port after provider admission.

### Child process inherits cloud credentials or ambient authority

Controls: isolated Python mode, exact executable and module hashes, minimal
explicit environment, no provider variables, no inherited stdin, no shell, no
admin request and no product configuration. Runtime tests inspect the child
environment contract without exposing secret values.

### Pre-fault or post-fault evidence is stale or fabricated

Controls: independent process and HTTP observers, exact source/revision/time
bindings, short expiry, monotone generation, fresh connection-refused proof and
frame-set digest. Any process/HTTP disagreement, stale observation or changed
target stops before the provider call or actuator.

### Provider invents a cause, runbook or success

Controls: every hypothesis cites admitted observation ids; only the exact
stopped-process diagnosis and start runbook are eligible; missing evidence is
explicit; proofreader rejects unsupported causation, executable prose and any
success claim. Deterministic fresh readback alone establishes recovery.

### Provider retry silently changes cost or request meaning

Controls: one primary and at most one proofreader-ticketed correction, distinct
hash-bound ledgers, USD 0.50 ceiling, exact 1,024/2,048 positive-reasoning
envelope, no unchanged retry and no fallback. Every ledger is consumed or
closed during cleanup.

### Replay, concurrency or authority mutation launches twice

Controls: one shared store and critical section own authority, evidence,
idempotency, attempt sequence and launch state. Evidence is opaque, expiring
and one-use. Same-key exact replay returns the stored receipt; conflicts and
different-key reuse reject; authority is locked across launch, audit and fresh
readback; cross-runtime adversarial tests require one winner.

### Launch or readback failure leaves an uncontrolled process

Controls: any post-launch failure invokes only the exact stop rollback through
the owned handle, followed by fresh process-absence and connection-refused
checks. Verified and inconclusive rollback are distinct terminal states. No
failure reopens evidence.

### Cleanup deletes unrelated files or leaves residue

Controls: the task directory is created under a newly generated validated
temporary root, its resolved absolute path and ownership marker are checked
before removal, and no recursive removal accepts a caller path or workspace
root. Cleanup targets only the exact process handle and directory and verifies
process, port, directory, ledger and capability absence. Cleanup is idempotent
for the exact run only.

### Local live evidence is exaggerated into deployment or production assurance

Controls: the exact evidence label is
`occupied_authored_synthetic_disposable_live_development_recovery`; receipts
enumerate the provider and loopback process effects and prove all other effect
counters zero. Product, ordinary-service, database, container, deployment,
production, release, sovereignty and autonomous-recovery claims are forbidden.

## Residual closed risks

C5 does not prove product service diagnosis, persistent technical telemetry,
database-backed execution evidence, cross-host locking, container/VM/cloud
isolation, real service-manager permissions, production identity separation,
operational rollback, incident response, deployment, release, patient safety or
clinical continuity. Those require separate exact descendants.

Patient/product/protected data, real practice databases, ordinary services,
cloud/IAM mutation, deployment, production, release, Pages, protected evidence
and protected refs remain closed. The Context Fabric remains a separate
unimplemented programme direction.
