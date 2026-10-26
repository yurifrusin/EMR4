"""Synthetic selected-context move checks; no product data or write path."""

from __future__ import annotations

import copy
from datetime import date, time
from types import SimpleNamespace
import uuid

import pytest

from scripts import reception_one_bureau_typed_plan_protocol as bureau
from app.models.appointments import Appointment
from app.models.patients import Patient
from app.models.tenancy import Practitioner
from app.services.reception_one_proposal_runtime import (
    ReceptionOneRuntimeError,
    _read_selected_appointment,
    build_slot_search_input,
)


PATIENT = "synthetic-patient-selected"
OTHER = "synthetic-patient-other"
PRACTITIONER = "synthetic-practitioner-selected"
APPOINTMENT = "synthetic-appointment-selected"
SLOT = "synthetic-slot-target"


def frame(instruction: str) -> dict:
    context = {
        "patients": [
            {"id": PATIENT, "display": "Avery Quinn", "aliases": ["Avery"]},
            {"id": OTHER, "display": "Jordan Vale", "aliases": ["Jordan"]},
        ],
        "practitioners": [
            {"id": PRACTITIONER, "display": "Dr Chen", "aliases": ["Dr Mira Chen", "Chen"]},
        ],
        "selected_appointment": {
            "id": APPOINTMENT,
            "patient_ref": PATIENT,
            "practitioner_ref": PRACTITIONER,
            "date": "2026-07-29",
            "start_time": "09:00",
            "duration_minutes": 15,
            "status": "booked",
        },
        "appointments": [],
        "candidate_slots": [],
        "squeeze_policy": {
            "id": "synthetic-policy-squeeze-review",
            "assessment_enabled": True,
            "allow_move_existing": False,
            "allow_overbook": False,
            "requires_human_review": True,
        },
        "default_duration_minutes": 15,
        "allowed_statuses": ["arrived", "completed", "dna"],
    }
    result = {
        "contract_version": "reception.one.bureau.plan-input.v1",
        "request_id": "synthetic-request-selected",
        "practice_ref": "synthetic-practice-one",
        "correlation_id": "synthetic-correlation-one",
        "context_revision": 12,
        "observed_at": "2026-07-29T00:30:00Z",
        "expires_at": "2026-07-29T00:32:00Z",
        "data_class": "authored_synthetic",
        "utterances": [instruction],
        "reference_date": "2026-07-29",
        "context": context,
        "authority": {
            "effect_ceiling": "proposal_only",
            "appointment_write_authority": False,
            "confirmation_authority": False,
            "provider_execution": False,
            "network_access": False,
            "database_access": False,
            "product_delivery": False,
        },
    }
    extraction = bureau.extraction_for(result)
    if extraction.normalized_values.get("appointment_date") and extraction.normalized_values.get("earliest_time"):
        context["candidate_slots"] = [{
            "id": SLOT,
            "practitioner_ref": PRACTITIONER,
            "date": extraction.normalized_values["appointment_date"],
            "start_time": extraction.normalized_values["earliest_time"],
            "duration_minutes": 15,
            "classification": "available",
            "warning_codes": ["no_reservation"],
        }]
    return result


def test_selected_only_move_keeps_opaque_identity_and_proposal_ceiling():
    source = frame("Move this appointment to Tuesday at 2 pm")
    assert bureau.selected_move_subject(source, bureau.extraction_for(source)) == "selected_only"
    plan = bureau.deterministic_plan(source)
    selected_step = next(step for step in plan["steps"] if step["operator"] == "read_selected_appointment")
    assert set(selected_step["args"]) == {"appointment"}
    review, normalized = bureau.proofread_plan(source, plan)
    assert review["disposition"] == "admit"
    result = bureau.execute_plan(source, normalized, review)["final_output"]
    assert (result["appointment_ref"], result["patient_ref"], result["practitioner_ref"]) == (APPOINTMENT, PATIENT, PRACTITIONER)
    assert result["candidate_slot_ids"] == [SLOT]
    assert result["write_performed"] is False
    assert result["requires_human_confirmation"] is True
    selected_patient = uuid.uuid4()
    selected_practitioner = uuid.uuid4()
    search = build_slot_search_input(source, {
        PATIENT: selected_patient,
        PRACTITIONER: selected_practitioner,
    })
    assert search is not None
    assert search.patient_id == selected_patient
    assert search.practitioner_id == selected_practitioner
    assert search.duration_minutes == 15


