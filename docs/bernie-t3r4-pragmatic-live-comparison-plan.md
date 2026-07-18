# Bernie T3R4 Pragmatic Live Comparison Plan

Date: 2026-07-18

Decision: `approved_for_bounded_synthetic_only_execution`

## Experiment

GPT/Codex and Gemini/Antigravity are the production-relevant comparison. Each
receives the frozen 24-case T3R2 selection twice, for 48 observations per lane
and 96 primary observations in total.

DeepSeek is not a deployment candidate and is excluded from the primary
ranking. It receives a reduced 12-case subset twice, for 24 auxiliary
observations. The subset preserves two cases per action, six medium and six
high-noise cases, and covers all eight dialogue forms. Its only purpose is to
look for useful diversity or failure patterns from a different model family.

Maximum scheduled observations are therefore 120, not the earlier 144.

The installed Codex subscription catalog did not expose the proposed
`gpt-5.6-sol` alias. Four GPT observations were consumed as transport/model
errors before Sol established that boundary. Before any successful GPT
observation, the lane was explicitly amended to the latest visible catalog
alias, `gpt-5.5`. Those four failures remain evidence and the lane's 48-sample
ceiling is unchanged; there is no retry or silent fallback.

The first `gpt-5.5` observation also exited before returning content while
using Codex's provider-side output-schema flag. The next untouched observation
uses the identical prompt and strict local schema parser without that optional
CLI flag. This is a bounded transport diagnosis, not a retry; failure closes
the remaining GPT lane.

## Accepted limitations

Yuri explicitly accepted a pragmatic agentic-surface comparison rather than a
pure-model comparison. Codex and Antigravity cannot prove an all-tools-off,
exact-revision, retention-equivalent transport. They run in fresh empty
sandboxes with explicit no-tool instructions; observed tool use invalidates an
observation, while unobservable tool use is retained as a methodology limit.

Yuri also accepted DeepSeek's documented mainland-China storage, caching, and
retention posture for this auxiliary synthetic-only lane. This approval does
not make DeepSeek eligible for EMR4 production use.

## Fail-closed execution

- Only the committed synthetic Silver v2 T3R1 projection may be transmitted.
- Each scheduled observation has one attempt and no retry.
- Provider errors consume the scheduled observation.
- Raw prompts and responses remain in process memory only and are not written
  to disk or committed.
- Durable evidence contains prompt and normalized-response hashes, normalized
  decisions, safe error codes, latency, and provider-reported usage when
  available.
- The runner resumes only by skipping already consumed lane/case/repeat keys;
  it never retries them.
- The product T3 live gate remains blocked. No runtime route, provider tool,
  database/audit write, appointment action, confirmation, deployment, release,
  or product authority is opened.

## Interpretation

The primary result may compare the practical GPT/Codex and
Gemini/Antigravity systems under this harness. It may not claim an exact or pure
underlying-model comparison. DeepSeek results are reported in a separate
auxiliary section and cannot select the production provider.
