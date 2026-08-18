# DeepSeek native Harness authored-synthetic agentic-coding traceability rehearsal plan

Date: 2026-08-18

Timestamp: 2026-08-18T14:50:55.4816780+10:00 (Australia/Brisbane)

Status: frozen

Reasoning level: high

Operation:
`deepseek-native-harness-authored-synthetic-agentic-coding-traceability-rehearsal`

## Objective

Run one bounded but materially agentic DeepSeek V4 Flash/high coding session
through the official native DeepSeek Harness. The session must inspect a small
authored-synthetic Python repository, diagnose a deterministic defect, edit
only allowlisted files, add one focused regression test, run the complete
synthetic test suite and report its result. Preserve enough attributable
terminal, session, model-turn and tool-event evidence to judge whether the
native Harness is a viable traceable worker transport for later EMR4 trials.

This succeeds the accepted no-call micro-rehearsal at source
`ed044625b6f1e59d323c21ced6ec6e2372a11d3f`. It does not erase that preliminary
closeout and it does not change EMR4's default DeepSeek-via-Claude-Code worker
allocation.

## Exact upstream and isolation

- Use only official package `@deepseek-ai/dsh@0.1.0-rc.7`, corresponding to
  release tag `dsh-v0.1.0-rc.7`, with exact registry shasum and integrity
  rechecked against the accepted micro evidence.
- Bootstrap with `npx` in one newly created disposable directory under
  `C:\Users\sarashera\EMR4-worktrees\`, with its own npm cache and Harness home.
- Make no global installation, PATH, shell-profile, user-profile or durable
  Harness configuration change.
- Put no EMR4 file, name, source excerpt, prompt, diff, test, untracked file or
  repository metadata in the disposable workspace. Use newly authored generic
  interval-processing fixtures only.
- Initialise the synthetic workspace as its own Git repository and commit its
  deliberately failing baseline before the Harness starts. This makes the
  permitted edit surface and final diff independently attributable.

## Synthetic work package

The mini-repository contains a small pure-Python interval-merging package and
deterministic tests. Its seeded implementation mishandles one nested/adjacent
interval boundary. The exact task packet instructs the Harness to:

1. inspect the repository and failing tests;
2. diagnose the defect without changing dependencies or test configuration;
3. edit the implementation and add exactly one focused regression test;
4. run the complete synthetic test suite; and
5. return a concise summary naming changed files and the test result.

Only the synthetic implementation file and its one test file may change.
Generated caches may appear but are excluded from the candidate diff and
removed during cleanup.

## Fail-closed execution sequence

1. Bootstrap and inspect the pinned package offline after download. Determine
   the exact rc.7 permission mode, native tool identifiers, model-turn bound,
   session format and headless invocation from package source/help before any
   provider-capable process.
2. Build one exact profile that enables only workspace-scoped filesystem read,
   search, string-replacement/editor and PowerShell execution needed for the
   synthetic test command. Disable Bash, web, browser, MCP/ACP, plugins,
   skills, jobs, workflows, subagents, nested agents, auxiliary title-model
   requests and telemetry.
3. Use a non-empty valid retry-code allowlist with `maxRetries: 0`; select only
   DeepSeek V4 Flash with high reasoning effort, no fallback, and at most 2,048
   output tokens per model turn.
4. Run the exact occupied profile first with `DEEPSEEK_API_KEY` absent in a
   separate empty diagnostic Harness home. Admission requires the plugin tree
   and tools to load and then fail specifically at the missing-credential
   boundary before provider I/O. Any earlier configuration/tool failure stops
   the tranche before an occupied request.
5. Admit exactly one occupied headless session only if rc.7 exposes an
   enforceable ceiling of six model turns or fewer. Automatic retries and
   fallback remain zero. The session has a 10-minute hard wall-clock bound and
   a USD 0.25 maximum derived from the admitted model-turn/output-token
   envelope; inability to establish the envelope stops without a call.
6. Do not repeat an occupied session. A model error, tool error, timeout,
   malformed trace, wrong edit, failing test or incomplete task is evidence
   for the conclusion, not authority to spend again.
7. After exit, independently run the complete synthetic tests, inspect the
   exact Git diff and verify that only allowlisted files changed. Reduce raw
   session material to sanitized metadata, then send the exact disposable
   directory/cache/Harness homes to the Windows Recycle Bin and verify absence.

## Evidence retained

Retain package identity, effective non-secret configuration hash, process
start/end/duration and exit code, stdout/stderr byte counts and hashes,
sanitized final answer, session identifier and file names, ordered event-type
and tool-name sequence, provider model-turn/request count, retry/fallback and
auxiliary-call counts, token/cost accounting when exposed, tool exit statuses,
baseline/final Git hashes and diff, deterministic test results, and exact
cleanup readback.

Do not commit raw chain-of-thought/reasoning, provider request or response
bodies, credential/header material, environment dumps, package caches, raw
session transcripts or generated tool payload bodies. Raw synthetic session
material may be inspected only long enough to derive the bounded metadata and
must then be removed with the disposable workspace.

## Acceptance

An occupied pass requires all of the following:

- the exact pinned official package and admitted profile are attributable;
- the credential-absent boot reaches the missing-credential guard without a
  provider request;
- exactly one occupied session uses two to six model turns, zero automatic
  retries, zero fallbacks and no auxiliary model;
- its trace exposes an ordered inspect/read, edit and test tool sequence bound
  to the same session and process;
- only the two allowlisted synthetic files change, exactly one regression test
  is added and the independently rerun complete suite passes;
- terminal text, exit status, session trace and provider/tool accounting agree;
- wall time and USD 0.25 ceiling are respected; and
- cleanup and every EMR4/protected boundary pass.

A bounded failed occupied result is still valid comparison evidence if its
failure stage, model/tool/request accounting and cleanup remain attributable.
It is not an occupied pass and does not justify a retry or default-transport
change.

## Protected boundaries

No EMR4 product or runtime change; no product, patient, clinical,
historical-diary, real-person, protected-holdout or product-derived data; no
ordinary-practice authority; no action grammar, client, route, waiting-area or
status change; no deployment, production, release, Pages or protected-ref
movement. Local/origin `master` and `handoff/current` remain exact protected
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. `docs/branding/` and every
unrelated untracked file remain preserved and excluded. Repository staging is
explicit-path only.

## Parallelism assessment

- DeepSeek native-Harness lane: `planned`, positive leverage. It owns the one
  serial authored-synthetic agentic coding session and automatically produced
  native session/tool evidence.
- Gemini lane: `declined`, neutral leverage. This is a transport-observability
  measurement over deterministic synthetic code; a second paid model cannot
  independently validate Harness transport facts and owns no product review.
- Native-subagent lane: `declined`, neutral leverage. Current developer policy
  prohibits proactive delegation; no independent write or review package is
  needed for the synthetic fixture.

All steps are serial: plan commit, package/config discovery, credential-absent
admission, one occupied session, deterministic readback, evidence reduction,
cleanup, closeout and task-branch publication.

## Claim boundary

Passing can establish that this pinned Windows rc.7 invocation completed one
representative small agentic coding loop with attributable model/tool/session
evidence. It cannot establish general DeepSeek model quality, comparative
superiority, long-run reliability, production suitability, privacy or
sovereignty, and it cannot select the native Harness as EMR4's default worker
transport without a later evidence-backed allocation decision.
