# Ariadne agent error and correction register — revision 171

Date: 2026-08-10

Revision 171 records AER-0197 and raises the bounded incident population to
197. The incident is an independently caught verifier evidence-path
misreport, not a source-code defect, provider transport failure or database
failure.

The fresh r157 Gemini review correctly ran 140 focused tests and left exact
candidate `3b35f173d7a09fd4a8dfb65f0716c49b4de6e7f9` unchanged, but it labelled
tracked historical
`provider-free-behavior-transaction-failure-evidence-029.json` as the mutable
primary-only `provider-free-behavior-transaction-evidence.json`. The two files
share SHA-256 `09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`,
but the requested mutable alias is absent from the clean exact-HEAD review
worktree. Hash equality cannot substitute file identity.

Sol rejected the terminal pass before exact reproduction, proved the worktree
path facts directly and preserved the failed receipt. The corrected review
packet restricts verifier evidence claims to tracked immutable files present
at exact HEAD. Primary-only mutable hashes remain Sol-owned pre/postflight
checks and are not delegated across worktree isolation.

Counts after this revision:

- origin: 124 agent behavior, 22 harness, 43 repository and eight transport;
- category: 20 command-scope violations, 25 evidence misreports, 22 harness
  failures, 51 output-contract violations, three read-only violations, 25
  reasoning-claim errors, 43 repository defects and eight transport timeouts;
- candidate state: 64 accepted-candidate changes, 111 canonical-unchanged and
  22 untrusted partial worktrees.

No incident remains open. The corrected fresh r158 review subsequently passed
140 focused tests, Ruff and exact tracked-evidence reconciliation without
claiming or substituting any primary-only mutable path. One exact reproduction
run becomes eligible only after Sol commits and admits that corrected review.
