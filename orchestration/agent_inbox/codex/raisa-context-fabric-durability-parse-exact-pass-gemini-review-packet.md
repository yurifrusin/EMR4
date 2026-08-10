# Independent veto packet: parse exact reproduction pass

Date: 2026-08-10

Decision required: exactly one terminal `pass` or `fail`

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r153`
- Branch: `codex/review-context-fabric-parse-exact-pass-ebcd813b`
- Candidate: `ebcd813b22db6f8da49af5aa44652d047a323b8c`
- Accepted pre-run candidate: `f4cdb2ca04510f70d238e9b0d6df84586938f6df`
- Protected refs: exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform and name the complete five-source `AGENTS.md` rehydration.

Independently verify the immutable exact-reproduction evidence file has byte
SHA-256 `041ccbf16d22b80872a397968470c8e215625350e31c87511789775cd2bbb2ce`,
attempt `1b606b88bd168f7e48d65224`, exact pass result, contract `b81be9b7...`,
artifact `ca22e47e...`, all 15 exact digests, and cleanup container
`633a6466452e93679526a61265854d1d32bb0b8c2a454a549c6d847845dd51ee`
removed with absence verified. Confirm the repository test schema-validates and
hash-binds every fact.

Verify the mutable accepted evidence remains untracked at SHA-256 `97d1385c...`
and protected historical failure remains untracked at `3bf66870...`; neither is
in the candidate diff. Confirm preexecution receipt, exact local image, one-run
boundary, no operational database, and independent exact-ID absence result.

Repeat the exact builder, inert, eleven-file pytest, twelve-file Ruff check and
format commands from the committed parse exact-evidence packet, using basetemp
`emr4-gemini-r153`. The packet now contains exactly 463 tests. Also run:

```powershell
git diff --check f4cdb2ca04510f70d238e9b0d6df84586938f6df..ebcd813b22db6f8da49af5aa44652d047a323b8c
git status --short --branch
git rev-parse HEAD
```

Do not edit, format, commit, push, start Docker/PostgreSQL, inspect branding,
access product/protected data, deploy or move refs. Return `fail` for any P0-P2
finding, digest mismatch, incomplete 463-test packet, evidence mutation or dirty
postcondition. Otherwise return exactly one `pass` with counts and HEAD.
