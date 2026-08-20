# Authored-synthetic native Harness worker attempt 002 diagnosis

Date: 2026-08-20

Timestamp: 2026-08-20T22:49:53.3849430+10:00 (Australia/Brisbane)

## Exact terminal

Attempt `deepseek-native-synthetic-window-worker-002` is consumed and cannot be
resumed. Exactly one native Harness process started and exited `1` after
11,214 ms. The immutable terminal coordinate is
`native_harness_terminal_failure`.

The broker admitted zero provider requests: started `0`, completed `0`, failed
`0`, rejected `0`. The runner recorded no terminal, no request, no model step,
no tool call and no tool result. The synthetic file remained at its exact
baseline digest, no path changed, and neither public nor holdback cases ran.
Automatic retries, fallbacks and auxiliary model calls are all zero. Harness,
broker and the exact disposable root are absent after cleanup. Attempt 001's
retained lifecycle artifacts remain byte-identical to their pre-attempt-002
baseline.

## Narrow factual location

The broker reached its exact ready contract before native process creation;
otherwise the controller would not have written both runtime-profile digests or
started Harness. Harness then exited before either `sentinel_activated` or
`stock_headless_hmr_ready`, and before a runner terminal existed. The observed
failure therefore lies after native process creation but before the first HMR
activation coordinate and before any DeepSeek/provider boundary.

The Harness wrote 7,314 stderr bytes with SHA-256
`5ea9223c665329dc184b798abdf651ec615d90b223d586dde21414b2216687ab`.
The frozen safety contract retained only that byte count and digest, then
removed the raw startup stream with the disposable root. The terminal collapses
every nonzero pre-HMR exit to `native_harness_terminal_failure`. Existing
evidence consequently cannot select profile parsing, dependency injection,
plugin/service construction, HMR bootstrap, runner loading or another startup
exception as the cause. It would be unsound to infer one.

## Conclusion

The broker/clockwork gear did its accounting job: one launch was consumed,
provider I/O remained zero, there was no retry or fallback, the candidate was
unchanged, the failure was terminal and cleanup was exact. This is materially
more traceable than an unattributed worker disappearance.

It is not yet sufficiently diagnosable for productive EMR4 worker use. The
startup failure is localized to a bounded pre-HMR interval, but its semantic
cause was deleted before a safe closed classification was produced. This
attempt supplies no evidence about DeepSeek reasoning, coding quality or model
reliability because DeepSeek was never called.

No repeat is authorised. The narrow recovery is provider-disabled: introduce a
closed sanitized pre-HMR startup-failure vocabulary and terminalize the exact
stage/cause before raw startup material is deleted, with deterministic hostile
fixtures and no occupied provider call. Only a later distinct Yuri decision may
open another DeepSeek worker attempt.
