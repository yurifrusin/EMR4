import json
import ast
from pathlib import Path

import pytest

from app.graphql.schema import schema
from app.models.appointments import AppointmentAuditLog
from app.models.tenancy import PracticeLocation, Practitioner, User, UserRole
from app.services.auth_service import hash_password
from tests.conftest import make_token
from tests.graphql_practitioner_consumer_harness import (
    PractitionerGraphQLConsumerHarness,
    assert_approved_practitioner_projection,
    assert_graphql_error_code,
    assert_http_auth_failure,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-internal-consumer-harness.json"


SENSITIVE_FRAGMENTS = {
    "providerNumber",
    "prescriberNumber",
    "ahpra",
    "hpi",
    "practiceId",
    "email",
    "phone",
    "address",
    "password",
}


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
    first_name: str = "Alex",
    last_name: str = "Shera",
    active: bool = True,
    default_location_id=None,
) -> Practitioner:
    practitioner = Practitioner(
        practice_id=practice.id,
        first_name=first_name,
        last_name=last_name,
        specialty="GP",
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


def _location(db, practice, *, name: str = "Main Clinic") -> PracticeLocation:
    location = PracticeLocation(practice_id=practice.id, name=name, is_active=True)
    db.add(location)
    db.flush()
    return location


def test_internal_consumer_harness_success_uses_approved_projection(
    client,
    db,
    receptionist_user,
    practice,
):
    location = _location(db, practice)
    practitioner = _practitioner(db, practice, default_location_id=location.id)
    harness = PractitionerGraphQLConsumerHarness(client)

    result = harness.query_practitioners(token=make_token(receptionist_user))

    assert result.status_code == 200
    assert result.errors == []
    assert result.rows == [
        {
            "id": str(practitioner.id),
            "displayName": "Alex Shera",
            "roleLabel": "GP",
            "active": True,
            "defaultLocation": {
                "id": str(location.id),
                "name": "Main Clinic",
            },
        }
    ]
    assert_approved_practitioner_projection(result.rows)


def test_internal_consumer_harness_handles_missing_auth_as_401(client):
    result = PractitionerGraphQLConsumerHarness(client).query_practitioners(token=None)

    assert_http_auth_failure(result)


def test_internal_consumer_harness_handles_bad_user_input(client, receptionist_user):
    harness = PractitionerGraphQLConsumerHarness(client)

    result = harness.query_practitioners(token=make_token(receptionist_user), limit=0)

    assert_graphql_error_code(result, "BAD_USER_INPUT")


@pytest.mark.parametrize(
    "variables",
    [
        {"limit": -5},
        {"limit": 201},
        {"offset": -1},
        {"activeOnly": None},
        {"limit": None},
        {"offset": None},
    ],
)
def test_internal_consumer_harness_preserves_bad_user_input_variants(
    client,
    receptionist_user,
    variables,
):
    result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
        token=make_token(receptionist_user),
        variables=variables,
    )

    assert_graphql_error_code(result, "BAD_USER_INPUT")


def test_internal_consumer_harness_handles_forbidden_inactive_scope(
    client,
    db,
    receptionist_user,
    practice,
):
    _practitioner(db, practice, active=False)
    harness = PractitionerGraphQLConsumerHarness(client)

    result = harness.query_practitioners(
        token=make_token(receptionist_user),
        active_only=False,
    )

    assert_graphql_error_code(result, "FORBIDDEN")


def test_internal_consumer_harness_all_roles_can_read_default_active_scope(
    client,
    db,
    practice,
):
    _practitioner(db, practice)
    users = [
        _user(db, practice, role, f"{role.value.lower()}-gql-harness@test.local")
        for role in UserRole
    ]

    for user in users:
        result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
            token=make_token(user),
        )

        assert result.status_code == 200
        assert result.errors == []
        assert len(result.rows) == 1


def test_internal_consumer_harness_admin_and_owner_can_read_inactive_scope(
    client,
    db,
    practice,
):
    inactive = _practitioner(db, practice, active=False)
    admin = _user(db, practice, UserRole.Admin, "admin-gql-harness@test.local")
    owner = _user(db, practice, UserRole.PracticeOwner, "owner-gql-harness@test.local")

    for user in (admin, owner):
        result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
            token=make_token(user),
            active_only=False,
        )

        assert result.status_code == 200
        assert result.errors == []
        assert str(inactive.id) in {row["id"] for row in result.rows}


def test_internal_consumer_harness_default_active_only_excludes_inactive(
    client,
    db,
    receptionist_user,
    practice,
):
    active = _practitioner(db, practice, first_name="Active", last_name="Able")
    _practitioner(db, practice, first_name="Inactive", last_name="Able", active=False)

    result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
        token=make_token(receptionist_user),
        variables={},
    )

    assert result.status_code == 200
    assert [row["id"] for row in result.rows] == [str(active.id)]


def test_internal_consumer_harness_handles_practice_id_mismatch_as_null(
    client,
    db,
    receptionist_user,
    practice_b,
):
    _practitioner(db, practice_b, first_name="Other", last_name="Practice")
    harness = PractitionerGraphQLConsumerHarness(client)

    result = harness.query_practitioners(
        token=make_token(receptionist_user),
        practice_id=str(practice_b.id),
    )

    assert result.status_code == 200
    assert result.errors == []
    assert result.practice_is_null is True
    assert "Other Practice" not in json.dumps(result.body)


