import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-security-audit-test-harness-preflight.md"
)
REST_PROPOSAL = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-first-runtime-implementation-proposal.md"
)
DRIFT_CONTRACT = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-rest-graphql-drift-contract.md"
)
PERMISSION_MATRIX = ROOT / "docs" / "api-spine" / "security" / "permission-matrix.yaml"
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)
DEPENDENCIES = ROOT / "app" / "dependencies.py"
AUTH_SERVICE = ROOT / "app" / "services" / "auth_service.py"
CONFIG = ROOT / "app" / "config.py"
TENANCY_MODEL = ROOT / "app" / "models" / "tenancy.py"
APP = ROOT / "app"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


def _gate_rows() -> dict[str, str]:
    section = _read(PREFLIGHT).split("## Gate Verdict", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = cells[1].strip("`")
    return rows


def _app_python_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(APP.rglob("*.py"))
    )


def test_security_preflight_gate_verdict_keeps_runtime_blocked():
    assert _gate_rows() == {
        "security_audit_preflight_defined": "true",
        "authn_contract_defined": "true",
        "authz_contract_defined": "true",
        "tenancy_anti_enumeration_contract_defined": "true",
        "read_audit_posture_defined": "true",
        "future_rls_field_encryption_rate_limit_posture_defined": "true",
        "no_write_no_provider_contract_defined": "true",
        "runtime_code_authorized": "false",
        "rest_route_ready": "false",
        "graphql_resolver_ready": "false",
        "external_read_model_runtime_ready": "false",
        "readiness_snapshot_decision": "blocked",
        "pause_required_before_route_or_resolver_code": "true",
        "explicit_yuri_go_no_go_required": "true",
    }


def test_authn_contract_uses_existing_oauth2_and_get_current_user():
    preflight = _read(PREFLIGHT)
    dependencies = _read(DEPENDENCIES)
    auth_service = _read(AUTH_SERVICE)
    config = _read(CONFIG)

    for phrase in [
        "`app/dependencies.py::oauth2_scheme`",
        "`OAuth2PasswordBearer`",
        "`app/dependencies.py::get_current_user`",
        "`app/services/auth_service.py::verify_token`",
        "missing `Authorization` header",
        "invalid token",
        "expired token",
        "inactive user",
    ]:
        assert phrase in preflight
    assert "OAuth2PasswordBearer" in dependencies
    assert "def get_current_user" in dependencies
    assert "verify_token(token)" in dependencies
    assert "def verify_token" in auth_service
    assert "access_token_expire_minutes" in config


def test_authn_dependency_filters_inactive_users():
    dependencies = _read(DEPENDENCIES)
    preflight = _read(PREFLIGHT)

    assert "User.is_active == True" in dependencies
    assert "HTTP_401_UNAUTHORIZED" in dependencies
    assert "inactive user | `401`" in preflight


def test_authz_roles_and_inactive_admin_gate_documented():
    text = _read(PREFLIGHT)
    model = _read(TENANCY_MODEL)
    dependencies = _read(DEPENDENCIES)

    for role in ["GP", "Receptionist", "Nurse", "Admin", "PracticeOwner"]:
        assert f"`{role}`" in text
        assert role in model
    for phrase in [
        "`activeOnly=false` requires `Admin` or `PracticeOwner`",
        "insufficient role returns `403`",
        "unknown or unmapped roles fail closed",
        "agent and integration principals do not gain human directory-list authority",
    ]:
        assert phrase in text
    assert "def require_role" in dependencies
    assert "HTTP_403_FORBIDDEN" in dependencies


def test_tenancy_and_anti_enumeration_contract_defined():
    compact = _compact(_read(PREFLIGHT))

    for phrase in [
        "Every query filters `Practitioner.practice_id == current_user.practice_id`",
        "Practice scope comes only from the authenticated current user",
        "No `GET /api/v1/practice/practitioners/{id}` detail route",
        "Other-practice practitioners are silently absent through the practice filter",
        "Error messages must not reveal whether another-practice practitioner exists",
        "`PracticeLocation.practice_id == current_user.practice_id`",
        "`PracticeLocation.is_active == true`",
        "Patient, appointment, roster, schedule, billing, result, reminder, message",
    ]:
        assert phrase in compact


def test_read_audit_posture_excludes_appointment_audit_writes():
    text = _read(PREFLIGHT)
    compact = _compact(text)

    for phrase in [
        "must not write appointment audit rows or command audit rows",
        "`AppointmentAuditLog` exists for appointment command/write evidence",
        "no `AppointmentAuditLog` write for `GET /api/v1/practice/practitioners`",
        "no `Idempotency-Key` header required for this GET route",
        "no staff-confirmation or confirmation payload",
        "audit/log metadata must never include provider numbers",
        "Correlation id continuity is useful for tracing",
        "not authorized by this preflight",
    ]:
        assert phrase in compact


def test_future_rls_field_encryption_rate_limit_posture_documented():
    compact = _compact(_read(PREFLIGHT))
    matrix = _read(PERMISSION_MATRIX)

    for phrase in [
        "PostgreSQL RLS | not implemented here",
        "field-level encryption | not implemented here",
        "rate limiting | not implemented here",
        "runtime FGA / OpenFGA / Auth0 | blocked",
        "external patient clients | blocked",
        "RLS/RLS-equivalent",
        "CORS/CSRF",
    ]:
        assert phrase in compact
    assert "runtime_fga_clients: blocked" in matrix
    assert "external_patient_clients: blocked" in matrix


