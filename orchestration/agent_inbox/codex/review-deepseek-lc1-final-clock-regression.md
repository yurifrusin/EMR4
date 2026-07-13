# LC1 Final Explicit-Clock Delta Review

**Reviewer:** DeepSeek Flash (Deep Code transport)
**Review scope:** `e830af45..HEAD`
**Focal commit:** `a3c7fa0a` — fix(bernie): preserve explicit clock forms across LC1
**Intervening commit (evidence, not product):** `95537b32` — chore(ariadne): record LC1 final independent review
**Review date:** 2026-07-14
**Worktree:** `lc1-final-review` (disposable, read-only review)

---

## Commands Executed

| # | Command | Result |
|---|---|---|
| 1 | `git diff --check e830af45..HEAD` | Clean — no whitespace errors |
| 2 | `pytest tests/test_bernie_temporal_policy.py tests/test_smoke_bernie_interpreter_script.py tests/bernie_scenarios/test_scenario_replay.py tests/test_bernie_booking_classifier.py tests/test_bernie_scenario_spec.py tests/test_bernie_coverage_lattice.py -q` | **All passed** (39 passed, 1 xfailed) |
| 3 | `pytest tests/test_bernie_shadow_eval_contract.py tests/test_bernie_shadow_corpus.py tests/test_bernie_shadow_runner.py tests/test_bernie_shadow_live_gate.py -q` | **All passed** (7/7) |
| 4 | `pytest tests/bernie_scenarios/test_scenario_replay.py -k "exact_duplicate" -v` | **4/4 passed** |
| 5 | `pytest tests/bernie_scenarios/test_scenario_replay.py -v` | **39 passed, 1 xfailed** (full replay) |
| 6 | Extended edge-case verification via Python REPL | All assertions PASS |

---

## Files Changed by Focal Commit a3c7fa0a

| File | Lines | Nature |
|---|---|---|
| `app/services/diary/temporal.py` | +12 / -7 | 3 regex pattern changes + guard condition in `parse_time_fragment()` |
| `tests/fixtures/bernie_scenarios/booking_create_then_exact_duplicate.yaml` | +4 / -3 | Fixture corrected from interval to exact-point |
| `tests/test_bernie_temporal_policy.py` | +7 / -0 | New regression test for zero-padded clock forms |

**Total product code delta:** 17 lines changed (12 added, 7 removed, 3 files).

---

## Findings by Criterion

### Criterion 1: Preserves 24-hour meaning for explicit zero-padded clock forms ✅ PASS

**Problem:** The old regex `(?:1?[0-9]|2[0-3])` could not match two-digit leading-zero hours like `09:00` because `1?` means "optional 1", not "optional 0 or 1". This caused `09:00` to be parsed as a bare `9:00` through a different branch, then hit the business-hours inference on `9` → `21:00`, which is wrong for a zero-padded 24-hour clock form.

**Fix applied in all 4 regex patterns:**
- `1?[0-9]` → `[01]?[0-9]` in `_NAT_TIME_PAT`, `_BARE_EXPLICIT_TIME_RE`, `_TIME_FRAGMENT_RE`
- This correctly matches `00`–`23` including `00`–`09` which the old pattern missed.

**Additive guard in `parse_time_fragment()`:**
```python
elif (
    not meridiem
    and 1 <= hour <= 11
    and not (len(hour_text) == 2 and (":" in raw or "." in raw))
):
    hour += 12
```
When `hour_text` is 2 characters long (e.g. `"09"`, `"10"`, `"11"`) AND the raw input contains `:` or `.`, the business-hours inference is suppressed. This is the critical guard that keeps `09:00` as 09:00 (24-hour clock) while allowing `3:45` to become 15:45 (business-hours inference for conversational forms).

**Verified edge cases:**
| Input | Expected | Actual | Status |
|---|---|---|---|
| `09:00` | `09:00` | `09:00` | ✅ |
| `10:00` | `10:00` | `10:00` | ✅ |
| `11:00` | `11:00` | `11:00` | ✅ |
| `00:00` | `00:00` | `00:00` | ✅ |
| `08:30` | `08:30` | `08:30` | ✅ |
| `07:45` | `07:45` | `07:45` | ✅ |

### Criterion 2: Retains intended business-hours inference for conversational forms ✅ PASS

