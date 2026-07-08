import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = (
    ROOT / "docs" / "api-spine" / "patient-messages-route-schema-ownership-candidate.md"
)
DESIGN_PATH = ROOT / "docs" / "api-spine" / "patient-messages-read-shape-design.md"
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
PATIENTS_ROUTER = ROOT / "app" / "routers" / "patients.py"
CLINICAL_ROUTER = ROOT / "app" / "routers" / "clinical.py"
PATIENTS_SCHEMA = ROOT / "app" / "schemas" / "patients.py"
MESSAGING_MODEL = ROOT / "app" / "models" / "messaging.py"

EXPECTED_OWNERSHIP = {
    "route_path": (
        "GET /api/v1/patients/{patient_id}/messages",
        "candidate_only",
    ),
    "router_owner": (
        "existing app/routers/patients.py with prefix /api/v1/patients",
        "candidate_only",
    ),
    "schema_owner": (
        "existing app/schemas/patients.py::PatientMessageSummaryOut",
        "candidate_only",
    ),
    "graphql_owner": ("future external read-model resolver layer", "candidate_only"),
    "model_anchor": (
        "app/models/messaging.py::InternalMessage and app/models/messaging.py::SmsLog",
        "evidence_only",
    ),
    "auth_dependency": (
        "authenticated current user with practice and patient scoping",
        "candidate_only",
    ),
}

EXPECTED_RESPONSE_FIELDS = {
    "id": "union_id_namespace_pending",
    "sentAt": "derive_rename_gap",
    "channel": "derive_channel_incomplete_enum",
    "summary": "derive_truncate_display_safe",
    "status": "incomplete_status_union_pending",
}

REQUIRED_CLOSED_GATE_PHRASES = {
    "adding a REST patient messages route",
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
    "SMS send/receive, internal-message creation, mark-read, retry, delivery, or notification commands",
    "result-triage, reminder, appointment, practitioner, or directory write",
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


def test_candidate_targets_patient_messages_only_and_references_prerequisites():
    text = _candidate_text()
    design = DESIGN_PATH.read_text(encoding="utf-8")
    planning = PLANNING_PATH.read_text(encoding="utf-8")
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert "Query.patient.messages" in text
    assert "Query.patient.messages" in design
    assert "route_ownership" in planning
    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert "Query.practice.practitioners(activeOnly" not in text
    assert "Query.patient.reminders" not in text
    assert "RACGP_GUIDELINES" not in text
    assert "COCHRANE_LIBRARY" not in text


def test_candidate_ownership_rows_remain_candidate_only_or_evidence_only():
    rows = _ownership_rows()

    assert set(rows) == set(EXPECTED_OWNERSHIP)
    for item, (candidate, status) in EXPECTED_OWNERSHIP.items():
        assert rows[item]["candidate"] == candidate
        assert rows[item]["status"] == status
    assert not any(row["status"] in {"approved", "implemented"} for row in rows.values())


def test_candidate_response_shape_matches_message_design_without_schema_creation():
    rows = _response_rows()
    design = DESIGN_PATH.read_text(encoding="utf-8")

    assert {field: row["posture"] for field, row in rows.items()} == EXPECTED_RESPONSE_FIELDS
    for field in EXPECTED_RESPONSE_FIELDS:
        assert f"`PatientMessageSummary.{field}`" in design
    schema_text = PATIENTS_SCHEMA.read_text(encoding="utf-8")
    assert "class PatientMessageSummaryOut" not in schema_text
    assert "class MessageSummaryOut" not in schema_text


def test_current_code_still_has_no_candidate_route_or_schema():
    router_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in [PATIENTS_ROUTER, CLINICAL_ROUTER]
    )
    schema_text = PATIENTS_SCHEMA.read_text(encoding="utf-8")

    for fragment in [
        '@router.get("/{patient_id}/messages"',
        '@router.get("/{patient_id}/message"',
        '@router.get("/messages"',
        "def list_patient_messages",
        "def list_messages",
    ]:
        assert fragment not in router_text
    assert "class PatientMessageSummaryOut" not in schema_text
    assert "class MessageSummaryOut" not in schema_text


def test_candidate_names_model_evidence_and_sensitive_field_exclusions():
    text = _candidate_text()
    model_text = MESSAGING_MODEL.read_text(encoding="utf-8")

    for fragment in [
        "class InternalMessage",
        "class SmsLog",
        "practice_id",
        "patient_id",
        "sender_id",
        "recipient_id",
        "phone_number",
        "clicksend_message_id",
        "message_body",
        'Index("ix_internal_messages_practice_id"',
        'Index("ix_sms_log_patient_id"',
    ]:
        assert fragment in model_text
    for phrase in [
        "model evidence is not route/schema implementation",
        "phone numbers",
        "ClickSend IDs",
        "sender IDs",
        "recipient IDs",
        "appointment IDs",
        "raw message bodies",
        "raw model dumps",
    ]:
        assert phrase in text


def test_static_preconditions_include_auth_scoping_union_gaps_and_tests():
    section = _candidate_text().split(
        "## Static Preconditions Before Implementation Proposal", 1
    )[1].split("\n## ", 1)[0]
    compact = " ".join(section.split())

    for phrase in [
        "final router module and route path",
        "final schema module and class name",
        "auth dependency, same-practice filtering, and requested-patient ownership check",
        "ID namespace strategy for the two-table union",
        "timestamp mapping policy for `sentAt`",
        "`INTERNAL`/`SMS` channel derivation from table source",
        "unreachable `EMAIL`",
        "summary derivation and truncation/redaction policy",
        "`InternalMessage.subject` preferred over `InternalMessage.body`",
        "`SmsLog` inclusion policy",
        "bulk SMS and inbound replies must be default-excluded",
        "status mapping that covers `InternalMessage.is_read`",
        "SmsStatus",
        "candidate `default_limit=20` and `max_limit=100`",
        "deterministic ordering by message timestamp descending with stable source/id tie-breakers",
        "candidate `200` plus empty list",
        "candidate `404` recorded as an unapproved anti-enumeration planning value",
        "GraphQL resolver owner and resolver authorization plan",
        "no provider calls, no Access AI invocation, no RAG/GraphRAG, no",
        "not approved by this packet",
    ]:
        assert phrase in compact


def test_candidate_preserves_closed_gates_and_boundary():
    text = _candidate_text()
    compact = " ".join(text.split())

    for phrase in REQUIRED_CLOSED_GATE_PHRASES:
        assert phrase in compact
    assert "does not authorize" in text
    assert "does not prove runtime GraphQL resolver implementation" in compact
    assert "patient-facing client readiness" in text
