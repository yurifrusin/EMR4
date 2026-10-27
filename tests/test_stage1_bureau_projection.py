"""Focused source-bound reply projection; no application, DB or provider import."""
import ast
import copy
from datetime import date, time
import hashlib
from pathlib import Path
import re
import unittest
from typing import Any
from typing import Literal, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field, ValidationError


source = Path(__file__).resolve().parents[1] / "stage1_demo_http.py"
tree = ast.parse(source.read_text(encoding="utf-8"))
nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)
         and node.name in {"local_minute", "project_bureau_move"}]
assert {node.name for node in nodes} == {"local_minute", "project_bureau_move"}
namespace = {"Any": Any, "date": date, "re": re, "hashlib": hashlib,
             "LOCAL_MINUTE": re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d(?::00(?:\.0+)?)?\Z")}
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)
project = namespace["project_bureau_move"]
REQUEST_CORRELATION_ID = "11111111-1111-4111-8111-111111111111"
NEXT_CORRELATION_ID = "22222222-2222-4222-8222-222222222222"

# Read only the response contract and trusted compose tail, without importing
# application modules, starting the route or exercising database/admission code.
schema_source = source.parent / "app/schemas/appointments.py"
schema_tree = ast.parse(schema_source.read_text(encoding="utf-8"))
schema_names = {"ReceptionOneProductContextRequestIn", "ReceptionOneProductContextReviewOut",
                "ReceptionOneProductContextSlotOut", "ReceptionOneProductContextAppointmentOut",
                "ReceptionOneProductContextAdapterReviewOut", "ReceptionOneProductContextProposalOut"}
schema_nodes = [node for node in schema_tree.body
                if isinstance(node, ast.ClassDef) and node.name in schema_names]
assert {node.name for node in schema_nodes} == schema_names
schema_namespace = {"__name__": __name__, "BaseModel": BaseModel, "ConfigDict": ConfigDict, "Field": Field,
                    "Literal": Literal, "Optional": Optional, "date": date,
                    "time": time, "uuid": uuid}
exec(compile(ast.Module(body=schema_nodes, type_ignores=[]), str(schema_source), "exec"),
     schema_namespace)
ProposalOut = schema_namespace["ReceptionOneProductContextProposalOut"]
RequestIn = schema_namespace["ReceptionOneProductContextRequestIn"]

router_source = source.parent / "app/routers/appointments.py"
router_tree = ast.parse(router_source.read_text(encoding="utf-8"))
compose_nodes = [node for node in router_tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == "compose_reception_one_product_context_proposal"]
assert len(compose_nodes) == 1
compose = compose_nodes[0]
tail_starts = [index for index, node in enumerate(compose.body)
               if isinstance(node, (ast.Assign, ast.Return)) and isinstance(node.value, ast.Call)
               and isinstance(node.value.func, ast.Name)
               and node.value.func.id == "build_reviewed_proposal_result"]
