# Provider-free check-in server post-readiness exit-state and stdin-lifecycle conformance repair closeout

Date: 2026-08-20

Timestamp: 2026-08-20T16:04:16.4951745+10:00 (Australia/Brisbane)

Status: `accepted_repair_with_failed_closed_native_probe`

Operation:
`raisa-provider-free-check-in-server-post-readiness-exit-state-and-stdin-lifecycle-conformance-repair`

Exact corrected reviewed candidate:
`7d39641c3170fc0fec76fadce5cd45309bdffdb2`

Corrected verifier evidence source:
`3ee2b9c074864b12225338d8559fd4226bac2a7a`

## Result

The server lifecycle repair passes. Credential delivery writes and flushes the
exact line while leaving attached stdin open. The final attachment cleanup is
the sole owner that closes it, closes it at most once, and retains bounded
terminate/kill fallback behavior. A stopped post-readiness server now projects
only the accepted nine-key sanitized OCI/host vocabulary, with malformed or
unknown values collapsing to closed null, `unknown` or `unreadable` forms.

The sole provider-disabled native Harness process did not pass. It reached
`PRESET_DISCOVERY_ENTERED` and `PRESET_DISCOVERY_PASSED`, then failed closed at
the first missing `PRESET_VALIDATION_PASSED` marker. It created zero agents and
turns, made zero broker, model, provider, network, Docker or database requests,
retained no raw logs, retried zero times and left both the process and
disposable root absent. This terminal is immutable and is not a DeepSeek model
or coding-quality result.

## Verification and correction

The implementation and evidence passed 52 provider-free tests, Ruff, Python
compilation, JSON/schema validation, closed-boundary checks and clean-diff
checks. The initial isolated Gemini 3.7 Flash/high veto accurately found one P1:
the worker-root constructor doubled `EMR4-worktrees` inside a review worktree.
Sol made the plan's one permitted bounded correction and added a two-shape
regression. The fresh corrected veto then passed all nine bound commands with
the same exact clean pre/post HEAD.

The accepted evidence therefore proves the server stdin/cleanup semantics,
the closed post-readiness projection, the separation of server and native
preset families, and a narrower native failing coordinate. It does not prove
native preset validation, agent creation, effective tools, an occupied
DeepSeek worker, attempt 006, PostgreSQL behavior or product readiness.

## Workflow efficacy

Clockwork kept the single native process to one and provider cost to zero. It
also detected a direct-latch ownership breach and a hand-completed Git object
before acceptance. Eight qualifying incidents are closed in register revision
572. The controls are readings rather than new operator memory rules: exact
Git objects, dependency closure, bounded checkpoint text, artifact roles,
changed paths and canonical ownership are mechanically derived or validated.

Two npm-cache exploration dead ends were discarded before admission and had no
candidate, provider or canonical effect; they are build exploration, not
additional accepted Harness evidence.

## Next boundary

The narrow successor is
`raisa-provider-free-check-in-native-harness-preset-validation-subcoordinate-recovery`.
It first freezes deterministic/package-source readings for exact preset-row
discovery, exact byte read/parse, and digest/length binding. No native process
is admitted until a separate checkpoint; any later process is provider-disabled
and one-shot. The consumed process is not retried, and attempt 006 remains
closed.

## Closed surfaces

Dedicated check-in remains default-off. Generic status does not gain
`Arrived`. No route, feature flag, allowlist, action grammar, first-party
client, waiting-area behavior, REST/OpenAPI, GraphQL, product configuration,
product/patient/appointment/clinical/historical/protected data, live DeepSeek,
Docker/database execution, production runtime, deployment, release, Pages or
protected ref changed. Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. `docs/branding/` and every
unrelated untracked path remain preserved.

