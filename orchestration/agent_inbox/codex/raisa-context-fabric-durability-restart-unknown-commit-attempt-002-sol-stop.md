# Sol stop decision — CF-D2 attempt 002

Date: 2026-08-11

Decision: `revision_required_user_attention`

Sol admits the immutable attempt-002 artifact as valid failure evidence only.
It is not a CF-D2 acceptance artifact and releases no crash/restart,
unknown-commit, recovery, retry or downstream durability authority.

The candidate passed all ten fixture preconditions and stopped before its first
restart with a closed but coordinate-ambiguous terminal failure. Exact cleanup
and all zero-external-operation claims reconcile. The one authorised mechanical
recovery was already consumed after attempt 001, so another runtime would
expand authority rather than continue the frozen plan.

CF-D2 and its dependent key-rotation plus retention/purge direction are stopped
pending Yuri's explicit choice recorded in the paired human-inbox closeout.
