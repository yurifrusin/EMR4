# Sprint R15 — Receptionist-Domain Reason-Code UX & Privacy Review

This document establishes the receptionist workflow and privacy acceptance criteria for Sprint R15. It addresses contextual reason-code dropdown filtering and the mitigation of risks associated with the `PATIENT_UNWELL` code in the first-party Diary user interface.

---

## 1. Contextual Reason-Code Filtering

To minimize receptionist cognitive load and prevent "first-option bias" (where staff select the first available reason to dismiss a mandatory field), the options presented in the `status_reason_code` dropdown must be dynamically filtered based on the specific terminal status selected in the first-party Diary.

### Status-to-Reason Code Mappings

The dropdown list must only show codes that make logical and operational sense for the selected status:

| Selected Status | Allowed Reason Codes | Hidden / Filtered-Out Codes |
| :--- | :--- | :--- |
| **Cancelled** | <ul><li>`PATIENT_CANCELLED` ("Patient cancelled")</li><li>`PATIENT_TRANSPORT` ("Transport or access issue")</li><li>`PRACTITIONER_UNAVAILABLE` ("Practitioner unavailable")</li><li>`CLINIC_OPERATIONAL` ("Clinic operational issue")</li><li>`ADMIN_ERROR` ("Administrative correction")</li><li>`DUPLICATE_BOOKING` ("Duplicate booking")</li><li>`OTHER` ("Other administrative reason")</li></ul> | <ul><li>`PATIENT_RESCHEDULED`</li><li>`CLINIC_RESCHEDULED`</li><li>`DID_NOT_ATTEND`</li><li>`LEFT_WITHOUT_SEEN`</li><li>`PATIENT_UNWELL` *(Removed)*</li><li>`LEGACY_UNCLASSIFIED` *(Backend only)*</li></ul> |
| **DNA** (Did Not Attend) | <ul><li>`DID_NOT_ATTEND` ("Did not attend")</li><li>`ADMIN_ERROR` ("Administrative correction")</li><li>`DUPLICATE_BOOKING` ("Duplicate booking")</li><li>`OTHER` ("Other administrative reason")</li></ul> | <ul><li>`PATIENT_CANCELLED`</li><li>`PATIENT_RESCHEDULED`</li><li>`PATIENT_TRANSPORT`</li><li>`PRACTITIONER_UNAVAILABLE`</li><li>`CLINIC_OPERATIONAL`</li><li>`CLINIC_RESCHEDULED`</li><li>`LEFT_WITHOUT_SEEN`</li><li>`PATIENT_UNWELL`</li><li>`LEGACY_UNCLASSIFIED`</li></ul> |
| **NoShow** (No Show) | <ul><li>`DID_NOT_ATTEND` ("Did not attend")</li><li>`ADMIN_ERROR` ("Administrative correction")</li><li>`DUPLICATE_BOOKING` ("Duplicate booking")</li><li>`OTHER` ("Other administrative reason")</li></ul> | <ul><li>`PATIENT_CANCELLED`</li><li>`PATIENT_RESCHEDULED`</li><li>`PATIENT_TRANSPORT`</li><li>`PRACTITIONER_UNAVAILABLE`</li><li>`CLINIC_OPERATIONAL`</li><li>`CLINIC_RESCHEDULED`</li><li>`LEFT_WITHOUT_SEEN`</li><li>`PATIENT_UNWELL`</li><li>`LEGACY_UNCLASSIFIED`</li></ul> |

### Dropdown Behavioral Rules

1. **Empty Default State:** When the status changes to a terminal state (`Cancelled`, `DNA`, `NoShow`), the dropdown must default to `[ -- Select Reason -- ]` with a blank value (`null`).
2. **Mandatory Selection:** The "Save Booking" button must be disabled, and an inline validation error shown, until a valid non-empty reason code is selected.
3. **Reschedule Exception:**
   - If an appointment is moved on the grid (via drag-and-drop or status change to rescheduled), the UI should automatically assign `PATIENT_RESCHEDULED` or `CLINIC_RESCHEDULED` silently or auto-select it in the confirmation dialog, bypassing the manual selection requirement.

---

## 2. Elimination of `PATIENT_UNWELL` Privacy Risks

The code `PATIENT_UNWELL` ("Patient unwell") represents a high compliance risk under the **Australian Privacy Principles (APPs)**. Administrative logs are visible to IT personnel, billers, and general office staff. Permitting the capture of clinical symptoms or illness states in these records exposes the clinic to privacy violations.

### Mitigation Strategy

> [!IMPORTANT]
> **Core Rule:** The option `PATIENT_UNWELL` must be completely removed from all first-party UI dropdown menus and never be selectable by receptionists.

1. **Merging Behavior:** If a patient cancels because they are sick, receptionists must select `PATIENT_CANCELLED`.
2. **Administrative Notes Enforcement:**
   - The free-text note field (`booking-cancel-reason` / `cancellation_reason`) must remain strictly administrative (e.g., "Patient called to reschedule", "Transport issue").
   - The note field is capped at **150 characters**.
3. **Dynamic Client-Side Privacy Warnings:**
   - As the receptionist types in the note field, a client-side listener checks for symptoms/medical terms:
     `sick, unwell, pain, flu, covid, cancer, pregnant, bleeding, depression, anxiety, surgery, doctor, medication, rx, script, clinic, disease, illness`
   - If detected, a dynamic inline warning is shown:
     > ⚠️ **Privacy Notice:** Please do not enter medical symptoms, diagnoses, or sensitive personal information here. Keep notes limited to administrative context.
   - The warning is **non-blocking** (does not prevent save) to avoid workflow friction, but must be clearly visible in orange/yellow alert styling.

---

## 3. UI and Smoke Test Preservation

To ensure the new filtering and privacy rules do not break the existing test harness, the implementation must align with `review/test_diary_smoke.py`:

- **Smoke Mode Compatibility:** The UI must continue to load and interact correctly under the `?smoke=true` environment.
- **Selector Stability:** Ensure elements maintain their data-testid selectors:
  - Dropdown container: `[data-testid='booking-status-reason-code-container']`
  - Reason select: `[data-testid='booking-status-reason-code']`
  - Note input: `[data-testid='booking-cancel-reason']`
  - Warning block: `[data-testid='booking-reason-privacy-warning']`
- **Dropdown Options Assertion:** The test `test_reason_code_dropdown_no_default_and_ui_required` verifies that `LEGACY_UNCLASSIFIED` is not in the list. Future implementations must also verify that `PATIENT_UNWELL` is not present in the list options.

---

## 4. Acceptance Criteria Checklist

Future developers must meet these criteria before merging the R15 implementation:

- [ ] `PATIENT_UNWELL` option is removed from the `#booking-status-reason-code` select element.
- [ ] Dropdown options are dynamically filtered based on chosen status (`Cancelled` shows cancellation codes; `DNA`/`NoShow` shows attendance codes).
- [ ] Changing status back to a non-terminal state hides the dropdown container and resets the value.
- [ ] Character cap of 150 on `#booking-cancel-reason` is preserved.
- [ ] The dynamic keyword check triggers the warning message but does not block save.
- [ ] Smoke tests run and pass without failures (`pytest review/test_diary_smoke.py`).
