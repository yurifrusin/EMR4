# Bernie Reception Scenario Corpus

This directory contains the canonical receptionist-domain scenarios for testing Bernie's native diary-agent behavior. Older corpus-memory scenarios represent real-world interactions and edge cases found during GP clinic testing; executable `interpret_*` cases are authored synthetic receptionist-style contract fixtures.

The directory contains two fixture styles:

- executable replay fixtures with `turns[].action`, loaded by
  `tests/bernie_scenarios/loader.py`;
- older scenario-memory fixtures with `turns[].user`, which remain useful corpus
  notes but are intentionally skipped by the executable replay loader.

Executable `interpret_*` fixtures are fake-provider, route-level contract tests.
They are not live-backend, live-provider, or provider-quality evidence.

The current executable `interpret_*` corpus covers two slices:

- first-pass natural prompt threads: full requests, clarifications, follow-up
  changes, confirm-required no-write boundaries, past-date blocking, and
  interpret -> search -> select handoff;
- edge-contract prompts: empty instruction validation, unknown patient names
  without invented patient ids, visible-diary date context, and explicit
  per-turn reference-date drift;
- context-precedence prompts: selected proposal date wins over selected diary
  appointment and visible diary page dates, while selected diary appointment
  date wins over visible diary page date;
- context-fallback prompts: omitted dates with no selected proposal, selected
  diary appointment, or visible diary page context ask for the missing date
  instead of guessing;
- context-threading prompts: omitted `context_frames` auto-threads prior
  requested appointment context, while explicit `context_frames: []` clears the
  thread and asks again, including when the threaded requested appointment was
  originally derived from multiple diary context frames;
- explicit-frame prompts: caller-supplied `requested_appointment` frames can
  provide prior appointment fields directly while current instruction fields
  still win;
- partial-override prompts: follow-up wording can change one threaded field,
  such as practitioner, while preserving the remaining patient/date/time/
  duration fields;
- multi-field override prompts: a single follow-up can change date and time
  together while preserving patient, practitioner, and duration;
- multi-field-missing prompts: patient-only booking requests without context ask
  for missing practitioner/date details instead of guessing;
- temporal-drift follow-ups: relative-date corrections resolve against the
  current turn reference date while preserving threaded appointment details.
- reference-date reload/reset prompts: repeated relative-date wording
  re-resolves against the current turn reference date and wins over
  auto-threaded prior requested appointment dates.
- reference-date no-op prompts: when a follow-up changes only time and contains
  no date wording, a changed turn reference date must not re-resolve the
  threaded absolute appointment date.
- time-window threading prompts: date-change follow-ups preserve both earliest
  and latest time-window bounds from the threaded requested appointment.
- same-time distractor prompts: "at the same time" wording in a date-change
  follow-up is treated as inert by the fake interpreter, so the prior time is
  preserved through route-level threading without claiming true anaphora
  support.
- reset/no-merge follow-ups: explicit `context_frames: []` prevents patient,
  practitioner, time, and duration from being carried forward unless the
  receptionist restates them in the current turn.
- default-duration prompts: complete generic booking requests with no duration
  or appointment type default to 15 minutes at the route boundary while staying
  fake-provider and no-write.

Unknown patient-name fixtures deliberately assert the current route contract:
the interpret layer may still produce a slot-search command when practitioner
and date are known, but it must leave `command_candidate.patient_id` null and
must not write appointments or audit rows. Patient identity enforcement belongs
to later proposal/confirmation surfaces unless a future reviewed sprint changes
this contract.

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
- **`preserved_fields`** *(executable replay only)*: Dotted response paths whose
  first non-null value must not change or disappear on later turns.

Executable replay fixtures instead use:

```yaml
turns:
  - action: interpret
    input:
      instruction: "Book Margaret Thompson next Tuesday at 15:30 for 30 minutes"
    expect:
      status: 200
      fields:
        result: clarification_required
```

For `interpret` turns, omitted `context_frames` auto-threads the
`requested_appointment` frame from the previous `interpret` turn. Use
`context_frames: []` to force a fresh turn.

## Boundary & Dissent Guidelines

1. **Focus on Intent and Context**: These fixtures assert domain intent and clinical state correctness. They do not test Diary frontend visual elements (like grid cards, slot rendering, or buttons).
2. **Clean Separation**: Antigravity owns scenario intent, receptionist-domain behavior, and expected state verification. Claude owns harness execution code. Codex owns integrity rules.
3. **Preserve Bugs in `xfail`**: Do not hide or remove failing scenarios for known bugs. Use `xfail` with a clear explanation so the harness can skip or expect failure without failing the CI run.
