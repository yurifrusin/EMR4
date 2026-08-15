# Ariadne agent error and correction register — revision 291

Date: 2026-08-15

Timestamp: 2026-08-15T17:38:04+10:00 (Australia/Brisbane)

Revision 291 records AER-0330. The register now contains 330 bounded known
incidents, all corrected or contained by an explicit control.

AER-0330 preserves one rejected Ariadne Prime-derived harness-adaptation
preplanning state. Its parallelism assessment did not use the exact live
active-operation identifier and used invented `expected_leverage` values
instead of the configured vocabulary. The deterministic preflight returned
`revision_required` before any native subagent, DeepSeek or Gemini dispatch;
the candidate remained unchanged and no provider/model call occurred.

Sol corrected the same bounded state before dispatch: the assessment was
aligned to the exact live operation identifier, DeepSeek and native-subagent
leverage became `positive`, Gemini leverage became `required_independence`, and
a fresh five-source receipt passed. The leverage defect is the third occurrence
of `orchestrator.parallelism_expected_leverage_vocabulary_mismatch`, following
AER-0314 and AER-0321. Its stronger preventive control is to copy
`operation_id` from the validated latch and select each leverage value from the
configured enum before receipt generation, leaving timing and qualifications
to rationale text.
