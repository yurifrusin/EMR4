# Provider-free unmounted status transaction-kernel protocol design

Date: 2026-08-12

Status: `frozen_unmounted_design`

## Boundary

The protocol is a deterministic model of what a future backend-owned status
transaction must guarantee. It is not the kernel implementation. Synthetic
objects are plain dictionaries; locks are trace labels; commit and rollback
copy or discard in-memory state only.

## Admission and outcome precedence

1. closed structure and exact operation/practice/actor/session/target/digest
   bindings;
2. exact `practice -> appointment -> idempotency_record` lock plan;
3. current authority recheck before any stored receipt disclosure;
4. separate signed-confirmation and warning acknowledgement validation;
5. idempotent replay or digest conflict;
6. source-version/freshness comparison;
7. current target and transition-domain validation; and
8. atomic first effect.

The accepted public outcome vocabulary remains `committed`,
`idempotent_replay`, `stale_precondition`, `schedule_conflict`,
`authority_revoked`, `confirmation_required`, `validation_rejected` and
`idempotency_conflict`. Status does not use `schedule_conflict` in its admitted
current profile; the vocabulary remains shared with the four-family kernel.

## Atomic first effect

One successful synthetic transaction stages:

- one appointment status/version transition;
- one attributable mutation-audit record; and
- one completed idempotency receipt containing response/readback identity.

The commit point publishes all three together. Any injected failure before it
publishes none. Readback is derived from committed state, never from a staged
object. A replay observes the completed receipt and never appends a second
domain audit.

## Concurrency and disclosure

All contenders acquire the same ordered labels. A waiting contender rechecks
current authority and expected appointment version after acquiring them. A
revoked actor learns no stored receipt. A stale contender loses without an
effect. Same-key/same-digest observes the original receipt; same-key/different-
digest observes only the conflict type.

## Deferred boundaries

Terminal re-transition is not silently settled by the protocol. The case stops
as `validation_rejected` with reason `transition_policy_deferred`, labelled as
an architecture review boundary rather than a product policy change.

Response serialization occurs after the synthetic commit. Failure there is a
delivery failure, not a rollback claim. The packet pairs it with a replay
schedule to prove that a client can recover the original receipt without a
duplicate effect.
