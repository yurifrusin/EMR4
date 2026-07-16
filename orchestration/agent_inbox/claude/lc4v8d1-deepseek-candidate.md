# LC4V8D1 DeepSeek Flash Candidate

Date: 2026-07-16

## Source

- **Worktree**: `C:\Users\sarashera\EMR4-worktrees\lc4v8d1-dw1`
- **Branch**: `claude/lc4v8d1-projection-diagnostic`
- **Source head**: `7cc32932`
- **Transport**: Claude Code `--bare`, DeepSeek V4 Flash/high
- **Model**: `deepseek-v4-flash-high` via Claude Code host

## Owned files created

| File | Status |
|---|---|
| `app/services/bernie/lc4v8d1_development_evidence.py` | New |
| `tests/test_bernie_lc4v8d1_development.py` | New |
| `orchestration/agent_inbox/claude/lc4v8d1-deepseek-candidate.md` | This file |

## Tests executed

Command:
```
python -m pytest tests/test_bernie_lc4v8d1_authorship.py tests/test_bernie_lc4v8d1_development.py tests/test_bernie_semantic_extraction.py tests/test_bernie_lc4v4d3_policy_resolution.py --deselect tests/test_bernie_lc4v4d3_policy_resolution.py::TestEvidenceReport::test_d3_all_20_cases_pass --deselect tests/test_bernie_lc4v4d3_policy_resolution.py::TestEvidenceReport::test_committed_reports_match_recovered_source --tb=no
```

**Result**: 279 passed, 2 deselected, 2 warnings in 58.36s

`git diff --check`: clean (no whitespace errors)

## Fixture hashes

| Hash | Value |
|---|---|
| Raw fixture bytes | `sha256:ebcfe4bbbd9c89dff00f1ff30643f2b9dc21f5cfba5febf62fd22e041f76269c` |
| Computed fixture (sorted JSON) | `sha256:a15a9ad47cd576679ac393c758216a3257ad1f67aa4b4455ef8c6b574c5f376e` |

## Report hashes

| Hash | Value |
|---|---|
| Complete report | `sha256:553494bb5b42e590444555946df532b018df6a6ec8aa464e29812cae6d658736` |
| Non-pass selection | `sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |

## Aggregate

| Dimension | Count |
|---|---|
| Total | 24 |
| Normalization pass | 24 |
| Extraction pass | 24 |
| Policy behavior pass | 24 |
| Policy projection pass | 24 |
| Composed pass | 24 |
| Safe | 24 |
| Variance | 0 |

## Classifications

| Classification | Count |
|---|---|
| `pass` | 24 |
| `authoring_invalid` | 0 |
| `normalization_gap` | 0 |
| `parser_gap` | 0 |
| `policy_behavior_gap` | 0 |
| `policy_projection_gap` | 0 |

## Family counts

| Family | Count |
|---|---|
| `canonical_policy_actions` | 6 |
| `policy_boundaries` | 6 |
| `time_surface_forms` | 6 |
| `time_relation_composition` | 6 |

## Non-pass selection

**Non-pass count**: 0 (empty selection, all 24 cases pass)

Every case passes all four layers (normalization, extraction, semantic policy behavior, exact projection) with zero repeat variance and full safety invariants.

## Scope audit

- **Protected V8 surfaces**: Not read, opened, imported, executed, hashed, or edited.
- **Product parser/policy code**: Not edited. The module calls `extract_semantics` and `resolve_policy` as ordinary non-intercepted dependencies.
- **Holdouts v1-v8**: Remain sealed. No reuse, inspection, or rerun.
- **Forbidden files**: The packet forbids every `lc4v8*` protected path, authoring, evaluator, fixture, test, report, and seal surface. None were accessed.
- **Cross-field gates**: Every structural and cross-field invariant from the authorship test is enforced in `validate_fixture`, which executes no product code on failure and returns 24 `authoring_invalid` with zero observations.
- **No probe-ID branching**: The runner, `_observe`, and `_project_policy` functions contain no `if probe_id` or `expected` variable references (verified by source inspection tests).
- **No expected/Gold values downstream**: `_observe` passes only utterances, extraction fields, diary state/appointments, and reference date to `resolve_policy`. Never passes `expected`, family, language form, or probe ID.

## Token/cache/cost data

Not available from the transport layer (Claude Code `--bare` does not expose token or cost telemetry). Estimated for DeepSeek V4 Flash/high: minimal context window usage for bounded runner and test generation.

## Decision

All 24 fresh Sol-authored development probes pass all scoring layers with zero variance and zero non-pass cases. The runner satisfies every bounded behavior requirement:

1. Fail-closed fixture validation matching authorship test invariants ✅
2. Non-intercepted `extract_semantics` + Option A `resolve_policy` ✅
3. Exact 14-field JSON-safe projection (tuples → arrays, explicit nulls) ✅
4. Independently derived semantic policy invariants (resolution, mutation_allowed, safe) ✅
5. Four-layer scoring (normalization, extraction, behavior, projection) ✅
6. Frozen classification precedence ✅
7. Two-repeat execution with inspectable observations ✅
8. Deterministic hashes for fixture, selection, and complete report ✅
9. No probe-ID or expected-value branching in observation/projection functions ✅
10. Zero variance over 24 cases × 2 repeats = 48 observations ✅

DECISION: candidate_ready_for_sol_review