def test_internal_consumer_harness_matching_practice_id_returns_viewer_practice(
    client,
    receptionist_user,
):
    result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
        token=make_token(receptionist_user),
        practice_id=str(receptionist_user.practice_id),
    )

    assert result.status_code == 200
    assert result.errors == []
    assert result.practice_is_null is False
    assert result.rows == []


def test_internal_consumer_harness_practice_scoping_excludes_other_practice(
    client,
    db,
    receptionist_user,
    practice_b,
):
    _practitioner(db, practice_b, first_name="Other", last_name="Practice")

    result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
        token=make_token(receptionist_user),
    )

    assert result.status_code == 200
    assert result.rows == []


def test_internal_consumer_harness_pagination_defaults_max_and_offset(
    client,
    db,
    receptionist_user,
    practice,
):
    for index in range(55):
        _practitioner(db, practice, first_name=f"First{index:02d}", last_name="Limit")
    harness = PractitionerGraphQLConsumerHarness(client)
    token = make_token(receptionist_user)

    default_result = harness.query_practitioners(token=token, variables={})
    max_result = harness.query_practitioners(token=token, limit=200)
    offset_result = harness.query_practitioners(token=token, limit=10, offset=5)

    assert len(default_result.rows) == 50
    assert len(max_result.rows) == 55
    assert [row["id"] for row in offset_result.rows] == [
        row["id"] for row in max_result.rows[5:15]
    ]


def test_internal_consumer_harness_inactive_or_other_practice_location_is_null(
    client,
    db,
    receptionist_user,
    practice,
    practice_b,
):
    inactive_location = _location(db, practice, name="Closed Clinic")
    inactive_location.is_active = False
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

    result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
        token=make_token(receptionist_user),
    )

    assert [row["defaultLocation"] for row in result.rows] == [None, None]


def test_internal_consumer_harness_does_not_require_idempotency_key(
    client,
    db,
    receptionist_user,
    practice,
):
    _practitioner(db, practice)

    result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
        token=make_token(receptionist_user),
    )

    assert result.status_code == 200
    assert result.rows


def test_internal_consumer_harness_idempotency_key_does_not_change_read_behavior(
    client,
    db,
    receptionist_user,
    practice,
):
    _practitioner(db, practice)
    harness = PractitionerGraphQLConsumerHarness(client)
    token = make_token(receptionist_user)

    without_key = harness.query_practitioners(token=token)
    with_key = harness.query_practitioners(
        token=token,
        extra_headers={"Idempotency-Key": "not-required-for-graphql-read"},
    )

    assert without_key.status_code == 200
    assert with_key.status_code == 200
    assert without_key.body == with_key.body


def test_internal_consumer_harness_read_does_not_write_audit_log(
    client,
    db,
    receptionist_user,
    practice,
):
    _practitioner(db, practice)
    before = db.query(AppointmentAuditLog).count()

    result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
        token=make_token(receptionist_user),
    )

    assert result.status_code == 200
    assert db.query(AppointmentAuditLog).count() == before


def test_internal_consumer_harness_rejects_sensitive_field_requests(
    client,
    receptionist_user,
):
    query = """
    {
      practice {
        practitioners {
          id
          ahpraNumber
        }
      }
    }
    """

    result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
        token=make_token(receptionist_user),
        query=query,
    )

    assert result.status_code == 200
    assert result.errors
    assert "Cannot query field" in json.dumps(result.body)


def test_internal_consumer_harness_schema_and_response_exclude_sensitive_fields(
    client,
    db,
    receptionist_user,
    practice,
):
    _practitioner(db, practice)

    result = PractitionerGraphQLConsumerHarness(client).query_practitioners(
        token=make_token(receptionist_user),
    )
    serialized = json.dumps(result.body) + schema.as_str()

    for fragment in SENSITIVE_FRAGMENTS:
        assert fragment not in serialized
    for secret in ("PN-SECRET", "PR-SECRET", "AHPRA-SECRET", "HPII-SECRET"):
        assert secret not in serialized


def test_internal_consumer_harness_source_has_no_forbidden_runtime_paths():
    imported_modules = set()
    for path in [
        ROOT / "tests" / "graphql_practitioner_consumer_harness.py",
        ROOT / "tests" / "test_practitioner_directory_graphql_internal_consumer_harness.py",
    ]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)

    for fragment in (
        "app.routers",
        "app.services.diary",
        "app.services.ai",
        "access_ai",
        "memory",
        "rag",
        "graphrag",
        "h15",
        "h_series",
        "historical_diary",
        "local_data",
        ".commit(",
        ".add(",
        "mutation",
        "subscription",
    ):
        assert all(fragment not in module for module in imported_modules)


def test_internal_consumer_harness_evidence_keeps_adjacent_gates_closed():
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "api_spine.practitioner_directory_graphql_internal_consumer_harness.v1"
    assert payload["sprint"] == 273
    assert payload["approved_release_boundary_commit"] == "0ad2b639"
    assert payload["approval_expires_on"] == "2026-08-06"
    assert payload["authorized_now"]["internal_authenticated_staff_consumer_harness"] is True
    assert all(value is False for value in payload["must_remain_false"].values())
