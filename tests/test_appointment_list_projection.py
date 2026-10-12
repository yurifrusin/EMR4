"""Standalone synthetic tests; load only the candidate source file by path."""

import copy
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "app" / "services" / "appointment_list_projection.py"
SPEC = importlib.util.spec_from_file_location("isolated_appointment_list_projection", SOURCE)
projection = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = projection
SPEC.loader.exec_module(projection)

TENANT = "11111111-1111-4111-8111-111111111111"
ACTOR = "22222222-2222-4222-8222-222222222222"
FIRST = "33333333-3333-4333-8333-333333333333"
SECOND = "44444444-4444-4444-8444-444444444444"
SOURCE_ID = "88888888-8888-4888-8888-888888888888"


def fixture():
    context = {
        "tenant_id": TENANT, "actor_id": ACTOR, "role": "reception",
        "read_capability": "appointments.read", "source_revision": 7,
        "as_of": "2026-10-10T00:01:00Z",
    }
    items = []
    for item_id, start, end, label in (
        (FIRST, "2026-10-10T01:00:00Z", "2026-10-10T01:15:00Z", "Appointment 1"),
        (SECOND, "2026-10-10T01:15:00Z", "2026-10-10T01:30:00Z", "Appointment 2"),
    ):
        items.append({
            "id": item_id, "practice_id": TENANT, "start_time": start,
            "end_time": end, "status": "scheduled", "display_label": label,
            "accessibility_label": f"{label}; starts {start}; ends {end}; status scheduled",
            "warnings": [],
        })
    raw = {
        "schema_version": projection.VERSION, "tenant_id": TENANT,
        "actor_id": ACTOR, "role": "reception", "source_revision": 7,
        "captured_at": "2026-10-10T00:00:00Z", "authority": "read_only",
        "heading": "Appointments", "columns": ["Start", "End", "Status", "Appointment"],
        "items": items, "warnings": ["TIME_UNCONFIRMED"],
    }
    return raw, context


def reverse_rows_with_valid_ordinals(raw, _context):
    raw["items"].reverse()
    for ordinal, row in enumerate(raw["items"], 1):
        label = f"Appointment {ordinal}"
        row["display_label"] = label
        row["accessibility_label"] = (
            f"{label}; starts {row['start_time']}; ends {row['end_time']}; status {row['status']}"
        )


def fixture_v2():
    raw, old_context = fixture()
    context = {
        **old_context, "source_id": SOURCE_ID,
        "practice_timezone": "Australia/Brisbane", "expected_total": 2,
    }
    raw.update({
        "schema_version": projection.V2_VERSION,
        "source_id": SOURCE_ID, "practice_timezone": "Australia/Brisbane",
        "total_count": 2, "is_complete": True,
    })
    for version, status, item in zip((4, 5), ("Booked", "Cancelled"), raw["items"]):
        item["source_version"] = version
        item["status"] = status
        item["accessibility_label"] = (
            f"{item['display_label']}; starts {item['start_time']}; ends {item['end_time']}; "
            f"status {status}; timezone Australia/Brisbane"
        )
    return raw, context


