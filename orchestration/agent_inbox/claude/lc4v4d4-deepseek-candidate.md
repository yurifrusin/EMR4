# LC4V4D4 DeepSeek Flash Candidate — Versioned Composed Integration

## Worker Identity

- **Worker**: DeepSeek V4 Flash/high through Claude Code `--bare`
- **Worktree**: `C:\Users\sarashera\EMR4-worktrees\lc4v4d4-dw1`
- **Branch**: `claude/lc4v4d4-composed-integration`
- **Sources**: `fbcd1c63f7dbbafce8ef96f71a5cdab22b15735e`

## Owned Files

| Path | Action |
|---|---|
| `app/services/bernie/composed_corpus_evaluator.py` | Narrow additive edit |
| `app/services/bernie/lc4v4d4_composed_evidence.py` | Created |
| `tests/test_bernie_lc4v4d4_composed_integration.py` | Created |
| `docs/bernie-lc4v4d4-composed-integration.json` | Created |
| `docs/bernie-lc4v4d4-composed-integration.md` | Created |
| `orchestration/agent_inbox/claude/lc4v4d4-deepseek-candidate.md` | This receipt |

## Commands Executed

```bash
cd C:\Users\sarashera\EMR4-worktrees\lc4v4d4-dw1
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_lc4v4d4_composed_integration.py -v
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_lc4v4d3_policy_resolution.py -v
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_composed_corpus_evaluator.py -v
git diff --check
```

## Results Summary

- **D4 evidence procedure**: all 12/12 gates pass → `candidate_complete`
- **Legacy 60-probe baseline hash**: exact `sha256:665851ffe055efb40f2ba1e43291d6b945c4764b4f441837781d4fc964d6ff27`
- **D2 report hash**: exact `sha256:3220ac943659ae1449c5c285144b1fa980f659668a705ca7aef98f0aea6d317a`
- **D3 report hash**: exact `sha256:94b751aea657696329c6b6d394253aef3ef0dbe82316e7725efc1c16fac523a8`
- **D3 selection hash**: exact `sha256:d3c6618cb586f5dc43824ec7a6e9e33957fee587a45c19f89e5a4bb425006e2a`
- **D4 report hash**: `sha256:7a5c09f5b8859bc1a3fe7c5bbc7530ac93ef7084eaa9e2252da1b26b43eb19cc`
- **Category counts**: 20/20 passes (5 clarification_alternatives, 2 corrected_patient, 1 omitted_practitioner, 2 corrected_practitioner, 5 diary_state_join, 5 unsafe_bypass)
- **Variance**: zero (identical fingerprints on two runs)
- **Legacy runner equivalence**: all 60 probes match direct interpret/replay
- **Utterance semantics**: all 20 Option A observations preserve pure utterance fields
- **Forbidden mutation**: none

## Implementation Details

### `PolicyVersion` enum (in `composed_corpus_evaluator.py`)
- Two explicit values: `LEGACY` (default) and `OPTION_A`
- `default()` static method returns `LEGACY`

### `VersionedComposedResult` dataclass
- `policy_version`: the PolicyVersion used
- `interpretation`: `InterpretationObservation` (utterance-derived fields)
- `replay`: `ReplayObservation` (built from policy for Option A)
- `diary_relation`: separate diary comparison relation
- `conflicting_fields`: tuple of conflicting field names
- `resolved_patient`, `resolved_practitioner`, `resolved_practitioner_id`

### `compose_versioned()` function
- **LEGACY branch**: delegates to `deterministic_interpret` / `deterministic_replay` exactly
- **OPTION_A branch**: runs `extract_semantics` once, calls `resolve_policy`, builds typed interpretation/replay preserving utterance fields and carrying policy fields
- **Unsupported version**: raises `ValueError`

### D4 evidence module
- 12-gate fail-closed procedure
- 20-case exact-20 overlay oracle using the same category structure as D3
- Legacy 60-probe baseline hash computation
- D2/D3 hash validation
- Deterministic JSON and Markdown reports

## Boundary Compliance

| Boundary | Status |
|---|---|
| Holdouts v1-v4 sealed | ✅ Not accessed |
| T3.1-T3.4 blocked | ✅ Not modified |
| Utterance parser unchanged | ✅ Not modified |
| Generic scorer unchanged | ✅ Not modified |
| D3 resolver unchanged | ✅ Not modified |
| No scenario-ID, expected-field, or scorer branch | ✅ Confirmed |
| No product/write surface | ✅ Not touched |

## Limitations

- D4 is development-only evidence; not a certification run
- The evidence overlay maps only the exact 20 accepted D3 development IDs
- Six D1 cases remain incompatible with Option A and are recorded as versioned-overlay differences

---

**DECISION: candidate_complete**
