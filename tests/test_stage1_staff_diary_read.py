"""Five retained pure cases and two prospective real-product list cases.

The latter require the separately reviewed stage1_fixture_adapter and fresh,
owned synthetic PostgreSQL host. They have not been executed or accepted.
"""

from __future__ import annotations

import importlib.util
import ast
import json
from pathlib import Path
import sys
import unittest
import uuid
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

CASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CASE))

PRODUCT = CASE
BACKEND = CASE / "serve_stage1_backend.py"
spec = importlib.util.spec_from_file_location(
    "stage1_staff_diary_read", PRODUCT / "stage1_staff_diary_read.py")
assert spec and spec.loader
diary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diary)
guard_spec = importlib.util.spec_from_file_location(
    "stage1_diary_route_guard", PRODUCT / "stage1_diary_route_guard.py")
assert guard_spec and guard_spec.loader
guard = importlib.util.module_from_spec(guard_spec)
guard_spec.loader.exec_module(guard)

TENANT = "10000000-0000-4000-8000-000000000001"
ACTOR = "20000000-0000-4000-8000-000000000002"
PATIENT = "30000000-0000-4000-8000-000000000003"
DOCTOR = "40000000-0000-4000-8000-000000000004"
ITEM = "50000000-0000-4000-8000-000000000005"
TYPE = "60000000-0000-4000-8000-000000000006"


def row() -> dict:
    return {
        "id": ITEM, "practice_id": TENANT, "patient_id": PATIENT,
        "patient_name_provisional": None,
        "patient": {"id": PATIENT, "first_name": "Ada", "last_name": "Example"},
        "practitioner_id": DOCTOR,
        "practitioner": {"id": DOCTOR, "first_name": "Sam", "last_name": "Example"},
        "appointment_type_id": TYPE, "appointment_type": {"id": TYPE, "name": "Review"},
        "start_time": "2026-10-24T00:00:00Z",
        "end_time": "2026-10-24T00:30:00Z",
        "appointment_date": "2026-10-24", "start_time_local": "10:00:00",
        "duration_minutes": 30, "status": "Booked",
        "appointment_state_version": 3,
    }


def read(rows: list[dict], **change) -> dict:
    arguments = dict(
        body=json.dumps(rows).encode(), status_code=200,
        content_type="application/json", tenant_id=TENANT,
        actor_id=ACTOR, authenticated_role="Receptionist",
        date_from="2026-10-24", date_to="2026-10-31",
        practice_timezone="Australia/Brisbane",
        captured_at="2026-10-24T00:00:30Z",
        as_of="2026-10-24T00:00:31Z",
    )
    arguments.update(change)
    return diary.render_staff_diary_read(**arguments)


class StaffDiaryReadTests(unittest.TestCase):
    def test_complete_normal_and_fallback_same_authoritative_facts(self) -> None:
        normal, fallback = read([row()]), read([row()], fallback=True)
        for view in (normal, fallback):
            self.assertEqual(view["state"], "complete")
            self.assertEqual(view["items"][0]["source_version"], 3)
            self.assertEqual(view["items"][0]["patient_name"], "Ada Example")
            self.assertEqual(view["items"][0]["practitioner_name"], "Sam Example")
            self.assertFalse(view["availability_authority"])
            self.assertEqual(view["qualification"], "appointments_only_no_availability")
            self.assertEqual(view["source"]["kind"], "immutable_capture")
            self.assertEqual(view["source"]["revision"], 1)
        self.assertEqual(normal["items"], fallback["items"])
        self.assertNotEqual(normal["source"]["id"], fallback["source"]["id"])

    def test_rejection_never_leaks_raw_fields(self) -> None:
        bad = row(); bad["practice_id"] = ACTOR
        for view in (read([bad]), read([bad], fallback=True),
                     read([row()], authenticated_role="Patient"),
                     read([row()], body=b"[not-json")):
            self.assertEqual(view, diary.unavailable())
            self.assertNotIn("Ada", str(view))

    def test_size_and_completeness_bound(self) -> None:
        many = []
        for index in range(33):
            item = row(); item["id"] = str(uuid.UUID(int=index + 1)); many.append(item)
        self.assertEqual(read(many), diary.unavailable())
        self.assertEqual(read([row()], body=b"[" + b" " * 262144 + b"]"),
                         diary.unavailable())
        self.assertEqual(read([row()], status_code=206), diary.unavailable())
        self.assertEqual(read([row()], status_code=503), diary.unavailable())
        self.assertEqual(read([row()], captured_at="2026-10-23T23:55:00Z"),
                         diary.unavailable())

    def test_seven_day_local_window_and_exact_query(self) -> None:
        path = diary.list_path("2026-10-24", "2026-10-31", "Australia/Brisbane")
        self.assertTrue(guard.valid_diary_list_path("GET", path))
        self.assertFalse(guard.valid_diary_list_path("POST", path))
        self.assertFalse(guard.valid_diary_list_path("GET", path + "&patient_id=" + PATIENT))
        self.assertFalse(guard.valid_diary_list_path("GET", path.replace("2026-10-31", "2026-11-01")))
        self.assertIn("date_from=2026-10-24T00%3A00%3A00%2B10%3A00", path)
        self.assertIn("date_to=2026-10-31T00%3A00%3A00%2B10%3A00", path)
        self.assertEqual(read([row()], date_to="2026-11-01"), diary.unavailable())
        self.assertEqual(read([row()], practice_timezone="Australia/Sydney"), diary.unavailable())
        bad = row(); bad["appointment_date"] = "2026-10-25"
        self.assertEqual(read([bad]), diary.unavailable())

    def test_row_version_and_name_consistency(self) -> None:
        bad = row(); bad["appointment_state_version"] = None
        self.assertEqual(read([bad]), diary.unavailable())
        bad = row(); bad["patient"]["id"] = ACTOR
        self.assertEqual(read([bad]), diary.unavailable())
        bad = row(); bad["duration_minutes"] = 15
        self.assertEqual(read([bad]), diary.unavailable())


