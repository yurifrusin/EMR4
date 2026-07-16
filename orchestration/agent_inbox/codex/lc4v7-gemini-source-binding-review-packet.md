# LC4V7 Gemini Source-Binding Amendment Review

Date: 2026-07-16

Review exact head `b4f8cb18fe4229aea7fe230822a9b2832f906bc9` in
`C:\Users\sarashera\EMR4-worktrees\antigravity` on
`antigravity/current`. This is a fresh Gemini 3.5 Flash/medium veto before any
V7 corpus content exists.

The previously passed empty framework at `186ccf44` had a pre-content
integration flaw: an unconsumed seal committed after corpus authorship cannot
contain the hash of its own future commit. Sol amended only the runner and its
focused tests so `source_commit` now means the earlier committed corpus-source
commit. The runner must prove that commit is an ancestor of the execution head
and contains the exact corpus blob at the explicit path. The later manifest and
seal commit binds that source commit, current framework hashes, manifest, and
corpus without self-reference.

Read the V7 contract, frozen acceptance rule, prior Gemini review, exact diff
`186ccf44..b4f8cb18`, amended runner, and V7 focused tests. Run both focused
test files serially. Verify:

1. source commit format is exact;
2. corpus path must remain inside the repository;
3. the source commit must be an ancestor of execution HEAD;
4. the exact committed blob at that path must have the live canonical corpus
   hash;
5. manifest/seal source/hash checks still fail closed;
6. seal consumption remains before corpus validation/runtime execution;
7. no Gold, scenario identity, prior holdout, or V7 content was introduced; and
8. all original layer-specific scoring and aggregate-only gates remain intact.

Holdouts v1-v6 remain sealed. Do not open, list, search, import, or run any
protected prior-version fixture, support, manifest, seal, receipt, or test. Do
not inspect the rejected Flash branch or create any V7 content.

Create and commit only
`orchestration/agent_inbox/antigravity/lc4v7-source-binding-review.md`.
Record exact reviewed head, tests, findings, and finish with exactly
`DECISION: pass` or `DECISION: revision_required`. Do not edit source, author
content, push protected refs, accept the sprint, or move the baton.
