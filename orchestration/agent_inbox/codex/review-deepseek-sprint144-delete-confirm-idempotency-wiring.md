# DeepSeek Review - Sprint 144 Delete-Confirm Idempotency Wiring

| Item | Value |
|---|---|
| Sprint | 144 |
| Lane | DeepSeek worker |
| Date | 2026-07-07 |
| Status | Integrated into Ariadne wiring |

## Verdict

Proceed with narrow `delete-confirm` idempotency wiring only. The change should
mirror the existing status/update-confirm pattern and keep raw/proposal-only
families out of scope.

## Key Findings Integrated

- Normalize `Idempotency-Key`, claim the appointment command ledger, and handle
  replay/conflict/in-progress/stale/failed decisions before delete-confirm
  block checks or mutation.
- Add a scoped `commit=False` path to `_apply_appointment_delete()`, defaulting
  to `commit=True` so raw `DELETE /api/v1/appointments/{appointment_id}` keeps
  its existing behavior.
- Roll back started claims on blocked confirmation paths, including
  `confirmed=false`, signed-evidence failures, stale freshness, waiting-area
  mismatch, already-cancelled appointments, and missing appointments.
- Return completed replays from stored ledger response JSON before rerunning
  destructive soft-cancel checks.
- Treat the full validated `AppointmentDeleteProposalConfirmationIn`, including
  `confirmed_warnings` and nested `delete_proposal`, as the conflict hash
  surface.

## Gates Preserved

No raw delete idempotency, proposal-only delete idempotency, provider calls,
GraphQL mutation, H15/H-series runtime import, memory/RAG/GraphRAG, external
patient client, runtime FGA client, or broad historical diary trove behavior was
requested or approved.