Single-digit and non-zero-padded forms without `:`/`.` separator still receive the business-hours inference (bare hours 1–11 → pm):

| Input | Expected | Actual | Status |
|---|---|---|---|
| `3:45` | `15:45` | `15:45` | ✅ |
| `3` | `15:00` | `15:00` | ✅ |
| `5` | `17:00` | `17:00` | ✅ |
| `11` | `23:00` | `23:00` | ✅ |
| `3pm` | `15:00` | `15:00` | ✅ |
| `9am` | `09:00` | `09:00` | ✅ |

Through `extract_natural_time_constraints()`:
| Instruction | Relation | Earliest | Latest | Status |
|---|---|---|---|---|
| `tomorrow at 09:00` | exact | `09:00` | `09:00` | ✅ |
| `tomorrow at 3pm` | exact | `15:00` | `15:00` | ✅ |
| `tomorrow at 3:45` | exact | `15:45` | `15:45` | ✅ |
| `tomorrow after 3 but before 4.30` | interval | `15:00` | `16:30` | ✅ |

### Criterion 3: Corrects the exact-duplicate fixture ✅ PASS

The historical T1 exact-duplicate fixture used an **interval phrase** (`after 3 but before 4.30`), which produces `temporal_relation: interval` and `latest_time != earliest_time`. This is semantically wrong for testing exact-duplicate detection.

**Fix:** The fixture now uses an **exact-point phrase** (`at 3pm`):
- `temporal_relation: exact` is asserted in both interpret turns
- `latest_time` = `15:00:00` (matching `earliest_time` = `15:00:00`)
- Scenario replay passes: 4/4 exact_duplicate tests pass

Verified that `extract_natural_time_constraints("... at 3pm ...")` returns `exact` relation with `earliest='15:00', latest='15:00'`.

### Criterion 4: No regression in explicit temporal relation authority, supervision, or normalization ✅ PASS

- All 7 shadow evaluator tests pass (contract, corpus, runner, live gate), proving no regression in the supervised duplicate route, canonical scenario validation, or normalization.
- All 40 scenario replay tests pass (39 passed, 1 xfailed — xfail is pre-existing).
- `git diff --check` is clean — no whitespace errors in the delta.
- The change is purely to `temporal.py` regex patterns + `parse_time_fragment()` guard logic; no changes to supervision routes, normalization contracts, or scenario validation schemas.

### Criterion 5: T3.1–T3.4 intact, T3.5/provider/write authority closed ✅ PASS

| Check | Status |
|---|---|
| `test_bernie_shadow_live_gate` | All 7/7 pass (provider calls remain blocked) |
| `test_bernie_shadow_runner` | Passes (no live provider wiring added) |
| `test_bernie_shadow_eval_contract` | Passes |
| `test_bernie_shadow_corpus` | Passes |
| Product code diff scope | Only `temporal.py` — no provider, route, DB, or write-authority changes |

The delta adds no provider calls, no route endpoints, no database writes, no T3.5/live-provider surfaces, and no write-authority. All T3.x infrastructure is intact.

---

## Risk Assessment

| Risk | Severity | Assessment |
|---|---|---|
| Zero-padded 24-hour clock regression | None | Correctly preserved; regression test added (`test_zero_padded_clock_forms_keep_24_hour_meaning`) |
| Business-hours inference broken for conversational forms | None | Verified intact for `3:45`, `3`, `5`, `11`, `3pm` |
| Fixture change breaks existing replays | None | All 40 replays pass; exact change is semantically correct |
| Regex match regression for edge hour values | Low | `[01]?[0-9]|2[0-3]` is a strict superset of `1?[0-9]|2[0-3]` — matches all same values plus `00`–`09` |
| Shadow eval / provider boundary compromised | None | No changes to that code; all shadow gate tests pass |

**Residual risk level:** None. The fix is minimal, purely additive in guard logic, and fully covered by existing and new regression tests.

---

## Scope and Authority Assessment

| Aspect | Verdict |
|---|---|
| Assertive scope | `app/services/diary/temporal.py` only — bounded temporal extraction module |
| Write authority | Not touched — no route, DB, provider, or write-path changes |
| Provider access | Not touched — all shadow live gate tests pass |
| Documentation | Not changed |
| Independent review | DW3 prior review artifact (`review-deepseek-lc1-dw3-coverage-review.md`) confirmed at baseline `e830af45` |

---

DECISION: pass
