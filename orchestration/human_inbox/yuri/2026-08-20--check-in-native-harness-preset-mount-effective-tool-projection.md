# EMR4 update — native Harness preset and tool projection

## Lay summary

The native DeepSeek Harness can now see our exact EMR4 worker preset, mount it,
and reduce the worker's effective tools to precisely edit, glob and read before
any AI request is made. The final provider-disabled rehearsal passed cleanly in
one native process and left nothing running or behind.

Two earlier launches stopped before the Harness itself started. The first found
an installation-directory ordering bug; the second found an npm timeout and
Windows cleanup weakness. Both were contained, preserved as evidence and never
retried. The final version removed npm from this proof and reused a cryptographically
bound package tree that had already passed the accepted Harness rehearsal.

This is a meaningful reliability step: the worker's preset and least-authority
tool view are now observable in the real native lifecycle, rather than inferred
from disconnected configuration.

## Technical summary

- Final candidate: `c8b0e3a587191b65da212edda36b8b833a2ecc2c`.
- Native terminal: `EFFECTIVE_TOOL_COMPOSITION_PASSED`.
- Events: 9/9 in exact order.
- Effective tools: `edit`, `glob`, `read` only.
- Native processes / retries: 1 / 0.
- Agent sessions, turns, broker/model/provider/network calls, occupied workers,
  Docker and database invocations: all 0.
- Credential environment names removed: 3.
- Stdout/stderr: 0 bytes / 0 bytes.
- Process and disposable-root cleanup: both exact.
- Final shell-free ledger: 12/12 commands passed.
- Independent review: Gemini 3.7 Flash/high passed at the exact clean candidate.
- Attempts 001 and 002: immutable zero-native-process prelaunch failures.
- Protected refs remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Next, the accepted native preset/tool path can be used for one separately
bounded authored-synthetic monitored DeepSeek worker rehearsal. It still does
not authorise product data, ordinary-practice check-in, production or release.
