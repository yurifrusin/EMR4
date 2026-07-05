# Receptionist-Domain Safety & Test-Design Review: Sprint R7 Raw Temporal Policy

This document provides the independent receptionist-domain, clinical safety, and test-design review for **Sprint R7: Raw Appointment Temporal Guard Hardening**. It analyzes the temporal safety profile of direct API mutation paths (create, update, status update, deletion), details the rules separating slots-consuming writes from status modifications, and outlines the implementation and testing blueprints for the raw paths under the Ariadne amendment.

---

## 1. Executive Summary & Domain Invariants

While Sprint R6 consolidated the pure temporal-policy engine for Bernie-guided conversational workflows, direct API endpoints remain vulnerable to out-of-order, historical, or retrospective scheduling writes. Direct API writes bypass Bernie’s conversational normalization, meaning they do not benefit from natural-language clarification dialogs. They must therefore enforce a strict fail-closed safety posture.

### The Ariadne Amendment
1. **Slots-Consuming Writes (Create/Update)**: Directly creating (`POST /appointments`) or updating (`PUT /appointments/{id}`) an appointment to a date/time that is already fully elapsed (either absolute past date or fully elapsed same-day time) represents a clinical and scheduling anomaly. These paths must **hard-block** by default unless an explicit administrative bypass or data-import override is designed.
2. **State-Only Mutations (Status/Delete)**: Modifying an appointment's status (`PATCH /appointments/{id}/status`) or deleting/cancelling an appointment (`DELETE /appointments/{id}`) do not allocate or create temporal slots. Therefore, they should be governed by separate operational/auditing policies and **must not be blocked** under appointment-date temporal write checks.

---

## 2. Classification of Raw API Temporal Policies by Safety & Domain Value

The table below outlines the safety classifications and expected behaviours for direct API actions:

| API Endpoint | Scenario / Condition | Semantic Category | Safety Value | Expected Guardrail Behaviour |
|---|---|---|---|---|
| **POST `/appointments`** | `appointment_date < clinic_today` | hard_block | **High** | Rejects write immediately; returns `420 Temporal Violation` or `422 Unprocessable Entity` with `date_in_past`. |
| **POST `/appointments`** | `appointment_date == clinic_today`<br>and `start_time_local < clinic_now_time` | hard_block | **High** | Rejects write immediately; returns `420 Temporal Violation` or `422 Unprocessable Entity` with `same_day_time_elapsed`. |
| **PUT `/appointments/{id}`** | Moving `appointment_date` or `start_time_local` to elapsed past | hard_block | **High** | Rejects write; returns conflict/temporal validation error. |
| **PATCH `/appointments/{id}/status`** | Updating status of an elapsed past appointment | permit_modification | **Medium (Separate Policy)** | Permitted. Allowing retrospective status changes (e.g. marking "No Show" or "Completed" retrospectively) is necessary for operational bookkeeping. |
| **DELETE `/appointments/{id}`** | Deleting/Cancelling an elapsed past appointment | permit_modification | **Medium (Separate Policy)** | Permitted. Deletion frees up slot capacity or cancels erroneous records. Enforcing temporal blocking would lead to dead database states. |
| **POST/PUT** (Override Mode) | Mutating with `admin_override: true` or bypass header | administrative_bypass | **Low (Explicit Use)** | Permitted. Bypasses temporal validations for batch data imports or senior administrative overrides (audited separately). |

---

## 3. Route-Class Segregation: Slots-Consuming vs. State-Only Writes

Direct API route design must respect the clinical and operational distinction between raw scheduling actions:

### A. Slots-Consuming Writes (Create & Update)
* **The Domain Risk**: Allowing general staff or raw API consumers to book past slots retrospectively introduces major clinical risks. It facilitates retrospective charting fraud, bypasses scheduling collision checks, and creates discrepancies in billing audits under the General Medical Services Table (GMST) rules in Australia.
* **Same-Day Temporal Exhaustion**: Unlike Bernie’s conversational flow which asks for clarification when a requested time has elapsed, the raw API has no dialogue interface. If a client attempts to post an appointment for 9:00 AM at 11:30 AM today, the API must fail-closed.
* **Bypass Design**: Retrospective entries (e.g., recording a walk-in emergency after-the-fact) are legitimate senior administrative actions. These must require an explicit administrative override payload parameter (e.g. `admin_override: bool = False`) or an API header (e.g. `X-EMR4-Admin-Bypass: True`). This ensures that bypass actions are intentional, restricted by role permissions, and distinctly flagged in the audit logs.

### B. State-Only Mutations (Status & Delete)
* **The Domain Risk of Blocking**: Status updates are inherently retrospective. A practitioner completes a consultation at 10:45 AM, and the receptionist changes the status to `Completed` at 11:15 AM. If status writes were subject to the same temporal blocking as create/update writes, updating past appointments would be impossible, locking the EMR into outdated states.
* **Deletion/Cancellation**: Deleting or cancelling past appointments is a corrective measure. Preventing cancellations on elapsed appointments would leave phantom occupied slots in the database, polluting operational reports.
* **Separate Governance**: Rather than applying raw temporal blocks, status updates and deletions must be handled by:
  1. Role-based access control (RBAC) ensuring only authorized staff can modify status or delete records.
  2. Extensive auditing (`AppointmentAuditLog`) tracking the exact user, status change, and timestamp.

