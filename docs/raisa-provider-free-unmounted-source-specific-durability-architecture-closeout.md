# Provider-free unmounted source-specific durability architecture closeout

Date: 2026-08-06

Status: accepted

Result:
`raisa_provider_free_unmounted_source_specific_durability_architecture_pass`

Exact independently reviewed source HEAD:
`14e8d3257b9531601260bef094c73e08a9c7b92d`

## Outcome

The first source-specific durability architecture for the patient-free
`diary.appointment_rescheduled.v1` family now passes as a provider-free,
unmounted contract. It separates a payload-free observer principal from the
internal durability coordinator, allocates one rollback-safe per-practice
transaction position, and atomically joins classified receipt, durable
invalidation watermark, coalesced reassembly obligation, minimized audit and
checkpoint disposition.

Frame currentness is derived from the durable invalidation watermark against
the frame's exact assembled-through position. A future replacement read must
either share the source snapshot or prove an exact before/after source-head
fence. Gaps hold the last contiguous checkpoint, force full invalidation and
require rebase; they cannot be hidden by the existing event-feed cursor or by
an appointment aggregate revision.

## Acceptance reconciliation

- the observer and coordinator are distinct exact service principals with no
  staff-JWT, product-read, provider, persistence or command authority;
- the future stream is practice-scoped, epoch-bound and positioned by a
  transactionally locked stream head in the same future producer transaction;
- rollback removes both the head advance and projected row, avoiding an
  artificial durability gap;
- PostgreSQL sequence, identity, time, UUID, `xmin`, commit timestamp, WAL LSN,
  the existing `(occurred_at,event_id)` cursor and `aggregate_revision` are
  explicitly ineligible as the continuity coordinate;
- admitted receipt, invalidation watermark, reassembly obligation, privacy-safe
  audit and checkpoint disposition are one all-or-nothing future transaction;
- exact redelivery is idempotent, unrelated changes advance contiguously
  without invalidation, and a gap or unverifiable coordinate fails closed;
- restart, overflow, coalescing, retention eligibility and source/checkpoint/
  audit lifecycle boundaries are explicit;
- identity uses a dedicated HMAC key ring with exact position intervals and
  generation-consuming failure for unverifiable rotation; and
- every payload, audit, producer, checkpoint and atomic tuple is an exact
  ordered schema constant.

The first fresh exact-head veto rejected source
`92cf76b17bbab276df701ee1e0af0da77e1768a9` because safety-critical arrays were
only generically bounded. Sol preserved AER-0048, invoked the named recovery
lease, made all seven tuples exact, and added append, removal, replacement and
reordering tests. A genuinely fresh recovery veto at the accepted source
rejected all 28 independent tuple mutations, passed 160 serial checks and
found no P0-P2 issue. AER-0048 is corrected in register revision 42.

## Preserved evidence

All user-owned untracked files, especially `docs/branding/`, and every unrelated
Gate -1, Consultant, receipt/state, evidence and cost-ledger artifact remain
preserved and excluded.

## Claim boundary

This acceptance freezes architecture and authored-synthetic contracts only. It
does not create a database table, migration, outbox, source row, trigger, feed,
watcher, listener, operational principal or credential, durable checkpoint,
product read, patient/product/protected data flow, API route, provider call,
command/write, runtime wiring, deployment, production, release, Pages operation
or protected-ref authority.

## Next safe descendant

Under Yuri's standing uninterrupted-gate authority, proceed directly to a pure
provider-free, unmounted, authored-synthetic durability state-machine rehearsal.
It may implement in-memory contract types and transitions for exact redelivery,
contiguous relevant and irrelevant observations, durable watermark and
coalesced-obligation semantics, gap/hold/rebase, restart reconstruction, key
interval boundaries and retention eligibility.

It may not add or alter application code, migration, database, outbox, feed,
watcher, listener, source access, operational persistence, product read,
patient/product/protected data, provider/model call, API route, command/write,
runtime wiring, deployment, production, release, Pages or protected refs. Any
live implementation remains a later separately bounded gate.
