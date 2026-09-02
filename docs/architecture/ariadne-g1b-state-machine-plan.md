# Ariadne G1B State-Machine Plan

## Status and authority

This is a review-pending design and extraction boundary, not a G1B
implementation. The programme remains at `G1A.3`; G1A closeout awaits external
review, G1B is closed pending a separately reviewed state transition, and no
G1B task is currently eligible.

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
remain byte-exact at the accepted source. G1B.1 may reuse their pure vocabulary
only; filesystem, Git, live publication and migration/cutover behavior stay
behind adapters and are not implemented or executed by this candidate.

## State-only transition seam

After this controller candidate receives a zero-finding external PASS, a clean
gatekeeper pinned to the exact reviewed candidate may evaluate one direct-child
`G1A_TO_G1B1_STATE_TRANSITION`. The transition is limited to the seven declared
control-plane paths, binds the reviewed candidate, before-state and
before-policy digests, accepted-surface and clockwork-scope physical digests and
Git blobs, exact semantic pointer delta, production destination, expected
remote head and fresh readback. It closes G1A and activates G1B.1 as state; it
does not implement G1B.1.

## Bounded G1B.1 kernel

The future profile is `G1B.1_PURE_STATE_EVENT_KERNEL_ACTIVE`, task class
`g1b_1_pure_state_event_kernel`. Its allowed implementation paths are exactly:

- `orchestration_harness/clockwork_state.py`
- `tests/test_clockwork_state.py`

Both paths are absent from this candidate. The kernel will be limited to closed
typed state, event and command schemas; a pure transition/reducer function;
invalid-transition rejection; explicit schema versions; and canonical,
deterministic serialisation. It will not import filesystem, Git, network,
subprocess, database, clock, randomness, environment, provider, integration,
product, worktree or existing clockwork runtime adapters.

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
runtime mutation, G1C work, and protected-ref movement remain closed. The next
action is external review of the G1A closeout and G1B transition-enablement
candidate only.
