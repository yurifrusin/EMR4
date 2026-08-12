# Ariadne agent error and correction register — revision 254

Date: 2026-08-12

Revision 254 records and corrects AER-0286. The register now contains 286
bounded known incidents with none open.

While creating the final independent-review worktree, Sol manually expanded
short candidate ID `9c040ec4` into a nonexistent full SHA instead of resolving
the exact value from Git. `git worktree add` failed with `invalid reference`
before creating a directory, branch or worktree. No verifier, provider,
database, product or network operation occurred and the candidate stayed
unchanged.

The corrected flow reads the exact commit with `git rev-parse HEAD`, carries
that literal result into worktree creation and verifies it again with the
read-only worktree preflight. Exact identities are outputs of Git, not values
to complete from memory.
