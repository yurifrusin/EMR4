# Gemini Synthetic Noise Recovery Review Round 2 Packet

Date: 2026-07-17

## Binding

- Worktree: `C:\Users\sarashera\EMR4-worktrees\synthetic-noise-gemini-review-2`
- Branch: `codex/synthetic-noise-gemini-review-2`
- Exact source head: `b1380f6aaf6eb21d9af763cfcc8db5130cba138d`
- Candidate: `tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl`
- Canonical hash: `sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`
- Model: Gemini 3.5 Flash through a fresh Antigravity project
- Role: fresh independent exact-candidate Silver reviewer and veto
- Acceptance/integration owner: GPT Sol

Read completely:

- `AGENTS.md`;
- `docs/bernie-synthetic-receptionist-silver-contract.md`;
- `docs/bernie-synthetic-receptionist-silver-review-round-1-disposition.md`;
- `orchestration/agent_inbox/codex/synthetic-noise-sol-recovery-amendment.md`;
- `tests/fixtures/bernie_synthetic_noise/semantic_seeds.json`;
- the exact candidate above; and
- `app/services/bernie/synthetic_noise_corpus.py`.

Do not read, list, search, hash, or infer protected V1-V10 material. Do not use
external corpora. These named ordinary-development artifacts are the complete
review evidence.

## Task

Review all 192 records against their seeds. Verify the exact source and hash,
then independently assess action/entity/temporal/duration/status semantics,
dialogue form, compact Australian receptionist-to-Bernie naturalness, variant
distinction, evidence spans, ambiguity/omission preservation, closed
authority, and the truthfulness of every declared noise operation.

Round one was superseded because 18 records declared `correction` without an
explicit correction surface. Confirm that every remaining `correction`
declaration now has an explicit `Correction—` or `—sorry,` surface and that
removing those 18 labels did not make any medium/high operation count invalid.

Classify every record as `accept`, `quarantine`, or `reject`. List every
quarantine/reject ID and reason. A single semantic contradiction is a veto.

Run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_synthetic_noise_candidates.py --input tests\fixtures\bernie_synthetic_noise\candidates_sol_recovery.jsonl --provider-id openai --model-id gpt-sol-recovery --lane-id synthetic-noise-sol-recovery --candidate-prefix sol
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_synthetic_noise_corpus.py tests\test_bernie_synthetic_noise_sol_recovery.py -q
git diff --check
```

Write only
`orchestration/agent_inbox/antigravity/synthetic-noise-recovery-review-round-2.md`,
commit it on the disposable branch, and do not push. Do not edit candidates.

Forbidden: protected or historical data, external corpora, runtime/provider
product calls, parser/policy/product/API/database/UI changes, write authority,
Gold promotion, certification, deployment, release, and any unowned file.

End exactly:

```text
DECISION: pass|revision_required
SOURCE_HEAD: b1380f6aaf6eb21d9af763cfcc8db5130cba138d
CANDIDATE_SHA256: sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665
REVIEWED: 192
ACCEPT: <count>
QUARANTINE: <count>
REJECT: <count>
PROTECTED_ACCESS: false
EXTERNAL_CORPUS_ACCESS: false
```
