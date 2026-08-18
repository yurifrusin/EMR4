# Ariadne agent error and correction register — revision 513

Date: 2026-08-19

Timestamp: 2026-08-19T04:02:20.6269613+10:00 (Australia/Brisbane)

Status: accepted closed register update

## Change

AER-0592 records recurrence of a narrowed verifier branch-prefix argument. The
preflight requires the exact configured `codex/review-` value. AER-0593 records
the next invocation binding `--serial-repo-root` to the primary checkout rather
than the exact review worktree. Both attempts stopped locally before any
provider call and left candidate `4204ec6348abb0f92b1a30314699d4a469fa860a`
unchanged. The third invocation used one exact review-root reading and passed.

Revision 513 contains 593 bounded incidents. All are corrected or contained;
none is open.

## Prevention

Generate verifier prefix and worktree-root arguments from typed execution-
policy and review-worktree readings. `branch_prefix` is the exact enum
`codex/review-`; `cwd`, `serial_repo_root` and the manifest's external runner
`--repo-root` must all resolve to the same exact review worktree.
