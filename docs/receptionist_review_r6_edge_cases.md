# R6 Temporal Edge-Case Scout — Finalized Review Artifact

> **Status:** Finalized
> **Worker:** Shen (DeepSeek Flash)
> **Branch:** codex/sprint-r6-temporal-edge-scout
> **Baton base:** 99a5e50 — Sprint R5 executable Bernie scenario promotion
> **Date:** 2026-07-05
> **Audience:** Ariadne/Codex (orchestrator), Claude (main implementation lane)
> **Instruction:** Review artifact only. Do not edit production code or tests.

---

## Findings Verified Against Source

All edge cases in this matrix were traced through source code, not inferred from
spec or comment documentation. Key files examined:

| File | Path |
|---|---|
| Temporal policy (pure) | `app/services/diary/temporal.py` (6.6 KB) |
| Interpret + supervised routes | `app/routers/appointments.py` (275 KB) |
| Slot normalizer | `app/services/bernie_slot_normalizer.py` (10 KB) |
| Temporal policy tests | `tests/test_bernie_temporal_policy.py` |

---

## Category A: Should Fix Now — Route-Level Bug

### A1 — `window_fully_past` with only `latest_time` set (interpret path)

| Field | Value |
|---|---|
| **Layer** | Interpret path — `propose_bernie_interpret_booking_instruction` |
| **Source** | `app/routers/appointments.py` line 3718–3722 |
| **Edge case** | Receptionist says "Book today before 10 AM" at 10:30 AM. Only `latest_time` (10:00) is extracted; `earliest_time` is `None`. |
| **Expected behaviour** | `evaluate_same_day_window()` returns `window_fully_past`. The interpret path should recognise the band is exhausted and set `temporal_band = "ask"` with a clarifying message. |
| **Actual behaviour** | The guard at line 3718–3722 requires BOTH `_earliest is not None` AND `_latest is not None`. Since `_earliest` is `None`, the condition is `False`. The `temporal_band` is never set to `"ask"`, and the request proceeds as if the window is still open — searching for slots that cannot exist. |
| **Risk** | **Medium.** User confusion (searches for unreachable slots), wasted LLM calls. The supervised path (line 5734) is NOT affected — it checks only `same_day_decision.kind == "window_fully_past"` without requiring `_earliest`. The UI currently uses the supervised path, so this bug affects the interpret path which powers the LLM-band backend. |

**Proposed fix** (one-line change at line 3718):

```python
# Current (gap):
if (
    same_day_decision.kind == "window_fully_past"
    and _earliest is not None
    and _latest is not None
):
# Proposed:
if (
    same_day_decision.kind == "window_fully_past"
    and (_latest is not None)
):
```

**Rationale:** `evaluate_same_day_window()` (line 182) returns `window_fully_past` when `latest_time is not None and latest_time <= now_time`. The `earliest_time` parameter is irrelevant for this decision path — the window is fully past whether or not an earliest boundary was set. Removing the `_earliest is not None` guard is safe because:
- If both earliest and latest are set and the window is fully past → still caught by `_latest is not None`.
- If only latest is set (the bug case) → now caught.
- If neither is set, `evaluate_same_day_window()` cannot return `window_fully_past` (only `"ok"`), so the guard is never reached.

**Affected copy (line 3724–3727):** The existing "ask" band message is already
generic: *"Same-day request: the requested time window has already passed today."*
No copy change needed.

**New test needed:**

```python
def test_same_day_window_fully_past_latest_only():
    """window_fully_past when only latest_time is set and it has passed."""
    decision = evaluate_same_day_window(
        date(2026, 7, 3),   # same day
        None,                # no earliest
        time(10, 0),         # latest = 10:00
        _dt(10, 30),         # now = 10:30
    )
    assert decision.kind == "window_fully_past"
```

