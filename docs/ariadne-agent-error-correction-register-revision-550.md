# Ariadne agent-error and correction register — revision 550

Date: 2026-08-19
Timestamp: 2026-08-19T09:14:20.5352564+10:00 (Australia/Brisbane)

## Revision scope

Revision 550 preserves AER-0638. After AER-0637, the complete register suite found two stale hand-maintained projections: the explicit incident-ID population range still ended at AER-0636 and the repository-origin aggregate remained one lower than the generated report. Both failures belong to the same register-advance attempt.

Every affected fixture now reads revision 550 and 638 incidents; repository-origin and repository-defect counts are 99, and the untrusted-partial-worktree count is 132. All 638 incidents remain corrected or contained and none open. This is construction rerun nine, separate from the zero-rerun steady-state replay.

## Prevention

The proposed clockwork projection owns population and aggregate readings from one validated register source. Until adoption, the generated report must be compared to every remaining exact fixture before the full suite runs.
