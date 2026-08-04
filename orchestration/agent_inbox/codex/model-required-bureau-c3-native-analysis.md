# C3 controlled-recovery risk and authority analysis

Date: 2026-08-04

Status: bounded advisory only; provider-free, non-executing and non-accepting

Source branch: `codex/ariadne-bernie-davida-parallel-seam`

Source HEAD: `3008cdb4d7b5801c45024f7361fb4294aa76fc48`

Decision owner: Sol; this analysis grants no implementation, acceptance,
provider, product-data, command, actuator, deployment, release or protected-ref
authority.

## Rehydration and source boundary

This lane is bound to the passed pre-dispatch orchestrator receipt
`orchestration/agent_inbox/codex/model-required-bureau-c3-d3-predispatch-receipt.json`.
Its five non-empty sources were independently restored for this analysis:

- `live_handover_current_baton`: `AGENTS.md`, whose exact next baton is the
  provider-free, non-executing C3/D3 architecture tranche;
- `current_authority_allocation`: Sol retains architecture and acceptance;
  this worker owns only this advisory artifact;
- `active_plan_and_acceptance`: the controlled-recovery development plan,
  parent Bureau architecture, Gate-zero contract, accepted successor-lane
  design and their three relevant threat-model deltas;
- `protected_evidence_boundaries`: no protected evidence, historical PHI,
  local data, `docs/branding/`, patient/product data, provider call, live read,
  command/write, shell/SQL/cloud/IAM, actuator, deployment or release surface;
  and
- `git_refs_and_worktree`: task HEAD `3008cdb4...`; local/origin `master` and
  `handoff/current` remain protected at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The EMR4 API Steward sources were also read. The applicable rule is the mixed
API Spine: named scoped reads only in GraphQL, provider and state-changing work
only through separately opened REST/OpenAPI commands, events as hints rather
than authority, and manifests as declarative inputs enforced by typed code.

## Findings, ordered by severity

### Critical — operation class and authority tier must be separate fields

The model may propose an operation and a risk label, but deterministic policy
must independently derive both an `operation_class` and a
`required_authority_tier`. A single model-authored `risk_tier` would permit
semantic downgrades: a database restore described as a “restart”, a failover
described as “reversible”, or a reference-data activation described as a
“refresh”.

Use this closed C3 operation-class order. If more than one class matches, select
the most restrictive. Missing, contradictory or unrecognised classification
inputs resolve to `forbidden_autonomous_action`, never to a lower tier.

| C3 operation class | Deterministic predicates | Gate-zero authority tier | Minimum authority evidence | C3 effect |
|---|---|---|---|---|
| `observe_explain_only` | No change, command, external call, reservation, lock, active-version switch or persistent-state effect | `observe_only` | Current authorized operator may view a proofread candidate | None |
| `reversible_scoped_service_recovery` | Exact signed allowlisted runbook; one bounded non-data service target; verified rollback; no database, security, data-supply, deployment or traffic-primary change; blast radius within policy | `ordinary_confirmation` | One current authenticated principal with `recovery.execute.scoped_reversible` over the exact environment and target | None in C3; future command remains closed |
| `human_approved_rollback_or_failover` | Changes active version, routing, primary/standby role or last-known-good selection; exact maintenance window and reverse path; no database/security/data-supply mutation | `maintenance_release_authority` | One current authenticated maintenance/release principal bound to the exact plan hash, environment, target and expiry | None in C3; future command remains closed |
| `dual_reviewed_database_security_or_data_supply` | Any database/schema/restore/data mutation, security control/key/identity/policy change, or reference/policy data import or activation | `dual_review` | Two distinct current authorized humans; one operation-domain owner and one maintenance/release authority; neither is the actuator principal | None in C3; future command remains closed |
| `forbidden_autonomous_action` | Unknown or unsigned runbook; generic shell/SQL/code/tool/URL; unbounded, cross-environment, irreversible or unverifiable effect; missing rollback/readback; secret/PHI/protected-data access; safety/audit bypass; or any explicitly closed surface | `forbidden` | No approval can cure the plan under this contract; a new material gate and contract are required | Deny |

`manager_confirmation` remains a valid Gate-zero authority tier but is not a
C3 shortcut. A future environment policy may raise a scoped recovery from
`ordinary_confirmation` to `manager_confirmation`; it must never lower the
table's minimum. A dual-review operation should additionally require that at
least one of the two reviewers holds the maintenance/release capability. This
does not collapse `dual_review` into a single release approval.

