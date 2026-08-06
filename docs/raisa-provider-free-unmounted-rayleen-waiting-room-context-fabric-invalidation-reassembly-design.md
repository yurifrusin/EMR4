# Provider-free unmounted Rayleen invalidation/reassembly seam design

Date: 2026-08-06

Status: frozen provider-free authored-synthetic design

## Boundary classification

The seam composes two already accepted pure read-context protocols. The Rayleen
source adapter supplies one minimal Current waiting-room envelope after an
authorised read has already completed. The temporal weave decides only whether
the immutable resulting `ContextFrameSet` remains usable. Neither protocol
creates a read, event consumer, provider call, command, write or API route.

The EMR4 API Spine distinction remains intact:

- GraphQL/read models may later expose fresh context but receive no change here;
- committed-event metadata is a non-authoritative invalidation signal;
- REST/OpenAPI remains the sole future command plane;
- manifests declare and narrow dependencies but do not execute policy;
- backend typed code owns authority, reconstruction and proofreading.

## Composition packet

`RayleenInvalidationReassemblyPacket` is a closed, sealed aggregate containing:

- `adapter_binding_trace`;
- `dependency_manifest` and `watch_lease`;
- the one payload-free signal;
- invalidation decisions and watcher transitions;
- committed checkpoint and monotonic frame-set state;
- exactly one reassembly requirement;
- `fresh_reassembly_instruction`;
- stale-result decision;
- temporal trace; and
- same-packet proofreader trace.

It deliberately does not duplicate the full parent frames or source payloads.
Their authoritative values remain inputs to reconstruction and are referenced
only by exact digests in the packet.

## Adapter-to-temporal binding

The binding trace is derived only after:

1. the adapter recomputes the A4 source from frame, binding, grant and alias
   manifest;
2. the extractor reruns the adapter and returns a deep copy of its recomputed
   envelope;
3. the envelope replaces only the parent waiting source;
4. the unchanged Current assembler creates a new frame set; and
5. the unchanged Current proofreader returns `RELEASE`.

The trace binds:

- source frame digest;
- alias manifest digest;
- adapter result and trace digests;
- extracted source-envelope id, revision and digest;
- rebuilt source-trace digest;
- the exact waiting frame id/digest/source digest; and
- rebuilt frame-set id/digest plus binding and grant digests.

The waiting frame source digest must equal the extracted envelope digest. The
dependency manifest's waiting dependency must then repeat that exact frame and
source chain. A self-consistent reseal cannot substitute for reconstruction.

## Signal and invalidation semantics

The signal is created by the accepted temporal constructor, not accepted as an
arbitrary object. Its closed schema excludes event payloads. It cites one newer
authored-synthetic waiting-state aggregate revision and the next exact stream
transaction position.

The accepted temporal processor owns classification. If the signal intersects
more than the waiting-room dependency, the requirement truthfully lists every
affected dependency; the seam never narrows a real impact merely to make the
source-adapter story simpler. The only mandatory seam-specific invariant is that
the adapted waiting dependency is present.

The processor records its checkpoint and transition before any imagined fresh
read. Its output must be `REASSEMBLY_REQUIRED`, `usable_for_new_reasoning: false`
and `frames_mutated: false`. Subsequent lifecycle work creates a different frame
set; it never patches or restores this one.

## Inert fresh-reassembly instruction

`FreshContextReassemblyInstruction` translates the temporal requirement into a
typed description of the future backend-owned sequence. It binds the exact
superseded set, manifest, lease, requirement, adapter result and waiting-source
digests, session generation, request revision and expiry.

Its ordered steps are fixed:

1. `fresh_authority_check`;
2. `fresh_waiting_room_source_read`;
3. `rerun_waiting_room_source_adapter`;
4. `assemble_new_current_weave`;
5. `same_packet_proofread`.

These are labels, not callbacks, URLs, commands or executable function names.
The object fixes all execution and authority flags to false and returns no data.
It cannot be treated as permission to call the current source, inspect the old
event payload or reuse the superseded frame.

## Proofreader

The seam proofreader accepts the original authoritative A4 frame, parent packet,
alias manifest inputs and signal coordinates. It reconstructs the adapted
parent, manifest, lease, signal, temporal result, binding trace and instruction
through accepted public functions. Canonical packet equality is therefore the
release condition.

It additionally verifies:

- the parent Current proofreader released;
- the waiting envelope/frame/dependency digest chain is exact;
- temporal state is monotonic and the parent bytes are unchanged;
- exactly one requirement exists and the waiting dependency is included;
- no event payload became context;
- no source read or command was executed;
- the stale-result decision is a rejection; and
- all read, command, provider, execution and returned-data ceilings are fixed.

The released packet is a deep copy of the trusted reconstruction. A supplied
packet is never repaired or partially admitted.

## Schemas and evidence

JSON Schemas recursively close the packet, binding trace, instruction and
evidence. The accepted temporal objects remain validated by deterministic
reconstruction and their existing seals. The authored-synthetic example is the
exact released packet without external or product data.

Evidence records case identifiers, expected dispositions, artifact hashes and
static surface counts. It is repository-local proof only and carries the label
`provider_free_authored_synthetic_unmounted_rayleen_invalidation_reassembly_seam`.

## Non-authority statement

This design contains no live watcher. It does not prove that a database change
will be delivered, that a checkpoint survives a crash, or that a fresh source
read is authorised. It only proves that an already accepted adapter-built frame
set can be deterministically retired and converted into one inert requirement
without becoming a command or treating event metadata as truth.
