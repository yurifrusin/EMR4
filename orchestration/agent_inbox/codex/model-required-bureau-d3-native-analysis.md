# D3 staged-promotion and rollback native analysis

Date: 2026-08-04

Source branch and HEAD:
`codex/ariadne-bernie-davida-parallel-seam` at
`3008cdb4d7b5801c45024f7361fb4294aa76fc48`

Decision posture: advisory only; provider-free; repository-local;
non-executing. This analysis grants no provider, product or patient data,
runtime, download, import, migration, activation, actuator, deployment,
production, release, Pages, protected-ref or protected-evidence authority.

Source boundary: the live `AGENTS.md` baton, the active controlled-recovery
development plan, the parent deterministic-authority architecture, the
Gate-zero shared contract, the D1/D2 successor-lane contract and their threat
model deltas, plus the API Spine ADR/programme, Access AI boundary, release
gates, current declarative/command/event examples and artifact invariants.

## Findings, ordered by severity

### Critical — “Atomic activation” is not one transaction across all four classes

The frozen classes have materially different commit boundaries:

- an application/dependency build can normally activate by an atomic,
  compare-and-swap release pointer only after the candidate is already present
  in an isolated target;
- a database migration may include transactional DDL, non-transactional DDL,
  destructive data transformation or an application/schema compatibility
  interval, none of which becomes atomic merely because a promotion record is
  committed;
- a reference dataset can activate by swapping an immutable version pointer
  only if every reader resolves that pointer consistently; and
- policy content can activate by a version/effective-time pointer only if the
  prior and new rule evaluators cannot observe a mixed policy set.

D3 should therefore freeze a shared state protocol but four distinct future
command families and four class-specific activation barriers. A database plan
that cannot prove transactional execution or an exact maintenance barrier,
forward/backward application compatibility and a viable recovery route must be
`forbidden`, not downgraded to a warning. The shared protocol must never expose
a generic `activate_update` operation.

### Critical — Last-known-good is not necessarily a valid rollback target

“Previously active” and “safe to reactivate now” are different facts. A prior
reference dataset or policy may have been withdrawn, expired, superseded by a
safety correction or become jurisdictionally ineligible. A previous
application build may be incompatible with the migrated schema. A database
pointer cannot undo committed data transformation.

Every plan needs a typed `rollback_eligibility` decision bound to the current
target, candidate, baseline, compatibility window, source lifecycle and policy
version. It must identify the rollback mechanism, not just a hash. If the
previous version is no longer eligible, activation must stop unless a separate
reviewed recovery candidate exists. Database rollback must distinguish a true
down migration, snapshot/restore, compatible application rollback and
forward-fix; absence of a proven option is an activation block. A model cannot
declare last-known-good status.

### High — D1/D2 provenance needs a verifiable attestation binding before promotion

The current D1/D2 schema binds source identity, licence identifier, checksum,
schema, jurisdiction and lifecycle metadata, but those declarations alone do
not prove that the named source produced the bytes or that the licence decision
is current. D3 should require a deterministic provenance-admission result that
binds the candidate digest to a named attestation/signature scheme, signer,
trust-anchor set and version, verification time, licence decision and source
lifecycle readback. These are evidence references and digests, not raw keys,
credentials, licensed content or URLs.

Authenticity, licence, jurisdiction, effective/expiry, withdrawal and
supersession must be checked both at initial admission and immediately before
canary and activation. A changed trust anchor, withdrawn source or expired
licence supersedes all earlier approvals and fails closed.

### High — Every transition needs immutable revision and evidence binding

Without exact content and baseline bindings, a valid review can be replayed
against different bytes or a changed active version. Each state snapshot and
transition decision should bind:

- promotion id and immutable plan revision;
- update class and its exact future command family;
- candidate content, normalized-content and semantic-delta digests;
- source-provenance admission and validator-suite identity/version/digest;
- target environment and exact scope;
- expected active baseline revision/digest and eligible rollback target;
- review-policy version, evidence-set digest and expiry; and
- correlation id, idempotency identity and expected state revision.

Any change creates a new plan revision, marks the prior revision
`superseded`, and invalidates its reviews. Transitions use compare-and-swap on
the expected state revision. Unknown, missing, stale or mismatched evidence is
a typed denial; it cannot be repaired by operator prose.

### High — Shadow and canary stages must remain non-serving and separately authorized

Shadow admission means a quarantined, content-addressed version that no
ordinary product read can resolve. Validation occurs only against that version.
A canary is a bounded effect, not a stronger form of static validation, and its
future execution needs its own backend authority and exact environment/scope.
The present D3 lane can specify and simulate the transition contract only.

