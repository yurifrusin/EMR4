# Provider-free unmounted CF-D2 event and cue representation architecture plan

Date: 2026-08-13

Timestamp: 2026-08-13T17:19:52+10:00 (Australia/Brisbane)

Status: `frozen_for_inert_representation_execution`

Planning baseline: `784fdc4c0237e1c363676638d010b2bd4b033210`

Accepted observability source: `e8677b54d1c339dcd14776ce8bf15e7db2980378`

Accepted admission source: `a7c6f7a66b06fbc065ae8a6eede7fa8baaee1b6b`

Target result: `raisa_provider_free_unmounted_cf_d2_event_cue_representation_architecture_pass`

## Objective

Define the smallest relational representation capable of carrying the exact
facts proved by the accepted CF-D2 observability architecture and pure
admission rehearsal. The result must distinguish what a database can represent
with keys, references and row checks from what a later transaction protocol
must prove. It must not connect to a database or lower the design into
executable DDL.

Events and cues remain acceleration hints. No represented row becomes Diary
truth, a Context Frame, confirmation evidence, a command receipt or command
authority. A delivered obligation can support only one fresh authorised read
attempt, and every consequential command still rechecks current authority and
source truth.

## Frozen representation boundary

The architecture contains exactly seven abstract relations:

1. `event_partition` for the opaque partition identity and current fencing
   generation;
2. `observer_coordinate` for typed source-head observation and greatest
   observed position, explicitly non-authoritative;
3. `terminal_receipt` for one immutable classification per partition, epoch
   and position;
4. `cue_obligation` for one payload-free pending or delivered refresh range;
5. `consumer_checkpoint` for the highest contiguous admitted position;
6. `dispatch_attempt` for payload-free at-least-once outcomes; and
7. `reconciliation_receipt` for one typed fresh-read attempt outcome.

No raw practice identifier, appointment/person identifier, appointment truth,
free text, event payload, command evidence, credential, provider output or
arbitrary JSON/blob column is representable.

## Enforcement classes

Every invariant is assigned to exactly one primary enforcement class:

- `row_constraint`: scalar type, nullability, enum, literal and range rules;
- `key_or_reference`: primary key, uniqueness and relation reference rules;
- `transaction_protocol`: duplicate comparison, receipt/obligation atomicity,
  pending-only coalescing, contiguous checkpoint movement, fencing, dispatch
  sequencing and reconciliation truth-table rules; or
- `external_authority`: current source truth, current user authority, fresh
  scoped read and command mutation correctness.

The architecture must never claim that a key, foreign key or row check alone
proves a transaction-protocol or external-authority invariant.

## Frozen transaction protocols

1. `admit_terminal`: fence on the exact generation; reuse an exact duplicate;
   reject divergent identity without mutation; create or extend a required
   obligation in the same future transaction as its receipt.
2. `coalesce_pending`: extend only an adjacent pending obligation with the same
   partition, epoch, consumer and reason; never alter a delivered obligation.
3. `advance_contiguous_checkpoint`: advance only across an unbroken receipt
   sequence whose `cue_required` members all reference a covering obligation;
   delivery is not a prerequisite.
4. `record_dispatch_attempt`: fence the writer, allocate one monotone attempt
   ordinal and preserve a stable failure class without changing cue content.
5. `record_reconciliation`: require a delivered attempt, apply the accepted
   outcome truth table, reuse an exact duplicate and reject a conflicting
   second result.

These are inert protocol descriptions. No transaction, lock, trigger,
function, migration or database behavior is exercised here.

## Deterministic representability census

The pure checker must admit twelve authored-synthetic row families:

- empty partition;
- one pending required cue;
- adjacent same-reason coalescing;
- different-reason separate obligations;
- out-of-order gap held;
- gap filled with checkpoint advancement;
- suppressed terminal without obligation;
- rejected terminal without obligation;
- failed dispatch retaining pending state;
- delivered dispatch;
- successful refreshed reconciliation; and
- typed failed reconciliation retaining the old display.

It must also reject at least 48 hostile contract or row mutations, including
missing relations/keys/references/checks/protocols, payload columns, invalid
ranges, orphaned obligations, checkpoint gap crossing, stale fencing, delivery
without an attempt and inconsistent reconciliation outcomes.

## Acceptance

- The closed representation contract passes JSON Schema and semantic checks.
- All seven relation field sets, keys, references, checks and mutability limits
  are exact and payload-free.
- Every accepted admission fact has exactly one representable home.
- The five future transaction protocols preserve the accepted admission
  semantics without being mislabelled as DDL proof.
- All twelve row families pass and at least 48 hostile variants fail closed.
- Denied variants do not alter the canonical contract or row fixtures.
- Source truth, Context Frames, cues and commands remain disjoint under the API
  Spine authority contract.
- Focused tests, canonical fast verification and Git whitespace pass.

## Recovery and worker decision

The relation contract, enforcement classification, fixtures and checker are a
small tightly coupled architecture artifact, so Sol owns implementation and
acceptance under the worker-economy rule. No external worker, verifier or
provider is selected. Mechanical defects may be repaired inside this frozen
boundary. Any need for SQL lowering, a database connection, migration
execution, timing, restart, source observation or product data stops this
tranche rather than broadening it.

## Next descendant

If accepted, the next dependency-satisfied tranche is a provider-free
unmounted inert-DDL lowering of this exact contract. It may render SQL text and
prove deterministic structural coverage, but receives no database connection,
migration execution, source access, watcher, persistence, operational
retention, restart or delivery authority.

## Closed surfaces

No protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient client or real identity, database/source, migration execution,
persistence, operational retention, watcher/listener/worker runtime,
provider/ADC, credential/IAM/network, executable tool, command/write,
GraphQL/OpenAPI route, deployment, production, release, Pages or protected-ref
movement is authorised. `docs/branding/` and every unrelated untracked file
remain preserved and excluded; staging is explicit-path only.
