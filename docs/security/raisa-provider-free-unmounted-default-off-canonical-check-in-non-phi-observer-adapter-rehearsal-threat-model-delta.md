# Threat-model delta — unmounted default-off canonical check-in non-PHI observer adapter rehearsal

Date: 2026-08-22

Timestamp: 2026-08-22T23:59:22.8176645+10:00 (Australia/Brisbane)

Status: `frozen_for_execution`

Operation:
`raisa-provider-free-unmounted-default-off-canonical-check-in-non-phi-observer-adapter-rehearsal`

## Security boundary

This tranche adds one pure in-memory adapter under `orchestration_harness/`.
It has no application mount, runtime configuration, filesystem read/write,
network, database, exporter, alert destination, provider, command or automatic-
action capability. The only constructible adapter generation is disabled.

## Protected assets

- exact default denial and zero disabled-path work;
- the accepted manifest's low-cardinality non-PHI vocabulary;
- honest separation of shared, rehearsal-only and future-only reason codes;
- immutable typed metric/alert intents with no delivery capability;
- REST/OpenAPI command authority and read-only GraphQL posture; and
- all product, data, provider, production and protected-ref closures.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Rehearsal-only denial is mislabeled as a production cause | Exact set-difference assertions; `ordinary_activation_closed` raises `reason_not_in_manifest_domain` and produces no batch. |
| Future ordinary admission is fabricated | Manifest-only reasons are recorded as unavailable from the current kernel and cannot be constructed as a kernel `DecisionReason`. |
| High-cardinality or identifying material enters an intent | Material shape contains only enums, one bounded number and Booleans; exact label domains and source AST checks reject identifiers/free text. |
| Disabled runtime still evaluates data | Generation-first short circuit returns the shared empty batch without calling the material supplier. |
| Intent object becomes an emitter | Module has no callback, registry, queue, exporter, transport, filesystem, environment, application or network capability. |
| Alert becomes an actuator | Alert type freezes `automatic_control_action=false`; module has no retry, switch-clear, rollback or command port. |
| Snapshot age alert is invented without a bound reading | `snapshot_age_over_bound` requires an explicit non-negative age; the adapter does not invent a threshold absent from the manifest. |
| Active-record, audit or rollback alert overclaims evidence | Each Boolean condition requires its compatible typed decision/operation context before an alert can be built. |
| Unknown commit releases success or retry | Only the exact kernel no-success/readback-required/no-retry result is accepted. |
| Control operation labels drift | One exhaustive five-entry full-ID-to-short-label mapping is asserted against both contracts. |
| Metric shape drifts from the manifest | Names, kinds, label order/domains, counter increment and gauge ranges are validated in immutable dataclasses and repository tests. |
| Telemetry feeds back into admission | Adapter returns data only; no kernel input, route response, audit, command or control path accepts its output. |

## API and data posture

No REST/OpenAPI, GraphQL or async contract changes. The adapter receives no
request, response, audit record, token, digest, practice, appointment, patient,
practitioner, user, actor, correlation, idempotency, command or record identity.
No product, patient, clinical, historical or protected evidence is read.

## Residual risk

The pure builder proves only an interface shape. No registry, concurrency,
retention, cardinality under load, delivery, outage, exporter, destination,
access-control or operational alert behavior is tested. The manifest/kernel
reason asymmetry remains explicit: a later production kernel must add future
reasons through a separate authority-controlled tranche rather than coercing
this adapter.

No provider, database, Docker, application runtime, deployment, release, Pages
or protected ref is accessed or changed.
