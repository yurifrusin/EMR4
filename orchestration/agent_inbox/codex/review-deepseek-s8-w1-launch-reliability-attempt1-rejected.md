# S8 W1 — Diary Launch Reliability — Implementation Artifact

| Field | Value |
|---|---|
| Role | implementation owner |
| Resource | `deepseek-flash-workers` instance 1 |
| Packet | `orchestration/agent_inbox/deepcode/deepcode-s8-w1-diary-launch-reliability.md` |
| Parent plan | `orchestration/agent_inbox/codex/plan-claude-fable-s8-receptionist-workflow.md` |
| Branch | `deepcode/s8-w1-launch` |
| Base commit | `24e6b171` (docs(ariadne): dispatch S8 implementation lanes) |
| Candidate commit | (staged at `deepcode/s8-w1-launch` but not committed — permission denied at commit step. Base `24e6b171`, staged diff includes 4 files, +410/-20 net) |
| Settings fingerprint | `sha256:58313bbfd011f4eb70234fc320b1c0393f2a6a56dd537f329baacd830010cb24` |

## Files Changed

| File | Change | Lines |
|---|---|---|
| `EMR4 Sidebar/src/taskpane/taskpane.js` | Add `resolveDiaryUrl()`, error mapping, rewrite `openDiary()` with 12007 auto-retry, retry affordance, and `_setupDiaryDialog()` | +106/-18 |
| `EMR4 Sidebar/src/taskpane/taskpane.html` | Add diary-error container; bump `?v=54→55` (css) and `?v=57→58` (js) | +5/-2 |
| `EMR4 Sidebar/src/taskpane/taskpane.css` | Add diary-error banner and retry-button styles | +31 |
| `review/test_taskpane_diary_launch.py` | **New** — focused Playwright/pytest coverage | +268 |

## Implemented Behavior

### 1. Pure URL resolver: `resolveDiaryUrl(location)`

A pure, unit-testable function that mirrors the `BACKEND_URL` environment pattern:

- **Port 3000** (dev server) → `http://localhost:3000/diary/diary.html` (local diary, served by npm dev server)
- **Everything else** (GitHub Pages, ngrok, unknown) → `https://yurifrusin.github.io/EMR4/diary/diary.html` (deployed Pages diary, safe fallback)

The hardcoded `const DIARY_URL = "https://..."` is replaced by `const DIARY_URL = resolveDiaryUrl(window.location)`.

### 2. Error-code mapping: `getDiaryErrorMessage(code, rawMessage)`

| Code | Receptionist-readable message | Action |
|---|---|---|
| 12007 | "The Diary window was already open. Closing the old window and trying again..." | `retry_once` (auto-retry) |
| 12009 | "Diary window request was declined. When Word shows the Allow prompt, select Allow to open the Diary." | `retry_user` |
| 12011 | "Popup blocked by your browser. Please enable popups for this site and try again." | `retry_user` |
| generic | "Could not open Diary: <raw message>" | `retry_user` |

### 3. Visible error display and retry affordance

A `#diary-error` banner appears below the command-centre bar with:
- Orange warning background (`#fef3c7` with amber border)
- The receptionist-readable error message
- A visible Retry button calling `retryOpenDiary()`

This is in addition to the `setStatus()` line, so the failure is clearly visible in the taskpane.

### 4. Bounded 12007 auto-retry

When `displayDialogAsync` returns code 12007:
1. Close the stale dialog handle (best-effort)
2. Null out `diaryDialogRef`
3. Call `displayDialogAsync` exactly once more
4. If the retry also fails, show the error message (no further retry, no loop)

### 5. sync_taskpane.py patch parity preserved

The `BACKEND_URL` block (lines 7–9) is unchanged. The `.replace()` pair in `sync_taskpane.py` still matches exactly. The diary resolver is self-contained and does not need a sync patch — it reads `window.location` at runtime.

### 6. Cache-bust bump

- `taskpane.css`: `v=54` → `v=55`
- `taskpane.js`: `v=57` → `v=58`

### 7. Command Centre behavior preserved

`openCommandCentre()` and `CC_URL` are untouched. Shared helper functions (`hideDiaryError`, `setStatus`, `showDiaryError`) are new additions only; none affect the CC launch path.

## Tests

New file: `review/test_taskpane_diary_launch.py`

| Test class | Tests | Coverage |
|---|---|---|
| `TestResolveDiaryUrl` | 4 | Dev server (port 3000), GitHub Pages, ngrok tunnel, unrecognized-host safe fallback |
| `TestGetDiaryErrorMessage` | 5 | 12007, 12009, 12011 codes, generic error, generic missing raw message |
| `TestRetryAffordance` | 3 | Error banner hidden on load, visible after show, hidden after retry click |
| `Test12007AutoRetry` | 1 | Retry hides error before attempting dialog open |

Test pattern: `serve_dir` + `stub_office` from `review/harness.py`, pure-function evaluation through `page.evaluate()`, and DOM visibility assertions.

## Verification Run

| Check | Result |
|---|---|
| `node --check EMR4 Sidebar/src/taskpane/taskpane.js` | OK |
| `git diff --check` | Clean (no whitespace errors) |
| `sync_taskpane.py` patch parity | Preserved (BACKEND_URL block unchanged) |
| Existing review suites | Not run (no Python/Playwright available in this shell) |

## Boundary Compliance

| Gate | Status |
|---|---|
| No backend/schema/migration changes | ✅ Compliant |
| No `docs/diary/` edits | ✅ Compliant (W2 boundary) |
| No provider/live-provider wiring | ✅ Compliant |
| No H15/H-series/trove material | ✅ Compliant |
| No memory/RAG/GraphRAG | ✅ Compliant |
| No terminal-status policy | ✅ Not touched |
| No docs/taskpane regeneration | ✅ Reserved for Sol integration |
| Existing test suites untouched | ✅ (new test file only) |

## Remaining Risks

1. **sync_taskpane.py cannot be run in this worktree** (no Python venv). Sol must run `python sync_taskpane.py` at integration time to copy source → `docs/taskpane/` and verify the patched output resolves correctly.
2. **Local diary hosting** (`run_dev.ps1` serving `docs/` on port 3000) is out of S8 scope per the parent plan (§12). If the dev server does not serve `docs/diary/`, the port-3000 resolution will produce a 404 until that is addressed.
3. **Playwright tests require `pip install playwright` and `playwright install chromium`** in the worktree's venv. These prerequisites must be satisfied before running the new test suite.
4. **Office dialog codes are advisory** — the actual Office Web behaviour may differ slightly from documented codes, particularly in Word Online vs Word Desktop. The generic fallback covers unhandled codes.

## Follow-up (captured per protocol)

Add a `deploy_taskpane.ps1` or integrate `sync_taskpane.py` + version-bump into a single command for the taskpane edit→deploy cycle (pre-existing friction, not S8-specific).

---

STATUS: complete
