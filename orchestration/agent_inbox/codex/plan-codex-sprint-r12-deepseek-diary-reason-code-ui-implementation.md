# Implementation Plan: Sprint R12 — Diary Reason-Code UI Controls

| Item | Value |
|---|---|
| **Task** | codex-sprint-r12-deepseek-diary-reason-code-ui-implementation |
| **Role** | codex-worker |
| **Worker Name** | Shen (DeepSeek Flash) |
| **Worker Branch** | codex/sprint-r12-diary-reason-code-ui |
| **Status** | accepted |

## My Understanding

Sprint R11 laid the nullable `status_reason_code` substrate across the backend:
- `Appointment.status_reason_code` (DB column, nullable `String(50)`)
- `AppointmentAuditLog.status_reason_code` (same)
- `STATUS_REASON_CODES` frozenset in `app/schemas/appointments.py` with 13 codes:
  `PATIENT_CANCELLED`, `PATIENT_RESCHEDULED`, `PATIENT_UNWELL`, `PATIENT_TRANSPORT`,
  `PRACTITIONER_UNAVAILABLE`, `CLINIC_OPERATIONAL`, `CLINIC_RESCHEDULED`, `ADMIN_ERROR`,
  `DUPLICATE_BOOKING`, `DID_NOT_ATTEND`, `LEFT_WITHOUT_SEEN`, `OTHER`, `LEGACY_UNCLASSIFIED`
- `validate_status_reason_code()` validator applied to `AppointmentStatusCommand`,
  `AppointmentDeleteCommand`, `AppointmentUpdate`, and `AppointmentOut`

However, the diary frontend (`docs/diary/`) has **no first-party reason-code UI**. The only
control is a free-text `#booking-cancel-reason` input (cancellation_reason, nullable String).
The `status_reason_code` field is never sent from the UI for either cancel/delete flows or
status-change flows.

This sprint adds a **dropdown select** with the 13 reason codes (plus blank default) to:
1. The delete/cancel confirmation flow (shown when user clicks Cancel → Confirm Cancel)
2. The status-change flow (shown when status changes to Cancelled/DNA/NoShow)
3. Thread `status_reason_code` through `simulateStatusProposal` (smoke mode) and real
   backend proposal calls

## Intended Surface / Boundary

| Surface | Change? |
|---|---|
| `docs/diary/diary.html` — booking modal | Add `<select id="booking-status-reason-code">` below cancel-reason row, hidden by default |
| `docs/diary/diary.js` — `deleteBooking()` | Thread status_reason_code into proposal payloads |
| `docs/diary/diary.js` — `saveBooking()` | Thread status_reason_code when status changes to terminal |
| `docs/diary/diary.js` — `simulateStatusProposal()` | Accept and return status_reason_code in mock proposal |
| `docs/diary/diary.js` — `prepareStatusDropdown()` / change handler | Show/hide reason-code dropdown based on selected status |
| `docs/diary/diary.js` — audit history rendering | Show status_reason_code if present in audit events |
| `docs/diary/diary.js` — flow card rendering | Show status_reason_code on cancelled flow cards |
| `docs/diary/diary.css` | Styling for new dropdown |
| `review/checks_diary.json` | Optional data-testid check if applicable |

### Adjacent surfaces that must NOT change
- Word taskpane patient-file UI (`taskpane/`)
- Backend routes and schemas (`app/routes/`, `app/schemas/`, `app/models/`)
- Admin modal, waiting room panel, Bernie session machinery
- Diary grid layout, column/room/slot rendering
- Git cachebust version strings on unchanged assets

## Out of Scope
- Backend migrations, routes, or database changes
- Making reason codes mandatory
- Changing temporal slot-write guards
- External API consumer reason-code enforcement
- Expanding the STATUS_REASON_CODES taxonomy
- Adding backend tests for reason-code contracts
- Bernie session changes

