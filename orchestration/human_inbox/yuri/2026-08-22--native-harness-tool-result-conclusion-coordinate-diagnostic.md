# Native Harness tool-result/conclusion diagnostic — paired closeout

Date: 2026-08-22

Timestamp: 2026-08-22T14:31:55.5258598+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

We have stopped one important clockwork circle from being circular. The
previous DeepSeek attempt told us that an edit had been called but not whether
the edit failed, was blocked, or simply failed to end the turn. The new control
now gives those outcomes different fixed readings.

The test was deliberately more comprehensive than the first atomic check. It
loaded the exact installed Harness tool runtime and drove five success and
failure cases through the real tool pipeline. All five produced the expected
reading. In particular, it confirmed that our old instruction to end the turn
was issued too late; the corrected runner issues it at the last safe point
before the edit executes.

No DeepSeek request was spent, no worker or broker was started, no product code
or patient data was touched, and cleanup is complete. This does not yet prove
that DeepSeek will perform the job usefully. It means the next bounded attempt
will either succeed or fail in a way the orchestrator can distinguish without
guessing and rerunning.

## Technical summary

- Result: `native_harness_tool_result_conclusion_coordinates_pass`.
- Reviewed source: `d9a5ca40328c336857a44e5b28f94b991f61d269`.
- Exact dependency: `@deepseek-ai/dsh-tools` `0.1.0-rc.7`, package/runtime/type
  sources digest-bound.
- Fixture: one local Node process, five real `ToolRuntime` executions, five
  unique schema-valid coordinates.
- Corrected seam: conclusion requested in pre-execute after boundary
  acceptance and before dispatch; post decision and final result observed
  separately.
- Negative coverage: unknown keys/values, contradictory combinations, false
  concluded success, concluding error and successful block all rejected.
- External activity: worker/model/provider/broker/network/database/Docker all
  zero; retry/resume/fallback all zero.
- Cleanup: owned process absent, exact root absent, no raw sensitive material
  retained.
- Product/API effect: none; protected refs unchanged.

The next tranche will freeze one new, separately identified native-Harness
useful-worker attempt using this typed runner, the same closed default-off
runbook candidate, one DeepSeek request and no retry. It is not a reopening of
the consumed attempt. After that proof, the programme can return to the
default-off canonical check-in route-adapter convergence work with a materially
more controllable DeepSeek lane.
