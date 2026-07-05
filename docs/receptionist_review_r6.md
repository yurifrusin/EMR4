# Receptionist-Domain Safety & Test-Design Review: Sprint R6 Temporal Boundary

This document provides the independent receptionist-domain, clinical safety, and test-design review for **Sprint R6: Temporal Boundary Harness Follow-Up**. It classifies EMR4 Centaur's temporal-boundary validation policies, details the semantic rules separating hard blocks, user clarifications, and stale-session rollovers, and assesses the DeepSeek A1/latest-only fully-past edge case.

---

## 1. Executive Summary & Domain Invariants

In a general practice clinical environment, date and time validations are critical safety boundaries. Booking appointments on dates or times that have already elapsed introduces major clinical risks (e.g., retrospective entry errors, auditing anomalies, billing compliance issues under the General Medical Services Table).

In EMR4 Centaur, Bernie (the clinical assistant) must enforce these boundaries using clear, receptionist-safe semantics. We distinguish between:
1. **Absolute Past Dates**: Strictly blocking historical bookings.
2. **Same-Day Bounded Windows**: Clamping or clarifying same-day requests where time is passing dynamically.
3. **Session Freshness**: Managing stale-session states across date boundaries or concurrent edits.

This review verifies that the pure temporal logic consolidation in `app/services/diary/temporal.py` is a solid foundation, identifies a route-level gap (the **DeepSeek A1 Edge Case**) in the interpret route, and provides deterministic testing recommendations.

---

## 2. Classification of Temporal Policies by Safety & Domain Value

Below is the receptionist-domain priority ranking and executable readiness classification for EMR4's temporal boundary scenarios.

| Policy / Scenario | Semantic Category | Safety Value | Expected Behaviour | Replay Harness / Test Readiness |
|---|---|---|---|---|
| **Absolute Past Date**<br>(e.g. `date_from < reference_date`) | hard_block | **High**<br>Prevents incorrect historical bookings, billing fraud, and audit log corruption. | **Hard Block**:<br>Rejects proposal and prevents slot search entirely. Emits `requested_date_in_past`. | **High**:<br>Stateless evaluation. Already promoted to executable in Sprint R5. |
| **Stale Reference Date**<br>(e.g. session `reference_date < clinic_today` at confirmation) | stale_session | **High**<br>Prevents confirming bookings across date-rollover boundaries (e.g. waking tab up next day). | **Session Refresh**:<br>Blocks mutation, forcing the client to reload and sync with "today". | **Medium**:<br>Requires mocking the system clock or database state injection. |
| **Stale Session Revision**<br>(e.g. `expected_revision` mismatch) | stale_session | **High**<br>Prevents double-booking or overwriting concurrent updates from other staff. | **Hard Block**:<br>Aborts write and returns `409 Conflict` (`stale_session_revision`). | **Medium**:<br>Requires multi-client simulation or DB revision intercept. |
| **Same-Day Bounded (Partly-Past)**<br>(e.g. `earliest_time < now < latest_time`) | clamp_earliest | **Medium**<br>Prevents offering slots that have already passed today while keeping upcoming slots available. | **Clamping**:<br>Clamps the search parameter `earliest_time` to clinic `now` and proceeds with slot search. | **Medium**:<br>Requires clinic clock mocking. |
| **Same-Day Bounded (Fully-Past)**<br>(e.g. `latest_time <= now`) | window_fully_past | **Medium**<br>Prevents empty slot queries and receptionist cognitive load when requested time is elapsed. | **Clarification**:<br>Prompts receptionist for a later time today or different day. Blocks slot search. | **Medium**:<br>Requires clinic clock mocking. |
| **DeepSeek A1 (Latest-Only Fully-Past)**<br>(e.g. `earliest_time is None`, `latest_time <= now`) | window_fully_past | **Medium**<br>Ensures consistent copilot guidance when user only specifies a past upper-bound time. | **Clarification**:<br>Must block search and prompt for clarification. (Currently broken in interpret route). | **Medium**:<br>Requires clinic clock mocking. |

---

## 3. Hard Block vs. Clarification vs. Stale-Session Handling

Understanding the distinct semantic rules prevents introducing UX or clinical friction:

### A. Hard Block Semantics
* **When**: Used for absolute past dates (`date_from` in the past relative to session reference date).
* **Action**: Fail-closed immediately. Do **not** execute slot searches, do **not** query databases, and do **not** display empty diary cards.
* **Staff Copy**: Rejection must be explicit, professional, and clear: *"New appointments cannot be booked in the past. Please request today or a future date."*

### B. Soft Clarification Semantics
* **When**: Used for same-day requests where the window is fully or partly past.
* **Action**: Same-day requests are dynamic. A fully-past window today should not trigger a permanent hard-block rejection of the conversation. Instead, it must trigger a **Clarification Path**, asking the receptionist to prompt the patient for a later time today or another day. A partly-past window must automatically **clamp** the earliest search bound to clinic-local "now" to keep search execution efficient.
* **Staff Copy**: *"That time has already passed today — would you like a later time or another day?"*