## Files I Expect To Edit
1. `docs/diary/diary.html` — Add `<select>` dropdown + container + label in booking modal
2. `docs/diary/diary.js` — Wire dropdown show/hide, proposal payloads, smoke simulate, audit/flow card display
3. `docs/diary/diary.css` — Styling for the new dropdown
4. `review/checks_diary.json` — (if applicable) New harness check for reason-code dropdown

## Implementation Steps

### Step 1: HTML — Add reason-code dropdown to the booking modal
- Add a hidden `#booking-status-reason-code-container` div below `#booking-cancel-reason-container`
- Inside: `<label>` with text "Reason Code (administrative, not clinical)"
- `<select id="booking-status-reason-code">` with a blank default option plus option values
- Map codes to user-friendly labels: Patient cancelled, Practitioner unavailable, etc.
- Add `data-testid="booking-status-reason-code"` on the select

### Step 2: CSS — Style the dropdown
- Style `.status-reason-code-container` matching existing form aesthetics

### Step 3: JS — Show/hide dropdown on status change
- Add change event listener on `#booking-status` that shows the container when status is
  Cancelled/DNA/NoShow and hides otherwise
- Also show during delete confirmation alongside cancel-reason container
- Clear and hide on modal close

### Step 4: JS — Thread into proposal payloads
- `deleteBooking()`: Read `status_reason_code`, send in delete proposal body \`{intent: "delete_appointment", cancellation_reason, status_reason_code}\` and in the 404 fallback status-proposal path
- `saveBooking()`: When status changes to terminal, include reason code in status proposal
- `simulateStatusProposal()`: Accept and return `status_reason_code` in proposal

### Step 5: JS — Show in audit history and flow cards
- Audit: display `evt.status_reason_code` similarly to cancellation_reason
- Flow cards: show reason code label if present
- Handle missing reason code gracefully in both display locations

### Step 6: JS — Clear on modal close/reset
- Reset reason-code dropdown value to blank and hide container

## Visual / Behavioural Acceptance Checks
1. Opening booking editor for existing non-terminal appointment shows Cancel button
2. Clicking Cancel → Confirm Cancel shows reason-code dropdown with no preselection
3. Selecting a reason code and confirming sends `status_reason_code` in the payload
4. Changing status in edit mode to Cancelled/DNA/NoShow shows reason-code dropdown
5. Changing status to non-terminal hides dropdown
6. Free-text Cancellation Reason still works alongside new dropdown
7. Smoke mode: `simulateStatusProposal` accepts and returns `status_reason_code`
8. No preselected default — staff must explicitly choose
9. Privacy label shows "(administrative, not clinical)" hint
10. `node --check docs/diary/diary.js` passes
11. No unrelated diary layout changes in git diff

## Risks / Ambiguities
1. **Backend validation**: Sending `""` (empty string) may fail — must send `null` or omit
2. **404 fallback**: Both delete-proposal and status-proposal paths need threading
3. **Existing mock data**: Smoke mocks lack `status_reason_code`; handle missing gracefully
4. **Privacy copy**: "(administrative, not clinical)" avoids clinical-detail framing
5. **Version cachebust**: Update diary.js/diary.css version strings if editing (e.g. JS `v=169`, CSS `v=133`)

## Verification Plan
```powershell
node --check docs/diary/diary.js
Select-String -Pattern "status_reason_code" -Path docs/diary/diary.js
git diff --stat
git diff --check
```

## Merge Criteria
- First-party Diary cancel/status actions can supply `status_reason_code` without breaking existing nullable flows
- UI copy avoids clinical-detail capture
- No unrelated Diary layout churn
- JS syntax check passes
- Backward compatible: null/absent reason code still works

## Codex Plan Review

- Review result: Accepted with amendments. Use the actual branch `codex/sprint-r12-diary-reason-code-ui-implementation`; do not expose `LEGACY_UNCLASSIFIED` in first-party dropdowns; keep `status_reason_code` optional at API level; target `docs/diary` only unless tests require minimal review selector support; avoid audit/free-text access-control changes in this sprint.
- Required changes before implementation: See review result amendments.
- Approved to proceed: yes
