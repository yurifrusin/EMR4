# Authored-synthetic native Harness worker attempt 003 diagnosis

Date: 2026-08-21

Timestamp: 2026-08-21T07:35:11.0925861+10:00 (Australia/Brisbane)

## Exact terminal

Attempt `deepseek-native-synthetic-window-worker-003` is consumed and cannot be
retried, resumed or reclassified. Exactly one native Harness process started
and exited `1` after 11,241 ms. The outer coordinate is
`native_harness_terminal_failure`.

The recovered pre-HMR gear additionally proves stage
`native_process_started_before_first_hmr_event`, controller coordinate
`native_process_exited_nonzero`, exit code `1`, zero HMR events and cause
`unclassified_nonzero_exit`. The 7,314 stderr bytes matched none of the six
fixed semantic signature groups. Their SHA-256 is
`803374be8cc52569aadbd787500d6044d84ef1ed80d4e14828d2ae974dd57d67`;
raw content is not retained.

The broker recorded zero started, completed, failed or rejected provider
requests. The runner produced no terminal, request, model step, tool call or
tool result. The synthetic source remained at its exact baseline with no
changed path, and no public or holdback case ran. Retry, fallback and auxiliary
model-call counts are zero. Harness, broker and the literal disposable root are
absent after cleanup.

## What became more traceable

Attempt 002 could only be placed between process creation and the first HMR
event. Attempt 003 preserves that same bounded stage as a schema-validated safe
sidecar, proves that no admitted signature group was present, binds its digest
into the outer terminal and writes it before raw-root removal. The classifier
did not invent a cause: zero matches correctly remained unclassified.

This is a genuine traceability improvement, but not yet enough diagnosis to
repair the startup. The result cannot distinguish an unlisted profile,
dependency-injection, service-construction, HMR bootstrap or other startup
exception. The equal stderr byte count across attempts 002 and 003 does not
prove equal content or cause; their digests differ.

## Honest conclusion

The Ariadne clockwork and broker reliably bounded the attempt: one consumed
launch, zero provider spend, zero retry, exact candidate accounting, a safer
pre-HMR terminal and complete cleanup. The native Harness still did not reach
DeepSeek under this profile, so attempt 003 supplies no evidence about
DeepSeek reasoning, coding quality or worker usefulness.

The next architecture-strengthening tranche should be provider-disabled and
source-static: derive the narrowest non-secret structured diagnostic seam for
currently unclassified pre-HMR exceptions without launching another Harness,
worker, broker or provider request. No further occupied attempt is authorised.