---

## 4. Current Temporal Safety Gaps in `app/routers/appointments.py`

Reviewing the current implementation of direct mutation routes reveals that no temporal checks are currently enforced at the raw router level:

### A. Raw Create Route (`POST /appointments`)
* **Current Behaviour** (L983-L999):
  ```python
  @router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
  def create_appointment(body: AppointmentCreate, ...):
      ...
      return _create_appointment_from_body(...)
  ```
  `_create_appointment_from_body` performs basic relational checks (`_ensure_patient`, `_ensure_practitioner`, etc.) and conflict checks (`_raise_if_conflict`) but does **not** evaluate whether the target appointment date or time lies in the past.

### B. Raw Update Route (`PUT /appointments/{appointment_id}`)
* **Current Behaviour** (L4038-L4052):
  ```python
  @router.put("/{appointment_id}", response_model=AppointmentOut)
  def update_appointment(appointment_id: uuid.UUID, body: AppointmentUpdate, ...):
      ...
      return _apply_appointment_update(...)
  ```
  `_apply_appointment_update` recalculates canonical times if updated, verifies references, and performs slot conflict checks, but completely lacks validation against the current clinic date and time.

### C. Raw Status (`PATCH /appointments/{id}/status`) & Delete (`DELETE /appointments/{id}`)
* **Current Behaviour** (L4155 & L4331):
  These routes properly modify status or delete records without enforcing appointment-date constraints, which matches the required state-only design. However, they lack structured documentation declaring this operational exemption.

---

## 5. Actionable Implementation & Policy Recommendations for Sprint R7

To address these gaps, the following changes should be integrated into `app/routers/appointments.py` in the subsequent implementation phase:

### A. Define the Exception Schema
Introduce a specific temporal validation error structure to distinguish temporal blocks from general validation failures:
```python
class TemporalValidationError(HTTPException):
    def __init__(self, detail: str, code: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": detail, "code": code}
        )
```

### B. Implement Router-Level Raw Guards
Inject temporal checks in `_create_appointment_from_body` and `_apply_appointment_update`:

```python
# Implementation Draft for Create Guard
practice_tz = _practice_zoneinfo(db, practice_id)
clinic_now = _clinic_local_now(practice_tz)
clinic_today = clinic_now.date()
clinic_now_time = clinic_now.time().replace(second=0, microsecond=0)

# Check if admin override is present and permitted
is_bypass = getattr(body, "admin_override", False)

if not is_bypass:
    if appointment_date < clinic_today:
        raise TemporalValidationError(
            "Cannot book appointments on an absolute past date.",
            "DATE_IN_PAST"
        )
    elif appointment_date == clinic_today and start_time_local < clinic_now_time:
        raise TemporalValidationError(
            "Cannot book appointments for a same-day time that has already elapsed.",
            "SAME_DAY_TIME_ELAPSED"
        )
```

For updates, the guard should only fire if `appointment_date` or `start_time_local` are explicitly included in the patch/PUT values.

---

## 6. Recommendations for Deterministic Testing

To verify the raw temporal guards without relying on real-world system clocks, the test suite must simulate specific temporal scenarios:

### A. Pytest Mocking Patterns (Unit & Integration Tests)
Using pytest's `monkeypatch`, mock `_clinic_local_now` in `app.routers.appointments` to a fixed baseline (e.g. `2026-07-05 10:30:00`).

1. **Test Direct Create Past Date**:
   * **Input**: `POST /appointments` with `appointment_date="2026-07-04"`, `start_time_local="09:00:00"`.
   * **Assert**: Response status `422` containing error code `"DATE_IN_PAST"`.

2. **Test Direct Create Same-Day Elapsed**:
   * **Input**: `POST /appointments` with `appointment_date="2026-07-05"`, `start_time_local="10:00:00"`.
   * **Assert**: Response status `422` containing error code `"SAME_DAY_TIME_ELAPSED"`.

3. **Test Direct Create Same-Day Future**:
   * **Input**: `POST /appointments` with `appointment_date="2026-07-05"`, `start_time_local="11:00:00"`.
   * **Assert**: Response status `201` (Success).

4. **Test Direct Update Same-Day Elapsed**:
   * **Input**: `PUT /appointments/{id}` with `start_time_local="10:00:00"`.
   * **Assert**: Response status `422` with `"SAME_DAY_TIME_ELAPSED"`.

5. **Test Status & Delete Exemption**:
   * **Input**: `PATCH /appointments/{id}/status` or `DELETE /appointments/{id}` where the target appointment date is `"2026-07-04"`.
   * **Assert**: Response status `200` or `204` (Success; no temporal block triggered).

6. **Test Admin Override Bypass**:
   * **Input**: `POST /appointments` with `appointment_date="2026-07-04"`, `admin_override=True`.
   * **Assert**: Response status `201` (Success; validation bypassed).
