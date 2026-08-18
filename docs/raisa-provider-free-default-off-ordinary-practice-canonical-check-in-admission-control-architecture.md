# Provider-free default-off ordinary-practice canonical check-in admission-control architecture

Date: 2026-08-19

Status: source-bound architecture; no enablement

Source HEAD: `062f5fb12eb82eab6ec570abea56ad1bd9a7b304`

## Outcome

The accepted A5.1 check-in route can gain a future ordinary-practice lane
without turning its authored-synthetic allowlist into an accidental production
admission mechanism. The architecture uses one immutable, versioned control-
plane snapshot and one deterministic evaluator. Absence, ambiguity, staleness,
unresolved evidence or an engaged kill switch denies.

This document explains the normative machine reading in
`orchestration/continuity/raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture/contract.json`.
If prose and that contract differ, deterministic validation fails closed.

## Authority layers

The layers are deliberately non-substitutable:

1. The existing A5.1 feature flag remains the global default-off boundary.
2. The existing authored-synthetic practice allowlist remains exactly a
   synthetic development gate.
3. A future ordinary-practice admission record is a separate server-owned
   control-plane object. It is bound to one practice, environment, operation
   family, record version, snapshot generation, freshness window, exact
   authority Git object and three operational-evidence digests.
4. Route authentication, the Receptionist role, opaque proposal evidence,
   idempotency, locking, audit, event and check-in product adapter remain the
   data-plane command boundary. Admission cannot replace any of them.

An ordinary record is not derivable from a feature flag, synthetic allowlist,
synthetic receipt, client header, GraphQL input, async event, telemetry, model
output or DeepSeek WorkOrder. If ordinary and synthetic lanes both match, the
configuration is ambiguous and the evaluator denies.

## State machine

No ordinary record means disabled. `prepared` is a reviewable but non-admitting
candidate. Only `active` could admit, and only after every shared and
operational prerequisite passes. `suspended` is a practice-scoped emergency
stop. `withdrawn` is terminal.

The allowed graph is:

```text
absent ──prepare──> prepared ──activate──> active ──suspend──> suspended
                         │          │                         │
                         └──────────┴──────withdraw───────────┘
                                              │
                                              v
                                          withdrawn
```

There is no resume edge. A suspended or withdrawn admission cannot be turned
active in place. Any later reactivation starts with a new record, new expected
version, new generation and fresh evidence. Rollback is the `withdraw`
operation and is disable-only; it can never restore a prior active version.

The architecture describes activation so its prerequisites can be tested, but
this tranche neither implements nor authorizes it. The contract has zero
ordinary records and `activation_authority_granted: false`.

## Decision algebra

The evaluator operates on an immutable process-consistent snapshot. Its allow
condition is equivalent to:

```text
feature_enabled
AND NOT global_kill_switch_engaged
AND exactly_one_lane_matches
AND (
  unchanged_authored_synthetic_admission
  OR (
    ordinary_record_state_is_active
    AND exact_record_bindings_match
    AND all_three_operational_evidence_gates_pass
  )
)
```

Before evaluating that condition, snapshot shape, signature, Git-object
resolution, freshness, environment and uniqueness must all validate. No stale
last-known-good snapshot is used. Unknown fields, states, versions or reason
codes deny.

The output is a bounded decision containing schema version, admitted/denied,
lane, closed reason code, snapshot generation and digest. It has no database,
route, patient, confirmation-evidence or command capability.

## Dominant kill switch

The global switch is `clear` by default and has one in-generation transition:
`clear -> engaged`. Engagement denies both synthetic and ordinary lanes. It
cannot clear itself, be cleared by telemetry, or be toggled by a retry. Clearing
requires a new validated generation and a separately authorised operation.

Practice-scoped suspension and withdrawal remain useful even when the global
switch is clear. The global switch is deliberately broader and takes
precedence over every practice record.

## API Spine classification

