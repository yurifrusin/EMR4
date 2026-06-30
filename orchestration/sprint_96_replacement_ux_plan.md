# Sprint 96 Replacement UX Plan - Bernie Reception Assistant

| Item | Value |
|---|---|
| Status | Accepted |
| Owner | Codex UX worker with Ariadne review |
| Replaces | Rejected Antigravity/Gemini reception UX plan |
| Accepted at | 2026-06-30 |

## Direction

Keep backend/API state keys such as `blocked`, `candidate_selection_required`,
and `confirmation_ready` unchanged. Treat them as internal contract values only.
Receptionist-facing text should come from UI copy mapping in the diary layer.

The UX should make Bernie feel like a calm reception assistant. Staff still make
the final booking decision, and confirmation remains the only appointment write.
Safety should be carried by typed APIs, RBAC, confirmation endpoints, and audit,
not by alarming labels.

## Copy Changes

Replace visible wording as follows:

| Current | Replacement |
|---|---|
| `Supervised Booking Review` | `Bernie` |
| `Launch Bernie Pilot (Supervised)` | `Open Bernie` |
| `blocked` | `Needs details` |
| `candidate selection required` | `Choose a time` |
| `confirmation ready` | `Ready to book` |
| `Supervised Booking Blocked` | `Add the missing details` |
| `Supervised Candidate Selection Required` | `Bernie found these times` |
| `Supervised Proposal Ready` | `Ready to book this appointment` |
| `Block Issues` | `Needs` |
| `Candidate Slots` | `Available times` |
| `Selected Slot` | `Appointment details` |
| `Preview on diary` | `Show on diary` |
| `Bernie provisional booking` | `Proposed appointment` |
| `Confirm and Process Booking` | `Confirm booking` |
| `Booking proposal approved successfully...` | `Booking confirmed.` |
| `Booking proposal confirmation failed: ...` | `Booking could not be confirmed: ...` |
| `Submit Instruction for Review` | `Find times` |
| `Interpreting...` | `Finding times...` |
| `Type booking instructions for staff-supervised analysis...` | `Tell Bernie what appointment to find...` |

Keep one quiet reminder near the confirm area: `Review the details before
confirming.` Do not use robot/masked iconography or red safety-theatre language
for normal proposal states.

## Card Hierarchy

1. Header: `Bernie`, without robot emoji or "supervised" language.
2. Instruction/context card: selected patient, DOB when known, practitioner,
   existing appointment time when imported, and a `Change` action.
3. Request summary: practitioner, patient, date/window, and duration. Hide raw
   provider/debug metadata unless explicit dev diagnostics are open.
4. Patient details: patient, DOB, identity evidence, and checks where present.
   Convert codes such as `medicare_not_on_record` into readable labels.
5. Available times: each candidate is a keyboard-accessible button with time as
   primary text, plus duration, practitioner, patient, and `Show on diary`.
6. Appointment details: selected patient, DOB/evidence, practitioner, date,
   time, and duration.
7. Confirmation: primary `Confirm booking` button with `Ctrl+Alt+Enter` shown
   as the keyboard shortcut. The button click is the explicit staff
   confirmation and posts `confirmed: true`.

## Candidate And Confirmation Behaviour

- Candidate buttons remain ordinary buttons and support click, Enter, and Space.
- Selecting a candidate sets the selected candidate index, stages the diary
  preview, marks the chosen card with `aria-pressed="true"`, and calls the
  existing review path with `selected_candidate_index`.
- No confirmation action appears until the backend returns confirmation-ready
  evidence for a selected slot.
- The staged diary card is not clickable and cannot confirm the booking.
- `Ctrl+Alt+Enter` triggers the confirm button only when Bernie is open, the
  button is visible and enabled, and focus is not inside the instruction
  textarea. It no-ops in needs-details and choose-a-time states.

## Provisional Diary Card Pulse

Yuri approved trying a restrained pulse on the provisional booking slot.

Constraints:

- Apply only when a candidate has just been staged.
- Pulse border and shadow only: no scale, no layout shift, no infinite loop.
- Run two to three gentle cycles, then stop.
- Respect `prefers-reduced-motion: reduce` by disabling the animation.
- Keep the card information-first: patient, practitioner, time, duration, and
  identity evidence are more important than the animation.
- The card copy should say `Proposed appointment`, not `Bernie provisional
  booking`.

## Test Plan

Update `review/test_diary_smoke.py` to assert:

- The normal Bernie panel copy uses `Bernie`, `Find times`, `Available times`,
  `Show on diary`, and `Confirm booking`.
- `Supervised Booking Review`, `BLOCKED`, and `Bernie provisional booking` do
  not appear in the ordinary receptionist workflow.
- Selecting a candidate stages `[data-testid="bernie-staged-booking-card"]`,
  sends `selected_candidate_index`, and still performs no confirm write.
- The confirm POST happens only after the explicit Confirm button or valid
  `Ctrl+Alt+Enter` shortcut, and includes `confirmed: true`.
- The keyboard shortcut no-ops before the confirmation-ready state.
- Reduced-motion mode disables the staged-card pulse animation.

Run these checks before integration:

```powershell
node --check docs\diary\diary.js
.venv\Scripts\python.exe scripts\check_frontend_versions.py
.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q --tb=short
git diff --check
```

## Risks

- Backend reason strings can still leak into the UI if evidence summaries are
  rendered directly. The diary layer should map them into calm copy.
- Removing visible safety theatre must not remove API-level guardrails or audit.
- The pulse can imply urgency if overdone; keep it finite and paired with a
  separate Confirm action.