def test_spoken_time_uses_existing_normalization_without_rewriting_words():
    words = "Move this appointment to Wednesday at two pm"
    source = frame(words)
    extraction = bureau.extraction_for(source)
    assert source["utterances"] == [words]
    assert extraction.normalized_values["earliest_time"] == "14:00"
    assert bureau.selected_move_subject(source, extraction) == "selected_only"
    review, _ = bureau.proofread_plan(source, bureau.deterministic_plan(source))
    assert review["disposition"] == "admit"


@pytest.mark.parametrize("instruction", [
    "Move disappointments to Tuesday at 2 pm",
    "Move this appointment to Tuesday at 2 pm for Alex",
    "Move this appointment to Tuesday at 2 pm for Jordan Vale",
    "Move Avery Quinn's appointment to Tuesday at 2 pm for Alex",
    "Move Avery Quinn's appointment to Tuesday at 2 pm with Jordan's booking",
    "Move Avery Quinn or Jordan Vale's appointment to Tuesday at 2 pm",
    "Move not for Avery Quinn to Tuesday at 2 pm",
])
def test_uncertain_or_conflicting_subject_releases_no_move(instruction):
    source = frame(instruction)
    assert source["utterances"] == [instruction]
    assert bureau.selected_move_subject(source, bureau.extraction_for(source)) is None
    plan = bureau.deterministic_plan(source)
    review, _ = bureau.proofread_plan(source, plan)
    assert review["disposition"] != "admit"
    assert build_slot_search_input(source, {PATIENT: uuid.uuid4(), PRACTITIONER: uuid.uuid4()}) is None


def test_untrusted_plan_cannot_omit_patient_to_override_spoken_identity():
    source = frame("Move this appointment to Tuesday at 2 pm")
    plan = bureau.deterministic_plan(source)
    plan["planner_class"] = "untrusted_model_candidate"
    source["utterances"] = ["Move Jordan Vale's appointment to Tuesday at 2 pm"]
    review, _ = bureau.proofread_plan(source, plan)
    assert review["disposition"] == "reject"
    assert "selected_identity_conflict" in {item["code"] for item in review["violations"]}


def test_untrusted_move_operator_cannot_claim_another_goal():
    source = frame("Move this appointment to Tuesday at 2 pm")
    plan = bureau.deterministic_plan(source)
    plan["planner_class"] = "untrusted_model_candidate"
    plan["goal"] = "create"
    review, _ = bureau.proofread_plan(source, plan)
    assert review["disposition"] == "reject"
    assert "selected_operation_mismatch" in {item["code"] for item in review["violations"]}


@pytest.mark.parametrize("goal,operator,suffix", [
    ("cancel", "prepare_cancel_proposal", ""),
    ("resize", "prepare_resize_proposal", ""),
    ("status_change", "prepare_status_proposal", "; completed"),
])
def test_untrusted_optional_selected_read_cannot_change_operation(goal, operator, suffix):
    source = frame("Move this appointment to Tuesday at 2 pm" + suffix)
    assert bureau.extraction_for(source).intended_action == "move"
    plan = bureau.base_plan(source, planner_class="untrusted_model_candidate", goal=goal)
    proposal_args = {"appointment": bureau.step_binding("step-selected", "appointment")}
    if goal == "resize":
        proposal_args["duration_minutes"] = bureau.context_binding("default_duration_minutes")
    if goal == "status_change":
        proposal_args["status"] = bureau.mention_binding(source, "status")
    plan["steps"] = [
        {
            "id": "step-selected",
            "operator": "read_selected_appointment",
            "args": {"appointment": bureau.context_binding("selected_appointment")},
        },
        {"id": "step-proposal", "operator": operator, "args": proposal_args},
    ]
    review, _ = bureau.proofread_plan(source, plan)
    assert review["disposition"] == "reject"
    assert "selected_operation_mismatch" in {item["code"] for item in review["violations"]}


def test_matching_named_legacy_read_keeps_patient_equality_guard():
    source = frame("Move Avery Quinn's appointment to Tuesday at 2 pm")
    assert bureau.selected_move_subject(source, bureau.extraction_for(source)) == "named"
    plan = bureau.deterministic_plan(source)
    selected_step = next(step for step in plan["steps"] if step["operator"] == "read_selected_appointment")
    assert set(selected_step["args"]) == {"patient", "appointment"}
    review, _ = bureau.proofread_plan(source, plan)
    assert review["disposition"] == "admit"
    with pytest.raises(ValueError, match="patient binding"):
        bureau.execute_operator("read_selected_appointment", {
            "patient": OTHER,
            "appointment": source["context"]["selected_appointment"],
        }, source)


