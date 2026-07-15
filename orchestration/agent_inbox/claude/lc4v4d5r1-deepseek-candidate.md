# LC4V4D5R1 — Exact-four remediation candidate

**Date:** 2026-07-16
**Decision:** `exact_four_remediation_frozen`
**Source commit:** `93575762c13bdf7dd7e0969fa5fb8057de9ce0b9`

---

## Summary

Bounded policy-resolution change in `lc4v4d3_policy_resolution.py`:

1. Excludes `duration` from diary identity/conflict comparison when the
   intended action is `resize` (duration is the mutation target, not a
   conflict).
2. Generates the same deterministic simulated appointment and audit deltas
   for safe `move`, `resize`, `cancel`, and `status_change` actions that
   the legacy replay contract already produces.

Result: all four previously identified adoption blockers are eliminated.

---

## Changed files

- `app/services/bernie/lc4v4d3_policy_resolution.py` — modified
- `app/services/bernie/lc4v4d5r1_remediation_evidence.py` — new
- `tests/test_bernie_lc4v4d5r1_remediation.py` — new
- `orchestration/agent_inbox/claude/lc4v4d5r1-deepseek-candidate.md` — new

---

## Implementation details

### `lc4v4d3_policy_resolution.py`

1. **`compare_all_entities_to_diary`**: Added `exclude_fields: tuple[str, ...]`
   parameter.  Fields named in `exclude_fields` are skipped during entity-vs-diary
   comparison (both conflict detection and duplicate detection).

2. **`resolve_policy` — diary comparison**: When `intended_action == "resize"`,
   passes `exclude_fields=("duration",)` to the diary comparison.  This prevents
   the requested resize duration from being treated as a diary field conflict.

3. **`resolve_policy` — normal action deltas**: For `move`, `resize`, `cancel`,
   and `status_change` in the safe normal-action path, now builds the same
   deterministic appointment delta (`apt-001`, `p-001`, mapped practitioner ID,
   date, start_time, duration_minutes defaulting to 15) and one-count audit
   delta as the legacy replay contract.  Sets `is_simulated_confirmed_write: true`.

All changes are general action-aware — no branching on scenario IDs.

---

## Taxonomy verification

Run all 60 probes × 2 repeats × 2 policy versions = 240 observations:

| Classification | Expected | Actual |
|---|---|---|
| `legacy_equivalent` | 37 | 37 |
| `accepted_d4_versioned_change` | 20 | 20 |
| `expected_versioned_relation` | 3 | 3 |
| `adoption_blocker_*` | 0 | 0 |
| `unexpected_difference` | 0 | 0 |
| `option_a_failed` | 0 | 0 |

### Expected versioned relations (diary_relation-only difference)

1. `lc4v4d1_diary_exact_duplicate_02`
2. `lc4v4d1_safety_cancel_safe_07`
3. `lc4v4d1_safety_status_safe_09`

Selection hash: `sha256:98df6544620da87e12df7df0d8afbdf0ad8e0f0eab16eab85385857158ab3188`

### Repaired probes (now legacy_equivalent)

- `lc4v4d1_safety_move_safe_03`
- `lc4v4d1_safety_resize_safe_05`

### Empty blocker selection

Canonical empty hash: `sha256:4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`

### All 4 unsafe cases still refuse with no deltas

- `lc4v4d1_safety_unsafe_danger_01`
- `lc4v4d1_safety_unsafe_harm_02`
- `lc4v4d1_safety_unsafe_danger_04`
- `lc4v4d1_safety_unsafe_harm_06`

### All 3 authoring-invalid probes remain legacy-equivalent

- `lc4v4d1_entity_duration_corrected_28`
- `lc4v4d1_entity_duration_negated_29`
- `lc4v4d1_dialogue_ellipsis_multi_08`

---

## Test commands

```bash
# Run the full D5R1 taxonomy suite
python -m pytest tests/test_bernie_lc4v4d5r1_remediation.py -v

# Run with verbose output
python -m pytest tests/test_bernie_lc4v4d5r1_remediation.py -v --tb=long

# Run only gate summary
python -m pytest tests/test_bernie_lc4v4d5r1_remediation.py::TestD5R1Gates -v

# Generate evidence report
python -c "from app.services.bernie.lc4v4d5r1_remediation_evidence import run_d5r1_evidence; import json; print(json.dumps(run_d5r1_evidence(), indent=2))"
```

---

## Preserved surfaces

- D4 gates pass unchanged
- Legacy 60-probe baseline hash unchanged
- D2/D3/D4 historical report hashes unchanged
- The four matched unsafe cases still refuse with no deltas
- D4 duration-conflict behavior for non-resize actions intact
- All 20 D4 versioned-change cases byte-for-byte preserved
- Fixtures, parser, extractor, scorer, AGENTS.md — untouched

---

## Boundary

- This is test-harness replay evidence only.  No runtime write, confirmation,
  route, API, database, UI, provider, or product authority is created.
- Holdouts v1-v4 remain sealed.  T3.1-T3.4 remain blocked.
- T3.5, providers, historical diary material, product runtime/default changes,
  routes, APIs, UI, database, deployment, release, and all live/write authority
  remain deferred.

---

**DECISION: pass**