Foundational preconfigured infrastructure safety, such as platform liveness or
transaction rollback, is outside this taxonomy only while it remains the
already-authorized deterministic safeguard described by the parent
architecture. A model-generated plan cannot reclassify itself as foundational
automation.

### Critical — C3 must end at an admitted, non-executing plan

The C2 diagnosis, C3 recovery plan, authority decision and future command must
remain four different objects owned by different principals:

1. `TechnicalDiagnosisCandidate`: proofread, evidence-bound and read-only;
2. `RecoveryPlanCandidate`: untrusted model candidate, authority ceiling
   `recovery_plan_candidate`;
3. `AdmittedRecoveryPlan`: deterministic proof and policy classification,
   still without effect authority; and
4. a future backend-owned command envelope, created only after a separately
   opened actuator gate and current authority evidence.

The C3 schema must not contain shell, SQL, code, URL, callback, executable text,
provider-supplied command, generic `execute_runbook`, approval claim, command
token or success field. Runbook parameters must be closed typed values whose
names, types, ranges and target meanings come from the exact signed catalog.
Free-form operator or model prose cannot become a parameter.

An admitted plan is not an authorized command. A reviewer-approved plan is not
proof of execution. An execution receipt is not proof of the postcondition.
Only the separately authorised handler plus deterministic readback could
support a later success claim.

### High — risk derivation must be monotone and evidence-bound

The proof plane should derive the operation class from signed runbook metadata,
not from candidate prose. At minimum the derivation inputs are:

- exact runbook id, version, manifest digest and signature decision;
- operation family and target class;
- environment id/class and current target revision;
- whether persistent data, schema, security, identity, routing, primary role,
  active version, reference content or policy content changes;
- reversibility class and validated rollback/runbook reference;
- maximum target count, scope and downtime budget;
- precondition and postcondition evidence kinds; and
- required capability and separation-of-duties policy version.

Every item must be grounded in the fresh C1 `TechnicalAnatomyFrame`, signed
runbook catalog or deterministic policy registry. The join is conservative:
the earliest expiry wins, stale input makes the plan stale, and the highest
operation risk / strongest authority requirement wins. Endorsement cannot erase
provenance, refresh evidence or raise the authority ceiling.

### High — plan amendment, freshness and supersession invalidate authority

All authority evidence must bind a canonical `plan_sha256` covering the exact
plan revision, context and anatomy hashes, diagnosis id, environment, target,
runbook version/digest, parameter values, operation class, blast radius,
rollback, preconditions, postconditions and expiry.

The effective plan expiry is the earliest of:

- anatomy/frame expiry;
- any cited observation expiry;
- signed runbook/catalog or policy expiry;
- plan expiry;
- confirmation/review expiry; and
- future one-use command evidence expiry.

Changing any bound field creates a new plan revision and invalidates all prior
review evidence. Reauthorization, review revocation, target-revision drift,
policy change, supersession or timeout returns the plan to denial/pending; it
must not “refresh” in place. Immediately before any future command, the backend
must reauthorize the actor, reread current target state, re-evaluate policy,
recheck the exact revision and all preconditions, and recheck every review.

### High — reviewer separation must be explicit and mechanically testable

The model, cognitive cell, provider broker, proofreader, source collector,
automated test and actuator can never satisfy a human review. Each review must
contain a backend-authenticated principal, role/capability, environment and
target scope, decision, plan hash, issued time, expiry, revocation state and
correlation id.

For `dual_review`:

- reviewer ids must differ;
- both must be current and independently authorized for the exact target;
- one must hold the applicable database/security/data-supply ownership
  capability and one the maintenance/release capability;
- neither may be the actuator service principal;
- a delegated, copied, replayed, self-issued, expired or superseded review is
  invalid; and
- any plan change or reviewer revocation discards the whole review set.

One human may request and confirm a scoped reversible service operation only if
current policy expressly permits that same-person ordinary confirmation. This
exception must not flow into rollback/failover or dual-review classes.
Break-glass or emergency authority is absent from C3 and cannot be inferred.

### High — rollback is a separately typed policy, not prose

Every action-bearing plan requires a closed `rollback_contract` with exact
last-known-good or rollback runbook identity, version/digest, eligibility
preconditions, trigger reason codes, maximum rollback scope, verification
postconditions and authority mode. The authority mode must be one of:

- `same_atomic_handler_contract` for a deterministic compensating action
  wholly inside an exact future command;
