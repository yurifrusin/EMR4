# Sprint R12 — First-Party Diary Reason-Code UX & Privacy Review

This document provides a detailed UX, copywriting, and privacy design review for implementing the first-party Diary cancellation and status change reason-code UI flow. Building upon the Sprint R11 backend substrate, this review sets the exact usability and compliance guidelines for frontend implementation to ensure APP (Australian Privacy Principle) compliance while minimizing receptionist cognitive load.

---

## 1. Dropdown Behavior & Default State

The introduction of the `status_reason_code` selection element to the first-party Diary must balance compliance reporting with speed of entry.

### Empty Default State
* **Policy:** The dropdown must always default to an empty state: `[ -- Select Reason -- ]` with a blank value (`null` or empty string sent as `null`).
* **Rationale:** Pre-selecting a default option (e.g. "Patient Cancelled") leads to "first-option bias," where users hit Enter to dismiss the dialog without selecting the actual reason. This corrupts operational metrics.
* **UI Enforcement:** The "Confirm Cancel" or "Save" button must be disabled, or validation must prevent submit, until the receptionist selects a non-empty option.

### Dropdown Taxonomy Mapping
To prevent cognitive overload, the dropdown must only display codes relevant to first-party receptionist workflows.

* **In Scope Codes:**
  * `PATIENT_CANCELLED` ("Patient requested cancellation")
  * `PATIENT_RESCHEDULED` ("Patient requested reschedule")
  * `PATIENT_TRANSPORT` ("Transport or access issue")
  * `PRACTITIONER_UNAVAILABLE` ("Practitioner unavailable")
  * `CLINIC_OPERATIONAL` ("Clinic operational issue")
  * `CLINIC_RESCHEDULED` ("Clinic requested reschedule")
  * `ADMIN_ERROR` ("Administrative correction")
  * `DUPLICATE_BOOKING` ("Duplicate booking")
  * `DID_NOT_ATTEND` ("Did not attend")
  * `LEFT_WITHOUT_SEEN` ("Left before being seen")
  * `OTHER` ("Other reason")
* **Out of Scope Codes (Backend Only):**
  * `LEGACY_UNCLASSIFIED`: **Must be hidden from the UI dropdown.** This code exists solely for backend database compatibility with historical data and must never be selectable by a user.

---

## 2. Administrative-Note Copy & UI Guidance

The free-text note field is a major source of accidental Personally Identifiable Information (PII) and Sensitive Health Information (SHI) leaks. To mitigate this risk, clear visual copy and input constraints must be applied.

### Character Constraints
* **Limit:** The free-text input field must enforce a hard limit of **150 characters**.
* **Rationale:** Restricting character count prevents receptionists from pasting clinical email correspondence, copying long referral letters, or entering detailed patient histories into the administrative audit trail.

### Copywriting for Input Field
The label and placeholder text should explicitly define the purpose of the field.

* **Dialog Label:**
  > **Note (Optional):**
* **Placeholder Text:**
  > *Brief administrative reason only (e.g., "Called to reschedule"). Do not enter medical details.*
* **Footer Disclaimer (inline, muted text):**
  > ⚠️ *Administrative notes are logged permanently. Under the Australian Privacy Principles (APPs), do not write symptoms, diagnoses, or clinical details.*

---

## 3. Real-Time Clinical Keyword Warning (Client-Side Guard)

A client-side dynamic validation script must scan the free-text note field as the user types.

### Keyword Dictionary
If the note input contains any of the following clinical keywords (case-insensitive):
`sick, unwell, pain, flu, covid, cancer, pregnant, bleeding, depression, anxiety, surgery, doctor, medication, rx, script, clinic, disease, illness`

### UI Response
A warning banner must appear dynamically below the input box.
* **Copy:**
  > ⚠️ **Privacy Notice:** Please do not enter medical symptoms, diagnoses, or sensitive personal information here. Keep notes limited to administrative context.
* **Non-Blocking Rule:** This warning must be **advisory only**. It should not block the user from submitting the dialog if they have typed one of these words in a non-clinical context (e.g., "Practitioner sick"). Blocking would disrupt the reception workflow and lead to workarounds.

---

## 4. Audit-Display Privacy & Access Guidance

Administrative reason codes and notes are recorded in the `AppointmentAuditLog`. Because audit records are accessed by IT administrators, external billers, and general office staff, access to raw free text must be constrained.

### Redaction Strategy
* **Structured Codes:** The structured `status_reason_code` (e.g., `PATIENT_TRANSPORT`) is safe for general display and must be shown on all administrative audit lists, booking flow cards, and diary detail views.
* **Free-Text Notes:** The free-text note field (`cancellation_reason`) must be **redacted or hidden by default** on general receptionist views.
* **Role-Based Access:** Only authorized Clinic Managers and compliance Audit Officers should be able to click to reveal the raw free-text note. For general staff, the note should display as `[Note Recorded - Private]` or only be accessible via clinical systems.

---

## 5. First-Party UI Flow & Acceptance Gates

The implementation must pass these specific UX verification checks:

1. **No Churn on Adjacent Layouts:** The addition of the reason-code container must not distort the layout of the booking modal or conflict with other fields. It should follow the CSS flex/grid spacing rules defined in `docs/diary/diary.css`.
2. **Dynamic Visibility:**
   * In edit mode, the reason-code selection container must remain hidden until the status is changed to a terminal state (`Cancelled`, `DNA`, `No Show`).
   * If the status is changed back to an active state (e.g. `Arrived`), the container must automatically clear its inputs and hide.
3. **Payload Sanitization:** If the user does not select a reason code, the frontend must send `null` or omit `status_reason_code` entirely rather than sending an empty string `""` or `undefined`.
