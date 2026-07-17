# Synthetic Silver V2 Anchor Contract — Pre-Content Review Packet

Date: 2026-07-17

## Assignment

Independently veto or accept the exact Sol-owned v2 contract at source head
`232b191c`. This review occurs before any v2 anchor or dialogue
content exists. Do not generate content, inherit Sol's decision, or modify the
contract.

## Workspace and ownership

- worktree: `C:\Users\sarashera\EMR4-worktrees\synthetic-silver-v2-precontent-review`
- branch: `codex/review-synthetic-silver-v2-precontent`
- source branch: `codex/synthetic-silver-v2`
- source head under review: `232b191c`
- owned file:
  `orchestration/agent_inbox/antigravity/synthetic-silver-v2-precontent-review.md`

Write and commit only the owned review file. Do not push any ref. You have no
anchor-authorship, corpus-admission, product-repair, integration, handoff, or
protected-ref authority.

## Exact review surface

- `docs/bernie-synthetic-silver-v2-anchor-contract.md`
- `AGENTS.md`, only the Current Baton, synthetic-v2 authorization paragraph,
  protected-evidence boundary, and user-decision boundary
- the historical v1 disposition stated in
  `docs/bernie-synthetic-silver-coherence-audit-closeout.md`

Do not inspect any protected V1-V10 fixture, support module, manifest, seal,
receipt, per-case report, or path. Do not run broad discovery commands that
could enumerate protected paths. No v2 seed or candidate content should exist.

## Required independent decisions

1. Confirm the fresh 96-anchor/192-candidate matrix is exactly balanced: two
   anchors per each of six actions by eight dialogue forms, yielding 16 anchors
   per action and 12 per form.
2. Decide whether clarification is fail-closed and coherent: explicit
   ambiguity, a non-null question and choices, only
   `request_clarification`, `clarification_required`, and no deltas.
3. Decide whether true whole-action reversal is coherent: initial intended
   action remains extractable, the final turn explicitly withdraws it, outcome
   is null, mutation/audit deltas are empty, and only bounded read lookup may
   remain.
4. Confirm correction, ellipsis, anaphora, repetition, and session restart
   cannot receive hidden values from the anchor or scorer.
5. Confirm anchor coherence and admission are independent of current parser
   output and distinct from later product robustness.
6. Confirm the successive-refinement stop conditions do not silently authorize
   clarification-policy, replay, scorer, certification, provider/runtime,
   API/database/UI, confirmation, deployment, release, or write changes.
7. Confirm v1 remains immutable historical evidence and no quarantined row is
   relabelled or rewritten.
8. Confirm protected holdouts, historical diary, external corpora, and the
   appointment-call corpus remain inaccessible.
9. Verify no v2 content file exists at the reviewed head and `git diff --check`
   passes.

## Durable decision format

End with exactly:

```text
DECISION: pass|revision_required
SOURCE_HEAD: 232b191c
PRE_CONTENT: true
ANCHOR_TARGET: 96
CANDIDATE_TARGET: 192
CLARIFICATION_COHERENT: true|false
REVERSAL_COHERENT: true|false
STANDING_BOUNDARY_CLOSED: true|false
PROTECTED_ACCESS: false
```

If `revision_required`, list each exact conceptual or mechanical blocker above
the decision block. Do not repair it.
