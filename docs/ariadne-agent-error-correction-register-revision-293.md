# Ariadne agent error and correction register — revision 293

Date: 2026-08-15

Timestamp: 2026-08-15T19:53:46+10:00 (Australia/Brisbane)

Revision 293 records AER-0332. The register now contains 332 bounded known
incidents, all corrected or contained by an explicit control.

AER-0332 preserves a low-severity process-orchestration timeout mismatch during
the first Gemini 3.7 Flash/high veto launch. Sol configured the outer shell for
120 seconds while the Antigravity launcher declared a 30-minute print timeout.
The shell returned exit 124 after 124 seconds, but exact inspection showed the
original authorized Python and `agy` process still active.

Sol treated the shell result as non-terminal, inspected the exact process tree,
receipt path and verifier worktree, and did not retry. The original process then
completed with one valid pass receipt for
`79f5d6cf1cbe4ca9ad4893f257e92eccfd2ac2ce`; postflight confirmed the same HEAD
and a clean worktree. No duplicate verifier dispatch or second model call
occurred.

This is the second occurrence of
`harness.shell_wrapper_timeout_before_live_external_worker_completion`, after
AER-0256. The strengthened control requires every outer orchestration timeout
to cover the declared inner adapter timeout. After any outer timeout, exact
process, receipt and worktree state must be inspected before recovery, and a
duplicate dispatch is forbidden while the original authorized process may
still complete.