Class-specific canary posture should be:

| Update class | Shadow boundary | Future canary boundary |
|---|---|---|
| `application_dependency_build` | immutable build/image plus SBOM, lock and configuration digests; no active release pointer | an exact isolated release ring with bounded traffic or authored-synthetic probes, explicit stop conditions and no implicit expansion |
| `database_schema_migration` | an isolated disposable schema/database using only separately authorized data | migration plus compatibility checks in that isolated target; a live shard or real-data clone is not implied |
| `reference_dataset` | quarantined immutable dataset namespace excluded from canonical reads | non-serving dual-read/evaluation queries over separately authorized synthetic inputs; no canonical pointer change |
| `operational_clinical_policy` | immutable policy bundle in a shadow evaluator | synthetic case comparison in a non-authoritative evaluator; no product decision uses the candidate |

Canary scope, duration, sample definition, abort thresholds and maximum blast
radius are typed and cannot be widened during execution. A canary failure moves
to a terminal rejection/quarantine state for that revision; it cannot fall
through to activation review.

### High — Reviewer separation must be backend-owned and checked twice

The model, cognitive cell, proofreader, plan author, importer/validator process,
future actuator and audit/event consumer cannot satisfy human review. Review
evidence should be an opaque, server-held, one-use reference whose server record
binds reviewer principal, role, scope, decision, plan/evidence digest, issue and
expiry times. Client-supplied reviewer claims are assertions only.

There should be one authorization gate before canary and a fresh gate after
canary readback before activation. The backend rechecks current role and
separation of duties at use time. Recommended minimum profiles are:

- application/dependency build: a distinct technical reviewer plus current
  maintenance/release authority;
- database migration: dual review with database/technical competence plus
  current maintenance/release authority;
- reference dataset: dual review separating source/licence/data stewardship
  from domain or clinical safety review where the dataset is clinical; and
- operational/clinical policy: dual review separating policy ownership from
  clinical governance for clinical content, plus current release authority.

These profiles are future policy requirements, not current runtime grants.

### High — Activation output is not proof of active state

The activation path must end first in
`activation_committed_pending_readback`, never directly in `active_verified`.
An independent, scoped read path must establish the resolved active version,
candidate digest, source/provenance binding, schema or policy head, health and
class-specific postconditions. Command output, provider explanation and async
events are not readback.

Timeout, contradiction or incomplete readback produces
`activation_unverified`, blocks subsequent promotion and requires an explicit
rollback or incident decision. Rollback likewise ends in
`rollback_committed_pending_readback`; success is released only after the
independent read path proves the eligible rollback target and postconditions.

### Medium — Audit must be append-only state evidence, not a mutable status log

Every attempted transition, denial, expiry, supersession, canary result,
activation, readback and rollback decision should append an immutable event.
The event records prior/next state, plan and evidence digests, sanitized actor
and reviewer references, policy version, target scope, reason code,
correlation/idempotency coordinates and the resulting receipt digest. It must
not contain raw artifacts, licensed content, secrets, unrestricted logs,
patient/clinical data or model bytes.

For a future mutating command, idempotency claim, one-use authority consumption,
state compare-and-swap, active-pointer or migration barrier change, audit
append, outbox append and durable receipt completion must share the strongest
available atomic boundary. Publication is post-commit only. An event reports a
committed state and may trigger a fresh authorized read; it never grants a
transition.

### Medium — Failure states must be first-class and non-bypassable

The state machine needs closed denial and terminal states rather than a generic
`failed` flag. At minimum: `rejected`, `quarantined`, `expired`, `superseded`,
`activation_unverified`, `rollback_unverified` and `incident_locked`. Unknown
states or transitions deny. No backward state mutation is allowed; retries are
idempotent replays of the same exact transition, while changed input creates a
new plan revision. `incident_locked` permits read/audit only until a separately
authorized recovery decision exists.

## Recommended compact closed schema and state model

### 1. Shared, non-executable `StagedPromotionPlan`

Use one closed schema for evidence and state coordination, but never as a
generic command envelope. Recommended required fields:

