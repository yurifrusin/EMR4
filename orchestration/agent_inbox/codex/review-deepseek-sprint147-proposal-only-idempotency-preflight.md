# review-deepseek-sprint147-proposal-only-idempotency-preflight

| Item | Value |
|---|---|
| Source Task | Sprint 147 proposal-only idempotency preflight review |
| Reviewer | DeepSeek worker lane |
| Status | Integrated |

## Verdict

DeepSeek accepted proposal-only appointment idempotency as the right next
preflight before raw compatibility writes, provided Sprint 147 resolves the
different proposal contract rather than drifting into implementation.

## Key Finding

Proposal idempotency is not confirmation idempotency:

- confirmation routes replay committed write responses from the durable command
  ledger;
- proposal routes return freshness/evidence envelopes and must not gain write
  replay authority;
- same-key/different-body semantics, replay response shape, client-readiness
  signaling, retention, status/waiting-area operation identity, and storage
  reuse need explicit policy before wiring.

## Integrated Response

`orchestration/api_spine_appointment_idempotency_proposal_only_preflight.md`
now records those proposal-specific design questions and keeps Sprint 148 as a
guarded route-test-contract sprint only. Runtime route wiring, schemas,
migrations, raw compatibility policy, providers, GraphQL, H15/H-series,
memory/RAG/GraphRAG, and historical diary trove gates remain closed.
