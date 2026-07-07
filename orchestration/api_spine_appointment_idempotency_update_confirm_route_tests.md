# API Spine Update-Confirm Idempotency Route Tests

| Item | Value |
|---|---|
| Sprint | 140 |
| Programme | Programme 2G / EMR4 API Spine |
| Date | 2026-07-07 |
| Status | Sprint 141 wiring completed; update-confirm route tests executable |
| Steward posture | Define deterministic update-confirm idempotency route tests before enabling HTTP `Idempotency-Key` |

## Source Pass

Reviewed sources:

- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/api_spine_appointment_idempotency_update_confirm_preflight.md`
- `orchestration/agent_inbox/codex/review-deepseek-sprint139-update-confirm-idempotency-preflight.md`
- `orchestration/agent_inbox/codex/review-deepseek-sprint140-update-confirm-idempotency-route-contract.md`
- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `app/services/appointment_idempotency.py`
- `tests/test_appointment_update_proposal.py`
- `tests/test_api_spine_status_confirm_idempotency_route_contract.py`

## Route Under Test

- route: `POST /api/v1/appointments/proposals/update/confirm`;
- handler: `confirm_update_proposal_route`;
- helper: `confirm_update_proposal`;
- typed body: `BernieUpdateProposalConfirmationIn`;
- canonical operation id: `confirmAppointmentUpdateProposal`;
- proposed route family: `update-confirm`.

Sprint 140 created the guarded route-test contract only. Sprint 141 consumed it
and wired `Idempotency-Key` enforcement for `update-confirm` only.

## Explicitly Out Of Scope

Do not wire beyond the future approved `update-confirm` surface:

- delete-confirm;
- raw compatibility `PUT /api/v1/appointments/{appointment_id}`;
- proposal-only routes such as `POST /api/v1/appointments/proposals/update/{id}`;
- slot-search or Bernie session routes;
- provider calls;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG;
- broad historical diary trove mining.

## Future Behavior Matrix

The executable route-test contract covers:

1. missing `Idempotency-Key` returns a fail-closed error before ledger,
   appointment, or audit mutation;
2. invalid update confirmation payload does not create a ledger row;
3. first confirmed update writes exactly one appointment update, one
   `AppointmentAuditAction.update` row, and one completed ledger row;
4. same-key/same-body replay returns the stored response without a second
   appointment update, audit row, helper call, or revalidation pass;
5. same-key/different-body returns `409 idempotency_key_conflict` without
   appointment or audit mutation;
6. active `in_progress` returns `409 idempotency_key_in_progress`;
7. stale `in_progress` returns `409 idempotency_key_stale_in_progress`;
8. `failed_transient` returns `503 idempotency_key_failed_transient`;
9. `Idempotency-Key` does not bypass `confirmed=true`, signed confirmation
   evidence, `update_proposal_freshness_id`, or update revalidation;
10. blocked revalidation after a started claim rolls back or removes the claim;
11. full validated confirmation-body hashing remains consistent with staff
   create-confirm, Bernie create-confirm, and status-confirm unless a future
   versioned cross-route canonicalization change is explicitly approved;
12. update-confirm remains scoped away from delete-confirm, raw compatibility
   writes, and proposal-only routes.
13. empty or whitespace-only `Idempotency-Key` returns
    `400 idempotency_key_required`;
14. same-key/same-effective-update but different `confirmed_warnings` conflicts
    because `confirmed_warnings` is semantic request content;
15. same-key replay after an intervening raw update returns the stored response
    verbatim without revalidation;
16. concurrent different keys on the same appointment remain appointment-write
    concurrency, not idempotency-key protection.

## Update-Specific Gotchas

`update-confirm` is not the same as status-confirm. It has a wider revalidation
and helper boundary:

- `confirm_update_proposal_route` currently delegates directly to
  `confirm_update_proposal`;
- `confirm_update_proposal` re-runs `propose_update_appointment()` before
  writing;
- replay must return at the route wrapper before that revalidation step, so a
  valid retry cannot be blocked by a later diary conflict or freshness change;
- started-claim business or revalidation blocks must use `db.rollback()`,
  matching status-confirm, unless a future reviewed policy makes blocked update
  confirmations replayable;
- `_apply_appointment_update()` currently commits internally, so Sprint 141
  wiring must add a scoped `commit=False` path or equivalent proof before
  completing the idempotency ledger;
- raw `PUT /api/v1/appointments/{appointment_id}` must keep default
  `_apply_appointment_update()` commit behavior and must not gain
  `Idempotency-Key` semantics;
- `_UPDATE_CONFIRM_METADATA_FIELDS` is signed-evidence payload shaping only; it
  must not become the idempotency request-body canonicalizer;
- update writes may affect date, time, duration, practitioner, appointment
  type, location, patient/provisional patient, reason, and notes.

## Canonicalization Boundary

Use full validated confirmation-body hashing:

`request_body=body.model_dump(mode="json")`

That means `signed_confirmation_evidence`, `update_proposal_freshness_id`,
`turn_ref`, `session_binding`, and `confirmed_warnings` are part of the
idempotency request body. A same-key retry with the same effective update but
different confirmation evidence or warning acknowledgements must fail closed as
`409 idempotency_key_conflict` unless a future versioned cross-route
canonicalization change is explicitly approved.

## Smallest Next Alignment Slice

Recommended Sprint 142:

**Delete-confirm idempotency preflight.**

Choose the safest delete-confirm ordering and route-test shape before touching
the destructive soft-cancel path. Keep raw/proposal-only/provider/GraphQL/H15/
memory/trove gates closed.
