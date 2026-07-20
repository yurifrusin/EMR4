# Reception One committed-event vertical — Sol plan review

**Reviewer:** GPT Sol Extra High
**Date:** 2026-07-21
**Decision:** `accepted_for_bounded_implementation`

## Reviewed authority

Yuri explicitly authorized the bounded event-runtime changes. The mandatory five-source rehydration passed before planning, and the implementation source is protected `master` / `handoff/current` at `be5e01d00b23ef43f7aab8b30f6dbdfa6e858c45` in an isolated clean worktree.

## Acceptance finding

`docs/bernie-reception-one-committed-event-vertical-plan.md` is sufficiently exact to freeze implementation. It adds one local `diary.appointment_rescheduled` signal to the existing signed appointment-update confirmation path. It introduces no new appointment command and requires atomic appointment/audit/idempotency/event persistence, forced practice RLS, append-only enforcement, a patient-free event schema, default-off read-only polling, deterministic client relevance and deduplication, fresh authorized Diary reads, and a quiet user-controlled cue.

The paired threat-model delta covers transaction split-brain, replay/order/expiry, cross-practice leakage, payload creep, stale-payload trust, command tunnelling, attention abuse, privacy, tampering, and correlation loss. Its controls are represented in the frozen deterministic, browser, and database gates.

## Reasoning disposition

Extra High was appropriate because this is the first committed-event runtime and required freezing new transaction, delivery, privacy, and user-visible attention semantics. The material choices are now fixed. High is sufficient for mechanical implementation, testing, evidence packaging, correction within the contract, review, and check-gated closeout unless a material fork or failed gate requires reconsideration.

## Preserved boundaries

The review does not authorize provider calls, PII, protected or historical evidence, Stage 3B, representative users, voice, external brokers, background workers, WebSockets, GraphQL mutations/subscriptions, new appointment actions, persistent preferences, production configuration, deployment, or release. A fresh Gemini veto remains required after candidate evidence and before acceptance.
