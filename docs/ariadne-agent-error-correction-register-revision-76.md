# Ariadne agent-error register revision 76

Date: 2026-08-08

Status: repeated Windows descriptive-worktree failure contained

Revision 76 adds AER-0078. The first R6 final-review checkout repeated the
known Windows long-path failure because its destination was descriptive rather
than the required short `rNN` form. Git returned `Filename too long`; the
destination was absent and unregistered afterward, no reviewer was dispatched
from it, and candidate
`0bfd3e7545dfa1a7431f856b5eaf2aac32a9292d` remained unchanged.

The successor checkout uses `C:/Users/sarashera/EMR4-worktrees/r34` on the same
exact review branch and candidate. Its independent worktree preflight passed
with a clean status before dispatch. Future Windows verifier allocation must
choose the next short `rNN` destination first and keep descriptive identity in
the branch, packet and receipt only.

Revision 76 contains 78 bounded incidents. Incident counts remain
workflow-improvement signals only.
