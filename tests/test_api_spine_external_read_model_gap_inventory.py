import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAP_PATH = ROOT / "docs" / "api-spine" / "external-router-read-model-gap-inventory.md"
CURRENT_STATUS_PATH = (
    ROOT / "docs" / "api-spine" / "external-read-model-current-surface-status.json"
)
ROOT_INVENTORY_PATH = ROOT / "docs" / "api-spine" / "external-router-read-root-inventory.md"
GRAPHQL_PATH = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
TENANCY_MODEL = ROOT / "app" / "models" / "tenancy.py"
RESULTS_MODEL = ROOT / "app" / "models" / "results.py"
MESSAGING_MODEL = ROOT / "app" / "models" / "messaging.py"
BILLING_MODEL = ROOT / "app" / "models" / "billing.py"
SEARCH_ROUTER = ROOT / "app" / "routers" / "search.py"
PRACTICE_ROUTER = ROOT / "app" / "routers" / "practice.py"
DIARY_ROUTER = ROOT / "app" / "routers" / "diary.py"
PATIENTS_ROUTER = ROOT / "app" / "routers" / "patients.py"
CLINICAL_ROUTER = ROOT / "app" / "routers" / "clinical.py"

EXPECTED_SURFACES = {
    "Query.practice.practitioners",
    "Query.patient.reminders",
    "Query.patient.messages",
    "Query.directorySearch.RACGP_GUIDELINES",
    "Query.directorySearch.COCHRANE_LIBRARY",
}

EXPECTED_POSTURES = {
    "Query.practice.practitioners": "route_gap",
    "Query.patient.reminders": "route_and_shape_gap",
    "Query.patient.messages": "route_and_shape_gap",
    "Query.directorySearch.RACGP_GUIDELINES": "source_and_licensing_gap",
    "Query.directorySearch.COCHRANE_LIBRARY": "source_and_licensing_gap",
}

REQUIRED_BLOCKED_GATE_PHRASES = {
    "adding GraphQL resolvers or GraphQL mutations",
    "adding new REST routes",
    "provider calls or live provider gates",
    "provider dry-run wiring",
    "runtime FGA clients",
    "external patient clients",
    "H15/H-series runtime imports",
    "memory/RAG/GraphRAG runtime wiring",
    "broad historical diary trove mining",
    "Access AI invocation wiring",
    "reminder, message, SMS, practitioner, or directory write authority",
    "model-to-database writes outside REST command handlers",
    "raw compatibility deprecation mode changes",
}


def _gap_rows() -> list[dict[str, str]]:
    text = GAP_PATH.read_text(encoding="utf-8")
    section = text.split("## Gap Inventory", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(
            {
                "surface": cells[0].strip("`"),
                "model": cells[1].strip("`"),
                "route_source": cells[2].strip("`"),
                "coverage": cells[3].strip("`"),
                "future_read_model": cells[4].strip("`"),
                "gap_posture": cells[5].strip("`"),
                "notes": cells[6],
            }
        )
    return rows


def _class_fields(path: Path, class_name: str) -> set[str]:
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source)
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


def test_gap_inventory_targets_only_the_five_external_read_model_gaps():
    rows = _gap_rows()

    assert {row["surface"] for row in rows} == EXPECTED_SURFACES
    assert len(rows) == 5
    assert "Query.practice.practitioners" in ROOT_INVENTORY_PATH.read_text(encoding="utf-8")
    assert "Query.patient.reminders" in ROOT_INVENTORY_PATH.read_text(encoding="utf-8")
    assert "Query.patient.messages" in ROOT_INVENTORY_PATH.read_text(encoding="utf-8")


def test_gap_inventory_rows_are_gap_only_and_name_no_current_routes():
    for row in _gap_rows():
        assert row["route_source"] == "none"
        assert row["gap_posture"] == EXPECTED_POSTURES[row["surface"]]
        assert row["coverage"] in {"model_only", "none"}
        assert not row["future_read_model"].startswith(("POST ", "PUT ", "PATCH ", "DELETE "))


def test_practitioner_gap_names_existing_model_and_shape_gap():
    row = next(row for row in _gap_rows() if row["surface"] == "Query.practice.practitioners")
    fields = _class_fields(TENANCY_MODEL, "Practitioner")

    assert row["model"] == "app/models/tenancy.py::Practitioner"
    assert {"first_name", "last_name", "specialty", "is_active", "default_location_id"} <= fields
    assert "display-safe `Practitioner` shape" in GAP_PATH.read_text(encoding="utf-8")
    assert "dedicated practitioner directory route" in row["notes"]


