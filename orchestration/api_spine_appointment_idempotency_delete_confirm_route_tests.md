# API Spine Delete-Confirm Idempotency Route Tests

| Item | Value |
|---|---|
| Sprint | 143 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Guarded route-test contract only; no route behavior changed |
| Steward posture | Define deterministic delete-confirm idempotency route tests before enabling HTTP `Idempotency-Key` on the destructive soft-cancel path |

## Source Pass

Reviewed sources:

- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/api_spine_appointment_idempotency_delete_confirm_preflight.md`
- `orchestration/agent_inbox/codex/review-deepseek-sprint142-delete-confirm-idempotency-preflight.md`
- `orchestration/agent_inbox/codex/review-deepseek-sprint143-delete-confirm-idempotency-route-contract.md`
- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `app/services/appointment_idempotency.py`
- `tests/test_appointment_status_mutations.py`
- `tests/test_appointment_audit.py`
- `tests/test_reason_code_backend.py`

## Route Under Test

- route: `POST /api/v1/appointments/proposals/delete-confirm`;
- handler: `confirm_delete_proposal_route`;
- helper: `_apply_appointment_delete`;
- typed body: `AppointmentDeleteProposalConfirmationIn`;
- canonical operation id: `confirmAppointmentDeleteProposal`;
- proposed route family: `delete-confirm`.

Sprint 143 creates the guarded route-test contract only. It must not wire
`Idempotency-Key` enforcement or change delete-confirm behavior.

## Explicitly Out Of Scope

Do not wire beyond the future approved `delete-confirm` surface:

- raw compatibility `DELETE /api/v1/appointments/{appointment_id}`;
- proposal-only routes such as `POST /api/v1/appointments/proposals/delete/{id}`;
- already-wired create/status/update confirmation routes;
- slot-search or Bernie session routes;
- provider calls;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG;
- broad historical diary trove mining.

## Future Behavior Matrix

When Sprint 144 wires delete-confirm idempotency, the route-test contract should
cover:

1. missing `Idempotency-Key` returns a fail-closed error before ledger,
   appointment, or audit mutation;
2. blank/whitespace `Idempotency-Key` is treated as missing;
3. invalid delete confirmation payload does not create a ledger row;
4. first confirmed delete writes exactly one soft-cancel, one
   `AppointmentAuditAction.delete` row, one completed ledger row, clears
   `waiting_area_id`, and persists cancellation/status reason evidence;
5. same-key/same-body replay returns the stored response without a second audit
   row or repeated soft-cancel side effect;
6. same-key/same-body replay after an intervening raw delete returns the stored
   response without re-running delete checks;
7. same-key/different-body returns `409 idempotency_key_conflict` without
   appointment or audit mutation;
8. active `in_progress` returns `409 idempotency_key_in_progress`;
9. stale `in_progress` returns `409 idempotency_key_stale_in_progress`;
10. `failed_transient` returns `503 idempotency_key_failed_transient`;
11. `Idempotency-Key` does not bypass `confirmed=true`, signed confirmation
    evidence, `delete_proposal_freshness_id`, or waiting-area state checks;
12. blocked checks after a started claim call `db.rollback()` before returning
    the blocked response;
13. full validated confirmation-body hashing remains consistent with create,
    status, and update-confirm unless a future versioned cross-route
    canonicalization change is explicitly approved;
14. raw `DELETE`, proposal-only delete routes, providers, GraphQL, H15,
    memory/RAG/GraphRAG, and broad trove gates remain closed.
15. already-cancelled and non-existent appointment confirmations do not create
    ledger or audit rows;
16. same-key/different `confirmed_warnings` and same-key/different nested
    `delete_proposal` bodies conflict;
17. replay preserves stored merged `confirmed_warnings`;
18. invalid `status_reason_code`, missing signed evidence, and both
    waiting-area mismatch directions block without mutation;
19. concurrent different keys on the same appointment are appointment-write
    concurrency, not idempotency protection.

## Delete-Specific Gotchas

- `_apply_appointment_delete()` currently commits internally, so Sprint 144
  wiring must add a scoped `commit=False` path or equivalent proof before
  completing the idempotency ledger.
- Raw `DELETE /api/v1/appointments/{appointment_id}` must keep default
  `_apply_appointment_delete()` commit behavior and must not gain
  `Idempotency-Key` semantics.
- Delete-confirm does not re-run `propose_delete_appointment()` today; freshness
  and waiting-area-state checks are the confirm-time revalidation boundary.
- Replay must return before those destructive checks can run again.
- Soft-cancel clears waiting-area state and stores cancellation/status reason
  evidence, so duplicate audit rows or repeated clearing are release-blocking
  replay bugs.
- The route merges proposal warning codes with `body.confirmed_warnings`; replay
  must return the stored merged response rather than recomputing warnings.
- Invalid `status_reason_code` must fail before any ledger/audit mutation.
- Waiting-area state is a confirm-time safety invariant in both directions:
  `clears_waiting_area=True` with no waiting area and `clears_waiting_area=False`
  with a waiting area must both block.

## Smallest Next Alignment Slice

Recommended Sprint 144:

**Delete-confirm idempotency route wiring.**

Wire only `POST /api/v1/appointments/proposals/delete-confirm` with HTTP
`Idempotency-Key`, full validated-body hashing, started-claim rollback on
blocks, and one transaction covering soft-cancel, audit row, ledger completion,
and commit. Keep raw/proposal-only/provider/GraphQL/H15/memory/trove gates
closed.
