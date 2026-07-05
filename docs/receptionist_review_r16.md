# EMR4 Sprint R16 — Receptionist-Domain Status-Specific Reason-Code UX Review

This document outlines the receptionist-domain reason-code mapping and governance policy for **Sprint R16**. It refines the Sprint R15 implementation plan by moving from datetime-based filtering to strict **status-specific filtering** for terminal appointment states (`Cancelled`, `DNA`, and `NoShow`).

---

## 1. Contextual Status-Specific Filtering

In General Practice clinic administration, the reasons for cancellation or non-attendance differ based on whether a patient proactively cancels or fails to attend. 

To reduce administrative friction and data noise:
1. The `#booking-status-reason-code` select element must dynamically update its options to show **only** the codes relevant to the selected booking status.
2. The past/future datetime context check (`bookingReasonCodeContext()`) is replaced by a direct lookup against the chosen terminal status (`Cancelled`, `DNA`, or `NoShow`).

### Status-to-Reason Code Mappings

| Selected Status | Allowed Reason Codes (Administrative Only) | Hidden / Filtered-Out Codes |
| :--- | :--- | :--- |
| **Cancelled** | <ul><li>`PATIENT_CANCELLED` ("Patient cancelled")</li><li>`PATIENT_TRANSPORT` ("Transport or access issue")</li><li>`PRACTITIONER_UNAVAILABLE` ("Practitioner unavailable")</li><li>`CLINIC_OPERATIONAL` ("Clinic operational issue")</li><li>`ADMIN_ERROR` ("Administrative correction")</li><li>`DUPLICATE_BOOKING` ("Duplicate booking")</li><li>`OTHER` ("Other administrative reason")</li></ul> | <ul><li>`DID_NOT_ATTEND`</li><li>`LEFT_WITHOUT_SEEN`</li><li>`PATIENT_RESCHEDULED` *(Auto-assigned)*</li><li>`CLINIC_RESCHEDULED` *(Auto-assigned)*</li><li>`PATIENT_UNWELL` *(Removed for compliance)*</li><li>`LEGACY_UNCLASSIFIED` *(Backend only)*</li></ul> |
| **DNA** (Did Not Attend) | <ul><li>`DID_NOT_ATTEND` ("Did not attend")</li><li>`LEFT_WITHOUT_SEEN` ("Left before being seen")</li><li>`ADMIN_ERROR` ("Administrative correction")</li><li>`DUPLICATE_BOOKING` ("Duplicate booking")</li><li>`OTHER` ("Other administrative reason")</li></ul> | <ul><li>`PATIENT_CANCELLED`</li><li>`PATIENT_TRANSPORT`</li><li>`PRACTITIONER_UNAVAILABLE`</li><li>`CLINIC_OPERATIONAL`</li><li>`PATIENT_RESCHEDULED`</li><li>`CLINIC_RESCHEDULED`</li><li>`PATIENT_UNWELL`</li><li>`LEGACY_UNCLASSIFIED`</li></ul> |
| **NoShow** (No Show) | <ul><li>`DID_NOT_ATTEND` ("Did not attend")</li><li>`LEFT_WITHOUT_SEEN` ("Left before being seen")</li><li>`ADMIN_ERROR` ("Administrative correction")</li><li>`DUPLICATE_BOOKING` ("Duplicate booking")</li><li>`OTHER` ("Other administrative reason")</li></ul> | <ul><li>`PATIENT_CANCELLED`</li><li>`PATIENT_TRANSPORT`</li><li>`PRACTITIONER_UNAVAILABLE`</li><li>`CLINIC_OPERATIONAL`</li><li>`PATIENT_RESCHEDULED`</li><li>`CLINIC_RESCHEDULED`</li><li>`PATIENT_UNWELL`</li><li>`LEGACY_UNCLASSIFIED`</li></ul> |

---

## 2. Where `LEFT_WITHOUT_SEEN` Belongs

### Operational Rationale
- **Does it belong with DNA/NoShow?** Yes.
- **Why?** In clinic administration, `LEFT_WITHOUT_SEEN` (the patient walked out after checking in, usually due to long wait times) is a critical operational status representing non-completion of the appointment on the day.
- **The Gap in Statuses:** The EMR4 booking model only exposes `Completed` (consultation occurred), `Cancelled` (prior notice), `DNA`, and `NoShow` as terminal states. Since the consultation did not occur, the appointment cannot be marked `Completed`. Since the patient arrived, it cannot be marked `Cancelled` in advance.
- **Resolution:** The receptionist must mark the appointment as `DNA` or `NoShow` to close the record on the day's grid. The selection of `LEFT_WITHOUT_SEEN` as the reason code ensures the database records that the patient **did** arrive but walked out, protecting the clinic from clinical liability (e.g., walkout audits) and billing errors.

### Implementation Rule
- Show `LEFT_WITHOUT_SEEN` and `DID_NOT_ATTEND` whenever the user selects `DNA` or `NoShow` as the booking status.
- Hide them completely when the booking status is set to `Cancelled`.

---

## 3. UI Implementation Details

### Modification of `populateBookingReasonCodeOptions(status)`

Instead of checking the datetime context, `docs/diary/diary.js` will populate options based on the selected status:

```javascript
const STATUS_SPECIFIC_REASON_CODES = {
  Cancelled: [
    "PATIENT_CANCELLED",
    "PATIENT_TRANSPORT",
    "PRACTITIONER_UNAVAILABLE",
    "CLINIC_OPERATIONAL",
    "ADMIN_ERROR",
    "DUPLICATE_BOOKING",
    "OTHER"
  ],
  DNA: [
    "DID_NOT_ATTEND",
    "LEFT_WITHOUT_SEEN",
    "ADMIN_ERROR",
    "DUPLICATE_BOOKING",
    "OTHER"
  ],
  NoShow: [
    "DID_NOT_ATTEND",
    "LEFT_WITHOUT_SEEN",
    "ADMIN_ERROR",
    "DUPLICATE_BOOKING",
    "OTHER"
  ]
};

function populateBookingReasonCodeOptions(status) {
  const select = document.getElementById("booking-status-reason-code");
  if (!select) return;
  const currentValue = select.value;
  select.innerHTML = "";
  
  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "-- Select Reason --";
  select.appendChild(defaultOption);

  const codes = STATUS_SPECIFIC_REASON_CODES[status] || [];
  codes.forEach(code => {
    const option = document.createElement("option");
    option.value = code;
    option.textContent = statusReasonCodeLabel(code);
    select.appendChild(option);
  });

  select.value = codes.includes(currentValue) ? currentValue : "";
}
```

---

## 4. Smoke Test Alignment & Selection Stability

The changes in Sprint R16 must maintain compatibility with all assertions in `review/test_diary_smoke.py`:

1. **Selection Stability:** Keep all data-testid selectors:
   - Dropdown container: `[data-testid='booking-status-reason-code-container']`
   - Select element: `[data-testid='booking-status-reason-code']`
   - Warnings & error containers: `[data-testid='booking-reason-privacy-warning']`
2. **Smoke Test Compatibility:** 
   - `test_reason_code_dropdown_no_default_and_ui_required` verifies that selecting `Cancelled` on a future date excludes `DID_NOT_ATTEND` and `LEFT_WITHOUT_SEEN`. With status-specific filtering, this naturally passes since `Cancelled` options list is independent of date.
   - `test_reason_code_retrospective_options_are_prioritized` verifies that selecting `DNA` on a past date makes `DID_NOT_ATTEND` and `LEFT_WITHOUT_SEEN` the first options. With status-specific filtering, they are naturally the primary options for `DNA`.
