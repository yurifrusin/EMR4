# EMR4 controlled recovery — C4 allowlisted-actuator simulator plan

Date: 2026-08-05

Status: frozen provider-free authored-synthetic plan candidate

Source HEAD: `4c3a682e6c1076d8b5cfdc6143a4a07a57d63a57`

Parents:

- `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
- `docs/emr4-model-required-bureau-gate-zero-shared-contract.md`
- `docs/emr4-model-required-bureau-c3-d3-provider-free-architecture.md`
- `docs/security/emr4-model-required-bureau-c3-d3-threat-model-delta.md`

## 1. Exact result sought

C4 implements the smallest executable-shaped descendant of the accepted C3
contract: a local, provider-free, in-memory authored-synthetic simulator for
one exact reversible service-recovery runbook. It proves that backend-owned
typed authority can reach a single-purpose handler and that success remains
unreleasable until a distinct fresh readback verifies the simulated result.

The only allowlisted forward runbook is
`restart-api-synthetic.v1`, targeting only
`isolated_authored_synthetic / service / synthetic:api-service`. Its effect is
a pure state transition in a task-created in-memory `SyntheticServiceState`
from `degraded` to `healthy`. Its exact rollback runbook is
`restore-api-synthetic-lkg.v1`, which restores the transaction snapshot if the
fresh-read postcondition is not satisfied.

This is not a product command route and not a live actuator. It starts no
process or container, changes no file, database, network, cloud, IAM,
deployment or service, and imports no production actuator code.

## 2. Closed boundary

The descendant uses only newly authored deterministic fixtures and local
in-memory state. It has:

- zero provider/model calls, prompts, costs and Access AI openings;
- zero patient, clinical, participant, practice, product-derived, protected or
  production data;
- zero mounted FastAPI, GraphQL, REST, command-bus or event-consumer route;
- zero filesystem, subprocess, shell, SQL, URL, network, socket, database,
  container, cloud, IAM, secret-store, deployment or external side effect;
- zero production, release, Pages or protected-ref authority; and
- no C5 live-development recovery authority.

`docs/branding/` and every pre-existing untracked receipt/state file remain
preserved and excluded. The provider model remains mandatory for a future
intelligent diagnosis or recovery-plan claim, but no provider is necessary or
permitted for this deterministic simulator component claim.

## 3. Frozen inputs

C4 accepts only canonical objects that have already crossed distinct trust
boundaries:

1. one C3 `RecoveryPlanCandidate` whose deterministic classification is exact
   `reversible_scoped_service_recovery`;
2. one backend `RecoveryAuthorityDecision` bound to the exact canonical plan
   hash/revision, policy version, target/current revision, earliest expiry,
   ordinary confirmation and one current `authorized_technical_operator`;
3. one immutable signed-catalog entry for the exact forward and rollback
   runbook ids, exact target kind/id, exact empty parameter schema and catalog
   digest;
4. one fresh synthetic observation set matching every plan precondition and
   the current target revision; and
5. one opaque one-use `ExecutionEvidence` reference minted by a separate
   backend authority function after all inputs above pass.

The simulator never accepts the model candidate, reviewer assertion or plan
text as execution authority. C3's `execution_authorized: false` remains true;
C4 constructs a distinct backend-owned simulator command envelope.

## 4. Closed schemas and authority objects

Implementation adds closed Draft 2020-12 schemas and canonical examples under
`orchestration/continuity/model-required-bureau-c4-allowlisted-actuator-simulator/`:

- `runbook-catalog-entry.v1` — exact ids, target, empty parameter schema,
  expected transition, rollback and deterministic catalog digest;
- `execution-evidence.v1` — opaque random reference plus server-held record
  binding plan/decision/catalog/actor/role/context/target/preconditions,
  correlation, nonce, issued/expiry and one-use state;
- `simulator-command-envelope.v1` — backend-owned exact runbook, target,
  expected revision, empty parameters, plan/decision/evidence bindings,
  correlation and idempotency hashes, and readback contract;
- `simulator-execution-receipt.v1` — bounded patient-free simulated result,
  audit correlation, before/after/readback hashes, rollback disposition and
  exact evidence label; and
- `simulator-denial-receipt.v1` — one stable reason code and sanitized bounded
  correlation without attacker-controlled prose.

Unknown properties, duplicate JSON keys, non-canonical encodings, free-form
commands, shell/SQL/path/URL/cloud/template fields and unknown parameters are
rejected before authority or state lookup.

## 5. Exact authority and evidence issuance

The provider-free authority service may mint execution evidence only when all
of the following are true at the same in-memory state revision:

- plan, decision and canonical plan hash/revision match;
- plan environment is exactly `isolated_authored_synthetic`;
- target is exactly `service / synthetic:api-service` and the expected
  revision matches current synthetic state;
- operation class, computed risk tier and required authority are exactly
  `scoped_service_recovery`, `reversible_scoped_service_recovery` and
  `ordinary_confirmation`;
- runbook and rollback ids plus catalog digest match the immutable allowlist;
- parameters are the exact empty object;
- every required observation is fresh and its digest matches;
- the authority decision is current, not expired or superseded, requires one
  reviewer, and contains one current distinct
  `authorized_technical_operator` who is not the candidate generator;
- plan, decision, reviewer, observation and catalog expiries remain current,
  with the earliest expiry becoming the evidence expiry; and
- no effective evidence already exists for the same plan revision and
  supersession key.

The returned value is an opaque random reference. The server-held record binds
the exact canonical inputs and a cryptographically random nonce. Structured
claims, reviewer ids, a plan hash or a model output cannot substitute for the
reference. Evidence is short-lived, one-use and cannot be refreshed; expiry,
amendment, supersession, role loss, target drift or observation drift requires
a complete fresh authority decision and evidence issuance.

## 6. Single-purpose simulator handler

The handler performs this fixed sequence inside one in-memory transactional
critical section:

1. return the exact stored receipt for same-key/same-fingerprint replay;
2. reject same-key/different-fingerprint or an in-progress key;
3. resolve and lock the opaque one-use evidence record;
4. reauthorize actor/role and revalidate plan, decision, catalog, expiry,
   supersession, target revision and every observation;
5. reject a consumed reference, including with a different idempotency key;
6. construct the backend-owned closed command envelope;
7. mark the evidence consumed and take an immutable state snapshot;
8. invoke only the hard-coded Python transition associated with exact runbook
   id `restart-api-synthetic.v1` — never a string interpreter or dispatcher;
9. append an immutable simulated audit record;
10. perform a separately invoked fresh read of the in-memory state rather than
    trusting the handler return;
11. release `simulated_effect_verified` only when the readback proves the exact
    expected health and revision transition; otherwise invoke only
    `restore-api-synthetic-lkg.v1`, freshly read again, and release a denial
    that distinguishes verified rollback from inconclusive rollback; and
12. store the bounded receipt under the idempotency record.

The handler registry is a code-level mapping from the exact enum-like runbook
id to one fixed callable. No dynamic import, reflection, `eval`, `exec`,
subprocess, shell, SQL, template, URL, path, generic tool or arbitrary function
name is permitted.

Evidence remains consumed after an attempted transition, whether success or
verified rollback. No failure path may re-open it. A second attempt requires a
new plan/decision/evidence sequence against current state.

## 7. Atomicity, replay and concurrency semantics

The in-memory simulator models two deliberately distinct monotone units under
one critical section. Admission atomically seals idempotency, consumes evidence
and appends an immutable attempt record; those facts never roll back. The
simulated effect unit snapshots state, applies the transition and appends its
effect audit only on verified success. If the transition or effect-audit append
fails, state and effect audit restore from the snapshot while the sealed failed
attempt remains. If postcondition readback fails after the transition, the
exact rollback runs and a second fresh read must prove restoration before
`simulated_rollback_verified` is released. An inconclusive rollback is a
terminal fail-closed result, never success.

Two concurrent requests using one evidence reference produce at most one
handler attempt. Same-key exact replay returns the stored terminal receipt.
Different-key reuse returns `EXECUTION_EVIDENCE_REPLAY`. Canonical request
fingerprints include plan/decision/catalog/evidence/actor/target/revision/
correlation/runbook/parameters and readback bindings.

## 8. Denial taxonomy

Stable denials include at least:

- `SCHEMA_REJECTED`
- `EXECUTABLE_CONTENT_REJECTED`
- `UNKNOWN_RUNBOOK`
- `UNKNOWN_PARAMETER`
- `SCOPE_EXPANSION_REJECTED`
- `STALE_OR_SUPERSEDED`
- `TARGET_REVISION_CONFLICT`
- `OBSERVATION_MISMATCH`
- `AUTHORITY_MISMATCH`
- `REVIEWER_INVALID`
- `EXECUTION_EVIDENCE_INVALID`
- `EXECUTION_EVIDENCE_REPLAY`
- `IDEMPOTENCY_CONFLICT`
- `IDEMPOTENCY_IN_PROGRESS`
- `SIMULATED_TRANSITION_FAILED`
- `SIMULATED_READBACK_FAILED_ROLLBACK_VERIFIED`
- `SIMULATED_ROLLBACK_UNVERIFIED`

Denials expose no secret, raw evidence reference, attacker-controlled text,
stack trace or ambient state.

## 9. API Spine disposition

C4 creates no mounted product or technical-control-plane endpoint. The command
envelope and handler are an isolated simulator component. A declarative
OpenAPI-shaped command contract may document the future single-purpose REST
ownership, but it must be explicitly `not_mounted` and cannot be imported by
`app.main`. GraphQL remains read-only. No event is emitted. A later real route,
database-backed evidence store, external actuator or C5 target requires a new
exact descendant.

## 10. Expected implementation ownership

After a fresh independent architecture/security veto passes this frozen plan:

- one DeepSeek V4 Flash/high worker may implement the stable, separable closed
  schemas, pure in-memory simulator and focused deterministic tests in an
  isolated descendant worktree;
- Sol owns the packet, source review, API/security reconciliation, all
  integration and acceptance, and any conceptual recovery; and
- a fresh Gemini 3.6 Flash/high Antigravity project performs the final read-only
  exact-HEAD implementation veto after deterministic checks pass.

The implementation worker may not edit `AGENTS.md`, accepted historical
evidence, provider configuration, product routers, deployment files,
`docs/branding/` or protected refs.

## 11. Acceptance matrix

- all schemas are closed, canonical examples validate and source/evidence
  hashes are bound from LF bytes;
- exact success changes only the in-memory synthetic service, consumes one
  evidence reference, appends one immutable audit record and releases success
  only after a distinct fresh read;
- same-key replay, changed-body conflict, in-progress state, different-key
  evidence replay and concurrent single-winner behavior are exact;
- tampered/unknown/expired/superseded evidence, wrong plan/decision/catalog,
  wrong actor/role, invalid reviewer separation, stale observation, target
  revision drift and multi-environment scope all produce zero simulated effect;
- shell, SQL, URL, path, cloud, template, dynamic-import, callable-name and
  unknown-parameter inputs are structurally unreachable and adversarially
  rejected;
- transition, audit, readback and rollback fault injections prove no false
  success and distinguish verified rollback from unverified rollback;
- source inspection and runtime counters prove zero filesystem, process,
  network, socket, database, container, cloud, IAM, product, provider or
  external event operations;
- no `app.main` import, route inventory or OpenAPI runtime surface changes;
- focused tests, inherited C3/Gate-zero/continuity/API-spine tests, Ruff,
  compilation, Bandit and `git diff --check` pass; and
- fresh Gemini 3.6 Flash/high returns exactly one pass on a clean unchanged
  exact candidate before Sol acceptance.

The exact evidence label is
`provider_free_authored_synthetic_allowlisted_actuator_simulation`. It does not
support `live_actuator`, `live_recovery`, `deployment`, `production` or
`release` claims.

## 12. Stop conditions

Ordinary plan refinement, implementation defects, deterministic failures and
bounded recovery do not require a user pause. Stop only if completion would
require a real target, real database, product/system credentials, provider
call, patient/product/protected data, mounted route, external effect, C5 live
action, deployment/release/Pages/protected-ref movement, or a non-inferable
change to the accepted evidence meaning.
