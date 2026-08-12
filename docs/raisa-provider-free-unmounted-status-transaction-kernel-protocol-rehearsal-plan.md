# Provider-free unmounted status transaction-kernel protocol rehearsal plan

Date: 2026-08-12

Source HEAD: `490cf1048d4a66183ccdbbe185a28f3c3609fdac`

Status: `frozen_for_provider_free_unmounted_execution`

## Purpose

Prove the narrow status-confirm transaction protocol beneath the accepted
conditional-command interface before any application route can use it. The
rehearsal uses only authored-synthetic in-memory state machines and transaction
schedules. It imports and executes no application route, model, database or
command.

## Frozen status profile

- canonical operation: `confirmAppointmentStatusProposal`;
- target: exactly one existing synthetic appointment;
- lock plan: `practice -> appointment -> idempotency_record`;
- the full global order remains `practice -> schedule_domain -> appointment ->
  idempotency_record`, with the unused schedule-domain lock skipped rather than
  reordered;
- authority is rechecked under the transaction boundary before receipt
  disclosure;
- confirmation evidence is separate from authentication and arrival;
- same-key/same-digest completion returns the original receipt without another
  mutation or domain audit;
- same-key/different-digest fails as `idempotency_conflict`;
- source-version drift fails as `stale_precondition`; and
- only `committed` may atomically make appointment mutation, attributable audit
  and completed receipt durable and return readback.

## Two-layer rehearsal

### Decision state machine

Closed scenarios exercise structure/binding admission and the accepted eight
outcomes. Structural or lock-plan failures stop before an outcome. Current
authority precedes confirmation, replay disclosure, freshness and domain
validation.

### Transaction schedule simulator

Closed schedules exercise failure before locks, after staged mutation, after
staged audit, after staged receipt, and after commit but before response
serialization. Every pre-commit failure restores all three durable components.
Post-commit response failure leaves all three committed; a same-digest retry
returns the original receipt without another mutation or audit.

Two-command schedules additionally prove same-digest replay, different-digest
conflict, stale source loss and authority loss after waiting. All participants
use the same canonical lock order.

## Explicit review questions

1. Current product behavior warns and permits a separately confirmed
   re-transition from a terminal status. This protocol labels that profile
   `policy_deferred` and performs no planned effect; it does not silently make
   the behavior valid or invalid for a later runtime.
2. Current helpers serialize their response after commit. This protocol proves
   the safe retry requirement for a serialization failure but does not claim
   the present route already exposes an unknown-commit response contract.
3. The existing idempotency helper acquires its ledger row before the
   appointment row. The protocol freezes the newer source-owned-truth order;
   no application route may mix the two orders until a later reconciliation.

## Owned artifacts

- this plan and its design/threat-model delta;
- a closed JSON scenario/schedule packet and JSON Schema under
  `orchestration/continuity/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal/`;
- one pure provider-free validator/simulator script;
- focused deterministic tests;
- exact receipts and, after passing, closeout/acceptance/Yuri/Continuity
  artifacts.

## Acceptance

The tranche passes only if:

1. the fresh five-source receipt passes;
2. the packet validates against a closed schema and exact parent hashes;
3. every decision scenario returns its exact admission, outcome, reason,
   disclosure and planned-effect shape;
4. authority loss precedes replay disclosure and every later loser;
5. all status lock plans are exactly `practice -> appointment ->
   idempotency_record`;
6. only committed schedules make mutation, audit and completed receipt durable;
7. every pre-commit injected failure rolls back all three components;
8. response serialization failure after commit is safely replayable without a
   second mutation or audit;
9. concurrent same/different-digest, stale-source and authority-loss schedules
   award exactly one correct winner/loser set;
10. terminal re-transition remains deferred and performs no effect;
11. at least 30 independent hostile mutations fail closed;
12. focused parent/API tests, canonical repository checks and whitespace pass;
    and
13. protected refs and all unrelated untracked files remain unchanged.

## Forbidden surfaces

- no application import/edit/route execution or runtime kernel;
- no database driver, source, watcher, event, migration, model or transaction;
- no real lock, mutation, audit write, receipt write or command;
- no operational, product, patient, clinical, financial or licensed data;
- no provider, network, credential, IAM, metadata, tool or executable;
- no raw-route change, create fence, observer/sink/persistence or shadow enablement;
- no deployment, production, release, Pages or protected-ref movement; and
- no broad staging, `docs/branding/`, protected evidence or unrelated
  untracked file.

## Recovery and next work

A mechanical packet/schema/simulator/test defect may receive one bounded
correction without changing the precedence, locks, outcomes or claim boundary.
Any need to decide terminal re-transition product policy, reconcile runtime
lock order or change the eight outcomes is a separate architecture/runtime
decision.

After acceptance, the next safe candidate is a provider-free unmounted
status-confirm kernel adapter contract. It may freeze the exact transformation
between the existing signed confirmation envelope and this protocol, but still
may not import or execute an application route, database or command.
