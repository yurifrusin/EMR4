# API Spine Appointment Proposal-Only Idempotency Preflight

| Item | Value |
|---|---|
| Sprint | 147 |
| Programme | Programme 2G / EMR4 API Spine |
| Steward posture | Policy/preflight only before any proposal-route header enforcement |
| Runtime posture | No route behavior changed |

## Decision

After Sprint 146, all proposal-confirm appointment mutation families have
route-level idempotency integration coverage. The next expansion surface should
be the proposal-only appointment routes, not raw compatibility writes.

Rationale:

- proposal routes are canonical OpenAPI command-plane routes and the Sprint 101
  draft already requires `Idempotency-Key` on them;
- proposal routes are non-mutating, so they are safer than raw compatibility
  writes for the next client-discipline step;
- proposal idempotency must not create write authority or durable appointment
  replay authority;
- raw compatibility writes still need a separate deprecation/compatibility
  policy before behavior changes.

## Proposal-Only Scope

Future proposal-only idempotency route-test work may cover these current
FastAPI routes:

| Proposal family | Route | Handler | OpenAPI operation |
|---|---|---|---|
| Create proposal | `POST /api/v1/appointments/proposals/create` | `propose_create_appointment` | `proposeAppointmentCreate` |
| Update proposal | `POST /api/v1/appointments/proposals/update/{appointment_id}` | `propose_update_appointment` | `proposeAppointmentUpdate` |
| Status proposal | `POST /api/v1/appointments/proposals/status/{appointment_id}` | `propose_status_update` | `proposeAppointmentStatus` |
| Waiting-area proposal | `POST /api/v1/appointments/proposals/waiting-area/{appointment_id}` | `propose_waiting_area_update` | `proposeAppointmentStatus` |
| Delete proposal | `POST /api/v1/appointments/proposals/delete/{appointment_id}` | `propose_delete_appointment` | `proposeAppointmentDelete` |

Slot-search, Bernie interpreter/supervised-booking, no-slot selection, and
Bernie session routes remain out of scope unless a later policy sprint
explicitly reclassifies them.

## Proposed Future Semantics

Proposal-only idempotency must have a different contract from confirmation
idempotency. Confirmation routes replay a committed write response from the
durable appointment command ledger. Proposal routes produce fresh/evidence
envelopes and do not own a write. They must not take on confirmation-grade
write replay authority by accident.

The next proposal-only implementation sprint should start with route-test
contracts, not route wiring. Those tests should require:

1. missing `Idempotency-Key` fails closed once enforcement is intentionally
   enabled for that proposal route;
2. blank or whitespace-only `Idempotency-Key` is treated as missing;
3. valid proposal requests continue to produce proposal envelopes and
   confirmation payloads without appointment, audit, or confirmation-ledger
   writes;
4. repeated proposal submissions with the same key and same body do not gain
   confirmation/write authority and do not reserve slots;
5. same-key/different-body behavior is either deterministic no-ledger
   re-evaluation or a short-retention proposal conflict, but this must be
   chosen explicitly before wiring;
6. proposal-only idempotency must not weaken signed confirmation evidence,
   freshness, warning acknowledgement, or later confirmation-route ledger
   checks.

## Design Questions Before Wiring

The route-test contract should explicitly answer these before enforcement:

| Question | Sprint 147 preflight posture |
|---|---|
| Client readiness | Do not enforce until known clients can send `Idempotency-Key` deliberately; route tests may define the future contract first. |
| Replay response | Do not assume confirmation-style stored response replay. Proposal replay may be deterministic re-evaluation, a short-retention proposal marker, or stored proposal-envelope replay, but it must not grant write authority. |
| Same-key/different-body conflict | Choose explicitly per proposal route before wiring. A `409` conflict is acceptable only if scoped to proposal client discipline, not durable appointment write replay. |
| Retention | If a proposal marker/ledger is used, retention must be short and bounded by proposal freshness/session expectations, not confirmation-write retention. |
| Operation identity | `status/{appointment_id}` and `waiting-area/{appointment_id}` share the `proposeAppointmentStatus` OpenAPI family, but route-family identity may need to preserve the status-vs-waiting-area body shape for conflict clarity. |
| Storage reuse | The confirmation ledger schema may be reusable only if proposal entries are clearly distinguished by operation/result kind and short retention; otherwise use a separate proposal marker design. |

## Current Required Guard

Sprint 147 must keep the current FastAPI proposal routes unwired:

- no `Idempotency-Key` header binding on proposal-only routes;
- no `claim_appointment_command()` or `complete_appointment_command()` calls
  from proposal-only routes;
- no appointment/audit mutation behavior changes;
- no raw compatibility route behavior changes.

## Gates Still Closed

This preflight does not open:

- raw compatibility `POST`, `PUT`, `PATCH`, or `DELETE` idempotency
  enforcement;
- slot-search reservation or replay semantics;
- Bernie interpreter/session command idempotency expansion;
- provider calls, live-provider gates, or Access AI invocation changes;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- model-to-database writes outside REST command handlers.

## Recommended Sprint 148

Add a guarded proposal-only route-test contract for the first proposal family,
preferably `POST /api/v1/appointments/proposals/create`, because it is the
lowest-risk canonical proposal route and feeds the already-wired staff
create-confirm ledger path.

Do not wire proposal-route enforcement in Sprint 148. The route-test contract
must first define proposal-specific replay/conflict/client-readiness semantics
without copying confirmation-write replay authority.
