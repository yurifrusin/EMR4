# S5 Usability Review — Receptionist Workflow Critique
**Lane:** A-1 (Usability Veto)  
**Assigned Agent:** Antigravity (Gemini 3.5 Flash / Medium)  
**Date:** 2026-07-12  

---

## 1. Executive Summary & Verdict

### Verdict: **Conditional Go**

The EMR4 Centaur Diary Grid and Taskpane workflow provides a highly functional, visually structured, and modern diary experience. The columns (rooms) and rows (time slots) are logically laid out, and the lifecycle status colors are easily distinguishable. However, the system is **not ready for production receptionist use** without addressing several critical usability blockers and technical oversights detailed below. 

### Core Conditions for Production Release:
1. **Fix Grid Auto-Refresh Behavior:** Stop the silent refresh from destroying and rebuilding the entire grid DOM, which clears active editing selections (`.appt-active`) and open dropdowns.
2. **Resolve Hardcoded Dev/Production Split:** The `DIARY_URL` in the taskpane must be dynamically routed rather than hardcoded to a GitHub Pages remote host, which breaks local developer environments.
3. **Streamline Popup Dialogs:** Address popup blocker prompts in Word Online caused by `displayDialogAsync`.

---

## 2. Tested vs. Static Limitations

To ensure a robust evaluation, this review distinguishes between findings observed dynamically (tested) and architectural constraints identified in the source files (static).

### Tested Limitations (Dynamic Verification)
* **Playwright Test Suite Failures:** 
  Running `pytest review/test_diary_smoke.py` revealed **8 test failures out of 139 checks**. These failures are caused by two issues in the test harness setup:
  1. **GraphQL vs. REST Drift:** The tests mock the REST `/practice/practitioners` endpoint. However, since the client has transitioned to GraphQL (`ENABLE_GRAPHQL_PRACTITIONERS = true`), the client queries `/graphql` instead, which is not mocked in the tests.
  2. **Smoke Mode Network Bypass:** The tests run with `?smoke=true` in the URL but assert that network requests are made to `/appointments/proposals/update/...` and `/confirm`. In `smoke=true` mode, `diary.js` simulates proposal validation and confirmation locally, bypassing the API endpoints entirely and causing assertions on captured requests to fail.
* **Status Transitions:** Verified that status transitions on the grid and within the flow panel correctly update patient lifecycle statuses (e.g., Booked → Arrived → In Consult → Completed).

### Static Limitations (Codebase Analysis)
* **Hardcoded Remote URL:** Statically verified that `DIARY_URL` is a hardcoded constant in [taskpane.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/EMR4%20Sidebar/src/taskpane/taskpane.js#L1020) pointing to GitHub Pages, bypassing the local dev server.
* **Hidden Date Picker:** Statically verified that `#diary-date-picker` is hidden via CSS (`opacity: 0; pointer-events: none`) in [diary.css](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.css#L175-L181) and relies on `showPicker()`, which is unsupported in several embedded webview runtimes.
* **Destructive Refresh:** Statically verified that `loadDiary` clears and rebuilds the grid inner HTML (`grid.innerHTML = ""`) in [diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js#L3520) every 60 seconds.

---

## 3. Ranked Usability Findings

Findings are ranked by their impact on a clinical practice receptionist's daily workflow.

### [Go Blocker] Grid Background Auto-Refresh Clears User Selection
* **Impact:** Every 60 seconds, the grid triggers a background reload (`loadDiary(true)`) which rebuilds the DOM. If a receptionist has clicked an appointment to make it active (`.appt-active`) and is about to edit it or change its status, the active selection is wiped out, and the inline status changer/edit buttons disappear.
* **Recommendation:** Perform a diff-based DOM update or preserve the ID of the active appointment across reloads, reapplying the `.appt-active` class and restoring inline dropdown states.

### [High] Hardcoded Remote URL in Taskpane
* **Impact:** `DIARY_URL` is hardcoded to `https://yurifrusin.github.io/EMR4/diary/diary.html` in `taskpane.js`. When developers or clinics test the EMR4 stack locally, clicking the `📅` Diary button opens the production GitHub Pages frontend rather than the local dev copy.
* **Recommendation:** Dynamically set `DIARY_URL` based on the current `window.location.origin` or port, similar to `BACKEND_URL`.

### [High] Word Online Popup Dialog Blocking
* **Impact:** The `openDiary` button uses `Office.context.ui.displayDialogAsync`. In web-based environments (Word Online), this triggers browser popup blockers or demands explicit user consent to open the window, creating clinical friction.
* **Recommendation:** Provide clear visual instructions on the taskpane explaining how to enable popups if the dialog fails to load, and ensure status messages are highly visible (e.g., using toast notifications instead of small status text).

### [High] Multi-Step Booking Cancellation / DNA Validation Friction
* **Impact:** Changing an appointment status to `Cancelled`, `NoShow`, or `DNA` requires selecting an administrative reason code. However, the reason code select dropdown is hidden by default and only shown after the status changes. If the user clicks "Save" without selecting a reason, the modal throws an error on save.
* **Recommendation:** Keep the reason code selection container visible and highlighted immediately when a cancellation status is selected, guiding the receptionist before they hit "Save".

### [Medium] Date Picker Webview Compatibility
* **Impact:** The date navigation calendar button triggers the hidden input (`#diary-date-picker`) using `showPicker()`. Many embedded Office JS webview controls do not support `showPicker()`, rendering the date selection calendar button non-functional.
* **Recommendation:** Fall back to a custom lightweight JavaScript date-picker modal if `showPicker()` is unsupported, rather than relying on native invisible inputs.

### [Medium] Lack of Grid Search / Filtering
* **Impact:** There is no local search box on the diary grid. To find if a patient is booked today, the receptionist must manually scroll or use the global patient search on the taskpane (which queries the entire database).
* **Recommendation:** Add a simple text input at the top of the grid to filter and highlight matching appointments in real time.

### [Medium] Note Access Requires Opening Modal
* **Impact:** Appointment reasons and notes are hidden or truncated on the appointment cards unless the card height is large enough. Receptionists must open the full edit modal just to read a brief message or note left for the doctor.
* **Recommendation:** Implement a custom hover card (tooltip) that displays the full appointment details, patient DOB, Medicare link status, and notes without opening the modal.

### [Low] Icon-Only Taskpane Button
* **Impact:** The `📅` button in the taskpane banner is small and icon-only. It may not be immediately clear to new receptionists that this launches the main diary screen.
* **Recommendation:** Add a short text label or distinct onboarding tooltip.

---

## 4. Compliance Declarations

### Code Modification Statement
No code modifications, file edits, or test script adjustments were made to the project repository during this review. This is a read-only usability veto lane (A-1).

### Data Privacy & PHI Statement
No Protected Health Information (PHI) or files from `local_data` (including the historical diary trove) were reviewed, accessed, or transmitted during this usability review. All evaluations were conducted using mock data and local development schemas.

---

**STATUS: complete**
