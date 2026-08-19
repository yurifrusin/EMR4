# Yuri summary — check-in server-attachment observability repair

Date: 2026-08-20

## Lay summary

The repair is accepted. The rehearsal now keeps its connection to the test
server alive until the whole operation is finished, and if the server is not
usable after readiness it tells us whether it stopped or whether its identity
and containment checks failed. It still reveals no sensitive values.

The DeepSeek Harness did not reach DeepSeek. It failed safely while assembling
the three allowed tools, before any provider request, token use, tool use or
file change. That makes this a Harness-control defect rather than another
untraceable DeepSeek failure. We know the specific missing control and will add
it before another occupied worker is attempted.

## Technical summary

- Implementation source:
  `cfc7eb472aaaa4fdf7ffef35b07a65a2729073c5`.
- Independently reviewed candidate:
  `9f9984e0575beb7b300035fdb74433f5bef32028`.
- Repaired harness SHA-256:
  `62a18d9ce2a29eb417f491c8ce341416f03183375f042f8c41bcb1f4674df77c`.
- Provider-free deterministic tests: 72/72 passed locally; Gemini repeated
  72/72 and eleven commands, returned `pass`, and found zero P0-P2 issues.
- DeepSeek native-Harness: one consumed launch, broker ready, zero provider
  calls, requests, model steps, tool calls, file changes and retries; cleanup
  complete.
- Cause: rc.7 `tools.restrict()` was given scope-local preset tool names even
  though it filters inherited global tools; the terminal sanitizer then reduced
  the exception to `CUSTOM_RUNNER_FAILURE`.
- Ten workflow repair events are retained in the efficacy reading. They show
  remaining automation work around exact filenames, sparse dependency closure,
  terminal capture, source-specific test classification and exact clockwork
  predecessor derivation. The predecessor mismatch was rejected before write;
  a later local commit-chain continuation was corrected and amended before push.
- Docker/database invocations: zero. Product/API/ordinary-practice changes:
  zero. Protected refs remain exact
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The next operation is a provider-free effective-tool composition and stable
terminal-coordinate guard. It will make zero provider calls. Attempt 005 is not
yet admitted.

The usual non-PHI Pushover closeout notification succeeded with request
`05131aab-9513-46b0-9a49-ceaeb7ee3335`.
