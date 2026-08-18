# DeepSeek native Harness authored-synthetic agentic-coding traceability rehearsal closeout

Date: 2026-08-18

Timestamp: 2026-08-18T15:32:45.5143044+10:00 (Australia/Brisbane)

Status: accepted bounded occupied traceability; worker completion not demonstrated

Reasoning level: high

Accepted evidence source: `25067e7d633eae597929d6969a35b22b735b253e`

Result:
`bounded_occupied_traceability_demonstrated_worker_completion_not_demonstrated`

## Outcome

The pinned official `@deepseek-ai/dsh@0.1.0-rc.7` package ran one occupied
DeepSeek V4 Flash/high session in a separately rooted generic synthetic Git
workspace. The session used the exact `rehearsal-write` permission preset,
workspace-write sandbox, approval `never`, one parallel tool call, zero
automatic retries, zero fallbacks, no auxiliary model route and disabled
telemetry. The profile patch digest is
`1c430fae949d34474855b699d7b48f9a0b4ae1db8382c0d0b8adb1661b22f897`.

The process lasted 24,903 ms and produced a durable attributable session with
six successful model-usage anchors, eight ordered tool calls and eight tool
results. The worker read its local instructions and both fixture files, ran
the failing four-test suite, attempted an edit, received `FS_STALE_VERSION`,
reread the file and then applied the correct bounded repair. Independent
readback found only `intervals.py` changed and all four tests passed.

The worker did not add the exactly one required regression test and did not
emit a successful terminal summary. Its seventh request was rejected locally
by the rehearsal's six-request ceiling, so the process exited 1 with an
attributable local `RATE_LIMIT`. This is therefore an occupied traceability
pass and a correct partial implementation, not a complete worker-task pass.
The ceiling was a rehearsal containment control; Yuri's prepaid DeepSeek
balance is the monetary boundary for future EMR4 use, so a Harness-native turn
budget is not required.

The six successful steps consumed 5,845 uncached input tokens, 29,440 cached
input tokens and 2,936 output tokens, including 1,958 reasoning tokens. The
estimated provider cost at the official 2026-08-18 Flash rates was
`$0.001722812`. No retry, fallback, title, compaction, telemetry, web or
subagent request occurred.

After sanitized reduction, the exact disposable root was moved to the Windows
Recycle Bin. Readback confirmed its absence from the active filesystem. Raw
session/reasoning content was not copied into EMR4 and remains recoverable
only with the disposable directory until the Recycle Bin is emptied.

## Assessment

The native Harness demonstrated materially stronger orchestrator visibility
than the recent Claude Code non-results: exact session identity, ordered tool
history, per-step token usage, explicit stale-version recovery, terminal
classification and a bounded candidate diff are all attributable. It also
exposed versatile controls that can be pinned per session: named permission
presets, minimized tool sets, model routing, retry/fallback policy, auxiliary
route suppression, telemetry control, session persistence and resumability.

One attempt does not prove lower failure frequency or complete worker
reliability. It does prove enough control and observability to stop broad
synthetic qualification and move to monitored low-risk EMR4 development. The
next evidence should come from real repository work, with Sol reviewing every
candidate before admission.

## EMR4 worker profile direction

Use a small versioned profile family rather than one permissive universal
worker:

- `emr4-readonly-review`: repository-local read/search and admitted test
  execution only; no edits and no auxiliary model routes.
- `emr4-bounded-worker`: exact owned paths, read/search/edit/test tools,
  single-tool serial execution, approval `never`, zero automatic retry and no
  fallback. “Bounded” describes authority and file scope, not account spend.
- `emr4-provider-free`: the same trace discipline with no credential injection
  and no provider call, for architecture, profile and deterministic admission
  work.
- specialist workflow or subagent presets only when an accepted tranche
  assigns an independent work package and prevailing policy permits them.

Every occupied run should pin the package and profile digests, start a fresh
session, disable title/compaction/telemetry model routes unless explicitly
needed, preserve sanitized JSONL-derived metadata, verify exact HEAD and owned
paths, and resume a session only for the same interrupted tranche. Provider
prepay supplies the monetary ceiling; EMR4 supplies the authority, data and
tool ceiling.

## Parallelism closeout

- DeepSeek lane: completed with positive leverage. It owns the single occupied
  candidate and sanitized session metadata; its task result is incomplete.
- Gemini lane: declined, neutral. No EMR4 product/runtime source changed and
  deterministic Git plus unittest readback were sufficient for this transport
  rehearsal.
- Native-subagent lane: declined, neutral. Current developer policy prohibits
  proactive delegation and the closeout has no independent parallel package.

Sol alone admits the evidence and closeout.

## Protected boundaries

No EMR4 source or untracked file entered the Harness workspace. No product,
patient, clinical, historical-diary or protected data was used. No ordinary
practice, generic-status `Arrived`, action grammar, first-party client,
waiting-area movement, live runtime, deployment, production, release, Pages
or protected ref changed. `docs/branding/` and every unrelated untracked file
remain excluded. Local/origin `master` and `handoff/current` remain protected
at `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

## Next tranche

Begin
`deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-admission`.
It may codify the versioned minimal profile family and use the bounded worker
for one low-risk, provider-free EMR4 development package with exact owned
paths and Sol review. It authorises no product/patient/clinical data, live
provider or runtime, ordinary-practice enablement, deployment, release, Pages
or protected-ref movement. It is a monitored trial transport, not a blanket
default-worker promotion.