- `preauthorized_same_plan` only when the same plan hash, risk tier and review
  evidence explicitly cover the rollback; or
- `fresh_authority_required`.

Missing or ambiguous rollback posture is a block. Postcondition failure does
not authorize an improvised rollback and does not prove rollback success.

### High — idempotency must bind effect identity and partial outcomes

The model must not mint the effective idempotency key. The admitted plan should
declare an `idempotency_contract`; a future backend authority service derives
or assigns the effective key and binds it to:

- command family, environment and exact target;
- admitted plan id/revision/hash;
- runbook id/version/digest and canonical parameter hash;
- expected target revision; and
- actor/authority decision and correlation id.

Same key plus a different binding is denied. Same key plus the same binding
returns the durable prior terminal receipt and performs no second effect.
In-flight, timed-out or partial outcomes remain `inconclusive` until durable
handler state and fresh readback resolve them; they must not be retried as a new
effect merely because a client lost the response.

### High — audit and readback must be independent of candidate claims

The audit contract should predeclare typed append-only events for plan received,
proof denied/admitted, risk classified, review issued/revoked/expired,
authorization allowed/denied, future command accepted/blocked, attempt started,
effect returned, readback passed/failed/inconclusive and rollback considered/
attempted/read back. Events carry sanitized ids, plan hash, policy version,
environment/target, actor/reviewer principal ids, correlation and idempotency
keys, state transition and closed reason codes. They do not retain raw provider
bytes, unrestricted logs, credentials, secrets, PHI or executable text.

A future readback contract must name exact postcondition ids, fresh source
wrappers, comparison rules, deadline and failure disposition. The readback
principal must be distinct from the cognitive cell and actuator, and its values
must use the C1 provenance vocabulary. Events may announce that a readback is
available, but they cannot substitute for the fresh authorized read. No state
becomes `succeeded` from model prose, handler return code or event payload.

### Moderate — API Spine mapping must remain deliberately asymmetric

- A future GraphQL technical-control query may expose named, scoped, sanitized
  C1 observations and plan/readback status only. It cannot invoke a provider,
  accept approval, create a plan, execute a runbook or expose raw logs/secrets.
- Any future model-assisted plan formation is an Access AI backend command and
  must bind capability, method, actor, environment/practice scope, entitlement,
  context hash, data class, provider/model/region/cost and audit policy. C3
  opens none of those bindings.
- Any future effect is a single-purpose REST/OpenAPI command. Do not introduce
  a generic `POST /runbooks/{id}/execute` tunnel. Separate operation families
  and their least-privilege handlers must have typed request/result schemas.
- A technical command must carry an explicit `environment_scope` and an
  explicit `practice_scope` binding. When no practice is involved, use a closed
  backend-defined control-plane sentinel rather than omitting or accepting an
  arbitrary nullable scope.
- Events are committed hints/audit signals only. They may trigger a fresh
  authorized read or a new plan attempt, never approval, command authority or a
  success transition.
- YAML may declare signed runbook metadata, closed parameter schemas, risk
  policy, capability requirements and rollback hints. Typed backend code must
  validate and enforce them; YAML is not an executable rules engine.

The future command envelope must preserve the Gate-zero fields: exact command
type, actor, scope, correlation and idempotency keys, target and expected
revision, context/freshness bindings, expiry, warnings/blocks, risk tier,
confirmation/dual-review evidence, audit and readback contracts. C3 should
prototype plan/authority metadata only; it must not publish a runtime route.

### Moderate — evidence and denial labels must prevent claim inflation

C3 may claim only provider-free architecture/schema/policy behavior. Its
examples may classify authored-synthetic plans and demonstrate denials, but
cannot claim an occupied model, live technical observer, approval workflow,
actuator, database operation, failover, rollback, deployment or production
result.

Recommended closed denial codes are:

`SCHEMA_REJECTED`, `CROSS_ENVIRONMENT_REFERENCE`, `STALE_ANATOMY_VERSION`,
`CONTEXT_EXPIRED`, `UNBOUND_EVIDENCE`, `UNKNOWN_OR_UNSIGNED_RUNBOOK`,
`UNKNOWN_PARAMETER`, `RISK_CLASSIFICATION_AMBIGUOUS`,
`AUTHORITY_TIER_DOWNGRADE`, `FORBIDDEN_OPERATION_FAMILY`,
`BLAST_RADIUS_UNBOUNDED`, `ROLLBACK_UNPROVEN`,
`PRECONDITION_UNSATISFIED`, `POSTCONDITION_UNVERIFIABLE`,
`PLAN_EXPIRED`, `PLAN_SUPERSEDED`, `REVIEW_NOT_AUTHORIZED`,
`REVIEWER_NOT_DISTINCT`, `REVIEW_EXPIRED`,
`IDEMPOTENCY_BINDING_MISMATCH`, `COMMAND_GATE_CLOSED` and
`ACTUATOR_GATE_CLOSED`.

