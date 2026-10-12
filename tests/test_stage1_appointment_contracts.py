"""Standalone authored-synthetic checks for inert Stage 1 contracts."""

import copy
import importlib.util
from pathlib import Path
import sys
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "app" / "services" / "appointment_lifecycle.py"
SPEC = importlib.util.spec_from_file_location("isolated_appointment_lifecycle", SOURCE)
lifecycle = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = lifecycle
SPEC.loader.exec_module(lifecycle)

TENANT = "11111111-1111-4111-8111-111111111111"
ACTOR = "22222222-2222-4222-8222-222222222222"
APPOINTMENT = "33333333-3333-4333-8333-333333333333"
PATIENT = "44444444-4444-4444-8444-444444444444"
PRACTITIONER = "55555555-5555-4555-8555-555555555555"
APPOINTMENT_TYPE = "66666666-6666-4666-8666-666666666666"
LOCATION = "77777777-7777-4777-8777-777777777777"


def fixture():
    context = {
        "tenant_id": TENANT, "actor_id": ACTOR, "role": "reception",
        "move_capability": "appointments.move.propose", "source_revision": 7,
        "selected_appointment_id": APPOINTMENT, "selected_state_version": 4,
        "selected_status": "Booked", "selected_date": "2026-10-22",
        "selected_start_local": "14:00", "patient_id": PATIENT,
        "practitioner_id": PRACTITIONER, "appointment_type_id": APPOINTMENT_TYPE,
        "location_id": LOCATION, "duration_minutes": 30,
        "practice_timezone": "Australia/Brisbane",
        "captured_at": "2026-10-12T00:00:00Z", "as_of": "2026-10-12T00:01:00Z",
    }
    intent = {
        "schema_version": lifecycle.MOVE_VERSION, "tenant_id": TENANT,
        "actor_id": ACTOR, "role": "reception",
        "source_appointment_id": APPOINTMENT, "source_state_version": 4,
        "source_revision": 7, "target_date": "2026-10-29",
        "target_start_local": "14:30", "authority": "proposal_only",
    }
    return intent, context


class LifecycleTests(unittest.TestCase):
    def assert_rejected(self, change, code):
        intent, context = fixture()
        change(intent, context)
        with self.assertRaises(lifecycle.LifecycleRejected) as caught:
            lifecycle.move_review(intent, context)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(str(caught.exception), code)
        self.assertNotIn(PATIENT, str(caught.exception))

    def test_exact_bureau_mapping_and_unsupported_states(self):
        self.assertEqual(
            {name: lifecycle.bureau_status(name) for name in ("Booked", "Arrived", "Completed", "DNA")},
            {"Booked": "booked", "Arrived": "arrived", "Completed": "completed", "DNA": "dna"},
        )
        for name in ("Cancelled", "Confirmed", "InConsult", "NoShow", "unknown", None):
            with self.subTest(name=name), self.assertRaises(lifecycle.LifecycleRejected) as caught:
                lifecycle.bureau_status(name)
            self.assertEqual(caught.exception.code, "STATUS_UNSUPPORTED")
        self.assertEqual(lifecycle.domain_status("Cancelled"), "Cancelled")

    def test_move_review_preserves_identity_constraints_and_input(self):
        intent, context = fixture()
        before = copy.deepcopy((intent, context))
        review = lifecycle.move_review(intent, context)
        self.assertEqual((intent, context), before)
        self.assertEqual(review["appointment_id"], APPOINTMENT)
        self.assertEqual(review["before"], {"date": "2026-10-22", "start_local": "14:00"})
        self.assertEqual(review["after"], {"date": "2026-10-29", "start_local": "14:30"})
        self.assertEqual(review["unchanged"], {
            "patient_id": PATIENT, "practitioner_id": PRACTITIONER,
            "appointment_type_id": APPOINTMENT_TYPE, "duration_minutes": 30,
            "location_id": LOCATION, "status": "Booked",
        })
        self.assertEqual(review["confirmation"], "staff_signed_update_required")
        self.assertEqual(review["authority"], "proposal_only")
        self.assertFalse(review["write_performed"])
        self.assertEqual(review["affordances"], {"confirm": False, "write": False})
        intent["target_date"] = "2026-11-01"
        context["patient_id"] = None
        self.assertEqual(review["after"]["date"], "2026-10-29")
        self.assertEqual(review["unchanged"]["patient_id"], PATIENT)

    def test_non_time_fields_and_claimed_effect_are_rejected(self):
        self.assert_rejected(lambda i, c: i.update(patient_id=PATIENT), "STRUCTURE_INVALID")
        self.assert_rejected(lambda i, c: i.update(duration_minutes=45), "STRUCTURE_INVALID")
        self.assert_rejected(lambda i, c: i.update(location_id=LOCATION), "STRUCTURE_INVALID")
        self.assert_rejected(lambda i, c: i.update(authority="confirmed_write"), "AUTHORITY_INVALID")
        self.assert_rejected(lambda i, c: i.update(schema_version="appointment.move_time_intent.v2"), "VERSION_UNSUPPORTED")

    def test_scope_revision_freshness_and_terminal_rejections(self):
        self.assert_rejected(lambda i, c: i.update(actor_id=TENANT), "SCOPE_MISMATCH")
        self.assert_rejected(lambda i, c: i.update(source_appointment_id=PATIENT), "SCOPE_MISMATCH")
        self.assert_rejected(lambda i, c: i.update(source_state_version=3), "REVISION_MISMATCH")
        self.assert_rejected(lambda i, c: i.update(source_revision=8), "REVISION_MISMATCH")
        self.assert_rejected(lambda i, c: c.update(role="patient"), "CONTEXT_UNAUTHORIZED")
        self.assert_rejected(lambda i, c: c.update(captured_at="2026-10-11T23:55:59Z"), "SOURCE_STALE")
        self.assert_rejected(lambda i, c: c.update(selected_status="Cancelled"), "STATUS_NOT_MOVABLE")
        self.assert_rejected(lambda i, c: c.update(selected_status="InConsult"), "STATUS_NOT_MOVABLE")
        self.assert_rejected(lambda i, c: c.update(practice_timezone="Unknown/Zone"), "TIMEZONE_UNSUPPORTED")

    def test_time_and_no_change_rejections(self):
        self.assert_rejected(lambda i, c: i.update(target_date="2026-02-30"), "TIME_INVALID")
        self.assert_rejected(lambda i, c: i.update(target_start_local="25:00"), "TIME_INVALID")
        self.assert_rejected(lambda i, c: i.update(target_date="2026-10-22", target_start_local="14:00"), "NO_CHANGE")


if __name__ == "__main__":
    unittest.main()
