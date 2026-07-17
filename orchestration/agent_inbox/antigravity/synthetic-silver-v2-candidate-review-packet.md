# Synthetic Silver V2 Exact Candidate — Independent Review Packet

Date: 2026-07-17

## Assignment

Independently review the exact 192-candidate v2 corpus and admission at source
head `e1984ef7`. Review every row against its v2 anchor and form contract. Do
not inherit Sol's admission decision, generate replacements, or modify any
candidate.

## Workspace and ownership

- worktree: `C:\Users\sarashera\EMR4-worktrees\synthetic-silver-v2-candidate-review`
- branch: `codex/review-synthetic-silver-v2-candidates`
- source branch: `codex/synthetic-silver-v2`
- exact source head under review: `e1984ef7`
- owned file:
  `orchestration/agent_inbox/antigravity/synthetic-silver-v2-candidate-review.md`

Write and commit only the owned review file. Do not push. You have no corpus
repair/admission, product repair, acceptance, integration, handoff, or
protected-ref authority.

## Exact review surface

- `docs/bernie-synthetic-silver-v2-anchor-contract.md`
- `app/services/bernie/synthetic_noise_v2.py`
- `app/services/bernie/synthetic_noise_v2_candidates.py`
- `scripts/bernie_synthetic_silver_v2_anchors.py`
- `scripts/bernie_synthetic_silver_v2_candidates.py`
- `tests/fixtures/bernie_synthetic_noise/semantic_seeds_v2.json`
- `tests/fixtures/bernie_synthetic_noise/candidates_sol_v2.jsonl`
- `tests/fixtures/bernie_synthetic_noise/admission_v2.json`
- `tests/test_bernie_synthetic_silver_v2_anchors.py`
- `tests/test_bernie_synthetic_silver_v2_candidates.py`
- `orchestration/agent_inbox/antigravity/synthetic-silver-v2-anchor-review.md`

Protected V1-V10 fixtures/supports/manifests/seals/receipts/per-case reports,
historical diary data, appointment-call data, and external corpora are
forbidden. Do not run broad discovery commands.

## Required independent checks

1. Reproduce 96 exact anchors and 192 unique candidates: two per anchor, 32
   per action, 24 per form, 96 medium and 96 high.
2. Reproduce exact hashes:
   - anchor manifest:
     `sha256:92ad7d9fe2af1efe3f65831ac7e6586d26b6c44b41eabae4be0545740bf3518c`;
   - candidates:
     `sha256:634a7de32356d41232a279c335bcfb5e5a13cf6df884b8abf43e9769b7dc4cf9`;
   - admission:
     `sha256:a630151b011ae09b63ae6daee84aabefb4a4e913c514a13e918d68c570e80cce`.
3. Review every candidate row, not a sample. Verify each evidence span slices
   its utterance and surfaces the anchor's required action, entity, date,
   temporal, duration/status, and dialogue-transition evidence.
4. Confirm clarification candidates remain unresolved and surface the exact
   anchor ambiguity target plus the request to clarify before action.
5. Confirm correction candidates explicitly surface `Dr Patel`, replacement,
   and final `Dr Shera`, and bind only corrected final evidence.
6. Confirm reversal candidates first surface the complete request and finally
   withdraw that whole action with no competing operative request.
7. Confirm ellipsis/anaphora have a same-candidate antecedent; repeated requests
   are exact repeats; session restarts abandon the prior incomplete draft and
   contain one complete fresh request.
8. Confirm declared core noise operations are visibly supported and do not
   introduce a second action, patient, practitioner, time, duration, clinical
   fact, identifier, unsafe bypass, or authority grant.
9. Confirm admission is independent of product parser/replay/scorer output and
   accepts exactly the reviewed canonical hash with zero quarantine/reject.
10. Independently tamper a span, seed hash, authority flag, correction marker,
    reversal marker, repeated turn, and admission binding; each must fail.
11. Run serially:
    `C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_synthetic_silver_v2_anchors.py --check`,
    `C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_synthetic_silver_v2_candidates.py --check`,
    and
    `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_synthetic_silver_v2_candidates.py tests\test_bernie_synthetic_silver_v2_anchors.py tests\test_bernie_synthetic_noise_corpus.py tests\test_agents_handover_archive.py`.
12. Verify `git diff --check`, no product-code change, and
    `PROTECTED_ACCESS: false`.

## Durable decision format

End with exactly:

```text
DECISION: pass|revision_required
SOURCE_HEAD: e1984ef7
ANCHORS: <n>/96
CANDIDATES_REVIEWED: <n>/192
ACCEPT: <n>
QUARANTINE: <n>
REJECT: <n>
CANDIDATE_HASH: sha256:<hex>
ADMISSION_HASH: sha256:<hex>
TESTS: <passed>/<selected>
PROTECTED_ACCESS: false
```

If `revision_required`, list every exact row-level or conceptual blocker above
the decision block. Do not repair it.