Admission changes authority state, so every future change is a REST/OpenAPI
command. Candidate operations are:

- `prepareAppointmentCheckInAdmission`;
- `activateAppointmentCheckInAdmission`;
- `suspendAppointmentCheckInAdmission`;
- `withdrawAppointmentCheckInAdmission`; and
- `engageAppointmentCheckInGlobalKillSwitch`.

They are architecture identifiers only. No endpoint or manifest is added here.
Each future command requires a current authenticated human with a separate
check-in-admission operator role, server-owned practice and environment scope,
correlation, idempotency bound to the complete request digest, optimistic
record/generation version, closed reason, freshness, append-only audit and a
bounded patient-free receipt. The authority source is a full lowercase
40-character Git object resolved by the shared guard; a seven-character
abbreviation does not satisfy the type.

Unknown commit yields no success. The caller must read back by the server-owned
command and idempotency identity. Proving that behavior with the future
ordinary runtime role remains an operational-evidence gate.

REST or GraphQL may later expose read-only posture. GraphQL cannot prepare,
activate, suspend, withdraw, engage or clear. Async events and metrics are
observations only and cannot become authority.

## Operational evidence still required

An `active` record is invalid without all of:

- ordinary runtime role proof showing non-owner, `NOBYPASSRLS`, exact-tenant
  access and cross-tenant denial;
- pre-commit rollback, commit-uncertainty no-success, bounded readback and
  disable-only rollback drills; and
- exact environment manifest, secret/key-reference, rotation and break-glass
  posture.

Each artifact is immutable, SHA-256 bound, tied to the exact environment and
snapshot generation, fresh, independently verified and bound to a resolved
full 40-character Git object. Authored-synthetic testing cannot substitute for
ordinary operational proof.

## Non-PHI observability

The exact five metric families are:

| Metric | Labels |
|---|---|
| `emr4_check_in_admission_decisions_total` | environment, lane, outcome, closed reason code |
| `emr4_check_in_admission_snapshot_age_seconds` | environment |
| `emr4_check_in_admission_kill_switch` | environment |
| `emr4_check_in_unknown_commit_total` | environment |
| `emr4_check_in_control_commands_total` | environment, closed operation, closed outcome |

All label domains are closed, low-cardinality enums. No practice, appointment,
patient, practitioner, actor, user, correlation, idempotency, command, record,
evidence or token identifier is permitted. Free text and request/response
bodies are forbidden. The attributable append-only control audit is an
authority record and is not copied into metrics.

Critical alerts cover an engaged kill switch, invalid/stale snapshot, any
unknown commit, rejected active record, control-audit failure and rollback
failure. Alerts carry no identifiers and perform no automatic control action,
retry, activation, rollback or switch change.

## Clockwork and DeepSeek broker relationship

This contract is one typed reading rather than a collection of hand-copied
facts. The deterministic validator derives the architecture evidence and tests
the whole reading. Full Git object shape is a machine invariant, which removes
the need to remember whether an abbreviation is acceptable at each write.

The accepted Ariadne journal and DeepSeek broker coupling remains a shadow
candidate. A later adoption could bind an architecture-review WorkOrder to the
contract digest and continue the same ordered causal clock. That would improve
traceability, but it would confer neither check-in command authority nor
admission activation authority on DeepSeek. This tranche performs no occupied
provider call and retires no current control.

## What this architecture proves

It closes the three design gaps identified by the readiness review with one
fail-closed contract. It does not close the three operational-evidence gaps.
It does not create an ordinary record, enable a practice, edit product or API
source, call a route or database, move a waiting area, expose patient data,
deploy, release, rebuild Pages, adopt the clockwork live or move protected
refs.

The narrow successor is a provider-free unmounted kernel rehearsal. It may
implement only the pure evaluator and typed control-command protocol with zero
active records. Any product mounting or ordinary enablement remains a later,
separately authorised gate.
