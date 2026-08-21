# DeepSeek native Harness provider-free repaired-sentinel native boot proof closeout

Date: 2026-08-21
Timestamp: 2026-08-21T14:22:57.0516264+10:00 (Australia/Brisbane)
Reviewed candidate: `b99d961e225f355a17e74ec15d6e82fb61d83532`
Execution checkpoint HEAD: `976dd4dd2c67bc337e2f0ca54a315bcb8ebeab7b`

## Outcome

The sole authorised attempt is complete and **failed closed**.

Exactly one pinned rc.7 Node/Harness process started with the repaired initial
profile, no task argument, no changed runner and no retry. It ran for 7,310 ms,
exited 1 and emitted zero HMR events. Therefore neither sentinel activation nor
stock-headless HMR readiness was proved. The accepted two-row static repair is
preserved, but it is insufficient to clear the initial-profile startup path.

The result is not reclassified as partial success. Attempt
`repaired-sentinel-native-boot-attempt-001` is consumed and no second process,
same-attempt retry, resume or fallback is authorised.

## Boundary and cleanup reading

- native processes: 1;
- retries: 0;
- changed runner, broker and worker processes/sessions: 0;
- prompts and tool executions: 0;
- model, provider and network requests/attempts: 0;
- HMR events: 0;
- raw stdout/stderr retained: false;
- process absent: true; and
- disposable root absent: true.

The terminal retains only stream byte counts and SHA-256 digests. No raw error,
message, stack, path, environment, session or credential was retained or
reconstructed.

## Evidence interpretation correction

The immutable terminal's generic `claim_boundary` and generated report say
that the artifact “proves only” sentinel loading and HMR readiness. In a failed
terminal that wording is too affirmative. The authoritative interpretation is
the structured fields: `result: failed_closed`, zero `hmr_events`,
`readiness_observed: false` and
`failure_coordinate: native_process_exited_before_readiness`. The artifact
proves the bounded attempt and cleanup, not sentinel loading or readiness.
AER-0782 records this output-contract defect; the immutable terminal is not
rewritten.

## Clockwork publication correction

The first lease-109 publication passed the transactional writer but its wider
post-publication suite passed 97 of 98 checks: the successor latch expressed
the substantive ordinary-practice denial without also retaining the canonical
flag/allowlist/mounting token. The clockwork rolled the generation back at
lease 110 byte-exactly. AER-0787 records the omission; the corrected typed
intent now carries both the canonical token and the narrower tranche denial.
This correction launched no Node, Harness, worker, model or provider activity
and does not alter the consumed native terminal.

## Parallelism efficacy

DeepSeek and Gemini were correctly declined because worker/model/provider
activity would have invalidated the pre-provider result. Native subagents were
correctly declined under the serial one-process owner constraint and current
developer policy. GPT Sol owned the launch, terminal and cleanup. No lane
change could have improved the runtime reading without breaking its claim.

## Decision and next operation

Accept the terminal integrity, no-retry latch and cleanup. Reject the native
boot proof and any worker-readiness claim.

The next dependency-satisfied operation is
`deepseek-native-harness-provider-free-repaired-sentinel-preactivation-source-coordinate-diagnosis`.
It may inspect the pinned rc.7 source, unchanged initial profile, accepted
predecessor evidence and sanitized terminal to identify the narrowest unique
pre-sentinel exit coordinate. It must remain provider-free and static: no Node,
Harness, broker, worker, model, provider, network or attempt retry.

Product source, data, route, feature flag, client, waiting-area, production,
deployment, release, Pages and protected refs remain unchanged and closed.