class ProjectionTests(unittest.TestCase):
    def assert_rejected(self, change, code):
        raw, context = fixture()
        change(raw, context)
        with self.assertRaises(projection.ProjectionRejected) as caught:
            projection.render_view(raw, context)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(str(caught.exception), code)
        fallback = projection.render_fallback(raw, context)
        self.assertEqual(fallback["items"], ())
        self.assertEqual(fallback["warnings"], ())
        self.assertEqual(fallback["unavailable_reason"], "PROJECTION_UNAVAILABLE")
        self.assertNotIn("Appointment 1", repr(fallback))

    def test_valid_normal_and_fallback_match_without_mutation(self):
        raw, context = fixture()
        prior = copy.deepcopy((raw, context))
        normal = projection.render_view(raw, context)
        self.assertEqual(normal, projection.render_fallback(raw, context))
        self.assertEqual((raw, context), prior)
        self.assertEqual([row["id"] for row in normal["items"]], [FIRST, SECOND])
        self.assertEqual(normal["warnings"], ("TIME_UNCONFIRMED",))
        self.assertTrue(all(value is False for value in normal["affordances"].values()))
        raw["items"][0]["display_label"] = "Appointment 9"
        self.assertEqual(normal["items"][0]["display_label"], "Appointment 1")

    def test_mutation_after_validation_cannot_enter_normal_or_fallback_view(self):
        original = projection.validate_projection

        def mutate_after_validation(raw, context):
            snapshot = original(raw, context)
            raw["warnings"][:] = ["PRIVATE_DETAIL"]
            raw["items"][0]["display_label"] = "Appointment MARY"
            raw["items"][0]["warnings"][:] = ["PRIVATE_DETAIL"]
            return snapshot

        for renderer in (projection.render_view, projection.render_fallback):
            raw, context = fixture()
            with patch.object(projection, "validate_projection", side_effect=mutate_after_validation):
                view = renderer(raw, context)
            self.assertEqual(view["warnings"], ("TIME_UNCONFIRMED",))
            self.assertEqual(view["items"][0]["warnings"], ())
            self.assertEqual(view["items"][0]["display_label"], "Appointment 1")
            self.assertNotIn("PRIVATE_DETAIL", repr(view))
            self.assertNotIn("MARY", repr(view))

    def test_version_scope_revision_and_authority_rejections(self):
        self.assert_rejected(lambda p, c: p.update(schema_version="appointment.list_projection.v2"), "VERSION_UNSUPPORTED")
        self.assert_rejected(lambda p, c: p.update(tenant_id=ACTOR), "SCOPE_MISMATCH")
        self.assert_rejected(lambda p, c: p.update(actor_id=TENANT), "SCOPE_MISMATCH")
        self.assert_rejected(lambda p, c: p.update(role="clinician"), "SCOPE_MISMATCH")
        self.assert_rejected(lambda p, c: p.update(source_revision=8), "REVISION_MISMATCH")
        self.assert_rejected(lambda p, c: p.update(authority="signed_confirm"), "AUTHORITY_INVALID")
        self.assert_rejected(lambda p, c: c.update(read_capability="appointments.write"), "CONTEXT_UNAUTHORIZED")

    def test_freshness_and_structure_rejections(self):
        self.assert_rejected(lambda p, c: p.update(captured_at="2026-10-10T00:01:01Z"), "FUTURE_PROJECTION")
        self.assert_rejected(lambda p, c: p.update(captured_at="2026-10-09T23:55:59Z"), "STALE_PROJECTION")
        self.assert_rejected(lambda p, c: p.update(confirm_endpoint="/unsafe"), "STRUCTURE_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].update(notes="private"), "STRUCTURE_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].pop("accessibility_label"), "STRUCTURE_INVALID")
        self.assert_rejected(lambda p, c: p.update(columns=["Appointment", "Start", "End", "Status"]), "ACCESSIBILITY_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].update(accessibility_label="Other appointment"), "ACCESSIBILITY_INVALID")
        self.assert_rejected(lambda p, c: p["items"].append(copy.deepcopy(p["items"][0])), "DUPLICATE_ID")
        self.assert_rejected(reverse_rows_with_valid_ordinals, "ORDER_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].update(practice_id=ACTOR), "SCOPE_MISMATCH")

    def test_bounded_content_and_exact_types(self):
        self.assert_rejected(lambda p, c: p["items"][0].update(display_label="Patient Mary"), "LABEL_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].update(display_label="Appointment MARY"), "LABEL_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].update(display_label="Appointment 2"), "LABEL_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].update(status="unknown"), "STATUS_INVALID")
        self.assert_rejected(lambda p, c: p.update(warnings=["PRIVATE_DETAIL"]), "WARNINGS_INVALID")
        self.assert_rejected(lambda p, c: p.update(items=p["items"] * 17), "SIZE_INVALID")
        self.assert_rejected(lambda p, c: p.update(source_revision=True), "REVISION_MISMATCH")


class ProjectionV2Tests(unittest.TestCase):
    def assert_rejected(self, change, code):
        raw, context = fixture_v2()
        change(raw, context)
        with self.assertRaises(projection.ProjectionRejected) as caught:
            projection.render_view_v2(raw, context)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(str(caught.exception), code)
        fallback = projection.render_fallback_v2(raw, context)
        self.assertEqual(fallback["items"], ())
        self.assertEqual(fallback["warnings"], ())
        self.assertIsNone(fallback["source"])
        self.assertEqual(fallback["unavailable_reason"], "PROJECTION_UNAVAILABLE")
        self.assertNotIn(FIRST, repr(fallback))

    def test_valid_normal_fallback_parity_and_snapshot(self):
        raw, context = fixture_v2()
        before = copy.deepcopy((raw, context))
        view = projection.render_view_v2(raw, context)
        self.assertEqual(view, projection.render_fallback_v2(raw, context))
        self.assertEqual((raw, context), before)
        self.assertEqual([item["status"] for item in view["items"]], ["Booked", "Cancelled"])
        self.assertEqual(view["source"]["total_count"], 2)
        self.assertTrue(view["source"]["is_complete"])
        self.assertEqual(view["practice_timezone"], "Australia/Brisbane")
        self.assertTrue(all(value is False for value in view["affordances"].values()))
        raw["items"][1]["status"] = "Booked"
        raw["warnings"][:] = ["PRIVATE_DETAIL"]
        self.assertEqual(view["items"][1]["status"], "Cancelled")
        self.assertEqual(view["warnings"], ("TIME_UNCONFIRMED",))

    def test_mutation_after_validation_cannot_enter_v2_view(self):
        original = projection.validate_projection_v2

        def mutate_after_validation(raw, context):
            snapshot = original(raw, context)
            raw["warnings"][:] = ["PRIVATE_DETAIL"]
            raw["items"][0]["display_label"] = "Appointment MARY"
            raw["items"][0]["status"] = "Cancelled"
            raw["practice_timezone"] = "Unknown/Zone"
            return snapshot

        for renderer in (projection.render_view_v2, projection.render_fallback_v2):
            raw, context = fixture_v2()
            with patch.object(projection, "validate_projection_v2", side_effect=mutate_after_validation):
                view = renderer(raw, context)
            self.assertEqual(view["warnings"], ("TIME_UNCONFIRMED",))
            self.assertEqual(view["items"][0]["display_label"], "Appointment 1")
            self.assertEqual(view["items"][0]["status"], "Booked")
            self.assertEqual(view["practice_timezone"], "Australia/Brisbane")
            self.assertNotIn("PRIVATE_DETAIL", repr(view))
            self.assertNotIn("MARY", repr(view))

    def test_all_domain_statuses_retain_their_exact_meaning(self):
        for status in ("Booked", "Confirmed", "Arrived", "InConsult", "Completed", "Cancelled", "NoShow", "DNA"):
            with self.subTest(status=status):
                raw, context = fixture_v2()
                raw["items"][0]["status"] = status
                raw["items"][0]["accessibility_label"] = (
                    f"Appointment 1; starts {raw['items'][0]['start_time']}; "
                    f"ends {raw['items'][0]['end_time']}; status {status}; timezone Australia/Brisbane"
                )
                self.assertEqual(projection.render_view_v2(raw, context)["items"][0]["status"], status)

    def test_binding_completeness_meaning_and_structure(self):
        self.assert_rejected(lambda p, c: p.update(schema_version="appointment.list_projection.v3"), "VERSION_UNSUPPORTED")
        self.assert_rejected(lambda p, c: p.update(actor_id=TENANT), "SCOPE_MISMATCH")
        self.assert_rejected(lambda p, c: p.update(source_id=FIRST), "SCOPE_MISMATCH")
        self.assert_rejected(lambda p, c: p.update(source_revision=8), "REVISION_MISMATCH")
        self.assert_rejected(lambda p, c: p.update(practice_timezone="Australia/Sydney"), "TIMEZONE_INVALID")
        self.assert_rejected(lambda p, c: p.update(is_complete=False), "COMPLETENESS_INVALID")
        self.assert_rejected(lambda p, c: p.update(total_count=1), "COMPLETENESS_INVALID")
        self.assert_rejected(lambda p, c: p["items"].pop(), "COMPLETENESS_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].update(status="unknown"), "STATUS_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].update(status="scheduled"), "STATUS_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].update(source_version=True), "REVISION_INVALID")
        self.assert_rejected(lambda p, c: p["items"][0].update(notes="private"), "STRUCTURE_INVALID")
        self.assert_rejected(lambda p, c: p.update(confirm_endpoint="/unsafe"), "STRUCTURE_INVALID")
        self.assert_rejected(lambda p, c: p.update(authority="confirmed_write"), "AUTHORITY_INVALID")
        self.assert_rejected(lambda p, c: p.update(captured_at="2026-10-09T23:55:59Z"), "STALE_PROJECTION")


if __name__ == "__main__":
    unittest.main()
