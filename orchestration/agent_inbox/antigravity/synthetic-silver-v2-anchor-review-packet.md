# Synthetic Silver V2 Recovered Anchor — Independent Review Packet

Date: 2026-07-17

## Assignment

Independently review the exact Sol-recovered dialogue-free v2 anchor
implementation at source head `b41d9d56`. Do not inherit the worker's
`candidate_ready` claim or Sol's recovery conclusion. Do not modify the
candidate implementation.

## Workspace and ownership

- worktree: `C:\Users\sarashera\EMR4-worktrees\synthetic-silver-v2-anchor-review`
- branch: `codex/review-synthetic-silver-v2-anchors`
- source branch: `codex/synthetic-silver-v2`
- exact source head under review: `b41d9d56`
- owned file:
  `orchestration/agent_inbox/antigravity/synthetic-silver-v2-anchor-review.md`

Write and commit only the owned review file. Do not push. You have no content
generation, admission, product repair, acceptance, integration, handoff, or
protected-ref authority.

## Exact review surface

- `docs/bernie-synthetic-silver-v2-anchor-contract.md`
- `app/services/bernie/synthetic_noise_v2.py`
- `scripts/bernie_synthetic_silver_v2_anchors.py`
- `tests/test_bernie_synthetic_silver_v2_anchors.py`
- `tests/fixtures/bernie_synthetic_noise/semantic_seeds_v2.json`
- `orchestration/agent_inbox/claude/synthetic-silver-v2-anchor-worker.md`
- `orchestration/agent_inbox/codex/synthetic-silver-v2-anchor-recovery-record.md`

Do not inspect any protected V1-V10 fixture/support/manifest/seal/receipt or
per-case report, historical diary data, appointment-call content, or external
corpus. Do not run broad discovery commands. No v2 candidate dialogue should
exist at this head.

## Required independent checks

1. Reproduce 96 anchors, exactly two per six-action/eight-form cell, 16 per
   action, 12 per form, with unique IDs/hashes and exact fixture regeneration.
2. Reproduce manifest hash
   `sha256:92ad7d9fe2af1efe3f65831ac7e6586d26b6c44b41eabae4be0545740bf3518c`.
3. Verify every source ID/hash/action against ordinary
   `DevelopmentOnlyLoader` and confirm no source dialogue, description, or
   span is exported.
4. Confirm successful mutation anchors preserve exact coherent source
   outcome/tool/appointment-delta/audit-delta shapes, while schedule reads use
   only `find_slots` and no deltas.
5. Confirm clarification anchors freeze explicit ambiguity: non-schedule
   variant 1 patient, variant 2 practitioner; schedule-read variants
   practitioner; all have clarification outcome/tool and no deltas.
6. Confirm every correction freezes an initial `Dr Patel`, explicit
   replacement, final `Dr Shera`, and corrected practitioner/entity semantics.
7. Confirm every reversal has final whole-action withdrawal, negated entity
   state, null outcome, empty deltas, and only the bounded read lookup allowed
   by the contract.
8. Confirm ellipsis/anaphora/repetition/restart form contracts require local
   surfaced evidence without hidden values.
9. Independently test tampering with source hash, ambiguity semantics,
   correction replacement, reversal outcome/deltas/tools, schedule deltas,
   authority, and seed hash; all must fail closed.
10. Confirm the validator does not import or call product interpretation,
    replay, scorer, robustness, protected, historical, or external-data code.
11. Run serially:
    `C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_synthetic_silver_v2_anchors.py --check`
    and
    `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_synthetic_silver_v2_anchors.py tests\test_bernie_synthetic_noise_corpus.py tests\test_agents_handover_archive.py`.
12. Verify `git diff --check`, v1 immutability, no candidate dialogue content,
    and `PROTECTED_ACCESS: false`.

## Durable decision format

End with exactly:

```text
DECISION: pass|revision_required
SOURCE_HEAD: b41d9d56
ANCHORS: <n>/96
ACTION_BALANCE: <n_each>
FORM_BALANCE: <n_each>
MANIFEST_HASH: sha256:<hex>
COHERENCE_ERRORS: <n>
TESTS: <passed>/<selected>
PROTECTED_ACCESS: false
```

If `revision_required`, state every exact blocker above the decision block. Do
not repair it.
