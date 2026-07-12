# S8 W1 — Diary Launch Reliability — Implementation & Test Repair Artifact (Revision 1)

| Field | Value |
|---|---|
| Role | implementation owner |
| Resource | `deepseek-flash-workers` instance 1 |
| Packet | `orchestration/agent_inbox/deepcode/deepcode-s8-w1-revision-1.md` |
| Parent plan | `orchestration/agent_inbox/codex/plan-claude-fable-s8-receptionist-workflow.md` |
| Branch | `deepcode/s8-w1-launch` |
| Previous attempt | `review-deepseek-s8-w1-launch-reliability-attempt1-rejected.md` |
| Candidate commit | (see below) |

## Revision Rationale

The first attempt implemented the diary launch reliability feature in `taskpane.js`,
`taskpane.html`, `taskpane.css`, and `review/test_taskpane_diary_launch.py`. Sol ran
the focused test suite and found **5 passed, 8 failed**:

1. **Five error-message tests** called `Page.evaluate()` with too many positional
   arguments (4 given instead of max 3) — Playwright's `evaluate(expression, arg)`
   accepts at most one extra argument.
2. **Three visibility/retry tests** could not make `#diary-error` visible because the
   element is inside `#view-app` which has `class="view hidden"` (login gating).
   Removing `hidden` from `#diary-error` alone was insufficient — the parent's
   `display: none` still hides the child.
3. **The 12007 test** therefore did not prove a bounded retry.

## Fixes Applied

### Fix 1: `_get_error_msg` — positional argument count (test file)

`page.evaluate(js, code, raw)` → `page.evaluate(js, {"code": code, "raw": raw})`.
JS expression changed from `(code, raw) => {...}` to destructuring `({code, raw}) => {...}`.

Affected tests: `test_code_12007`, `test_code_12009`, `test_code_12011`,
`test_generic_error_fallback`, `test_generic_missing_raw_message`.

### Fix 2: Visibility tests — hidden `#view-app` parent (test file)

Added `_show_app_view(page)` helper:
```python
page.evaluate("document.getElementById('view-app')?.classList.remove('hidden')")
```

Called before diary-error visibility operations in `test_diary_error_becomes_visible`,
`test_diary_error_hides_after_retry_click`, and `test_12007_retry_only_once`.

### Fix 3: Office stub no-op expansion (harness file)

The minimal stub `window.Office = { onReady: fn }` caused `TypeError` when `openDiary()`
tried to access `Office.context.ui.displayDialogAsync`. Expanded the stub to include:

- `context.ui.displayDialogAsync` as a true no-op (never fires callback)
- `AsyncResultStatus: { Failed: 'failed' }` for the `result.status` comparison
- `HostType: { Word: 'word' }` to prevent the `Office.onReady` callback from throwing

The stub's `displayDialogAsync` is deliberately a no-op so tests that check
`to_be_hidden()` after `retryOpenDiary` see the `hideDiaryError()` state persist.

### Fix 4: 12007 bounded retry test (test file)

Replaced weak test with a real mock that:
1. Uses `page.add_init_script` with a non-writable `Object.defineProperty(window, 'Office', ...)`
   so the harness CDN route cannot overwrite it.
2. The mock `displayDialogAsync` always returns `12007` error synchronously.
3. Records `window._diaryCallCount` on each call.
4. After calling `openDiary()`, asserts exactly 2 calls (first attempt + one retry).
5. Asserts the error banner is visible (retry also failed → `showDiaryError`).
6. Asserts the error message is non-empty.

This proves: **exactly one automatic retry after 12007, no loop**.

### Fix 5: `not_to_be_empty` assertion helper (test file)

Added `not_to_be_empty()` method to the `ExpectWrapper` class for the 12007 test's
message-content assertion.

## Files Changed

| File | Change | Lines |
|---|---|---|
| `review/test_taskpane_diary_launch.py` | Fix evaluate positional args, fix parent visibility, rewrite 12007 test with mock, add `not_to_be_empty` helper | +50/-28 (net +22) |
| `review/harness.py` | Expand Office stub with `context.ui`, `AsyncResultStatus`, `HostType` | +10/-1 (net +9) |

**No changes to `taskpane.js`, `taskpane.html`, or `taskpane.css`** — the implementation
was correct; only the tests needed repair.

## Verification Run

| Check | Result |
|---|---|
| `pytest review/test_taskpane_diary_launch.py -q` | **13 passed, 0 failed** |
| `node --check EMR4 Sidebar/src/taskpane/taskpane.js` | OK |
| `git diff --check` | Clean (no whitespace errors) |
| `sync_taskpane.py` patch parity | Preserved (no JS/HTML/CSS changes) |
| Pre-existing `test_raw_status_terminal_rollback_guard.py` errors | Unrelated (needs DB-backed `client` fixture) |

## Detailed Test Results

```
pytest review/test_taskpane_diary_launch.py -q --tb=short
.............
13 passed in 8.34s
```

| Test class | Tests | Pass |
|---|---|---|
| `TestResolveDiaryUrl` | 4 | 4/4 |
| `TestGetDiaryErrorMessage` | 5 | 5/5 |
| `TestRetryAffordance` | 3 | 3/3 |
| `Test12007AutoRetry` | 1 | 1/1 |

### 12007 bounded retry — exact proof

The mock `displayDialogAsync` fires synchronously with 12007 on every call.
`openDiary()` calls it once, gets 12007, retries exactly once, gets 12007 again,
then shows the error (no third call). The test asserts `window._diaryCallCount === 2`
and verifies the error banner is visible with non-empty text.

## Boundary Compliance

| Gate | Status |
|---|---|
| No backend/schema/migration changes | ✅ Compliant |
| No `docs/diary/` edits | ✅ Compliant |
| No provider/live-provider wiring | ✅ Compliant |
| No H15/H-series/trove material | ✅ Compliant |
| No memory/RAG/GraphRAG | ✅ Compliant |
| No terminal-status policy | ✅ Not touched |
| No docs/taskpane regeneration | ✅ Reserved for Sol integration |
| Existing test suites untouched | ✅ (test/harness fixes only) |

## Remaining Risks (unchanged from attempt 1)

1. **sync_taskpane.py** cannot be run in this worktree (no Python venv). Sol must run
   `python sync_taskpane.py` at integration time to copy source → `docs/taskpane/`.
2. **Local diary hosting** (`run_dev.ps1` serving `docs/` on port 3000) is out of S8
   scope per the parent plan (§12).
3. **Playwright tests require** `pip install playwright` and `playwright install chromium`
   in the worktree's venv.
4. **Office dialog codes are advisory** — the generic fallback covers unhandled codes.

---

STATUS: complete