def test_reminder_gap_documents_date_and_completed_status_limitations():
    row = next(row for row in _gap_rows() if row["surface"] == "Query.patient.reminders")
    fields = _class_fields(RESULTS_MODEL, "Reminder")

    assert row["model"] == "app/models/results.py::Reminder"
    assert {"practice_id", "patient_id", "due_date", "message", "is_dismissed"} <= fields
    assert "`due_date` is a `Date`, while SDL `dueAt` is `DateTime`" in row["notes"]
    assert "cannot represent SDL `ReminderStatus.COMPLETED`" in row["notes"]


def test_message_gap_documents_two_table_split_email_absence_and_summary_only():
    row = next(row for row in _gap_rows() if row["surface"] == "Query.patient.messages")
    internal_fields = _class_fields(MESSAGING_MODEL, "InternalMessage")
    sms_fields = _class_fields(MESSAGING_MODEL, "SmsLog")
    text = GAP_PATH.read_text(encoding="utf-8")

    assert row["model"] == "app/models/messaging.py::InternalMessage`; `app/models/messaging.py::SmsLog"
    assert {"patient_id", "body", "is_read", "created_at"} <= internal_fields
    assert {"patient_id", "message_body", "status", "sent_at"} <= sms_fields
    assert "two-table union" in row["notes"]
    assert "`MessageChannel.EMAIL` has no backing model" in row["notes"]
    assert "must avoid raw bodies" in text


def test_directory_gaps_preserve_local_mbs_snomed_only_and_name_source_prerequisites():
    rows = {row["surface"]: row for row in _gap_rows() if row["surface"].startswith("Query.directorySearch")}
    billing_text = BILLING_MODEL.read_text(encoding="utf-8")
    search_text = SEARCH_ROUTER.read_text(encoding="utf-8")

    assert "class MbsDirectory" in billing_text
    assert "class SnomedDirectory" in billing_text
    assert '@router.get("/search-mbs")' in search_text
    assert '@router.get("/search-snomed")' in search_text

    for surface in {"Query.directorySearch.RACGP_GUIDELINES", "Query.directorySearch.COCHRANE_LIBRARY"}:
        row = rows[surface]
        assert row["model"] == "none"
        assert row["coverage"] == "none"
        assert row["gap_posture"] == "source_and_licensing_gap"
        assert "reviewed local/cited source" in row["notes"] or "licensing/subscription review" in row["notes"]


def test_gap_inventory_surfaces_exist_in_graphql_sdl_without_mutation_root():
    graphql = GRAPHQL_PATH.read_text(encoding="utf-8")

    for fragment in [
        "practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0)",
        "reminders: [PatientReminder!]!",
        "messages: [PatientMessageSummary!]!",
        "RACGP_GUIDELINES",
        "COCHRANE_LIBRARY",
    ]:
        assert fragment in graphql
    assert "type Mutation" not in graphql


def test_historical_gap_inventory_is_superseded_without_rewriting_history():
    current = json.loads(CURRENT_STATUS_PATH.read_text(encoding="utf-8"))
    current_rows = {row["surface"]: row for row in current["surfaces"]}
    practitioner_history = next(
        row for row in _gap_rows() if row["surface"] == "Query.practice.practitioners"
    )
    practitioner_current = current_rows["Query.practice.practitioners"]

    assert practitioner_history["gap_posture"] == "route_gap"
    assert practitioner_history["route_source"] == "none"
    assert practitioner_current["implementation_status"] == "implemented_mounted"
    assert practitioner_current["rest"]["mounted"] is True
    assert '@router.get("/practitioners"' in PRACTICE_ROUTER.read_text(encoding="utf-8")

    router_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in [DIARY_ROUTER, PATIENTS_ROUTER, CLINICAL_ROUTER, SEARCH_ROUTER]
    )

    for missing in [
        '@router.get("/{patient_id}/reminders"',
        '@router.get("/{patient_id}/messages"',
        '@router.get("/search-racgp"',
        '@router.get("/search-cochrane"',
    ]:
        assert missing not in router_text


def test_gap_inventory_preserves_closed_gate_boundary():
    text = GAP_PATH.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    for phrase in REQUIRED_BLOCKED_GATE_PHRASES:
        assert phrase in text
    assert "does not authorize" in text
    assert "does not create GraphQL resolvers" in text
    assert "does not prove runtime GraphQL resolver implementation" in compact
    assert "practice-knowledge advisory facts as directory authority" in text
    assert "model-to-database writes outside REST command handlers" in text
