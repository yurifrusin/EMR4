# S8 W1 — Independent Review of Candidate

| Field | Value |
|---|---|
| Role | independent review / veto |
| Resource | `deepseek-flash-workers` instance 3 |
| Model | `deepseek-v4-flash` / high |
| Candidate | `12bac6c9a98928c4ed65c2ae1b88023762f3f59c` |
| Branch | `deepcode/s8-w3-w1-review` |
| Base | `24e6b171` (docs(ariadne): dispatch S8 implementation lanes) |
| Parent plan | `orchestration/agent_inbox/codex/plan-claude-fable-s8-receptionist-workflow.md` |
| W1 packet | `orchestration/agent_inbox/deepcode/deepcode-s8-w1-diary-launch-reliability.md` |
| W1 completion artifact | `orchestration/agent_inbox/codex/review-deepseek-s8-w1-launch-reliability.md` |
| Rejected attempt 1 | `review-deepseek-s8-w1-launch-reliability-attempt1-rejected.md` |
| Rejected attempt 2 | `review-deepseek-s8-w1-launch-reliability-attempt2-rejected.md` |
| Date | 2026-07-13 |

---

## 1. Candidate Summary

Single commit on `deepcode/s8-w3-w1-review` (which is also HEAD). The candidate is the output of W1 implementation (initial attempt), Revision 1 (test repair), and Revision 2 (ownership boundary correction), committed together:

```
12bac6c9 feat(taskpane): harden diary launch
```

### Files changed (12 files, +918/-18)

**Production files (W1-owned):**
| File | Δ | Purpose |
|---|---|---|
| `EMR4 Sidebar/src/taskpane/taskpane.js` | +106/-18 | `resolveDiaryUrl()`, `getDiaryErrorMessage()`, `showDiaryError()`/`hideDiaryError()`, `_setupDiaryDialog()`, `retryOpenDiary()`, rewritten `openDiary()` with 12007 auto-retry |
| `EMR4 Sidebar/src/taskpane/taskpane.html` | +5/-2 | Diary error container (`#diary-error`), cache bump `?v=54→55` (css), `?v=57→58` (js) |
| `EMR4 Sidebar/src/taskpane/taskpane.css` | +31 | `.diary-error` banner, `.btn-diary-retry` styles |
| `review/test_taskpane_diary_launch.py` | +338 (new) | 13 Playwright/pytest tests |

**Orchestration artifacts:**
- `orchestration/agent_inbox/codex/review-deepseek-s8-w1-launch-reliability.md` (completion)
- `orchestration/agent_inbox/codex/review-deepseek-s8-w1-launch-reliability-attempt1-rejected.md`
- `orchestration/agent_inbox/codex/review-deepseek-s8-w1-launch-reliability-attempt2-rejected.md`
- `orchestration/agent_inbox/deepcode/deepcode-s8-w1-revision-1.md`
- `orchestration/agent_inbox/deepcode/deepcode-s8-w1-revision-2.md`
- `orchestration/deepcode_pty/s8-w1-receipt.json` (completed, `turn_completion_observed: true`)
- `orchestration/deepcode_pty/s8-w1-r1-receipt.json` (failed, `turn_completion_timeout`)
- `orchestration/deepcode_pty/s8-w1-r2-receipt.json` (completed, `turn_completion_observed: true`)

---

## 2. Evidence Collected

### 2a. Focused test suite

```bash
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m pytest review/test_taskpane_diary_launch.py -v --tb=short
```
Result: **13 passed in 1.25s** — all 13 tests pass.

| Class | Tests | Coverage |
|---|---|---|
| `TestResolveDiaryUrl` | 4/4 | Dev server port 3000 → local; GitHub Pages, ngrok, unknown → deployed Pages fallback |
| `TestGetDiaryErrorMessage` | 5/5 | 12007 (`retry_once`), 12009 (Allow prompt), 12011 (popups blocked), generic, generic+missing raw |
| `TestRetryAffordance` | 3/3 | Hidden on load, visible on error, hidden after retry |
| `Test12007AutoRetry` | 1/1 | Exactly 2 `displayDialogAsync` calls (first + one retry), error banner visible, message non-empty |

**No evidence of test weakening.** No `xfail`, no `@unittest.skip`, no `pytest.skip` (except the module-level Playwright import guard in line 24 which is standard). All tests have real assertions that prove specific behaviour. The 12007 test proves exactly 2 calls using a non-writable `Object.defineProperty` mock — honest, not weakened.

### 2b. JavaScript syntax

```bash
node --check "EMR4 Sidebar/src/taskpane/taskpane.js"
```
Result: **OK** (exit 0).

### 2c. Whitespace

```bash
git diff --check 24e6b171..12bac6c9
```
Result: **Clean** (exit 0) — no whitespace errors.

### 2d. Shared harness integrity

```bash
git diff 24e6b171..12bac6c9 -- review/harness.py
```
Result: **Empty** — `review/harness.py` was restored to base `24e6b171` per Revision 2 requirements. All expanded Office stub code (`_OFFICE_STUB`, `stub_office`, `assert_valid_review_token`, `_decode_base64url_json`) lives locally inside `review/test_taskpane_diary_launch.py` and does not import from `harness.py`.

### 2e. Pre-existing review suites

