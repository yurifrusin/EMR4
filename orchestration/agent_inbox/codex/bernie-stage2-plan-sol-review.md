# Bernie Stage 2 Plan — Sol Extra High Review

Date: 2026-07-19

Decision: `approved_scope_frozen_for_implementation`

Sol accepts
`docs/bernie-stage2-durable-authority-recovery-security-plan.md` as the exact
implementation and acceptance contract for Yuri's approved Stage 2 decision.

The plan is bounded to the existing local synthetic appointment-create
vertical. It resolves the disclosed Stage 1 gaps with additive durable session
and event storage, ledger-first atomic idempotency, reciprocal command/audit
correlation, append-only audit enforcement, practice-scoped RLS evidence,
restart/concurrency/rollback/retry tests, JWT practice consistency, and the
approved 24-hour/30-day development retention policy.

The review specifically rejects any inference of provider, protected,
historical, PII, production, deployment, release, additional appointment
action, GraphQL mutation, broad platform migration, autonomous confirmation,
or Stage 3 authority. It also makes no production encryption, runtime-role, or
retention claim.

The exact focused pre-change regression population passed 73 tests. Alembic and
the development database are aligned at `l1m2n3o4p5q6`; all five protected Git
refs were aligned at `8cadc64c56d014a7f3fbd70d82ac5c041e63fed8` before the
plan freeze.

A filename-only protected metadata enumeration incident is preserved and
contained. No protected content was opened, hashed, run, or used. Later work
must use only explicit Stage 2 source and test paths.

Sol remains the sole implementation, acceptance, recovery, and integration
owner. The database lifecycle is serial and tightly coupled, so no worker is
dispatched. Every acceptance gate is fail-closed; a failed gate returns
`revision_required` and cannot be overridden within this authority.
