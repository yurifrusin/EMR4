# Provider-free check-in relay-free recovery attempt 002 plan

Date: 2026-08-19

Timestamp: 2026-08-19T21:47:53+10:00 (Australia/Brisbane)

Status: `frozen`

Clockwork transition source:
`4012ce578b0409c72215a624b1c4f115e45a7d60`

Lifecycle-admission repair source:
`fc772085a02d7db790b938fb845ef4546156d31e`

Accepted relay-free transport source:
`4f0f54c2b0861828f9994444201b8da1bd54be00`

Accepted runtime-role and tenant-isolation source:
`6a2832575e9b4df5c40a13984db7281e79814a94`

Target result:
`raisa_provider_free_check_in_relay_free_recovery_attempt_002_pass`

Reasoning level: Extra High freezes the one-run authority, immutable evidence
namespace, transaction identity, forced-RLS, OCI outcome and cleanup
boundaries. High is sufficient for the fixed adapter, deterministic admission,
one occupied execution, independent veto and clockwork closeout.

## Authority and objective

Yuri explicitly confirmed one new attempt after attempt 001 closed blocked.
This plan does not reopen, erase or rerun attempt 001. It creates the distinct
operation `raisa-provider-free-check-in-relay-free-recovery-attempt-002` and
authorises exactly one attempt-002 occupied execution after all preexecution
gates pass.

The one execution must prove, in one uniquely named provider-free disposable
local PostgreSQL 16 environment, that:

1. an authored-synthetic effect/receipt/audit transaction is explicitly rolled
   back and fresh restricted-role readback observes zero members;
2. a disjoint transaction commits once and loses its complete terminal
   response through the accepted relay-free caller path;
3. the caller releases neither success nor retry;
4. fresh restricted-role authoritative readback observes one exact consistent
   packet, zero duplicates and zero cross-practice visibility; and
5. the ephemeral role, attachments, sidecars, server and network are exactly
   absent at close.

The attempt stops fail-closed on the first mismatch. It may not be rerun under this plan.
Any further occupied execution would require another explicit user
decision and separately frozen descendant.

## Immutable predecessor evidence

Attempt 001 is consumed negative evidence. These exact files may be read and
hash-checked but never edited, replaced or reused as attempt-002 outputs:

| SHA-256 | Exact source |
|---|---|
| `5c38080aa27615ea1efad166d14a61605596130058498ea03c8b631bbeae3be2` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/rehearsal-failure-evidence.json` |
| `a8920b0a294b43c8f67d0348bc6087b84921f8f8788ccd3f969913d95861c06a` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/attempt-001-cleanup-recovery.json` |

The accepted closed contract remains an executable input at exact SHA-256
`bed2a89a3814ba9e9ac006d0fdb0c68d204fec53d8c21b6128190605b6ad9ec2`:
`orchestration/continuity/raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal/contract.json`.
The accepted transaction-attestation schema remains exact SHA-256
`d2c186b0d30419e0459d93d92af1f84907125becdeb75c7e1890dce597d3e72c`.

The clockwork user-decision transition is exact SHA-256
`a7cbc9e7ce683f0cbd53e95d40e54f01a4bce43a688c7a0a93ff0794f90c3cae`:
`orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/clockwork-tick-evidence.json`.

All Git bindings are full 40-character object IDs. Abbreviated Git IDs are
inadmissible.

## Narrow implementation

The accepted harness remains the transaction and Docker authority. The only
permitted implementation delta is a fixed fail-closed attempt adapter:

- add the exact attempt-002 Continuity directory to a closed output-topic
  allowlist; no caller-supplied or arbitrary filesystem output path is allowed;
- make the existing rehearsal runner select terminal paths from that admitted
  topic while retaining the historical topic as its unchanged default;
- add one attempt-002 wrapper with only `--check` and `--execute`; its execute
  mode always selects the fixed attempt-002 topic;
- add a closed attempt-002 execution envelope and schema binding the resolved
  full plan commit, lifecycle repair source, exact current source, one occupied
  execution, zero retry, terminal-artifact digest and cleanup disposition; and
- add focused tests proving topic rejection, collision denial, historical
  default preservation, exact attempt-002 routing and sanitized envelope shape.

The exact owned attempt-002 terminal filenames are:

- `transaction-attestation.json` plus `rehearsal-evidence.json` on pass;
- `rehearsal-failure-evidence.json` on failure; and
- exactly one `attempt-002-execution-envelope.json` for the occupied execution.

All live terminal files are under
`orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-002/`.
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

The lifecycle has one cleanup owner. Every captured object is reinspected before removal.
Pass or failure requires role absence, attachment absence, sidecar/server/network
absence and zero matching labelled resources. A cleanup mismatch is terminal
failure, never success or permission to rerun.

## Deterministic preexecution admission

Before Docker object creation, all of the following must pass at one committed
candidate:

1. the resolved plan source is a full 40-character ancestor and all immutable
   SHA-256 inputs match;
2. the existing static gate rejects at least 256 hostile contract mutations,
   96 manifest mutations, 96 OCI-state mutations and 24 classifier packets
   with zero escapes;
3. focused plan, harness, attempt-adapter, API Spine, latch, Baton and
   clockwork tests pass;
4. source inspection finds no forbidden host relay, listener, port publication,
   Docker exec, process or queue path;
5. Ruff, compilation and `git diff --check` pass;
6. a fresh five-source Ariadne receipt records all three parallelism lanes; and
7. the clockwork advances the latch to the exact one-execution stage.

Then exactly one command may perform the occupied run:

`.venv/Scripts/python.exe -m scripts.raisa_provider_free_check_in_relay_free_recovery_attempt_002 --execute`

No automatic or manual retry is permitted. The command is run once even if its
process return, terminal output or retained evidence is unexpected.

## Acceptance and review

Pass requires the closed attempt-002 envelope, all 12 accepted relay-free
scenarios, explicit rollback zero effect, committed-exactly-once authoritative
readback, no success from the ambiguous response, retry count zero, other
practice visibility zero, ordinary/product effect zero, schema-valid sanitized
evidence and exact cleanup.

Only after a deterministic pass may one fresh Gemini 3.7 Flash/high verifier
perform an exact-candidate read-only veto in a clean unchanged worktree. A veto
or any execution failure closes the operation blocked with immutable evidence;
it does not authorise a rerun.

## Explicit parallelism assessment

- **DeepSeek:** declined. The native DeepSeek Harness still requires its
  separate stock-headless-to-custom-runner boot proof, Claude Code is no
  fallback, and the database lifecycle has no separable worker package.
- **Gemini:** reserved for one fresh post-success exact-candidate read-only
  veto; no provider call occurs before deterministic and occupied success.
- **Native subagents:** declined under current developer policy and the one
  cleanup owner serial constraint.

At closeout the clockwork is the sole writer of canonical governance surfaces.
Sol writes the paired lay/technical summary to `orchestration/human_inbox/yuri/`
and sends the usual non-PHI Pushover notification.

All staging uses explicit paths only. `git add .` and `git add -A` are
forbidden. Preserve `docs/branding/` and every unrelated untracked file.

## Fail-closed rule

Any source, output-topic, collision, identity, image, credential, containment,
OCI-state, observer, transaction, readback, RLS, hostile-mutation, redaction,
envelope or cleanup mismatch stops and preserves one sanitized terminal result.
Ambiguity never becomes success, retry, ordinary admission or wider authority.
