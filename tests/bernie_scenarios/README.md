# Bernie Scenario Replay Harness

Backend pytest replay harness for the Bernie receptionist scenario corpus.

## What it does

Loads YAML scenario fixtures, runs ordered backend/session turns (no LLM calls),
and asserts structured outcomes (field values, row writes, forbidden outcomes, preserved
field invariants). Supports `xfail` scenarios for known behaviour that a future sprint
will fix.

## Running

```powershell
pytest tests/bernie_scenarios/ -v
```

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

xfail:                                # optional; mark scenario as expected-failing
  reason: "Why this fails today and what sprint will fix it"

turns:
  - action: normalize | search | select | confirm
    input:                            # action-specific; may use {practitioner_id},
      key: value                      # {patient_id}, {practice_id} template vars
    expect:
      status: 200                     # HTTP status code (default 200)
      fields:                         # dotted-path -> expected value
        "safe": true
        "constraint.date_from": "YYYY-MM-DD"

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

### Template variables

| Variable | Resolves to |
|---|---|
| `{practitioner_id}` | `str(practitioner.id)` from conftest fixture |
| `{patient_id}` | `str(patient.id)` from conftest fixture |
| `{practice_id}` | `str(practice.id)` from conftest fixture |

### Action turn state threading

- **search**: when `input` is empty, reuses the command from the last `normalize` turn
- **select**: always uses the `search_execution` from the last `search` turn
- **confirm**: always uses the `selection_proposal` from the last `select` turn

## Authorship boundary

| Files | Owner | Sprint |
|---|---|---|
| `tests/fixtures/bernie_scenarios/harness_demo_*.yaml` | Claude/harness | R1-A |
| `tests/fixtures/bernie_scenarios/*.yaml` (corpus) | Antigravity | R1-B |
| Fixture integrity review | DeepSeek | R1-C |
| `tests/bernie_scenarios/*.py` | Claude/harness | R1-A |

Antigravity should add corpus scenario files directly to `tests/fixtures/bernie_scenarios/`.
The harness will discover them automatically at collection time.
