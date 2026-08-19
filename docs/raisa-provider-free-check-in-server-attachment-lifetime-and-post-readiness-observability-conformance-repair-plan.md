# Provider-free check-in server attachment lifetime and post-readiness observability conformance repair plan

Date: 2026-08-20

Timestamp: 2026-08-20T03:29:08.3073070+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`dccddf16d4c617a34ba006f09e9bda9373a4e731`

Accepted attempt-004 terminal-evidence source:
`4908bf53265e1356a9c5dac84a05b05702ad6d34`

Accepted attempt-004 blocked-transition source:
`a6a292e36978aa95e439fa398242c67816b6d4cc`

Accepted no-database clockwork source:
`958ae762e7c6a065b5926f47eb1a2b63115212c7`

Accepted native-Harness HMR boot-proof clockwork source:
`5ff79d68f6df25d8bebdba78a6d504afb64de2ab`

Accepted relay-free transport source:
`4f0f54c2b0861828f9994444201b8da1bd54be00`

Accepted runtime-role and tenant-isolation source:
`6a2832575e9b4df5c40a13984db7281e79814a94`

Operation:
`raisa-provider-free-check-in-server-attachment-lifetime-and-post-readiness-observability-conformance-repair`

Reasoning level: Extra High freezes the lifecycle ownership, diagnostic,
worker-transport and protected-evidence boundaries. High is sufficient for the
bounded worker patch, deterministic verification, independent veto and
clockwork closeout while this plan remains unchanged.

## Objective and authority

Yuri's standing uninterrupted-development authority admits the narrowest
provider-free source repair implied by attempt 004. The immutable attempt-004
terminal proves that the readiness sidecar completed before the base harness
stopped its own `docker start --attach` client and then combined two distinct
post-readiness observations under
`server_not_ready_or_identity_mismatch`. It does not prove whether the server
was no longer running or which identity predicate failed.

This tranche may only:

1. keep the captured server attachment under the existing controller's single
   cleanup ownership until final teardown;
2. inspect the server after readiness while that attachment remains owned;
3. report a distinct failure when the server is not running;
4. report a distinct identity/profile failure carrying only sorted sanitized
   failed-predicate names; and
5. add provider-free fake-process and fake-inspection tests proving lifecycle,
   branch selection, sanitization and final cleanup.

It performs no Docker object creation, container start or attachment, credential
delivery, PostgreSQL process, SQL, database access or occupied recovery run.
Attempt 004 remains consumed and cannot be retried, resumed, overwritten or
reclassified. Any future attempt 005 requires a separately frozen operation,
namespace, preexecution admission and one-run latch.

## Immutable evidence and exact source boundary

The accepted base harness remains exact SHA-256
`eda68427b87db48064bcfb82762d55c51b600cf2ba5d4724a0faae24d8a3db5b` at
planning:
`scripts/raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py`.
Only this harness and its exact focused test may change:
`tests/test_raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py`.

The attempt-004 failure and execution envelope remain immutable at exact
SHA-256 values:

| SHA-256 | Exact source |
|---|---|
| `1ccc86c76826aa805a48a8823186f5b0eee6e0b571f6deff59ece0474f5df4d3` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-004/rehearsal-failure-evidence.json` |
| `415f054f10639c2dba2466842ad7b957ce9a66f71f48bf07abe5bfdf4e47e7d5` | `orchestration/continuity/raisa-provider-free-check-in-relay-free-recovery-attempt-004/attempt-004-execution-envelope.json` |

Their exact terminal coordinate
`environment/server_not_ready_or_identity_mismatch`, lifecycle prefix and zero
retry count are historical facts. The repair explains why that coordinate was
under-observable; it cannot assert which hidden branch occurred.

Every Git binding must be a machine-resolved full 40-character object and an
ancestor of the candidate. Abbreviations and caller-completed identifiers are
inadmissible.

## Frozen implementation semantics

The accepted `run_rehearsal` ownership structure already retains
`server_attachment` and stops it in `finally`. The repaired success path must
remove the earlier `_stop_attachment(server_attachment)` call and must not set
the handle to `None` after readiness. It must not add another attachment owner,
waiter, thread, process, queue, relay or log reader.

Immediately after readiness:

- inspect the captured server exactly once through the existing inspection
  surface;
- if `State.Running` is not exactly `True`, fail at stage `environment` with
  code `server_not_running_after_readiness` and no failed-predicate detail;
- otherwise obtain the exact map from `_container_profile_predicates` using the
  already captured ID, name, network, nonce, contract, kind and forbidden
  values;
- if any predicate is not exactly `True`, fail at stage `environment` with code
  `server_identity_mismatch_after_readiness` and detail equal to the sorted,
  comma-joined failed predicate names; and
- append `relay_free_server_readiness_verified` only after running state and
  every identity predicate pass.

Failure evidence may retain only predicate names matching the existing closed
`[a-z_,]+` sanitizer. No values, IDs, names, paths, credentials, nonce, raw
inspection payload, environment or Docker output may enter evidence. The
malformed-inspection fallback remains the sanitized predicate
`inspect_shape`.

The final `finally` block remains the sole attachment teardown owner on
success and every failure path. Attachment stop failure remains
`cleanup/server_attachment_absence_unverified`; the existing primary-error
preservation rule remains exact. Container, role and network cleanup semantics
must not change.

## DeepSeek native-Harness worker admission

DeepSeek receives one bounded implementation opportunity because the accepted
rc.7 stock-headless-to-custom-runner HMR proof now closes the earlier startup
gap and this is a small real-EMR4 two-path package. Before any model request,
Sol must commit the plan and create all of the following from that exact source:

- one `ariadne.deepseek_work_order.v2` binding the full source commit, exact
  authority and forbidden-surface digests, branch, sparse worktree, command
  manifest, no-database admission digest and prior broker event;
- one command manifest containing only the provider-free focused tests Sol will
  execute outside the model session;
- one passing static no-database admission artifact for those exact test bytes;
- one fresh non-protected worker branch and sparse worktree containing the full
  root `AGENTS.md`, this plan and threat delta, the accepted profile contract,
  the base harness and its focused test;
- one fresh five-source predispatch receipt and one clockwork one-run latch; and
- one HMR custom-runner binding that exposes exactly `read`, `glob`, `edit` and
  independently matches the broker allowlist.

The occupied worker is pinned to official `@deepseek-ai/dsh@0.1.0-rc.7`,
`deepseek-official/deepseek-v4-flash`, high reasoning, the accepted
`emr4-bounded-worker` profile, zero automatic retries, zero fallback, one
parallel tool call and a 15-minute wall clock. The worker has no shell, test,
Docker, database, Git, network, web, subagent, workflow, skill, telemetry,
title or compaction tool. It may edit only the two owned paths and cannot
commit, push, accept, close, clean up or move any ref.

Sol runs every admitted test and independently reads the complete diff. A
terminal worker failure consumes the one model attempt and receives no retry or
resume. A useful partial patch may be accepted or repaired only by Sol without
changing these frozen semantics; otherwise Sol may implement the same bounded
repair directly. Claude Code is not a fallback.

Retain only sanitized package/profile/session/process/broker/usage/tool-name,
changed-path, test and cleanup metadata. Never retain raw prompts, reasoning,
responses, messages, tool payloads, credentials, environment dumps, package
caches or raw sessions in EMR4.

## Deterministic acceptance

Provider-free tests must prove, without importing shared `conftest.py`, Docker
or a database:

1. the attachment is still live and has not received `terminate`, `kill` or
   `wait` when post-readiness inspection and the next admitted sidecar stage
   begin;
2. the existing final cleanup stops the attachment exactly once on the passing
   path and on each post-readiness failure path;
3. running state `False`, missing or malformed selects only
   `server_not_running_after_readiness` and carries no predicate detail;
4. running state `True` plus failed predicates selects only
   `server_identity_mismatch_after_readiness` and retains exact sorted names;
5. running state `True` plus all exact predicates appends the readiness
   lifecycle event and continues;
6. malformed identity shape retains only `inspect_shape`;
7. cleanup failure never overwrites an earlier primary failure; and
8. no attempt-004 terminal artifact, plan source, transaction, API/product or
   containment contract is rewritten.

The exact plan test, focused harness test and all neighbouring provider-free
relay-free tests must pass through `scripts.ariadne_provider_free_pytest` with
a matching manifest/admission digest. Ruff, Python compilation, JSON/schema
validation and `git diff --check` must pass. Ordinary pytest, Docker,
PostgreSQL, model-executed tests and database execution are forbidden.

Only after a deterministic clean candidate exists may one fresh Gemini 3.7
Flash/high isolated read-only veto inspect that exact candidate. A P0-P2
finding requires bounded correction and one fresh corrected veto; Gemini
receives no write, product, provider, database, execution, cleanup or Git
authority.

## API Spine and product boundary

This repair changes no API contract. GraphQL remains read-only. The accepted
REST command retains explicit actor and practice scope, authorization,
idempotency identity, exact request digest, atomic effect/receipt/audit
membership, default denial and authoritative readback. Events remain
post-commit evidence hints rather than command authority.

No REST/OpenAPI, GraphQL, async contract, route, schema, migration, feature
flag, authored-synthetic allowlist, action grammar, first-party client,
waiting-area behavior or product configuration may change. Dedicated check-in
remains default-off; generic status does not gain `Arrived`; no ordinary
practice is enabled; and no product record is written.

## Explicit parallelism assessment

- **DeepSeek native Harness:** `planned`, positive but bounded leverage. It owns
  one two-path test-first patch after the v2 WorkOrder, exact no-database
  admission, custom-runner binding and one-run latch pass. No retry, resume or
  Claude Code fallback is permitted.
- **Gemini:** `reserved`, material independent leverage. It owns one fresh
  exact-candidate read-only veto only after deterministic acceptance.
- **Native subagents:** `declined`, neutral leverage. Current developer policy
  prohibits proactive delegation, and lifecycle ownership plus final teardown
  form one serial implementation boundary.

Sol alone freezes authority, admits commands, executes tests, accepts or
repairs the candidate, owns cleanup, commits, publishes clockwork and chooses
any successor. Reassess all three lanes at predispatch, candidate, pre-verifier
and closeout.

## Protected and closeout boundaries

No Docker/database execution, live provider other than the single admitted
DeepSeek worker request path, product/patient/appointment/clinical/historical
or protected data, ordinary-practice enablement, product runtime, deployment,
release, Pages, protected evidence access or protected-ref movement is
authorised. Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

At closeout the clockwork is the sole writer of canonical governance surfaces
and must run `--check` before a separate `--publish`. Sol writes the paired
lay/technical Yuri summary, sends the usual non-PHI Pushover notification,
stages only explicit paths and preserves `docs/branding/` plus every unrelated
untracked file. `git add .` and `git add -A` are forbidden.

After accepted closeout, freeze the narrowest attempt-005 operation only if the
repair evidence supports another occupied rehearsal. Otherwise continue to the
narrowest dependency-satisfied product tranche. Pause only for a genuine,
safety-critical user-attention fork.