### C. Stale-Session Rollover Semantics
* **When**: Browser hibernation/date rollover or database revision mismatches.
* **Action**: This is a state-integrity issue, not a patient-intent error. Do **not** treat it as `requested_date_in_past`. Instead, the system must trigger a rollover event, prompting the receptionist to refresh the workspace. Any confirmation must be blocked until the session is re-synchronized.

---

## 4. Assessment of the DeepSeek A1 (Latest-Only Fully-Past) Edge Case

### The Bug Description
During static analysis of the same-day clamping logic in `app/routers/appointments.py`, a route-level discrepancy was identified.

In the **supervised booking route**, the same-day window is evaluated and the route correctly short-circuits:
```python
# app/routers/appointments.py L5734
if same_day_decision.kind == "window_fully_past":
    # Correctly records clinic_day_exhausted and returns block outcome
```

However, in the **interpret route** (which computes the conversational copilot's confidence bands/UI card outputs), the guard is over-constrained:
```python
# app/routers/appointments.py L3718
if (
    same_day_decision.kind == "window_fully_past"
    and _earliest is not None
    and _latest is not None
):
    temporal_band = "ask"
```

### Clinical Safety & UX Impact
If a receptionist says *"Book today before 10 AM"* at 10:30 AM (meaning `_earliest` is `None` but `_latest` is `10:00`):
1. `evaluate_same_day_window()` correctly returns `SameDayWindowDecision(kind="window_fully_past")`.
2. The interpret route (line 3718) bypasses the `if` block because `_earliest` is `None`.
3. The interpret route proceeds with `temporal_band = "proceed_with_check"` or `"assume"`, telling the staff UI that the request is valid.
4. When the receptionist clicks "Book", the supervised route executes, evaluates line 5734, and hard blocks the request with `clinic_day_exhausted`.

This results in a **disjointed user experience**: the AI copilot chat says "Proceed to confirm", but clicking the button immediately triggers a block.

### Proposed Code Correction
The interpret route check must match the supervised check by relaxing the `_earliest` requirement:
```diff
         if (
             same_day_decision.kind == "window_fully_past"
-            and _earliest is not None
-            and _latest is not None
+            and (_latest is not None)
         ):
             temporal_band = "ask"
```
*Note: Since `window_fully_past` is only returned by `evaluate_same_day_window` when `latest_time is not None` (line 182), checking `_latest is not None` is sufficient and catches both bounded and latest-only windows.*

---

## 5. Recommendations for Deterministic Testing

To guarantee the reliability of Bernie's temporal policies without depending on the live system clock, EMR4 must implement two distinct testing patterns.

### A. Router-Level Mocking (Unit & Integration Tests)
Use `monkeypatch` in pytest suites to isolate the router from the operating system clock.

1. **Test A1 (Latest-Only Fully-Past)**:
   * **Setup**: Mock `_clinic_local_now` to `2026-07-05 10:30:00`.
   * **Input**: Request `date_from="2026-07-05"`, `latest_time="10:00"`, `earliest_time=None`.
   * **Assert**: `temporal_axis.band == "ask"` (interpret endpoint) and `status == "clinic_day_exhausted"` (supervised endpoint).
2. **Test Partly-Past Clamping (Open-Ended)**:
   * **Setup**: Mock `_clinic_local_now` to `2026-07-05 10:15:00`.
   * **Input**: Request `date_from="2026-07-05"`, `earliest_time="09:00"`, `latest_time=None`.
   * **Assert**: `command_values.earliest_time == "10:15"` and basis matches open-ended clamp description.
3. **Test Exact Boundary (Now)**:
   * **Setup**: Mock `_clinic_local_now` to `2026-07-05 10:15:00`.
   * **Input**: Request `date_from="2026-07-05"`, `earliest_time="10:15"`, `latest_time=None`.
   * **Assert**: `temporal_axis.band == "ok"`.

### B. Replay Harness Clock Injection (Declarative Scenarios)
To enable YAML-based scenario replays (`same_day_past_window_clarify.yaml`) to run deterministically on CI, the EMR4 API should support header-based time mocking in development environments.

1. **Implement Middleware**:
   Add dev-only middleware in the FastAPI app that checks for an `X-Clinic-Simulated-Now` header. If present, override `_clinic_local_now()` with the header value.
2. **Scenario YAML Syntax**:
   Extend the replay harness schema to support setting headers:
   ```yaml
   - turn: 1
     action: normalize
     headers:
       X-Clinic-Simulated-Now: "2026-07-05T15:00:00+10:00"
     input:
       instruction: "Book today before 2 PM"
       reference_date: "2026-07-05"
     expect:
       outcome: clarification_required
       reason_codes: ["window_fully_past"]
   ```

Using this approach, all 16 natural-language corpus fixtures can gradually be converted to fully executable integration tests.