```text
schema_version
promotion_id
plan_revision
update_class
future_command_family
evidence_label = provider_free_d3_architecture_advisory
candidate_binding {
  source_provenance_delta_schema_version
  content_sha256
  normalized_content_sha256
  semantic_delta_sha256
  provenance_admission_ref
  provenance_admission_sha256
}
target_binding {
  environment_ref
  scope_kind
  scope_refs[]
  expected_active_revision
  expected_active_sha256
}
shadow_spec {
  isolation_profile_id
  non_serving = true
  canonical_read_visibility = false
  maximum_scope
}
validation_spec {
  suite_id
  suite_version
  suite_sha256
  required_class_checks[]
  incompatibility_is_blocking = true
}
canary_spec {
  profile_id
  maximum_scope
  duration_seconds
  success_predicates[]
  abort_predicates[]
  expansion_allowed = false
}
review_policy {
  policy_id
  policy_version
  pre_canary_requirements[]
  pre_activation_requirements[]
  distinct_principals_required = true
  model_or_actuator_review_allowed = false
}
activation_spec {
  class_specific_barrier_id
  expected_state_revision
  expiry
  postconditions[]
}
readback_spec {
  independent_reader_profile_id
  active_identity_checks[]
  health_or_integrity_checks[]
  deadline
}
rollback_spec {
  mechanism
  target_revision
  target_sha256
  eligibility_evidence_ref
  eligibility_evidence_sha256
  preconditions[]
  postconditions[]
}
risk_and_authority {
  risk_tier
  required_authority_profile
  maximum_blast_radius
}
created_at
expires_at
```

`update_class` and `future_command_family` retain the exact D1/D2 mapping:

| `update_class` | Required future command family |
|---|---|
| `application_dependency_build` | `application_build_promotion` |
| `database_schema_migration` | `database_migration_promotion` |
| `reference_dataset` | `reference_dataset_activation` |
| `operational_clinical_policy` | `policy_content_activation` |

The schema should reject free-form executable instructions, shell, SQL, URLs,
credentials, arbitrary callbacks, raw logs and generic command payloads.

### 2. Closed transition record

`PromotionTransitionDecision` should require `promotion_id`, `plan_revision`,
`expected_state`, `expected_state_revision`, `proposed_state`, exact evidence
references and digests, current policy version, expiry, correlation id and a
typed decision of `admit` or `deny`. An admitted decision remains evidence for
a separately defined class-specific future command; it is not itself an
effect. A denial has a closed reason code and sanitized evidence only.

Recommended principal flow:

```text
planned
  -> provenance_verified
  -> shadow_admitted
  -> validation_passed
  -> canary_review_pending
  -> canary_authorized
  -> canary_observing
  -> canary_verified
  -> activation_review_pending
  -> activation_authorized
  -> activation_committed_pending_readback
  -> active_verified
```

Post-activation recovery flow:

```text
activation_committed_pending_readback
  -> activation_unverified
  -> rollback_review_pending
  -> rollback_authorized
  -> rollback_committed_pending_readback
  -> rolled_back_verified
```

At every pre-effect state, provenance/validation/review failure can move only to
`rejected`, `quarantined`, `expired` or `superseded`. A failed or contradictory
rollback readback moves to `rollback_unverified` and then `incident_locked`;
there is no success claim and no automatic next promotion.

### 3. API Spine implications

- **GraphQL/read context:** a future technical-control read graph may expose a
  scoped, sanitized promotion state, evidence summary, audit timeline and
  independent readback. It has no `Mutation`, provider field, raw artifact,
  licence text, command evidence secret or actuator handle.
- **REST/OpenAPI commands:** any later effect uses separate, single-purpose
  proposal/confirm/activate/rollback operations for each of the four command
  families. Each binds authenticated actor, environment/practice where
  applicable, target, expected revision, candidate and evidence digests,
  current reviewer evidence, correlation, idempotency, expiry, audit and
  readback contract. No `/activate-update` or GraphQL mutation is appropriate.
- **Access AI:** a future approved provider path is a backend Access AI command
  used only for operator dialogue and a closed plan candidate. It cannot
  authenticate provenance, set validator results, provide review evidence,
  activate, roll back or claim readback success. D3 performs no provider call.
- **Async/events:** distinct committed event types may report class-specific
  state changes after commit. Payloads contain identifiers, versions, hashes
  and sanitized state only; consumers must perform a fresh authorized read and
  cannot use an event as transition authority.
- **YAML/manifests:** manifests may declare validator suites, review profiles,
  canary ceilings, risk/authority mappings and readback predicates. They remain
  declarative, signed/versioned inputs; typed code and backend policy enforce
  them. They contain no executable shell/SQL, credentials or live actuator
  instructions.

## Claim boundary

This report is a bounded design advisory for D3. It does not implement or test
the proposed schemas or state machine and does not establish that any shadow
import, validator, canary, reviewer service, activation barrier, readback path
or rollback mechanism exists. All actual download, licence acceptance, import,
migration, activation, actuator, deployment, production and release work
remains outside this lane.
