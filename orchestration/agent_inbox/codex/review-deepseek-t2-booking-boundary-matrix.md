# Review: DeepSeek T2.1 - Booking Boundary and Invariant Matrix

**Worker:** DeepSeek Flash via Deep Code (interactive TUI)
**Model:** `deepseek-v4-flash` / high
**Date:** 2026-07-13
**Candidate commit:** `1114c1443fa13fb85db6a5cf8805bd4052d75807`
**Branch:** `deepcode/t2-booking-boundary-matrix`

---

## Files Changed

| File | Change |
|---|---|
| `tests/test_bernie_booking_boundary_matrix.py` | **Created** — 583 lines, 15 new tests |

Zero files in `app/` were edited. All other test files are untouched.

---

## Coverage Added

### 1. Half-open Interval Edges (5 tests)

The booking classifier uses half-open `[earliest, latest)` windows for
exact-duplicate detection and `[existing_start, existing_end)` interval overlap
for collision detection. The following edge conditions were NOT covered by
existing tests:

| Test | Condition | Expected |
|---|---|---|
| `test_end_equals_start_not_overlap` | Existing 09:00–09:15, request [09:15, 10:00) | `same_day_distinct` (NOT overlapping — existing_end == req_start) |
| `test_zero_width_window_no_exact` | Request [10:00, 10:00), existing 09:00 | `same_day_distinct` (empty window cannot contain any start) |
| `test_one_minute_intersection` | Existing 09:00–09:30, request [09:29, 10:00) | `overlapping_same_patient` (1-minute overlap at 09:29–09:30) |
| `test_containment_exact_duplicate` | Existing 10:00–10:15 inside [09:00, 11:00), matching type/duration | `exact_duplicate` (existing start inside wider window) |
| `test_duration_extension_overlap` | Existing 09:45–10:15 inside [09:00, 10:00) but extends beyond | `overlapping_same_patient` (start inside, duration mismatch prevents exact) |

### 2. Date and Active/Terminal-Status Boundaries (3 tests)

| Test | Condition | Expected |
|---|---|---|
| `test_adjacent_date_returns_none` | Existing on BOUNDARY_DATE, request on BOUNDARY_OTHER_DATE | `none` |
| `test_weekend_gap_returns_none` | Existing on Friday, request on Monday | `none` |
| `test_booked_on_boundary_adjacent_date_no_collision` | Existing on both dates, request on BOUNDARY_DATE only | `same_day_distinct` (cross-date appointment ignored) |

### 3. Stable Result Under Insertion/Query Ordering (3 tests)

| Test | Condition | Expected |
|---|---|---|
| `test_two_appointments_insertion_order_invariant` | Appointments at 14:00 then 09:00 (reverse time order), request [10:00, 11:00) | `same_day_distinct` |
| `test_two_appointments_overlap_stable` | 10:00 then 09:00 (30min), request [09:15, 10:00) | `overlapping_same_patient` (09:00 overlaps window) |
| `test_multiple_same_day_distinct_stable` | Three appointments (16:00, 09:00, 12:00 inserted non-chronologically) | `same_day_distinct` regardless of DB return order |

### 4. Classifier-Level Read-Only Proof (2 tests)

| Test | Condition | Expected |
|---|---|---|
| `test_classifier_does_not_write_appointments` | Pre/post appointment and audit counts after classifier call | Zero new rows |
| `test_classifier_reads_without_flush` | Commit seed, run classifier, rollback — counts stable | `count_after == count_before` |

### 5. Route Candidates Within Normalized Bounds (2 tests)

| Test | Condition | Expected |
|---|---|---|
| `test_non_duplicate_candidates_respect_latest_edge` | Request [09:00, 09:30) | 09:30 excluded by half-open, 09:00 and 09:15 present |
| `test_non_duplicate_candidates_respect_earliest_edge` | Request [09:15, 10:00) | 09:00 excluded, 09:15 present |

---

## Cross-Reference: Coverage Intentionally Not Duplicated

The following invariants are already thoroughly tested in
`tests/test_bernie_booking_classifier.py` and
`tests/test_slot_search_proposal.py`. They are NOT replicated here:

**Booking classification values:**
- `test_classification_enum_values` — all four values present
- `test_classification_evidence_frozen` — Evidence is immutable

**None/same-day-distinct return:**
- `test_no_existing_appointments_returns_none` — empty DB
- `test_no_appointments_on_requested_date_returns_none` — other date
- `test_different_patient_no_collision` — different patient
- `test_same_day_distinct_before_window` — existing before window
- `test_same_day_distinct_after_window` — existing after window
- `test_same_day_distinct_no_time_bounds` — no time bounds

**Terminal-status exclusion:**
- `test_terminal_status_excluded` — Completed/Cancelled/NoShow/DNA
- `test_non_terminal_status_included` — Booked is active

**Practice isolation:**
- `test_practice_isolation` — practice_b does not interfere

