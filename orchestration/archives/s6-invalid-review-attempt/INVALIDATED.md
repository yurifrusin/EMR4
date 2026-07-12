# Invalidated S6 Review Attempts

These artifacts are retained for the S7 Ariadne cross-boundary contract audit
and are not acceptance evidence.

## Attempt 1

The orchestrator created the review worktree at `2842bb3b` but accidentally ran
the candidate cherry-pick in the integration worktree. The reviewer therefore
did not have the candidate in its own checkout. Its PASS narrative and adapter
receipt are invalid, even though its artifact was syntactically normalized with
`DECISION: pass` to demonstrate the marker mismatch.

## Attempt 2

The candidate was present, but strict DeepCode permissions stopped the reviewer
on an unexpected shell permission prompt before any artifact was written. The
blocked receipt is retained. It is not a candidate verdict.

## Accepted Evidence

Only `review-deepseek-s6-scope-delta-review-v3.md` and
`s6-scope-delta-review-v3-receipt.json` are the accepted Lane 2 evidence. V3
used in-worktree static review plus Sol's persisted deterministic verification
from the corrected candidate worktree.

STATUS: invalidated
