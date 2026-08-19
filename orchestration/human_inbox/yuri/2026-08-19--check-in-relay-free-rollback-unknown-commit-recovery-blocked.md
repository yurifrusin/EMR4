# Relay-free check-in rollback and unknown-commit recovery — blocked

Date: 2026-08-19

Timestamp: 2026-08-19T21:18:50.8703927+10:00 (Australia/Brisbane)

Yuri attention required: **yes**

## Lay summary

The single allowed database rehearsal stopped safely before PostgreSQL even
started. A temporary server container did not match the harness's own profile
check. The first cleanup path lost track of that never-started object, but I
identified it using its full ownership evidence, removed only that object and
verified that no matching container or network remains.

Nothing reached the database: no password was delivered, no SQL or transaction
ran, no success was announced and nothing was retried. I repaired the harness
so a future acquisition must either hand its exact resource ID to cleanup or
clean that exact owned resource itself, and so a cleanup issue cannot hide the
original failure. The repair passes its complete static and focused test packet,
but it cannot turn the consumed attempt into a successful database proof.

The clockwork also earned its keep. It rejected my attempted hand-maintained
register update as a second-writer drift, so I restored the canonical
projections and let the clockwork publish only the honest blocked reading.
There was no Continuity/Compass or product advance.

## Technical summary

- Immutable failure SHA-256:
  `5c38080aa27615ea1efad166d14a61605596130058498ea03c8b631bbeae3be2`.
- Lifecycle reached static admission and captured internal-network admission,
  then failed during server profile admission before PostgreSQL startup.
- Cleanup recovery verified exact full ID, prefix, cached image, harness label,
  nonce shape, Created state, zero published ports and zero bind mounts; matching
  containers/networks are now zero.
- Repair source: `fc772085a02d7db790b938fb845ef4546156d31e`.
- Static gates: 366/366 contract mutations, 96/96 manifest mutations, 24/24
  classifier packets and 96/96 OCI states rejected; 17 focused tests, Ruff and
  compilation passed. Canonical latch/Baton/register surrounding tests passed.
- Clockwork source:
  `2bb9d41cfe0a6368389d5a26f7c5e593515296e1`; generation
  `gen-e742878078cc53f6696e1b117c55f641d717d30ebd3a36ab451c4949efa9bb2a`,
  lease 12, zero drift, zero dual owners and no bespoke updater.
- DeepSeek was not eligible pending its native-Harness boot proof; Gemini was
  not eligible because the occupied proof failed; native subagents remained
  serially constrained.

## Deliberately closed

No ordinary-practice activation, feature/allowlist change, product/API/client
change, generic-status `Arrived`, action grammar, waiting-area movement, data,
provider workload, production, deployment, release, Pages or protected-ref
movement occurred. `docs/branding/` and unrelated untracked files are
preserved.

The non-PHI Pushover notification succeeded with request
`a528b280-cfb5-49ed-859f-e17d3e757a12`.

## Decision needed

My recommendation is to authorise a separately frozen descendant plan for one
new occupied attempt using the repaired harness. The alternative is to defer
this evidence gap and leave ordinary check-in admission not ready.

The current plan authorises no second run.
