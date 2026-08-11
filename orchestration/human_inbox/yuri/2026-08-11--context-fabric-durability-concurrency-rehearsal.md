# Tranche closeout — Context Fabric durability concurrency rehearsal

Date: 2026-08-11

Result: `passed`

Yuri attention required: `no`

## Lay summary

The Context Fabric's database record-keeping now survives the six most
important two-clerk races we selected. When two actions reach the same record
together, PostgreSQL produces one exact durable outcome: it does not silently
duplicate a registration, skip a source position, replace the winning reading,
apply a coordinator change twice or retain a deliberately rolled-back change.

The proof used only invented records in a disposable local PostgreSQL 16
container. That container was removed and confirmed absent. No patient,
practice or product data was read, no provider was contacted and no product
command was available.

## Technical summary

- Passed all six frozen concurrent-session scenarios with observed
  `PgSleep`/`Lock` overlap.
- Proved exact `40001`, `CF004` and injected `P0001` loser behavior, monotone
  producer positions 1/2, same-primary replay, native receipt replay and full
  outer-transaction rollback.
- Reconciled all 22 relation snapshots and all forbidden-effect checks.
- Started exactly 12 participant and 11 precondition transactions with zero
  retry.
- Validated the immutable pass document at SHA-256
  `7dd7372a8f45b6a049aca4f835057a33ab37952be98088bbbf34ed94875dd0e4`.
- Removed exact container
  `0e8900cf035d9af6e38926d43586f9510efd2ef36a39410377054fbe0e9ee175`
  and confirmed no matching container remains.
- Fresh Gemini 3.6 Flash/high independently passed 254 static checks before
  runtime with zero external operations.

## Issues revealed

Three rejected attempts were useful and remain preserved. They found a direct
launcher import defect, insufficient minimized failure telemetry and one
near-match result spelling (`RECEIPT_REPLAY` instead of PostgreSQL's accepted
`RECEIPT_REPLAYED`). Each stopped closed, cleaned up exactly where applicable
and received a reviewed regression before the final run.

## Deliberately still closed

Crash/restart behavior, unknown commit, general retry or deadlock policy, load
and performance, more than two participants, key rotation, retention/purge,
long-lived or operational persistence, real source/watcher access,
patient/clinical/product data, providers, tools, commands, deployment,
production, release, Pages and protected refs remain unproved and closed.

## Planned next tranche

Proceed directly to CF-D2: freeze the narrowest provider-free disposable
restart and unknown-commit recovery plan against this accepted durability
schema. It must distinguish definitely committed, definitely rolled back and
genuinely indeterminate client observations without guessing success. No
intervention is needed under the standing authority.
