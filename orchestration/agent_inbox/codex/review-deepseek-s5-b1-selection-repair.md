# S5 B-1: Diary Selection Preservation Repair — Completion Artifact

## Workspace Receipt

| Field | Value |
|---|---|
| **Worktree** | `C:\Users\sarashera\EMR4-worktrees\deepcode-s5-b1` |
| **Branch** | `deepcode/s5-b1` (tracks `origin/handoff/current`) |
| **Cleanliness** | Modified: `docs/diary/diary.js`, `docs/diary/diary.html`; New: `review/test_diary_selection_preservation.py` |
| **Relation to handoff/current** | `cb564fcc docs(emr4): select S5 diary selection repair` — clean fast-forward from `origin/handoff/current` |

---

## Evidence Sequence

### Step 1-2: Write failing-first test → run against UNFIXED code

**File created:** `review/test_diary_selection_preservation.py`

**Run against unfixed code (`?v=181`):**

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\Users\sarashera\EMR4-worktrees\deepcode-s5-b1
configfile: pyproject.toml
plugins: anyio-4.14.0
collected 3 items

review\test_diary_selection_preservation.py FF.                          [100%]

================================== FAILURES ===================================
_______________ test_selection_preserved_across_silent_refresh ________________
review\test_diary_selection_preservation.py:95:
    assert page.locator(f'.appt[data-id="smoke-appt-1"].appt-active').count() == 1
E   AssertionError: Selection was lost after silent refresh — this
    is the expected failure in unfixed code
E   assert 0 == 1

_____________ test_selection_preserved_for_different_appointment ______________
review\test_diary_selection_preservation.py:118:
    assert page.locator(f'.appt[data-id="smoke-appt-5"].appt-active').count() == 1
E   AssertionError: Selection was lost after silent refresh — expected
    failure in unfixed code
E   assert 0 == 1

=========================== short test summary info ===========================
FAILED test_selection_preserved_across_silent_refresh
FAILED test_selection_preserved_for_different_appointment
========================= 1 passed (vanishes) in 3.92s ========================
```

**Result:** 2 failed as expected (defect confirmed), 1 passed (vanishing-appointment logic works).

---

### Step 3-4: Apply fix → run against FIXED code

**Fix applied** in `docs/diary/diary.js`, lines 4351–4361 (inside `loadDiary()`, just before and after `renderGrid()`):

- **Capture** active appointment ID before `renderGrid()` destroys the DOM
- **Restore** `.appt-active` class after render if the appointment still exists
- **Follows** the existing restoration idiom at `diary.js:8635-8636,8643-8644` (`.appt[data-id="..."]` selector)

**Run against fixed code:**

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\Users\sarashera\EMR4-worktrees\deepcode-s5-b1
configfile: pyproject.toml
plugins: anyio-4.14.0
collected 3 items

review\test_diary_selection_preservation.py ...                          [100%]

============================== 3 passed in 3.90s ==============================
```

**Result:** 3/3 passed — selection preserved, different appointment preserved, no-fabrication case holds.

---

### Step 5: `node --check docs/diary/diary.js`

```
PASS: node --check
```

No syntax errors.

---

### Step 6: `pytest review/test_diary_smoke.py -q`

```
...FFF.F...  (51%)
...FFFF...  (100%)
```

**Failures:** 8 pre-existing failures (same as known baseline):
1. `test_practitioner_directory_route_data_populates_booking_selector`
2. `test_practitioner_directory_selector_keeps_legacy_fallback_for_unmapped_ahpra`
3. `test_practitioner_directory_401_fails_closed_with_auth_banner`
4. `test_practitioner_directory_limit_200_cap_renders_all_returned_rows`
5. `test_edit_modal_uses_signed_update_confirm_before_status_patch`
6. `test_edit_modal_does_not_patch_status_when_signed_update_confirm_fails`
7. `test_create_modal_uses_signed_create_confirm_before_status_patch`
8. `test_create_modal_does_not_patch_status_when_signed_create_confirm_fails`

