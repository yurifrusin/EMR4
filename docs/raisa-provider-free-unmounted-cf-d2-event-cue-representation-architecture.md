# CF-D2 event and cue relational representation architecture

Date: 2026-08-13

Timestamp: 2026-08-13T17:19:52+10:00 (Australia/Brisbane)

Status: `architecture_only_provider_free_unmounted_inert`

## Decision

The durable cue mechanism needs seven small kinds of row, not another copy of
the Diary. Together they can represent which source position was classified,
whether a payload-free refresh obligation exists, how far a consumer has
contiguously progressed and whether one delivery and fresh-read attempt
occurred. None of those rows is current appointment truth.

The representation is deliberately abstract. It names relations, scalar
types, keys, references, checks, allowed mutations and future atomic protocols.
It is not SQL, a migration or evidence that PostgreSQL has enforced anything.

## Relational shape

| Relation | Purpose | Mutable fact |
|---|---|---|
| `event_partition` | Opaque source/practice/family identity and fencing generation | generation may advance only through a future ownership protocol |
| `observer_coordinate` | Last non-authoritative source-head observation and greatest observed position | typed coordinate snapshot |
| `terminal_receipt` | Exactly one terminal classification per partition/epoch/position | none |
| `cue_obligation` | Payload-free contiguous refresh range | upper bound while pending; pending may become delivered |
| `consumer_checkpoint` | Highest contiguous admitted position or explicit none | checkpoint under the fenced admission protocol |
| `dispatch_attempt` | Ordered delivered/failed attempt fact | none after insert |
| `reconciliation_receipt` | One typed fresh-read attempt outcome | none |

`none` is represented as an explicit state plus a null position. Source
position zero is never stored as if it were a real source event. Unknown and
epoch-mismatched head observations likewise retain null numeric lag rather than
silently becoming zero.

## Exact identity and references

The partition has a stable opaque identifier and a unique tuple of source
system, practice-scope digest and event family. A terminal receipt is unique by
partition, source-epoch digest and positive position. A cue-required receipt
references one obligation; several adjacent receipts may reference the same
pending obligation after allowed coalescing.

An obligation is bound to the same partition, epoch, fixed Reception One
consumer and one allowlisted reason. Its inclusive range must be positive and
ordered. A checkpoint is unique for partition, epoch and consumer. Dispatch
attempts are unique by obligation and positive ordinal. One reconciliation
receipt is unique per obligation, matching the accepted duplicate-reuse and
conflict behavior.

## What row constraints can prove

Closed enums, positive positions, explicit nullable states, the literal
`fresh_authorized_read_required=true`, ordered ranges, reason/classification
compatibility and reconciliation outcome shapes are row constraints. Primary
keys, uniqueness and references can prevent ambiguous identities and simple
orphans.

They cannot alone prove that:

- receipt and obligation were committed atomically;
- a checkpoint crossed every lower position only after its receipt existed;
- an obligation range covers every referencing cue-required receipt;
- a generation was still current at commit time;
- an attempt ordinal was allocated without a race;
- the referenced attempt was delivered before reconciliation; or
- a fresh read and current authority check truly occurred.

Those facts belong respectively to a future database transaction protocol or
the external authoritative read/command plane. Keeping this distinction
explicit prevents a plausible-looking schema from receiving more evidentiary
weight than it deserves.

## Minimal future atomic protocols

`admit_terminal` first fences the generation and resolves the unique source
position. An exact duplicate returns the original identities. Divergent reuse
fails without mutation. `cue_required` creates or safely extends its obligation
in the same transaction as the immutable receipt.

`advance_contiguous_checkpoint` examines the next position only and stops at a
gap, missing terminal receipt or uncovered required cue. It does not wait for
delivery. `record_dispatch_attempt` preserves ordered at-least-once history and
a stable failure class. `record_reconciliation` requires delivered evidence and
applies the accepted scope/fresh-read truth table; it neither updates Diary
truth nor certifies future freshness.

## Payload ceiling

Only opaque IDs, SHA-256 digests, fixed enums, positive/nonnegative integers,
booleans and nulls are admitted. There is no arbitrary JSON, binary payload,
free text, appointment/person field, status/time truth, command result,
confirmation, audit body, credential or provider output. Operator evidence can
identify the failed stage without retaining the event itself.

## Authority and API Spine

The authoritative source owns current Diary truth and source commits. The
accepted read surface owns fresh projections. The command service owns current
authority checks, atomic preconditions, mutation, idempotency, audit and
readback. This representation owns none of them and adds no route,
subscription, acknowledgement endpoint or command.

## Deliberate non-claims

This architecture does not prove SQL syntax, PostgreSQL catalogue shape,
transactions, locks, isolation, concurrency, restart, unknown commit, crash
recovery, dispatch transport, source observation, timing, retention, rotation,
purge, application wiring, product-data safety, deployment or production.
