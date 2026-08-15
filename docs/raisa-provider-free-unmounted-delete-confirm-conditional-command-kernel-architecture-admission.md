# Provider-free unmounted delete-confirm conditional-command kernel architecture

Date: 2026-08-15

Timestamp: 2026-08-15T11:50:49+10:00 (Australia/Brisbane)

Status: `frozen_unmounted_architecture`

## Boundary

This is the normative abstract contract for a future backend-owned appointment
cancellation transaction. It uses plain authored-synthetic objects, symbolic
locks and copy/discard commit semantics. It is neither the application kernel
nor a database design.

## Input ownership

The authenticated server session owns `practice_id`, `actor_user_id`,
`actor_role` and `session_id`; request-body claims cannot replace them. The
backend-minted proposal owns the exact operation, target appointment, signed
pre-state, waiting-area state, existing and proposed reasons, warning set,
freshness interval, nonce and command digest. The human supplies a distinct
affirmative confirmation and exact warning acknowledgements. The client
supplies an idempotency key but cannot select stored receipt identity.

## Exact order

The command evaluator has these ordered phases:

1. reject malformed or non-dedicated ingress;
2. reject missing idempotency identity before transaction work;
3. begin one command-owned transaction;
4. lock the exact practice authority fence;
5. lock the exact appointment by `(practice_id, appointment_id)` or stop
   non-disclosing;
6. check current actor activity, practice binding, role and cancellation
   capability;
7. lock an existing idempotency row or conflict-safely insert and lock one
   target-bound in-progress row;
8. recheck current authority while every lock is held;
9. classify exact actor/session/operation/route/target/key/request bindings;
10. disclose only an integrity-valid complete same-digest receipt;
11. for a first effect, validate explicit confirmation, exact warning
    acknowledgement, evidence authenticity/expiry/bindings, locked source
    version/status/waiting-area/existing-reason state and proposed reasons;
12. stage the soft-cancelled appointment, delete audit and completed receipt;
13. require one version advance and exact cross-artifact reason/identity
    equality;
14. atomically commit the three-part write set;
15. deliver minimized stored receipt bytes; and
16. perform a separate fresh authorised readback for display.

The lock order is `practice -> appointment -> idempotency_record`. A future
physical design must show that the practice fence stabilizes the authoritative
actor/practice/capability generation across the transaction, or provide an
equivalent lock without violating this global order. This protocol does not
pretend that current tables already do so.

## Reason policy

New dedicated cancellation ingress requires one structured
`status_reason_code` from the current `Cancelled` allowlist. Optional
`cancellation_reason` is either JSON null or a string of at most 500 characters.
Once admitted, its exact value is bound by the proposal signature and request
digest and copied unchanged to appointment truth, audit and receipt.

`confirmed_warnings` acknowledges proposal warnings; it is not a cancellation
reason. `LEGACY_UNCLASSIFIED`, an absent structured reason, raw-delete
permissiveness and a status-family reason are compatibility concerns, not ways
to weaken new dedicated ingress.

## Decision vocabulary and precedence

Structural or binding failures return `admission_rejected` with no command
outcome. Structurally admitted cases return exactly one of:

- `committed`;
- `idempotent_replay`;
- `stale_precondition`;
- `authority_revoked`;
- `confirmation_required`;
- `validation_rejected`; or
- `idempotency_conflict`.

Authority/target non-disclosure precedes replay. Replay/conflict precedes
first-effect evidence and freshness checks because a completed exact request
must be recoverable without reconstructing its historical proposal, but only
for an actor who still has current authority. For a new effect, confirmation
and signed evidence precede freshness and domain validation. No denial plans an
effect or discloses a stored receipt.

## Atomic first effect

One success publishes together:

- appointment status `Cancelled`, waiting area null, exact cancellation text,
  exact structured reason and state version `n + 1`;
- one attributable `delete` audit binding practice, actor, session, command,
  pre/post state, reasons, warnings and correlation; and
- one completed operation-scoped receipt binding the target, pre/post version,
  audit identity, response digest and minimized canonical response bytes.

Every injected failure before commit discards the in-progress claim and all
three staged effects. A connection/serialization loss after commit is an
unknown-delivery condition; retrying the same key and digest returns the stored
receipt without a second mutation or audit.

## Concurrency and readback

Two different idempotency keys aimed at the same signed pre-state serialize on
the appointment. The winner advances the state version; the waiter rechecks
authority and locked state and loses as `stale_precondition`. Same-key,
same-digest contenders produce one commit and one replay. Same-key,
different-digest contenders produce one commit and one non-disclosing conflict.

Readback occurs after commit through a fresh practice/action/resource check. A
later authority revocation may deny display readback but cannot undo the
committed command or convert an effect into failure. The minimized receipt is
the command outcome; readback is reconciliation evidence.

## Compatibility and channel boundary

Only dedicated `delete-confirm` ingress may enter this kernel. Raw compatibility
delete lacks this confirmation contract. The native Diary's `Cancelled` status
fallback is a different command family. Events, context frames, model output,
email/SMS/voice/channel assertions and delegates cannot confirm or authorize.
Any later ingress adapter must acquire and bind all required evidence and
cannot create a second mutation path.

## Claim boundary

The rehearsal may prove closed structure, ordering, precedence, rollback,
replay and authored-synthetic state transitions. It cannot prove a SQL schema,
isolation level, lock strength, real authority store, route response, database
effect, UI behavior, patient-channel delegation or production suitability.