```bash
git ls-tree --name-only 24e6b171 -- review/
git ls-tree --name-only 12bac6c9 -- review/
```
The candidate adds exactly one new file (`review/test_taskpane_diary_launch.py`). All 7 pre-existing review files (`test_diary_smoke.py`, `test_diary_selection_preservation.py`, `test_diary_graphql_practitioner_switch.py`, `test_diary_deprecation_consumer.py`, `test_raw_status_terminal_rollback_guard.py`, `harness.py`, etc.) are **unchanged**.

### 2f. sync_taskpane.py

```bash
git diff 24e6b171..12bac6c9 -- sync_taskpane.py
```
Result: **Empty** — `sync_taskpane.py` is untouched.

### 2g. PROTECTED_SECTIONS invariant

`grep -c "PROTECTED_SECTIONS"` on `taskpane.js` at base and candidate: **3 in both** — unchanged.

### 2h. Command Centre isolation

The diff touches zero code in or near `openCommandCentre()` or `CC_URL`. The only mention of `openCommandCentre` in the diff is the pre-existing comment `// NOTE: synchronous within the click gesture — same rule as openCommandCentre.`

---

## 3. Veto Criteria Assessment

| Criterion | Finding |
|---|---|
| **Test weakening** | ✅ Not observed. All 13 tests are honest with real assertions. The 12007 test proves exactly 2 calls via a non-writable mock. No assertions stripped. |
| **Incorrect URL resolution** | ✅ Not observed. `resolveDiaryUrl` maps port 3000 to local, everything else to deployed Pages fallback. Tests confirm all 4 environments. |
| **Unbounded 12007 retry** | ✅ Not observed. The code retries exactly once after 12007 (close stale handle → retry → if fails again, show error, no loop). Test proves `_diaryCallCount === 2`. |
| **Inaccessible/misleading failure UI** | ✅ Not observed. `#diary-error` banner with amber background, `role="alert"`, receptionist-readable messages per code, visible Retry button. Tests confirm hidden-on-load, visible-on-error, non-empty message. |
| **Command Centre regression** | ✅ Not observed. `openCommandCentre()` and `CC_URL` fully untouched. |
| **Shared harness modification** | ✅ Not observed. `review/harness.py` diff is empty. Test file keeps all stubs local. |
| **Scope/gate expansion** | ✅ Not observed. Only W1-owned files modified: `taskpane.js`, `taskpane.html`, `taskpane.css`, new test file. No `docs/diary/`, backend, schema, migrations, provider, H15/H-series, memory, RAG, GraphRAG, or terminal-status touches. |
| **Artifact claims vs observed evidence** | ✅ Passes. Artifact claims 13 passed, `node --check` OK, whitespace clean, harness restored, URL resolver correct, exactly-two-call 12007 proof — all confirmed. |

---

## 4. Word Online Strictness Check (Conservative)

The candidate adds:
- **CSS**: Simple `.diary-error` flex layout, `#fef3c7`/`#fbbf24` amber background, standard border-radius and cursor — no OOXML injection, no desktop-specific rendering dependency.
- **HTML**: Basic `<div>` with `role="alert"` and `hidden` class toggling — widely supported in Office Online dialogs.
- **JS**: `document.getElementById()`, `classList` operations, `window.location`, and standard Office.js API (`displayDialogAsync`, `addEventHandler`, `DialogEventReceived`, `DialogMessageReceived`, `AsyncResultStatus`) — all documented as working in Word Online.

No risk of out-of-order OOXML element rejection or desktop-tolerated behaviour that would break in Word Online.

---

## 5. Residual Risks (recorded, not blocking)

1. **sync_taskpane.py integration**: Sol must run `python sync_taskpane.py` to copy source → `docs/taskpane/` and verify the patched output. The resolver is runtime (`window.location`) so no sync patch is needed for the diary URL itself, but the existing `BACKEND_URL` patch block must be verified at integration time.
2. **Local diary hosting**: Port 3000 resolution assumes the dev server serves `docs/diary/`. If `run_dev.ps1` does not yet serve `docs/`, the local URL produces a 404 (out of S8 scope per §12 of the parent plan).
3. **Playwright prerequisite**: The new test suite requires `playwright` pip-installed and Chromium installed. Already satisfied in the shared main venv.
4. **Office dialog codes are advisory**: The generic fallback covers unhandled codes and raw error messages. The exact codes 12007/12009/12011 behaviour in Word Online vs Desktop may vary slightly, but the fallback renders a usable message in all cases.

---

## 6. Decision

**DECISION: pass**

The candidate meets all W1 requirements from the parent plan:
- Pure, testable URL resolver (`resolveDiaryUrl`) with environmental awareness and safe deployment fallback
- Distinct receptionist-readable error handling for 12007, 12009, 12011, and generic failures
- Visible error banner with retry affordance
- Bounded single retry for 12007 (proven by exactly-two-call test)
- `sync_taskpane.py` patch parity preserved, Command Centre behaviour preserved
- Cache-bust bumped
- 13 focused tests passing, JS syntax clean, whitespace clean
- No test weakening, no scope expansion, no shared harness modification
- Word Online compatible
- Rejected-attempt history preserved transparently
- PTY receipts at all three stages (attempt 1 completed, revision 1 timed out, revision 2 completed)

No veto triggers are present. Sol may proceed with acceptance and integration into the S8 checkpoint.