def test_no_write_no_provider_assertions_documented():
    text = _read(PREFLIGHT)

    for phrase in [
        "no `db.add`",
        "no `db.commit`",
        "no `db.flush`",
        "no `db.delete`",
        "no ORM mutation",
        "no database migration",
        "no provider call",
        "no Access AI invocation",
        "no RAG",
        "no GraphRAG",
        "no memory runtime wiring",
        "no H15/H-series runtime import",
        "no historical diary trove import",
        "no practice-knowledge authority",
        "no external patient client",
        "no runtime FGA client",
        "no practitioner create/update/delete/onboarding command",
    ]:
        assert phrase in text
    assert "test_get_route_does_not_write_database_state" in _read(REST_PROPOSAL)
    assert "test_route_does_not_call_provider_access_ai_rag_or_graphrag" in _read(
        REST_PROPOSAL
    )


def test_required_future_runtime_tests_are_listed():
    text = _read(PREFLIGHT)

    for test_name in [
        "test_unauthenticated_request_returns_401",
        "test_invalid_token_returns_401",
        "test_inactive_user_denied",
        "test_all_authenticated_roles_can_read_active_directory",
        "test_active_only_false_requires_admin_or_practice_owner",
        "test_unknown_or_unmapped_role_fails_closed",
        "test_practice_scoping_excludes_other_practice_practitioners",
        "test_no_practitioner_detail_route_or_idor_surface",
        "test_no_cross_practice_existence_leak",
        "test_default_location_same_practice_active_only",
        "test_response_excludes_sensitive_fields",
        "test_read_does_not_create_appointment_audit_log",
        "test_read_does_not_require_idempotency_key",
        "test_read_does_not_write_database_state",
        "test_read_does_not_call_provider_access_ai_rag_graphrag",
    ]:
        assert test_name in text


def test_current_code_has_rest_slice_but_no_graphql_resolver_or_extra_surface():
    app_text = _app_python_text()

    assert (APP / "routers" / "practice.py").exists()
    assert (APP / "schemas" / "practice.py").exists()
    assert (APP / "services" / "practice" / "practitioner_directory_read.py").exists()
    for fragment in [
        '@router.get("/practitioners"',
        "def get_practitioners",
        "class PractitionerOut",
        "class PractitionerDefaultLocationOut",
        "def list_practitioner_directory",
    ]:
        assert fragment in app_text
    for fragment in [
        '@router.get("/practice/practitioners"',
        "def list_practitioners",
        "Query.practice.practitioners",
        "@strawberry.field",
        "import strawberry",
        "from strawberry",
        "import graphene",
        "from graphene",
        "import ariadne",
        "from ariadne",
    ]:
        assert fragment not in app_text


def test_readiness_snapshot_remains_blocked():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False
    assert snapshot["runtime_or_memory_ready"] is False
    assert snapshot["write_authority_ready"] is False


def test_closed_gates_preserved():
    compact = _compact(_read(PREFLIGHT))

    for phrase in [
        "adding a REST practitioner directory route",
        "adding GraphQL resolvers or GraphQL mutations",
        "adding a GraphQL runtime dependency or server",
        "changing the SDL",
        "adding Pydantic runtime schemas",
        "adding `app/services/practice/` or a practitioner directory read service",
        "adding database queries, joins, indexes, migrations, read services, or query services",
        "adding audit writes or audit migrations",
        "adding rate-limiting middleware",
        "adding field-encryption code",
        "adding RLS migrations or policies",
        "changing the blocked readiness snapshot",
        "changing readiness flags to `true`",
        "provider calls or live provider gates",
        "provider dry-run wiring",
        "runtime FGA clients",
        "external patient clients",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "broad historical diary trove mining",
        "Access AI invocation wiring",
        "RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping",
        "practitioner create/update/onboarding commands",
        "appointment, roster, schedule, diary, billing, result, reminder, message",
        "model-to-database writes outside REST command handlers",
        "raw compatibility deprecation mode changes",
    ]:
        assert phrase in compact


def test_boundary_says_preflight_is_not_runtime_or_production_readiness():
    compact = _compact(_read(PREFLIGHT))

    for phrase in [
        "static security/audit test-harness preflight",
        "does not prove runtime REST authorization",
        "GraphQL authorization",
        "resolver correctness",
        "route correctness",
        "database query correctness",
        "field-level authorization",
        "audit implementation",
        "RLS",
        "field encryption",
        "rate limiting",
        "pagination performance",
        "deployment readiness",
        "provider readiness",
        "external directory readiness",
        "patient-facing client readiness",
        "production readiness",
    ]:
        assert phrase in compact


def test_static_preflight_aligns_with_drift_contract_and_permission_matrix():
    text = _read(PREFLIGHT)
    drift = _read(DRIFT_CONTRACT)
    matrix = _read(PERMISSION_MATRIX)

    assert "default-deny" in text
    assert "abac_default_deny" in matrix
    for phrase in [
        "runtime FGA / OpenFGA / Auth0 | blocked",
        "external patient clients | blocked",
        "same-practice operational read",
        "`activeOnly=false` requires `Admin` or `PracticeOwner`",
    ]:
        assert phrase in text
    for phrase in [
        "`activeOnly` | default `true`; camelCase preserved on both surfaces",
        "inactive inclusion | `activeOnly=false` requires `Admin` or `PracticeOwner`",
        "cross-practice data | silently absent through tenancy filtering",
    ]:
        assert phrase in drift