## Recommended closed schema model

Use three C3 objects. Do not merge their principals or fields.

### `RecoveryPlanCandidate.v1` — untrusted model output

Required closed fields:

- `schema_version`, `candidate_id`, `attempt_id`, `cell_generation_id`;
- `anatomy_frame_id`, `anatomy_version`, `source_context_sha256` and
  `diagnosis_candidate_id`;
- `environment_ref`, `target_ref`, `runbook_ref` and closed typed
  `parameter_bindings`;
- `precondition_evidence_refs`, `expected_effect_code`,
  `max_blast_radius_claim`, `rollback_ref` and `postcondition_refs`;
- `operator_explanation` as bounded data-only prose; and
- constant `authority_ceiling: recovery_plan_candidate`.

It must not contain risk-policy decisions, reviewers, approvals, effective
idempotency keys, audit decisions, command envelopes, executable strings or
success/rollback-success claims.

### `AdmittedRecoveryPlan.v1` — deterministic proof-plane output

Required closed fields:

- `plan_id`, `plan_revision`, canonical `plan_sha256`, candidate and proof
  evidence digests;
- exact anatomy/diagnosis/environment/target/runbook/parameter bindings;
- deterministic `operation_class`, `required_authority_tier`, policy version
  and classification reason codes;
- exact `preconditions`, `expected_effect`, `maximum_blast_radius`,
  `rollback_contract`, `expires_at`, `idempotency_contract`, `audit_contract`
  and `postcondition_readback_contract`;
- `warnings`, `blocks`, proofreader principal/version and admitted time; and
- constant `execution_authorized: false` and
  `actuator_gate: closed` for this tranche.

### `RecoveryAuthorityRequirement.v1` — backend policy output

Required closed fields:

- `authority_requirement_id`, `plan_id`, `plan_revision`, `plan_sha256` and
  policy version;
- required tier, capabilities, reviewer count, role composition,
  distinctness rules, separation from actuator and any maintenance window;
- issue/expiry/revocation conditions and reauthorization requirements;
- current decision limited to `observe_release`, `review_required`, `denied`,
  `expired` or `superseded`; and
- typed reason codes.

Actual `ReviewEvidence`, backend command, handler receipt and readback receipt
belong to later separately authorised gates. They may be specified as required
future inputs, but C3 must not mint instances that look executable or approved.

## Recommended fail-closed C3 state model

```text
candidate_unadmitted
  -> proof_denied
  -> admitted_non_executing

admitted_non_executing
  -> observe_release                 [observe_only; no effect]
  -> review_required                 [ordinary / maintenance / dual]
  -> denied                          [forbidden or policy failure]
  -> expired
  -> superseded

review_required
  -> expired
  -> superseded
  -> denied                          [invalid, revoked or non-distinct review]
  -> future_command_eligibility      [reserved for a later opened gate only]
```

For C3, `future_command_eligibility` is structurally unreachable because both
the command and actuator gates are closed. There are no C3 states named
`authorized`, `executing`, `succeeded`, `rolled_back` or equivalent. A future
gate must add those states with backend reauthorization, one-use command
evidence, durable idempotency, typed handler outcome and independent readback.

All unspecified transitions deny. Expiry, supersession, policy drift, target
revision drift, review invalidation or binding mismatch can only move to a
less-authoritative state. No transition may revive or mutate an expired,
denied or superseded plan in place.

## Advisory conclusion

The safe C3 candidate is a closed deterministic classifier and authority-policy
contract over the already accepted C1/C2 evidence vocabulary. It can prove that
authored-synthetic plans are classified, denied or marked as requiring exact
human authority. It cannot prove intelligent diagnosis, approval, execution,
rollback or recovery. The next implementation should encode the separate
operation/authority mapping, canonical plan binding, monotone invalidation and
unreachable actuator boundary mechanically; any attempt to add a generic
executor, live observer, provider call or actual review/command instance is a
scope expansion rather than C3 completion.
