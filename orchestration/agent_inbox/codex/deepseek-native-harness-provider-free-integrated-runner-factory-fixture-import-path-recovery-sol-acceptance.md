# Sol acceptance: integrated-runner factory fixture import-path recovery

Date: 2026-08-22

Timestamp: 2026-08-22T19:27:57.8855998+10:00 (Australia/Brisbane)

Decision: `accepted_pass`

Reasoning level: high

I accept the one-process provider-free result as exact dynamic evidence of the
occupied integrated-runner factory mismatch.

Accepted facts are:

- the successor fixture differs from the consumed fixture only in the exact
  `parents[1]` to `parent` package-scope projection;
- both scoped imports existed and were bound before the process;
- installed `AgentRegistry.create` and the runner setup callback were each
  entered exactly once;
- the old occupied guard released exactly
  `EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID` before preset mounting;
- the runner reproduced `failed` at `factory` with zero request, tool-result or
  turn activity;
- retry, resume, fallback, Harness, broker, worker, model and provider counts
  are zero; and
- raw streams were not retained and cleanup is complete.

The evidence selects only the already accepted four-argument guard, bridge and
sanitizer graph beside the unchanged runner. It does not prove native Harness
boot, a DeepSeek turn, provider reachability, useful worker output or general
Harness reliability.

Product, data, ordinary-practice, runtime, deployment, release, Pages and
protected-ref boundaries remain closed.
