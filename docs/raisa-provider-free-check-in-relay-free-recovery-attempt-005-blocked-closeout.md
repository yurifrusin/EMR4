# Provider-free check-in relay-free recovery attempt 005 blocked closeout

Date: 2026-08-20

Timestamp: 2026-08-20T14:15:35.7847894+10:00 (Australia/Brisbane)

Status: `blocked`

Operation: `raisa-provider-free-check-in-relay-free-recovery-attempt-005`

Plan source: `d8eec606735ed7d1b5ab089c0c33b8d4469d612f`

Exact occupied execution source: `905184b76f576006232fcfdc78da71d98fcf0ca0`

## Result

Attempt 005 is consumed once and failed closed at
`environment/server_not_running_after_readiness`. Static admission passed, the
captured internal network and server profile passed, the server credential was
delivered through attached stdin and the readiness sidecar returned its exact
success terminal. The immediate post-readiness OCI inspection then found the
captured PostgreSQL server was no longer running.

The intended setup, restricted runtime role, rollback transaction,
unknown-response commit, authoritative readback and transaction attestation did
not run. No retry is permitted. No ambiguous success, ordinary admission or
product record was released. The server attachment, sidecars, server and
network are absent; zero matching owned resources remain.

Immutable terminal bindings:

- failure SHA-256:
  `a9e6331471dadc06ddc1fc7f5f6e9510a231fa7cd3a0fc748495f8c9794bb887`;
- execution-envelope SHA-256:
  `dedfcbf008ea11c9dac9241a59c900582f5ca82a1de003bcd9f740409c0bbb54`;
- occupied execution count: `1`;
- automatic retry count: `0`;
- transaction attestation: absent;
- cleanup: `cleanup_verified`; and
- matching owned residue: `0`.

## DeepSeek native-Harness result

The sole brokered rc.7 worker was also consumed without a retry, but before
DeepSeek was called. It failed at
`EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED` after broker/HMR readiness.
Provider requests, model steps, tool calls, model-executed tests and edits were
all zero; raw prompts, responses and sessions were not retained; cleanup was
exact. Both owned placeholders retained their predispatch hashes.

This is a Harness composition/diagnostic-coordinate failure, not evidence
about DeepSeek reasoning or coding quality. Sol completed the exact frozen
adapter and focused tests directly. The admitted postcommit suite passed 239
provider-free tests and the postexecution suite passed 240. Ruff, compilation,
static admission and the full clockwork regression passed. Gemini was not
dispatched because occupied success is a prerequisite for its veto.

## Honest diagnosis and next boundary

The server-attachment repair did improve the evidence: attempt 004 could not
distinguish stopped state from identity drift, while attempt 005 proves the
stopped-server branch exactly. It did not solve the underlying post-readiness
exit. The retained evidence deliberately excludes raw logs, exit details and
secrets, so it cannot honestly choose among stdin/attachment lifecycle,
entrypoint exit, OOM or another OCI terminal cause.

The narrow successor is
`raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair`.
It must first remain provider-disabled and database-nonexecuting: freeze safe
OCI exit-state coordinates, separate preset/server lifecycle causes, prove the
attached-stdin behavior with deterministic fakes and add the narrowest repair.
Only a separately frozen attempt 006 may later admit another disposable
PostgreSQL execution.

## Workflow efficacy

Clockwork prevented every expensive repetition: the Harness mount failure
spent zero model/provider calls, the database attempt ran once only, protected
refs did not move and canonical checkpoint drift stayed zero. Seven construction
events still consumed human/orchestrator time: one wrong hand-entered full Git
object, one sparse dependency omission, the pre-provider preset-mount failure,
one historical source-pin test selection, one 500-character checkpoint-field
overflow, one postexecution fixture bound to the real consumed namespace and
one noncanonical negative-acceptance filename rejected before publication.

The answer is not six more memory rules. The successor workflow work should
generate full Git bindings, dependency closure, bounded prose and changed-path
classification from schema-backed readings. This efficacy claim is bounded to
observed workflow behavior; it is not a comparative model score.

## Closed surfaces

Dedicated check-in remains default-off. Generic status does not gain
`Arrived`. No route, feature flag, allowlist, action grammar, first-party
client, waiting-area behavior, REST/OpenAPI, GraphQL, product data, patient or
clinical data, live provider, production runtime, deployment, release, Pages
or protected ref changed. Local/origin `master` and `handoff/current` remain
exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`. `docs/branding/` and every
unrelated untracked path remain preserved.
