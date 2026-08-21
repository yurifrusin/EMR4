# Native Harness attempt 004 — paired summary

Date: 2026-08-21

Timestamp: 2026-08-21T12:45:22.5790561+10:00 (Australia/Brisbane)

## Lay summary

The fourth bounded attempt did not reach DeepSeek, so the Harness is still not
ready for EMR4 development work. The important improvement is that it no longer
failed mysteriously: the new diagnostic gear proved that startup died while
loading the Harness plugin tree, before any provider request or cost. The one
attempt is consumed, nothing was retried, and every temporary process and file
was cleaned up.

The sensible next step is a no-provider source inspection of that exact
plugin-tree failure path. We will not spend another occupied attempt merely to
repeat the same failure.

## Technical summary

- Exact terminal source:
  `26c95db309c2bfb12e640b6fd504b7399f87d73d`.
- One native process exited `1` after 11,150 ms; zero HMR events occurred.
- The v2 terminal records `structured_entrypoint_import_rejected`, top
  coordinate `plugin_tree_failed_to_load`, four sanitized cause nodes and one
  deepest `unrecognized` code coordinate.
- Broker/provider, runner request, model, tool, retry, fallback and candidate
  change counts are all zero.
- Harness, broker and the exact disposable root are absent after cleanup; raw
  messages, stacks, paths, streams, sessions and credentials were not retained.
- Gemini and native-subagent lanes were declined because the machine terminal
  is decisive and there is no surviving code or provider result to review.

No product, patient, clinical, ordinary-practice, deployment, Pages or
protected-ref surface changed. `docs/branding/` remains untouched.
