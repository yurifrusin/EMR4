# Provider-free unmounted durability state-machine rehearsal plan

Date: 2026-08-06

Status: frozen bounded implementation plan

Parent result:
`raisa_provider_free_unmounted_source_specific_durability_architecture_pass`

## Objective

Implement one pure, immutable, in-memory rehearsal of the accepted source-
specific durability contract for the patient-free
`diary.appointment_rescheduled.v1` family. The rehearsal must prove that exact
source positions and proofread decisions produce the architecture's atomic
checkpoint, invalidation-watermark, coalesced-obligation, receipt and minimized-
audit transitions without mounting a source or persisting operational state.

The intended result label is
`raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal_pass`.

This tranche is provider-free, unmounted and authored-synthetic. It adds no
application code, migration, database object, route, worker, listener, runtime
configuration or operational credential.

## API Spine classification

This is an internal async/event durability rehearsal only:

- GraphQL remains read-only and unchanged;
- REST/OpenAPI remains the only command plane and gains no operation;
- `diary.appointment_rescheduled.v1` remains a committed-change signal, not
  current truth or command evidence;
- the existing signed update-confirm command and committed-event feed remain
  untouched;
- no API schema, source adapter or live observer is mounted; and
- every future fresh read remains separately gated to a current application
  principal and a new no-wider `ContextScopeGrant`.

## Frozen implementation surface

The rehearsal may add only:

- one pure Python module under `scripts/`;
- one deterministic acceptance generator under `scripts/`;
- one closed authored-synthetic rehearsal contract/schema plus generated
  evidence under a new `orchestration/continuity/` directory;
- focused tests;
- this plan, its design and threat-model delta; and
- later review, closeout, acceptance and continuity artifacts.

No `app/**`, `alembic/**`, `docs/diary/**`, API Spine contract, existing source
adapter or existing runtime file may change.

## Canonical immutable state

The pure module must use immutable value objects and copy-on-transition state.
The canonical state contains only:

- an exact practice-binding digest, source-contract digest, stream id/epoch,
  observer id/generation and controlling policy/binding/registry/impact/key-
  schedule digests;
- one checkpoint state and last contiguous classified position/digest;
- closed frame generations with opaque synthetic ids, closed frame types,
  `assembled_through_position` and `CURRENT` or `RETIRED` lifecycle;
- monotonic invalidation watermarks by closed frame type;
- at most one pending reassembly obligation per frame-generation id;
- immutable classified receipts keyed by exact position;
- minimized audit records; and
- a metadata-only key schedule with no key material.

No patient, appointment, practitioner, location, time-slot, actor, session,
payload, command, provider or free-text field is admitted.

## Exact decision inputs

Each authored-synthetic candidate is already inside the accepted observation
membrane and contains only exact stream/practice/generation coordinates,
position, predecessor, opaque observation digest, aggregate revision, key id,
closed decision, closed reason code and closed affected frame types.

The rehearsal accepts exactly these decision families:

- `CONTIGUOUS_ADMIT` for one or more affected frame types;
- `CONTIGUOUS_NO_INTERSECTION` with no affected frame type;
- `CONTIGUOUS_FULL_INVALIDATION` over the complete conservative frame-type set;
- `EXACT_REDELIVERY` derived by the state machine, never caller-asserted;
- coverage-gap, same-position identity mismatch and digest-reuse corruption,
  all of which hold the checkpoint, fully invalidate and require rebase; and
- malformed, foreign-scope or wrong-contract stop outcomes that leave the
  prior state byte-equivalent and grant no suppression/continuation.

The caller cannot choose checkpoint disposition directly.

## Atomic transition contract

For a contiguous accepted candidate the pure transition stages exactly these
five members in order:

1. immutable classified-observation receipt;
2. monotonic invalidation-watermark updates;
3. insert/coalesce one reassembly obligation per affected frame generation;
4. one privacy-safe audit record; and
5. positive checkpoint advance.

The transition returns a wholly new state only when every staged member
succeeds. A closed authored-synthetic fault-injection selector may fail before
any one member; every such run must return the exact original state and no
receipt, watermark, obligation, audit or checkpoint residue. Fault injection
is rehearsal-only and cannot appear in an operational contract.

For coverage corruption, full invalidation, obligations, audit and checkpoint
state `REBASE_REQUIRED` commit atomically while the last contiguous position is
held. A malformed/foreign/wrong-contract candidate produces no state mutation.

