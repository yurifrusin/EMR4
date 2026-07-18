# Bernie Stage 1 Acceptance Plan — Sol Review

Date: 2026-07-18

Decision: **accepted_for_execution**

Reviewed candidate:
`docs/bernie-stage1-provider-free-supervised-booking-acceptance-plan.md`

Candidate SHA-256:
`1cb02436b161167ac4b9f0fb9d33d33a9ee9657a7b9eb2a9205188d1917cbbf3`

Yuri approval: exact candidate approved and frozen on 2026-07-18

Frozen plan SHA-256:
`f4a149e0792cabf1beba3f0344e3379fdd3f897d1720bdc3b5abefbfdee5790c`

Pre-plan Ariadne receipt:
`orchestration/agent_inbox/codex/bernie-stage1-acceptance-plan-preplan-receipt.json`

Receipt SHA-256:
`b0e061f9a7a8bf249cedde754f2ef02f39b55308227235b6346fd655d1af30c1`

## Review findings

- The candidate implements Yuri's accepted strategic direction: pause provider
  work and prove the existing supervised-booking product vertical locally.
- The happy-path acceptance claim requires a real, non-intercepted Diary →
  FastAPI → isolated PostgreSQL run. Existing route-intercepted browser and
  in-process backend evidence remain supporting evidence only.
- The existing REST `confirm-bernie` command is the sole product mutation.
  GraphQL, the model/fake provider, and the Diary client receive no write or
  confirmation authority.
- Proposal, explicit staff confirmation, backend revalidation, exactly-one
  appointment/audit/idempotency result, typed receipt, and Diary readback are
  all independently gated.
- Ambiguity, no-slot, stale/conflict, exact duplicate, and replay behavior are
  included with no-extra-write acceptance boundaries.
- Provider calls, cloud setup/mutation, PII/production, protected evidence,
  external corpora, new synthetic/holdout versions, migrations, durable session
  work, broad redesign, deployment, and release remain closed.
- The standing release instruction can be run deterministically by pinning the
  existing Diary/session reference date to a future rostered weekday. No clock
  override is needed.
- The plan begins with evidence-only readiness and unchanged-product execution.
  It does not manufacture a correction sprint if the current product passes.
- The plan defines exact evidence classes, acceptance decisions, stop rules,
  bounded recovery, reasoning allocation, and the handoff required before
  dispatch.

## API Spine assessment

The plan is compatible with the current API Spine boundary:

- read/context and proposal operations remain non-mutating;
- the existing authenticated REST command owns the appointment mutation;
- confirmation evidence and idempotency are required at the mutation boundary;
- the backend revalidates authoritative state before writing;
- a typed receipt and audit evidence are required; and
- provider abstraction and GraphQL mutation are out of scope.

## Execution handoff

Yuri approved the exact candidate contract. The plan is frozen and the Current
Baton names it as active acceptance. Execution must start in a fresh Sol/high
context with mandatory rehydration and a fresh pre-dispatch receipt, then begin
at read-only Tranche A. No implementation, provider work, cloud mutation, or
product write is implied by this planning acceptance itself.
