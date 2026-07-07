# API Spine Update-Confirm Idempotency Preflight

| Item | Value |
|---|---|
| Sprint | 139 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Preflight/review only; no route behavior changed |
| Steward posture | Choose the next confirmation family after status-confirm wiring before widening HTTP `Idempotency-Key` enforcement |

## Source Pass

Reviewed sources:

- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/api_spine_appointment_idempotency_status_confirm_route_tests.md`
- `orchestration/agent_inbox/codex/review-deepseek-sprint138-status-confirm-canonicalization.md`
- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `app/services/appointment_idempotency.py`
- `tests/test_appointment_update_proposal.py`
- `tests/test_appointment_status_mutations.py`
- `tests/test_appointment_audit.py`
- `tests/test_reason_code_backend.py`
- `orchestration/agent_inbox/codex/review-deepseek-sprint139-update-confirm-idempotency-preflight.md`

## Candidate Family Decision

The next narrow confirmation family should be:

- route: `POST /api/v1/appointments/proposals/update/confirm`;
- handler: `confirm_update_proposal_route`;
- implementation helper: `confirm_update_proposal`;
- typed body: `BernieUpdateProposalConfirmationIn`;
- canonical operation id: `confirmAppointmentUpdateProposal`;
- proposed route family label: `update-confirm`;
- writes today: one existing appointment row update plus one
  `AppointmentAuditAction.update` audit row.

`update-confirm` should come before `delete-confirm` because it is reversible
and exercises the next important non-create command pattern without opening the
destructive soft-cancel path. It is more complex than delete-confirm in two
ways: it re-runs `propose_update_appointment()` before writing, and it currently
delegates to `_apply_appointment_update()`, which commits internally. Those are
exactly the boundaries Sprint 140 should test before route wiring.

DeepSeek's Sprint 139 read-only review independently affirmed this family
order. It noted that delete-confirm would be simpler to wire, but update-confirm
is the safer next risk-order step because it exercises revalidation before the
destructive soft-cancel path.

## Candidate Comparison

| Family | Route | Decision | Rationale |
|---|---|---|---|
| Update confirm | `POST /api/v1/appointments/proposals/update/confirm` | Choose for next route-test contract | Reversible existing-row mutation, signed evidence, freshness, revalidation, conflict checks, one update audit row |
| Delete confirm | `POST /api/v1/appointments/proposals/delete-confirm` | Defer | Soft-cancels appointment, clears waiting area, persists cancellation/status reason evidence, and carries more destructive workflow semantics |

## Do Not Wire Yet

Do not enforce HTTP `Idempotency-Key` on `update-confirm` in Sprint 139. Do not
wire delete-confirm, raw compatibility PUT/PATCH/DELETE routes, proposal-only
routes, slot-search routes, Bernie session routes, providers, GraphQL
mutations, memory/RAG/GraphRAG, H15/H-series runtime imports, external patient
clients, runtime FGA clients, or broad historical diary trove material.

## Extra Boundary Compared With Status-Confirm

Status-confirm is self-contained after Sprint 138. Update-confirm has a helper
boundary and a wider revalidation window:

1. `confirm_update_proposal_route` delegates to `confirm_update_proposal()`;
2. `confirm_update_proposal()` checks `confirmed=true`, proposal intent/safety,
   signed evidence, and `update_proposal_freshness_id`;
3. it re-runs `propose_update_appointment()` before writing;
4. `_apply_appointment_update()` currently commits internally;
5. update changes can affect date, time, duration, practitioner, location,
   patient/provisional patient, reason, and notes.

Sprint 140 wiring should not complete the appointment/audit transaction before
completing the idempotency ledger. The expected implementation shape mirrors
status-confirm: add a scoped `commit=False` path to `_apply_appointment_update`,
apply the update and audit row, complete the ledger, then commit once.

## Proposed Claim Order

1. authenticate and authorize actor/practice;
2. require and normalize HTTP `Idempotency-Key`;
3. validate `BernieUpdateProposalConfirmationIn`;
4. canonicalize the validated body using `model_dump(mode="json")`;
5. claim the appointment command ledger with operation id
   `confirmAppointmentUpdateProposal` and route family `update-confirm`;
6. return replay/conflict/in-progress/stale/failed-transient decisions before
   confirmation checks, signed evidence, freshness checks, revalidation,
   appointment mutation, or audit write;
7. run existing `confirmed=true`, proposal-safety, signed-evidence, freshness,
   entity, and revalidation checks;
8. if blocked after the claim, roll back or remove the claim unless a future
   reviewed policy makes blocked update confirmations replayable;
9. on confirmed write, apply the update and audit row without an early commit,
   complete the ledger with the final response body and target appointment id,
   then commit once;
10. on same-key replay, return the stored response without re-running
    revalidation, changing the appointment again, or adding another audit row.

## Required Route-Test Contract

Recommended Sprint 140 should add guarded or executable tests for:

- missing `Idempotency-Key` blocks before ledger, appointment, or audit mutation;
- invalid update confirmation payload does not create a ledger row;
- first confirmed update writes exactly one appointment update, one audit row,
  and one completed ledger row;
- same-key/same-body replay returns the stored response without a second audit
  row or repeated update;
- same-key/different-body returns `409 idempotency_key_conflict` without an
  appointment or audit mutation;
- active `in_progress`, stale `in_progress`, and `failed_transient` rows fail
  closed without appointment or audit mutation;
- `Idempotency-Key` does not bypass `confirmed=true`, signed confirmation
  evidence, `update_proposal_freshness_id`, or update revalidation;
- blocked revalidation after a started claim rolls back or removes the claim;
- full validated confirmation-body hashing remains consistent with create and
  status-confirm unless a future versioned cross-route canonicalization change
  is explicitly approved;
- update-confirm idempotency remains scoped away from delete-confirm, raw
  compatibility writes, and proposal-only routes.

## Gates Still Closed

This preflight does not open:

- live providers;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- broad historical diary trove mining;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- model-to-database writes.

## Smallest Next Alignment Slice

Recommended Sprint 140:

**Update-confirm idempotency route-test contract.**

Add the guarded route-test contract for
`POST /api/v1/appointments/proposals/update/confirm` before enforcing HTTP
`Idempotency-Key` on that route.