assert len(tail_starts) == 1
tail = ast.FunctionDef(name="trusted_compose_tail",
    args=ast.arguments(posonlyargs=[], args=[ast.arg(arg="body")],
                       vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
    body=copy.deepcopy(compose.body[tail_starts[0]:]), decorator_list=[], type_params=[])
tail_module = ast.fix_missing_locations(ast.Module(body=[tail], type_ignores=[]))
route_namespace = {"hashlib": hashlib, "ReceptionOneProductContextProposalOut": ProposalOut,
                   "frame": None, "displays": None, "normalized_plan": None,
                   "review": None, "execution": None, "adapter_review": None,
                   "provider_calls": 0, "runtime_audit_ref": None}
route_namespace["build_reviewed_proposal_result"] = lambda **unused: route_namespace["prepared"]
exec(compile(tail_module, str(router_source), "exec"), route_namespace)


def trusted_compose(prepared, correlation_id=REQUEST_CORRELATION_ID):
    route_namespace["prepared"] = prepared
    body = RequestIn(instruction="Move this appointment to Thursday at three pm.",
                     reference_date="2026-10-27", correlation_id=correlation_id)
    return route_namespace["trusted_compose_tail"](body)


def fixture():
    current = {"ref": "synthetic-appointment", "state_version": 4, "date": "2026-10-27",
               "start_local": "14:00", "duration_minutes": 30, "status": "Booked",
               "patient_label": "Alex Chen", "practitioner_label": "Mira Rao"}
    slot = {"slot_handle": "synthetic-slot-0123456789abcdef0123",
            "appointment_date": "2026-10-28", "start_time_local": "14:00:00",
            "duration_minutes": 30, "warning_codes": []}
    reply = {"contract_version": "reception.one.product-context-proposal.v1",
             "result": "proposal_ready", "planner_mode": "deterministic",
             "data_class": "authored_synthetic",
             "summary": "One current move option; nothing has changed.",
             "request_id": "synthetic-request-0123456789abcdef0123",
             "correlation_id": "synthetic-correlation-0123456789abcdef0123",
             "request_correlation_sha256": hashlib.sha256(
                 REQUEST_CORRELATION_ID.encode("utf-8")).hexdigest(),
             "operation_id": "proposeAppointmentUpdate", "safe": True,
             "requires_confirmation": True, "proposal_only": True,
             "database_reads_performed": True, "write_performed": False,
             "confirmation_performed": False, "model_database_access": False,
             "legacy_interpreter_gate_changed": False, "provider_calls": 0,
             "warning_codes": ["staff_confirmation_required", "staff_selection_required"], "context_revision": 3,
             "review": {"disposition": "admit", "context_revision": 3},
             "selected_appointment": {"appointment_handle": "synthetic-appointment-0123456789abcdef0123",
                 "appointment_date": current["date"],
                 "start_time_local": "14:00:00", "duration_minutes": 30, "status": "booked"},
             "patient_display": current["patient_label"],
             "practitioner_display": current["practitioner_label"],
             "candidate_slots": [slot], "proposed_appointment_date": "2026-10-28",
             "proposed_start_time_local": "14:00:00", "proposed_duration_minutes": 30,
             "adapter_review": {"adapter_kind": "update_proposal", "summary": "One reviewed move option; no write authority.", "performed": True,
                 "safe": True, "freshness_verified": True, "confirmation_evidence_released": False,
                 "write_performed": False, "warning_codes": [], "block_codes": [], "candidate_count": 1}}
    return current, reply


class BureauProjectionTests(unittest.TestCase):
    def test_one_reviewed_option_projects_only_editable_details(self):
        current, reply = fixture()
        before = copy.deepcopy(reply)
        self.assertEqual(project(reply, current, REQUEST_CORRELATION_ID),
                         {"target_date": "2026-10-28", "target_start_local": "14:00"})
        self.assertEqual(reply, before)

    def test_multiple_options_are_not_an_implicit_first_choice(self):
        current, reply = fixture()
        reply["candidate_slots"].append({**reply["candidate_slots"][0], "start_time_local": "15:00:00"})
        reply["adapter_review"]["candidate_count"] = 2
        self.assertIsNone(project(reply, current, REQUEST_CORRELATION_ID))

    def test_unreserved_notice_is_projected_with_no_write_authority(self):
        current, reply = fixture()
        reply["warning_codes"].append("no_reservation")
        reply["candidate_slots"][0]["warning_codes"] = ["no_reservation"]
        self.assertEqual(project(reply, current, REQUEST_CORRELATION_ID),
                         {"target_date": "2026-10-28", "target_start_local": "14:00"})

    def test_bureau_labels_are_not_identity_evidence_or_released_content(self):
        current, reply = fixture()
        reply["practitioner_display"] = "Dr Rao"
        reply["patient_display"] = "Untrusted presentation text"
        self.assertEqual(project(reply, current, REQUEST_CORRELATION_ID),
                         {"target_date": "2026-10-28", "target_start_local": "14:00"})

    def test_domain_and_bureau_status_vocabulary_is_exact(self):
        for wrong in ("booked", "BOOKED", " Booked", "Cancelled", None, True, []):
            with self.subTest(current_status=wrong):
                current, reply = fixture()
                current["status"] = wrong
                self.assertIsNone(project(reply, current, REQUEST_CORRELATION_ID))
        for wrong in ("Booked", "BOOKED", " booked", "cancelled", None, True, []):
            with self.subTest(bureau_status=wrong):
                current, reply = fixture()
                reply["selected_appointment"]["status"] = wrong
                self.assertIsNone(project(reply, current, REQUEST_CORRELATION_ID))
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
                self.assertIsNone(project(reply, current, REQUEST_CORRELATION_ID))

    def test_binding_is_required_and_exactly_the_current_request_digest(self):
        for value in (None, True, 0, [], {}, b"a" * 64, "a" * 63, "a" * 65,
                      "A" * 64, "g" * 64, "0" * 64, "a" * 64 + "\n"):
            with self.subTest(value=value):
                current, reply = fixture()
                reply["request_correlation_sha256"] = value
                self.assertIsNone(project(reply, current, REQUEST_CORRELATION_ID))
        current, reply = fixture()
        del reply["request_correlation_sha256"]
        self.assertIsNone(project(reply, current, REQUEST_CORRELATION_ID))

    def test_a_prior_request_reply_cannot_bind_to_a_fresh_nonce(self):
        current, reply = fixture()
        self.assertEqual(project(reply, current, REQUEST_CORRELATION_ID),
                         {"target_date": "2026-10-28", "target_start_local": "14:00"})
        self.assertIsNone(project(reply, current, NEXT_CORRELATION_ID))

    def test_privacy_handle_must_keep_the_actual_bureau_shape(self):
        for handle in (REQUEST_CORRELATION_ID, "synthetic-correlation",
                       "synthetic-correlation-" + "A" * 20,
                       "synthetic-correlation-" + "a" * 19,
                       "synthetic-correlation-" + "a" * 21,
                       "synthetic-correlation-" + "g" * 20,
                       "synthetic-correlation-" + "a" * 20 + "\n", None, True):
            with self.subTest(handle=handle):
                current, reply = fixture()
                reply["correlation_id"] = handle
                self.assertIsNone(project(reply, current, REQUEST_CORRELATION_ID))

    def test_optional_typed_binding_preserves_pure_helper_construction(self):
        _, reply = fixture()
        del reply["request_correlation_sha256"]
        self.assertIsNone(ProposalOut.model_validate(reply).request_correlation_sha256)
        reply["request_correlation_sha256"] = None
        self.assertIsNone(ProposalOut.model_validate(reply).request_correlation_sha256)
        for value in (True, 0, [], {}, b"a" * 64, "a" * 63, "a" * 65,
                      "A" * 64, "g" * 64, "a" * 64 + "\n"):
            with self.subTest(value=value):
                reply["request_correlation_sha256"] = value
                with self.assertRaises(ValidationError):
                    ProposalOut.model_validate(reply)

    def test_trusted_route_overwrites_binding_and_preserves_opaque_correlation(self):
        current, reply = fixture()
        reply["request_correlation_sha256"] = "f" * 64
        prepared = ProposalOut.model_validate(reply)
        bound = trusted_compose(prepared)
        self.assertEqual(bound.request_correlation_sha256,
                         hashlib.sha256(REQUEST_CORRELATION_ID.encode("utf-8")).hexdigest())
        self.assertEqual(bound.correlation_id, reply["correlation_id"])
        self.assertEqual(prepared.request_correlation_sha256, "f" * 64)
        self.assertEqual(project(bound.model_dump(mode="json"), current, REQUEST_CORRELATION_ID),
                         {"target_date": "2026-10-28", "target_start_local": "14:00"})

    def test_trusted_route_binds_every_typed_disposition_and_request_separately(self):
        for result in ("proposal_ready", "clarification_required", "revision_required", "blocked"):
            with self.subTest(result=result):
                _, reply = fixture()
                reply["result"] = result
                prepared = ProposalOut.model_validate(reply)
                bound = trusted_compose(prepared, NEXT_CORRELATION_ID)
                self.assertEqual(bound.result, result)
                self.assertEqual(bound.request_correlation_sha256,
                                 hashlib.sha256(NEXT_CORRELATION_ID.encode("utf-8")).hexdigest())

    def test_trusted_route_revalidates_the_whole_output(self):
        _, reply = fixture()
        reply["candidate_slots"][0]["duration_minutes"] = "not-an-integer"

        class InvalidPreparedResult:
            def model_dump(self):
                return copy.deepcopy(reply)

        with self.assertRaises(ValidationError) as caught:
            trusted_compose(InvalidPreparedResult())
        self.assertIn(("candidate_slots", 0, "duration_minutes"),
                      {tuple(error["loc"]) for error in caught.exception.errors()})

    def test_request_schema_does_not_admit_caller_chosen_response_binding(self):
        with self.assertRaises(ValidationError):
            RequestIn(instruction="Move this appointment to Thursday at three pm.",
                      reference_date="2026-10-27", correlation_id=REQUEST_CORRELATION_ID,
                      request_correlation_sha256="f" * 64)


if __name__ == "__main__":
    unittest.main()
