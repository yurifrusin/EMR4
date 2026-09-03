# Ariadne G1B State-Machine Plan

## Status and authority

G1B.1 is implemented and externally accepted at exact commit
`faaf2d2b4e72c823b79d9da9aed49f0182125748`. Its accepted two-file surface and
byte-exact PASS are frozen by `orchestration/programme/g1b1-accepted-surface.yaml`.
The programme remains at `G1B.1` in the review-pending `G1B-C0` controller
profile. G1B.1 closeout is not yet accepted, G1B.2 is closed pending a separate
state transition, and no implementation task is eligible.

The source inventory is
`orchestration/programme/g1b-clockwork-scope.yaml`, bound to commit
`23aa3ab19aec6cee9246e7dd3a88f61ada39bd7a` and tree
`e06fbf5c5f46b7a637a1d2987ce34c8f37990283`. It records the existing schemas,
reducers, writers, journals, leases, replay paths, projections, adapters,
fixtures, coupling and historical fixture failures without changing them.

The pre-closeout `current-state.json` `harness_inventory.clockwork_core` is the
minimum closed inventory, not an illustrative subset. In particular,
`governance_live_adoption.py` and `governance_migration.py` are
authority-bearing writer/cutover surfaces. The former owns live single-writer
publication, canonical replacement, retirement and byte-exact rollback. The
latter owns canonical-mirror generation preparation, migration leasing,
ownership transfer, pointer-commit cutover and immutable-generation recovery.
Their exact source blobs, direct CLI adapters, importing tests, and historical
contract/intent/evidence fixtures are enumerated one-for-one in the scope.

The scope also records per-module persistence format, atomic commit point,
lease/CAS checks, replay and recovery semantics, structured-versus-narrative
authority, EMR4 coupling, and extraction disposition. These runtime modules
remain byte-exact at the accepted source. Neither this controller nor the future
G1B.2 kernel imports, changes or executes them.

## State-only transition seam

After this controller candidate receives a zero-finding external PASS, a clean
gatekeeper pinned to that exact reviewed candidate may evaluate one direct-child
`G1B1_TO_G1B2_STATE_TRANSITION`. The transition changes exactly seven declared
control-plane/evidence paths and binds the G1B.1 PASS, reviewed controller
commit/tree/sole parent, recomputed before-state and before-policy digests,
accepted G1B.1 surface and Git blobs, exact semantic pointer delta, production
destination, expected remote head and fresh readback. It closes G1B.1 and
activates G1B.2 as state; it does not implement G1B.2.

## Frozen G1B.1 kernel

The accepted profile was `G1B.1_PURE_STATE_EVENT_KERNEL_ACTIVE`, task class
`g1b_1_pure_state_event_kernel`. Its complete implementation is exactly:

- `orchestration_harness/clockwork_state.py`
- `tests/test_clockwork_state.py`

Both files remain byte-identical to the externally reviewed commit. The closed
typed state/event/command vocabulary, pure total reducer, invalid-transition
result and canonical deterministic serialization are accepted. The reducer is
a typed internal API; G1B.2 owns untrusted journal-boundary validation.

## Defined G1B.2 kernel

`docs/architecture/ariadne-g1b2-journal-replay-plan.md` and
`orchestration/programme/g1b2-journal-replay-scope.yaml` define the future pure
versioned journal and deterministic replay kernel. Its only future paths are
`orchestration_harness/clockwork_journal.py` and
`tests/test_clockwork_journal.py`; both are absent in this candidate.

## Extraction boundary

Portable Ariadne mechanics include schema vocabulary, pure deterministic
reduction, canonical serialisation and hashing, invalid-transition rules, and
lease/CAS and journal validation vocabulary. Filesystem persistence, Git
observation, subprocess and provider adapters, EMR4 product coupling, Raisa
narrative projections, and every existing clockwork writer remain outside the
pure kernel.

Structured state, events and manifests are authoritative. Markdown remains a
derived narrative projection. Existing clockwork modules and their tests stay
unchanged and are used only as inventory and later compatibility evidence.

## Closed boundaries

Provider invocation, integration execution, product and migration work,
dependency or workflow changes, deployment and Pages work, existing clockwork
runtime mutation, persistence, G1C work, and protected-ref movement remain
closed. The next action is external review of task generation
`g1b1-closeout-g1b2-enablement-field-protocol-closure-replacement-20260903-v1`
only. That replacement retains the canonical staged exact-index transition
lifecycle but closes every future journal and nested transition-result field
type before protocol use; it does not perform the transition.
