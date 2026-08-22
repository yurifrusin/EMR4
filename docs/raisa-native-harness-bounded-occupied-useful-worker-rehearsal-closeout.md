# Raisa native Harness bounded occupied useful-worker rehearsal closeout

Date: 2026-08-22

Timestamp: 2026-08-22T13:30:09.9126535+10:00 (Australia/Brisbane)

Status: accepted failed-closed terminal; useful candidate rejected

Result: `native_harness_useful_worker_failed_closed_no_candidate`

## Outcome

The sole authorised native-Harness DeepSeek V4 Flash/high turn was consumed
once. Native boot and both expected HMR coordinates passed. The loopback broker
started and completed one DeepSeek request. The runner observed one `edit` tool
call and one tool result, but no target path changed, the post-execute hook did
not mark the turn concluded, and the turn ended with `turn_kind: error`. The
broker correctly rejected any later request after the one-request ceiling.

No candidate was admitted, retained or adopted. No retry, resume, fallback,
auxiliary model or Claude Code fallback occurred. Harness and broker processes
are absent, the exact disposable root is absent, and raw prompt, response,
reasoning, stream, session, environment and credential material was not
retained.

## What this establishes

- The installed rc.7 package, stock-headless boot, custom HMR runner,
  operation-specific loopback broker and first provider exchange were
  reachable in one bounded EMR4 attempt.
- DeepSeek selected the admitted `edit` tool and the Harness returned one tool
  result.
- The request ceiling, no-retry rule, typed terminal, candidate rejection and
  cleanup controls worked.
- The path is not yet effective as a useful development worker: it produced
  zero changed paths and zero adoptable artifacts.

The evidence does not distinguish an invalid edit result, a rejected
post-execute decision or another tool-result/conclusion mismatch. It therefore
does not support a broad DeepSeek-quality or native-Harness-reliability claim.

## Verification and workflow reading

- 189 combined useful-worker, accepted runner/guard, broker, latch, Baton and
  API Spine checks passed before terminal preservation;
- the exact occupied terminal validates against its closed JSON Schema;
- the post-terminal ten-command deterministic validation passes;
- protected refs remained unchanged and `docs/branding/` remained present;
- preexecution corrections moved validation-runner Git evidence, checkpoint
  ancestry and exact attempt cleanup into machine controls; and
- the occupied attempt itself used one process, one completed provider request,
  zero retries and complete cleanup.

The clockwork materially improved containment and traceability, but did not
make this attempt useful. That distinction is the efficacy conclusion.

## Parallelism outcome

- DeepSeek V4 Flash/high: used exactly once for the frozen closed-form edit;
  result failed closed with no candidate.
- Gemini: correctly declined; the envelope permitted no auxiliary model and no
  semantic candidate existed to review.
- Native subagents: correctly declined under developer policy and the serial
  one-turn lifecycle.
- GPT Sol: froze controls, monitored the attempt, rejected the absent
  candidate, validated cleanup and owns recovery planning.

## Closed boundaries and successor

No ordinary practice, feature flag, allowlist, route, generic-status
`Arrived`, action grammar, first-party client, waiting-area movement,
product/patient/appointment/clinical/historical/protected data, live product
runtime, production, deployment, release, Pages or protected ref changed.

The dependency-satisfied successor is
`deepseek-native-harness-provider-free-tool-result-conclusion-coordinate-diagnostic-recovery`.
It may use only provider-free authored-synthetic fixtures to distinguish the
edit-result and post-execute conclusion states and extend the typed terminal
before any separately frozen occupied successor. This attempt remains
immutable and cannot be retried or resumed.
