from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models.appointments import Appointment, AppointmentAuditLog
from app.models.tenancy import PracticeLocation, Practitioner, User, UserRole
from app.services.auth_service import hash_password
from app.services.practice.practitioner_directory_read import list_practitioner_directory
from tests.conftest import make_token

ROUTE = "/api/v1/practice/practitioners"

SENSITIVE_KEYS = {
    "provider_number",
    "prescriber_number",
    "ahpra_number",
    "hpi_i",
    "practice_id",
    "created_at",
    "email",
    "phone",
    "address",
    "address_line1",
    "address_suburb",
    "address_state",
    "address_postcode",
    "password_hash",
    "credentials",
    "schedule_overrides",
    "schedules",
    "appointments",
    "displayOrder",
    "is_active",
}


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _user(db, practice, role: UserRole, email: str) -> User:
    user = User(
        practice_id=practice.id,
        email=email,
        password_hash=hash_password("Password1!"),
        role=role,
    )
    db.add(user)
    db.flush()
    return user


def _practitioner(
    db,
    practice,
    *,
    first_name: str,
    last_name: str,
    active: bool = True,
    specialty: str | None = None,
    default_location_id=None,
) -> Practitioner:
    practitioner = Practitioner(
        practice_id=practice.id,
        first_name=first_name,
        last_name=last_name,
        specialty=specialty,
        default_location_id=default_location_id,
        is_active=active,
        provider_number="PN-SECRET",
        prescriber_number="PR-SECRET",
        ahpra_number="AHPRA-SECRET",
        hpi_i="HPII-SECRET",
    )
    db.add(practitioner)
    db.flush()
    return practitioner


def _location(db, practice, *, name: str, active: bool = True) -> PracticeLocation:
    location = PracticeLocation(
        practice_id=practice.id,
        name=name,
        phone="555-SECRET",
        address_line1="Hidden Street",
        address_suburb="Hidden",
        address_state="QLD",
        address_postcode="4000",
        is_active=active,
    )
    db.add(location)
    db.flush()
    return location


def _keys(value) -> set[str]:
    if isinstance(value, dict):
        found = set(value)
        for child in value.values():
            found |= _keys(child)
        return found
    if isinstance(value, list):
        found = set()
        for child in value:
            found |= _keys(child)
        return found
    return set()


def test_auth_denial_returns_401(client):
    response = client.get(ROUTE)

    assert response.status_code == 401


def test_invalid_token_returns_401(client):
    response = client.get(ROUTE, headers=_auth("not-a-token"))

    assert response.status_code == 401


def test_inactive_user_denied(client, db, receptionist_user):
    token = make_token(receptionist_user)
    receptionist_user.is_active = False
    db.flush()

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 401


