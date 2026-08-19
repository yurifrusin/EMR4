# Provider-free check-in relay-free recovery attempt 003 plan

Date: 2026-08-19

Timestamp: 2026-08-19T23:20:30.4199339+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`dd9f0f8469b04bd91ddf38888032ce38a93926a5`

Accepted Created-state correction source:
`02a1fbfaa517a0d2a2dff66f31fabe482653c430`

Accepted Created-state reviewed candidate:
`260eeda97a3204a39b0f639d216fd7a53c0d2014`

Accepted Created-state closeout transition source:
`cf7e86c19e0a33c9702359f4ee4439c4f86ff977`

Accepted relay-free transport source:
`4f0f54c2b0861828f9994444201b8da1bd54be00`

Accepted runtime-role and tenant-isolation source:
`6a2832575e9b4df5c40a13984db7281e79814a94`

Operation:
`raisa-provider-free-check-in-relay-free-recovery-attempt-003`

Target result:
`raisa_provider_free_check_in_relay_free_recovery_attempt_003_pass`

Reasoning level: Extra High freezes the one-run authority, corrected harness,
immutable predecessor evidence, transaction identity, forced-RLS, OCI outcome
and exact cleanup boundaries. High is sufficient for the fixed adapter,
deterministic admission, one occupied execution, independent veto and
clockwork closeout.

## Authority and objective

Yuri has given standing authority to continue under Sol's recommended course
until this tranche reaches its aim and then into the next dependency-satisfied
tranche, without further permission unless a truly extraordinary fork occurs.
This plan converts that authority into exactly one newly named attempt-003
occupied execution only after deterministic, clockwork and fresh five-source
preexecution admission all pass.

The one execution must prove, in one uniquely named provider-free disposable
local PostgreSQL 16 environment, that:

1. an authored-synthetic effect/receipt/audit transaction is explicitly
   rolled back and fresh restricted-role readback observes zero members;
2. a disjoint transaction commits once and loses its complete terminal
   response through the accepted relay-free caller path;
3. the caller releases neither success nor retry;
4. fresh restricted-role authoritative readback observes one exact consistent
   packet, zero duplicates and zero cross-practice visibility; and
5. the ephemeral role, attachments, sidecars, server and network are exactly
   absent at close.

The attempt stops fail-closed on the first mismatch. It may not be rerun under
this plan. Any future occupied execution requires a separately named and
frozen descendant; ordinary continuation authority never converts a failed
attempt into retry authority.

## Immutable predecessor and correction evidence

Attempts 001 and 002 are consumed negative evidence. These exact files may be
read and hash-checked but never edited, replaced or reused as attempt-003
outputs:

| SHA-256 | Exact source |
|---|---|
| `5c38080aa27615ea1efad166d14a61605596130058498ea03c8b631bbeae3be2` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence.json` |
| `a8920b0a294b43c8f67d0348bc6087b84921f8f8788ccd3f969913d95861c06a` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/attempt-001-cleanup-recovery.json` |
| `7efb9853beee9723dbb01fac1f03c4392216bfcc15e9f490f4cb0baae08920ff` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/rehearsal-failure-evidence.json` |
| `6418ecf2e2356b6c875a70106136cdc65d6e545ead5fceeb2c793db45ebe2e40` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/attempt-002-execution-envelope.json` |

The accepted closed transaction contract remains executable input at exact
SHA-256 `bed2a89a3814ba9e9ac006d0fdb0c68d204fec53d8c21b6128190605b6ad9ec2`:
`orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/contract.json`.
The accepted transaction-attestation schema remains exact SHA-256
`d2c186b0d30419e0459d93d92af1f84907125becdeb75c7e1890dce597d3e72c`.

The corrective positive evidence is exact and immutable:

| SHA-256 | Exact source |
|---|---|
| `9f721e0d0e11f5570c2ebe95f8e62d4f1f0e7b2af27f704e4108e2f1792fb98b` | `orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/created-state-representation-evidence.json` |
| `49c5a3673d388fc84b2f046a993a8f4c747f9887252ef4cdd2dfcc59e9a11410` | `orchestration/continuity/raisa-provider-free-docker-created-state-profile-conformance-repair/repair-attestation.json` |

It proves only the Created-state shape and derived containment correction. The
current relay-free harness is accepted at SHA-256
`6965328b6dce6ecf939e86456bfcd99f1bdee7d32202e276f37454796e012b6b`.
Its exact admitted lifecycle is: sole network map key equals the captured
network name, `HostConfig.NetworkMode` equals the captured network ID, and
`EndpointSettings.NetworkID` is empty before attachment or the captured ID
after attachment. Credentials are absent from Docker configuration; the
ownership nonce is mandatory at its exact label and absent elsewhere.

All Git bindings are full 40-character object IDs. Abbreviated Git IDs are
inadmissible.

## Narrow implementation

The accepted corrected harness remains the sole transaction and Docker
authority and must remain byte-for-byte unchanged. The only permitted
implementation delta is a fixed fail-closed attempt adapter:

- add one attempt-003 wrapper with only `--check` and `--execute`; it exposes no
  caller-supplied or arbitrary filesystem output path;
- run the corrected harness's complete static admission before changing any
  process-local binding;
- for the single runner call, bind only its three terminal-path module globals
  to the exact attempt-003 Continuity directory, then restore all three in a
  `finally` block; the accepted file and its historical defaults remain
  unchanged;
- add a closed attempt-003 execution envelope and schema binding the resolved
  full plan commit, Created-state correction source and evidence, exact current
  source, one occupied execution, zero retry, terminal-artifact digest and
  cleanup disposition; and
