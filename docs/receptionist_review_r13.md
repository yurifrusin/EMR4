# Sprint R13 — Receptionist Domain Review: Diary Smoke Harness Recovery

This domain review evaluates the 12 Bernie session/pilot full-smoke failures from a receptionist workflow and UI-semantics perspective. It confirms that the failures represent harness auth-token drift rather than a regression in production clinical workflows, and recommends acceptance checks to prevent future auth regressions from masking real clinical UI errors.

## 1. Issue Classification and Diagnostic Overview

The 12 failures are classified as **Harness Auth-Token Drift**. There is **no receptionist workflow regression** in the production code. 

### Root Cause
The test harness in `review/test_diary_smoke.py` set a fake token (`ordinary-staff-token`) in `localStorage` to simulate logged-in sessions. When `docs/diary/diary.js` was updated in Sprint R12 to parse JWTs and clear invalid/expired tokens, this fake token (which is not a valid JWT containing three period-separated parts) was detected as invalid and immediately cleared. As a result, the UI operated as if unauthenticated.

### Affected Functional Areas

| Failure Mode | Failing Tests | Receptionist Impact | Harness Diagnosis |
| :--- | :--- | :--- | :--- |
| **A. Session append capture** | 3 tests (Active load, stale conflict, server session coordinates) | Server session initialization failed because the token was null, preventing `/api/v1/appointments/bernie/sessions/active` from being called. | **Harness setup error.** The UI correctly protected session endpoints by requiring valid auth, but the test supplied invalid auth. |
| **B. Grid/pilot not visible on non-smoke URLs** | 9 tests (Ordinary mode, imported context, instruction affordances, practitioner mismatches, candidate previews) | The main Diary grid and Bernie pilot panel failed to render because `loadDiary()` and `checkBerniePilotEligibility()` returned early upon detecting a null token. | **Harness setup error.** The tests timed out waiting for `#diary-grid` or pilot buttons, which were never rendered due to the missing token. |

---

## 2. Prevention & Acceptance Checks

To ensure that future harness/infrastructure fixes do not hide real regressions in receptionist workflows, we recommend the following clinical and technical acceptance checks:

### Visual & Behavioral Acceptance Checks
1. **Explicit Authentication Alerting:**
   Instead of failing silently by not rendering the diary grid or pilot controls when an auth token is invalid, the UI should render a clear, staff-facing notification (e.g., a "Session Expired - Please Log In Again" banner or redirect to a login card). This ensures that if auth fails in production, the receptionist is not left with a broken, blank diary page.
2. **Harness Boot Diagnostics:**
   Playwright smoke tests should explicitly verify authentication state at boot. If `localStorage` is cleared or is empty during a smoke test run, the harness should fail immediately with an authentication error, rather than timing out on subsequent selectors (like `#diary-grid` or `pilot-launch-button`).
3. **Console Log Interception:**
   Configure Playwright to fail the test run if warning/error logs related to authentication clearing (e.g., from `clearExpiredAuthToken()`) are emitted on the console, unless the test explicitly expects a logout scenario.

### Clinical Workflow Safeguards
- **Offline / Token-Expired Fallbacks:**
  Confirm that when a token does expire, any active draft appointment proposals or receptionist instructions in progress are not silently discarded, but are safely cached or the user is warned before losing their draft state.

---

## 3. Scope Verification
- **Touch Boundary:** Checked to ensure only `docs/receptionist_review_r13.md` is created. No production code, tests, or mock routes have been modified.
