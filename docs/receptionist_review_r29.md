# R29 Receptionist Acceptance Review: Native Action Grammar Foundation

Date: 2026-07-06
Status: source-safe acceptance criteria

## 1. Executive Summary

This document defines the receptionist-domain acceptance criteria for the first native Bernie/Diary action grammar foundation (dispatched in Programme 2B/2D). It establishes safety boundaries, write-authority preservation, and adversarial gates to ensure receptionist workflow integrity without introducing visual UI changes.

Following the R28 Fable readiness recommendations:
- The H15 semantic labelling gate remains closed.
- The 58k-file historical trove is not utilized or processed.
- The native action grammar acts as a versioned, typed schema representing the target vocabulary for all clinical diary mutations.

---

## 2. Receptionist-Domain Acceptance Criteria

The action grammar vocabulary comprises seven core actions. For each action, the receptionist domain demands strict validation rules and semantic constraints:

### A. Create Appointment (`Create`)
- **Clinical Intent**: Drafting a new appointment slot for a patient with a specific practitioner.
- **Acceptance Criteria**:
  - Must validate practitioner availability, roster templates, and clinic operational hours on the backend.
  - Must perform duplicate patient detection.
  - Returns a `proposal` frame requiring explicit staff confirmation.
  - Autonomous booking is strictly prohibited.

### B. Move Appointment (`Move`)
- **Clinical Intent**: Relocating an existing appointment to a new day/time slot.
- **Acceptance Criteria**:
  - Must validate patient collision and practitioner availability at the destination.
  - Requires source-appointment exclusion from destination collision checks.
  - Exposes a staged `proposal` frame showing the old vs. new time slot to the receptionist.

### C. Resize Appointment (`Resize`)
- **Clinical Intent**: Extending or shortening the duration of an appointment slot.
- **Acceptance Criteria**:
  - Must check for adjacent booking blockages/collisions before extending.
  - Requires staff confirmation via a proposal frame before mutating duration.

### D. Cancel Appointment (`Cancel`)
- **Clinical Intent**: Removing an appointment and capturing a reason.
- **Acceptance Criteria**:
  - All cancellations must enforce valid reason codes from the committed taxonomy (e.g., `Patient Cancelled`, `Clinic Operational`, `Admin Error`).
  - The model must never default or guess a reason; it must issue a `clarify` frame if the receptionist's prompt is ambiguous.

### E. Roster Change (`RosterChange`)
- **Clinical Intent**: Modifying doctor shift times or availability.
- **Acceptance Criteria**:
  - Must not be modifiable directly via patient booking paths.
  - Changes must stage a distinct proposal and be validated against existing booked appointments to prevent orphan bookings.

### F. Check-In Patient (`CheckIn`)
- **Clinical Intent**: Marking a patient as arrived in the clinic waiting area.
- **Acceptance Criteria**:
  - Must match the specific scheduled appointment slot and verify patient identity.
  - Must transition status strictly according to the backend waiting area state machine.

### G. Link Patient (`LinkPatient`)
- **Clinical Intent**: Resolving a provisional patient file to a verified master record.
- **Acceptance Criteria**:
  - Must prevent linking matching duplicates without explicit receptionist review.
  - Exposes disambiguation candidate lists inside a `clarify` frame.

---

## 3. Strict Safety Invariants & Boundaries

### A. Strict Zero-UI-Change Boundary
- **Definition**: The native action grammar foundation is a backend schema and data contract layer. Absolutely no visual, layout, or interactive changes are allowed in the frontend user interface.
- **Preserved Surfaces**: The following receptionist-facing surfaces must remain completely unchanged:
  - The [diary grid](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary) and booking slot layouts.
  - Waiting room panels, waiting area tabs, and card stacking visual states.
  - Appointment creation modals and status dropdown controls.
  - The Command Center taskpane.

### B. Backend Write-Authority Preservation
- **Definition**: The backend database remains the sole authoritative source of truth.
- **Invariants**:
  - Action grammar outputs from the model are advisory `proposal` or `clarify` frames only.
  - No frame can bypass backend database checks (for availability, collisions, status transitions, signed evidence, audit trails, and route permissions).

### C. No Autonomous Bookings
- **Definition**: No appointment can be booked, modified, or cancelled automatically by the AI provider.
- **Invariants**:
  - Every draft action must stage a proposal requiring explicit receptionist review and confirmation (`requires_staff_confirmation: true`).
  - The parameter `writes_authorized` must default to `false` and cannot be modified by the AI provider.

### D. Trove & H15 Isolation
- **Definition**: The historical 58k-file trove remains local and completely ignored.
- **Invariants**:
  - The H15 semantic labelling gate remains closed.
  - No trove data or neutral profile metrics may be consumed, processed, or sent to external AI providers.

---

## 4. Adversarial Gates

To harden the EMR4 receptionist workflow against boundary-bypassing inputs, the action grammar must enforce four adversarial gates:

### A. No New Authority Vocabulary for Reception
- The action grammar must not introduce new override parameters, vocabulary, or backdoor bypass fields (such as direct `bypass_confirm` or `force_write` flags) that would allow a receptionist or AI client to execute database changes without regular validation.

### B. No Confirm Affordance Bypass
- The confirmation flow is structurally mandatory. The action grammar schema must lack any endpoints or routes that allow the application to transition a proposal to a confirmed state without receiving backend signed evidence of explicit receptionist interaction.

### C. No H-Series Semantics in Action Grammar
- The action grammar must use clean, domain-specific terminology mapping to real clinical events (`booking`, `cancellation`, `check_in`).
- It must not import or reference neutral H-series event classes (e.g., `no_structural_change`, `small_content_delta`, `time_grid_delta`, `large_unexplained_delta`) as part of its action/status schemas or transition parameters.

### D. Planned-Not-Implemented Actions Must Not Appear Available
- Actions defined in the grammar that are not yet implemented in the backend (e.g., roster changes or multi-provider slot blocking) must return a strict `refusal` or error response rather than appearing to staff as available or selectable options.

---

## 5. Next Steps & Replay Verification

As recommended by the approved Fable plan:
1. Establish this receptionist review as the acceptance foundation for the native action grammar.
2. Implement a deterministic replay harness that simulates synthetic receptionist days using the action grammar.
3. Keep the H15 semantic gate closed until a small-slice semantic extraction prototype is verified and explicitly approved.
