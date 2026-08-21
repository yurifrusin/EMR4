# Native Harness attempt 005 — paired summary

Date: 2026-08-21

Timestamp: 2026-08-21T19:35:59.5541506+10:00 (Australia/Brisbane)

## Lay summary

The fifth bounded attempt got substantially farther: it fully started the
Harness, reached its live-reload readiness point and entered our custom worker
runner. It then failed before contacting DeepSeek. So there was no provider
cost, no edit and no retry, and all temporary processes and files were cleaned
up.

This means the previous startup repairs worked, but the Harness is still not
ready for EMR4 development. The remaining weakness is now narrower: our runner
recorded only a generic failure code instead of telling us which pre-request
step failed. The next work will improve that diagnostic mechanism without
spending another occupied attempt.

## Technical summary

- Exact terminal source:
  `0b2aebd104f4c9dcfd4603af5dd51a687bace555`.
- One native process exited `1` after 10,929 ms.
- Both `sentinel_activated` and `stock_headless_hmr_ready` occurred.
- The runner terminal records `CUSTOM_RUNNER_FAILURE` before request zero could
  become request one.
- Provider, tool, retry, fallback, auxiliary-model and candidate-change counts
  are all zero.
- Harness, broker and the exact disposable root are absent; no raw streams,
  sessions, prompts, reasoning or credentials were retained.
- Gemini and native-subagent lanes were declined because the machine terminal
  is decisive and there is no surviving candidate or provider result to review.

No product, patient, clinical, ordinary-practice, deployment, Pages or
protected-ref surface changed. `docs/branding/` remains untouched.
