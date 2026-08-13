# CF-D2 observability-first durable event and cue architecture

Date: 2026-08-13

Timestamp: 2026-08-13T16:04:58+10:00 (Australia/Brisbane)

Status: `architecture_only_provider_free_unmounted`

## Decision

Durability will preserve a refresh obligation, not a second copy of Diary
truth. A cue means only: “the authorised projection for this practice and
consumer may be stale through source position N.” The recipient must perform a
fresh authorised read. The command service still checks current authority and
source truth inside every consequential mutation.

This is deliberately smaller than the stopped CF-D2 anchor design. It first
makes every handoff independently observable. Crash/restart behavior can later
be tested against those simple facts without asking one terminal coordinate to
stand for several internal assertions.

## Authority planes

| Plane | Owns | Never owns |
|---|---|---|
| Authoritative source | current Diary truth, source head and committed event position | consumer refresh or command authority |
| Durable observer | terminal classification and checkpoint through a contiguous position | current Diary truth or delivery success |
| Cue store/dispatcher | pending obligation and at-least-once delivery state | command receipt, confirmation or current truth |
| Reception One consumer | fresh scoped read and local projection reconciliation | source mutation or truth inferred from cue payload |
| Command service | current authority, atomic precondition, mutation, idempotency, audit and readback | authority inferred from any event or cue |

## Position and checkpoint

The partition key is the exact tuple `(source_system, practice_scope_digest,
event_family)`. Raw practice identity is absent from retained evidence. The
coordinate `(source_epoch, source_position)` is ordered only inside that
partition and epoch.

The operator separately observes:

- `source_head`: greatest committed source position currently known;
- `observed_position`: greatest position seen by this fenced observer; and
- `checkpoint_position`: greatest contiguous position whose immutable terminal
  classification receipt is durable and, when a cue is required, whose durable
  obligation was atomically created.

The checkpoint may advance across `suppressed_irrelevant` and
`rejected_unsupported` receipts because both are terminal and auditable. It
cannot cross an absent receipt, a required-but-absent obligation or a position
gap. Delivery is intentionally outside this transaction; a durable backlog can
survive observer restart without blocking source observation.

Lag is never guessed:

- `exact`: source head and checkpoint share an epoch and the nonnegative
  difference is known;
- `unknown`: either coordinate has not been observed; or
- `epoch_mismatch`: the source epoch changed and rebasing has not been admitted.

Unknown and epoch mismatch are operational attention states, never aliases for
zero lag.

## Terminal classification

Each source position has exactly one terminal result:

- `cue_required`: a supported committed event can affect the consumer scope;
- `suppressed_irrelevant`: the event is supported but cannot affect it; or
- `rejected_unsupported`: schema, family or policy admission failed.

The classifier is deterministic and receives no command, provider or product
tool. Reprocessing the same identity returns the original receipt. Divergent
content for the same identity is `identity_conflict` and cannot advance the
checkpoint.

## Minimal cue obligation

The durable obligation contains:

- version and opaque obligation identity;
- practice-scope digest and fixed consumer scope;
- event family;
- source epoch plus inclusive contiguous `from_position` and `through_position`;
- one allowlisted reason code; and
- the literal requirement for a fresh authorised read.

It contains no appointment or person identifier, status, time, clinical or
free text, command outcome, precondition, confirmation, audit payload,
credential or provider value. Adjacent pending obligations with identical
partition, consumer and reason may coalesce; the range endpoints preserve what
was covered. A delivered or terminally failed obligation is immutable.

## Delivery and reconciliation

Delivery is at least once and practice-scoped. A consumer deduplicates the
obligation identity, then asks the accepted read surface for its current scoped
projection. It compares that response with its current visible selection or
proposal and silently retains, updates or clears local UI state under the
existing reconciliation rules.

No acknowledgement certifies freshness forever. It records only that this cue
caused one fresh read attempt. A later source position may make the projection
stale again. Failed authorization, unavailable source or stale session yields a
typed reconciliation failure and no display update.

## Discriminating operator evidence

The following stages are mutually distinct and payload-free:

| Condition | Required distinguishing evidence | Safe response |
|---|---|---|
| Source head unavailable | `source_head_state=unknown` | show unknown, do not claim zero lag |
| Observer behind | exact head/checkpoint epoch and positive lag | resume after checkpoint |
| Position gap | observed higher position plus exact missing lower position | hold checkpoint at gap |
| Classification absent | observed position with no terminal receipt | retry classification only |
| Classification rejected | immutable reject receipt and reason code | alert; no cue |
| Obligation absent | `cue_required` receipt with no atomically bound obligation | hold checkpoint and fail closed |
| Dispatch pending | durable pending obligation and no attempt | retain backlog |
| Dispatch failed | immutable attempt result and stable failure class | bounded redelivery, same obligation |
| Ownership fenced | stale lease generation on proposed checkpoint write | reject writer immediately |
| Reconciliation failed | delivered obligation plus typed fresh-read failure | retain truthful old UI state and surface refresh failure |

The evidence-led gate requires each future diagnostic hypothesis to map to one
of these distinct observations before any correction or runtime attempt is
eligible.

## API Spine effect

This architecture adds a non-invasive async prototype only. It creates no
GraphQL mutation, subscription, REST command, read route or acknowledgement
endpoint. A later runtime contract must authenticate its integration principal,
scope every operation to one practice, enforce idempotency and preserve audit,
but none of those runtimes are opened here.

## Deliberate non-claims

This does not prove PostgreSQL representation, transactions, restart, unknown
commit, crash recovery, delivery, source observation, latency, availability,
retention, rotation, purge, application wiring, product-data safety,
deployment or production. CF-D1 remains accepted concurrency evidence; both
stopped CF-D2 sequences remain negative evidence and are not promoted.
