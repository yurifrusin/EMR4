"""Focused source-bound reply projection; no application, DB or provider import."""
import ast
import copy
from datetime import date
from pathlib import Path
import re
import unittest
from typing import Any


source = Path(__file__).resolve().parents[1] / "stage1_demo_http.py"
tree = ast.parse(source.read_text(encoding="utf-8"))
nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)
         and node.name in {"local_minute", "project_bureau_move"}]
assert {node.name for node in nodes} == {"local_minute", "project_bureau_move"}
namespace = {"Any": Any, "date": date,
             "LOCAL_MINUTE": re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d(?::00(?:\.0+)?)?\Z")}
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)
project = namespace["project_bureau_move"]


def fixture():
    current = {"ref": "synthetic-appointment", "state_version": 4, "date": "2026-10-27",
               "start_local": "14:00", "duration_minutes": 30, "status": "booked",
               "patient_label": "Alex Chen", "practitioner_label": "Mira Rao"}
    slot = {"appointment_date": "2026-10-28", "start_time_local": "14:00:00",
            "duration_minutes": 30, "warning_codes": []}
    reply = {"contract_version": "reception.one.product-context-proposal.v1",
             "result": "proposal_ready", "planner_mode": "deterministic",
             "data_class": "authored_synthetic", "correlation_id": "synthetic-correlation",
             "operation_id": "proposeAppointmentUpdate", "safe": True,
             "requires_confirmation": True, "proposal_only": True,
             "database_reads_performed": True, "write_performed": False,
             "confirmation_performed": False, "model_database_access": False,
             "legacy_interpreter_gate_changed": False, "provider_calls": 0,
             "warning_codes": ["staff_confirmation_required", "staff_selection_required"], "context_revision": 3,
             "review": {"disposition": "admit", "context_revision": 3},
             "selected_appointment": {"appointment_date": current["date"],
                 "start_time_local": "14:00:00", "duration_minutes": 30, "status": "booked"},
             "patient_display": current["patient_label"],
             "practitioner_display": current["practitioner_label"],
             "candidate_slots": [slot], "proposed_appointment_date": "2026-10-28",
             "proposed_start_time_local": "14:00:00", "proposed_duration_minutes": 30,
             "adapter_review": {"adapter_kind": "update_proposal", "performed": True,
                 "safe": True, "freshness_verified": True, "confirmation_evidence_released": False,
                 "write_performed": False, "warning_codes": [], "block_codes": [], "candidate_count": 1}}
    return current, reply


class BureauProjectionTests(unittest.TestCase):
    def test_one_reviewed_option_projects_only_editable_details(self):
        current, reply = fixture()
        before = copy.deepcopy(reply)
        self.assertEqual(project(reply, current, "synthetic-correlation"),
                         {"target_date": "2026-10-28", "target_start_local": "14:00"})
        self.assertEqual(reply, before)

    def test_multiple_options_are_not_an_implicit_first_choice(self):
        current, reply = fixture()
        reply["candidate_slots"].append({**reply["candidate_slots"][0], "start_time_local": "15:00:00"})
        reply["adapter_review"]["candidate_count"] = 2
        self.assertIsNone(project(reply, current, "synthetic-correlation"))

    def test_unreserved_notice_is_projected_with_no_write_authority(self):
        current, reply = fixture()
        reply["warning_codes"].append("no_reservation")
        reply["candidate_slots"][0]["warning_codes"] = ["no_reservation"]
        self.assertEqual(project(reply, current, "synthetic-correlation"),
                         {"target_date": "2026-10-28", "target_start_local": "14:00"})

    def test_bureau_labels_are_not_identity_evidence_or_released_content(self):
        current, reply = fixture()
        reply["practitioner_display"] = "Dr Rao"
        reply["patient_display"] = "Untrusted presentation text"
        self.assertEqual(project(reply, current, "synthetic-correlation"),
                         {"target_date": "2026-10-28", "target_start_local": "14:00"})

    def test_rejected_or_wrong_authority_replies_release_no_fields(self):
        changes = [
            lambda r: r.update(result="clarification_required"),
            lambda r: r.update(planner_mode="isolated_vertex"),
            lambda r: r.update(provider_calls=1),
            lambda r: r.update(provider_calls=False),
            lambda r: r.update(write_performed=True),
            lambda r: r.update(requires_confirmation=False),
            lambda r: r.update(correlation_id="other-request"),
            lambda r: r.update(operation_id="proposeAppointmentDelete"),
            lambda r: r.update(warning_codes=["NEEDS_REVIEW"]),
            lambda r: r.update(warning_codes=[]),
            lambda r: r.update(warning_codes=["staff_confirmation_required"]),
            lambda r: r["warning_codes"].append("UNREVIEWED_WARNING"),
            lambda r: r["review"].update(context_revision=2),
            lambda r: r["review"].update(context_revision=True),
            lambda r: r["review"].update(disposition="reject"),
            lambda r: r["selected_appointment"].update(appointment_date="2026-10-26"),
            lambda r: r.update(adapter_review=None),
            lambda r: r["adapter_review"].update(freshness_verified=False),
            lambda r: r["adapter_review"].update(confirmation_evidence_released=True),
            lambda r: r.update(proposed_appointment_date="2026-02-30"),
            lambda r: r.update(proposed_start_time_local="25:00"),
            lambda r: r.update(proposed_duration_minutes=45),
            lambda r: r["candidate_slots"][0].update(start_time_local="15:00:00"),
        ]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                current, reply = fixture()
                change(reply)
                self.assertIsNone(project(reply, current, "synthetic-correlation"))


if __name__ == "__main__":
    unittest.main()