The existing test `test_same_day_window_fully_past_when_latest_is_not_after_now`
sets BOTH earliest and latest, so it passes without triggering the corner case.
The pure function already handles the scenario — the bug is in the interpret
path adapter, not in `evaluate_same_day_window()`.

---

## Category B: Should Fix Now — Missing Coverage (Minor)

### B1 — `clamp_earliest` without `latest_time` in interpret path — copy basis

| Field | Value |
|---|---|
| **Source** | Line 3728–3744 |
| **Edge case** | When `clamp_earliest` fires and `_latest` is not None, the basis correctly says "clamped because partly passed". When `_latest` is None (open-ended), the basis says "open-ended start time had already passed" (also correct). But if both earliest and latest are None after clamping, `temporal_clarifying` may use a stale copy. |
| **Risk** | **Low.** The clamp behaviour itself is correct. Only the clarifying question copy might be stale — the LLM receives the correct constraint either way. |

### B2–B4 — Already Covered (Documented for completeness)

| # | Edge Case | Layer | Status |
|---|---|---|---|
| B2 | Same-day latest_time == now_time exact boundary | Supervised path (line 5734) | **Already covered.** `evaluate_same_day_window` returns `window_fully_past` at exact boundary; supervised path catches ALL `window_fully_past` cases. |
| B3 | date_to crosses midnight into the past | Slot normalizer | **Already covered.** `SlotSearchProposalIn.validate_date_range()` catches `date_to < date_from`. |
| B4 | "today" + reference_date is in the past | Route intake | **Already covered.** Session freshness guards (`session_reference_date_stale` / `stale_session_revision`) handle stale sessions. |

---

## Category C: Worth Adding Executable Fixtures

| # | Edge Case | Layer | Status |
|---|---|---|---|
| C1 | Same-day open-ended "after X" passes 24-hour boundary | Pure + route | **No gap found.** Consider an integration-level assertion. |
| C2 | Same-day window_fully_past supervised path with only-latest | Supervised path (line 5734) | **Already covered in code.** The supervised path checks `kind == "window_fully_past"` without requiring `_earliest`. No executable test asserts this — worth adding one. |
| C3 | Exact-now earliest boundary | Pure + supervised | **Already covered** by `test_same_day_window_ok_at_exact_earliest_boundary`. |
| C4 | date_to exceeds 14-day ceiling | Supervised path | **Already covered.** `SlotSearchProposalIn` schema clamps. |

---

## Category D: Defer / Document Only

| # | Edge Case | Layer | Recommendation |
|---|---|---|---|
| D1 | Raw mutation date-policy separate from slot search | Product policy | **Defer to product policy sprint.** Current system blocks past-date slot searches but does not block raw appointment creation with a past date. |
| D2 | Timezone boundary at clinic-local midnight | Pure + route | **Already covered.** Stale reference_date / session freshness guards handle this. |

---

## Summary

| Priority | Finding | Action |
|---|---|---|
| **High** | A1 — interpret path misses `window_fully_past` when only `latest_time` is set | One-line fix in `app/routers/appointments.py:3718` |
| **Medium** | C2 — no executable test for supervised path with only-latest `window_fully_past` | Add test fixture |
| **Low** | B1 — minor copy staleness in `clamp_earliest` with no latest | Document only |
| **Documented** | B2–B4, C1, C3–C4, D1–D2 | Already covered or deferred |

The only genuine route-level gap is **A1**: a one-line code change (remove
`and _earliest is not None` from the guard at line 3718) combined with a
single new test for the pure function with `latest_time`-only past boundary.


---

## Completion Note

> **Submitted via:** Artifact only (git `add` blocked by sandbox).
> **File:** `docs/receptionist_review_r6_edge_cases.md` on branch `codex/sprint-r6-temporal-edge-scout`.
> **Ariadne action needed:** `git add docs/receptionist_review_r6_edge_cases.md && git commit -m "Finalize R6 temporal edge-case scout review artifact"` then integrate via normal flow.
> **Do not edit production code or tests.** This is a review-only artifact.
