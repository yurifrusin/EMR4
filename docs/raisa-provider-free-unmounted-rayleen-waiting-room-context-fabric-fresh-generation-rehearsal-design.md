# Provider-free unmounted Rayleen fresh-generation rehearsal design

Date: 2026-08-06

Status: frozen provider-free authored-synthetic design

## Boundary classification

This descendant exercises an already-described fresh reassembly sequence with
newly authored synthetic completed-read-shaped inputs. It neither performs a
read nor implements a watcher. The API Spine remains unchanged: GraphQL/read
models are read-only, REST/OpenAPI remains the sole future command plane,
event metadata only invalidates, and backend typed code owns policy,
reconstruction, admission and proofreading.

## Generation packet

`RayleenFreshGenerationPacket` is a recursively closed sealed aggregate with:

- the accepted predecessor packet and requirement digests;
- `FreshGenerationAuthorityTrace`;
- `RequiredDependencyRefreshTrace`;
- second Diary-source and waiting-adapter provenance digests;
- unaffected-source carry-forward trace;
- new Current frame-set/source/weave/proofreader digests;
- new temporal manifest and lease;
- one admitted-generation record;
- one older-result rejection and two completion-order traces;
- old-generation immutability/non-restoration trace; and
- final same-packet proofreader trace.

Large source payloads need not be duplicated in the released aggregate. They
remain authoritative reconstruction inputs and are represented by exact sealed
digests and minimum safe synthetic outcome fields.

## Fresh authority and request identity

The accepted session authority binding is revalidated at a later assembly
instant. A newly authored synthetic request candidate uses a new need id and a
monotonically newer request revision. Accepted public policy functions derive a
new context need and grant. A generation-authority trace proves the new grant
does not widen any parent authority, scope, disclosure, time, freshness, item,
byte or execution ceiling.

Request revision is not session generation. The session remains the same only
while the accepted binding is valid; the new request revision distinguishes
concurrent results inside that session. Any session-generation mismatch fails
before request supersession is considered.

## Required refresh and carry-forward

The predecessor requirement, not the implementation, decides refresh coverage.
The accepted signal intersects Diary and waiting-room dependencies, so both
receive newly authored synthetic completed-read-shaped inputs. Event metadata
contains no replacement fields and is never consulted when authoring them.

Directory and private-session sources may carry forward only because they are
not named by the requirement and remain granted, coherent and unexpired at the
new assembly instant. Their complete canonical values and digests stay
unchanged. This is a deterministic optimization proof, not retention or cache
authority; changing requirement impact or freshness makes carry-forward fail.

## New Current generation

The second waiting frame passes through a fresh request-scoped alias manifest,
accepted adapter and sole extractor-recomputed handoff. Its resulting source
and the new Diary envelope are combined with eligible unaffected sources.
The unchanged assembler and proofreader must produce `RELEASE` for a frame set
whose need id, frame-set id, digest and source trace are distinct from the
retired parent.

A new temporal manifest and lease are derived only from that exact released
frame set. No old checkpoint, manifest or lease is copied. A sealed local
generation-state record may say `CURRENT`; it is evidence inside this packet,
not a mounted runtime state or persistent checkpoint.

## Admission and supersession

`FreshGenerationAdmission` is a pure deterministic gate. It binds the exact
predecessor requirement, fresh authority trace, refresh trace, Current
proofreader, new frame-set digest, new manifest/lease and the currently active
request coordinates. It admits only when all upstream proofs pass and releases
only a deep copy of the trusted reconstruction.

The accepted temporal stale-result assessor separately evaluates the older
request coordinate against the newer current revision and must return
`REJECT_SUPERSEDED_REQUEST`. Two pure ordering simulations prove convergence:

- if the old result completes first, it is never admitted and the new result
  becomes current; and
- if the new result completes first, the later old completion is rejected and
  cannot restore the retired frame set.

No scheduler, task, callback or asynchronous worker exists in this rehearsal.

## Proofreader

The final proofreader accepts only the original authoritative parent inputs and
the newly authored second-generation inputs. It reconstructs the predecessor,
new request/grant, refreshed sources, adapter result, Current weave, temporal
objects, admissions and ordering traces. Canonical equality is the release
condition.

It additionally verifies exact-type closure, validity windows, no-wider
authority, complete requirement coverage, source independence from event
metadata, carry-forward eligibility, distinct generation identity, old-frame
immutability, new-result admission, older-result rejection and all-false
provider/command/runtime ceilings. Supplied packets are never repaired.

## Schemas and evidence

JSON Schemas recursively close the generation packet and evidence. The
authored-synthetic example is the exact released packet without product or
external data. Evidence records closed cases, expected dispositions, direct
artifact hashes and static surface counts under
`provider_free_authored_synthetic_unmounted_rayleen_fresh_generation_rehearsal`.

## Non-authority statement

This design does not establish that a real change is observed, a read is
authorised or delivered, a checkpoint survives restart, or a model receives
context. It proves only that already completed synthetic inputs can create one
new typed frame generation and that an older result cannot supersede it.
