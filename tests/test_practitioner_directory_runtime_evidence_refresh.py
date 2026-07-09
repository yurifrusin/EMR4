import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFRESH = ROOT / "docs" / "api-spine" / "practitioner-directory-runtime-evidence-refresh.json"
REFRESH_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-runtime-evidence-refresh.md"
ROUTE_TEST = ROOT / "tests" / "test_practitioner_directory_route.py"
ROUTER = ROOT / "app" / "routers" / "practice.py"
SCHEMA = ROOT / "app" / "schemas" / "practice.py"
SERVICE = ROOT / "app" / "services" / "practice" / "practitioner_directory_read.py"


def _payload() -> dict:
    return json.loads(REFRESH.read_text(encoding="utf-8"))


def _fold(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_runtime_evidence_refresh_records_bounded_route_surface():
    payload = _payload()

    assert payload["schema_version"] == "api_spine.practitioner_directory_runtime_evidence_refresh.v1"
    assert payload["decision"] == "runtime_evidence_refreshed_readiness_blocked"
    assert payload["implemented_route"] == "GET /api/v1/practice/practitioners"
    assert payload["runtime_surface"] == {
        "router": "app/routers/practice.py",
        "schema": "app/schemas/practice.py",
        "read_service": "app/services/practice/practitioner_directory_read.py",
        "test_file": "tests/test_practitioner_directory_route.py",
        "runtime_test_function_count": 25,
    }


def test_runtime_evidence_refresh_matches_current_test_inventory():
    payload = _payload()
    route_test_source = ROUTE_TEST.read_text(encoding="utf-8")
    test_names = re.findall(r"^def (test_[a-zA-Z0-9_]+)\(", route_test_source, flags=re.MULTILINE)

    assert len(test_names) == payload["runtime_surface"]["runtime_test_function_count"]
    for expected in [
        "test_auth_denial_returns_401",
        "test_invalid_token_returns_401",
        "test_inactive_user_denied",
        "test_all_authenticated_roles_can_read_active_directory",
        "test_active_only_false_requires_admin_or_practice_owner",
        "test_practice_scoping_never_returns_other_practice_practitioners",
        "test_no_practitioner_detail_route_or_idor_surface",
        "test_response_excludes_sensitive_practitioner_fields",
        "test_read_does_not_create_appointment_audit_log",
        "test_get_route_does_not_write_database_state",
        "test_route_does_not_call_provider_access_ai_rag_or_graphrag",
        "test_route_does_not_import_h15_h_series_or_historical_diary_material",
        "test_route_does_not_change_readiness_snapshot",
    ]:
        assert expected in test_names


def test_runtime_evidence_refresh_matches_current_code_surface():
    assert '@router.get("/practitioners", response_model=list[PractitionerOut])' in ROUTER.read_text(
        encoding="utf-8"
    )
    assert "class PractitionerOut(BaseModel):" in SCHEMA.read_text(encoding="utf-8")
    assert "def list_practitioner_directory(" in SERVICE.read_text(encoding="utf-8")


def test_runtime_evidence_refresh_keeps_readiness_and_scope_closed():
    payload = _payload()

    assert all(payload["evidence_refreshed"].values())
    assert payload["readiness_posture"]["rest_route_implemented"] is True
    assert payload["readiness_posture"]["runtime_tests_refreshed"] is True
    for key, value in payload["readiness_posture"].items():
        if key not in {"rest_route_implemented", "runtime_tests_refreshed"}:
            assert value is False
    assert all(value is False for value in payload["closed_scope"].values())
    assert payload["next_recommended_sprint"] == "practitioner_directory_readiness_criteria_packet"


def test_runtime_evidence_refresh_markdown_restates_not_readiness_approval():
    folded = _fold(REFRESH_MD)

    assert "Decision: `runtime_evidence_refreshed_readiness_blocked`" in folded
    assert "`GET /api/v1/practice/practitioners`" in folded
    assert "It does not change route code, schemas, services, readiness flags" in folded
    assert "The route remains implemented but not readiness-approved" in folded
    assert "not a readiness-flag flip" in folded
