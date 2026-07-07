# Antigravity Sprint 146 Confirmation-Family Integration Acceptance Packet

| Item | Value |
|---|---|
| Sprint | 146 |
| Lane | Antigravity acceptance packet |
| Status | Queued for bounded review |

## Product/UX Acceptance Frame

Sprint 146 is backend/API-spine proof work. It should not change the diary UI,
taskpane, receptionist copy, provider behavior, or patient-facing behavior.

## Acceptance Criteria

- The five confirmation routes keep the same visible workflow semantics.
- Retries with the same idempotency key do not create duplicate appointment,
  audit, ledger, or Bernie session-event side effects.
- Conflicting or blocked retry states fail closed with typed errors.
- Raw compatibility writes and proposal-only routes remain outside this sprint.
- No provider, GraphQL mutation, memory/RAG/GraphRAG, H15/H-series runtime, or
  historical diary trove gate is opened.

## Review Target

`tests/test_api_spine_confirmation_family_idempotency_integration.py` and the
Sprint 146 closeout notes.
