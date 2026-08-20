# Threat-model delta — DeepSeek native Harness provider-free pre-HMR startup classification and terminalization

Date: 2026-08-20

Timestamp: 2026-08-20T23:23:58.3235077+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`deepseek-native-harness-provider-free-pre-hmr-startup-failure-classification-and-terminalization-recovery`

## Changed surface

The outer development controller gains bounded in-memory inspection of local
native-Harness startup stdout/stderr and one exclusive sanitized terminal
outside the disposable root. It adds no worker, provider, product, database,
network, credential or production authority.

| Risk | Fail-closed control |
|---|---|
| Raw startup text leaks into durable evidence | The terminal schema admits only fixed enums, integers, counts, SHA-256 digests and identifiers already bound by the checkpoint. Tests search outputs for raw fixture fragments and secret-shaped tokens. |
| A broad text match falsely asserts root cause | Use exact fixed byte signatures grouped by cause; zero groups is unclassified and multiple groups is ambiguous. No priority rule upgrades ambiguity. |
| Truncated large output is misclassified | Hash/count incrementally, cap classification bytes at 64 KiB per stream and use `startup_stream_limit_exceeded` above the cap. |
| Post-HMR failures are mislabelled pre-HMR | Require exactly zero HMR events. Any event rejects the component and leaves the later lifecycle layer authoritative. |
| Successful or live work is classified as failure | Require a failed process-creation coordinate, a closed controller exception, or a nonzero exit; exit zero and missing/invalid exit data reject. |
| Terminal is written inside the disposable root and deleted | Resolve the output as an exact repository evidence descendant outside the exact attempt root; reject symlinks, escapes and root overlap. |
| Cleanup deletes raw streams before evidence exists | Exclusive write, schema validation and canonical readback digest must complete before exact-root removal is called. Deterministic ordering fixtures make deletion-first impossible. |
| Stale or duplicate terminal is overwritten | Prelaunch requires output absence and terminal write uses exclusive-create semantics. A second writer fails closed. |
| Terminal failure causes raw secret retention | Cleanup remains mandatory even when terminalization fails; such an attempt is non-acceptable and cannot retry. No raw stream becomes a durable evidence substitute. |
| Existing negative evidence is rewritten | Hash-bind and assert byte equality for attempt-001 and attempt-002 consumed, terminal, report, diagnosis and efficacy artifacts. |
| Provider-disabled tests accidentally start Harness or a provider | Source and monkeypatched hostile tests reject subprocess creation; external I/O and provider credentials are unnecessary and unused. |
| A diagnostic pass is overstated as worker readiness | Claim only future sanitized pre-first-HMR terminalization. Attempt-002 cause, Harness reliability, DeepSeek quality, occupied execution and product readiness remain unproved. |

## Protected boundaries

No native process, worker, broker or provider request; no retry, resume,
fallback or new attempt; no product/database/data access or change; no raw
startup-stream retention; no production, deployment, release, Pages, protected
evidence or protected-ref action.

Passing evidence can prove only a provider-free deterministic controller
mechanism for future sanitized pre-first-HMR failure terminalization.
