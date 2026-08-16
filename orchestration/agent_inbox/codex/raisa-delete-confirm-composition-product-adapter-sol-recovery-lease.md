# Sol recovery lease — delete-confirm composition/product adapter

Date: 2026-08-16

Timestamp: 2026-08-16T20:19:05.2199314+10:00 (Australia/Brisbane)

Status: `closed`

## Preserved worker provenance

- original advisory-pass commit:
  `d9df95874ea674420b626f5182a68a07e96e6d91`;
- sole same-lane correction commit:
  `5dd9adef40bbc54c9737d0de83b3949c9b95539a`;
- original and correction receipts remain under
  `orchestration/agent_inbox/deepseek/`; and
- Sol rejection evidence is
  `orchestration/agent_inbox/codex/raisa-delete-confirm-composition-product-adapter-worker-candidate-rejection.json`.

Neither worker decision is acceptance evidence. Both commits remain immutable.

## Recovery authority

The accepted Ariadne recovery lease permits Sol to adopt this runtime/security-
boundary source as an untrusted candidate, amend it under Sol identity, run
risk-proportional deterministic verification and require the already-planned
fresh Gemini 3.7 Flash/high veto. The worker correction budget is exhausted;
there will be no further DeepSeek correction.

## Exact Sol amendments

Sol may edit only:

- `app/services/appointment_delete_product_adapter.py`;
- `tests/test_appointment_delete_product_adapter.py`.

The amendments are exactly:

1. require the proposal freshness ID and the confirmation-body freshness ID
   each to equal the recomputed signed-state freshness ID before any command
   session opens;
2. require the proposal's own signed-confirmation-evidence object to equal the
   confirmation body's verified evidence object, rather than admitting an
   absent proposal copy;
3. add focused zero-session/zero-physical tests for each mismatch; and
4. make the in-memory physical double practice-scope its target before yielding,
   so the cross-practice test expects the real seam's indistinguishable 404
   target-unavailable result rather than a later 403 locked-admission result.

No other semantics, path or test expectation may change.

## Closure

Exact recovered candidate `43e993a98ffec3f9ffe2740b0b38816bcb2d6adb`
and tree `bfb6a6de54fe42ce9eff5315c2ec9378e79b8310` pass the full closure
conditions. The consolidated provider-free profile passes 517 tests; Ruff,
compilation, twelve canonical-LF bindings and forbidden route/schema isolation
pass. The fresh Gemini 3.7 Flash/high veto executes all seven admitted commands,
returns one schema-constrained `pass`, and leaves the exact review HEAD and
worktree unchanged and clean. No further recovery amendment is required.

## Closure conditions

The lease closes only after the adopted candidate plus exact Sol amendments
pass the provider-free focused tests, frozen architecture tests, API Spine
static checks, harness guard, Ruff, compilation, diff/route isolation and one
fresh Gemini 3.7 Flash/high exact-candidate veto. Routes, schemas, models,
migrations, database/runtime, capability, product data, provider calls,
deployment, Pages and protected refs remain closed.
