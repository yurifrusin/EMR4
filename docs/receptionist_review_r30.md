# R30 Receptionist Acceptance Review: Action Grammar Replay Consumer

Date: 2026-07-06
Status: source-safe acceptance criteria

## 1. Executive Summary

This document establishes the receptionist-domain acceptance criteria for the R30 deterministic synthetic action replay consumer. The purpose of this consumer is to validate the native clinical action grammar defined in R29 by processing simulated receptionist actions. 

Following the R28 Fable readiness recommendations and strict safety guidelines:
- The replay consumer must run in a sandboxed, synthetic environment completely isolated from production state and raw troves.
- The H15 semantic labelling gate remains closed.
- The replay consumer must demonstrate non-tautological consumption of action payloads without possessing write authority or modifying the user interface.

---

## 2. Deterministic Replay Consumer Acceptance Criteria

The replay consumer must consume simulated receptionist actions and prove grammar compliance under the following criteria:

### A. Synthetic-Only Fake Day/Action Scripts
- **Definition**: The inputs to the replay harness must consist entirely of hand-authored, synthetic day/action scripts.
- **Constraints**:
  - Scripts must simulate common receptionist workflows (e.g., searching for a patient, staging a booking, canceling an appointment, and check-in events) using mock inputs.
  - No real patient identities, operational schedules, or actual clinic records may be simulated or imported.

### B. Complete Isolation from Raw/Full-Trove/H-Series Data
- **No Trove Access**: The replay consumer must not read, parse, or import files from the 58k-file historical diary trove (`local_data/historical-diary-trove/raw/` or ignored aggregate datasets).
- **No H-Series Input**: The replay runner must not consume or query neutral H-series profiles, transition statistics, or derived neutral graph JSON as input data.
- **H15 Gate Closed**: The semantic de-identification gate remains closed. No semantic appointment fixtures or de-identified real clinical records may be injected into the replay environment.

### C. Zero Autonomous Booking
- **Definition**: The replay consumer must never autonomously execute, schedule, or confirm booking actions.
- **Constraints**:
  - Every staged mutation must generate a proposal frame requiring explicit staff confirmation (`requires_staff_confirmation: true`).
  - The AI provider cannot auto-confirm or bypass the receptionist validation workflow.

### D. Zero Backend Write Authority
- **Definition**: The replay consumer must operate in a strictly read-only mode relative to the production clinical database.
- **Constraints**:
  - The `writes_authorized` field on all grammar actions processed during replay must remain strictly `false`.
  - The replay must not perform any mutations, inserts, or updates to the PostgreSQL database or persistent clinical state.

### E. Zero UI / Frontend Changes
- **Definition**: The replay consumer is a backend test harness and schema verification tool.
- **Constraints**:
  - Absolutely no visual, layout, or interactive UI elements in the clinical taskpane or workspace may be modified.
  - The [diary grid](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary), booking slot layouts, waiting room panels, and status controls must remain completely unchanged.

### F. Refusal of Planned Unavailable Actions
- **Definition**: Actions defined in the R29 grammar that are not yet implemented in the backend (e.g., roster changes, linking provisional patients, multi-provider slot blocking) must be rejected.
- **Constraints**:
  - The replay runner must assert that executing these planned unavailable actions results in immediate Refusals or validation errors, rather than returning staged success frames.

### G. Non-Tautological Verification
- **Definition**: The replay consumer must demonstrate useful, non-trivial grammar consumption rather than simple identity assertions.
- **Constraints**:
  - The replay must verify actual receptionist-domain validation logic (e.g., parsing of valid vs. invalid cancellation reason codes, identification of missing parameters leading to a `clarify` frame, and correct generation of staged `proposal` envelopes).
  - Assertions must check that incorrect inputs are rejected and correct inputs produce the expected advisory structures.

---

## 3. Boundary Definition & Architectural Decoupling

### A. Decoupling of Route-Level Replay and Database Verification
- **Invariant**: Route-level replay integration and direct database validation checks (such as verifying if a database record actually matches the state) remain completely separate from the R30 grammar replay consumer.
- **Rationale**:
  - The replay consumer operates strictly on the parsed action grammar payloads and mock state frames.
  - Real database constraint checking (e.g., actual SQL queries checking for overlapping sessions) will be wired in separately once the action grammar is integrated into the backend routes.
