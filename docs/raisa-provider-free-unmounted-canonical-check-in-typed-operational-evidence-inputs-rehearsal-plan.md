# Provider-free unmounted canonical check-in typed operational-evidence inputs rehearsal

Date: 2026-08-23

Timestamp: 2026-08-23T11:06:45.2591340+10:00 (Australia/Brisbane)

Status: `frozen_narrow_plan`

Operation:
`raisa-provider-free-unmounted-canonical-check-in-typed-operational-evidence-inputs-rehearsal`

Planning source HEAD:
`c976c5ab3096e4c93566dad8afd19a6f9f7d6b96`

Accepted normalizer source:
`39502b308a96842ffe0dcf06f9325eb2fb14b6f9`

Accepted normalizer product source:
`ae62faf95b289b369a6eea1793ee4325f33447bc`

Protected source:
`2e34bdad732fdab32fbf778280b3d3c70d66d602`

Reasoning level: High. The accepted gap decomposition and manifest
architecture freeze the evidence categories. This tranche defines only their
closed, immutable transport shape. It neither obtains evidence nor decides
whether evidence satisfies a gate.

## Objective

Implement only `typed_operational_evidence_inputs` as one pure unmounted Python
module plus focused authored-reference tests. The model carries:

- one external runtime-role attestation readback;
- exactly three ordered rotation/custody evidence readbacks; and
- one deny-only break-glass evidence readback.

The module accepts only an explicitly supplied in-memory object. It does not
parse YAML, read a file or environment, resolve a reference, verify an artifact,
compare with a manifest, evaluate current freshness, return an admission
reading or call any product surface.

## API Spine classification

This is declarative capability-input data only. It adds no GraphQL field,
REST/OpenAPI command, async event, Access AI invocation, client contract,
admission record, audit event or idempotent effect. The future evidence-gate
evaluator will consume the typed reading; this tranche gives the reading no
effect method and no path to a route, database, secret provider or runtime
configuration.

## Exact public contract

`app/services/appointment_check_in_operational_evidence.py` exports
`normalize_check_in_operational_evidence_inputs(payload: object)`. It returns a
frozen `OperationalEvidenceInputNormalizationResult`:

- `outcome == "normalized"`, `reason_code == "evidence_inputs_normalized"`
  and one complete frozen `CheckInOperationalEvidenceInputs`; or
- `outcome == "denied"`, one closed denial reason and `evidence_inputs is
  None`.

Caller-controlled input must not raise a parser or validation exception. The
input type is an exact built-in `dict`; nested records are exact built-in
`dict` values and the rotation collection is an exact built-in `list`.
Unknown, missing or extra fields deny. The input is never mutated and no bundle
digest is created or released.

The aggregate has exactly:

- `schema_version`, fixed to
  `emr4.check-in-operational-evidence-inputs.v1`;
- `role_attestation`;
- `rotation_custody_attestations`; and
- `break_glass_evidence`.

The complete field and vocabulary contract is frozen in
`orchestration/continuity/raisa-provider-free-unmounted-canonical-check-in-typed-operational-evidence-inputs-rehearsal/contract.json`.

## Role-attestation reading

The role record carries an evidence reference, artifact SHA-256, full authority
Git object, environment and snapshot generation, logical and physical role
identifiers, credential-slot identifier, observation/freshness times and an
independent-verifier reference.

Four closed categorical readbacks replace self-asserted Booleans:

- ownership: `non_owner`, `owner` or `unknown`;
- RLS bypass: `nobypassrls`, `bypassrls` or `unknown`;
- product-relation ownership: `absent`, `present` or `unknown`; and
- cross-tenant probe: `denied`, `allowed` or `not_observed`.

The typed layer deliberately represents both satisfactory and hostile
observations. It does not decide that the logical role, credential slot or any
categorical value matches the manifest requirement.

## Rotation/custody readings

Exactly three rows occur in the accepted slot order:

1. `database_connection_credential`;
2. `application_token_signing_key`; and
3. `admission_snapshot_verification_key`.

Each row uses the exact accepted architecture fields: slot and evidence
references, evidence-artifact SHA-256, full authority Git object, environment,
snapshot generation, key ID, version, rotation sequence, observation and
freshness times, and independent-verifier reference. The artifact digest is
the digest of the evidence artifact, never secret material.

No secret value, secret-resolution result, provider endpoint, credential,
database URL or secret-material fingerprint is a field in this type.

## Break-glass reading

