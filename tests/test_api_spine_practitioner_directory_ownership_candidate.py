import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = (
    ROOT / "docs" / "api-spine" / "practitioner-directory-route-schema-ownership-candidate.md"
)
DESIGN_PATH = ROOT / "docs" / "api-spine" / "practitioner-directory-read-shape-design.md"
PLANNING_PATH = (
    ROOT / "docs" / "api-spine" / "external-read-model-implementation-planning-review.md"
)
SNAPSHOT_PATH = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)
DIARY_ROUTER = ROOT / "app" / "routers" / "diary.py"
DIARY_SCHEMA = ROOT / "app" / "schemas" / "diary.py"
TENANCY_MODEL = ROOT / "app" / "models" / "tenancy.py"

EXPECTED_OWNERSHIP = {
    "route_path": ("GET /api/v1/practice/practitioners", "candidate_only"),
    "router_owner": ("new `app/routers/practice.py` with prefix `/api/v1/practice`", "candidate_only"),
    "schema_owner": ("new `app/schemas/practice.py::PractitionerOut`", "candidate_only"),
    "graphql_owner": ("future external read-model resolver layer", "candidate_only"),
    "model_anchor": ("app/models/tenancy.py::Practitioner", "evidence_only"),
    "auth_dependency": ("authenticated current user with practice scoping", "candidate_only"),
}

EXPECTED_RESPONSE_FIELDS = {
    "id": "direct_practice_scoped",
    "displayName": "derive_display_safe",
    "roleLabel": "optional_pending_semantics",
    "active": "rename_default_true_filter",
    "defaultLocation": "linked_read_pending",
}

REQUIRED_CLOSED_GATE_PHRASES = {
    "adding a REST practitioner directory route",
    "adding GraphQL resolvers or GraphQL mutations",
    "adding Pydantic runtime schemas",
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
    "practitioner create/update/onboarding commands",
    "appointment, roster, schedule, diary, billing, result, or clinical write",
    "model-to-database writes outside REST command handlers",
    "raw compatibility deprecation mode changes",
}


def _candidate_text() -> str:
    return CANDIDATE_PATH.read_text(encoding="utf-8")


def _ownership_rows() -> dict[str, dict[str, str]]:
    section = _candidate_text().split("## Candidate Ownership", 1)[1].split(
        "\n## ", 1
    )[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = {
            "candidate": cells[1].replace("`", ""),
            "status": cells[2].strip("`"),
        }
    return rows


def _response_rows() -> dict[str, dict[str, str]]:
    section = _candidate_text().split("## Candidate Response Shape", 1)[1].split(
        "\n## ", 1
    )[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = {
            "source": cells[1],
            "posture": cells[2].strip("`"),
        }
    return rows


def test_candidate_targets_practitioner_directory_only_and_references_prerequisites():
    text = _candidate_text()
    design = DESIGN_PATH.read_text(encoding="utf-8")
    planning = PLANNING_PATH.read_text(encoding="utf-8")
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert "Query.practice.practitioners(activeOnly: Boolean = true)" in text
    assert "Query.practice.practitioners(activeOnly: Boolean = true)" in design
    assert "route_ownership" in planning
    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert "Query.patient.messages" not in text
    assert "RACGP_GUIDELINES" not in text
    assert "COCHRANE_LIBRARY" not in text


def test_candidate_ownership_rows_remain_candidate_only_or_evidence_only():
    rows = _ownership_rows()

    assert set(rows) == set(EXPECTED_OWNERSHIP)
    for item, (candidate, status) in EXPECTED_OWNERSHIP.items():
        assert rows[item]["candidate"] == candidate.replace("`", "")
        assert rows[item]["status"] == status
    assert not any(row["status"] in {"approved", "implemented"} for row in rows.values())


def test_candidate_response_shape_matches_practitioner_design_without_schema_creation():
    rows = _response_rows()
    design = DESIGN_PATH.read_text(encoding="utf-8")

    assert {field: row["posture"] for field, row in rows.items()} == EXPECTED_RESPONSE_FIELDS
    for field in EXPECTED_RESPONSE_FIELDS:
        assert f"`Practitioner.{field}`" in design
    assert "PractitionerOut" not in DIARY_SCHEMA.read_text(encoding="utf-8")
    assert "PractitionerDirectory" not in DIARY_SCHEMA.read_text(encoding="utf-8")


def test_current_code_still_has_no_candidate_route_or_schema():
    router_text = DIARY_ROUTER.read_text(encoding="utf-8")
    schema_text = DIARY_SCHEMA.read_text(encoding="utf-8")

    for fragment in [
        '@router.get("/practice/practitioners"',
        '@router.get("/practitioners"',
        "def list_practitioners",
        "def get_practitioners",
    ]:
        assert fragment not in router_text
    assert "class PractitionerOut" not in schema_text
    assert "class PractitionerDirectory" not in schema_text


def test_candidate_names_model_evidence_and_sensitive_field_exclusions():
    text = _candidate_text()
    model_text = TENANCY_MODEL.read_text(encoding="utf-8")

    for fragment in [
        "class Practitioner",
        "provider_number",
        "prescriber_number",
        "ahpra_number",
        "hpi_i",
        "specialty",
        "default_location_id",
    ]:
        assert fragment in model_text
    for phrase in [
        "model evidence is not route/schema implementation",
        "provider number, prescriber number, AHPRA",
        "HPI-I, email, phone, address, credentials",
        "raw model dumps",
    ]:
        assert phrase in text


def test_static_preconditions_include_auth_scoping_pagination_and_tests():
    section = _candidate_text().split(
        "## Static Preconditions Before Implementation Proposal", 1
    )[1].split("\n## ", 1)[0]
    compact = " ".join(section.split())

    for phrase in [
        "final router module and route path",
        "final schema module and class name",
        "auth dependency and same-practice filtering",
        "default `activeOnly=true` behavior",
        "display-name derivation and deterministic ordering",
        "candidate `default_limit=50` and `max_limit=200`",
        "deterministic ordering by `Practitioner.last_name`, then `Practitioner.first_name`, then `Practitioner.id`",
        "candidate `200` plus empty list",
        "candidate admin-only review",
        "GraphQL resolver owner and resolver authorization plan",
        "no provider calls, no Access AI invocation, no RAG/GraphRAG, and no writes",
        "not approved by this packet",
    ]:
        assert phrase in compact


def test_candidate_preserves_closed_gates_and_boundary():
    text = _candidate_text()
    compact = " ".join(text.split())

    for phrase in REQUIRED_CLOSED_GATE_PHRASES:
        assert phrase in text
    assert "does not authorize" in text
    assert "does not prove runtime GraphQL resolver implementation" in compact
    assert "patient-facing client readiness" in text
