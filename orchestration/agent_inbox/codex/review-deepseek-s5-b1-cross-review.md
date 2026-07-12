# S5 B-1 D-2 Cross-Review

Sprint: S5
Role: D-2 independent cross-review
Candidate commit: `934871be` (tree matches HEAD `07a359b9` for the reviewed files)
Review scope: `docs/diary/diary.js`, `docs/diary/diary.html`, `review/test_diary_selection_preservation.py`

---

## Check: Selection captured before and restored after silent refresh

**PASS.** The fix at `diary.js:4351-4360` correctly:

1. **Captures** the active appointment ID before `renderGrid()` destroys the DOM:
   ```js
   const _activeBeforeId = document.querySelector(".appt-active")?.getAttribute("data-id") || null;
   ```
   Uses optional chaining (`?.`) — valid ES2020 — so `_activeBeforeId` is either a string ID or `null`.

2. **Restores** `.appt-active` after `renderGrid()` completes, only if the appointment element still exists:
   ```js
   if (_activeBeforeId) {
     const _el = document.querySelector(`.appt[data-id="${_activeBeforeId}"]`);
     if (_el) _el.classList.add("appt-active");
   }
   ```

The placement (inside `loadDiary()`, wrapping `renderGrid()`, before `loadTodayAppointments()`) is correct — it captures before the DOM is torn down and restores after the new DOM is built, before any unrelated async work continues.

The fix follows the existing restoration idiom used elsewhere in `diary.js` (lines 8635-8644 in `setAppointmentStatus`, which also use `.appt[data-id="..."]` selectors).

---

## Check: No selection fabricated when absent or when appointment disappears

**PASS.** Two independent guards:

- **Absent before refresh:** If no `.appt-active` element exists, `_activeBeforeId` is `null`, and the entire restore block is skipped. No `.appt-active` class is written to any element.
- **Appointment disappeared:** If the appointment with the captured ID was removed from the data and no longer renders, `querySelector` returns `null`, and the `if (_el)` guard prevents adding `appt-active` to a non-existent element.

The test `test_selection_not_fabricated_when_none_active_before_refresh` explicitly verifies the absent-before case: it clears `.appt-active` via `page.evaluate`, asserts zero `.appt-active` before refresh, triggers the silent refresh, then asserts zero `.appt-active` after.

---

## Check: Tests genuinely exercise the behaviour

**PASS.** The three tests cover the defect surface:

| Test | Surface | Verification |
|---|---|---|
| `test_selection_preserved_across_silent_refresh` | Selection preserved after `loadDiary(true)` for `smoke-appt-1` (Booked status) | ✅ |
| `test_selection_preserved_for_different_appointment` | Same for `smoke-appt-5` (Arrived status) — ensures the fix is not appointment-type-specific | ✅ |
| `test_selection_not_fabricated_when_none_active_before_refresh` | No `.appt-active` is fabricated when none existed before the refresh | ✅ |

The test uses `page.evaluate("() => loadDiary(true)")` — the exact production function path triggered by `scheduleRefresh` — not a synthetic event or mock. The smoke-mode fixtures (`?smoke=true`) provide deterministic, consistent appointments.

The original failing-first evidence (from the completion artifact) showed 2/3 tests failing before the fix and 3/3 passing after, confirming the test genuinely catches the defect.

---

## Check: Cache bust correct

**PASS.** `diary.js` cache-bust incremented from `v=181` to `v=182` in `diary.html:10`. Only `diary.js` was modified; `diary.css` (`v=135`) correctly unchanged. Single-line diff, no typographic issues.

---

## Check: No event, status, API, backend, or closed-gate semantics changed

**PASS.** The fix is a pure DOM manipulation — it captures an attribute before `renderGrid()` and adds a CSS class after. It does not:

- Change any API call, endpoint, or request payload
- Alter appointment status, status-change semantics, or lifecycle logic
- Touch event handlers or click/change listeners
- Modify any backend file (`app/`, routes, models, schemas)
- Open or alter any closed gate (Bernie D5, provider wiring, memory/RAG/GraphRAG, historical diary runtime/`local_data`, GraphQL expansion, deployment/Pages, schema migrations)
- Fix any pre-existing unrelated defect or Phase A finding
- Call `sync_taskpane.py`, deploy Pages, or modify any `review/` or `tests/` file besides the new test file

---

## Check: `node --check docs/diary/diary.js`

**PASS.** Syntax check passes without errors. No missing semicolons, unmatched brackets, or invalid syntax.

---

## Check: Focused test run

**NOT AVAILABLE.** Playwright is not available in this cross-review environment (Windows Microsoft Store Python redirect). The completion artifact from the original implementation workstream reports 3/3 passing on the fixed code. The test file is syntactically valid, uses the established `review/harness.py` pattern (same `stub_office`, `serve_dir`, `assert_valid_review_token` helpers, same smoke-mode URL structure), and references known smoke-mode appointment IDs from `getMockAppointments()`.

---

## Findings (not editing — per task instructions)

### Finding 1: Unused imports in test file

`review/test_diary_selection_preservation.py` imports `json` (line 15) and `time` (line 17), but neither is used anywhere in the test file:

```python
import json    # unused
import time    # unused
```

This is a minor hygiene issue. The tests work correctly without these imports. Recommend removing them before integration.

### Finding 2: Brittle timing

The test helper `_trigger_silent_refresh` uses `page.wait_for_timeout(500)` after `page.evaluate("() => loadDiary(true)")`. Since `loadDiary` is an `async function` doing multiple API fetches (`fetchAppointments`, `fetchAppointmentTypes`, `loadTodayAppointments`), 500ms is short enough to be brittle under load or slow network. In smoke mode (which mocks the API returns via `stub_office` and local `diary.js` mock data) the fetches return immediately, so this is acceptable for smoke tests, but if the tests are ever reused outside smoke mode, this timeout should be replaced with a DOM-based wait (e.g. `wait_for_selector(".diary-column")` or polling for a stable grid state).

### Finding 3: No test for appointment-removed-during-refresh case

The comment in `test_selection_not_fabricated_when_none_active_before_refresh` acknowledges that smoke-mode fixtures always return the same appointments regardless of date, so the "appointment was removed from the backend" case cannot be tested in smoke mode. The `if (_el)` guard in the production code correctly handles this case, but it is not end-to-end verified. This is an acceptable scope limitation for the current sprint but could be addressed in a future sprint with a route-intercepted test that returns different data on the second call.

---

## Summary

| Criterion | Verdict |
|---|---|
| Selection captured before and restored after silent refresh | ✅ PASS |
| No selection fabricated when absent before refresh | ✅ PASS |
| No stale selection when appointment disappeared from data | ✅ PASS (source guard, not E2E tested) |
| Tests genuinely exercise the defect surface | ✅ PASS |
| Cache bust correct (`v=181` → `v=182`) | ✅ PASS |
| No event/status/API/backend/closed-gate semantics changed | ✅ PASS |
| `node --check` syntax | ✅ PASS |
| Unused imports (`json`, `time`) | ⚠️ Finding — see above |
| Brittle timing (`wait_for_timeout`) | ⚠️ Finding — see above |
| Disappeared-appointment case not E2E tested | ⚠️ Finding — see above |

---

```text
DECISION: pass
```
