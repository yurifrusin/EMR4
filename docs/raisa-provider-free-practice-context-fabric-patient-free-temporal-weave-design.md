# Practice Context Fabric patient-free temporal weave design

Date: 2026-08-06

Status: provider-free authored-synthetic design

## API Spine classification

This tranche is a non-executing read-context freshness and historical-context
protocol. It adds no API surface. Committed events remain signals for later
authorised reads, GraphQL remains read-only, and REST/OpenAPI remains the only
future command plane.

## Why the frame set is replaced, not updated

An admitted `ContextFrameSet` binds exact source revisions, expiry, omissions,
proofreader result and a digest. Editing any frame during a Bureau turn would
break those bindings and could mix old and new truth. The watcher therefore
changes only the lifecycle state around the set. Once a relevant change is
known, the old set is no longer admissible and the only recovery is a complete
freshly authorised assembly followed by same-packet proofreading.

The event does not carry the replacement truth. It answers only: “one or more
dependencies may now be stale.”

## Typed objects

### `TemporalDependencyManifest`

Backend-derived, sealed metadata over the active frame set. It binds the exact
frame-set, need, grant, authority-binding and source-trace digests; practice and
session-binding digests; session generation; policy version; admitted event
families; starting checkpoint; expiry; and one dependency entry per frame.

Each dependency entry retains the exact frame id/digest/type, source class,
source contract/revision/digest, location and opaque resource selectors, and
the allowlisted event families that may invalidate it. A dependency cannot
name a frame, source, selector or event family outside the parent grant.

### `TemporalWatchLease`

A backend-owned, expiring and non-transferable capability to classify signals
against one manifest. It binds the practice/principal/session generation,
policy, manifest and active frame-set digest; accepted event families and
selectors; sensitivity ceiling; starting checkpoint; maximum signal count;
and handling policy `REASSEMBLE_AT_BOUNDARY`.

It has `execution_enabled: false`, `returns_data: false`, `read_only: true` and
`command_authority: false`. It is neither a database credential nor authority
to create a listener, retrieve a source or extend retention.

### `TemporalSignalEnvelope`

A patient-free control envelope containing stable event identity, event and
schema type, committed state, practice binding, aggregate class and opaque
aggregate reference, positive aggregate revision, affected selector
coordinates, occurrence/receipt/expiry times, cursor and sensitivity. It has no
event payload, patient identity, free text, before/after state or replacement
read data.

### `TemporalInvalidationDecision`

The pure classifier's sealed result for one signal. Decisions are:

- `IRRELEVANT`: valid but no dependency intersects;
- `SUPPRESSED`: duplicate, replay, equal/older revision or already superseded;
- `REASSEMBLY_REQUIRED`: the first relevant change to a current set;
- `COALESCED`: another relevant change while reassembly is already required;
- `CURSOR_GAP`: ordered delivery cannot be proved;
- `EXPIRED`: the frame set or lease has expired; or
- `REVOKED`: authority/session generation is no longer current.

Reasons are privacy-safe codes. A decision cannot contain replacement context
or command material.

### `ContextReassemblyRequirement`

An inert descriptor emitted once per affected active set. It cites the old
frame-set and manifest digests, exact source/frame classes to re-read, current
authority/session/policy coordinates, ordered cause signal digests, request
revision and expiry. It performs no read and has `execution_enabled: false`,
`returns_data: false`, `command_authority: false`.

### `TemporalFrameSetState`

An immutable lifecycle record around the existing set. Allowed states are
`CURRENT`, `REASSEMBLY_REQUIRED`, `EXPIRED` and `REVOKED`. State is monotonic:
no signal can return a non-current set to `CURRENT`, and a later reassembly
produces a new frame-set id and digest rather than mutating this record.

### `HistoricalOperationalSnapshot`

A distinct read-only frame for selected past operational state. It carries a
source contract/revision, purpose and scope, a half-open `valid_time` interval,
a half-open `transaction_time` interval, retention class, correction lineage,
provenance and minimal authored-synthetic content. It explicitly sets
`current_truth_authority: false` and `command_authority: false`.

The original record remains addressable after correction. “What appeared true
at 09:00?” uses valid time; “what had the practice recorded by 10:00?” also
clips transaction time. Neither question is answered by replaying event payloads.

## Classification order

For each signal the engine checks, in order:

1. closed schema and seal;
2. current session generation, binding, policy, manifest and lease;
3. frame-set and lease expiry/revocation;
4. committed state, allowlisted family/schema and sensitivity;
5. practice and scope intersection;
6. cursor continuity and monotonic aggregate revision;
7. event/lease/generation/frame-set deduplication; and
8. dependency intersection.

This ordering prevents a foreign or malformed signal from influencing cursor,
revision or state. Cursor discontinuity is a closed failure: it invalidates the
old set and requires a new baseline and authority decision.

## Reassembly race rule

Every reassembly request increments a monotonic request revision within the
session generation. A future result must cite the exact request revision,
manifest, lease, grant, binding and superseded frame-set digest. Starting a
later request consumes the earlier ticket. Session invalidation consumes every
pending ticket. This mirrors the accepted native-Diary reconciliation rule and
prevents a slow old read from restoring stale context.

## Historical selection

Historical selection is deterministic intersection, not free-text search. A
candidate may propose a named horizon or explicit interval and source classes;
backend policy supplies the permitted purpose, locations, retention classes,
maximum lookback, count and disclosure fields. The released historical frames
are canonically ordered by valid start, transaction start and snapshot id.

Overlapping snapshots for one source/subject must have explicit correction or
supersession lineage. Unknown gaps remain gaps; the engine does not interpolate
or treat absence as evidence.

## Non-authority statement

The watcher observes no database in this tranche. In a later runtime it may
receive minimal committed-event metadata through an authenticated,
practice-scoped feed, but it will still only revoke the usability of an old
context bundle. It cannot grant reads, disclose context, invoke a model, write
to the product, acknowledge a command or prove current truth.