**Source-appointment exclusion:**
- `test_source_appointment_excluded` — self-exclusion
- `test_source_exclusion_other_appointment_still_detected` — other collisions persist

**Temporal evidence exact-duplicate rules:**
- `test_no_temporal_evidence_not_exact` — no earliest+latest → not exact
- `test_latest_only_not_exact` — latest without earliest → not exact
- `test_exact_duplicate_earliest_only` — earliest-only exact match
- `test_earliest_only_not_matching_not_exact` — earliest-only no match

**Exact-duplicate conditions:**
- `test_exact_duplicate_both_bounds` — start inside [earliest, latest)
- `test_exact_duplicate_start_equal_earliest` — start == earliest
- `test_exact_duplicate_start_equal_latest_not_included` — start == latest excluded
- `test_exact_duplicate_with_matching_type` — type match contributors
- `test_type_mismatch_not_exact` — type mismatch prevents
- `test_duration_mismatch_not_exact` — duration mismatch prevents
- `test_different_practitioner_not_exact` — different practitioner prevents

**Overlap detection:**
- `test_overlapping_same_practitioner` — same practitioner overlap
- `test_overlapping_different_practitioner` — different practitioner overlap
- `test_30min_booking_removes_two_slots` — multi-slot conflict
- `test_cancelled_appointment_does_not_remove_candidate` — Cancelled non-blocking
- `test_noshow_does_not_remove_candidate` — NoShow non-blocking
- `test_dna_does_not_remove_candidate` — DNA non-blocking

**Route-level behavior:**
- `test_exact_duplicate_route_response` — existing_booking_found result shape
- `test_exact_duplicate_no_write` — no appt/audit rows created
- `test_non_duplicate_returns_candidates` — candidate_selection_required
- `test_golden_regression_duplicate_detected` — 15:00-16:30 golden case
- `test_slot_search_writes_no_appointments_and_no_audit_rows` — non-mutating proof

**D6/D8 source-exclusion:**
- `test_d6_has_existing_booking_on_requested_day`
- `test_d8_patient_has_active_booking_on_date`
- `test_d8_source_exclusion_preserved`

**Slot-search validation:**
- `test_unauthenticated_is_401` / `test_cross_practice_practitioner_is_404`
- `test_candidates_earliest_first` / `test_candidate_start_times_are_tz_aware`
- `test_limit_caps_candidate_count` / `test_break_overlap_surfaces_warning`
- `test_missing_duration_and_no_type_returns_blocked`
- `test_appointment_type_default_duration_used_when_no_explicit_duration`
- `test_date_to_before_date_from_is_422` / `test_date_range_exceeding_14_days_is_422`
- `test_earliest_time_filters_candidates` / `test_latest_time_filters_candidates`
- `test_no_schedule_day_yields_no_candidates_for_that_day`
- `test_no_schedule_single_day_returns_diagnostic_warning`
- `test_conflict_at_other_location_does_not_block_candidates`

---

## Test Results

```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_booking_boundary_matrix.py tests/test_bernie_booking_classifier.py tests/test_slot_search_proposal.py -q --tb=short
```

**64 passed** (15 new + 49 existing), **0 failed**, **0 errors**, **0 skipped**.

```
git diff --check
```
**Clean** — no whitespace errors detected.

---

## Boundaries and Findings

1. **No product defects exposed.** All 15 new tests pass against the current
   production classifier and route code. The classifier's half-open interval
   semantics are consistent across exact-duplicate detection, overlap detection,
   and candidate generation.

2. **The `_times_overlap` function is correct for all edge cases tested.**
   The condition `existing_start_m < req_end_m and existing_end_m > req_start_m`
   correctly handles adjacent intervals (end equals start → no overlap),
   zero-width windows (same start/end → empty), and one-minute intersections.

3. **Insertion order is stable.** Because the classifier scans all matching
   appointments and returns evidence from the first overlapping/exact match
   (not the first DB row), the classification value itself is deterministic
   even when multiple appointments exist. The evidence `start_time_local`
   may vary based on DB row order, but the `classification` enum is stable.

4. **Read-only invariant confirmed at the classifier level.** Before this
   module, read-only behavior was only tested at the route level. The new
   `test_classifier_does_not_write_appointments` and
   `test_classifier_reads_without_flush` prove no DB mutations at the
   service layer.

5. **Route candidates correctly use half-open windows.** The new
   `test_non_duplicate_candidates_respect_latest_edge` confirms that
   `09:30` is excluded from `[09:00, 09:30)` at the route level.

6. **No `app/` changes were needed.** All identified gaps were test-coverage
   gaps only. Production code is stable.

---

## Sprint-Engine State

`sprint engine continuing` — no pause required. The T2.1 boundary matrix is
complete for the booking classifier. The next recommended step is T2.2
(deterministic receptionist copy and alternative-action integration), building
on the same stateful scenario laboratory foundation.

STATUS: complete
