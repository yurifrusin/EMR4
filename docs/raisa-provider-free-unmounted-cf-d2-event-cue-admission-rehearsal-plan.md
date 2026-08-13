# Provider-free unmounted CF-D2 event and cue admission rehearsal plan

Date: 2026-08-13

Timestamp: 2026-08-13T16:42:39+10:00 (Australia/Brisbane)

Status: `frozen_for_pure_state_execution`

Planning baseline: `351c47bef9bf78383d054f89cd2161d9a6a91718`

Accepted architecture source: `e8677b54d1c339dcd14776ce8bf15e7db2980378`

Target result: `raisa_provider_free_unmounted_cf_d2_event_cue_admission_rehearsal_pass`

## Objective

Exercise the exact accepted observability contract as a pure, deterministic,
in-memory admission state machine. Prove the narrow behaviors that must be
unambiguous before any representation or runtime is considered: duplicate
reuse, identity conflict, position gaps, contiguous checkpoint advancement,
atomic cue-obligation admission, restricted coalescing, lease-generation
fencing, typed lag and fresh-read reconciliation.

This is not a watcher simulation. It opens no database, source, file-backed
state, process, listener, queue, route, provider or command. State exists only
inside one function call and the emitted evidence contains authored-synthetic
digests, positions, enums and counts.

## Frozen boundary

- Data: newly authored synthetic digests and integer positions only.
- Execution: pure Python objects; no clock, randomness, environment lookup,
  network, filesystem access from the state machine, database or subprocess.
- Authority: source truth and command-time current-authority checks remain
  outside and superior to every event or cue.
- Persistence claim: none. Repository evidence files describe the rehearsal;
  they are not operational state.
- API Spine: no new or changed route, command, read model or acknowledgement.

## Admission rules

1. One state machine instance represents one exact partition and source epoch
   under one positive lease generation.
2. An observation candidate has an exact closed field set. Extra payload,
   resource, person, appointment, status, time, command or provider fields fail
   before state change.
3. A position is a positive integer. The exact same identity and fingerprint
   reuses the original immutable receipt and obligation. Divergence is
   `identity_conflict` and changes nothing.
4. A terminal `cue_required` result is admitted only with an allowlisted reason
   and atomic obligation creation. A missing obligation request admits neither
   receipt nor checkpoint.
5. `suppressed_irrelevant` and `rejected_unsupported` are terminal receipts and
   can support contiguous checkpoint movement; neither creates a cue.
6. An out-of-order terminal receipt may be retained in memory, but checkpoint
   movement stops at the first missing lower position.
7. Only adjacent pending obligations with the same partition, consumer and
   reason may coalesce. Delivered obligations and different reasons do not.
8. Every mutating transition supplies the current lease generation. A stale or
   equal competing generation is fenced without state change.
9. Lag is `unknown`, `epoch_mismatch` or a same-epoch exact nonnegative value.
   Unknown and epoch mismatch never become numeric zero.
10. A delivered cue can record one typed reconciliation result only after the
    practice/role/resource check and fresh scoped read conditions appropriate
    to that result. No cue field updates visible truth directly, and an
    acknowledgement confers no future freshness.

## Frozen scenario census

The rehearsal must pass all 22 named scenarios in the closed admission
contract:

- sequential required cue;
- exact duplicate reuse;
- divergent duplicate conflict;
- out-of-order gap hold and later gap-fill advancement;
- suppressed and rejected terminal advancement;
- classification-gap and atomic-obligation-gap denial;
- allowed same-reason coalescing plus different-reason and delivered-state
  non-coalescing;
- stale-generation fencing and current-generation admission;
- unknown, epoch-mismatch and exact lag;
- successful fresh-read projection refresh;
- authorization, source-unavailable and stale-session reconciliation failure;
  and
- prohibited payload-field rejection.

## Acceptance

- The closed contract passes its JSON Schema and exact semantic gate.
- All 22 canonical scenarios pass with byte-stable normalized evidence.
- At least 40 hostile candidate or contract mutations fail closed.
- Denied transitions leave the complete normalized state unchanged.
- Duplicate admission returns the original receipt and obligation identities.
- Checkpoint never crosses a gap, missing terminal receipt, missing required
  obligation or stale fencing generation.
- Coalescing preserves exact lower and upper coverage and never merges across
  reason or terminal delivery state.
- Reconciliation never accepts projection success without a fresh authorised
  scoped read; failure outcomes retain the old visible projection.
- The parent observability contract and API Spine authority checks still pass.
- Focused tests, canonical fast verification and Git whitespace pass.

## Recovery and worker decision

The state model, contract and scenario runner are one tightly coupled bounded
artifact, so Sol owns implementation and acceptance under the worker-economy
rule. No external worker or provider is selected. Deterministic mechanical
defects may be repaired inside this frozen boundary. Any requirement for
persistence, source observation, a real clock, database semantics or a command
stops this tranche rather than broadening it.

## Next descendant

If this rehearsal passes, the next narrow dependency-satisfied question is a
provider-free, unmounted representation architecture for these already-proved
facts. That descendant may compare an inert relational representation with the
accepted state transitions, but receives no migration execution, database
connection, watcher, restart, delivery or operational-retention authority.

## Closed surfaces

No protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient client or real identity, watcher/listener/worker runtime,
database/source, persistence, operational retention, provider/ADC,
credential/IAM/network, executable tool, command/write, GraphQL/OpenAPI route,
deployment, production, release, Pages or protected-ref movement is
authorised. `docs/branding/` and every unrelated untracked file remain
preserved and excluded; staging is explicit-path only.
