# Codex Synthetic Noise Generation Packet

Date: 2026-07-17

## Binding

- Worktree: `C:\Users\sarashera\EMR4-worktrees\synthetic-noise-codex`
- Branch: `codex/synthetic-noise-codex-worker`
- Source head: `76e2516e63bd9f214e4cbad7bd98a2e85b0ec5aa`
- Model: native Codex worker
- Role: bounded Silver dialogue generator only
- Integration and acceptance owner: GPT Sol

Read completely:

- `AGENTS.md`;
- `docs/bernie-synthetic-receptionist-silver-contract.md`;
- `tests/fixtures/bernie_synthetic_noise/semantic_seeds.json`; and
- `app/services/bernie/synthetic_noise_corpus.py`.

Do not read or search any protected holdout artifact. Do not use broad file
enumeration. The seed manifest is the complete generation input.

## Task

Create a deterministic Codex-specific generator and exactly 192 JSONL
candidates: two for each of the 96 semantic seeds. Variant 1 is medium noise
with at least two allowlisted operations; variant 2 is high noise with at least
three. Follow the candidate schema and every semantic/noise invariant in the
contract.

Use the frozen seed hash and semantic contract as authority. Generate dialogue
only. Do not change, infer, repair, or duplicate an oracle. Seek a distinct
style from template-heavy prose: concise staff shorthand, realistic false
starts, locally resolvable references, and controlled formatting mistakes.

## Owned files

- `app/services/bernie/synthetic_noise_codex.py`
- `tests/fixtures/bernie_synthetic_noise/candidates_codex.jsonl`
- `orchestration/agent_inbox/codex/synthetic-noise-generation-completion.md`

Do not modify any other file. Commit owned files on the named disposable
branch. Do not push.

## Mechanical checks

Your generator must fail closed and check:

- exact generator identity `openai/codex/synthetic-noise-codex`;
- 192 records and exactly two per seed;
- exact source seed IDs and hashes;
- unique candidate IDs and full dialogue payloads;
- medium/high level and minimum operation counts;
- allowlisted noise operations only;
- exact evidence-span coordinates and every required key;
- `semantic_change=none`, `silver/pending`, and all authority fields false;
- no contact identifiers, clinical details, external-corpus content, or Bernie
  replies; and
- stable canonical SHA-256 over the completed JSONL records.

Run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_synthetic_noise_seed_manifest.py --check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile app\services\bernie\synthetic_noise_codex.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe app\services\bernie\synthetic_noise_codex.py --check
git diff --check
```

## Forbidden surfaces

Protected V1-V10 material; historical diary data; Kaggle or other external
corpora; provider/runtime prompts or adapters; routes; APIs; GraphQL; database;
UI; parser/policy changes; confirmation; write authority; deployment; release;
Gold promotion; certification; and any file outside the owned set.

## Durable decision

The completion file must end with:

```text
DECISION: pass
SOURCE_HEAD: 76e2516e63bd9f214e4cbad7bd98a2e85b0ec5aa
CANDIDATE_COUNT: 192
SEED_COUNT: 96
CANDIDATE_SHA256: sha256:<64hex>
PROTECTED_ACCESS: false
EXTERNAL_CORPUS_ACCESS: false
```

Use `DECISION: revision_required` and name exact blockers if any requirement
does not pass. Do not self-certify semantic acceptance; `pass` means only
your bounded generation contract and mechanical checks passed.
