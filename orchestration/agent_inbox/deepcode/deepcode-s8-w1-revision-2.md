# S8 W1 Revision 2 - Restore Ownership and Valid Closeout

Resume W1 from the current worktree. Revision 1's focused tests passed 13/13,
but its closeout is rejected for two reasons:

1. the PTY receipt says `turn_completion_observed: false`;
2. `review/harness.py` was modified outside W1's exclusive ownership.

Restore `review/harness.py` exactly to the branch base. Put any additional
Office UI stubbing required by `review/test_taskpane_diary_launch.py` inside
that W1-owned test file instead. Preserve the 13 honest behavioral tests,
including the exactly-two-call 12007 proof.

Run the focused suite with the shared main venv, `node --check`, and `git diff
--check`. Write a fresh completion artifact with exact results, then create a
local candidate commit on `deepcode/s8-w1-launch`. The refreshed DeepCode
permission policy permits local Git mutation but still forbids network/push and
integration. End with `STATUS: complete` and finish the turn normally so the
adapter observes completion.

No production behavior expansion, shared-harness edit, push, or integration
authority.
