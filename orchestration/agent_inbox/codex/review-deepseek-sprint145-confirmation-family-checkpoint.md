# DeepSeek Review - Sprint 145 Confirmation-Family Checkpoint

| Item | Value |
|---|---|
| Sprint | 145 |
| Lane | DeepSeek worker |
| Date | 2026-07-07 |
| Status | Integrated into Ariadne checkpoint |

## Verdict

All five proposal-confirm appointment mutation families are now wired for route
level `Idempotency-Key` enforcement. The checkpoint should remain non-runtime
and should not open proposal-only or raw compatibility idempotency enforcement.

## Confirm Families

- Staff create-confirm: `confirmAppointmentCreateProposal` /
  `create-confirm`.
- Bernie create-confirm: `confirmAppointmentCreateProposal` /
  `create-confirm-bernie`.
- Update-confirm: `confirmAppointmentUpdateProposal` / `update-confirm`.
- Status-confirm: `confirmAppointmentStatusProposal` / `status-confirm`.
- Delete-confirm: `confirmAppointmentDeleteProposal` / `delete-confirm`.

## Integrated Guidance

- Assert the shared fail-closed map for `replay`, `conflict`, `in_progress`,
  `stale_in_progress`, and `failed_transient`.
- Preserve closed gates for live providers, runtime FGA clients, external
  patient clients, GraphQL mutations, H15/H-series runtime imports,
  memory/RAG/GraphRAG, broad historical diary trove mining, model-to-database
  writes, proposal-only idempotency, and raw compatibility write enforcement.
- Recommended next slice: route-level integration tests that exercise the
  shared replay/conflict/preclaim behavior across all five wired confirmation
  families against a real DB session.
