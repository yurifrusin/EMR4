# Receptionist-Domain Acceptance Review: Sprint R2 Clarification Merge Semantics

This document provides the independent receptionist-domain and test-design review for **Sprint R2 Clarification Merge Semantics**. It critiques the scenario fixtures, evaluates semantic boundaries, highlights workflow risks, and records domain dissent.

---

## 1. Executive Summary & Verification Outcomes

Sprint R2 introduces selective clarification merge semantics to ensure that when a receptionist is prompted to fill missing fields, the system merges new inputs without losing already-resolved fields (e.g. patient identity, doctor, date, or time). 

As the Gemini domain/test-design reviewer, I have:
1. **Reviewed the R1 scenario corpus** for domain coverage and semantic correctness.
2. **Added a new scenario fixture** (`booking_to_extension_switch_during_clarification.yaml`) to verify that the system correctly discards booking context and shifts to extension context when the user switches intent mid-turn.
3. **Validated fixture integrity** using the project's test suite, confirming all scenario fixtures parse successfully.

---

## 2. Review of R2 Core Semantic Goals

### A. Preservation of Resolved Fields (No Re-Asking)
* **Goal**: If the user has resolved fields like patient ("Margaret Thompson"), date ("2026-07-14"), and time ("15:30"), and is only missing "practitioner", clarifying the practitioner must *preserve* all other fields.
* **Critique**: The R1 fixtures `booking_clarify_long_duration_preserves_patient_date_time.yaml` and `booking_clarify_long_duration_preserves_practitioner.yaml` successfully assert this. The backend must selectively update *only* the targeted missing fields. Overwriting the entire context frame on a clarification turn represents a critical workflow failure that frustrates receptionist pacing.
* **Verification Criterion**: The selective merge algorithm must perform a field-by-field merge of constraints, prioritizing the newly parsed values for the missing fields while keeping all other non-conflicting constraints unchanged.

### B. Distinguishing Extension-vs-Booking Clarification
* **Goal**: The system must differentiate between a turn that clarifies a *new booking* constraint (e.g. adding a duration to a booking request) and a turn that clarifies an *appointment extension* or update (e.g. changing an existing appointment from 15 to 45 minutes).
* **Critique**: In GP workflows, receptionists often shift context dynamically. If a patient already has a booked slot, saying "make it a long appointment" should resolve to an extension/update proposal rather than spawning a new booking. 
* **Hardening**: I authored `booking_to_extension_switch_during_clarification.yaml`. If the receptionist starts by booking a slot, is asked for a practitioner, and replies *"Actually, extend her 10:00 appointment today by 15 minutes instead"*, the merge semantics must detect the intent switch:
  - Discard the transient booking context.
  - Identify the target appointment `apt_1` from the seeded state.
  - Pivot the outcome to `confirmation_ready` for an `extend` action with `duration_minutes: 30`.
  - Discard the future date `2026-07-14` (preventing stale date leakage).

### C. Avoidance of Stale-Session Resurrection
* **Goal**: Prevent the resurrection of obsolete or stale context when a session is updated or refreshed.
* **Critique**: `refresh_does_not_resurrect_stale_latest_message.yaml` ensures that refreshing a stale view blocks confirmations and flags `context_reference_date_stale`. Selective merges must check session freshness first. If the session state has been invalidated by diary navigation, any subsequent merge command must fail-closed with `409 Conflict` (e.g. `stale_session_revision` or `stale_create_proposal_freshness_id`) rather than blending stale constraints with new inputs.

---

## 3. Detailed Fixture Critique & Coverage Analysis

The table below outlines how the scenario corpus locks down these behaviors:

| Fixture File | Target Invariant | Receptionist Workflow Importance | Status / Integrity |
|---|---|---|---|
| `clarification_reply_merges_missing_field_only.yaml` | Basic merge safety | Ensures basic multi-turn conversation memory works. | **Passes integrity check** (xfail holds bug reason) |
| `booking_clarify_long_duration_preserves_patient_date_time.yaml` | Patient & Time persistence | Prevents losing identity/time when clarifying custom duration. | **Passes integrity check** (xfail holds bug reason) |
| `booking_clarify_long_duration_preserves_practitioner.yaml` | Practitioner persistence | Prevents losing practitioner context when clarifying duration. | **Passes integrity check** (xfail holds bug reason) |
| `booking_to_extension_switch_during_clarification.yaml` | Context reset on intent shift | Discards pending booking frame if receptionist switches to extension mid-stream. | **Passes integrity check** (newly added) |
| `refresh_does_not_resurrect_stale_latest_message.yaml` | Stale session protection | Prevents stale context from resurrecting during browser reload. | **Passes integrity check** |

---

## 4. Dissent & Structural Risks (Independent Critique)

As the domain reviewer, I raise the following concerns and recommendations regarding the proposed R2 implementation boundary:

### Risk 1: Correction vs. Clarification Ambiguity
* **Concern**: When a receptionist provides a clarification turn, the language may look like a correction (e.g., user says *"Book Margaret next Tuesday"* -> missing practitioner -> user says *"Actually, Dr Shera next Wednesday"*). Here, the user is filling the missing practitioner *and* correcting the date. 
* **Dissent**: A strict "selective merge only for missing fields" algorithm might merge "Dr Shera" but refuse or ignore "next Wednesday" if the date constraint was already marked resolved. 
* **Recommendation**: The merge semantics must not treat resolved fields as immutable during clarification turns. If a turn explicitly specifies a new value for a resolved field, it must override the old constraint, whereas if it is silent on a resolved field, that field is preserved.

### Risk 2: Default Duration Overwriting
* **Concern**: During a booking request, duration often defaults to 15 minutes if not specified. If the user clarifies with *"It's a long appointment"*, the system must update `duration_minutes` to 30.
* **Dissent**: If the default 15 minutes is treated as a "resolved" field, a naive merge logic might refuse to overwrite it or complain that the field wasn't "missing". 
* **Recommendation**: Distinguish between *explicitly resolved* fields and *default-filled* fields in the request frame. Default-filled fields must always yield to explicit clarification inputs.

### Risk 3: Concurrency and Race Conditions
* **Concern**: If two receptionists are viewing the same diary day and making changes, one receptionist's clarification reply could post against a state that was just mutated by another receptionist.
* **Dissent**: Merging must occur on the server side using the session event log. The client should never send a merged state; it should send only the raw turn event, letting the server apply the merge logic deterministically based on the sequence of events.
* **Recommendation**: Fully enforce the session revision coordinates (`revision` check) on all `/appointments/proposals/bernie/session/append` routes. Reject any merge attempts that have stale revision headers.

---

## 5. Acceptance Checklist for Claude's Implementation

Before Claude's backend implementation is merged, the orchestrator should verify:
- [ ] **Preservation**: Replaying `clarification_reply_merges_missing_field_only.yaml` passes successfully (xfail removed).
- [ ] **No Regression**: All other R1/R2 test scenarios under `tests/fixtures/bernie_scenarios` parse and run, demonstrating that existing slot validation and confirmation gates remain intact.
- [ ] **Intent Switch**: The new `booking_to_extension_switch_during_clarification.yaml` passes, confirming that the backend discards stale temporal fields when pivoting to an extension request.
- [ ] **HTTP Errors**: Appending a clarification turn to a session with a mismatched `revision` returns a `409 Conflict` response containing `stale_session_revision`.
