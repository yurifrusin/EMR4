# EMR4 controlled-recovery C3 and update-supply D3 architecture

Date: 2026-08-04

Status: provider-free, non-executing architecture/schema candidate

Source HEAD: `3008cdb4d7b5801c45024f7361fb4294aa76fc48`

Parents:

- `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
- `docs/emr4-model-required-bureau-provider-free-successor-lanes.md`
- `docs/emr4-model-required-bureau-gate-zero-shared-contract.md`

## Decision

C3 and D3 specialize the accepted technical-anatomy, diagnosis and update-
provenance contracts into two deterministic planning boundaries. They define
what a future recovery or update plan must contain and which independent
authority it would require. They do not create an executor, importer, migration
runner, updater, provider call, product read, command route or activation path.

The eventual intelligent dialogue remains model-required. In this tranche,
authored-synthetic candidates exercise only closed schemas and deterministic
policy. A fixture is not evidence that the future provider path works.

## C3 recovery plan boundary

A `RecoveryPlanCandidate` is candidate-only data linked to one admitted
diagnosis, one exact technical-anatomy version and context hash, and one signed-
catalog runbook identifier. It must name:

- evidence-bound preconditions;
- an exact environment and target;
- one closed operation class;
- an expected effect and maximum blast radius;
- reversibility and an exact rollback candidate;
- expiry and supersession bindings;
- an idempotency scope and key;
- the immutable audit fields to retain; and
- deterministic postconditions and fresh-read evidence requirements.

Free-form shell, SQL, URL, cloud, path, template, executable, success, approval
or credential fields are forbidden. Bounded explanations remain data and are
screened for executable content before release.

The provider candidate may propose a risk tier, but it cannot set it. The
backend authority service derives the tier from the closed operation class,
target class, blast radius, reversibility and affected control/data plane. The
frozen matrix is:

| Deterministic risk tier | Required authority | Minimum review | Execution posture |
|---|---|---:|---|
| `observe_explain_only` | `observe_only` | 0 | never actuator-eligible |
| `reversible_scoped_service_recovery` | `ordinary_confirmation` | 1 authorized technical operator | one-use evidence would be required |
| `human_approved_rollback_or_failover` | `maintenance_release_authority` | 1 maintenance authority, separate from the candidate generator | one-use evidence would be required |
| `dual_review_database_security_or_data_supply` | `dual_review` | 2 distinct authorized reviewers with role separation | one-use evidence would be required |
| `forbidden_autonomous_action` | `forbidden` | 0 | permanently ineligible under this contract |

Unknown operations, unknown or irreversible rollback, multi-environment scope,
generic shell/SQL/cloud work, credential or policy-authority changes, and any
attempt to lower a computed tier classify as `forbidden_autonomous_action`.
The matrix is monotone: a deterministic classifier may raise risk but never
lower it because a candidate or reviewer asks.

An `AuthorityDecision` is a separate backend-owned object. It binds the
canonical plan hash and revision, earliest effective expiry, policy version,
computed tier, required reviewer roles and counts, separation of duties and
typed denials. The model cannot mint its effective idempotency key. Any plan
amendment, supersession, target-revision drift or policy/reviewer expiry
invalidates prior review evidence rather than refreshing it in place. The
decision always records
`execution_authorized: false` in C3. A future execution command would require a
separately authorized schema, fresh revalidation and one-use execution
evidence; C3 creates none of those.

## D3 staged promotion and rollback boundary

D3 keeps the four D1 command families distinct:

| Update class | Future command family | Canary design | Review authority |
|---|---|---|---|
| `application_dependency_build` | `application_build_promotion` | `single_disposable_instance` | `maintenance_release_authority` |
| `database_schema_migration` | `database_migration_promotion` | `empty_schema_clone` | `dual_review` |
| `reference_dataset` | `reference_dataset_activation` | `synthetic_dataset_namespace` | `dual_review` |
| `operational_clinical_policy` | `policy_content_activation` | `draft_policy_audience` | `dual_review` |

There is no generic update command. The non-executing plan describes this
future fail-closed sequence:

1. bind an admitted D2 provenance/delta digest and exact source artifact;
2. quarantine a future shadow import outside authoritative reads;
3. run class-specific schema, semantic, compatibility and withdrawal checks;
4. constrain a future canary to the class-specific scope above;
5. collect human or dual-review evidence from authenticated, distinct roles;
6. revalidate source attestation, licence/lifecycle, target revision, expiry,
   pre-canary and post-canary review, and current last-known-good eligibility;
7. perform one future class-specific atomic activation;
8. append immutable before/after/provenance/authority/audit evidence;
9. perform a fresh authoritative readback against deterministic postconditions;
10. on failed readback, require a separately authorized atomic rollback to the
    bound last-known-good digest and verify that result by a fresh read.

The design never treats shadow validation, canary success, provider explanation
or human review as activation. It never treats an activation receipt as
readback. Expiry, supersession, source withdrawal, checksum drift, incompatible
delta, missing reviewer separation, target-revision drift, incomplete audit or
unavailable last-known-good state stops the plan before any future effect.

For database migrations, transactionality or an exact maintenance barrier,
application/schema compatibility, rollback feasibility and backup/restore
evidence are mandatory; a pointer or receipt cannot pretend a non-transactional
data transformation is atomic. A withdrawn or expired reference/policy version
cannot become the last-known-good target merely because it was previously
active. This tranche does not run a database, migration or restore. For
reference or policy content, source identity, licence, jurisdiction and
lifecycle metadata remain mandatory. Clinical-policy content would additionally
require future clinician-governance authority; this document grants none.

## API Spine alignment

- GraphQL may eventually expose authorized read-only plan/status/readback
  projections. It cannot invoke a model, promote, activate or roll back.
- Every future effect remains a separate single-purpose REST/OpenAPI command
  family. This tranche adds no route or OpenAPI operation.
- A future command envelope must be backend-owned and bind actor, environment,
  target/current revision, correlation, idempotency, expiry, computed risk,
  confirmation or dual-review evidence, audit and deterministic readback.
- Events remain committed hints requiring fresh authorized reads. Manifests are
  declarative evidence, not command authority.
- Access AI remains closed. A future provider may explain or propose but cannot
  certify evidence, select final authority, approve itself or cause an effect.

## Evidence and claim boundary

The only claim is `provider_free_c3_d3_architecture_and_proof`. Provider calls,
external prompts, patient or product-derived data, live reads, recovery or
update commands, shell/SQL/cloud/IAM, actuators, downloads, licence acceptance,
imports, migrations, activation, deployment, production, release, Pages,
protected refs and protected evidence remain zero and closed. `docs/branding/`
and the four preserved Consultant/Gate-minus-one receipt/state files remain
excluded.
