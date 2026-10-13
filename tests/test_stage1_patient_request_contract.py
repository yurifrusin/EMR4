"""Pure tests; this source is inert until independently admitted."""

import unittest

from app.services import patient_request_contract as module

REQUEST = "3ab2e6d4-c521-46db-838a-34ddf429504c"


class PatientRequestContractTests(unittest.TestCase):
    def setUp(self):
        self.raw = {
            "schema_version": module.VERSION,
            "request_id": REQUEST,
            "request_version": 2,
            "date": "2026-10-22",
            "earliest_local": "14:00",
            "latest_local": "17:00",
            "reason_code": "follow_up",
            "authority": "request_only",
        }
        self.context = {
            "request_id": REQUEST,
            "request_version": 2,
            "state": "draft",
            "allowed_dates": ["2026-10-22"],
            "minimum_local": "14:00",
            "maximum_local": "17:30",
            "expires_at": "2026-10-20T12:00:00Z",
            "as_of": "2026-10-20T11:00:00Z",
        }

    def test_valid_preference_is_not_booking_and_inputs_unchanged(self):
        raw_before = dict(self.raw)
        context_before = dict(self.context)
        outcome = module.validate_submission(self.raw, self.context)
        self.assertEqual(outcome.request_id, REQUEST)
        self.assertEqual(outcome.reason_code, "follow_up")
        self.assertFalse(hasattr(outcome, "appointment_id"))
        self.assertEqual(self.raw, raw_before)
        self.assertEqual(self.context, context_before)

    def test_extra_command_fields_and_claimed_authority_fail_closed(self):
        for key, value in (
            ("patient_id", REQUEST),
            ("practitioner_id", REQUEST),
            ("confirmed", True),
            ("appointment_id", REQUEST),
        ):
            with self.subTest(key=key):
                raw = {**self.raw, key: value}
                with self.assertRaises(module.RequestRejected) as caught:
                    module.validate_submission(raw, self.context)
                self.assertEqual(caught.exception.code, "STRUCTURE_INVALID")
                self.assertNotIn(REQUEST, str(caught.exception))
        with self.assertRaises(module.RequestRejected) as caught:
            module.validate_submission({**self.raw, "authority": "staff_confirm"}, self.context)
        self.assertEqual(caught.exception.code, "AUTHORITY_INVALID")

    def test_malformed_submission_states_reject_with_state_invalid(self):
        for state in ([], {}, True, None):
            with self.subTest(state=state):
                with self.assertRaises(module.RequestRejected) as caught:
                    module.validate_submission(self.raw, {**self.context, "state": state})
                self.assertEqual(caught.exception.code, "STATE_INVALID")

    def test_malformed_read_window_states_reject_with_state_invalid(self):
        for state in ([], {}, True, None):
            with self.subTest(state=state):
                with self.assertRaises(module.RequestRejected) as caught:
                    module.read_access_window(
                        state=state,
                        capability_expires_at="2026-10-20T12:00:00Z",
                        booked_at=None,
                        as_of="2026-10-20T11:00:00Z",
                    )
                self.assertEqual(caught.exception.code, "STATE_INVALID")
    def test_revision_date_and_expiry_refuse_stale_submission(self):
        cases = (
            ({**self.raw, "request_version": 1}, self.context, "REVISION_MISMATCH"),
            ({**self.raw, "date": "2026-10-23"}, self.context, "DATE_NOT_ALLOWED"),
            (self.raw, {**self.context, "as_of": self.context["expires_at"]}, "CAPABILITY_EXPIRED"),
            (self.raw, {**self.context, "state": "booked"}, "STATE_INVALID"),
        )
        for raw, context, expected in cases:
            with self.subTest(code=expected):
                with self.assertRaises(module.RequestRejected) as caught:
                    module.validate_submission(raw, context)
                self.assertEqual(caught.exception.code, expected)

    def test_bearer_digest_is_exact_and_constant_error(self):
        token = "a" * 64
        secret = b"s" * 32
        digest = module.capability_digest(token, secret)
        self.assertTrue(module.capability_matches(token, digest, secret))
        self.assertFalse(module.capability_matches("b" * 64, digest, secret))
        with self.assertRaises(module.RequestRejected) as caught:
            module.capability_matches("secret-in-url", digest, secret)
        self.assertEqual(caught.exception.code, "CAPABILITY_INVALID")
        self.assertNotIn("secret-in-url", str(caught.exception))

    def test_booked_readback_window_does_not_extend_mutations(self):
        self.assertEqual(
            module.read_access_window(
                state="booked",
                capability_expires_at="2026-10-20T12:00:00Z",
                booked_at="2026-10-20T11:59:59Z",
                as_of="2026-10-20T12:00:00Z",
            ),
            "booked_readback",
        )
        with self.assertRaises(module.RequestRejected) as caught:
            module.validate_submission(
                self.raw, {**self.context, "as_of": "2026-10-20T12:00:00Z"},
            )
        self.assertEqual(caught.exception.code, "CAPABILITY_EXPIRED")
        with self.assertRaises(module.RequestRejected) as caught:
            module.read_access_window(
                state="booked",
                capability_expires_at="2026-10-23T12:00:00Z",
                booked_at="2026-10-20T11:59:59Z",
                as_of="2026-10-21T12:00:00Z",
            )
        self.assertEqual(caught.exception.code, "CAPABILITY_EXPIRED")
        with self.assertRaises(module.RequestRejected) as caught:
            module.read_access_window(
                state="booked",
                capability_expires_at="2026-10-20T12:00:00Z",
                booked_at="2026-10-20T11:59:59Z",
                as_of="2026-10-21T12:00:00Z",
            )
        self.assertEqual(caught.exception.code, "CAPABILITY_EXPIRED")


if __name__ == "__main__":
    unittest.main()
