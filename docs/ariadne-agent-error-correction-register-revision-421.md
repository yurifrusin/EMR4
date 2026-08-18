# Ariadne agent error and correction register — revision 421

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 421 preserves accepted revision 420 and adds AER-0491. The first
post-commit latch patch manually expanded short source `66bc1201` into an
incorrect full identifier before exact Git readback. A separate
`git rev-parse HEAD` exposed the mismatch while the latch edit was still
uncommitted.

The correction binds the checkpoint to exact source
`66bc12015d6184e00228d8abd8f77e1689f2e517` and requires full identifiers to
come only from completed Git readback. The canonical register contains 491
bounded incidents, all corrected or explicitly contained and none open.

The sparse worker worktree remains unpopulated. No container or occupied
provider call started, and no protected boundary changed.
