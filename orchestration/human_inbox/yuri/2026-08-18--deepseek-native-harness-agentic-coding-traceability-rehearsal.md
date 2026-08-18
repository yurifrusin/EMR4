# DeepSeek native Harness broader rehearsal — lay and technical summary

Date: 2026-08-18

Timestamp: 2026-08-18T15:32:45.5143044+10:00 (Australia/Brisbane)

Status: accepted traceability result; complete worker reliability not yet demonstrated

Yuri attention required: no.

## Lay summary

The broader native-Harness rehearsal produced the signal we needed. DeepSeek
worked through a real multi-step coding loop: it read the instructions and
files, ran the failing tests, encountered a safe stale-file refusal, reread
the file, made the correct repair and left all four tests passing.

More importantly, the work was visible. We have an exact session, every tool
step, per-step token accounting, the recovered error, the final diff and the
precise terminal cause. That is a substantial improvement over the recent
Claude Code runs that failed without an attributable worker result.

It did not fully finish the task. It failed to add the requested regression
test and did not give a final success summary before our locally imposed
six-request ceiling stopped request seven. So I am not calling DeepSeek or the
Harness reliable yet. I am calling the Harness controllable and traceable
enough to move on.

There is no reason for another broad ceremonial synthetic test. The next step
is to formalise a few small EMR4 presets, then use the native Harness on one
real low-risk, provider-free development package and monitor it closely. Your
prepaid DeepSeek balance can remain the monetary budget; EMR4 will enforce the
file, tool, data and authority limits.

## Technical summary

The pinned package was `@deepseek-ai/dsh@0.1.0-rc.7`; the exact profile patch
digest was
`1c430fae949d34474855b699d7b48f9a0b4ae1db8382c0d0b8adb1661b22f897`.
The session ran Flash/high with workspace-write, approval `never`, one parallel
tool call, zero automatic retries/fallbacks, disabled telemetry and no title or
compaction model route.

The 24,903 ms process created six successful usage-bearing model steps and
eight tool calls/results: instructions read, workspace glob, two source reads,
unittest, stale edit refusal, reread and successful edit. Independent readback
found only `intervals.py` changed; 4/4 tests passed. The task remained
incomplete because `test_intervals.py` was unchanged and no terminal summary
was emitted before local request ordinal seven was denied.

Usage was 5,845 uncached input, 29,440 cache-read and 2,936 output tokens; the
estimated cost was `$0.001722812`. Sanitized metadata only entered EMR4. Raw
session/reasoning material and the synthetic Git workspace were sent to the
Windows Recycle Bin after reduction, and the exact active path is absent.

Register revision 392 contains 450 corrected/contained incidents and none
open. No product source, patient/clinical data, ordinary-practice flag, client,
waiting-area action, live runtime, deployment, Pages or protected ref changed.
The proposed profile family is `emr4-readonly-review`,
`emr4-bounded-worker`, `emr4-provider-free`, plus specialist/subagent presets
only when an accepted tranche and prevailing policy allow them.