## Redelivery and corruption

- Position `last + 1` with predecessor `last` is the only new contiguous
  coordinate.
- Position at or below the checkpoint is exact redelivery only when the stored
  receipt position and observation digest match using constant-time comparison;
  it returns that receipt and the identical state object value.
- A different digest at an existing position is corruption.
- Reuse of an already classified observation digest at a new position is
  corruption.
- A position above `last + 1`, wrong predecessor or epoch mismatch is a gap.
- Concurrent database behavior is not simulated; the pure transition models
  the state resulting after the architecture's checkpoint-row lock.

## Watermarks, frame retirement and obligations

The exact conservative frame types are
`current_diary_projection` and `current_waiting_room_projection`.

A relevant contiguous decision monotonically raises only its affected
watermarks to the candidate position. Every matching `CURRENT` frame with
`assembled_through_position` lower than that watermark becomes permanently
`RETIRED`. A full-invalidation or corruption outcome raises both watermarks and
retires all current frames.

Obligations are keyed only by opaque frame-generation id. The first cause
creates one pending obligation; later causes for the same retired generation
coalesce into that object by advancing `latest_position`, a deterministic
bounded rolling cause digest and a closed count bucket (`ONE`, `TWO_TO_FOUR`,
`FIVE_PLUS`). No transition restores a retired frame or creates a second
obligation for it.

## Restart reconstruction

The pure restart function receives a candidate durable state plus exact next
retained-row metadata. It may return `RESUME` only when:

- checkpoint state is `ACTIVE`;
- all controlling digests match backend-authored expected values;
- stream id/epoch and observer generation match;
- the next position is exactly checkpoint plus one and its predecessor equals
  the checkpoint;
- the observation's key id is the sole key interval for that position; and
- the state integrity digest reproduces.

Any missing/corrupt state, mismatch, unavailable next row, retention overrun,
unknown key or non-contiguous coordinate returns a new fully invalidated
`REBASE_REQUIRED` state holding the prior contiguous position. It never reads a
payload, reconstructs truth or adopts an older frame as current.

## Key-interval rehearsal

The key schedule contains opaque key ids and exact inclusive start/exclusive
end transaction-position intervals. It contains no key material. Intervals
must be ordered, non-overlapping and gap-free from the established baseline to
the open final interval. Exactly one interval must resolve every candidate
position.

Tests must cover the last position before rotation, the first successor
position, overlap, gap, retroactive change, missing key id and attempt to use a
different interval key. Any unverifiable schedule consumes the generation
through full invalidation/rebase; no verifier tries every key.

## Retention eligibility rehearsal

Retention is a pure decision over authored-synthetic row metadata. A position
is purge-eligible only when every eligible non-consumed generation checkpoint
is at or beyond it, no recovery/audit pin remains, its verification-key overlap
is closed and the declared safety grace has elapsed. The minimum eligible
checkpoint controls; the existing event TTL and wall clock are absent.

Source-row, classified-receipt/checkpoint and audit retention remain separate
closed result families. The rehearsal decides source-row eligibility only and
grants no deletion effect.

## Audit minimization

The generated audit value may contain only closed schema/version codes,
practice/principal/policy/binding/source/registry/impact/key-schedule digests,
observer generation, stream coordinate, aggregate class/revision, observation
digest and key id, decision/reason, affected frame types, closed count buckets,
checkpoint disposition, lifecycle revision and prior audit digest.

It must contain no raw event id, aggregate alias, product identifier, active
session inventory, frame content, actor/correlation, payload, patient/clinical
value, provider output or free text. Audit is not Context Fabric content,
Bureau Memory, read authority or command evidence.

## Authored-synthetic evidence scenarios

The acceptance generator must deterministically produce and schema-validate a
single closed evidence packet covering at least:

1. relevant contiguous admission and selective watermark/retirement;
2. exact redelivery with byte-equivalent state;
3. irrelevant contiguous advancement without invalidation;
4. a later relevant cause coalesced into one existing obligation;
5. contiguous full invalidation over both frame types;
6. gap/hold/rebase with no skipped checkpoint;
7. same-position mismatch and digest reuse corruption;
8. five member-by-member atomic rollback injections;
9. successful restart plus gap, digest and retention-loss restart failures;
10. key-boundary success and overlap/gap/missing-key failure;
11. minimum-checkpoint, pin, key-overlap and grace retention decisions; and
12. static proof that all effect ceilings remain false.

