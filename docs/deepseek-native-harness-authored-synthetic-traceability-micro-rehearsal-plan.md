# DeepSeek native Harness authored-synthetic traceability micro-rehearsal plan

Date: 2026-08-18

Timestamp: 2026-08-18T14:06:21.9124665+10:00 (Australia/Brisbane)

Status: frozen

Reasoning level: high

Operation:
`deepseek-native-harness-authored-synthetic-traceability-micro-rehearsal`

## Objective

Run one deliberately tiny occupied DeepSeek V4 Flash/high task through the
official native DeepSeek Harness and determine whether its terminal and
durable trace evidence is materially clearer than the recent Claude Code
transport non-result. This is an evidence rehearsal, not a default-transport
change or a model-quality benchmark.

## Exact upstream and bootstrap

- Official repository: `https://github.com/deepseek-ai/deepseek-harness`.
- Immutable pre-release tag: `dsh-v0.1.0-rc.7`, release commit prefix
  `99f6f02`, released 2026-08-17.
- Package invocation: `npx -y @deepseek-ai/dsh@0.1.0-rc.7` with a dedicated
  temporary npm cache and an empty disposable working directory outside EMR4.
- No global install, system PATH change, shell profile change or user-owned
  application configuration is permitted.
- Official status remains developer preview with compatibility-breaking
  changes expected; the result cannot select production tooling.

Node `v24.18.0`, npm/npx `11.16.0` and the boolean presence of
`DEEPSEEK_API_KEY` are preflighted. The key value must never be printed,
persisted, hashed, transmitted anywhere except the official DeepSeek request
path used by the harness, or written into a command line or evidence file.

## Frozen execution

1. Create one new disposable directory with `New-Item` under the worker
   worktree root and verify its resolved path before any cleanup.
2. Use `npx` only inside that directory with a dedicated cache. Capture exact
   package/version and read-only `--help`/profile discovery before any model
   request.
3. Require a non-interactive/headless profile, explicit DeepSeek Flash model,
   high reasoning effort, no repository input and no requested tool action.
4. Submit exactly one authored-synthetic prompt:

   `Return exactly TRACE_OK and nothing else. Do not use tools.`

5. Permit at most one occupied provider request and at most USD 0.05. No retry,
   fallback model, subagent, MCP/ACP, filesystem edit, shell tool, browser,
   image, attachment, plugin or nested job is authorised.
6. Bound wall time to five minutes. Preserve exit code, start/end timestamps,
   stdout and stderr byte counts and SHA-256 digests, sanitized final text,
   harness version, session identifier if exposed, and the exact durable trace
   filenames/sequence/checksum metadata available after exit.
7. Never commit raw reasoning content, raw request/response bodies, credential
   material, environment dumps or provider headers. Durable evidence is
   sanitized non-PHI metadata and the exact benign terminal text only.
8. Verify cleanup of the disposable work directory and dedicated npm cache
   after evidence is copied into the named repository receipt.

If package resolution, version binding, headless invocation, default-deny tool
posture, cost bound, terminal evidence or safe cleanup cannot be established,
stop without an occupied request and close accurately as a bounded no-call
result.

## Acceptance

Pass requires all of the following:

- the exact pinned official package/version is observed;
- exactly one occupied Flash/high request starts and terminates without retry;
- the process exposes an unambiguous exit status and final text on stdout or a
  named structured result channel;
- durable session/trace evidence exists after process exit and is attributable
  to the same invocation, or the absence is explicitly demonstrated;
- the final result is `TRACE_OK` after only benign presentation normalization;
- no tool, subagent, repository read/write or non-harness network action is
  observed;
- the temporary working directory/cache are removed after bounded evidence is
  preserved; and
- EMR4 tracked state, all protected refs and all pre-existing untracked files
  remain unchanged.

A result may be accepted as `bounded_traceability_comparison_complete` without
declaring the native harness reliable enough to replace Claude Code. Default
transport selection requires a later evidence-backed decision, preferably an
A/B task representative of normal bounded implementation work.

## Protected boundaries

No EMR4 source is placed in the harness working directory or prompt. No
product, patient, clinical, historical-diary, protected-holdout, real-person or
product-derived data; no provider tool; no deployment, release, Pages,
production runtime, credential/IAM mutation, protected-ref movement or
ordinary-practice authority. `docs/branding/` and every unrelated untracked
file remain preserved; repository staging is explicit-path only.

## Parallelism assessment

- DeepSeek lane: `planned`, positive leverage. It owns only the single native
  harness request and its automatically produced local trace artifacts.
- Gemini lane: `declined`, neutral leverage. This tiny transport-observability
  measurement changes no product or repository runtime and does not justify a
  separate external veto; Sol deterministically admits the exact metadata.
- Native-subagent lane: `declined`, neutral leverage. Current developer policy
  prohibits proactive native delegation and parallel work would add briefing
  overhead to a one-process rehearsal.

All execution is serial: preflight, one occupied request, evidence admission,
cleanup, closeout and task-branch publication.

## Claim boundary

Passing can show only that this pinned Windows invocation produced a clearer
terminal/durable trace for one trivial authored-synthetic task. It cannot show
better model reasoning, coding quality, general reliability, production
suitability, sovereignty, privacy, cost efficiency or superiority over Claude
Code. It grants no continuing DeepSeek call and does not change EMR4's worker
allocation by itself.
