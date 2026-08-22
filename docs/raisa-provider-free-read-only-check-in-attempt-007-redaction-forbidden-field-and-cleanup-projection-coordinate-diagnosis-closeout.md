# Provider-free read-only check-in attempt-007 redaction and cleanup-projection diagnosis closeout

Date: 2026-08-23

Timestamp: 2026-08-23T04:09:17.7509356+10:00 (Australia/Brisbane)

Status: `accepted`

Exact frozen plan source:
`3240c0a00dcce1ea9c07907a1d67b2493c8f33ed`

Exact diagnosis candidate source:
`ca7970b3520b2c38e9abd6fee3462ebb743792e0`

## Result

The read-only diagnosis passes. It enumerates 67 prospective final-result key
paths and finds exactly one conflict with the accepted redaction vocabulary:

`closed_boundaries.live_secret_existing_hosted_or_product_database_used`

The accepted predicate returns `redaction/forbidden_field` on that exact key.
AST evidence proves the result is constructed before cleanup, cleanup is
finalized in the lifecycle `finally`, and final result redaction runs afterward
outside the earlier base failure handler. A pure wrapper fake then proves the
escaped typed failure is converted through a literal
`{"status": "not_started"}` projection instead of the finalized cleanup
object.

The diagnosis therefore accepts three exact coordinates:

- `prospective_success_projection_forbidden_field`;
- `post_cleanup_result_redaction_escape`; and
- `wrapper_untyped_post_finalization_cleanup_collapse`.

It accepts no transaction or database result from attempt 007.

## Selected repair boundary

The smallest future repair has two inseparable deterministic gears:

1. a complete prospective-success structural projection passed through the
   exact redactor during static admission before any occupied work; and
2. a base-owned typed post-finalization terminal bridge that carries only the
   already-finalized cleanup projection into sanitised failure evidence.

The exact conflicting closed-boundary field must be safely renamed or
projected without weakening redaction or changing false/default denial.
Hostile tests must prove a new conflicting key is rejected before occupied
work and a forced post-finalization failure retains the exact finalized cleanup
projection.

## Verification

- 25 focused diagnosis and plan tests passed after idempotent postcommit
  readback repair.
- 164 serial focused/broader diagnosis, predecessor, no-database, latch, Baton
  and clockwork tests passed.
- Ruff, Python compilation, exact schema validation, canonical readback and
  `git diff --check` passed.
- The canonical diagnosis evidence SHA-256 is
  `b6d473d20fa64757fc25fbd2eb4f1792d86ebc91e3f0a8bf5bb3c9bdcc62d8e4`.
- Docker object commands, PostgreSQL starts, SQL/database operations, provider
  requests and product effects were all zero.

## Workflow efficacy

The substantive loop narrowed: no occupied retry occurred, and a database run
is no longer required to expose either defect. The two future repair invariants
are now deterministic preconditions.

Five low-cost orchestration lapses remained: one nonexistent Baton-test path,
one missing serial-runner separator, one long-run session identifier not
retained by the orchestration wrapper, one prohibited direct edit of the
clockwork-owned latch, and one evidence readback that initially rebound to the
new live HEAD instead of its original full ancestor. The session lapse caused a
redundant second 164-test run; the clockwork rejected the latch drift before
publication. No event changed external state. They are registered so future
commands use discovered paths, typed runner/session forms, clockwork-only
canonical writes and stable full-object evidence bindings.

## Claim and authority boundary

Attempt 007 remains immutable and consumed. Rollback, unknown-response commit
recovery, transaction membership, role absence before teardown and internal
cleanup history remain unproved. Its separately accepted zero-owned-Docker-
resource observation is unchanged.

No attempt 008, Docker object, PostgreSQL process, SQL, database operation,
DeepSeek worker, provider, ordinary-practice enablement, feature flag,
allowlist, API, route, grammar, client, waiting-area, product/patient/clinical/
protected data, production, deployment, release, Pages or protected-ref
authority is opened. Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. `docs/branding/` and all unrelated
untracked files remain preserved.

## Next tranche

Proceed under standing authority with
`raisa-provider-free-check-in-prospective-success-redaction-and-typed-cleanup-projection-conformance-repair`.
It may implement and exhaustively test only the two selected deterministic
gears. It creates no Docker object, starts no PostgreSQL process, executes no
SQL or database operation, and does not plan or authorise attempt 008.
