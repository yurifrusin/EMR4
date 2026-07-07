# review-deepseek-sprint149-create-proposal-replay-model

| Item | Value |
|---|---|
| Source Task | Sprint 149 create-proposal replay-model review |
| Reviewer | DeepSeek worker lane |
| Status | Integrated |

## Verdict

DeepSeek accepted deterministic re-evaluation as the safest default before any
create-proposal route wiring.

## Rationale

Deterministic re-evaluation avoids:

- proposal marker storage being confused with the confirmation
  `AppointmentCommandIdempotency` ledger;
- TTL and cleanup policy for proposal markers;
- `409` conflicts when staff legitimately resubmit a corrected proposal body
  with the same key;
- stale stored proposal-envelope replay of freshness and signed confirmation
  evidence.

## Integrated Criteria

The Sprint 149 decision now records:

- proposal key validation is syntactic/header-only;
- `proposeAppointmentCreate` may be used for logging/review metadata, not
  storage;
- future wiring should bind `Idempotency-Key` on `propose_create_appointment`,
  not inside the request body or proposal helper;
- client readiness means clients can send the header and expect fresh
  evaluations on retry;
- future proposal marker or stored-envelope models are additive only and
  require new explicit review;
- Bernie create-proposal reuse does not need a separate idempotency path.

All raw compatibility, provider, GraphQL, H15/H-series, memory/RAG/GraphRAG,
historical diary trove, and model-to-database gates remain closed.
