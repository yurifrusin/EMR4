# review-deepseek-sprint148-create-proposal-idempotency-route-contract

| Item | Value |
|---|---|
| Source Task | Sprint 148 create-proposal idempotency route-test contract review |
| Reviewer | DeepSeek worker lane |
| Status | Integrated |

## Review Request

DeepSeek was asked to review the Sprint 148 scope:

- `POST /api/v1/appointments/proposals/create`;
- `propose_create_appointment`;
- proposal-only idempotency as client discipline, not confirmation-write replay;
- no runtime route wiring;
- raw compatibility, provider, GraphQL, H15/H-series, memory/RAG/GraphRAG, and
  historical diary trove gates closed.

## Local Closeout Posture

Local Sprint 148 verification treats this as a guarded route-test contract only.

## DeepSeek Verdict

DeepSeek accepted the contract as sound and appropriately scoped for closeout,
with no critical barrier to a contract-only sprint. It recommended:

- adding an explicit dynamic guard that create-proposal calls do not create
  `AppointmentCommandIdempotency` rows;
- recording the pending same-key/different-body/replay model options for
  Sprint 149;
- making clear that future skipped tests should become DB-backed route
  integration tests when enabled;
- checking the H37/H38 static route contract remains consistent with the
  no-wiring guard.

## Integrated Response

Sprint 148 now includes the idempotency-ledger no-side-effect assertion in
`tests/test_appointment_proposals.py`, records the pending replay-model
decision options in the contract document, links future tests to DB-backed
route integration, and adds static H37/H38 alignment guards to the Sprint 148
contract suite.
