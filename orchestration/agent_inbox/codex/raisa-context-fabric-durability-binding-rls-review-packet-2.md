# Independent veto 2: admission-receiver binding-RLS recovery

Date: 2026-08-10

Decision required: exactly one terminal structured `pass` or
`revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r144`
- Branch: `codex/review-context-fabric-binding-rls-fde9027b`
- Original recovery baseline: `75160f4497798665f83c31ca08079a760aed1136`
- First review candidate: `06951c61c56ca760cccf30bda135ebd5f58a2d78`
- Corrected candidate: `fde9027bc75a2b9620cb03538caeb685e323384f`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First read `AGENTS.md` completely and perform its complete five-source
rehydration, naming `live_handover_current_baton`,
`current_authority_allocation`, `active_plan_and_acceptance`,
`protected_evidence_boundaries`, and `git_refs_and_worktree`.

## Non-inheritance and authority

This is a fresh project and fresh exact-HEAD review. Do not inherit the prior
`pass`. Read these three tracked records:

1. `orchestration/agent_inbox/codex/raisa-context-fabric-durability-binding-rls-review-packet.md`
2. `orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-binding-rls-review-receipt.json`
3. `orchestration/agent_inbox/codex/raisa-context-fabric-durability-binding-rls-review-count-mismatch-sol-rejection.json`

The first verdict is rejected because its own receipt reported 553 passed
against an exact 552 requirement but returned `pass` despite the packet's
mandatory mismatch rule. This candidate preserves that incident as AER-0183.
No behavior runtime followed it.

This is review only. Do not edit, format, commit, push, start
Docker/PostgreSQL, run either runtime harness, contact any product/provider
surface other than this one verifier invocation, access
patient/clinical/product or protected data, inspect `docs/branding/`, move refs
or accept your own output.

## Required challenges

1. Verify clean exact HEAD
   `fde9027bc75a2b9620cb03538caeb685e323384f` before and after review.
2. Inspect full recovery diff
   `75160f4497798665f83c31ca08079a760aed1136..fde9027bc75a2b9620cb03538caeb685e323384f`:
   exactly 96 files, 4,076 insertions and 119 deletions.
3. Reperform every substantive challenge 3 through 23 in the first tracked
   review packet. Every semantic digest, immutable attempt-031 fact, exact RLS
   scope, parse reproduction, six-parent behavior binding, scenario population
   and closed authority remains mandatory.
4. Inspect count-recovery diff
   `06951c61c56ca760cccf30bda135ebd5f58a2d78..fde9027bc75a2b9620cb03538caeb685e323384f`:
   exactly 13 files, 512 insertions and 17 deletions. Verify it adds only the
   preserved first-review packet/receipt/preflight/postflight, Sol rejection,
   AER-0183, generated register report and precommit evidence.
5. Verify the first review receipt SHA-256 is
   `562b0a9423d88a9d1d30d500c8e67e538d7e636db219f4d5e313b0d798cc7f69`,
   was wrapper-valid and clean, reported 553 passed, and is explicitly not an
   accepted verdict.
6. Verify AER-0183 classifies the incorrect terminal decision without claiming
   a semantic candidate defect. Register revision 157 must contain exactly 183
   corrected incidents and zero open incidents.
7. Verify behavior contract SHA-256 remains
   `678252f6e5bca28118e041880c675e25ca4a51be999ccddd5c121d91d01c477a`
   and scenario population SHA-256 remains
   `eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`.
8. Run the exact pytest, Ruff check and Ruff format commands from the first
   tracked packet with only these two mechanical substitutions:
   `emr4-gemini-r143` becomes `emr4-gemini-r144`, and the required pytest
   count becomes exactly **554 passed**. The test path set remains the same 20
   exact files and the Ruff path set remains the same 34 exact files.
9. Run both full and working-tree `git diff --check`, confirm no Docker command
   or behavior/parse harness ran during review, and reverify protected refs.

Return `revision_required` for any P0-P2 finding, authority widening, evidence
mismatch, scenario drift, result other than exactly 554 passed tests, anything
other than 34 Ruff-clean/formatted files, invalid dispatch receipt or dirty
postcondition. Otherwise return one exact structured `pass`, stating all
commands/counts, exact HEAD, previous-verdict non-inheritance and post-review
cleanliness.
