# Bernie Scenario Replay Harness

Backend pytest replay harness for the Bernie receptionist scenario corpus.

## What it does

Loads YAML scenario fixtures, runs ordered backend/session turns (no live LLM
calls), and asserts structured outcomes (field values, per-turn and final row
writes, forbidden outcomes, preserved field invariants). Scenarios can seed
allowlisted appointment state and pin clinic-local time. Supports `xfail`
scenarios for known behaviour that a future sprint will fix.

Interpret scenarios run against the deterministic fake Bernie interpreter. They
are `fake-provider, route-level` evidence only: useful contract regression
coverage, not live-backend, live-provider, or provider-quality evidence.

## Running

```powershell
pytest tests/bernie_scenarios/ -v
```

Set `BERNIE_SCENARIO_EVIDENCE_DIR` to write one redacted
`bernie.scenario.evidence.v1` JSON record per scenario. Records contain action,
status, result kind, safety/confirmation flags, and row deltas; they omit raw
instructions, request bodies, response bodies, and entity IDs.

## Directory layout

```
tests/
  fixtures/
    bernie_scenarios/         # YAML scenario corpus (canonical for R1)
      harness_demo_*.yaml     # Claude/harness-owned demo fixtures (mechanics only)
      *.yaml                  # Antigravity corpus files (Sprint R1-B)
  bernie_scenarios/           # Harness code (this package)
    loader.py                 # YAML loader + schema validation
    replay.py                 # Turn executor + forbidden-outcome tracking
    test_scenario_replay.py   # Parametrized pytest
    README.md                 # This file
```

## Scenario YAML schema (R1)

```yaml
id: kebab-case-unique-string          # required; unique across corpus
category: booking_create              # required; free-form label
description: "..."                    # optional; human-readable
reference_date: "YYYY-MM-DD"          # required; anchor date for "today" resolution

initial_state:
  fixtures:                           # informational; conftest fixtures the scenario needs
    - practice
    - practitioner
    - gp_user
    - patient
    - schedule
  simulated_clinic_time: "08:00"       # optional; defaults to 08:00 on reference_date
  seeded_appointments:                  # optional allowlisted test setup
    - id: existing                      # local alias for {appointment_id:existing}
      patient: Margaret Thompson        # current fixture patient
      practitioner: Dr Shera            # current fixture practitioner
      date: "YYYY-MM-DD"
      time: "HH:MM"
      duration_minutes: 15
      status: Booked

xfail:                                # optional; mark scenario as expected-failing
  reason: "Why this fails today and what sprint will fix it"

turns:
  - action: interpret | normalize | search | select | supervise | confirm
    input:                            # action-specific; may use {practitioner_id},
      key: value                      # {patient_id}, {practice_id} template vars
    expect:
      status: 200                     # HTTP status code (default 200)
      fields:                         # dotted-path -> expected value
        "safe": true
        "constraint.date_from": "YYYY-MM-DD"
      appointment_delta: 0            # optional exact row delta for this turn
      audit_delta: 0                  # optional exact audit-row delta for this turn

expected:
  appointment_written: false          # assert Appointment row count changed (default false)
  audit_written: false                # assert AppointmentAuditLog row count changed

preserved_fields:                     # field paths that must not drift across turns
  - "constraint.date_from"

forbidden_outcomes:                   # things that must NOT happen
  - provider_called                   # AI provider call (enforced by monkeypatch guard)
  - appointment_written               # new Appointment row written
  - audit_written                     # new AppointmentAuditLog row written
```

`preserved_fields` snapshots the first non-null value for each dotted path and
fails if a later turn changes or drops that value. Use it for cross-turn
contracts such as `command_candidate.patient_id` or
`reception_context.frames.0.payload.date_from`.

### Template variables

| Variable | Resolves to |
|---|---|
| `{practitioner_id}` | `str(practitioner.id)` from conftest fixture |
| `{other_practitioner_id}` | `str(other_practitioner.id)` from the replay harness fixture |
| `{patient_id}` | `str(patient.id)` from conftest fixture |
| `{practice_id}` | `str(practice.id)` from conftest fixture |

### Action turn state threading

- **interpret**: posts `input.instruction` to
  `/api/v1/appointments/proposals/bernie/interpret-booking-instruction` with
  the fake interpreter. `reference_date` defaults to the scenario
  `reference_date`. If `input.context_frames` is omitted, the harness threads
  the `requested_appointment` frame from the previous `interpret` turn. Set
  `context_frames: []` explicitly to start a fresh turn.
- **search**: when `input` is empty, reuses the command from the last `normalize` turn
  or the `command_candidate` from the last `interpret` turn
- **select**: always uses the `search_execution` from the last `search` turn
- **supervise**: posts to the deterministic supervised-booking route, using an
  explicit `input.command` or the latest interpret/normalize command. It can
  select a candidate with `selected_candidate_index` and remains non-mutating.
- **confirm**: uses the `selection_proposal` from the last `select` turn or the
  authoritative `staff_review.confirm_payload` from the last `supervise` turn,
  and sends a deterministic `Idempotency-Key` unless `input.idempotency_key` is
  supplied

Example interpret thread:

```yaml
turns:
  - action: interpret
    input:
      instruction: "Book Margaret Thompson next Tuesday at 15:30 for 30 minutes"
    expect:
      status: 200
      fields:
        result: clarification_required
        "missing_fields.0": practitioner_id
        "reception_context.frames.0.payload.patient_id": "{patient_id}"
  - action: interpret
    input:
      instruction: "With Dr Shera please"
    expect:
      status: 200
      fields:
        result: interpreted
        "command_candidate.practitioner_id": "{practitioner_id}"
        "assumptions.0.field": clarification_merge
```

New interpret corpus fixtures should use receptionist-like natural phrasing
rather than `key:value` shorthand except where a fixture is deliberately testing
the lower-level command parser.

## Authorship boundary

| Files | Owner | Sprint |
|---|---|---|
| `tests/fixtures/bernie_scenarios/harness_demo_*.yaml` | Claude/harness | R1-A |
| `tests/fixtures/bernie_scenarios/*.yaml` (corpus) | Antigravity | R1-B |
| Fixture integrity review | DeepSeek | R1-C |
| `tests/bernie_scenarios/*.py` | Claude/harness | R1-A |

Antigravity should add corpus scenario files directly to `tests/fixtures/bernie_scenarios/`.
The harness will discover them automatically at collection time.
