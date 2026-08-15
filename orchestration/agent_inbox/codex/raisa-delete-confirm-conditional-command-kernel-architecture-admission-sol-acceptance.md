# Sol acceptance — provider-free unmounted delete-confirm conditional-command kernel

Date: 2026-08-15

Timestamp: 2026-08-15T12:56:41+10:00 (Australia/Brisbane)

Decision: accept

Accepted reviewed source: `356b28a1750e7a7b379406e864f2a3501606938a`

Result: `raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_pass`

## Acceptance reasoning

The recovered candidate satisfies every frozen acceptance item. Its closed
schema, generated contract and deterministic simulator agree on exact
authority, evidence, reason, idempotency, artifact, lock-order, rollback,
replay, response-loss and readback semantics. All direct scenario and hostile
mutation checks are source-bound and fail closed.

The important destructive-command precedence is preserved: current practice
authority and target non-disclosure precede idempotency classification and
receipt disclosure; exact completed replay precedes reconstruction of
historical first-effect evidence; and a new effect requires fresh signed
evidence, explicit human confirmation and exact locked pre-state. No client,
model, event or channel assertion can confer confirmation or write authority.

The abstract practice fence is explicitly a future physical-design obligation,
not a claim that current tables already stabilize authority. The result is
therefore correctly calibrated to an unmounted authored-synthetic contract.

## Recovery finding

The DeepSeek self-pass was correctly rejected as a conceptual rather than
mechanical failure. Sol's recovery lease corrected the invalid expiry ordering,
froze the exact authority and 24-field evidence contracts, added nullable
cancellation-text success and tightened cross-artifact invariants. AER-0321
through AER-0324 preserve the workflow incidents and their controls without
rewriting worker provenance.

## Verification finding

The candidate passes 46 decisions, 15 schedules, 67 hostile mutations, 24
focused protocol tests, 212 combined cancellation/API tests, 245 register
tests and the 196-test canonical fast profile. Gemini 3.6 Flash/high passed all
15 independent challenges and left the exact candidate clean and unchanged.

## API Spine finding

The work preserves the accepted mixed spine: cancellation remains one explicit
REST/OpenAPI command family; GraphQL remains read-only; events remain
acceleration hints; signed confirmation, current authority, idempotency, audit
and receipt completion remain backend-owned. The architecture introduces no
second mutation path.

## Authority finding

Acceptance opens no runtime or product authority. PostgreSQL representation,
real locking/concurrency, mounted route convergence, Reception One UI,
external adapters, patient identity/delegation, provider use, production and
release remain closed.

The next executable stage is the provider-free unmounted delete-confirm
physical representability review. Standing uninterrupted-development authority
applies and no user-attention fork is present.

