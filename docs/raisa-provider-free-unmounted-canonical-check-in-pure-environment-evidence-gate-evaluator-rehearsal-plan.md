# Provider-free unmounted canonical check-in pure environment evidence-gate evaluator rehearsal

Date: 2026-08-23

Timestamp: 2026-08-23T11:42:25.0002138+10:00 (Australia/Brisbane)

Status: `frozen_narrow_plan`

Operation:
`raisa-provider-free-unmounted-canonical-check-in-pure-environment-evidence-gate-evaluator-rehearsal`

Planning source HEAD:
`6edcc2486cfe18d48926f0d228dd3c23ac13dde4`

Accepted manifest-normalizer product source:
`ae62faf95b289b369a6eea1793ee4325f33447bc`

Accepted typed-evidence-input product source:
`9011d83d769f45bb717c039a126a890d43922dce`

Protected source:
`2e34bdad732fdab32fbf778280b3d3c70d66d602`

Reasoning level: High. This node turns two accepted structural readings into
one closed, capability-free gate reading. Deterministic reason precedence and
explicit time semantics are security properties even though the code remains
unmounted.

## Objective

Implement only `pure_environment_evidence_gate_evaluator` as one pure Python
module plus focused authored-reference tests. It consumes:

- an exact tuple of accepted manifest-normalization results;
- one accepted typed operational-evidence normalization result; and
- one explicit caller-supplied timezone-aware `datetime`.

It returns a frozen reading with one closed reason. It performs no YAML or raw
object normalization, current-clock read, evidence retrieval, Git lookup,
secret resolution, admission, command or product action.

## API Spine classification

This is a declarative capability-evaluation reading only. A satisfied reading
is not an admission record and has no effect method. It adds no GraphQL field,
REST/OpenAPI command, async event, Access AI invocation, audit record,
idempotency contract, client surface or runtime mount. The later default-off
admission seam remains a separate dependency and authority decision.

## Public contract

`app/services/appointment_check_in_environment_evidence_gate.py` exports
`evaluate_check_in_environment_evidence_gate(manifest_results,
operational_evidence_result, *, evaluation_time)`.

The evaluator returns a frozen `EnvironmentEvidenceGateReading` with exactly:

- `schema_version`, fixed to
  `emr4.check-in-environment-evidence-gate-reading.v1`;
- `outcome`, either `denied` or `satisfied`;
- one accepted `reason_code`;
- the selected `environment_identifier` or `None`;
- the selected positive `admission_snapshot_generation` or `None`; and
- the selected lowercase manifest SHA-256 or `None`.

The eleven reason codes remain exactly those accepted by the architecture:

1. `manifest_absent`;
2. `manifest_invalid`;
3. `manifest_stale`;
4. `manifest_ambiguous`;
5. `environment_mismatch`;
6. `role_binding_missing`;
7. `role_evidence_invalid`;
8. `secret_reference_invalid`;
9. `rotation_evidence_invalid`;
10. `break_glass_not_inactive`; and
11. `evidence_gate_satisfied`.

Only the last reason has `outcome == "satisfied"`. A satisfied reading remains
capability-free.

## Exact input and precedence rules

The manifest envelope must be an exact built-in tuple. An empty tuple yields
`manifest_absent`. Every item must be an exact internally consistent
`ManifestNormalizationResult` in its normalized state with a lowercase
64-character digest and exact normalized dataclasses; otherwise the result is
`manifest_invalid`. More than one valid normalized result yields
`manifest_ambiguous` without selecting either manifest.

The explicit evaluation time must be an exact timezone-aware `datetime`.
Programmer misuse is represented as `manifest_invalid`. The evaluator converts
the supplied time to UTC but never reads current time. For one valid selected
manifest, the half-open window is `issued_at <= evaluation_time < expires_at`;
outside it yields `manifest_stale`.

After the manifest envelope, reasons have this fixed evaluation order:

1. environment, snapshot-generation and full-authority-object equality across
   every evidence record;
