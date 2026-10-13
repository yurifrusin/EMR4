"""Direct source cases for future isolated adapter admission; not executed here."""

import json
import unittest

from stage1_demo_adapter_core import AdapterRejected, SessionBinding, admit_action


PATIENT = SessionBinding(
    persona="patient", session_id="server-session-a", csrf="csrf-a",
    practice_id="fictional-practice", request_id="request-a", patient_id="alex",
    patient_capability="private-a",
)
OTHER_REQUEST = SessionBinding(
    persona="patient", session_id="server-session-b", csrf="csrf-b",
    practice_id="fictional-practice", request_id="request-b", patient_id="alex",
    patient_capability="private-b",
)
STAFF = SessionBinding(
    persona="staff", session_id="server-session-staff", csrf="csrf-staff",
    practice_id="fictional-practice", request_id="request-a", patient_id="alex",
    staff_user_id="reception-one",
)


def admit(binding=PATIENT, *, action="refresh", body=None, key=None, csrf=None, origin="http://127.0.0.1:8000"):
    raw = {"method": "read" if action in {"refresh", "propose_create", "propose_move"} else "write",
           "action": action, "body": body, "idempotency_key": key}
    return admit_action(profile="STAGE1_SYNTHETIC_DEMO", enabled=True,
        listener_host="127.0.0.1", request_host="127.0.0.1", origin=origin,
        expected_origin="http://127.0.0.1:8000", content_type="application/json",
        csrf_header=csrf or binding.csrf, body_bytes=json.dumps(raw).encode(), binding=binding)


class AdapterBoundaryTests(unittest.TestCase):
    def test_two_distinct_request_sessions_keep_separate_server_bindings(self):
        first = admit(PATIENT)
        second = admit(OTHER_REQUEST)
        self.assertNotEqual(first.binding.request_id, second.binding.request_id)
        self.assertNotEqual(first.binding.patient_capability, second.binding.patient_capability)

    def test_patient_cannot_request_staff_action(self):
        with self.assertRaisesRegex(AdapterRejected, "ACTION_UNAVAILABLE"):
            admit(PATIENT, action="confirm_move", body={"proposal_ref": "x"}, key="12345678")

    def test_staff_has_no_patient_capability(self):
        self.assertEqual(admit(STAFF).binding.persona, "staff")
        self.assertIsNone(STAFF.patient_capability)

    def test_cross_session_csrf_fails(self):
        with self.assertRaisesRegex(AdapterRejected, "CSRF_INVALID"):
            admit(OTHER_REQUEST, csrf=PATIENT.csrf)

    def test_cross_origin_fails(self):
        with self.assertRaisesRegex(AdapterRejected, "ORIGIN_INVALID"):
            admit(PATIENT, origin="http://example.test")

    def test_closed_profile_fails(self):
        with self.assertRaisesRegex(AdapterRejected, "PROFILE_CLOSED"):
            admit_action(profile="prod", enabled=True, listener_host="127.0.0.1",
                request_host="127.0.0.1", origin="http://127.0.0.1:8000",
                expected_origin="http://127.0.0.1:8000", content_type="application/json",
                csrf_header=PATIENT.csrf, body_bytes=b'{}', binding=PATIENT)

    def test_oversized_body_fails_before_dispatch(self):
        with self.assertRaisesRegex(AdapterRejected, "BODY_INVALID"):
            admit_action(profile="STAGE1_SYNTHETIC_DEMO", enabled=True, listener_host="127.0.0.1",
                request_host="127.0.0.1", origin="http://127.0.0.1:8000",
                expected_origin="http://127.0.0.1:8000", content_type="application/json",
                csrf_header=PATIENT.csrf, body_bytes=b"x" * 4097, binding=PATIENT)

    def test_duplicate_json_field_fails(self):
        with self.assertRaisesRegex(AdapterRejected, "DUPLICATE_FIELD"):
            admit_action(profile="STAGE1_SYNTHETIC_DEMO", enabled=True, listener_host="127.0.0.1",
                request_host="127.0.0.1", origin="http://127.0.0.1:8000",
                expected_origin="http://127.0.0.1:8000", content_type="application/json",
                csrf_header=PATIENT.csrf,
                body_bytes=b'{"method":"read","action":"refresh","action":"refresh","body":null,"idempotency_key":null}',
                binding=PATIENT)


if __name__ == "__main__":
    unittest.main()
