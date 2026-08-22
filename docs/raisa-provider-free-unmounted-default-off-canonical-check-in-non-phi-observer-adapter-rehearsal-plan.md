# Provider-free unmounted default-off canonical check-in non-PHI observer adapter rehearsal plan

Date: 2026-08-22

Timestamp: 2026-08-22T23:59:22.8176645+10:00 (Australia/Brisbane)

Status: `frozen_for_execution`

Operation:
`raisa-provider-free-unmounted-default-off-canonical-check-in-non-phi-observer-adapter-rehearsal`

Task baseline: `3dbb048a00243dbeeb635bbad7d4ea5f92ab6134`

Target result:
`raisa_provider_free_unmounted_default_off_canonical_check_in_non_phi_observer_adapter_rehearsal_pass`

Reasoning level: High. The accepted kernel and canonical manifest freeze both
closed vocabularies. This tranche implements a pure disabled bridge without
changing authority, product behavior or runtime configuration.

## Objective

Add one pure standard-library module at:

`orchestration_harness/check_in_observability.py`

It must provide:

1. immutable non-PHI metric and alert intent types;
2. one future-shaped pure builder whose fields are limited to closed kernel
   values, exact manifest domains, a bounded non-negative snapshot age and
   explicit Boolean failure conditions;
3. one globally disabled unmounted adapter whose only constructible
   generation returns an empty batch before calling its material supplier; and
4. exact deterministic tests for the manifest vocabulary, compatibility
   boundary, typed outputs, hostile inputs and zero-work disabled path.

An intent is in-memory declarative data only. It is not emission, transport,
delivery, an exporter call, monitoring evidence or control authority.

## Exact source contracts

The adapter is bound to:

- the accepted pure admission kernel at
  `orchestration_harness/check_in_admission_control.py`, reviewed source
  `4204ec6348abb0f92b1a30314699d4a469fa860a`; and
- the exact 6,291-byte canonical manifest
  `docs/api-spine/manifests/canonical-check-in-non-phi-observability.json`,
  SHA-256
  `79d6191e1a499e85bb12be38fd15980c7f1bf7dc54eb15132c607b0c43341d8c`.

Tests load the repository manifest and require exact equality with the module's
closed constants. Runtime code performs no filesystem read.

## Frozen compatibility reading

The kernel and manifest intentionally have different time horizons.

- Lane values are exactly equal: `none`, `authored_synthetic`,
  `ordinary_practice`, `ambiguous`.
- Decision outcomes are exactly equal: `admitted`, `denied`.
- Twelve kernel decision reasons are present in the manifest and may map
  without renaming.
- Kernel-only `ordinary_activation_closed` is a rehearsal-profile denial. It
  must raise `reason_not_in_manifest_domain` and release no metric or alert
  intent. It must never be relabelled `ordinary_evidence_invalid`,
  `ordinary_state_not_active` or another production reason.
- Manifest-only `ordinary_record_missing`, `ordinary_evidence_invalid` and
  `admitted_ordinary` are future-production vocabulary. The current kernel
  cannot emit them, and this adapter must not fabricate them.
- Full kernel control operation IDs map one-to-one to the manifest's short
  labels: `prepare`, `activate`, `suspend`, `withdraw` and
  `engage_kill_switch`.

This asymmetry is a fail-closed interface fact, not a taxonomy repair.

## Typed material and intent boundary

`ObservationMaterial` may contain only:

- one exact environment enum;
- an optional kernel `AdmissionDecision`;
- an optional finite non-negative snapshot age plus a Boolean
  `snapshot_age_over_bound` reading;
- an optional kernel `KillSwitchState`;
- an optional exact kernel `UnknownCommitResult`;
- an optional kernel `ControlOperation` paired with an exact manifest
  `ControlOutcome`; and
- three explicit Booleans for active-record rejection, control-audit failure
  and rollback failure.

It contains no practice, appointment, patient, practitioner, user, actor,
correlation, idempotency, command, record, digest, token, free-text,
request-body or response-body value.

The builder may create only:

- counter intents with increment exactly `1`;
- snapshot-age and kill-switch gauge intents;
- closed label tuples in the exact manifest order; and
- one each of the six exact critical, non-identifying, non-actuating alerts.

Contradictory or under-specified material rejects before any batch is returned.
Active-record rejection requires an ordinary-lane decision; audit failure
requires a control operation; rollback failure requires `withdraw`; snapshot
age-over-bound requires an age; and unknown commit must retain exact no-
success/readback-required/no-retry posture.

