import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_PATH = ROOT / "docs" / "api-spine" / "patient-reminders-read-shape-design.md"
GAP_PATH = ROOT / "docs" / "api-spine" / "external-router-read-model-gap-inventory.md"
GRAPHQL_PATH = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
RESULTS_MODEL = ROOT / "app" / "models" / "results.py"
PATIENTS_ROUTER = ROOT / "app" / "routers" / "patients.py"
CLINICAL_ROUTER = ROOT / "app" / "routers" / "clinical.py"
PATIENTS_SCHEMA = ROOT / "app" / "schemas" / "patients.py"

EXPECTED_FIELD_MAPPINGS = {
    "PatientReminder.id": ("app/models/results.py::Reminder.id", "direct"),
    "PatientReminder.dueAt": ("Reminder.due_date", "date_to_datetime_gap"),
    "PatientReminder.summary": (
        "Reminder.message`; `Reminder.reminder_type",
        "derive_truncate",
    ),
    "PatientReminder.status": ("Reminder.is_dismissed", "incomplete_enum"),
}

REQUIRED_CLOSED_GATE_PHRASES = {
    "adding a REST patient reminder route",
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
    "reminder create/update/dismiss/complete/escalate commands",
    "result-triage or recall-policy write authority",
    "appointment, practitioner, message, SMS, or directory write authority",
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
        if not line.startswith("| `PatientReminder."):
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


def test_design_targets_only_patient_reminders_gap():
    text = _design_text()
    gap_text = GAP_PATH.read_text(encoding="utf-8")

    assert "`Query.patient.reminders`" in text
    assert "| `Query.patient.reminders` | `route_and_shape_gap` |" in text
    assert "Query.patient.reminders" in gap_text
    assert "route_and_shape_gap" in gap_text
    assert "Query.practice.practitioners(activeOnly" not in text
    assert "Query.patient.messages" not in text
    assert "RACGP_GUIDELINES" not in text
    assert "COCHRANE_LIBRARY" not in text


def test_display_safe_mapping_matches_sdl_and_current_model_fields():
    rows = {row["field"]: row for row in _mapping_rows()}
    graphql = GRAPHQL_PATH.read_text(encoding="utf-8")
    fields = _class_fields(RESULTS_MODEL, "Reminder")

    assert set(rows) == set(EXPECTED_FIELD_MAPPINGS)
    for field, (source, posture) in EXPECTED_FIELD_MAPPINGS.items():
        assert rows[field]["source"] == source
        assert rows[field]["posture"] == posture

    assert "type PatientReminder {" in graphql
    for fragment in [
        "id: ID!",
        "dueAt: DateTime",
        "summary: String!",
        "status: ReminderStatus!",
        "OPEN",
        "COMPLETED",
        "DISMISSED",
    ]:
        assert fragment in graphql
    assert {
        "id",
        "practice_id",
        "patient_id",
        "practitioner_id",
        "triggered_by_result_id",
        "reminder_type",
        "message",
        "due_date",
        "is_dismissed",
    } <= fields


def test_design_documents_date_and_status_semantic_gaps():
    text = _design_text()
    mapping_section = text.split("## Display-Safe Field Mapping", 1)[1].split(
        "\n## ", 1
    )[0]
    known_gap_section = text.split("## Known Shape Gaps", 1)[1].split("\n## ", 1)[0]

    assert "Current model stores a `Date`, while SDL reserves nullable `DateTime`" in mapping_section
    assert "cannot represent SDL `COMPLETED`" in mapping_section
    assert "`Reminder.due_date` is a date-only field" in known_gap_section
    assert "`Reminder.is_dismissed` cannot represent `ReminderStatus.COMPLETED`" in known_gap_section


def test_design_excludes_raw_message_and_internal_model_fields():
    text = _design_text()
    known_gap_section = text.split("## Known Shape Gaps", 1)[1].split("\n## ", 1)[0]
    future_section = text.split("## Future Route Requirements", 1)[1].split("\n## ", 1)[0]

    for fragment in [
        "raw `message`",
        "`reminder_type`",
        "`triggered_by_result_id`",
        "raw `practitioner_id`",
    ]:
        assert fragment in known_gap_section
    assert "must not expose practitioner IDs, result IDs, referral IDs" in future_section
    assert "must not expose reminder message raw bodies" in future_section


def test_current_code_still_has_no_patient_reminder_route_or_schema():
    router_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in [PATIENTS_ROUTER, CLINICAL_ROUTER]
    )
    schema_text = PATIENTS_SCHEMA.read_text(encoding="utf-8")

    for missing_route in [
        '@router.get("/{patient_id}/reminders"',
        '@router.get("/{patient_id}/reminder"',
        '@router.get("/reminders"',
    ]:
        assert missing_route not in router_text
    assert "class PatientReminderOut" not in schema_text
    assert "class ReminderOut" not in schema_text


def test_design_names_existing_model_evidence_without_claiming_read_model():
    text = _design_text()
    model_text = RESULTS_MODEL.read_text(encoding="utf-8")

    assert "class Reminder" in model_text
    assert 'Index("ix_reminders_practice_id"' in model_text
    assert 'Index("ix_reminders_patient_id"' in model_text
    assert "Existing reminder data is a potential backing model only" in text
    assert "not evidence that `Query.patient.reminders` is implemented" in text


def test_future_route_requirements_remain_read_only_patient_scoped_and_summary_only():
    section = _design_text().split("## Future Route Requirements", 1)[1].split(
        "\n## ", 1
    )[0]

    for phrase in [
        "patient-scoped GET read",
        "filter by `current_user.practice_id`",
        "verify the requested patient belongs to the authenticated user's practice",
        "only `id`, nullable `dueAt`, bounded `summary`, and `status`",
        "date-only to DateTime policy",
        "fail closed or omit `COMPLETED`",
        "ordering must be deterministic",
        "pagination or bounded result-size policy",
        "must not expose reminder message raw bodies without truncation/redaction policy",
        "must not expose practitioner IDs, result IDs, referral IDs, patient identifiers beyond the route scope, audit internals, or command payloads",
        "must not dismiss, complete, create, escalate, or mutate reminders",
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
