# Ariadne agent error and correction register — revision 277

Date: 2026-08-15

Timestamp: 2026-08-15T03:35:44+10:00 (Australia/Brisbane)

Revision 277 records AER-0316. The register now contains 316 bounded known
incidents, all corrected or contained by an explicit control.

AER-0316 records a recurrence of the detached-verifier worktree error in
AER-0012 and AER-0014. Sol created the exact clean candidate at detached HEAD;
the mandatory verifier preflight rejected it before receipt generation,
project creation or any model/provider call.

The unchanged worktree is now attached to disposable non-protected branch
`codex/review-reception-one-multi-change-editor-57d3cc30`. Its fresh exact-HEAD
and clean-status preflight passes. Future verifier worktrees must be created
directly on a named `codex/review` branch, never with `--detach`.
