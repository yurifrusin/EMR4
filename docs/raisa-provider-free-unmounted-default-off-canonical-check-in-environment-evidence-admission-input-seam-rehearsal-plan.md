# Provider-free unmounted default-off canonical check-in environment-evidence admission-input seam rehearsal plan

Date: 2026-08-23

Timestamp: 2026-08-23T12:59:52.4777123+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_plan`

Operation:
`raisa-provider-free-unmounted-default-off-canonical-check-in-environment-evidence-admission-input-seam-rehearsal`

Planning source HEAD:
`ba935ca41c5f93b3584304b0d479df49692bfe21`

Accepted evidence-gate product source:
`89640f1bb6ad992f68d5c20fd578b4062eeb193d`

Accepted admission-kernel source:
`4204ec6348abb0f92b1a30314699d4a469fa860a`

Accepted native-Harness policy source:
`10e46b5330e86c65721848ee0c9a4254983770d2`

Protected source:
`2e34bdad732fdab32fbf778280b3d3c70d66d602`

Reasoning level: High. This seam joins two accepted authority-sensitive pure
evaluators while deliberately leaving every route, command and ordinary-
practice actuator closed.

## Objective

Add one pure, unmounted adapter that consumes the accepted frozen
`EnvironmentEvidenceGateReading` as an independently mandatory ordinary-
practice prerequisite before the existing default-off admission evaluator can
reach its terminal `ordinary_activation_closed` posture.

The reading is evidence, not admission. It cannot create or activate an
ordinary admission record, override the feature flag, affect the authored-
synthetic lane, clear the kill switch, satisfy the existing operational-
evidence Boolean, authorize a command or release a product action.

## Narrowest source shape

The accepted admission evaluator remains unchanged. The new module
`orchestration_harness.check_in_environment_evidence_admission` will expose one
function:

`evaluate_admission_with_environment_evidence(snapshot, request, environment_evidence_gate_reading, *, profile=REHEARSAL_PROFILE)`

It calls `evaluate_admission` first and preserves that decision unless the
decision is exactly:

- `decision = denied`;
- `lane = ordinary_practice`; and
- `reason_code = ordinary_activation_closed`.

That exact result proves the current kernel has already accepted the snapshot
shape, freshness, feature flag, kill switch, lane isolation, ordinary binding,
active record state and existing `operational_evidence_valid` control. Only at
that point does the seam validate the additional reading.

The accepted `AdmissionSnapshot` gains two optional, signed-envelope binding
fields with default `None` for historical constructor compatibility:

- `environment_evidence_identifier`; and
- `environment_evidence_manifest_digest`.

The seam accepts the additional prerequisite only when all of these are true:

1. `type(reading) is EnvironmentEvidenceGateReading`;
2. its schema is exactly
   `emr4.check-in-environment-evidence-gate-reading.v1`;
3. `outcome` is exactly `satisfied`;
4. `reason_code` is exactly `evidence_gate_satisfied`;
5. the snapshot environment-evidence identifier is a valid `env:` identifier;
6. the snapshot manifest digest is a lowercase 64-character SHA-256 value;
7. reading and snapshot identifiers match exactly;
8. the reading generation equals the positive snapshot generation; and
9. reading and snapshot manifest digests match exactly.

Missing, denied, malformed, subclassed, duck-typed or mismatched readings
return the existing closed reason `ordinary_evidence_missing`. A valid reading
returns the original `ordinary_activation_closed` decision unchanged. The seam
does not add a new admitted reason or a path to the kernel's intentionally
unreachable ordinary activation branch.

## Preserved evaluator precedence

The adapter does not pre-empt or reinterpret the accepted kernel. Therefore:

1. snapshot absence/invalidity/ambiguity/freshness remains first;
2. default-off feature denial remains next;
3. the kill switch remains dominant;
4. lane absence and overlap still deny;
5. authored-synthetic-only admission remains byte-for-byte equivalent and
   does not require an environment reading;
6. ordinary binding and active-state checks remain mandatory;
7. `operational_evidence_valid` remains independently mandatory;
8. the typed environment reading becomes independently mandatory; and
9. ordinary activation authority remains false.

## Native DeepSeek worker package

This is the first real-work use under the pragmatic native-Harness plan. GPT
Sol freezes this contract, adds the two compatibility-safe snapshot fields,
builds the task-coupled runner/coordinator and owns all integration decisions.

One fresh DeepSeek session may edit exactly:

- `orchestration_harness/check_in_environment_evidence_admission.py`; and
- `tests/test_check_in_environment_evidence_admission.py`.

The read packet includes this plan, the threat delta, the contract, the two
accepted evaluator modules and focused predecessor tests. The worker has only
`read`, `glob` and `edit`, one call at a time, approval `never`, no shell, Git,
web, workflow, subagent or direct credential. It gets one natural multi-turn
session of at most 900 seconds, zero automatic retry, zero fallback and zero
auxiliary model.

One zero-provider preflight must prove the exact HMR handoff and effective
three-tool view before dispatch. If a mechanical pre-provider defect inside
the one-adapter allowance prevents packet delivery, one fresh attempt may be
made after correction. Once DeepSeek receives the packet, the assignment is
not automatically rerun. Sol accepts, repairs, rejects or recovers the task.

The Harness is measured only at the three agreed clockwork boundaries:
`prepared`, `terminal` and `accepted_or_recovered`. No model turn advances
canonical Continuity.

## Acceptance tests

Focused conformance must prove at least:

- a valid exact satisfied reading reaches `ordinary_activation_closed` and
  never admission;
- absent, denied and malformed readings return `ordinary_evidence_missing`;
- a subclass and a structurally similar duck type are rejected;
- schema, outcome, reason, environment identifier, generation and manifest-
  digest mismatches each deny;
- the existing operational-evidence Boolean cannot be bypassed by a valid
  typed reading;
- feature-disabled, kill-switch, snapshot, lane-overlap, binding and state
  precedence remain unchanged;
- authored-synthetic-only admission is unchanged without a reading;
- no new ordinary admitted reason exists and ordinary release count is zero;
- the predecessor admission-kernel and evidence-gate focused suites pass;
- the module is unmounted and performs no I/O, environment, provider,
  persistence, command or route operation; and
- Ruff, compilation, deterministic contract evidence and `git diff --check`
  pass.

Because this seam changes authority meaning, one fresh Gemini 3.7 Flash/high
read-only veto is reserved after the exact deterministic candidate passes. It
reviews product semantics, not Harness interoperability. Native subagents are
declined under developer policy.

## API Spine classification

This is an internal typed prerequisite adapter. It changes no public REST,
OpenAPI, GraphQL, async-event, Access AI, route or first-party-client contract.
The existing command envelope, human authentication, operator authorization,
server-owned scopes, confirmation, idempotency, audit, full Git identity,
unknown-commit posture and patient-free receipt semantics remain unchanged.

Any public request/response, route mount, activation command or client change
requires a separate plan and authority allocation.

## Protected boundary

No ordinary practice is enabled. No feature flag, authored-synthetic
allowlist, admission record transition, command grammar, generic-status
`Arrived`, route, API, first-party client, waiting-area movement, environment
configuration, operational manifest, secret/reference resolution, database,
Docker, product/patient/appointment/clinical data, production runtime,
deployment, release, Pages or protected ref may change.

Local/origin `master` and `handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage exact paths only; never `git add .` or
`git add -A`.
