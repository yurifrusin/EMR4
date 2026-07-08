import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_PATH = ROOT / "docs" / "api-spine" / "practitioner-directory-read-shape-design.md"
GAP_PATH = ROOT / "docs" / "api-spine" / "external-router-read-model-gap-inventory.md"
GRAPHQL_PATH = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
TENANCY_MODEL = ROOT / "app" / "models" / "tenancy.py"
DIARY_ROUTER = ROOT / "app" / "routers" / "diary.py"
AUTH_ROUTER = ROOT / "app" / "routers" / "auth.py"
DIARY_SCHEMA = ROOT / "app" / "schemas" / "diary.py"

EXPECTED_FIELD_MAPPINGS = {
    "Practitioner.id": ("app/models/tenancy.py::Practitioner.id", "direct"),
    "Practitioner.displayName": (
        "Practitioner.first_name`; `Practitioner.last_name",
        "derive",
    ),
    "Practitioner.roleLabel": ("Practitioner.specialty", "optional_map"),
    "Practitioner.active": ("Practitioner.is_active", "rename"),
    "Practitioner.defaultLocation": (
        "Practitioner.default_location_id`; `PracticeLocation",
        "linked_read_gap",
    ),
}

REQUIRED_CLOSED_GATE_PHRASES = {
    "adding a REST practitioner directory route",
    "adding GraphQL resolvers or GraphQL mutations",
    "adding Pydantic runtime schemas",
    "provider calls or live provider gates",
    "provider dry-run wiring",
    "runtime FGA clients",
    "external patient clients",
    "H15/H-series runtime imports",
    "memory/RAG/GraphRAG runtime wiring",
    "broad historical diary trove mining",
    "Access AI invocation wiring",
    "practitioner create/update/onboarding commands",
    "appointment, roster, schedule, or diary write authority",
    "model-to-database writes outside REST command handlers",
    "raw compatibility deprecation mode changes",
}


def _design_text() -> str:
    return DESIGN_PATH.read_text(encoding="utf-8")


def _mapping_rows() -> list[dict[str, str]]:
    section = _design_text().split("## Display-Safe Field Mapping", 1)[1].split(
        "\n## ", 1
    )[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `Practitioner."):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(
            {
                "field": cells[0].strip("`"),
                "source": cells[1].strip("`"),
                "posture": cells[2].strip("`"),
                "notes": cells[3],
            }
        )
    return rows


def _class_fields(path: Path, class_name: str) -> set[str]:
    module = ast.parse(path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            fields = set()
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            fields.add(target.id)
            return fields
    raise AssertionError(f"{class_name} not found in {path}")


def test_design_targets_only_practitioner_directory_gap():
    text = _design_text()
    gap_text = GAP_PATH.read_text(encoding="utf-8")

    assert "`Query.practice.practitioners(activeOnly: Boolean = true)`" in text
    assert "| `Query.practice.practitioners(activeOnly: Boolean = true)` | `route_gap` |" in text
    assert "Query.practice.practitioners" in gap_text
    assert "route_gap" in gap_text
    assert "Query.patient.reminders" not in text
    assert "Query.patient.messages" not in text
    assert "RACGP_GUIDELINES" not in text
    assert "COCHRANE_LIBRARY" not in text


def test_display_safe_mapping_matches_sdl_and_current_model_fields():
    rows = {row["field"]: row for row in _mapping_rows()}
    graphql = GRAPHQL_PATH.read_text(encoding="utf-8")
    fields = _class_fields(TENANCY_MODEL, "Practitioner")

    assert set(rows) == set(EXPECTED_FIELD_MAPPINGS)
    for field, (source, posture) in EXPECTED_FIELD_MAPPINGS.items():
        assert rows[field]["source"] == source
        assert rows[field]["posture"] == posture

    assert "type Practitioner {" in graphql
    for fragment in [
        "id: ID!",
        "displayName: String!",
        "roleLabel: String",
        "active: Boolean!",
        "defaultLocation: PracticeLocation",
    ]:
        assert fragment in graphql
    assert {
        "id",
        "first_name",
        "last_name",
        "specialty",
        "default_location_id",
        "is_active",
    } <= fields


def test_design_excludes_provider_identifiers_and_raw_contact_fields():
    text = _design_text()
    mapping_section = text.split("## Display-Safe Field Mapping", 1)[1].split(
        "\n## ", 1
    )[0]
    future_section = text.split("## Future Route Requirements", 1)[1].split(
        "\n## ", 1
    )[0]

    assert "do not expose provider, prescriber, AHPRA, HPI-I, email, phone, or address" in mapping_section
    for forbidden in [
        "provider identifiers",
        "prescriber identifiers",
        "AHPRA",
        "HPI-I",
        "user credentials",
        "contact details",
        "schedule internals",
        "appointment data",
    ]:
        assert forbidden in future_section


def test_current_code_still_has_no_practitioner_directory_route_or_schema():
    router_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in [DIARY_ROUTER, AUTH_ROUTER]
    )
    schema_text = DIARY_SCHEMA.read_text(encoding="utf-8")

    for missing_route in [
        '@router.get("/practitioners"',
        '@router.get("/practice/practitioners"',
        '@router.get("/practitioner-directory"',
    ]:
        assert missing_route not in router_text
    assert "class PractitionerOut" not in schema_text
    assert "class PractitionerDirectory" not in schema_text


def test_design_names_existing_context_reads_without_claiming_directory_coverage():
    text = _design_text()
    diary_text = DIARY_ROUTER.read_text(encoding="utf-8")

    assert '@router.get("/template"' in diary_text
    assert '@router.get("/roster"' in diary_text
    assert "_practitioner_ids_by_ahpra" in diary_text
    assert "The above diary reads are context reads, not a practitioner-directory read" in text
    assert "not evidence that `Query.practice.practitioners` is implemented" in text


def test_future_route_requirements_remain_read_only_and_practice_scoped():
    text = _design_text()
    section = text.split("## Future Route Requirements", 1)[1].split("\n## ", 1)[0]

    for phrase in [
        "practice-scoped GET read",
        "filter by `current_user.practice_id`",
        "`Practitioner.is_active == True`",
        "only `id`, derived `displayName`, optional `roleLabel`, `active`, and optional display-safe `defaultLocation`",
        "same-practice and display-safe",
        "ordering must be deterministic",
        "pagination or bounded result-size policy",
        "must not be used as provider, RAG, GraphRAG, Access AI, or external patient-client authority",
    ]:
        assert phrase in section
    for method in ["POST ", "PUT ", "PATCH ", "DELETE "]:
        assert method not in section


def test_design_preserves_closed_gates_and_boundary():
    text = _design_text()
    compact = " ".join(text.split())

    for phrase in REQUIRED_CLOSED_GATE_PHRASES:
        assert phrase in text
    assert "does not add a REST route" in text
    assert "does not authorize" in text
    assert "does not prove runtime GraphQL resolver implementation" in compact
    assert "patient-facing client readiness" in text
