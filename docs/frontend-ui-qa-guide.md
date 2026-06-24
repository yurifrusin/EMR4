# EMR4 Frontend UI QA Developer Guide

This guide explains how to programmatically verify and smoke-test the EMR4 Diary and Taskpane frontend assets to prevent cache-busters and visual/state regressions from landing on production.

---

## 1. Automated Assets & Cache Validation

### A. Run Version Checker
To verify that all local modifications to CSS/JS files have their cache-buster parameters (`?v=N`) correctly incremented inside referencing HTML pages:

```powershell
python scripts/check_frontend_versions.py
```

### B. Validation Logic
The script compares files in the working directory against `HEAD` and checks:
1. If `diary.js`, `diary.css`, `taskpane.js`, `taskpane.css`, or `command-centre.js` are modified.
2. If modified, it checks whether the referencing HTML files (`diary.html`, `taskpane.html`, `command-centre.html`) have updated version parameters compared to their `HEAD` versions.
3. If an asset is modified but the HTML version query parameter is identical to `HEAD`, the script fails with exit code `1` to block the commit.

---

## 2. Visual QA Smoke-Test Protocol

Always verify UI alterations using **Smoke Mode** (`?smoke=true`) to isolate layout inspections from backend API and auth dependencies.

### A. Testing URLs
- Deployed Smoke Diary: `https://yurifrusin.github.io/EMR4/diary/diary.html?smoke=true`
- Local Smoke Diary: Open `docs/diary/diary.html?smoke=true` directly in the browser.
- Deployed Taskpane (static review): `https://yurifrusin.github.io/EMR4/taskpane/taskpane.html`

### B. High-Risk Visual Areas to Inspect
1. **Diary Column Alignment**: Confirm rooms (practitioners) column headers stack properly above the time intervals without wrapping or offset.
2. **Waiting Room Sidebar**: Ensure cards do not clip and sidebar stack counts are aligned.
3. **Modal Dialogs**: Open the booking modal and the settings gear panel. Verify forms render clearly, buttons are clickable, and backdrop blur does not block modal content.
4. **Responsive Layouts**: Resize the window to narrow layout (<700px). Verify that panels dynamically collapse or align to single-column without breaking headers.

---

## 3. Console Assertions & State Checks

Use Chrome DevTools Console to programmatically assert frontend state controls.

### A. Taskpane Sandbox & Lock Assertions
To check the locks of the clinical command center, target the taskpane frame target in DevTools and run:

1. **Verify Lock Control Function Exists**:
   ```javascript
   typeof setTaskpaneLocked === 'function' ? "✓ Pass" : "❌ Fail: setTaskpaneLocked is missing!"
   ```

2. **Trigger Lock and Assert Element Attributes**:
   ```javascript
   setTaskpaneLocked(true);
   const inputs = [...document.querySelectorAll('input, select, textarea, button')];
   const unLocked = inputs.filter(el => !el.disabled && !el.id.includes('btn-unlock'));
   unLocked.length === 0 ? "✓ Pass: Taskpane locked!" : `❌ Fail: ${unLocked.length} elements remained active.`;
   ```

3. **Verify Consultation State Gating**:
   ```javascript
   console.log("Consultation Active:", consultStarted);
   ```

### B. Deployed Asset Delivery Checks
To confirm GitHub Pages is serving the correct cached reference:

```javascript
fetch("https://yurifrusin.github.io/EMR4/diary/diary.html?probe=" + Date.now(), { cache: "no-store" })
  .then(r => r.text())
  .then(t => console.log("Live Diary Script Reference:", t.match(/diary\.js\?v=\d+/)?.[0]))
```
