from pathlib import Path

import pytest

from app.models.appointments import AppointmentAuditLog
from app.models.tenancy import PracticeLocation, Practitioner, User, UserRole
from app.services.auth_service import hash_password
from tests.conftest import make_token


GRAPHQL_ROUTE = "/api/v1/graphql"
ROOT = Path(__file__).resolve().parents[1]
GRAPHQL_APP = ROOT / "app" / "graphql"
RESOLVER_JSON = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-resolver-runtime.json"


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
    "password_hash",
    "credentials",
    "schedule_overrides",
    "schedules",
    "appointments",
}


PRACTITIONERS_QUERY = """
query Practitioners($activeOnly: Boolean = true, $limit: Int = 50, $offset: Int = 0) {
  practice {
    practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset) {
      id
      displayName
      roleLabel
      active
      defaultLocation {
        id
        name
      }
    }
  }
}
"""


def _auth(user) -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token(user)}"}


def _post(client, user, query=PRACTITIONERS_QUERY, variables=None):
    return client.post(
        GRAPHQL_ROUTE,
        json={"query": query, "variables": variables or {}},
        headers=_auth(user),
    )


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


def _rows(response):
    assert response.status_code == 200, response.text
    body = response.json()
    assert "errors" not in body, body
    return body["data"]["practice"]["practitioners"]


def _error_codes(response) -> set[str]:
    assert response.status_code == 200, response.text
    return {error.get("extensions", {}).get("code") for error in response.json()["errors"]}


def test_query_practice_practitioners_requires_auth(client):
    response = client.post(GRAPHQL_ROUTE, json={"query": "{ practice { practitioners { id } } }"})

    assert response.status_code == 401


def test_query_practice_defaults_to_viewer_practice(client, receptionist_user):
    response = _post(client, receptionist_user, query="{ practice { id practitioners { id } } }")

    assert response.status_code == 200, response.text
    assert response.json()["data"]["practice"] == {
        "id": str(receptionist_user.practice_id),
        "practitioners": [],
    }


