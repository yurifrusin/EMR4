# Ariadne agent error and correction register — revision 288

Date: 2026-08-15

Timestamp: 2026-08-15T14:08:08+10:00 (Australia/Brisbane)

Revision 288 records AER-0327. The register now contains 327 bounded known
incidents, all corrected or contained by an explicit control.

AER-0327 preserves a repeated detached-verifier-worktree orchestration error.
Sol created the exact clean candidate worktree at detached HEAD and generated a
pre-verifier receipt without first running the mandatory verifier-worktree
preflight. Antigravity rejected the empty branch before project creation or any
provider/model call; no review receipt was created and candidate
`bc066a1b639c5c57cc72f2697c063c5842511840` remained unchanged.

The unchanged worktree is now attached to
`codex/review-delete-confirm-representability-bc066a1b`. The exact verifier
preflight passes with clean status, exact HEAD, admitted branch prefix and zero
provider/model calls. A distinct corrected pre-verifier receipt is required
before the intended review attempt.

This is the fourth recurrence of
`orchestrator.detached_verifier_branch`. The durable prevention control is
explicit: never create an Antigravity verifier worktree using `--detach`; make
the named `codex/review-` branch at worktree creation and run the verifier
preflight before constructing the receipt.
