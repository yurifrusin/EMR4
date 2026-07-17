# Gemini Synthetic Noise Recovery Review Packet

Date: 2026-07-17

## Binding

- Worktree: `C:\Users\sarashera\EMR4-worktrees\synthetic-noise-gemini-review`
- Branch: `codex/synthetic-noise-gemini-review`
- Exact source head: `0688818f3681da22a5586ce03f6a996eaa1f93e6`
- Candidate path: `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl`
- Canonical candidate hash: `sha256:a7d2292adb4aca76c86fcdd019dc44d1708d9723a9b282db181327af889039bf`
- Model: Gemini 3.5 Flash through a fresh Antigravity project
- Role: independent exact-candidate Silver reviewer and veto
- Acceptance/integration owner: GPT Sol

Read completely and only as needed:

- `AGENTS.md`;
- `docs/bernie-synthetic-receptionist-silver-contract.md`;
- `docs/bernie-synthetic-receptionist-silver-wave-1-rejection.md`;
- `orchestration/agent_inbox/codex/synthetic-noise-sol-recovery-amendment.md`;
- `tests/fixtures/bernie_synthetic_noise/semantic_seeds.json`;
- the exact candidate file above; and
- `app/services/bernie/synthetic_noise_corpus.py`.

Do not read, list, search, hash, or infer any protected V1-V10 artifact. Do
not use external corpora. The semantic seed manifest and candidate JSONL are
the complete review evidence.

## Task

Independently review all 192 candidates against their named semantic seeds.
First verify the exact source head and candidate hash with the central
validator. Then assess each record for:

- preservation of intended action, patient/practitioner state, temporal
  meaning, duration, status, and dialogue form;
- natural compact Australian receptionist-to-Bernie staff instruction, not
  patient dialogue or generic assistant prose;
- plausible medium/high noise without corruption or accidental clinical data;
- exact evidence spans and no invented resolution of ambiguous/omitted slots;
- meaningful distinction between the two variants for a seed;
- no Bernie reply, oracle mutation, authority grant, or real-world provenance
  claim.

Classify every candidate as `accept`, `quarantine`, or `reject`. A mechanical
pass is necessary but not sufficient. Report every quarantined/rejected ID
with a concise reason; summarize repeated accepted patterns rather than
listing 192 accepted IDs. A single semantic contradiction is a veto and
requires `revision_required`.

Run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_synthetic_noise_candidates.py --input tests\fixtures\bernie_synthetic_noise\candidates_sol_recovery.jsonl --provider-id openai --model-id gpt-sol-recovery --lane-id synthetic-noise-sol-recovery --candidate-prefix sol
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_synthetic_noise_corpus.py tests\test_bernie_synthetic_noise_sol_recovery.py -q
git diff --check
```

## Owned file

- `orchestration/agent_inbox/antigravity/synthetic-noise-recovery-review.md`

Modify no other file. Commit the review on the disposable branch. Do not
push and do not edit the candidates.

## Forbidden surfaces

Protected V1-V10 material; historical diary data; Kaggle or any external
corpus; provider/runtime product calls; routes; APIs; GraphQL; database; UI;
parser/policy changes; confirmation; write authority; deployment; release;
Gold promotion; certification; and every file outside the owned review.

End the review with exactly:

```text
DECISION: pass|revision_required
SOURCE_HEAD: 0688818f3681da22a5586ce03f6a996eaa1f93e6
CANDIDATE_SHA256: sha256:a7d2292adb4aca76c86fcdd019dc44d1708d9723a9b282db181327af889039bf
REVIEWED: 192
ACCEPT: <count>
QUARANTINE: <count>
REJECT: <count>
PROTECTED_ACCESS: false
EXTERNAL_CORPUS_ACCESS: false
```
