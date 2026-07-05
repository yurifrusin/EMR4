# Receptionist-Domain Acceptance Review: Sprint R3 Stale-Session/Revision Hardening

This document provides the independent receptionist-domain and test-design review for **Sprint R3 Stale-Session/Revision Hardening**. It critiques the scenario fixtures, evaluates semantic boundaries, highlights workflow risks, and records domain dissent for concurrent operations and reload logic in EMR4 Centaur.

---

## 1. Executive Summary & Verification Outcomes

Sprint R3 introduces robust stale-session prevention and session-revision protection to ensure GP receptionists do not overwrite each other's work or resurrect outdated contexts when refreshing their browsers.

As the Gemini domain/test-design reviewer, I have:
1. **Analyzed the R3 stale-session corpus** for domain completeness, clinical safety, and UX ergonomics.
2. **Authored three new scenario fixtures** under [tests/fixtures/bernie_scenarios/](tests/fixtures/bernie_scenarios/):
   - `stale_session_concurrency_conflict.yaml` (two receptionists writing concurrently)
   - `stale_session_reload_blocking.yaml` (stale browser tabs/refreshes blocking mutations)
   - `stale_session_correction_and_pivot.yaml` (correction overriding constraints and discarding aborted contexts during pivot)
3. **Validated fixture integrity** using the project's test suite (`pytest tests/test_bernie_scenario_integrity.py`), confirming that all new scenario fixtures conform to EMR4's structural rules.

---

## 2. Review of R3 Core Semantic Goals

### A. Concurrency Protection (Two Receptionists)
* **Goal**: Prevent two receptionists updating the same diary session simultaneously from creating overlapping or duplicate mutations.
* **Domain Context**: In a busy general practice, multiple receptionists coordinate appointments on the same day. If receptionist A modifies a slot while receptionist B is viewing a stale state, receptionist B's subsequent append command must be rejected.
* **Semantic Rule**: Every mutation request from the clientpane must include the client-visible `expected_revision` coordinate. The server checks this coordinate against the current session `revision` in PostgreSQL. If they do not match, the server aborts the transaction, returns `409 Conflict`, and includes the error code `stale_session_revision`.
* **UX/Behavioral Invariant**: The client-side taskpane must not crash or display raw database errors. It must present a friendly reload indicator (e.g. "Diary updated by another staff member. Please click to refresh.") without losing the user's unsaved text inputs where recoverable.

### B. Stale Browser Tabs & Reload Logic
* **Goal**: Gracefully handle page reloads, tab suspensions, and network reconnections without executing stale commands.
* **Domain Context**: Web applications often suffer from silent tab reload/hibernation under chromium memory managers. When the tab wakes up, resurrecting the last-sent message or auto-confirming a pending proposal represents a major clinical safety risk (e.g., booking on the wrong day due to shifted dates).
* **Semantic Rule**: Browser reload or initialization must check the session freshness token and reference date. If the reference date is stale, the session is marked `stale: true`. Any further mutation attempts block, returning `context_reference_date_stale`.
* **UX/Behavioral Invariant**: Stale sessions should fail-closed. The command interface must clear the transient memory of the last typed instruction, prevent the execution of outdated visual cards, and redirect the user back to the active diary view.

### C. Correction-vs-Clarification Merge Semantics
* **Goal**: If a receptionist provides new input that corrects an already resolved constraint (rather than merely filling a missing one), the merge logic must overwrite the old constraint with the new explicit value while leaving other unrelated resolved constraints intact.
* **Domain Context**: If the user books next Tuesday and gets a clarification prompt for the practitioner, but responds with *"Actually, Dr Shera next Wednesday"*, they are performing both a correction (date: Tuesday $\to$ Wednesday) and a clarification (practitioner: Dr Shera).
* **Semantic Rule**: An explicit value for a resolved field in a clarification turn overrides the old constraint. A field that is not mentioned in the clarification turn preserves its resolved constraint.
* **UX/Behavioral Invariant**: The receptionist should not have to re-key unchanged details. Overwriting the entire context frame and wiping unrelated inputs violates the pacing expectations of experienced medical receptionists.

### D. Intent Switches and Context Pivoting
* **Goal**: When a receptionist changes intent mid-conversation (e.g. pivoting from booking a new slot to extending an existing appointment), the system must discard all transient booking parameters immediately.
* **Domain Context**: If the user begins booking for next week, but mid-turn says *"Actually, let's just extend Margaret's 10:00 appointment today by 15 minutes"*, the future date and other booking-specific parameters must be completely discarded to prevent stale date leakage into the extension proposal.
* **Semantic Rule**: Detecting a command category pivot (e.g., from `booking` to `extend`) triggers a frame purge. The system cleanses all booking-specific parameters, loads the correct target appointment context, and resets the target coordinates.
* **UX/Behavioral Invariant**: The proposed outcome card must match the new intent exactly. Displaying residual parameters from the aborted booking frame (e.g., showing a duration extension with the date of next week) is a critical cognitive hazard.

