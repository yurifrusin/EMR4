# Ariadne agent-error register revision 11

Date: 2026-08-04

Status: fresh-worktree audit-hash defect corrected; deterministic and fresh
independent acceptance pending

## AER-0019: hashed JSONL evidence was not checkout-stable on Windows

Review 8 returned one admissible `revision_required` verdict against clean
exact candidate HEAD `794748c06b9a7c0d990ea5197d24e7cb859ae1e8`.
The original A3/B3 occupied audit file had LF bytes in the active worktree and
in the Git blob, but `.gitattributes` did not pin `*.jsonl`. With
`core.autocrlf=true`, a genuinely fresh Windows worktree checked that audit out
with CRLF bytes. Its SHA-256 therefore differed from the immutable interruption
evidence, and both acceptance and the reconciliation regression failed closed.

This is a repository checkout-stability defect, not evidence that the original
audit or immutable hash changed. The active bytes still match the preserved
`sha256:27d665f162ead5ee70d9db9cb39500bbe621e63b5bc0168b91ec6fb43d82bcad`.
The correction pins the A3/B3 JSONL evidence path to `text eol=lf` and adds a
mechanical test for the Git attribute, absent CRLF bytes and exact preserved
SHA-256. A fresh worktree must pass acceptance before AER-0019 or AER-0017 can
close.

Review 8 otherwise confirmed the one-call/no-release/no-Davida result,
provider-free finalizer, exact source-head distinctions, strict broker metadata
allowlist and unchanged authority/API Spine boundaries.