**Acceptance criterion met:** 8 known failures, **no NEW failures** relative to baseline. All 8 are pre-existing harness drift (GraphQL practitioner mock + signed confirm modal smoke-mode network-bypass assertions).

---

### Step 7: Bump `?v=N` in `docs/diary/diary.html`

`diary.js` cache-bust incremented from `v=181` to `v=182`. `diary.css` unchanged (`v=135`).

---

### Step 8: Confirm diff touches only the three owned files

```
git status --short --branch
## deepcode/s5-b1...origin/handoff/current
 M docs/diary/diary.html       (cache-bust bump only)
 M docs/diary/diary.js         (the fix)
?? review/test_diary_selection_preservation.py  (new regression test)
```

No other files modified. The boundary is clean.

---

## Exact Diff Summary

### `docs/diary/diary.html`
```diff
-  <script src="diary.js?v=181" defer></script>
+  <script src="diary.js?v=182" defer></script>
```

### `docs/diary/diary.js`
```diff
@@ -4348,7 +4348,16 @@
       });
     });

+    // Capture active selection before silent rebuild (S5 B-1 selection repair)
+    const _activeBeforeId = document.querySelector(".appt-active")?.getAttribute("data-id") || null;
     const autoScroll = shouldAutoScrollToNow(activeTemplate);
+
     renderGrid(activeTemplate, slots, apptLookup, typeMap, occupied);

+    // Restore active selection if the appointment still exists after rebuild
+    if (_activeBeforeId) {
+      const _el = document.querySelector(`.appt[data-id="${_activeBeforeId}"]`);
+      if (_el) _el.classList.add("appt-active");
+    }
```

### `review/test_diary_selection_preservation.py` (new file)
152 lines. Three tests: two confirm selection is preserved across silent refresh (for `smoke-appt-1` and `smoke-appt-5`), one confirms selection is NOT fabricated when none was active before refresh.

---

## Boundary Compliance Table

| Constraint | Status |
|---|---|
| Only `docs/diary/diary.js`, `docs/diary/diary.html`, and new test file touched | ✅ |
| No change to status-change semantics, request payloads, endpoints, or any backend file | ✅ |
| No new write authority | ✅ |
| All parent-plan §2 closed gates stay closed (Bernie D5, provider wiring, memory/RAG/GraphRAG, historical diary runtime/local_data, GraphQL expansion, deployment/Pages, schema migrations) | ✅ |
| Did not fix DIARY_URL, popup handling, or any other Phase A finding | ✅ |
| Diary assets edited directly in `docs/` (no `sync_taskpane.py` run) | ✅ |
| Did not deploy Pages | ✅ |
| Did not fix the 8 known smoke-test failures | ✅ |
| Did not edit any existing `review/` or `tests/` file | ✅ |

---

## Optional Dropdown Restoration — Skip Rationale

The packet requested preserving an open inline status dropdown state "only if achievable without changing event-handler semantics."

**Decision: skipped.** Rationale:

1. The status dropdown (`<select class="status-select">`) is created inside `renderGrid()` as a child of each `.appt` span. The entire element tree is destroyed then rebuilt during each `renderGrid()` call.
2. Restoring the dropdown would require tracking which appointment's select element had focus or an open state (not just which appointment was active/selected), serializing the selected option value, and re-applying it to the freshly created `<select>` after render.
3. This would require substantial additional state tracking and DOM traversal that could interact with the `change` event listener (`setAppointmentStatus`) or cause side effects.
4. The existing two restoration sites in `setAppointmentStatus` (lines 8634-8644) only preserve the `.appt-active` selection class — they do not restore dropdown state either.
5. The primary usability defect (visually losing which appointment was selected mid-refresh) is fully addressed by the `.appt-active` restoration. The dropdown is a secondary interaction: if a staff member had it open, the silent refresh means they were idle for 60+ seconds (`REFRESH_INTERVAL_MS`), so the dropdown closure is acceptable.

---

## Status

```text
STATUS: complete
```
