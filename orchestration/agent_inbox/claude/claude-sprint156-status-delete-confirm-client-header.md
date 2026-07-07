# Sprint 156 - Status/Delete Confirm Client Headers

## Request

Review the bounded Sprint 156 implementation target: add Diary client HTTP
`Idempotency-Key` headers to status-confirm and delete-confirm calls only.

## Context

- Sprint 155 wired staff create-confirm and Bernie review create-confirm-Bernie
  client headers.
- Remaining already-enforced confirm client gaps include update-confirm,
  status-confirm, delete-confirm, and Bernie tool-intent confirm.
- Status/delete have dedicated frontend helpers:
  `applySignedStatusProposal` and `applySignedDeleteProposal`.

## Questions

1. Should status-confirm and delete-confirm use object-scoped stable confirm
   keys on the proposal object?
2. What retry/lifecycle risk should tests guard?
3. Which call sites must remain deferred?
4. What closed gates must remain closed?

## Boundaries

No backend route behavior, OpenAPI schema, ledger semantics, raw compatibility
writes, proposal-only backend binding, update-confirm wiring, Bernie tool-intent
confirm wiring, providers, GraphQL mutations, H15/H-series runtime imports,
memory/RAG/GraphRAG, or strict `minLength: 8` runtime enforcement.
