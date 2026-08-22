# Threat-model delta — default-off canonical check-in non-PHI observability manifest convergence

Date: 2026-08-22

Timestamp: 2026-08-22T23:34:18.1886561+10:00 (Australia/Brisbane)

Status: `frozen_for_execution`

Operation:
`raisa-provider-free-default-off-canonical-check-in-non-phi-observability-manifest-convergence-rehearsal`

## Security boundary

This tranche adds one repository-static JSON manifest projected exactly from an
accepted architecture contract. It adds no instrumentation library, exporter,
collector, alert destination, credential, network, route, database, command,
runtime or deployment surface.

## Protected invariants

1. The projected `observability` object deep-equals the accepted source.
2. Instrumentation, alert transport, automatic control action and ordinary
   practice remain disabled.
3. Metric label domains are closed and low-cardinality.
4. Identifier, free-text, secret, request/response and audit-record values never
   enter telemetry.
5. Alerts contain no identifiers and cannot retry, activate, roll back or
   change a kill switch.
6. The manifest is declarative vocabulary, not operational monitoring evidence.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Projection silently drops or changes an accepted metric/alert | Deep equality with the accepted architecture sub-object plus exact count/name tests. |
| High-cardinality or identifying labels leak operational data | Exact label domains and the complete forbidden-label/value set are copied and asserted. |
| Alerts become command or rollback actuators | Every alert requires `automatic_control_action: false`; wrapper effects and transport defaults remain false. |
| Raw request/response or attributable audit becomes telemetry | Exact false flags and forbidden-value assertions reject the change. |
| Manifest presence is overstated as running monitoring | `prepared_not_authorized`, default-off wrapper and narrow claim separate vocabulary from runtime evidence. |
| A short or wrong source revision weakens provenance | The full accepted 40-character architecture object and exact source path are machine asserted. |
| JSON formatting or wrapper drift hides semantic change | Canonical sorted JSON bytes, fixed byte count and SHA-256 are required. |
| Scope expands into product or protected surfaces | Exact-path ownership, explicit-path staging, protected-ref and preserved-untracked checks fail closed. |

## Residual risk

No metric is emitted and no alert is delivered. A future instrumentation or
transport tranche must separately define cardinality budgets, retention,
destinations, access, outage behavior and proof that telemetry cannot feed back
into authority. This manifest supplies only an exact default-off vocabulary.

No protected evidence, PHI, provider, database, Docker, live route, deployment,
release, Pages or protected ref is accessed or changed.
