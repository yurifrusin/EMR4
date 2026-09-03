# Ariadne G1B.2 Pure Journal and Replay Plan

G1B.2 is defined here for a future, separately reviewed state transition. It is
not active in this candidate, and neither future implementation path exists.

## Identity and boundary

The future profile is `G1B.2_PURE_JOURNAL_REPLAY_KERNEL_ACTIVE`, the task class
is `g1b_2_pure_journal_replay_kernel`, and its complete implementation surface
is exactly `orchestration_harness/clockwork_journal.py` plus
`tests/test_clockwork_journal.py`. The module may import only the exact standard
library primitives needed for frozen records, a closed Enum vocabulary,
canonical JSON and SHA-256, plus the accepted public G1B.1 kernel. Admission is
not based on those descriptive properties: the controller compiles the original
runtime and test bytes without execution and requires their complete canonical
AST SHA-256 values to equal the two values frozen in
`g1b2-journal-replay-scope.yaml`. Any function-body, record, import, test or
top-level semantic substitution therefore fails closed.

The corrected canonical runtime AST is
`a514433e5b67312d0746e552f6a6e3d1ffb25d55056f4e7c7aabc344fe2b40fe`;
the corrected canonical test AST is
`07825bf0078dff36e490d27e46bf899bd1aead19c06bb77b46e811fb6e18aa83`.
The rejected runtime and test ASTs
`cd1aba1f360c25392e32dde56c2ca6cef1d66d08287f8e6b9309adecb00a4872` and
`2aa023fec78a41a720418d1b06bbf02914b0f79c885ca2727231819fc4a4a644` remain preserved
negative evidence and are not admissible.

The journal begins at sequence 1 with the fixed all-zero SHA-256 genesis value.
Every frozen `JournalEntry` binds its exact schema, sequence, previous-entry
digest, event, command, stored transition result and digest. A frozen
`ReplayResult` returns the derived state, next sequence, previous digest, fully
validated immutable journal prefix and an optional closed rejection. Canonical
compact sorted UTF-8 JSON is the only entry encoding, and the entry digest is
SHA-256 of those exact bytes.

`canonical_entry_bytes`, `entry_digest`, `append_entry` and `replay` are the
only functions in the public surface. Append first replays the complete input
tuple, constructs exactly one result with the accepted G1B.1 reducer, appends
one chained entry and replays the result. Replay checks collection and entry
types before attribute access, then schema, sequence, chain formatting and
predecessor binding, closed G1B.1 field types, invalid-code vocabulary and the
entry digest. Only then does it call the accepted reducer and compare success
versus invalid representation and canonical result bytes. A stored result is
evidence; it is never trusted merely because its shape is plausible.

Before `canonical_entry_bytes` compares, serialises, hashes or reads a `.value`,
it requires an exact `JournalEntry`; exact `str` schema, previous-digest and
digest fields; an exact non-boolean `int` sequence; exact `ClockworkEvent` and
`ClockworkCommand` members; an exact `TransitionResult`; exact nested state and
command members; and `None` or an exact `InvalidTransition` whose code is exact
`str`. Any foreign outer or field type raises only
`TypeError("invalid_clockwork_journal_entry")` before caller protocol dispatch;
`entry_digest` inherits the same boundary.

Replay closes each field before the operation that consumes it. A foreign
schema, digest field, event, command, result, nested state, nested command,
invalid object or invalid code returns `FOREIGN_TYPE`; a foreign or boolean
sequence returns `INVALID_SEQUENCE`. Only an exact wrong schema returns
`WRONG_SCHEMA`, and only an exact wrong invalid code returns
`UNRECOGNISED_INVALID_TRANSITION_CODE`. Every journal value therefore returns
an exact closed `ReplayResult`; caller comparison, ordering, length,
`startswith`, iteration, item-access, conversion, formatting, call and `.value`
protocols are never dispatched for rejected fields.

## Closed rejection vocabulary

The future kernel rejects wrong schemas, foreign types, boolean or non-positive
sequences, gaps, duplicates, reorder, wrong or malformed previous digests,
entry-byte tampering, stored-result mismatches, unrecognised invalid-transition
codes, success/invalid representation disagreement and mutable input
collections. There is no unreachable `noncanonical_serialization` member:
canonicality is represented by the one exact serializer and digest contract.
The exact frozen future tests call the real append and replay API, assert a
literal genesis entry byte sequence and digest, traverse a multi-entry hash
chain, rederive results, prove foreign entries are not inspected and reach every
closed rejection value. They additionally place a deterministic hostile
protocol sentinel in each outer and nested journal field, require the exact
closed rejection or fixed serializer error, and require a zero-event protocol
log. Set-literal or non-empty assertion substitutes fail the test AST binding.

## Explicit exclusions

Filesystem or Git access, process execution, network or database access,
environment, clocks, timezone, randomness, UUID, concurrency, native
interfaces, provider/worktree adapters, Raisa/EMR4 product code and every
existing clockwork writer or persistence adapter are closed. Mutable lease/CAS,
filesystem persistence, crash-safe append and narrative projection belong to
later G1B tranches. G1C remains blocked.

## Future transition only

The future state-only transition uses
`ariadne.programme_g1b1_to_g1b2_transition_manifest.v1`, emits an
`ariadne.g1b1-to-g1b2-transition.v1` artifact, and requires an independent
zero-finding `ariadne.external_g1b1_closeout_g1b2_enablement_review.v1` record.
It is one direct child of the reviewed controller, changes exactly five control
surfaces plus that new review and transition artifact, preserves the accepted
G1B.1 blobs and existing clockwork inventory, and requires fresh remote and
protected-ref readback. In development, the reviewed controller must still be
HEAD, the candidate count must be zero and the staged seven-path index tree is
frozen into the pinned operation binding and external receipt before mutation.
The pinned exact-index commit path creates that direct child from precisely
that tree. Pre-push and post-push admission then require that one child and the
same exact tree. Raw Git commit bypasses are not part of the lifecycle. This
candidate defines that transition; it does not perform it.
