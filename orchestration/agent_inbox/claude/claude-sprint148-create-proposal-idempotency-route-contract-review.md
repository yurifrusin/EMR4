# Claude Sprint 148 Create-Proposal Idempotency Route-Test Contract Review Packet

| Item | Value |
|---|---|
| Sprint | 148 |
| Lane | Claude review packet |
| Status | Queued for bounded review |

## Review Target

Review:

- `orchestration/api_spine_appointment_idempotency_create_proposal_route_tests.md`
- `tests/test_api_spine_create_proposal_idempotency_route_contract.py`

## Acceptance Questions

1. Does the contract keep create-proposal idempotency as proposal-specific
   client discipline rather than confirmation-write replay authority?
2. Are the skipped future behavior tests sufficient before any route wiring?
3. Are raw compatibility, provider, GraphQL, H15/H-series, memory/RAG/GraphRAG,
   and historical diary trove gates still closed?

## Expected Current Answer

Accept as a no-runtime-change route-test contract. Do not wire enforcement until
the create-proposal replay model is explicitly chosen.
