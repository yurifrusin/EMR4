# LC1 DW3 Final-Diff Coverage Review

**Reviewer:** DeepSeek Flash (Deep Code transport)
**Previous reviewed baseline:** `7143ee2f`
**Final reviewed baseline:** `e830af45`
**Date:** 2026-07-14

---

## Test Results Summary

| Test Suite | Result |
|---|---|
| `tests/test_bernie_slot_normalizer.py` | **38/38 PASS** |
| `tests/test_bernie_scenario_spec.py` | **51/51 PASS** |
| `tests/test_bernie_booking_classifier.py::test_tomorrow_at_3pm_interpret_then_duplicate_has_no_second_write` | **1/1 PASS** |
| `git diff --check` | **Clean** (no whitespace errors) |

---

## Check 1: Invalid `temporal_relation` labels block normalization and cannot fall back to legacy exact-duplicate authority

**Evidence:**

- `app/services/bernie_slot_normalizer.py` (lines 178–181): invalid `temporal_relation` values now use `blocks.append()` with severity `"blocked"` instead of the previous `warnings.append()` with `"warning"`. The constraint is set to `None`, so the result is `safe=False` and the normalizer never emits a fallback constraint.
- `tests/test_bernie_slot_normalizer.py` line 425 — `test_invalid_temporal_relation_fails_closed()`: calls `normalize_slot_search_command` with `temporal_relation="approximately_exact"` and asserts:
  - `result.safe is False`
  - `result.constraint is None`
  - `[block.code for block in result.blocks] == ["invalid_temporal_relation"]`
- **Verdict: PASS** — invalid relations fail normalization closed; no fallback to legacy exact-duplicate authority.

## Check 2: `ScenarioSourceSpan` stores turn index plus exact start/end coordinates and validation proves every span slices the original utterance

**Evidence:**

- `app/services/bernie/scenario_spec.py` lines 30–44 — new `ScenarioSourceSpan(BaseModel)`:
  - `turn_index: int` (ge=0), `start: int` (ge=0), `end: int` (gt=0), `text: str` (min_length=1)
  - `model_config = ConfigDict(extra="forbid", frozen=True)`
  - `@model_validator(mode="after")` method `validate_order` raises `ValueError` when `end <= start`
- `ReceptionScenarioSpec.source_spans` type changed from `dict[str, str]` to `dict[str, list[ScenarioSourceSpan]]` (line 75)
- Validator (lines 175–187): for each span, checks `span.end > len(original)` and `original[span.start:span.end] != span.text`, raising `ValueError` with `"does not match original text"` on mismatch
- `tests/test_bernie_scenario_spec.py` line 252 — `test_rejects_source_span_that_does_not_slice_original_turn()`: mutates `start` to `0` and asserts `ValidationError` matching `"does not match original text"`
- All three Gold fixtures updated to use `list[ScenarioSourceSpan]` structure with exact coordinates
- **Verdict: PASS** — span stores precise turn/start/end coordinates; validation proves every span slices the correct original utterance.

## Check 3: The three Gold seed fixtures still validate and reference committed T1/T2 scenario IDs

**Evidence:**

- Three Gold fixtures committed in `tests/fixtures/bernie_scenario_spec/`:
  1. `booking_create_then_exact_duplicate.json` — `scenario_id: "booking_create_then_exact_duplicate"`, `provenance: "gold"`, `adjudication: "adjudicated"`
  2. `booking_overlap_not_exact_duplicate.json` — `scenario_id: "booking_overlap_not_exact_duplicate"`, `provenance: "gold"`, `adjudication: "adjudicated"`
  3. `interpret_clarify_temporal_bounds.json` — `scenario_id: "interpret_time_window_date_change_preserves_upper"`, `provenance: "gold"`, `adjudication: "adjudicated"`
- `tests/test_bernie_scenario_spec.py` `TestSeedFixtureValidation` class:
  - `test_parses_valid_spec` (line 274): parametrized over all three fixtures, validates `spec.provenance == "gold"` and `spec.scenario_id is not None`
  - `test_all_fixtures_reference_committed_t1_t2_scenario_ids` (line 291): parses `id:` lines from `SOURCE_SCENARIO_DIR/*.yaml`, asserts each fixture's `scenario_id` is in the set
  - `test_all_fixtures_have_independent_adjudication` (line 286): all three assert `data["adjudication"] == "adjudicated"`
- **Verdict: PASS** — all three Gold fixtures parse, validate, and reference committed T1/T2 scenario IDs.

## Check 4: Lossless normalization does not promote invalid clock forms

**Evidence:**

- `app/services/bernie/language_normalization.py` lines 134–138 — three guard clauses in `_detect_time_forms()`:
  - `if minute > 59: continue` — rejects minute values like `:99`
  - `if ampm is not None and not 1 <= hour <= 12: continue` — rejects hours like `29` in 12-hour formats
  - `if ampm is None and not 0 <= hour <= 23: continue` — rejects hours like `29` in 24-hour formats
- All three guards use `continue`, skipping detection entirely — the fragment is never promoted to `time_forms`
- `tests/test_bernie_scenario_spec.py` line 453 — `test_invalid_clock_form_is_not_promoted_to_normalized_time()`: `normalize_utterance("at 29:99")` returns `time_forms == {}`
- **Verdict: PASS** — invalid clock forms are skipped in detection; never promoted to normalized time.

## Check 5: The additive API-spine classification remains accurate and no provider/write/T3.5 authority opened

**Evidence:**

- `docs/bernie-lc1-semantic-foundation.md` adds new "API-spine classification" section documenting that `temporal_relation` is an additive read-model constraint changing no route, auth, practice scope, idempotency key, audit payload, confirmation evidence, or mutation contract
- `app/routers/appointments.py` diff: purely cosmetic refactor extracting `current_earliest`/`current_latest` local variables — no behavioral change, no new route, no new authority
- `app/services/bernie_booking_interpreter.py` diff: removes unused `TemporalExtraction` import (cleanup only)
- No new GraphQL surface, OpenAPI command route, async integration, agent context-frame surface, provider call, diary write, or T3.5 code in the diff
- **Verdict: PASS** — API-spine classification accurate; no provider/write/T3.5 authority opened.

## Check 6: Specified test suites pass and `git diff --check` is clean

**Evidence:**

| Command | Result |
|---|---|
| `git diff 7143ee2f..e830af45 --check` | **No output** (no whitespace errors) |
| `pytest tests/test_bernie_slot_normalizer.py -v` | **38/38 PASS** |
| `pytest tests/test_bernie_scenario_spec.py -v` | **51/51 PASS** |
| `pytest tests/test_bernie_booking_classifier.py::test_tomorrow_at_3pm_interpret_then_duplicate_has_no_second_write -v` | **1/1 PASS** |

- **Verdict: PASS** — all four commands completed successfully with zero failures.

---

## Overall Decision

All six checks pass with deterministic evidence. The integrator amendments in `e830af45` are verified correct relative to baseline `7143ee2f`. No revision required.

DECISION: pass