Evidence must be regenerated from authoritative input artifacts and must not be
accepted solely because a committed expected-output file matches itself.

## Data, provider, cost and licence posture

- Data: newly authored synthetic opaque ids/digests and closed metadata only.
- Patient/product/protected/historical-PHI data: none.
- Provider/model/external retrieval: none.
- Database, source, network or browser contact: none.
- Cost: zero provider/cloud cost.
- Licence: no external content or corpus.

## Allowed side effects

Repository writes are limited to the frozen files named above. Test execution
may create ordinary interpreter/test-cache files only. There is no database,
network, subprocess child runtime, browser, source, listener, provider, product
or command effect.

## Forbidden surfaces

No `app/**`. No `alembic/**`. No `docs/diary/**`, API contract, route, resolver,
migration, database/table/view/function/trigger/sequence/role/credential. No
outbox, feed, watcher, listener, broker, scheduler or worker. No operational
checkpoint. No filesystem state store, product/source read, patient/product/
protected data, raw audit, provider/model call, command/write, runtime wiring,
deployment, production, release, Pages or protected-ref movement. Preserve and
exclude `docs/branding/` and every unrelated untracked artifact.

## Acceptance

1. The implementation is pure, immutable and accepts only the exact parent
   source/principal/stream/generation contract.
2. All public types and serialized evidence are recursively closed; prohibited
   product, session, payload, provider and free-text keys fail validation.
3. Caller input cannot assert redelivery or choose checkpoint disposition.
4. Contiguous relevant, irrelevant and full-invalidation decisions follow the
   exact parent dispositions.
5. Receipt, watermark, obligation, audit and checkpoint staging is all-or-
   nothing under each of five deterministic fault injections.
6. Watermarks are monotonic; a watermark newer than
   `assembled_through_position` permanently retires a matching frame.
7. Exactly one obligation exists per frame generation and later causes
   coalesce without exposing source or session identity.
8. Exact redelivery returns the existing receipt with no state mutation;
   mismatched same-position and digest-reuse candidates force rebase.
9. Gaps and restart uncertainty hold the last contiguous checkpoint, fully
   invalidate and require a new generation; they never skip forward.
10. Restart resumes only from an integrity-verified state and exact next row
    with all controlling digests and the sole position key matching.
11. Key intervals are ordered, gap-free and non-overlapping; boundary success
    and malformed/unavailable schedule failures are deterministic.
12. Retention eligibility uses the minimum eligible checkpoint plus pins, key
    overlap and safety grace; the event TTL and wall-clock are ineligible.
13. Audit/evidence use only the closed privacy-safe allowlist and cannot become
    context, read or command evidence.
14. Canonical evidence is regenerated deterministically, validates under Draft
    2020-12 and covers every named scenario.
15. Focused tests adversarially mutate source/principal/position/disposition,
    frame lifecycle, atomic members, key intervals, retention and audit fields.
16. Static tests prove no application, migration, API, source, database,
    operational persistence, provider, command, runtime, deployment, Pages or
    protected-ref surface was added.
17. The claim remains provider-free, unmounted and authored-synthetic and names
    every live implementation surface as a later gate.

Evidence label:
`provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal`.

## Recovery and stop

One bounded mechanical correction is permitted for a deterministic schema,
test or serialization defect. A semantic failure in checkpoint disposition,
atomicity, frame retirement, restart, key or retention meaning returns to Sol's
recovery lease and requires a fresh no-finding review. Any non-inferable choice
between materially different privacy/reliability outcomes is a genuine user
fork; none is presently identified.

## Claim boundary and next dependency

Passing proves only pure authored-synthetic in-memory state transitions. It
does not prove a table, migration, source observation, delivery, credential,
database isolation/transaction, checkpoint persistence, crash recovery,
retention capacity, real invalidation, product read, patient privacy,
provider/model behavior, command safety, runtime, deployment or production.

After acceptance, the next safe candidate is a migration-and-transaction
architecture for the exact payload-free stream head/outbox and durability
state, still without live mounting, real product reads or provider/command
authority. That candidate must separately freeze PostgreSQL isolation, schema,
RLS/roles, producer rollback, credential binding, operational retention and
database-backed acceptance before any implementation.
