# Review: DeepSeek Flash — T2.2 Exact-Match Precedence Matrix

| Field | Value |
|---|---|
| **Worker** | DeepSeek Flash (deepseek-v4-flash / high) via Deep Code PTY harness |
| **Packet source** | `orchestration/agent_inbox/deepcode/deepcode-flash-t2-exact-precedence-matrix.md` |
| **Candidate commit** | `3654e878` on `deepcode/t2-exact-precedence-matrix` |
| **Changed file** | `tests/test_bernie_booking_precedence_matrix.py` (+373 lines) |
| **Production/DB changes** | None |

---

## Matrix Axes

The generated precedence matrix iterates over all combinations of:

| Axis | Values | Cardinality |
|---|---|---|
| Practitioner | `match`, `mismatch` | 2 |
| Appointment type | `not_supplied`, `match`, `mismatch` | 3 |
| Location | `not_supplied`, `match`, `mismatch` | 3 |
| Duration | `not_supplied`, `match`, `mismatch` | 3 |
| Temporal mode | 9 modes (see below) | 9 |

### Temporal modes

| Mode | Earliest | Latest | Existing start | Exact possible? | Overlaps? |
|---|---|---|---|---|---|
| both_bounds_inside | 08:30 | 10:00 | 09:00 | Yes | Yes |
| both_bounds_equal_earliest | 09:00 | 10:00 | 09:00 | Yes | Yes |
| both_bounds_equal_latest_excluded | 08:00 | 09:00 | 09:00 | No (==latest) | No; endpoints only touch |
| both_bounds_outside_before | 10:00 | 11:00 | 09:00 | No (< earliest) | No |
| both_bounds_outside_after | 07:00 | 08:00 | 09:00 | No (> latest) | No |
| earliest_only_match | 09:00 | None | 09:00 | Yes (exact eq) | Yes |
| earliest_only_no_match | 09:30 | None | 09:00 | No (≠ earliest) | No |
| latest_only | None | 10:00 | 09:00 | No (latest-only) | Yes |
| no_bounds | None | None | 09:00 | No (no evidence) | No |

### Expected outcome derivation (rule table)

```
exact_duplicate:
  practitioner == match
  AND temporal mode ∈ {both_bounds_inside, both_bounds_equal_earliest, earliest_only_match}
  AND (type == not_supplied OR type == match)
  AND (location == not_supplied OR location == match)
  AND (duration == not_supplied OR duration == match)

overlapping_same_patient:
  NOT exact_duplicate
  AND intervals overlap (by half-open intersection)

same_day_distinct:
  NOT exact_duplicate
  AND NOT overlapping
  AND same-day appointment exists
```

---

## Counts

| Metric | Value |
|---|---|
| Total generated combinations | **486** (2 × 3 × 3 × 3 × 9) |
| Stable count guard | `assert len(GENERATED_PRECEDENCE_CASES) == 486` |
| Test nodes | 2 (matrix execution + count guard) |
| Execution time | ~1.3s for the matrix (one query-only node, no DB setup per case) |
| Query-only sessions used | Yes (486 calls to `classify_existing_booking()`, 1 query each) |

All 486 combinations execute through the public `classify_existing_booking()` function with labelled assertion messages. Any failed combination reports its full axis tuple in the assertion message.

---

## Test Results

```powershell
pytest tests/test_bernie_booking_precedence_matrix.py -v
# 2 passed in 1.30s

pytest tests/test_bernie_booking_generated_matrix.py tests/test_bernie_booking_classifier.py tests/test_bernie_booking_boundary_matrix.py tests/test_bernie_booking_precedence_matrix.py -v
# 55 passed in 16.21s
```

All 55 tests pass, including:
- **2** generated interval matrix tests (260 half-open interval combinations — T2.1)
- **36** DB-backed classifier regression tests (the existing authored golden corpus)
- **15** DB-backed boundary/invariant tests (T2.1 independent authored cases)
- **2** new precedence matrix tests (486 exact-match combinations — T2.2)

---

## Reused DB-Backed Authored Coverage

The following areas remain covered by existing authored DB-backed tests (not duplicated in the new generated matrix):

