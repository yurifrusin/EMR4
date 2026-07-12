# S7 Lane 1: Acceptance Gate Revision 3 — Durable Review Artifact

| Field | Value |
|---|---|
| **Agent** | DeepSeek Flash ("Deep Code") |
| **Resource** | `deepseek-flash-workers` |
| **Model** | `deepseek-v4-flash` |
| **Reasoning** | `high` |
| **Branch** | `deepcode/s7-acceptance-repair` |
| **Role** | Implementation owner, same lane |
| **Packet** | `orchestration/agent_inbox/deepcode/deepcode-s7-contract-audit-v2-repair-revision-3.md` |

## Problem

The first real gate invocation correctly verified artifact, receipt, marker,
branch, HEAD, and candidate ancestry, but rejected authoritative collection
evidence containing two normal pytest per-file lines:

```text
tests/test_ariadne_deepcode_adapter_settings.py: 30
tests/test_ariadne_review_acceptance.py: 52
```

The old implementation treated `{30, 52}` as conflicting (set of size 2) instead
of aggregating to 82. This was a candidate defect in `_parse_pytest_collect()`.

## Fix Applied

**File:** `orchestration_harness/review_acceptance.py`

Rewrote `_parse_pytest_collect()` to implement the aggregation contract:

1. **Per-file `.py: N` lines** — normalised by file path, rejecting conflicting
   duplicate counts for the same path, and summing unique file counts.
2. **Summary `N test(s) collected` lines** — all summary counts must agree.
3. **Both forms present** — summary count must equal the per-file sum.
4. **Only one form present** — use it.
5. **Zero, missing, conflicting duplicate, or summary-versus-sum mismatch** —
   rejected.
6. **Arbitrary colon-number patterns** (e.g. `total: 42`) — rejected (no `.py:`
   match).

The old approach used a flat `set[int]` that could not distinguish per-file
counts from summary counts and treated multiple distinct file counts as a
conflict.

## Tests Added

**File:** `tests/test_ariadne_review_acceptance.py` (6 new tests in
`TestPytestCollection`)

| Test | Input | Expected |
|---|---|---|
| `test_two_files_aggregated_30_plus_52_equals_82` | `30\n52` | accepted, count=82 |
| `test_one_file_139_accepted` | `139` | accepted, count=139 |
| `test_two_files_plus_matching_summary_accepted` | `30\n52\n82 tests collected` | accepted, count=82 |
| `test_two_files_plus_mismatching_summary_rejected` | `30\n52\n80 tests collected` | rejected, count=None |
| `test_duplicate_same_path_same_count_not_double_counted` | `10\n10` | accepted, count=10 |
| `test_duplicate_same_path_different_count_rejected` | `10\n15` | rejected, count=None |

## Verification

### `pytest --collect-only -q`

```text
tests/test_ariadne_deepcode_adapter_settings.py: 30
tests/test_ariadne_review_acceptance.py: 58
```

**Per-file:** 30 + 58 = **88 total** (30 existing adapter + 52 existing acceptance + 6 new = 88)

### `pytest -q --tb=short`

**88 passed** in — all existing tests preserved, all 6 new tests pass.

### `scripts/ariadne_review_acceptance.py --help`

Exits 0 with full usage documentation.

### `git diff --check`

No whitespace errors.

### `git diff --name-only`

Only the two intended files changed:
- `orchestration_harness/review_acceptance.py`
- `tests/test_ariadne_review_acceptance.py`

## Acceptance Criteria Satisfied

- [x] Two files `30 + 52 -> 82` accepted (test `test_two_files_aggregated_30_plus_52_equals_82`)
- [x] One file `139 -> 139` accepted (test `test_one_file_139_accepted`)
- [x] Two files plus matching `82 tests collected` accepted (test `test_two_files_plus_matching_summary_accepted`)
- [x] Two files plus mismatching summary rejected (test `test_two_files_plus_mismatching_summary_rejected`)
- [x] Duplicate same path/same count not double-counted (test `test_duplicate_same_path_same_count_not_double_counted`)
- [x] Duplicate same path/different count rejected (test `test_duplicate_same_path_different_count_rejected`)
- [x] All 82 existing tests preserved (30 adapter + 52 acceptance = 82 pre-existing, now 88 total)
- [x] Every other gate behaviour preserved
- [x] No settings or unrelated files edited

STATUS: complete
