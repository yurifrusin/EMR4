# Relay-free check-in rollback and unknown-commit recovery rehearsal blocked closeout

Date: 2026-08-19

Timestamp: 2026-08-19T21:18:50.8703927+10:00 (Australia/Brisbane)

Status: **blocked — not accepted**

## Result

The single authorised occupied execution failed closed before PostgreSQL
started. Static admission and internal-network inspection passed, but the newly
created server container was rejected during profile admission before its full
ID returned to the outer cleanup owner. No credential was delivered, no
database process or SQL started, no transaction ran and no success or retry was
released.

The immutable failure artifact records `cleanup/exact_cleanup_unverified`
because final cleanup overwrote the earlier server-profile coordinate. Its
SHA-256 is
`5c38080aa27615ea1efad166d14a61605596130058498ea03c8b631bbeae3be2`.
The lifecycle and exact residue inspection bound the failure to server
creation/profile admission without claiming the unavailable predicate.

Exact recovery inspection found one never-started, unpublished, unmounted,
harness-labelled container. Its full ID, name prefix, exact cached image,
ownership-nonce shape and Created/non-running state were verified before only
that object was removed. Matching containers and networks are now zero. The
failure artifact remains immutable; the separate cleanup-recovery artifact
records the later recovery.

The intended rollback-zero and lost-terminal-response/readback proof was not
reached. This tranche therefore does not close the
`atomic_effect_rollback_and_unknown_commit_recovery` evidence gap and grants no
ordinary check-in readiness.

## Static repair

Exact repair source `fc772085a02d7db790b938fb845ef4546156d31e`:

- makes network admission depend on exactly one attachment with the captured
  `NetworkID`, rather than Docker's runtime network-map key;
- gives every acquisition helper a closed two-outcome contract: return its
  captured ID to the sole cleanup owner or verify and remove only its exact
  owned object before raising;
- retains closed failed-predicate names; and
- preserves the earliest causal error while recording cleanup issues
  separately.

The repair passed 17 focused harness/plan tests, Ruff and compilation. Static
admission passed 366/366 hostile contract mutations, 96/96 manifest mutations,
24/24 classifier packets and 96/96 OCI states. The canonical latch, Current
Baton and error-register surrounding suite passed after the blocked
publication. This is static repair acceptance only; attempt 001 remains
consumed and no rerun occurred.

## Clockwork closeout

An attempted hand-maintained register/report projection was rejected by the
clockwork's canonical-drift gate before publication. Those draft projections
and their test fixtures were restored to the preceding clockwork-owned bytes
at exact descendant source
`2bb9d41cfe0a6368389d5a26f7c5e593515296e1`. They are not canonical evidence
and no second writer remains.

The dry run and one pointer-last publication then passed at generation
`gen-e742878078cc53f6696e1b117c55f641d717d30ebd3a36ab451c4949efa9bb2a`,
lease sequence 12. The reading reports ten clockwork-owned surfaces, zero dual
owners, zero canonical drift, zero caller-authored derived fields and zero
bespoke updater executions. Its `blocked_transition` changed only the active
latch and clockwork metadata; Continuity, Compass, Current Baton and canonical
register projections did not advance.

The latch is now `blocked`, has no next executable stage, requires Yuri's
attention and permits this terminal handback.

## Parallelism disposition

- DeepSeek was not dispatched. Its native-Harness boot proof remains a separate
  prerequisite and Claude Code was not used as fallback.
- Gemini was reserved for a post-success exact-candidate veto and was therefore
  not called after deterministic occupied failure.
- Native subagents were not used because the current developer policy and the
  single cleanup owner require serial execution.

## Closed boundaries

No feature flag or authored-synthetic allowlist changed. No product,
configuration, route, API/OpenAPI/GraphQL, schema, action grammar, first-party
client, generic-status `Arrived`, waiting-area or ordinary-practice behavior
changed. No product, patient, appointment, clinical, historical or protected
data, provider workload, production runtime, deployment, release, Pages or
protected-ref movement occurred.

Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. `docs/branding/` and all unrelated
untracked files remain preserved.

The non-PHI Pushover notification succeeded with request
`a528b280-cfb5-49ed-859f-e17d3e757a12`.

## User-attention fork

Yuri must choose whether to:

1. authorise a separately frozen descendant plan for one new occupied attempt
   using the statically repaired harness; or
2. defer this operational-evidence gap and leave ordinary check-in admission
   not ready.

The current plan authorises neither a second execution nor an inferred product
successor.
