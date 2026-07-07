# review-deepseek-sprint150-create-proposal-idempotency-wiring

| Item | Value |
|---|---|
| Source Task | Sprint 150 create-proposal syntactic idempotency wiring review |
| Reviewer | DeepSeek worker lane |
| Status | Integrated |

## Verdict

DeepSeek accepted the Sprint 150 scope as bounded:

- add `Idempotency-Key` header binding to `propose_create_appointment`;
- reject missing and whitespace-only keys with `400 idempotency_key_required`;
- keep `_build_create_appointment_proposal` idempotency-free;
- do not create `AppointmentCommandIdempotency` rows;
- preserve deterministic re-evaluation, including no same-key/different-body
  `409`;
- keep raw compatibility, other proposal families, providers, GraphQL,
  H15/H-series, memory/RAG/GraphRAG, and historical diary trove gates closed.

## Integrated Decisions

Sprint 150 uses a dedicated create-proposal normalization helper with a
proposal-specific error message. It deliberately accepts any non-blank key for
this first wiring pass; OpenAPI `minLength: 8` enforcement is recorded as a
future compatibility/alignment decision.

No separate Bernie proposal idempotency path was added. Any Bernie surface that
reuses the staff create-proposal route inherits the same deterministic
re-evaluation semantics.
