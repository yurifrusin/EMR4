# Ariadne agent-error register revision 64

Date: 2026-08-07

Status: exact-head verifier worktree path failure corrected

Revision 64 adds AER-0063. The first exact-head veto worktree attempt used the
descriptive destination
`C:/Users/sarashera/EMR4-worktrees/function-trigger-body-exact-veto-f51f5b65`.
Git reached an already-versioned long evidence filename and Windows rejected
the checkout with `Filename too long`; Git then failed the index reset and did
not retain or register the incomplete worktree.

The immutable candidate at
`f51f5b65dd77d9282e5325a5e4f17edd872d14df` remained unchanged and no reviewer
was dispatched. The failed destination is absent and unregistered. The
corrected distinct attempt uses the established short `rNN` worktree naming
pattern, performs the exact full-SHA verifier preflight before dispatch and
keeps the review read-only.

No protected ref moved and no provider, database, runtime, patient, product or
clinical-data boundary opened. Revision 64 contains 63 bounded incidents;
counts remain workflow-improvement signals only.
