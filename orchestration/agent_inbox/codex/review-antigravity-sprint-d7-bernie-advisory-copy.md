# Sprint D7: Bernie Diary UI Advisory Copy Review
**Agent:** Antigravity (Gemini 3.5 Flash)

---

## 1. Findings
- In [docs/diary/diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js#L1025-L1034), `bernieIssueDisplayText` hardcoded the display string for the `existing_future_follow_up` issue:
  ```javascript
  if (issue.code === "existing_future_follow_up") {
    return "Margaret already has another appointment in the diary. It is worth checking that an extra booking is intended.";
  }
  ```
- This completely overrides the dynamic, patient-specific (or generic) backend-authored message (`issue.message`) supplied by `app/services/bernie_patient_context.py` (which default-constructs as `"This patient already has an appointment on the requested day. Check whether a new booking is still needed."`).
- As a result, the UI displays "Margaret already has another appointment..." regardless of who the requested patient actually is.
- By updating `bernieIssueDisplayText` to return `issue.message || "This patient already has another appointment..."`, the UI correctly displays the backend-authored text while preserving a generic fallback when a backend message is missing.

---

## 2. Recommended Patch

### docs/diary/diary.js
```diff
--- docs/diary/diary.js
+++ docs/diary/diary.js
@@ -1025,3 +1025,3 @@
 function bernieIssueDisplayText(issue) {
   if (!issue) return "";
   if (issue.code === "existing_future_follow_up") {
-    return "Margaret already has another appointment in the diary. It is worth checking that an extra booking is intended.";
+    return issue.message || "This patient already has another appointment in the diary. It is worth checking that an extra booking is intended.";
   }
   if (issue.code === "no_practitioner_schedule") {
```

### review/test_diary_smoke.py
We updated the corresponding smoke test assertion to match the backend-supplied advisory message mock:
```diff
--- review/test_diary_smoke.py
+++ review/test_diary_smoke.py
@@ -6322,3 +6322,3 @@
         assert "Bernie found these times" not in panel_text
         assert "I could not find any free times for that request" not in panel_text
-        assert "Margaret already has another appointment in the diary" in panel_text
+        assert "This patient already has a future appointment booked. Check whether a new booking is still needed." in panel_text
         assert diary_page.locator("[data-testid='bernie-review-status']").text_content().strip() == "Try another time"
```

---

## 3. Verification
1. **JavaScript Syntax Check:** Ran `node --check docs/diary/diary.js` successfully (exit code 0).
2. **Deterministic Playwright Smoke Tests:** Ran `.venv\Scripts\pytest review/test_diary_smoke.py -q` which passes after applying the test assertion update (the old test assertion failed on the modified JS code, proving the test is sensitive and has been properly updated to verify correct rendering).

---

## 4. Risks
- **Low Risk:** The change only adjusts the rendering copy of a warning advisory on the client-side. No backend APIs, route logic, schemas, or database tables are modified.
- **Fallback safety:** If `issue.message` is null or undefined (e.g. legacy/mock payloads), it falls back to a clean, patient-agnostic warning message, preventing UI breakage or hardcoded patient confusion.
