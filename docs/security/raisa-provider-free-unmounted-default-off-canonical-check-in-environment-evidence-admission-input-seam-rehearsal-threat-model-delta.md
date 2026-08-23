# Threat-model delta — check-in environment-evidence admission-input seam

Date: 2026-08-23

Timestamp: 2026-08-23T12:59:52.4777123+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_delta`

## Security change

The tranche adds one pure unmounted adapter between the accepted capability-
free environment evidence-gate reading and the accepted default-off ordinary-
practice admission kernel. It adds no command, route, data source or runtime
authority.

## Threats and controls

| Threat | Required control |
|---|---|
| A caller substitutes a Boolean or duck-typed object for reviewed evidence | Require exact built-in type identity for `EnvironmentEvidenceGateReading`; reject subclasses and structural lookalikes. |
| A denied reading is relabelled as satisfied | Require exact schema, `satisfied` outcome and `evidence_gate_satisfied` reason together. |
| Evidence from another environment is replayed | Bind the exact reading environment identifier to the signed snapshot field and require the closed `env:` syntax. |
| Evidence from another admission generation is replayed | Require a positive snapshot generation and exact reading equality. |
| Evidence from another manifest is substituted | Require exact lowercase SHA-256 equality between reading and signed snapshot manifest binding. |
| New evidence bypasses an existing admission prerequisite | Call the accepted kernel first and validate the reading only after the exact `ordinary_activation_closed` result; do not alter existing decision precedence. |
| Evidence accidentally gates or widens authored-synthetic practice | Return every non-target kernel decision unchanged, including synthetic admission and lane-overlap denial. |
| A satisfied reading becomes an admission capability | Return the original denied `ordinary_activation_closed` decision; define no new admitted reason and keep ordinary activation authority false. |
| Exceptions escape from hostile caller-controlled objects | Use exact frozen dataclass types and bounded primitive validation; the public seam returns a closed decision for any invalid reading. |
| Harness tools or scope are widened to obtain a candidate | Keep the broker at exact `edit`, `glob`, `read`; constrain edits to two owned files in a fresh sparse worktree; Sol owns commands, diff review and integration. |
| Provider or model failure causes hidden fallback or repeated spend | Zero automatic retry, fallback and auxiliary model; one mechanical pre-provider retry only under the frozen rule, and no same-task rerun after packet delivery. |
| Model prose or Harness state changes workflow authority | Consume only the changed-path diff and coarse prepared/terminal boundary; Sol and deterministic tests own acceptance and canonical clockwork publication. |

## Data and trust boundary

The worker packet contains only repository source, synthetic fixtures and the
frozen contract. It contains no live manifest, environment configuration,
secret value or resolvable reference, product/patient/appointment/clinical
data, credential or protected evidence. The broker alone holds the DeepSeek
credential and releases no credential to the model-facing workspace.

The snapshot binding fields represent part of the future signed admission
snapshot envelope. This unmounted rehearsal does not create or verify a real
signature and cannot be used as evidence that operational signing or manifest
distribution exists.

## Residual risk

This proves deterministic fail-closed composition of accepted typed inputs.
It does not prove external evidence truth, key custody, production signature
verification, database authorization, deployment suitability or ordinary-
practice readiness. Those remain closed successor questions.

Local/origin `master` and `handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. No Pages or protected-ref movement
is authorized.
