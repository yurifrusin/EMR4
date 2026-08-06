# Ariadne semantic-recovery independent veto — durability state-machine rehearsal

- Decision: `REVISION_REQUIRED`
- Exact candidate: `62d0cc5402fe93c4f37cf23f587fc04a7daf01c3`
- Review branch: `codex/review-durability-state-machine-semantic-recovery-62d0cc54`
- Review worktree: `C:\Users\sarashera\EMR4-worktrees\r21`
- Reviewer authority: distinct fresh exact-head read-only veto

## P1 — closed count bucket advanced too early

Three coalesced causes produced `FIVE_PLUS`, although the closed privacy bucket
must remain `TWO_TO_FOUR` through the fourth cause. The resulting state still
passed `verify_state()`. The transition was deriving the next bucket only from
the already lossy bucket rather than from the complete minimized audit history.

## P1 — audit lifecycle could detach from rotation chronology

After one valid rotation, the canonical audit lifecycle revisions `[2, 4, 5]`
could be changed and rechained to `[3, 4, 5]`; the resealed state still passed
verification. Final lifecycle count and key-schedule interval count alone did
not preserve which revision belonged to the rotation.

Required correction: calculate coalesced buckets from exact cause count derived
from the canonical audit history, and retain a minimal payload-free canonical
rotation-revision ledger whose revisions and audit revisions form one exact,
non-overlapping lifecycle sequence.

## Postconditions

Testing stopped after the decisive reproducers. Before/after HEAD remained
`62d0cc5402fe93c4f37cf23f587fc04a7daf01c3`; the branch and review worktree
remained unchanged and clean. Local/origin `master` and `handoff/current`
remained `2e34bdad732fdab32fbf778280b3d3c70d66d602`. No file/ref mutation or
network, provider, database, source, runtime, product-data or protected-evidence
call occurred.
