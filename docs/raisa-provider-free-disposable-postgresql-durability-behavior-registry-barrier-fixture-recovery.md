# Disposable PostgreSQL behavior registry-barrier fixture recovery

Date: 2026-08-08

Status: provider-free recovery candidate; runtime closed pending fresh veto

## Trigger and exact evidence

Behavior attempt 016 admitted the corrected inert artifact and reached
`BTR-E01` under the required serializable boundary. It then stopped before
admitting a scenario with SQLSTATE `CF004` at internal line 51 of
`emr4_context_fabric.register_observer_generation_v1`.

The complete failure evidence is preserved at
`provider-free-behavior-transaction-failure-evidence-016.json`, SHA-256
`f5b7a272d52586ec1772f4906a6f7a26f58620efea944f61199b99c3ab4215ef`.
The exact owned container
`c6ee08840cbfc448a1329c0134efda4ea424e5476ff7e6369136aef81225070b`
was removed and absence was verified.

## Diagnosis

The released coordinate maps to the accepted `LOCK_EXACT` read of
`context_generation_registry_barrier`. The typed body contract and accepted
design require registration to lock and later advance that shared barrier;
the body's derived effect summary contains a barrier update and no barrier
insert. Bootstrap authority is explicitly outside the claimed role-behavior
boundary.

The behavior bootstrap created the complete beta isolation topology, including
its barrier, but did not create the alpha barrier required by `BTR-E01`. Its
delta table simultaneously expected registration to add one barrier row. That
misattributed a prerequisite fixture effect to an entry point that has no such
authority.

## Bounded correction

The recovery:

- creates exactly one authored-synthetic alpha practice/source/stream barrier
  at revision zero during bootstrap;
- changes only the alpha barrier row-count expectation from `+1` to `0` while
  retaining it in the allowed digest-change set;
- adds a private post-scenario proof that exactly one alpha barrier exists and
  its revision is exactly `3` after the three separate registrations; and
- preserves attempts 001-016 and validates the exact attempt-015 and
  attempt-016 function coordinates and cleanup facts.

No behavior-contract scenario, order, principal, SQLSTATE, transaction shape,
readback name, forbidden effect or category count changes. The canonical
behavior contract remains
`sha256:0ac09578c56aeb6528f5a05dc1e32f5b71d953dfd43ab6d8b5030cab202e7d03`.
The accepted body contract, rendered SQL, parse/catalogue evidence, Docker
profile and authority boundary remain unchanged.

## Runtime gate

Attempt 017 remains closed until the corrected harness and evidence packet
pass deterministic tests, Ruff and diff checks and one fresh exact-HEAD Gemini
3.6 Flash/high read-only veto from a clean worktree. A later eligible run is
still limited to one newly owned, pull-never, networkless, portless,
mountless, tmpfs-backed disposable PostgreSQL 16 container with exact-ID
cleanup.

There is no patient, clinical, product-derived or protected data; no provider
or external retrieval; no application/API/Diary wiring, operational database,
watcher/listener/feed, command or product write, deployment, production,
release, Pages or protected-ref movement. `docs/branding/` and all unrelated
untracked files remain preserved and excluded through explicit-path staging.
