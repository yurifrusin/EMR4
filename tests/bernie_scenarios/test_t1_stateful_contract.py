from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.bernie_scenarios.loader import load_scenario_yaml
from tests.bernie_scenarios.replay import ReplayResult, write_evidence_record


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "scenario.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_loader_accepts_seeded_state_supervise_and_per_turn_deltas(tmp_path):
    scenario = load_scenario_yaml(_write(tmp_path, """
id: stateful-contract
category: booking_confirmation
reference_date: 2026-07-13
initial_state:
  simulated_clinic_time: "08:30"
  seeded_appointments:
    - id: existing
      patient: Margaret Thompson
      practitioner: Dr Shera
      date: 2026-07-14
      time: "15:00"
      duration_minutes: 15
      status: Booked
turns:
  - action: supervise
    input:
      command:
        practitioner_id: "{practitioner_id}"
        patient_id: "{patient_id}"
        date_from: 2026-07-14
        earliest_time: "15:00"
        duration_minutes: 15
    expect:
      appointment_delta: 0
      audit_delta: 0
"""))

    assert scenario.turns[0].action == "supervise"
    assert scenario.turns[0].expect.appointment_delta == 0
    assert scenario.initial_state["seeded_appointments"][0]["id"] == "existing"


@pytest.mark.parametrize("fragment", ["unsupported: true", "duration_minutes: 0"])
def test_loader_rejects_unsafe_seed_shapes(tmp_path, fragment):
    with pytest.raises(ValueError):
        load_scenario_yaml(_write(tmp_path, f"""
id: bad-state
category: booking_confirmation
reference_date: 2026-07-13
initial_state:
  seeded_appointments:
    - date: 2026-07-14
      time: "15:00"
      {fragment}
turns:
  - action: supervise
    expect: {{}}
"""))


def test_evidence_writer_emits_only_redacted_contract(tmp_path):
    result = ReplayResult(
        scenario_id="safe-evidence",
        passed=True,
        evidence=["raw internal evidence must not be serialized"],
        evidence_record={
            "schema_version": "bernie.scenario.evidence.v1",
            "scenario_id": "safe-evidence",
            "raw_instruction_included": False,
            "raw_response_included": False,
            "passed": True,
        },
    )
    path = write_evidence_record(result, tmp_path / "evidence.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload == result.evidence_record
    assert "raw internal evidence" not in path.read_text(encoding="utf-8")


# ─── external_appointment loader validation ───────────────────────────────


def test_loader_accepts_external_appointment_create(tmp_path):
    scenario = load_scenario_yaml(_write(tmp_path, """
id: ext-create
category: booking_create
reference_date: 2026-07-13
initial_state: {}
turns:
  - action: external_appointment
    input:
      operation: create
      patient: Margaret Thompson
      practitioner: Dr Shera
      date: "2026-07-14"
      time: "15:00"
      duration_minutes: 30
      status: Booked
      id: ext-appt
    expect:
      appointment_delta: 0
      audit_delta: 0
"""))
    turn = scenario.turns[0]
    assert turn.action == "external_appointment"
    assert turn.input["operation"] == "create"
    assert turn.input["id"] == "ext-appt"


def test_loader_accepts_external_appointment_set_status(tmp_path):
    scenario = load_scenario_yaml(_write(tmp_path, """
id: ext-set-status
category: booking_create
reference_date: 2026-07-13
initial_state: {}
turns:
  - action: external_appointment
    input:
      operation: set_status
      appointment_id: existing
      status: Cancelled
    expect:
      appointment_delta: 0
      audit_delta: 0
"""))
    turn = scenario.turns[0]
    assert turn.action == "external_appointment"
    assert turn.input["operation"] == "set_status"
    assert turn.input["appointment_id"] == "existing"


@pytest.mark.parametrize("bad_op", ["delete", "update", "patch", ""])
def test_loader_rejects_unknown_external_operation(tmp_path, bad_op):
    with pytest.raises(ValueError, match="operation"):
        load_scenario_yaml(_write(tmp_path, f"""
id: bad-ext-op
category: booking_create
reference_date: 2026-07-13
initial_state: {{}}
turns:
  - action: external_appointment
    input:
      operation: {bad_op!r}
      date: "2026-07-14"
      time: "15:00"
    expect: {{}}
"""))


def test_loader_rejects_external_create_missing_date(tmp_path):
    with pytest.raises(ValueError, match="date"):
        load_scenario_yaml(_write(tmp_path, """
id: ext-no-date
category: booking_create
reference_date: 2026-07-13
initial_state: {}
turns:
  - action: external_appointment
    input:
      operation: create
      time: "15:00"
    expect: {}
"""))


def test_loader_rejects_external_set_status_missing_appointment_id(tmp_path):
    with pytest.raises(ValueError, match="appointment_id"):
        load_scenario_yaml(_write(tmp_path, """
id: ext-no-aid
category: booking_create
reference_date: 2026-07-13
initial_state: {}
turns:
  - action: external_appointment
    input:
      operation: set_status
      status: Cancelled
    expect: {}
"""))


def test_loader_rejects_external_unsupported_fields(tmp_path):
    with pytest.raises(ValueError, match="unsupported"):
        load_scenario_yaml(_write(tmp_path, """
id: ext-unsupported
category: booking_create
reference_date: 2026-07-13
initial_state: {}
turns:
  - action: external_appointment
    input:
      operation: create
      date: "2026-07-14"
      time: "15:00"
      arbitrary_field: true
    expect: {}
"""))


def test_loader_rejects_external_create_zero_duration(tmp_path):
    with pytest.raises(ValueError, match="duration_minutes"):
        load_scenario_yaml(_write(tmp_path, """
id: ext-zero-dur
category: booking_create
reference_date: 2026-07-13
initial_state: {}
turns:
  - action: external_appointment
    input:
      operation: create
      date: "2026-07-14"
      time: "15:00"
      duration_minutes: 0
    expect: {}
"""))