def test_query_practice_id_mismatch_does_not_leak_other_practice(
    client,
    db,
    receptionist_user,
    practice_b,
):
    other = _practitioner(db, practice_b, first_name="Other", last_name="Practice")
    response = _post(
        client,
        receptionist_user,
        query="query($id: ID!) { practice(id: $id) { id practitioners { id displayName } } }",
        variables={"id": str(practice_b.id)},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert "errors" not in body
    assert body["data"]["practice"] is None
    assert str(other.id) not in response.text
    assert "Other Practice" not in response.text


def test_query_practice_practitioners_matches_rest_projection_and_location(
    client,
    db,
    receptionist_user,
    practice,
):
    location = _location(db, practice, name="Main Clinic")
    practitioner = _practitioner(
        db,
        practice,
        first_name="Alex",
        last_name="Shera",
        specialty="GP",
        default_location_id=location.id,
    )

    rows = _rows(_post(client, receptionist_user))

    assert rows == [
        {
            "id": str(practitioner.id),
            "displayName": "Alex Shera",
            "roleLabel": "GP",
            "active": True,
            "defaultLocation": {"id": str(location.id), "name": "Main Clinic"},
        }
    ]


def test_query_practice_practitioners_defaults_to_active_only_limit_50(
    client,
    db,
    receptionist_user,
    practice,
):
    for index in range(55):
        _practitioner(db, practice, first_name=f"First{index:02d}", last_name="Limit")
    _practitioner(db, practice, first_name="Inactive", last_name="Limit", active=False)

    rows = _rows(_post(client, receptionist_user))

    assert len(rows) == 50
    assert all(row["active"] is True for row in rows)


def test_query_practice_practitioners_limit_200_and_offset_ordering(
    client,
    db,
    receptionist_user,
    practice,
):
    second = _practitioner(db, practice, first_name="Zara", last_name="Alpha")
    first = _practitioner(db, practice, first_name="Amy", last_name="Alpha")
    third = _practitioner(db, practice, first_name="Bob", last_name="Brown")

    rows = _rows(_post(client, receptionist_user, variables={"limit": 200, "offset": 1}))

    assert [row["id"] for row in rows] == [str(second.id), str(third.id)]
    assert str(first.id) not in {row["id"] for row in rows}


@pytest.mark.parametrize("variables", [{"limit": 0}, {"limit": 201}, {"limit": None}, {"offset": -1}, {"offset": None}])
def test_query_practice_practitioners_limit_and_offset_bounds(
    client,
    receptionist_user,
    variables,
):
    response = _post(client, receptionist_user, variables=variables)

    assert "BAD_USER_INPUT" in _error_codes(response)


def test_active_only_false_requires_admin_or_practice_owner(
    client,
    db,
    receptionist_user,
    practice,
):
    _practitioner(db, practice, first_name="Inactive", last_name="Able", active=False)

    response = _post(client, receptionist_user, variables={"activeOnly": False})

    assert "FORBIDDEN" in _error_codes(response)


def test_active_only_false_with_admin_or_owner_returns_inactive(client, db, practice):
    inactive = _practitioner(db, practice, first_name="Inactive", last_name="Able", active=False)
    admin = _user(db, practice, UserRole.Admin, "admin-gql@test.local")
    owner = _user(db, practice, UserRole.PracticeOwner, "owner-gql@test.local")

    for user in (admin, owner):
        rows = _rows(_post(client, user, variables={"activeOnly": False}))

        assert str(inactive.id) in {row["id"] for row in rows}


def test_other_practice_practitioners_are_silently_absent(
    client,
    db,
    receptionist_user,
    practice_b,
):
    _practitioner(db, practice_b, first_name="Other", last_name="Practice")

    rows = _rows(_post(client, receptionist_user))

    assert rows == []


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

    rows = _rows(_post(client, receptionist_user))

    assert [row["defaultLocation"] for row in rows] == [None, None]


def test_sensitive_fields_absent_from_schema_and_response(client, db, receptionist_user, practice):
    from app.graphql.schema import schema

    _practitioner(db, practice, first_name="Alex", last_name="Shera")
    response = _post(client, receptionist_user)

    assert _keys(response.json()).isdisjoint(SENSITIVE_KEYS)
    assert _keys({"schema": schema.as_str()}).isdisjoint(SENSITIVE_KEYS)
    for secret in ("PN-SECRET", "PR-SECRET", "AHPRA-SECRET", "HPII-SECRET"):
        assert secret not in response.text


def test_resolver_uses_shared_read_service_only_and_no_forbidden_imports():
    source = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(GRAPHQL_APP.rglob("*.py"))
    )

    assert "list_practitioner_directory" in source
    for fragment in (
        "app.routers.practice",
        "db.query(",
        "select(",
        "provider",
        "access_ai",
        "practice_knowledge",
        "memory",
        "rag",
        "graphrag",
        "h15",
        "h_series",
        "historical_diary",
        "local_data",
        ".add(",
        ".commit(",
        "audit",
    ):
        assert fragment not in source.lower()


def test_unhandled_resolver_exception_maps_to_internal_error_without_stack_trace(
    client,
    receptionist_user,
    monkeypatch,
):
    import app.graphql.schema as graphql_schema

    def boom(**_kwargs):
        raise RuntimeError("raw database stack trace secret")

    monkeypatch.setattr(graphql_schema, "list_practitioner_directory", boom)

    response = _post(client, receptionist_user)

    assert "INTERNAL_ERROR" in _error_codes(response)
    assert "raw database stack trace secret" not in response.text
    assert "Traceback" not in response.text


def test_query_practice_practitioners_does_not_write_audit_log(
    client,
    db,
    receptionist_user,
    practice,
):
    _practitioner(db, practice, first_name="Alex", last_name="Shera")
    before = db.query(AppointmentAuditLog).count()

    _rows(_post(client, receptionist_user))

    assert db.query(AppointmentAuditLog).count() == before


def test_sprint270_evidence_records_only_scoped_resolver_opening():
    import json

    payload = json.loads(RESOLVER_JSON.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "api_spine.practitioner_directory_graphql_resolver_runtime.v1"
    assert payload["sprint"] == 270
    assert payload["decision"] == "approved_query_practice_practitioners_only"
    assert payload["runtime_surface"]["query_practice_practitioners_resolver"] is True
    assert payload["resolver_contract"]["sole_data_path"].endswith("list_practitioner_directory")
    assert payload["resolver_contract"]["rest_router_import"] is False
    assert payload["resolver_contract"]["independent_sqlalchemy_query"] is False
    assert all(value is False for value in payload["must_remain_false"].values())
