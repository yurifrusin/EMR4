# Provider-free unmounted pure route-adapter differential design

Date: 2026-08-12

Status: `frozen_unmounted_design`

## Two ingress shapes, one kernel meaning

The rehearsal uses two deliberately different input shapes. A confirm envelope
contains `principal`, `command`, `proposal_evidence`, `confirmation`,
`idempotency` and `correlation_id`. A raw envelope contains
`request_context`, `mutation`, optional `conditional_controls`, optional
`confirmation_evidence`, optional `command_identity` and `correlation_id`.

The shapes prevent an equality test from passing merely because both adapters
copied one already-canonical object. Each adapter must perform its own pure
field mapping. The server-side adapter specification supplies
`canonical_operation_id` and `route_adapter_id`; neither is accepted from an
input envelope.

## Exact gap boundary

The current raw profile includes attributable practice, actor, role, session,
purpose, target/conflict, command digest and correlation fields. It omits three
independent command controls:

- `backend_precondition_missing` means both the backend-minted precondition
  version and digest are absent;
- `confirmation_evidence_missing` means both the separate confirmation mode
  and reference are absent; and
- `idempotency_identity_missing` means both the command idempotency-key digest
  and canonicalization version are absent.

The adapter reports the sorted union of missing groups and emits no partial
candidate. Authentication, request arrival, route method, current reads,
correlation identity, event data and audit attribution cannot fill a gap.

## Differential rule

For each operation family, the complete confirm and hypothetical complete raw
profiles must produce equal values for seventeen semantic fields. The only
excluded field is `route_adapter_id`, which records honest ingress provenance
for audit. The two create-confirm aliases must also agree semantically.

The comparison does not erase provenance from a real candidate. It creates a
separate comparison projection solely for this rehearsal.

## Operation invariants

- Create uses canonical operation `confirmAppointmentCreateProposal`, a null
  appointment target and `practice -> schedule_domain -> idempotency_record`.
- Update uses `confirmAppointmentUpdateProposal`, a target plus conflict
  domain and all four locks in canonical order.
- Status uses `confirmAppointmentStatusProposal`, a target and
  `practice -> appointment -> idempotency_record`.
- Delete uses `confirmAppointmentDeleteProposal`, a target, explicit
  destructive confirmation and the same three-lock profile as status.

All eight kernel outcomes are retained as vocabulary only. The pure adapter
returns neither an outcome nor a success receipt because current authority,
source truth, idempotency records, domain invariants and transaction effects
are outside this layer.

## Safety posture

Every identifier uses the `syn-` namespace and every digest is an inert label.
The evaluator reads only the closed repository fixture and its source-bound
parent contract. It imports no application, database, HTTP, network, provider
or process module and performs no write.