def _select_backend_routes(app) -> None:
    source = ast.parse(BACKEND.read_text(encoding="utf-8"), filename=str(BACKEND))
    matches = [node for node in source.body
               if isinstance(node, ast.Assign) and any(
                   isinstance(target, ast.Name) and target.id == "_ROUTES"
                   for target in node.targets)]
    matches += [node for node in source.body
                if isinstance(node, ast.FunctionDef) and node.name == "_restrict_routes"]
    assert len(matches) == 2
    namespace = {"require": unittest.TestCase().assertTrue}
    exec(compile(ast.Module(body=matches, type_ignores=[]), str(BACKEND), "exec"), namespace)
    assert ("GET", "/api/v1/appointments") in namespace["_ROUTES"]
    namespace["_restrict_routes"](app)


def _seed_window(db, practice, practitioner, patient, reception_user, count):
    from app.models.appointments import Appointment, AppointmentStatus
    from app.services.appointment_conflicts import set_appointment_practice_context

    zone = ZoneInfo("Australia/Brisbane")
    first = datetime.now(zone).date()
    set_appointment_practice_context(db, practice.id)
    rows = []
    for index in range(count):
        day = first + timedelta(days=1 + index // 6)
        local = datetime.combine(day, time(9 + (index % 6) // 2,
                                           30 * (index % 2)), tzinfo=zone)
        row = Appointment(
            practice_id=practice.id, patient_id=patient.id,
            practitioner_id=practitioner.id, booked_by=reception_user.id,
            start_time=local.astimezone(timezone.utc),
            appointment_date=day, start_time_local=local.time().replace(tzinfo=None),
            duration_minutes=30, status=AppointmentStatus.Booked,
            reason="Authored synthetic follow-up",
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
        assert row.appointment_state_version == 1
    return first, rows


def _actual_read(client, reception_user, first):
    from app.services.auth_service import create_access_token

    last = first + timedelta(days=7)
    path = diary.list_path(first.isoformat(), last.isoformat(), "Australia/Brisbane")
    assert guard.valid_diary_list_path("GET", path)
    token = create_access_token({
        "sub": str(reception_user.id), "practice_id": str(reception_user.practice_id),
        "role": reception_user.role.value,
    })
    response = client.get(path, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    captured = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return response, dict(
        body=response.content, status_code=response.status_code,
        content_type=response.headers["content-type"],
        tenant_id=str(reception_user.practice_id), actor_id=str(reception_user.id),
        authenticated_role="Receptionist", date_from=first.isoformat(),
        date_to=last.isoformat(), practice_timezone="Australia/Brisbane",
        captured_at=captured, as_of=captured,
    )


def test_product_list_one_complete_capture(
    client, db, practice, practitioner, patient, reception_user,
):
    from app.models.appointments import AppointmentAuditLog, AppointmentCommandIdempotency

    _select_backend_routes(client.app)
    first, seeded = _seed_window(db, practice, practitioner, patient, reception_user, 1)
    before = (
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )
    response, inputs = _actual_read(client, reception_user, first)
    assert len(response.json()) == 1
    normal = diary.render_staff_diary_read(**inputs)
    fallback = diary.render_staff_diary_read(**inputs, fallback=True)
    assert normal["state"] == fallback["state"] == "complete"
    assert normal["items"] == fallback["items"]
    assert normal["items"][0]["id"] == str(seeded[0].id)
    assert normal["items"][0]["source_version"] == seeded[0].appointment_state_version
    assert normal["source"]["kind"] == "immutable_capture"
    assert normal["source"]["revision"] == 1  # Capture-local, not a list/command revision.
    assert normal["source"]["total_count"] == 1
    assert normal["qualification"] == "appointments_only_no_availability"
    assert normal["availability_authority"] is False
    assert normal["read_only"] is True
    db.refresh(seeded[0])
    assert seeded[0].appointment_state_version == 1
    assert (
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    ) == before


def test_product_list_over_bound_fails_whole_capture(
    client, db, practice, practitioner, patient, reception_user,
):
    from app.models.appointments import AppointmentAuditLog, AppointmentCommandIdempotency

    _select_backend_routes(client.app)
    first, seeded = _seed_window(db, practice, practitioner, patient, reception_user, 33)
    before = (
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    )
    response, inputs = _actual_read(client, reception_user, first)
    assert len(response.json()) == 33  # The selected product GET is unpaginated.
    assert diary.render_staff_diary_read(**inputs) == diary.unavailable()
    assert diary.render_staff_diary_read(**inputs, fallback=True) == diary.unavailable()
    for row in seeded:
        db.refresh(row)
        assert row.appointment_state_version == 1
    assert (
        db.query(AppointmentAuditLog).count(),
        db.query(AppointmentCommandIdempotency).count(),
    ) == before


if __name__ == "__main__":
    unittest.main()