The record binds an evidence artifact to environment, generation and time. Its
mode is exactly `deny_only`; its state is one of `inactive`, `engaged_deny` or
`retired`. All three states normalize because the later evaluator owns the
decision that only `inactive` permits evaluation to continue. There is no
bypass, secret-injection, automatic-clear or grant Boolean in this type.

## Structural validation and deferred evaluation

This node checks only closed shape and value representation:

- lowercase 64-character SHA-256 and lowercase full 40-character Git-object
  syntax;
- accepted identifier/reference patterns and positive integer bounds;
- exact field sets and the three-row slot order;
- RFC 3339 timezone-aware timestamps normalized to UTC `Z`; and
- `fresh_until` strictly follows `observed_at` within each evidence record.

The following structurally valid conditions must remain representable for the
next evaluator to deny: wrong environment or generation, role mismatch,
authority-object mismatch across records, wrong key/version binding,
duplicate artifact/reference, self-verification, stale-at-evaluation-time,
`owner`, `bypassrls`, present product ownership, allowed/not-observed
cross-tenant behavior, and engaged/retired break glass.

The future `pure_environment_evidence_gate_evaluator` alone owns comparison
with the normalized manifest, cross-record uniqueness and full-object binding,
current-time freshness, independent-verifier separation and closed gate reason
codes. External artifact authenticity remains an input from an authorized
verifier, never a repository claim.

## Closed normalization vocabulary

Exactly these reasons are returned, in precedence order:

1. `evidence_input_type_invalid`;
2. `evidence_forbidden_field`;
3. `evidence_boolean_claim_forbidden`;
4. `evidence_shape_invalid`;
5. `evidence_git_object_invalid`;
6. `evidence_time_invalid`; and
7. `evidence_inputs_normalized` for success.

Recursive forbidden-field detection covers the accepted secret-value aliases.
Any Boolean anywhere in the supplied object denies separately, so a caller
cannot replace external evidence with `verified: true` or a similar switch.

## Minimal focused verification

Focused tests prove:

- complete immutable normalized readback and UTC normalization;
- exact field sets, exact list type and three-slot ordering;
- every closed categorical role value and every break-glass state remains
  representable without becoming a decision;
- structurally valid mismatch, stale and self-verifier cases remain available
  to the later evaluator;
- every denial reason and precedence-sensitive hostile class;
- full-object and digest syntax, integer bounds and timestamp ordering;
- recursive secret-field and Boolean denial;
- determinism and input non-mutation; and
- absence of filesystem, process environment, configuration, credential,
  YAML, database, route, network, current-time or admission dependencies.

Sol also runs the normalizer tests, architecture and gap-decomposition tests,
API Spine artifact tests, Ruff, compile and `git diff --check`. The historical
gap tripwire is updated to allow exactly this second unmounted service module
and no other application surface.

## Parallelism assessment

- DeepSeek native Harness: `declined`, negative leverage for this exact
  package. The accepted custom runner hard-codes one synthetic edit and prompt;
  changing it would be new runner engineering prohibited by the pragmatic
  stop rule. No Harness failure or provider-performance conclusion is claimed.
- Gemini 3.7 Flash/high: `declined`, neutral leverage for this low-risk
  unmounted model; reassess only on a scope or semantic risk trigger.
- Native subagents: `declined`, negative leverage under developer policy.
- GPT Sol owns the serial contract, implementation, tests, review, acceptance,
  clockwork and Git.

No generic Harness test, new runner, broker change, guard change or transport
fallback occurs in this tranche.

## Acceptance and stop conditions

Accept only when the exact owned source, focused test and historical tripwire
changes implement the frozen contract; the plan/contract packet is internally
consistent; all focused and surrounding checks pass; and review confirms the
module is unmounted and capability-free.

Stop on any external fact selection, evaluator/admission logic, ambient read,
secret/reference resolution, database or route access, API/client change,
ordinary-practice activation, additional application path or unresolved
contract ambiguity.

## Protected boundary

No operational manifest, external evidence artifact, secret value/reference
resolution, `.env`, process environment, configuration, credential store,
database, Docker, route, API, GraphQL, OpenAPI, client, ordinary-practice
admission, feature flag, allowlist, command mounting, generic-status `Arrived`,
action grammar, waiting area, product/patient/appointment/clinical/historical/
protected data, production, deployment, release, Pages or protected-ref
movement is authorized.

Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage exact paths only; never `git add .` or
`git add -A`.
