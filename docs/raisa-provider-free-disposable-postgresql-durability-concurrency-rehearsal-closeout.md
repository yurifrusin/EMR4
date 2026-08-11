# Provider-free disposable PostgreSQL durability concurrency rehearsal closeout

Date: 2026-08-11

Result:
`raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_pass`

Accepted runtime source HEAD:
`fed81847b4155d49cf997905e79cf31808ceb017`

Exact independently reviewed functional source HEAD:
`43f168f3d5d1f71ec0f9071c40fadf14b6107621`

Immutable pass evidence SHA-256:
`7dd7372a8f45b6a049aca4f835057a33ab37952be98088bbbf34ed94875dd0e4`

## Accepted result

CF-D1 passes all six frozen two-session races against the exact accepted
authored-synthetic PostgreSQL 16 Context Fabric durability schema. Every pair
proved simultaneous overlap through leader `Timeout/PgSleep` and contender
`Lock` observations before either result was admitted.

- `CFD1-C01`: one observer-generation registration committed, the concurrent
  contender failed with `40001`, and the fresh replay was inert.
- `CFD1-C02`: concurrent producer allocations committed at exact monotone
  positions 1 and 2.
- `CFD1-C03`: identical concurrent admission returned the same `PRIMARY`
  identity to both sessions without a duplicate effect.
- `CFD1-C04`: the leader admitted `PRIMARY`, the divergent contender failed
  with `CF004`, and fresh conflict plus replay readback remained exact.
- `CFD1-C05`: the coordinator leader returned `RECEIPT_APPLIED`, the contender
  failed with `40001`, and fresh replay returned native
  `RECEIPT_REPLAYED` without changing state.
- `CFD1-C06`: the injected leader returned `RECEIPT_APPLIED` then rolled back
  with fixed `P0001`; the waiting contender committed the sole durable
  coordinator effect, and fresh replay was inert.

All 22 relation snapshots reconciled before and after each race. The harness
started exactly 12 participant and 11 precondition transactions, performed no
automatic retry, passed all six scenarios in frozen order and admitted the
pass evidence as a whole document.

The result binds concurrency contract SHA-256
`96b3fb92d302206eb757f51203044c2aeeb76248a6844422404d13c79b785391`,
contract-schema SHA-256
`e5d89547cea0fd7a890e9000b034316d935072a6ced5fccab8c8508530116f95`,
accepted inert SQL SHA-256
`dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`
and render-manifest SHA-256
`2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`.

Exact container
`0e8900cf035d9af6e38926d43586f9510efd2ef36a39410377054fbe0e9ee175`
was ownership-reverified, removed and confirmed absent. The exact harness label
then matched zero containers. Provider calls, product reads, product commands
and external-network operations were all zero.

## Independent verification and recovery provenance

The planning and implementation each passed a genuinely fresh Gemini 3.6
Flash/high read-only veto before runtime. The final recovery veto inspected
exact clean functional source `43f168f3d5d1f71ec0f9071c40fadf14b6107621`,
passed 213 AER, 27 implementation and 14 plan tests (254 total), Ruff, format,
compilation and Git checks, and performed zero Docker, database, provider,
product or external-network operations.

Attempts 001 through 003 remain immutable failures and are not promoted:

- attempt 001 exposed a direct-file package bootstrap defect before Docker;
- attempt 002 exposed non-actionable failure telemetry and false static
  transaction accounting;
- attempt 003 proved the telemetry correction and isolated CF-D1's
  `RECEIPT_REPLAY` misspelling against the accepted native
  `RECEIPT_REPLAYED` enum.

AER-0269 through AER-0272 record and close those controls at register revision
239. Each recovery preserved the frozen SQL, race topology, isolation,
principal, overlap, effect and cleanup contracts and used a distinct evidence
path.

## Claim boundary

This is evidence only for the six fixed two-session concurrency outcomes and
their bounded lock overlap, monotone effect, replay, outer rollback,
least-privilege identity and exact cleanup. It is not a literal-infallibility,
arbitrary-deadlock-freedom, load, performance or operational-availability
claim.

It does not prove crash or server restart behavior, unknown commit, automatic
retry policy, more than two participants, key rotation, retention or purge,
migration operation, long-lived persistence, application/API/Diary wiring,
watcher/listener/source access, real/product/patient/clinical data, provider
use, executable tools, commands, deployment, production, release, Pages or
protected-ref safety.

## Programme handoff

CF-D1 is closed successfully at Continuity 243 / Compass 225. The next
dependency-satisfied planned direction is CF-D2: a provider-free disposable
restart and unknown-commit recovery rehearsal. CF-D2 must begin with a fresh
five-source rehydration and its own narrow fail-closed plan before any runtime.
It inherits no operational database, product data, provider, command,
deployment or protected-ref authority from this result.