### E. Safe Failure copy and Clinical Safety
* **Goal**: When a session is rejected or blocked, the copy shown to the user must be clear, professional, and action-oriented.
* **Domain Context**: Medical environments require absolute clarity. Ambiguous messages like "Error 500" or "Operation failed" lead to clinical uncertainty (e.g., "Is the patient booked or not?").
* **Semantic Rule**: Under no circumstances should the backend write an unconfirmed proposal to the database when a conflict occurs. Clinical safety mandates a strict "fail-closed" posture.
* **UX/Behavioral Invariant**: Error notifications must clearly distinguish between a concurrency conflict ("Another staff member has updated this view") and a stale session ("Session expired due to inactivity"). They must provide a single-click action to synchronize the display.

---

## 3. Detailed Fixture Critique & Coverage Analysis

The scenario corpus verified in this sprint locks down these behavioral expectations:

| Fixture File | Target Invariant | Receptionist Workflow Importance | Status / Integrity |
|---|---|---|---|
| [`stale_session_concurrency_conflict.yaml`](tests/fixtures/bernie_scenarios/stale_session_concurrency_conflict.yaml) | Revision verification (`409 Conflict`) | Prevents double-booking and concurrent mutation race conditions. | **Passes integrity check** (New) |
| [`stale_session_reload_blocking.yaml`](tests/fixtures/bernie_scenarios/stale_session_reload_blocking.yaml) | Session stale flag block | Prevents browser tab wakeup from resurrecting old context. | **Passes integrity check** (New) |
| [`stale_session_correction_and_pivot.yaml`](tests/fixtures/bernie_scenarios/stale_session_correction_and_pivot.yaml) | Override & frame pivot | Preserves selective merges during correction while purging booking data. | **Passes integrity check** (New) |
| [`refresh_does_not_resurrect_stale_latest_message.yaml`](tests/fixtures/bernie_scenarios/refresh_does_not_resurrect_stale_latest_message.yaml) | Reference date staleness | Prevents reloading from executing commands against the wrong date. | **Passes integrity check** (Existing) |
| [`booking_to_extension_switch_during_clarification.yaml`](tests/fixtures/bernie_scenarios/booking_to_extension_switch_during_clarification.yaml) | Category pivot parameters | Ensures context switches purge transient parameters cleanly. | **Passes integrity check** (Existing) |

---

## 4. Dissent & Structural Risks (Independent Critique)

As the domain reviewer, I raise the following concerns regarding the proposed R3 implementation boundary:

### Risk 1: The "Soft Reload" Loop Trap
* **Concern**: When a receptionist experiences a concurrency conflict (`stale_session_revision`), triggering a hard reload might discard all their typed context, forcing them to re-interview the patient.
* **Dissent**: While clinical safety mandates blocking the mutation, a "soft reload" that fetches the new server state, updates the background revision coordinate, and *re-evaluates* the receptionist's current input text against the new state is highly preferable to wiping the input frame.
* **Recommendation**: Implement client-side transaction buffering. If a conflict occurs, preserve the user's latest typed command string, prompt the refresh, and re-submit the command string against the fresh state automatically.

### Risk 2: Transient State Leakage via WebSockets
* **Concern**: If the client relies on long-running WebSocket sessions to sync diary updates, revision drifts might bypass HTTP route checks if not actively monitored.
* **Dissent**: Websocket state updates and REST mutations must share a single atomic revision counter. If a WebSocket message indicates a server mutation has occurred, the client must immediately increment its local revision sequence or mark its pending UI proposals as dirty to prevent stale clicks.
* **Recommendation**: Enforce revision checks inside WebSocket message payloads. Every client-bound event must broadcast the current transaction revision.

---

## 5. Acceptance Checklist for Implementation

Before the R3 implementation branch is merged, the orchestrator must verify:
- [ ] **Stale Rejection**: An append request containing a mismatched `expected_revision` fails with HTTP 409 and returning `"code": "stale_session_revision"`.
- [ ] **Reload Block**: Reloading a browser tab with a stale reference date triggers `context_reference_date_stale` and blocks subsequent confirm commands.
- [ ] **Frame Purge**: Pivoting from booking to extension purges all transient parameters (such as booking date, practitioner, etc.), matching the behavior defined in `stale_session_correction_and_pivot.yaml`.
- [ ] **Correction Override**: Clarification turns containing explicit corrections for resolved fields correctly overwrite old constraints rather than appending them or failing.
- [ ] **UX Fail-Safe**: Error alerts for `stale_session_revision` display professional copy instructing the receptionist to refresh, without crashing the sidebar runtime.