def test_matching_patient_and_practitioner_names_remain_grounded():
    source = frame("Move Avery Quinn's appointment with Dr Chen to Tuesday at 2 pm")
    assert bureau.selected_move_subject(source, bureau.extraction_for(source)) == "named"
    plan = bureau.deterministic_plan(source)
    review, _ = bureau.proofread_plan(source, plan)
    assert review["disposition"] == "admit"


def test_legacy_named_cancel_still_uses_required_patient_binding():
    source = frame("Cancel Avery Quinn's appointment")
    plan = bureau.deterministic_plan(source)
    selected_step = next(step for step in plan["steps"] if step["operator"] == "read_selected_appointment")
    assert "patient" in selected_step["args"]
    review, _ = bureau.proofread_plan(source, plan)
    assert review["disposition"] == "admit"


def test_selected_move_still_rejects_stale_context_and_open_authority():
    source = frame("Move this appointment to Tuesday at 2 pm")
    plan = bureau.deterministic_plan(source)
    stale = copy.deepcopy(plan)
    stale["context_revision"] -= 1
    review, _ = bureau.proofread_plan(source, stale)
    assert review["disposition"] == "reject"
    assert "stale_context" in {item["code"] for item in review["violations"]}
    opened = copy.deepcopy(source)
    opened["authority"]["confirmation_authority"] = True
    review, _ = bureau.proofread_plan(opened, plan)
    assert review["disposition"] == "reject"


class _ScopedQuery:
    def __init__(self, model, row, practice_id):
        self.model = model
        self.row = row
        self.practice_id = practice_id

    def filter(self, *clauses):
        rendered = " ".join(str(clause) for clause in clauses)
        values = [value for clause in clauses for value in clause.compile().params.values()]
        assert "practice_id" in rendered
        assert self.practice_id in values
        return self

    def first(self):
        return self.row if self.row.practice_id == self.practice_id else None


class _ScopedSession:
    def __init__(self, rows, practice_id):
        self.rows = rows
        self.practice_id = practice_id

    def query(self, model):
        return _ScopedQuery(model, self.rows[model], self.practice_id)


def test_selected_row_resolves_unspoken_parties_in_practice_scope():
    practice_id = uuid.uuid4()
    appointment_id, patient_id, practitioner_id = (uuid.uuid4() for _ in range(3))
    rows = {
        Appointment: SimpleNamespace(
            id=appointment_id, practice_id=practice_id, patient_id=patient_id,
            practitioner_id=practitioner_id, appointment_date=date(2026, 7, 29),
            start_time_local=time(9, 0), duration_minutes=15, status="Booked",
        ),
        Patient: SimpleNamespace(
            id=patient_id, practice_id=practice_id, first_name="Avery",
            last_name="Quinn", is_active=True,
        ),
        Practitioner: SimpleNamespace(
            id=practitioner_id, practice_id=practice_id, first_name="Mira",
            last_name="Chen", is_active=True,
        ),
    }
    patients, practitioners, handles = [], [], {}
    selected = _read_selected_appointment(
        _ScopedSession(rows, practice_id), practice_id=practice_id,
        appointment_id=appointment_id, handle_key=b"synthetic-request-key",
        handle_map=handles, patients=patients, practitioners=practitioners,
        allow_unmentioned_parties=True,
    )
    assert handles[selected["id"]] == appointment_id
    assert handles[selected["patient_ref"]] == patient_id
    assert handles[selected["practitioner_ref"]] == practitioner_id
    assert patients[0]["display"] == "Avery Quinn"
    assert practitioners[0]["display"] == "Dr Chen"
    other_practice_id = uuid.uuid4()
    with pytest.raises(ReceptionOneRuntimeError, match="selected_appointment_not_found"):
        _read_selected_appointment(
            _ScopedSession(rows, other_practice_id), practice_id=other_practice_id,
            appointment_id=appointment_id, handle_key=b"synthetic-request-key",
            handle_map={}, patients=[], practitioners=[],
            allow_unmentioned_parties=True,
        )