| Area | Test file(s) | Coverage |
|---|---|---|
| **Terminal statuses** | `test_bernie_booking_classifier.py` | Completed, Cancelled, NoShow, DNA excluded from classification |
| **Roster / schedule** | `test_diary_roster.py`, `test_slot_search_proposal.py` | Per-practitioner schedule filtering, no-schedule-day yields no candidates |
| **Breaks** | `test_break_overlap_contract.py` | Break overlap surfaces warning but candidate still offered |
| **Location query filtering** | `test_location_scoped_diary.py`, `test_slot_search_proposal.py` | Conflict at other location does not block candidates |
| **Normalized bounds** | `test_bernie_slot_normalizer.py`, `test_bernie_booking_classifier.py` | Route candidates within normalized date/time bounds, earliest/latest edge cases |
| **Stale confirmation** | `test_bernie_signed_confirmation_evidence.py`, `test_bernie_slot_flow_review_harness.py` | Confirmation state management |
| **No-write (classifier)** | `test_bernie_booking_classifier.py`, `test_bernie_booking_boundary_matrix.py` | classifier-level read-only proof, route-level no-write proof |
| **No-write (slot search)** | `test_slot_search_proposal.py` | `test_slot_search_writes_no_appointments_and_no_audit_rows` |
| **Tenancy (practice isolation)** | `test_bernie_booking_classifier.py` | cross-practice isolation, separate practices do not affect each other |
| **Source exclusion** | `test_bernie_booking_classifier.py`, `test_bernie_d8_patient_collision_source_hardening.py` | Self-exclusion preserves other appointment detection |

---

## Acceptance Checklist

| Requirement | Status | Evidence |
|---|---|---|
| Combine matching/mismatching practitioner | ✅ | `PractitionerMode.match`, `.mismatch` (2 values) |
| Optional matching/mismatching appointment type | ✅ | `OptionalDim.not_supplied`, `.match`, `.mismatch` (3 values) |
| Optional matching/mismatching location | ✅ | `OptionalDim` for location (3 values) |
| Optional matching/mismatching duration | ✅ | `OptionalDim` for duration (3 values) |
| Temporal modes (both bounds, earliest-only, latest-only, no bounds, outside window) | ✅ | 9 temporal modes covering all spec variants |
| Exact duplicate only when practitioner + supplied dimensions + temporal evidence all satisfy contract | ✅ | Rule table in `_expected_classification()` |
| Non-exact cases retain correct overlap/same-day-distinct outcome | ✅ | Overlap computed per temporal mode; non-exact falls through to overlap then same-day |
| At least 200 labelled combinations | ✅ | 486 (exceeds 200) |
| Stable count guard | ✅ | `test_generated_precedence_matrix_has_stable_count` asserts 486 |
| Completes in routine-gate budget | ✅ | ~1.3s for the matrix node |
| No production code changed | ✅ | No files in `app/` touched |
| No DB changed | ✅ | No migrations/models/schemas touched |
| Report reused DB-backed coverage | ✅ | See table above |

---

## Findings

1. **Query-only session works for all 486 combinations.** The `_ReadOnlySession` pattern from T2.1's interval matrix generalises cleanly to the exact-match dimensions. Every combination calls `classify_existing_booking()` once and asserts one DB query — proving the classifier is a single-read operation regardless of dimension count.

2. **No edge-case gaps found.** The derived expected outcomes matched the classifier's actual behaviour on all 486 combinations. This confirms the classifier's `_is_exact_match()` and `_might_be_exact_duplicate()` logic is internally consistent with the contract documented in `bernie_booking_classifier.py`.

3. **Practitioner mismatch still produces `overlapping_same_patient` when time bounds exist and intervals overlap.** This is correct classifier behaviour — the classifier treats time-bounded overlap as a patient-level concern regardless of practitioner. The matrix covers both same-practitioner and different-practitioner overlap cases.

4. **The `_times_overlap()` function's default-latest-to-1440 behaviour** means `earliest_only` with a data earlier than existing_start+existing_duration always produces overlap — the matrix correctly tests this.

---

## Boundaries

- **`none` classification not produced** — The query-only session always has the row, so `none` (no appointments found) is unreachable. The DB-backed `test_no_existing_appointments_returns_none` covers this path.
- **Write prohibition** — The query-only session's `query()` raises no `AttributeError` on `.filter()` but does not expose `.add()`, `.flush()`, or `.commit()`. Any accidental write attempt in the classifier would fail at the session level. The DB-backed no-write proofs in `test_bernie_booking_classifier.py` and `test_bernie_booking_boundary_matrix.py` cover the route and classifier level independently.
- **Source-appointment exclusion** — Not tested in the matrix (requires a known appointment ID for self-exclusion, which adds semantic coupling). Already covered by `test_source_appointment_excluded` and `test_d8_source_exclusion_preserved`.
- **Date adjacency** — The matrix tests a single date. Cross-date boundary tests stay in `test_bernie_booking_boundary_matrix.py::TestDateBoundaries`.

---

## Verification

```powershell
# New precedence matrix tests
pytest tests/test_bernie_booking_precedence_matrix.py -q

# Full classifier + matrix regression
pytest tests/test_bernie_booking_generated_matrix.py ^
      tests/test_bernie_booking_classifier.py ^
      tests/test_bernie_booking_boundary_matrix.py ^
      tests/test_bernie_booking_precedence_matrix.py -q

# Whitespace check
git diff --check
```

---

**STATUS: complete**