@pytest.mark.parametrize(
    ("role", "email"),
    [
        (UserRole.GP, "gp-reader@test.local"),
        (UserRole.Receptionist, "reception-reader@test.local"),
        (UserRole.Nurse, "nurse-reader@test.local"),
        (UserRole.Admin, "admin-reader@test.local"),
        (UserRole.PracticeOwner, "owner-reader@test.local"),
    ],
)
def test_all_authenticated_roles_can_read_active_directory(
    client,
    db,
    practice,
    practitioner,
    role,
    email,
):
    user = _user(db, practice, role, email)
    token = make_token(user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text
    assert [row["id"] for row in response.json()] == [str(practitioner.id)]


def test_active_only_default_excludes_inactive_practitioners(
    client,
    db,
    receptionist_user,
    practice,
):
    active = _practitioner(db, practice, first_name="Active", last_name="Able")
    _practitioner(db, practice, first_name="Inactive", last_name="Able", active=False)
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text
    assert [row["id"] for row in response.json()] == [str(active.id)]


def test_active_only_false_requires_admin_or_practice_owner(
    client,
    db,
    receptionist_user,
    practice,
):
    _practitioner(db, practice, first_name="Inactive", last_name="Able", active=False)
    token = make_token(receptionist_user)

    response = client.get(f"{ROUTE}?activeOnly=false", headers=_auth(token))

    assert response.status_code == 403


def test_active_only_false_allows_admin_and_practice_owner(
    client,
    db,
    practice,
):
    inactive = _practitioner(db, practice, first_name="Inactive", last_name="Able", active=False)
    admin = _user(db, practice, UserRole.Admin, "admin-inactive@test.local")
    owner = _user(db, practice, UserRole.PracticeOwner, "owner-inactive@test.local")

    for user in (admin, owner):
        response = client.get(f"{ROUTE}?activeOnly=false", headers=_auth(make_token(user)))

        assert response.status_code == 200, response.text
        assert str(inactive.id) in {row["id"] for row in response.json()}


def test_unknown_or_unmapped_role_fails_closed_for_inactive_scope(db, practice):
    fake_user = SimpleNamespace(practice_id=practice.id, role="UnknownRole")

    with pytest.raises(HTTPException) as exc_info:
        list_practitioner_directory(
            db=db,
            current_user=fake_user,
            active_only=False,
        )
    assert exc_info.value.status_code == 403


def test_practice_scoping_never_returns_other_practice_practitioners(
    client,
    db,
    receptionist_user,
    practice_b,
):
    _practitioner(db, practice_b, first_name="Other", last_name="Practice")
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_no_practitioner_detail_route_or_idor_surface(client, receptionist_user, practitioner):
    token = make_token(receptionist_user)

    response = client.get(f"{ROUTE}/{practitioner.id}", headers=_auth(token))

    assert response.status_code in {404, 405}


def test_no_cross_practice_existence_leak(client, db, receptionist_user, practice_b):
    other = _practitioner(db, practice_b, first_name="Other", last_name="Practice")
    token = make_token(receptionist_user)

    response = client.get(f"{ROUTE}/{other.id}", headers=_auth(token))

    assert response.status_code in {404, 405}
    assert "Other" not in response.text
    assert str(other.id) not in response.text


def test_display_name_derivation_joins_non_empty_name_parts(
    client,
    db,
    receptionist_user,
    practice,
):
    practitioner = _practitioner(
        db,
        practice,
        first_name="  Alex  ",
        last_name="  Shera  ",
        specialty="GP",
    )
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text
    assert response.json() == [
        {
            "id": str(practitioner.id),
            "displayName": "Alex Shera",
            "roleLabel": "GP",
            "active": True,
            "defaultLocation": None,
        }
    ]


def test_response_excludes_sensitive_practitioner_fields(
    client,
    db,
    receptionist_user,
    practice,
):
    _practitioner(db, practice, first_name="Alex", last_name="Shera")
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text
    assert _keys(response.json()).isdisjoint(SENSITIVE_KEYS)
    serialized = response.text
    for secret in ("PN-SECRET", "PR-SECRET", "AHPRA-SECRET", "HPII-SECRET"):
        assert secret not in serialized


def test_default_location_same_practice_active_only(
    client,
    db,
    receptionist_user,
    practice,
):
    location = _location(db, practice, name="Main Clinic")
    _practitioner(
        db,
        practice,
        first_name="Alex",
        last_name="Shera",
        default_location_id=location.id,
    )
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text
    assert response.json()[0]["defaultLocation"] == {
        "id": str(location.id),
        "name": "Main Clinic",
    }


def test_inactive_or_other_practice_default_location_returns_null(
    client,
    db,
    receptionist_user,
    practice,
    practice_b,
):
    inactive_location = _location(db, practice, name="Closed Clinic", active=False)
    other_location = _location(db, practice_b, name="Other Clinic")
    _practitioner(
        db,
        practice,
        first_name="Inactive",
        last_name="Location",
        default_location_id=inactive_location.id,
    )
    _practitioner(
        db,
        practice,
        first_name="Other",
        last_name="Location",
        default_location_id=other_location.id,
    )
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text
    assert [row["defaultLocation"] for row in response.json()] == [None, None]


def test_deterministic_ordering_by_last_first_id(
    client,
    db,
    receptionist_user,
    practice,
):
    second = _practitioner(db, practice, first_name="Zara", last_name="Alpha")
    first = _practitioner(db, practice, first_name="Amy", last_name="Alpha")
    third = _practitioner(db, practice, first_name="Bob", last_name="Brown")
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text
    assert [row["id"] for row in response.json()] == [
        str(first.id),
        str(second.id),
        str(third.id),
    ]


def test_limit_default_and_maximum(client, db, receptionist_user, practice):
    for index in range(55):
        _practitioner(db, practice, first_name=f"First{index:02d}", last_name="Limit")
    token = make_token(receptionist_user)

    default_response = client.get(ROUTE, headers=_auth(token))
    max_response = client.get(f"{ROUTE}?limit=200", headers=_auth(token))

    assert default_response.status_code == 200, default_response.text
    assert len(default_response.json()) == 50
    assert max_response.status_code == 200, max_response.text
    assert len(max_response.json()) == 55


@pytest.mark.parametrize("query", ["limit=0", "limit=201", "offset=-1"])
def test_invalid_limit_and_offset_return_422(client, receptionist_user, query):
    token = make_token(receptionist_user)

    response = client.get(f"{ROUTE}?{query}", headers=_auth(token))

    assert response.status_code == 422


def test_empty_practice_returns_200_empty_list(client, receptionist_user):
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200
    assert response.json() == []


def test_read_does_not_create_appointment_audit_log(
    client,
    db,
    receptionist_user,
    practice,
):
    _practitioner(db, practice, first_name="Alex", last_name="Shera")
    before = db.query(AppointmentAuditLog).count()
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text
    assert db.query(AppointmentAuditLog).count() == before


def test_read_does_not_require_idempotency_key(client, db, receptionist_user, practice):
    _practitioner(db, practice, first_name="Alex", last_name="Shera")
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text


def test_get_route_does_not_write_database_state(client, db, receptionist_user, practice):
    _practitioner(db, practice, first_name="Alex", last_name="Shera")
    before = {
        "practitioners": db.query(Practitioner).count(),
        "appointments": db.query(Appointment).count(),
        "appointment_audits": db.query(AppointmentAuditLog).count(),
    }
    token = make_token(receptionist_user)

    response = client.get(ROUTE, headers=_auth(token))

    assert response.status_code == 200, response.text
    assert {
        "practitioners": db.query(Practitioner).count(),
        "appointments": db.query(Appointment).count(),
        "appointment_audits": db.query(AppointmentAuditLog).count(),
    } == before


def test_route_does_not_call_provider_access_ai_rag_or_graphrag():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            Path("app/routers/practice.py"),
            Path("app/services/practice/practitioner_directory_read.py"),
        ]
    ).lower()

    for forbidden in (
        "access_ai",
        "provider",
        "rag",
        "graphrag",
        "gemini",
        "vertex",
        "knowledge_base",
    ):
        assert forbidden not in source


def test_route_does_not_import_h15_h_series_or_historical_diary_material():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            Path("app/routers/practice.py"),
            Path("app/services/practice/practitioner_directory_read.py"),
        ]
    ).lower()

    for forbidden in (
        "h15",
        "h_series",
        "historical_diary",
        "historical-diary",
        "local_data",
    ):
        assert forbidden not in source


def test_route_does_not_change_readiness_snapshot():
    import json

    snapshot = json.loads(
        Path("tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json")
        .read_text(encoding="utf-8")
    )

    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False
    assert snapshot["write_authority_ready"] is False
