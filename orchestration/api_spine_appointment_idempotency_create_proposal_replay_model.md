# API Spine Appointment Create-Proposal Replay Model Decision

| Item | Value |
|---|---|
| Sprint | 149 |
| Programme | Programme 2G / EMR4 API Spine |
| Steward posture | Replay-model decision only before route wiring |
| Runtime posture | No route behavior changed |

## Decision

For `POST /api/v1/appointments/proposals/create`, choose:

**Deterministic re-evaluation with a required `Idempotency-Key`, no proposal
ledger, and no stored proposal-envelope replay.**

This means a future wiring sprint may require syntactically valid
`Idempotency-Key` headers on create-proposal requests as client discipline, but
the backend should continue to evaluate each accepted proposal request against
current diary state and mint fresh proposal evidence.

## Accepted Semantics

| Case | Future behavior |
|---|---|
| Missing key | Fail closed with typed `idempotency_key_required` once enforcement is intentionally enabled |
| Blank/whitespace key | Treat as missing |
| Valid key + valid body | Run normal create-proposal evaluation and return a proposal envelope |
| Same key + same body | Re-evaluate current state and return a fresh proposal envelope; do not replay stale evidence |
| Same key + different body | Re-evaluate current state for the new body; do not return `409` in this deterministic model |
| Confirmation payload | Still requires staff confirmation, signed evidence, freshness, and the confirmation-route ledger |

## Rejected For This Route

### Short-Retention Proposal Marker

Rejected for the first create-proposal wiring pass because it creates a second
proposal idempotency state surface before product clients have proven they need
same-key/different-body conflict discipline. It may be reconsidered later if
client retry behavior demonstrates a concrete need.

### Stored Proposal-Envelope Replay

Rejected because proposal envelopes contain freshness and signed confirmation
evidence. Replaying a stored proposal envelope risks preserving stale evidence
or implying that proposal idempotency owns confirmation-grade replay authority.

## Required Implementation Boundary

A future create-proposal wiring sprint must:

- require and normalize `Idempotency-Key` before proposal evidence is minted;
- treat proposal idempotency-key validation as syntactic only: non-blank,
  header-supplied, and not actor/operation scoped in storage;
- use `proposeAppointmentCreate` as a route-level operation identity for
  logging/review metadata only, not as a ledger key;
- bind the key with `Header(None, alias="Idempotency-Key")` on
  `propose_create_appointment`, not in the request body and not inside
  `_build_create_appointment_proposal`;
- avoid `claim_appointment_command()` and `complete_appointment_command()` on
  the create-proposal route;
- avoid creating `AppointmentCommandIdempotency` rows from create-proposal
  calls;
- avoid appointment writes, audit writes, and slot reservations;
- keep same-key/different-body behavior as fresh re-evaluation, not `409`;
- keep the confirmation route responsible for durable replay of confirmed
  appointment writes.
- define client readiness as: all intended clients can send a non-blank
  `Idempotency-Key` header and understand that retries with the same key return
  fresh proposal evaluations, not conflicts or cached envelopes.

Deterministic re-evaluation leaves no stored proposal data to migrate. Any
future move to proposal markers or stored proposal-envelope replay must be
additive and must go through a new explicit review.

Bernie create-proposal surfaces that reuse `propose_create_appointment` or
`proposeAppointmentCreate` inherit this same deterministic re-evaluation model;
there is no separate Bernie proposal idempotency path in this decision.

## Current No-Wiring Guard

Sprint 149 does not wire the route. Current FastAPI behavior remains:

- `propose_create_appointment` has no `Idempotency-Key` header binding;
- `_build_create_appointment_proposal` has no idempotency helper call;
- dynamic proposal tests prove no appointment, audit, or idempotency-ledger row
  is created by a proposal call.

## Gates Still Closed

This decision does not open:

- create-proposal route enforcement wiring;
- update/status/waiting-area/delete proposal idempotency enforcement;
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

## Recommended Sprint 150

Wire `POST /api/v1/appointments/proposals/create` to require a syntactically
valid `Idempotency-Key` using deterministic re-evaluation semantics only. Enable
the create-proposal future behavior tests from Sprint 148 as DB-backed route
integration tests, and add same-key/same-body and same-key/different-body
cases proving fresh re-evaluation without proposal ledger rows or slot
reservation.