- add focused tests proving no path argument, collision denial, byte-exact
  corrected-harness preservation, exact attempt-003 routing, unconditional
  binding restoration, consumed predecessor immutability and sanitized
  envelope shape.

The exact owned attempt-003 terminal filenames are:

- `transaction-attestation.json` plus `rehearsal-evidence.json` on pass;
- `rehearsal-failure-evidence.json` on failure; and
- exactly one `attempt-003-execution-envelope.json` for the occupied execution.

All live terminal files are under
`orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-003/`.
The wrapper must refuse any pre-existing terminal file and deny execution. It
may not delete, rotate, rename or overwrite one.

## API Spine and data boundary

This plan changes no REST/OpenAPI, GraphQL, async integration contract, YAML
command manifest, product schema, route, feature flag, allowlist or client.
GraphQL remains read-only. The closed authored-synthetic fixture preserves
explicit practice scope, idempotency identity, exact request digest, audit
atomicity, default denial and authoritative readback.

All three probe relations retain enabled and forced RLS. The runtime role is a
non-owner `NOBYPASSRLS` role with only the exact probe grants. The run releases
no ordinary admission and writes no product record.

There is no ordinary-practice enablement, generic-status `Arrived` change,
action grammar or first-party-client change, waiting-area movement, product,
patient or clinical data, live provider, production runtime, deployment,
release, Pages or protected-ref movement.

## Transport, credential and cleanup boundary

The fixed predecessor containment remains unchanged: exact cached
`postgres:16-bookworm`, pull policy `never`, one internal captured network, no
published port, bind, volume or external network, and captured-ID-only Docker
operations. No host TCP listener, forwarder, Docker-exec byte bridge,
multiprocessing process or queue is permitted.

Credentials exist only in controller memory and are delivered through
post-inspection attached stdin. Attachment output and status are not evidence.
Only exact terminal OCI state plus the prior exact observer predicate may
classify the caller outcome.

The lifecycle has one cleanup owner. Every captured object is reinspected
before removal. Pass or failure requires role absence, attachment absence,
sidecar/server/network absence and zero matching labelled resources. A cleanup
mismatch is terminal failure, never success or permission to rerun.

## Deterministic preexecution admission

Before Docker object creation, all of the following must pass at one committed
candidate:

1. the resolved plan source is a full 40-character ancestor; all immutable
   SHA-256 inputs match; and the corrected harness digest is exact;
2. the existing static gate rejects at least 256 hostile contract mutations,
   96 manifest mutations, 96 OCI-state mutations and 24 classifier packets
   with zero escapes;
3. focused plan, harness, attempt-adapter, API Spine, latch, Baton and
   clockwork tests pass;
4. source inspection finds no forbidden host relay, listener, port
   publication, Docker exec, process or queue path;
5. Ruff, compilation and `git diff --check` pass;
6. exact Docker/image readback and zero pre-existing attempt-003 labelled
   resources pass;
7. a fresh five-source Ariadne receipt records all three parallelism lanes;
8. every exact verifier assertion is executed locally before any provider
   dispatch; and
9. a separate clockwork check, followed only on success by a separate publish,
   advances the latch to the exact one-execution stage.

Then exactly one command may perform the occupied run:

`.venv/Scripts/python.exe -m scripts.raisa_provider_free_check_in_relay_free_recovery_attempt_003 --execute`

No automatic or manual retry is permitted. The command is run once even if
its process return, terminal output or retained evidence is unexpected.

## Acceptance and review

Pass requires the closed attempt-003 envelope, all 12 accepted relay-free
scenarios, explicit rollback zero effect, committed-exactly-once authoritative
readback, no success from the ambiguous response, retry count zero, other
practice visibility zero, ordinary/product effect zero, schema-valid sanitized
evidence and exact cleanup.

Only after deterministic and occupied success may one fresh Gemini 3.7
Flash/high verifier perform an exact-candidate read-only veto in a clean
unchanged worktree. A veto or any execution failure closes the operation
blocked with immutable evidence; it does not authorise a rerun.

## Explicit parallelism assessment

- **DeepSeek:** declined. The native DeepSeek Harness still requires its
  separately frozen provider-free stock-headless-to-custom-runner boot proof,
  Claude Code is no fallback, plan semantics are Sol-owned, and the database
  lifecycle has no separable worker package.
- **Gemini:** reserved for one fresh post-success exact-candidate read-only
  veto; no provider call occurs during planning, implementation or
  preexecution.
- **Native subagents:** declined under current developer policy and the one
  cleanup owner serial constraint.

No worker receives plan, execution, cleanup, acceptance, Git or protected-ref
authority. Reassess all lanes at preexecution, pre-verifier and closeout.

At closeout the clockwork is the sole writer of canonical governance surfaces.
Sol writes the paired lay/technical summary to `orchestration/human_inbox/yuri/`
and sends the usual non-PHI Pushover notification.

All staging uses explicit paths only. `git add .` and `git add -A` are
forbidden. Preserve `docs/branding/` and every unrelated untracked file.

## Fail-closed and continuation rule

Any source, output-topic, collision, identity, image, credential, containment,
OCI-state, observer, transaction, readback, RLS, hostile-mutation, redaction,
envelope or cleanup mismatch stops and preserves one sanitized terminal
result. Ambiguity never becomes success, retry, ordinary admission or wider
authority.

After accepted closeout, proceed under Yuri's standing authority to the
narrowest dependency-satisfied successor. Pause only for a truly
extraordinary, genuinely non-inferable or safety-critical fork.
