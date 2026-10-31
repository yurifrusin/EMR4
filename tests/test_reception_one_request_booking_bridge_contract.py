"""Inert source contract tests for the request-booking semantic packet branch.

These tests use authored synthetic data only. They exercise compilation and
proposal-only proofing; they do not call an application, database, provider,
browser, or confirmation endpoint.
"""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from datetime import datetime, timezone

from scripts import reception_one_bureau_typed_plan_protocol as typedprotocol


NOW = datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc)
FRAME_VERSION = "reception.one.bureau.plan-input.request-booking.v1"
PACKET_VERSION = "emr4.bureau_model_semantic_packet.request-booking.v1"
PLAN_VERSION = "reception.one.bureau.plan-draft.model-first.request-booking.v1"
CONSTRUCTOR_VERSION = "emr4.bureau_model_semantic_constructor.request-booking.v1"
CASE_ID = "synthetic-request-booking-case"
UTTERANCE = "Please book my submitted request."


def synthetic_frame() -> dict:
    return {
        "contract_version": FRAME_VERSION,
        "request_id": "synthetic-bureau-request-001",
        "practice_ref": "synthetic-practice-001",
        "correlation_id": "synthetic-correlation-001",
        "context_revision": 3,
        "observed_at": "2026-11-01T00:00:00Z",
        "expires_at": "2026-11-01T00:02:00Z",
        "data_class": "authored_synthetic",
        "utterances": [UTTERANCE],
        "reference_date": "2026-11-01",
        "context": {
            "patients": [{"id": "synthetic-patient-001", "display": "Patient One", "aliases": []}],
            "practitioners": [{"id": "synthetic-practitioner-001", "display": "Clinician One", "aliases": []}],
            "selected_appointment": None,
            "appointments": [],
            "candidate_slots": [],
            "squeeze_policy": {
                "id": "synthetic-squeeze-policy-001",
                "assessment_enabled": False,
                "allow_move_existing": False,
                "allow_overbook": False,
                "requires_human_review": True,
            },
            "default_duration_minutes": 30,
            "allowed_statuses": ["arrived", "completed", "dna"],
            "selected_request": {
                "request_ref": "synthetic-selected-request-001",
                "request_version": 4,
                "state": "submitted",
                "patient_ref": "synthetic-patient-001",
                "practitioner_ref": "synthetic-practitioner-001",
                "appointment_date": "2026-11-03",
                "earliest_time": "09:00",
                "latest_start_time": "11:00",
                "duration_minutes": 30,
                "timezone": "Australia/Brisbane",
            },
        },
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


def packet_for(frame: dict, action: str = "create", *, target_bindings=None) -> bytes:
    frame_hash = hashlib.sha256(
        json.dumps(frame, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    evidence = {"utterance_index": 0, "start": 0, "end": len(UTTERANCE), "text": UTTERANCE}
    packet = {
        "packet_schema": PACKET_VERSION,
        "case_id": CASE_ID,
        "interpretation": {
            "frame_sha256": frame_hash,
            "context_revision": frame["context_revision"],
            "reference_date": frame["reference_date"],
            "candidates": [{
                "id": "candidate-action",
                "field": "intended_action",
                "value": action,
                "evidence": evidence,
                "supersedes": [],
            }],
            "selected": {"intended_action": "candidate-action"},
        },
        "target_bindings": target_bindings if target_bindings is not None else (
            {"selected_request": {"kind": "context_ref", "field": "selected_request"}}
            if action == "create" else {}
        ),
    }
    return json.dumps(packet, separators=(",", ":")).encode("utf-8")


def compile_packet(frame: dict, raw: bytes | None = None):
    return typedprotocol.compile_model_semantic_packet(
        frame, raw if raw is not None else packet_for(frame), case_id=CASE_ID, now=NOW
    )


class TestRequestBookingBridgeContract(unittest.TestCase):
    def test_request_booking_create_compiles_to_grounded_proposal_only_chain(self):
        frame = synthetic_frame()
        result = compile_packet(frame)
        plan = result["plan"]

        self.assertEqual(typedprotocol.REQUEST_BOOKING_PACKET_VERSION, PACKET_VERSION)
        self.assertEqual(typedprotocol.REQUEST_BOOKING_PLAN_VERSION, PLAN_VERSION)
        self.assertEqual(typedprotocol.REQUEST_BOOKING_CONSTRUCTOR_VERSION, CONSTRUCTOR_VERSION)
        self.assertEqual(plan["contract_version"], PLAN_VERSION)
        self.assertEqual(plan["goal"], "create")
        self.assertEqual(plan["effect_ceiling"], "proposal_only")
        self.assertEqual([step["operator"] for step in plan["steps"]], [
            "search_available_slots", "prepare_create_proposal"
        ])
        self.assertEqual(plan["steps"][0]["id"], "step-01-request-search")
        self.assertEqual(plan["steps"][1]["id"], "step-02-request-create")
        self.assertEqual(plan["steps"][0]["args"]["practitioner"], {
            "kind": "context_ref", "field": "selected_request.practitioner_ref"
        })
        self.assertEqual(plan["steps"][1]["args"]["patient"], {
            "kind": "context_ref", "field": "selected_request.patient_ref"
        })
        self.assertEqual(plan["steps"][1]["args"]["candidates"], {
            "kind": "step_output", "step_id": "step-01-request-search", "output": "candidates"
        })
        self.assertEqual(result["review"]["disposition"], "admit")
        self.assertIs(result["review"]["execution_authorized"], True)
        self.assertIs(result["execution_performed"], False)
        self.assertIs(result["confirmation_performed"], False)
        self.assertEqual(frame["context"]["selected_request"]["request_version"], 4)

    def test_packet_must_remain_bound_to_exact_frame_and_case(self):
        for mutation in ("case", "frame_hash", "context_revision", "reference_date"):
            with self.subTest(mutation=mutation):
                frame = synthetic_frame()
                packet = json.loads(packet_for(frame))
                if mutation == "case":
                    packet["case_id"] = "synthetic-other-case"
                elif mutation == "frame_hash":
                    packet["interpretation"]["frame_sha256"] = "0" * 64
                elif mutation == "context_revision":
                    packet["interpretation"]["context_revision"] += 1
                else:
                    packet["interpretation"]["reference_date"] = "2026-11-02"

                with self.assertRaises(typedprotocol.SemanticPacketRefusal):
                    compile_packet(frame, json.dumps(packet).encode("utf-8"))

    def test_create_requires_exact_request_target_role(self):
        targets_cases = (
            {},
            {"appointment": {"kind": "context_ref", "field": "selected_appointment"}},
            {"selected_request": {"kind": "context_ref", "field": "selected_request.patient_ref"}},
            {"selected_request": {"kind": "model_value", "field": "synthetic-patient-001"}},
        )
        for targets in targets_cases:
            with self.subTest(targets=targets):
                frame = synthetic_frame()
                with self.assertRaises(typedprotocol.SemanticPacketRefusal):
                    compile_packet(frame, packet_for(frame, target_bindings=targets))

    def test_request_identity_and_duration_are_not_model_editable(self):
        field_cases = (
            ("appointment_date", "2026-11-04"),
            ("duration_minutes", 60),
            ("patient_ref", "synthetic-other-patient"),
            ("practitioner_ref", "synthetic-other-practitioner"),
        )
        for field, value in field_cases:
            with self.subTest(field=field, value=value):
                frame = synthetic_frame()
                packet = json.loads(packet_for(frame))
                packet["interpretation"]["candidates"].append({
                    "id": "candidate-extra",
                    "field": field,
                    "value": value,
                    "evidence": {"utterance_index": 0, "start": 0, "end": len(UTTERANCE), "text": UTTERANCE},
                    "supersedes": [],
                })
                with self.assertRaises(typedprotocol.SemanticPacketRefusal):
                    compile_packet(frame, json.dumps(packet).encode("utf-8"))

    def test_selected_request_context_is_required_and_closed(self):
        frame = synthetic_frame()
        del frame["context"]["selected_request"]
        with self.assertRaises(typedprotocol.SemanticPacketRefusal):
            compile_packet(frame)

    def test_request_version_rejects_boolean_integer_alias(self):
        frame = synthetic_frame()
        frame["context"]["selected_request"]["request_version"] = True
        with self.assertRaises(typedprotocol.SemanticPacketRefusal):
            compile_packet(frame)

    def test_request_booking_frame_rejects_cross_family_selected_appointment(self):
        frame = synthetic_frame()
        frame["context"]["selected_appointment"] = {
            "id": "synthetic-appointment-001",
            "patient_ref": "synthetic-patient-001",
            "practitioner_ref": "synthetic-practitioner-001",
            "date": "2026-11-03",
            "start_time": "09:00",
            "duration_minutes": 30,
            "status": "booked",
        }
        with self.assertRaises(typedprotocol.SemanticPacketRefusal):
            compile_packet(frame)

    def test_forged_create_dataflow_is_rejected_by_proofreader(self):
        frame = synthetic_frame()
        plan = copy.deepcopy(compile_packet(frame)["plan"])
        plan["steps"][1]["args"]["candidates"] = {
            "kind": "context_ref", "field": "selected_request.request_ref"
        }

        review, _ = typedprotocol.proofread_plan(frame, plan, now=NOW)
        self.assertNotEqual(review["disposition"], "admit")

    def test_malformed_request_booking_lifetime_is_refused(self):
        frame = synthetic_frame()
        frame["expires_at"] = "2026-10-31T23:59:59Z"
        with self.assertRaises(typedprotocol.SemanticPacketRefusal):
            compile_packet(frame)

    def test_valid_request_booking_frame_refuses_at_original_expiry(self):
        frame = synthetic_frame()
        observed = datetime.fromisoformat(frame["observed_at"].replace("Z", "+00:00"))
        expiry = datetime.fromisoformat(frame["expires_at"].replace("Z", "+00:00"))
        self.assertEqual((expiry - observed).total_seconds(), 120)
        with self.assertRaises(typedprotocol.SemanticPacketRefusal) as raised:
            typedprotocol.compile_model_semantic_packet(
                frame, packet_for(frame), case_id=CASE_ID, now=expiry)
        self.assertEqual(str(raised.exception), "packet_plan_refused")
        self.assertTrue(any(item["code"] == "stale_context"
                            and item["path"] == "$.context_revision"
                            for item in raised.exception.review["violations"]))

    def test_clarification_has_no_target_and_no_create_chain(self):
        frame = synthetic_frame()
        result = compile_packet(frame, packet_for(frame, action="clarification"))

        self.assertEqual(result["plan"]["goal"], "clarification")
        self.assertEqual(result["plan"]["steps"], [{
            "id": "step-01-request-clarification",
            "operator": "request_clarification",
            "args": {},
        }])
        self.assertEqual(result["review"]["disposition"], "admit")
        self.assertIs(result["review"]["execution_authorized"], True)
        self.assertIs(result["execution_performed"], False)
        self.assertIs(result["confirmation_performed"], False)
