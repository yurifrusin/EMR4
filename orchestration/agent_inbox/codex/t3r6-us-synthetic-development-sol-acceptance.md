# T3R6 US Synthetic-Development Policy - Sol Acceptance

Date: 2026-07-18

Decision: `accepted_policy_scheduled_not_call_ready`

Sol accepts the environment-tiered policy and deterministic report hash
`sha256:7f3aac1d92a4200221c0b41bc70f496de4639cad93ff413cd79ef04d6a61f996`.

The accepted material distinction is that synthetic development residency and
production/PII residency are separate trust zones. The US development path is
authorized from 2026-10-16. Any production or PII path remains Sydney-gated
and requires a fresh review no earlier than 2027.

Gemini 3.5 Flash satisfies the documented US model/location/runway criterion.
It does not satisfy the whole invocation gate: Vertex enablement, billing and
cost acceptance, prediction-only IAM, explicit location and fallback controls,
audit/logging/retention evidence, disabled grounding/tools/cache, and a hard
application kill switch are not yet verified.

The gate correctly never authorizes a call, PII, production, runtime wiring,
API/database/UI work, appointments, confirmations, deployment, release, or
write authority. Protected holdouts, historical diary material, external
corpora, patient/practice information, and raw provider material remain closed.

No external worker was dispatched because this is a tightly coupled user-
decision and residency-policy contract. Sol owns the boundary and direct
verification.