## Disabled adapter boundary

`ObserverGeneration` has `enabled: false` and rejects construction with
`true`. The default adapter checks that immutable generation first and returns
one shared empty batch without invoking the supplied material factory.

No enabled adapter, emitter, registry, queue, exporter, callback, background
task, environment setting, route import or application mount exists. The pure
builder is exercised directly only in provider-free tests to prove the future
shape.

## API Spine classification

This is an unmounted observation adapter for a REST/OpenAPI command family's
accepted support vocabulary.

- REST/OpenAPI remains the only mutation authority.
- GraphQL remains read-only.
- Async events remain observations and cannot become command evidence.
- Metrics and alerts cannot admit a lane, clear a switch, retry a command,
  execute rollback or change a response.
- Audit remains attributable authority evidence and is never telemetry input.

No OpenAPI, GraphQL, route, response, command schema or operation ID changes.

## Exact owned outputs

GPT Sol may create only:

1. this plan and its threat-model delta;
2. `orchestration_harness/check_in_observability.py`;
3. one focused deterministic test module;
4. required five-source runtime states and receipts; and
5. bounded efficacy, closeout, Sol acceptance, Yuri summary and transactional
   clockwork evidence after acceptance.

No `app/**`, configuration, route, OpenAPI, GraphQL, client, migration,
database, transport/exporter, Harness broker/runner or protected source is
editable.

## Deterministic acceptance

Pass requires:

1. the fresh five-source receipt and all three lane dispositions pass;
2. imports remain standard library plus the exact sibling admission kernel;
3. module constants equal every relevant manifest name, kind, label, value,
   alert and false control;
4. every shared kernel reason produces the exact admission-decision intent;
5. `ordinary_activation_closed` rejects with zero intents and no production
   reason substitution;
6. no current-kernel test can manufacture the three manifest-only future
   reasons;
7. the five full operation IDs map exactly to the five short labels;
8. gauges, counters and all six alerts are exact and immutable;
9. malformed schema, negative/non-finite age, incomplete control pair,
   contradictory alert condition or malformed unknown-commit posture rejects;
10. the disabled adapter produces the shared empty batch and invokes zero
    supplier calls, including for a supplier that would raise;
11. source checks prove no filesystem, environment, network, database,
    application, transport or automatic-action capability;
12. focused, admission-kernel, API-Spine, latch, Baton, Compass and clockwork
    tests pass with Ruff, compilation and `git diff --check`; and
13. protected refs remain exact while `docs/branding/` and all unrelated
    untracked files remain preserved.

## Parallelism-efficacy assessment

- DeepSeek V4 Flash/high: `declined`, negative leverage. Native Harness worker
  allocation remains closed, Claude Code is historical only and no allowed
  provider-free transport exists.
- Gemini 3.7 Flash/high: `declined`, neutral leverage. The tranche is provider-
  free and exact closed-set comparison plus deterministic hostile tests decide
  this unmounted disabled adapter.
- Native subagents: `declined`, negative leverage. Developer policy prohibits
  proactive delegation and the compatibility reading, code and tests are one
  tightly coupled package.
- GPT Sol owns the plan, implementation, API Spine review, admission,
  acceptance, Git and closeout.

Reassess after focused validation, on any reason coercion or capability drift,
and at closeout.

## Recovery and stop rules

- A shared-value mismatch is a candidate defect and may receive one bounded
  mechanical repair.
- An attempt to coerce `ordinary_activation_closed` into a production reason
  is conceptual and must be rejected, not repaired by renaming.
- Any filesystem/runtime/product/transport dependency, enabled generation,
  identifier-bearing field or automatic action stops acceptance.
- Any P0-P2 API Spine conflict stops acceptance and requires a separately
  bounded corrective plan.

## Claim and protected boundary

Passing proves only a pure unmounted disabled adapter and exact future-shaped
intent mapping for compatible closed values. It does not prove metric emission,
alert delivery, monitoring, retention, exporter behavior, automatic control,
ordinary activation, live secret custody, unknown-commit recovery, client
cutover, runtime or production suitability.

No ordinary-practice enablement, feature/allowlist change, application/
configuration/route/OpenAPI/GraphQL/client change, generic-status `Arrived`,
action grammar, waiting-area movement, product/patient/appointment/clinical/
historical/protected data, DeepSeek/native-Harness work, provider, database/
Docker, production runtime, deployment, release, Pages or protected-ref
movement is authorised. Preserve `docs/branding/` and every unrelated
untracked file. Use explicit-path staging only.
