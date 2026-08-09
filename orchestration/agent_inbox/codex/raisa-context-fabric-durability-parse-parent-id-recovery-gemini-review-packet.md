# Independent veto packet: parse parent-ID recovery

Date: 2026-08-10

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r150`
- Branch: `codex/review-context-fabric-parse-parent-id-8f0d7f90`
- Rejected candidate: `2e59f606098b55e88bb2fbea0f0fdccaeb521193`
- Replacement candidate: `8f0d7f90aefd31d8ae060a099c937106e995c86c`
- Exact accepted parent: `c8ab7602e16e24453dbf909597b4f702a2388416`
- Protected refs: exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform and name the complete five-source `AGENTS.md` rehydration.

## Purpose

Independently decide whether the replacement correctly repairs a fabricated
full Git parent binding and preserves the non-accepting parse characterization
contract. The prior r149 `pass` is explicitly rejected by
`orchestration/agent_inbox/codex/raisa-context-fabric-durability-parse-characterization-review-sol-rejection.json`.

## Mandatory exact-ref challenge

Run these independently and quote their exact outputs:

```powershell
git rev-parse --verify c8ab7602^{commit}
git cat-file -t c8ab7602e16e24453dbf909597b4f702a2388416
git merge-base --is-ancestor c8ab7602e16e24453dbf909597b4f702a2388416 8f0d7f90aefd31d8ae060a099c937106e995c86c
git diff --check c8ab7602e16e24453dbf909597b4f702a2388416..8f0d7f90aefd31d8ae060a099c937106e995c86c
```

The first must return exactly
`c8ab7602e16e24453dbf909597b4f702a2388416`; the second exactly `commit`; the
last two must exit zero. Compare the complete forty characters with
`rehearsal-contract.json`, the parse rebind ledger and `PARENT_HEAD` in the plan
test. Do not abbreviate or infer any hash.

## Other required challenges

Verify and report:

1. exact replacement HEAD, clean worktree, protected refs and both diffs;
2. the former recorded parent
   `c8ab760220bc40863a18feaa3fc13a3d6ba04ba6` is not a Git object and appears
   only in preserved rejected provenance, not the corrected contract/ledger/test;
3. Sol's rejection keeps the former verifier receipt immutable but grants it no
   acceptance; AER-0192 and AER-0193 accurately record both failures;
4. corrected characterization contract SHA-256 is
   `a34fb46701396f9626a11f94024e233637e381f15e50d10bbec3cba6f1c4a0fa`;
5. inert SQL remains exact SHA-256
   `ca22e47e847409f1ae8a81f62dd7f5f8402a43176d9015211f657204460fbdbb`,
   1,435,142 LF bytes and 421 statements;
6. mode remains `characterization_only`, expected digests remain exactly `{}`
   and characterization cannot return a parse pass;
7. the new deterministic plan test asks Git to resolve the full parent commit;
8. accepted mutable parse evidence and protected historical failure evidence
   remain unmodified and unstaged;
9. the exact 459-test packet, twelve-file Ruff, builder/inert and diff checks
   pass; and
10. no Docker/PostgreSQL run or other closed authority opened, with clean exact
    postcondition.

Run the same explicit 11-file pytest and twelve-file Ruff population from the
committed r149 packet, using unique basetemp
`C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r150`; its count is now 459.
Also run builder `--check`, inert `check`, both exact-ref commands above,
`git diff --check 2e59f606098b55e88bb2fbea0f0fdccaeb521193..8f0d7f90aefd31d8ae060a099c937106e995c86c`,
`git status --short --branch`, and `git rev-parse HEAD`.

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, inspect branding,
access product/protected data, move refs or accept your own output. No provider
other than this exact Gemini verifier call is allowed.

## Decision rule

Return `fail` for any full-ID mismatch, unresolved object, invalid-range claim,
P0-P2 finding, incomplete 459-test packet or dirty postcondition. Otherwise
return one exact `pass` with verbatim full-object outputs and command counts.
