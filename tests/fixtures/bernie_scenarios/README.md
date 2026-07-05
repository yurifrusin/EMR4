# Bernie Reception Scenario Corpus

This directory contains the canonical receptionist-domain scenarios for testing Bernie's native diary-agent behavior. These scenarios represent real-world interactions and edge cases found during GP clinic testing.

## Scenario Schema Reference

Each scenario is defined as a YAML file containing:

- **`id`**: Unique identifier string.
- **`category`**: Scenario category (e.g., `booking_clarification`, `future_booking_advisory`, `no_slot_outcome`, `roster_unavailable_outcome`, `appointment_extension`, `mutation_safety`, `session_state_guard`).
- **`reference_date`**: The base date from which relative expressions (like "next Tuesday" or "tomorrow") are resolved (format: `YYYY-MM-DD`).
- **`initial_state`**: System state configuration before turns begin:
  - **`diary_date`**: Focused diary date (format: `YYYY-MM-DD`).
  - **`practice`**: Practice ID (e.g., `emr4_dev_main`).
  - **`seeded_appointments`** *(optional)*: List of pre-existing appointments to simulate existing bookings or collisions.
  - **`roster`** *(optional)*: Roster limits or rosters available for specific practitioners.
  - **`session_id`** / **`stale`** *(optional)*: Session configuration flags.
- **`turns`**: Ordered list of user prompts and the expected results after each turn:
  - **`user`**: The raw text prompt sent by the receptionist.
  - **`expect`**: Verification parameters:
    - **`outcome`**: The expected `BernieBookingOutcomeKind` classification (e.g., `clarification_required`, `confirmation_ready`, `no_matching_times`, `roster_unavailable`).
    - **`preserved`**: Map of fields that must be parsed/held in the request context (e.g., `patient`, `practitioner`, `date`, `time`, `duration_minutes`).
    - **`missing`** *(optional)*: List of missing fields that Bernie must ask clarification for.
    - **`advisory_warnings`** *(optional)*: List of advisory warnings expected in this state.
    - **`slot_search_run`** *(optional)*: Boolean indicating if a slot search was actually executed.
    - **`can_confirm`** / **`requires_confirmation`** / **`appointment_written`** *(optional)*: Mutation-safety flags.
- **`forbidden`**: List of strings describing behaviors, copy patterns, or outcomes that are strictly disallowed during this scenario (e.g., losing patient context, mutating the DB before confirmation, re-asking resolved fields).
- **`xfail`** *(optional)*: Used to mark known unfixed bugs. Contains a `reason` explaining why the scenario is expected to fail (for example, clarification merge bugs scheduled for Sprint R2).

## Boundary & Dissent Guidelines

1. **Focus on Intent and Context**: These fixtures assert domain intent and clinical state correctness. They do not test Diary frontend visual elements (like grid cards, slot rendering, or buttons).
2. **Clean Separation**: Antigravity owns scenario intent, receptionist-domain behavior, and expected state verification. Claude owns harness execution code. Codex owns integrity rules.
3. **Preserve Bugs in `xfail`**: Do not hide or remove failing scenarios for known bugs. Use `xfail` with a clear explanation so the harness can skip or expect failure without failing the CI run.
