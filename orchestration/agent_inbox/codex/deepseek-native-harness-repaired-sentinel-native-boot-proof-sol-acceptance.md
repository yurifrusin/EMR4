# Sol acceptance — repaired-sentinel native boot terminal

Date: 2026-08-21
Timestamp: 2026-08-21T14:22:57.0516264+10:00 (Australia/Brisbane)
Reviewed candidate: `b99d961e225f355a17e74ec15d6e82fb61d83532`

## Decision

Accept the terminal and cleanup; reject the boot proof.

The one authorised process started and the no-retry latch was consumed. It
exited 1 after 7,310 ms without emitting `sentinel_activated` or
`stock_headless_hmr_ready`. The result is therefore `failed_closed`, not a
partial pass and not evidence that the relative-specifier repair solved the
profile startup failure.

All provider boundaries held: no changed runner, broker, worker, prompt, tool,
model, provider or network activity occurred. The exact process and disposable
root are absent and raw streams were destroyed after retaining only counts and
digests.

The immutable terminal's generic claim sentence is over-affirmative for a
failure; the structured failure fields control, and AER-0782 preserves the
correction without rewriting execution evidence.

The first clockwork publication was also rolled back byte-exactly after one of
98 extended checks found the canonical closed-surface boundary token missing
from the successor latch. AER-0787 and the corrected typed intent preserve the
failure and repair; no Harness or provider retry occurred.

Proceed only to a separately frozen provider-free static preactivation source-
coordinate diagnosis. No second native process is authorised.