2. exact logical/physical role and credential-slot binding;
3. satisfactory fresh independent role evidence;
4. exact three-slot secret-reference ordering, uniqueness and key/version/
   evidence-reference binding;
5. fresh independent rotation/custody evidence matching every manifest row;
6. fresh independent deny-only break-glass evidence whose manifest and
   operational state are both exactly `inactive`; and
7. `evidence_gate_satisfied`.

The evaluator treats the normalized readings as data, not as an unforgeable
capability. It therefore rechecks the critical closed schema, full-object and
digest syntax, slot order, positive integers, timestamp parseability and
cross-binding invariants before release.

## Evidence semantics

Role evidence must match the manifest's tenant-attestation reference, logical
role, physical database role and credential slot. It must observe
`non_owner`, `nobypassrls`, absent product-relation ownership and a denied
cross-tenant probe. Its evidence artifact must be current at the explicit time
and its verifier reference must differ from its evidence reference.

The three operational rotation rows must retain the accepted slot order. Each
must match both the corresponding secret-reference binding and manifest
rotation row for evidence reference, artifact digest, authority object,
environment, generation, key, version, sequence and normalized time window.
Evidence references and artifact digests are distinct across the full role,
rotation and break-glass bundle; no verifier reference may equal any evidence
reference.

Break glass is deny-only. Missing, malformed, stale, self-verified, mismatched,
`engaged_deny` or `retired` posture yields
`break_glass_not_inactive`. It never grants or restores authority.

The complete frozen machine contract is
`orchestration/continuity/raisa-provider-free-unmounted-canonical-check-in-pure-environment-evidence-gate-evaluator-rehearsal/contract.json`.

## Minimal focused verification

Focused tests prove every reason, fixed precedence, the half-open manifest and
evidence freshness boundaries, timezone normalization, multiple-manifest
denial, exact role observations, all environment/generation/object bindings,
slot/key/version/reference equality, global artifact/reference uniqueness,
verifier separation, every break-glass state, deterministic immutable output,
and absence of filesystem, environment, configuration, credential, YAML,
database, route, network, current-time or admission capabilities.

Sol also runs the accepted normalizer and typed-input tests, architecture and
gap-decomposition tests, API Spine artifact tests, Ruff, Python compilation and
`git diff --check`. The historical gap tripwire may be changed only to permit
this exact third unmounted service module.

## Parallelism assessment

- DeepSeek native Harness: `declined`, negative leverage. No already accepted
  runner can implement this evaluator source-and-test package unchanged; new
  runner, broker or guard engineering is outside the pragmatic adoption rule.
- Gemini 3.7 Flash/high: `declined`, neutral leverage. The architecture already
  freezes the reasons and the node is pure and unmounted; reassess only on a
  semantic conflict or scope trigger.
- Native subagents: `declined`, negative leverage under developer policy.
- GPT Sol owns the serial contract, implementation, tests, review, acceptance,
  clockwork and Git.

No generic Harness test, provider call or silent Claude Code fallback occurs.

## Acceptance and stop conditions

Accept only when the exact source, focused test and historical tripwire changes
implement this frozen contract; every reason and boundary is covered; all
focused and surrounding checks pass; and direct review confirms a pure,
unmounted, capability-free reading.

Stop on any external fact selection, raw manifest/evidence parsing, ambient
clock or configuration read, secret/reference resolution, Git lookup,
database, route, admission record, product mount, ordinary-practice activation
or unresolved contract ambiguity.

## Protected boundary

No operational manifest or evidence artifact, real environment or practice
selection, secret value/reference resolution, `.env`, process environment,
configuration, credential store, Git command, database, Docker, route, API,
GraphQL, OpenAPI, client, ordinary-practice admission, feature flag, allowlist,
command mounting, generic-status `Arrived`, action grammar, waiting area,
product/patient/appointment/clinical/historical/protected data, production,
deployment, release, Pages or protected-ref movement is authorized.

Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage exact paths only; never `git add .` or
`git add -A`.
