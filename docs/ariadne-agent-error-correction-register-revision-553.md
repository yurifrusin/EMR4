# Ariadne agent-error and correction register — revision 553

Date: 2026-08-19
Timestamp: 2026-08-19T09:32:45.0527773+10:00 (Australia/Brisbane)

## Revision scope

Revision 553 preserves AER-0641. The first Gemini review attempt ran the allowlisted repair runner without `--publish`, but the runner still rewrote the tracked evidence file for the review HEAD. Antigravity's read-only worktree postcondition rejected the entire attempt and admitted no terminal decision.

Both persistent writes now sit behind the explicit `--publish` flag, and a regression test proves that the default runner leaves the evidence and report byte-identical. The register contains 641 incidents, all corrected or contained and none open. The latch records one review retry; aggregate construction cost is now twelve reruns.

Repair-only break-even remains two future closeouts at the measured nine-rerun avoidance rate. Cumulative break-even remains three closeouts.

## Prevention

The runner defaults to byte-preserving validation-only mode. Every persistent output requires `--publish`, which remains forbidden in verifier manifests.
