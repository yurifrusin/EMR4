import json
from pathlib import Path

from app.models.appointments import AppointmentAuditLog
from app.models.tenancy import PracticeLocation, Practitioner
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
EVIDENCE = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-office-addin-graphql-default-on-local-backend-smoke.json"
)
GRAPHQL_ROUTE = "/api/v1/graphql"


SENSITIVE_TOKENS = {
    "PN-SMOKE-SECRET",
    "PR-SMOKE-SECRET",
    "AHPRA-SMOKE-SECRET",
    "HPII-SMOKE-SECRET",
    "Hidden Smoke Street",
    "555-SMOKE",
}


def _office_addin_graphql_query() -> str:
    source = DIARY_JS.read_text(encoding="utf-8", errors="replace")
    prefix = "const PRACTITIONER_DIRECTORY_GRAPHQL_QUERY = `"
    start = source.index(prefix) + len(prefix)
    end = source.index("`;", start)
    return source[start:end]


def _auth(user) -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token(user)}"}


def _location(db, practice, *, name: str) -> PracticeLocation:
    location = PracticeLocation(
        practice_id=practice.id,
        name=name,
        phone="555-SMOKE",
        address_line1="Hidden Smoke Street",
        address_suburb="Hidden",
        address_state="QLD",
        address_postcode="4000",
        is_active=True,
    )
    db.add(location)
    db.flush()
    return location


def _practitioner(
    db,
    practice,
    *,
    first_name: str,
    last_name: str,
    specialty: str | None = None,
    active: bool = True,
    default_location_id=None,
) -> Practitioner:
    practitioner = Practitioner(
        practice_id=practice.id,
        first_name=first_name,
        last_name=last_name,
        specialty=specialty,
        default_location_id=default_location_id,
        is_active=active,
        provider_number="PN-SMOKE-SECRET",
        prescriber_number="PR-SMOKE-SECRET",
        ahpra_number="AHPRA-SMOKE-SECRET",
        hpi_i="HPII-SMOKE-SECRET",
    )
    db.add(practitioner)
    db.flush()
    return practitioner


def test_default_on_office_addin_query_runs_against_local_backend_fake_data(
    client,
    db,
    receptionist_user,
    practice,
    practice_b,
):
    location = _location(db, practice, name="Smoke Clinic")
    expected = _practitioner(
        db,
        practice,
        first_name="Alex",
        last_name="Smoke",
        specialty="GP",
        default_location_id=location.id,
    )
    inactive = _practitioner(
        db,
        practice,
        first_name="Inactive",
        last_name="Smoke",
        active=False,
    )
    other_practice = _practitioner(
        db,
        practice_b,
        first_name="Other",
        last_name="Smoke",
    )
    before_audit_count = db.query(AppointmentAuditLog).count()

    response = client.post(
        GRAPHQL_ROUTE,
        json={
            "query": _office_addin_graphql_query(),
            "variables": {"activeOnly": True, "limit": 200, "offset": 0},
        },
        headers=_auth(receptionist_user),
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert "errors" not in body
    assert body["data"]["practice"] is not None
    rows = body["data"]["practice"]["practitioners"]
    assert rows == [
        {
            "id": str(expected.id),
            "displayName": "Alex Smoke",
            "roleLabel": "GP",
            "active": True,
            "defaultLocation": {"id": str(location.id), "name": "Smoke Clinic"},
        }
    ]
    assert str(inactive.id) not in response.text
    assert str(other_practice.id) not in response.text
    for token in SENSITIVE_TOKENS:
        assert token not in response.text
    assert db.query(AppointmentAuditLog).count() == before_audit_count


def test_default_on_local_backend_smoke_evidence_records_bounded_claims():
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_office_addin_graphql_default_on_local_backend_smoke.v1"
    )
    assert payload["sprint"] == 283
    assert payload["target_consumer"] == "office_addin_diary_booking_practitioner_selector"
    assert payload["local_backend_smoke"]["endpoint"] == GRAPHQL_ROUTE
    assert payload["local_backend_smoke"]["uses_office_addin_graphql_document"] is True
    assert payload["local_backend_smoke"]["uses_fastapi_testclient"] is True
    assert payload["local_backend_smoke"]["uses_route_interception"] is False
    assert payload["local_backend_smoke"]["uses_fake_local_db_rows"] is True
    assert payload["local_backend_smoke"]["asserts_active_only"] is True
    assert payload["runtime_posture"]["feature_gate_default"] is True
    assert payload["runtime_posture"]["rest_fallback_retained"] is True
    assert payload["next_recommended_work"].startswith("Proceed to a rollback packet")
    assert all(value is False for value in payload["must_remain_false"].values())
