# Threat-model delta — default-off ordinary-practice canonical check-in admission control

Date: 2026-08-19

Status: architecture-only; no runtime or enablement

Parent evidence: accepted ordinary-practice readiness review at
`27101faa86b5aa3850e90bc4ded8600e5f8d7dc9`.

## Scope

This delta covers only the future authority boundary that decides whether one
practice may reach the already accepted canonical A5.1 check-in proposal and
confirmation routes. The route, adapter, authentication, transaction, audit,
event, response, client and waiting-area contracts are unchanged.

No threat is accepted merely because the architecture is provider-free. The
contract must represent each denial invariant and the deterministic validator
must reject missing or widened controls.

## Assets and trust boundaries

Protected assets are:

- default denial and the existing global feature flag;
- the exact authored-synthetic allowlist semantics;
- ordinary admission records, versions, freshness and generation identity;
- the global monotonic kill switch and practice-scoped disable state;
- full Git authority objects and operational-evidence digests;
- control-command idempotency, append-only audit and unknown-commit state;
- non-PHI metric/alert boundaries; and
- route authentication, opaque proposal evidence and patient-free receipt
  invariants below the admission layer.

New trust boundaries are the future control-plane writer, immutable admission
snapshot distributor, pure evaluator, operational-evidence verifier,
read-only posture projection and telemetry exporter. None may share a write
capability through GraphQL, events, models, agents or metrics.

## Threats and required controls

| Threat | Failure mode | Required fail-closed control |
|---|---|---|
| Synthetic-to-ordinary privilege confusion | A synthetic practice or receipt silently becomes ordinary authority. | Separate lane types and inputs; no inference or substitution; simultaneous matches deny. |
| Default-on or missing-record fallback | Absence is treated as admitted or a stale last-known-good record is reused. | Absence means disabled; malformed, stale, missing and unresolved snapshots deny without fallback. |
| Kill-switch bypass | Synthetic or ordinary admission succeeds while the global switch is engaged. | Switch denial dominates both lanes and is machine-tested before an allow result. |
| Unsafe switch clearing | A retry, metric, model or ordinary command clears the emergency stop. | In-generation transition is one-way `clear -> engaged`; clearing requires a new generation and separate authority. |
| Rollback re-enablement | Rollback restores a previous active record. | Withdrawal is disable-only and terminal; rollback has no transition to active. |
| Resume shortcut | Suspended state is resumed without fresh evidence. | No resume edge; reactivation requires a new record, version, generation and evidence. |
| Abbreviated or unresolved Git authority | A seven-character label is accepted as the reviewed source. | JSON Schema and semantic validator require lowercase `^[0-9a-f]{40}$` plus shared object resolution. |
| Cross-tenant admission | Caller-selected practice or wrong runtime role admits another tenant. | Server-owned scope, exact practice binding, non-owner `NOBYPASSRLS` operational proof and cross-tenant denial. |
| Concurrent lost update | Two controllers activate or disable from stale state. | Expected record version, snapshot generation and one-current-record constraint; conflict denies. |
| Unknown-commit false success | Control-plane write outcome is uncertain but success is released or blindly retried. | Release no success; read back by server-owned command/idempotency identity; no retry of uncertain rollback. |
| Model or event authority injection | A provider result, DeepSeek WorkOrder or committed event changes admission. | Current authenticated human and REST/OpenAPI command only; model/agent/event write authority false. |
| GraphQL command tunnel | A read projection performs a mutation. | GraphQL is read-only posture projection; all state changes are typed REST/OpenAPI commands. |
| Operational-proof laundering | Synthetic tests are presented as ordinary runtime/secret/recovery proof. | Three independent exact-generation evidence gates; synthetic substitution forbidden. |
| Telemetry PHI or tenant disclosure | Labels include practice, patient, appointment, user, correlation, tokens or text. | Exact five low-cardinality metric families, closed label values and explicit forbidden identifiers/bodies. |
| Telemetry feedback loop | Alert or exporter automatically activates, clears, retries or rolls back. | One-way observation only; no automatic control action, retry or admission feedback. |
| Audit omission | Admission changes without attributable evidence. | Append-only audit is a prerequisite of every command; audit failure denies and alerts. |
| Route-boundary erosion | Admission bypasses Receptionist role, evidence, idempotency or transaction checks. | Evaluator emits only a typed decision and has no route, confirmation, database or command capability. |
| Clockwork authority escalation | Shared Ariadne/DeepSeek journal is treated as product permission. | Shadow status remains explicit; broker protocol carries traceability only and no product or activation authority. |

## Data minimization

The admission evaluator needs control-plane identity but no patient or clinical
data. It must never receive an appointment body, reason, note, patient,
practitioner, token or response payload. The typed decision exposes only lane,
outcome, closed reason, generation and digest.

Control audit may contain protected operational identifiers required for
attribution, under its own access boundary. Metrics and alerts may not copy
them. Environment is the only deployment-scope label.

## API and transaction posture

Future state-changing operations use REST/OpenAPI, authenticated current-human
authority, a separate operations role, server-owned tenant/environment scope,
correlation, idempotency, full-request digest, expected version/generation,
closed reason, full resolved Git object, freshness, append-only audit and a
bounded patient-free receipt. GraphQL and events remain read-only/observational.

The architecture does not claim that the database transaction or runtime role
already exists. Non-owner tenant enforcement, concurrency, rollback and
unknown-commit drills remain mandatory operational evidence before an active
ordinary record can validate.

## Residual risk and closed authority

Residual risk remains deliberately blocking: the ordinary database role,
environment/secret posture and real unknown-commit recovery are unproved. A
pure unmounted kernel can be rehearsed next with zero active records, but no
product mounting or ordinary-practice activation may occur until those proofs
and a later explicit authority gate pass.

No product/configuration/OpenAPI/GraphQL/database change, route call, ordinary
enablement, generic-status `Arrived`, client, waiting-area movement,
patient/clinical data, provider/network call, deployment, release, Pages,
clockwork adoption or protected-ref movement is authorised.
