# DeepSeek Review - Sprint 140 Update-Confirm Idempotency Route Contract

| Item | Value |
|---|---|
| Sprint | 140 |
| Lane | DeepSeek worker |
| Date | 2026-07-07 |
| Status | Integrated into Ariadne route-test contract |

## Recommendation

Proceed with the guarded `update-confirm` route-test contract before wiring.
The route should remain unwired in Sprint 140.

## Key Findings Integrated

- Replay must short-circuit in `confirm_update_proposal_route()` before calling
  `confirm_update_proposal()` or re-running `propose_update_appointment()`.
- Idempotency belongs at the HTTP route wrapper, not inside the reusable
  `confirm_update_proposal()` helper.
- `_apply_appointment_update()` currently commits internally and needs the same
  `commit=False` pattern that Sprint 138 added for status-confirm.
- Raw `PUT /api/v1/appointments/{appointment_id}` must keep its default
  commit behavior and must not inherit update-confirm idempotency semantics.
- Started-claim business or revalidation blocks should use transaction rollback,
  matching status-confirm, rather than a separate delete/remove policy.
- Full validated confirmation-body hashing should remain the idempotency
  canonicalization rule. `_UPDATE_CONFIRM_METADATA_FIELDS` is only for signed
  evidence payload shaping and must not become the idempotency canonicalizer.
- Future tests should include empty/whitespace `Idempotency-Key`, replay after
  an intervening raw update, same effective command with different
  `confirmed_warnings`, and the advisory boundary that idempotency is key-scoped
  rather than appointment-scoped.

## Accepted Sprint 141 Wiring Shape

Sprint 141 should wire only
`POST /api/v1/appointments/proposals/update/confirm`:

1. validate `BernieUpdateProposalConfirmationIn`;
2. require and normalize HTTP `Idempotency-Key`;
3. claim the appointment command ledger with operation id
   `confirmAppointmentUpdateProposal`, route family `update-confirm`, and
   `request_body=body.model_dump(mode="json")`;
4. return replay/conflict/in-progress/stale/failed decisions before calling
   `confirm_update_proposal()`;
5. on started claims, run existing confirmation, signed-evidence, freshness, and
   revalidation checks;
6. roll back the started claim on any blocked response;
7. use `_apply_appointment_update(..., commit=False)`;
8. complete the ledger with the final response body and target appointment id;
9. commit once.

No user decision is required before Sprint 141 if this shape remains narrow and
delete/raw/proposal-only/provider/GraphQL/H15/memory/trove gates stay closed.
