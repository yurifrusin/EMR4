# Check-in environment-manifest and secret-posture architecture

Date: 2026-08-19

Timestamp: 2026-08-19T15:38:31+10:00 (Australia/Brisbane)

Status: **accepted**

## Lay summary

We have defined the shape of a future ordinary check-in environment without creating or enabling one. The record says what non-secret identity the environment must carry, what restricted database role it must eventually prove, and which three kinds of secret references it would need. It never contains the secrets themselves.

The safety design is deliberately one-way. Missing or stale evidence denies; a break-glass state can only shut the lane down; and even a fully valid environment record merely passes an evidence checkpoint. It cannot turn check-in on, reach a database or execute a command.

The deterministic proof tried 337 hostile changes and none escaped. Gemini independently passed all ten checks on the unchanged candidate, including 17 focused and 103 surrounding tests. One wider local run found four old tests whose assumptions were tied to an earlier clockwork generation. They were recorded rather than hidden or folded into this product architecture change.

## Technical summary

- Exact reviewed candidate: `a1f309a6d52d01f9866432f7e9abb8095788d023`.
- Population: 0 manifests, practices, roles, secret references and operational-evidence artifacts.
- Logical role: `appointment_check_in_ordinary_runtime_v1`; future proof must show non-owner, `NOBYPASSRLS`, no product ownership and cross-tenant denial.
- Reference slots: database credential, application signing key and admission-snapshot verification key.
- Proof: 16 source bindings, 268 contract mutations, 69 manifest mutations, 0 escapes.
- Independent veto: Gemini 3.7 Flash/high pass, unchanged clean worktree, 10/10 commands.
- Workflow reading: no preplanning trips, no post-freeze candidate construction correction, one read-only intent-schema trip, one candid broad-suite stale-fixture failure, no AER and no bespoke updater.
- Protected refs remain `2e34bdad732fdab32fbf778280b3d3c70d66d602`.
- Clockwork: generation `a7b3f1fc6696f535ef4f7d5e0d5b99c89f19bdc87546e5b4cf242b3b7483e88d`, Continuity 333 / Compass 315, lease 3, zero drift and no republication.

Three current-state test assertions still named older clockwork generations. They were replaced with readings from the selected transaction and active latch, then the full material suite passed. One duplicate failing run occurred because the first ongoing test-session handle was not retained; it changed no state. This is recorded as workflow cost rather than hidden in the successful product result.

The next step is a disposable local PostgreSQL rehearsal that proves the restricted role and exact tenant isolation using only authored-synthetic identifiers, then removes the instance and role completely. It does not enable ordinary check-in or open live secrets, product data, deployment, Pages or protected refs.

The usual non-PHI continuing Pushover notification succeeded with request `0b6402ec-152d-454c-8024-a80b1dfcb887`.
