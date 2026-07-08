import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_PATH = ROOT / "docs" / "api-spine" / "patient-messages-read-shape-design.md"
GAP_PATH = ROOT / "docs" / "api-spine" / "external-router-read-model-gap-inventory.md"
GRAPHQL_PATH = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
MESSAGING_MODEL = ROOT / "app" / "models" / "messaging.py"
PATIENTS_ROUTER = ROOT / "app" / "routers" / "patients.py"
CLINICAL_ROUTER = ROOT / "app" / "routers" / "clinical.py"
PATIENTS_SCHEMA = ROOT / "app" / "schemas" / "patients.py"

EXPECTED_FIELD_MAPPINGS = {
    "PatientMessageSummary.id": ("InternalMessage.id`; `SmsLog.id", "union_id_gap"),
    "PatientMessageSummary.sentAt": (
        "InternalMessage.created_at`; `SmsLog.sent_at",
        "derive_rename_gap",
    ),
    "PatientMessageSummary.channel": (
        "InternalMessage`; `SmsLog`; no email model",
        "incomplete_channel_enum",
    ),
    "PatientMessageSummary.summary": (
        "InternalMessage.subject`; `SmsLog.message_body",
        "derive_truncate",
    ),
    "PatientMessageSummary.status": (
        "InternalMessage.is_read`; `SmsLog.status`; `SmsDirection",
        "incomplete_enum_gap",
    ),
}

REQUIRED_CLOSED_GATE_PHRASES = {
    "adding a REST patient messages route",
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
    "SMS send/receive, internal-message creation, mark-read, retry, delivery, or notification commands",
    "result-triage, reminder, appointment, practitioner, or directory write authority",
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
        if not line.startswith("| `PatientMessageSummary."):
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


def test_design_targets_only_patient_messages_gap():
    text = _design_text()
    gap_text = GAP_PATH.read_text(encoding="utf-8")

    assert "`Query.patient.messages`" in text
    assert "| `Query.patient.messages` | `route_and_shape_gap` |" in text
    assert "Query.patient.messages" in gap_text
    assert "route_and_shape_gap" in gap_text
    assert "Query.practice.practitioners(activeOnly" not in text
    assert "Query.patient.reminders`" not in text
    assert "RACGP_GUIDELINES" not in text
    assert "COCHRANE_LIBRARY" not in text


def test_display_safe_mapping_matches_sdl_and_current_model_fields():
    rows = {row["field"]: row for row in _mapping_rows()}
    graphql = GRAPHQL_PATH.read_text(encoding="utf-8")
    internal_fields = _class_fields(MESSAGING_MODEL, "InternalMessage")
    sms_fields = _class_fields(MESSAGING_MODEL, "SmsLog")

    assert set(rows) == set(EXPECTED_FIELD_MAPPINGS)
    for field, (source, posture) in EXPECTED_FIELD_MAPPINGS.items():
        assert rows[field]["source"] == source
        assert rows[field]["posture"] == posture

    assert "type PatientMessageSummary {" in graphql
    for fragment in [
        "id: ID!",
        "sentAt: DateTime!",
        "channel: MessageChannel!",
        "summary: String!",
        "status: MessageStatus!",
        "INTERNAL",
        "SMS",
        "EMAIL",
        "DRAFT",
        "SENT",
        "RECEIVED",
        "FAILED",
        "READ",
    ]:
        assert fragment in graphql
    assert {
        "id",
        "practice_id",
        "sender_id",
        "recipient_id",
        "patient_id",
        "appointment_id",
        "subject",
        "body",
        "is_read",
        "created_at",
    } <= internal_fields
    assert {
        "id",
        "practice_id",
        "patient_id",
        "direction",
        "phone_number",
        "message_body",
        "status",
        "clicksend_message_id",
        "sent_at",
    } <= sms_fields


def test_design_documents_union_email_and_status_gaps():
    text = _design_text()
    mapping_section = text.split("## Display-Safe Field Mapping", 1)[1].split(
        "\n## ", 1
    )[0]
    known_gap_section = text.split("## Known Shape Gaps", 1)[1].split("\n## ", 1)[0]

    assert "two-table union over `InternalMessage` and `SmsLog`" in known_gap_section
    assert "`EMAIL` is reserved in the SDL but has no current backing" in known_gap_section
    assert "do not map cleanly to the SDL `MessageStatus` enum" in known_gap_section
    assert "subject-only summary semantics" in known_gap_section
    assert "bulk SMS" in known_gap_section
    assert "raw message bodies must not be projected as-is" in mapping_section


def test_design_excludes_raw_bodies_and_internal_identifiers():
    text = _design_text()
    known_gap_section = text.split("## Known Shape Gaps", 1)[1].split("\n## ", 1)[0]
    future_section = text.split("## Future Route Requirements", 1)[1].split(
        "\n## ", 1
    )[0]

    for fragment in [
        "`SmsLog.phone_number`",
        "`clicksend_message_id`",
        "raw `message_body`",
        "raw `body`",
        "sender/recipient IDs",
        "appointment IDs",
    ]:
        assert fragment in known_gap_section
    assert "must not expose phone numbers, ClickSend IDs, sender IDs, recipient IDs, appointment IDs" in future_section
    assert "raw message bodies must not be exposed" in future_section


def test_current_code_still_has_no_patient_messages_route_or_schema():
    router_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in [PATIENTS_ROUTER, CLINICAL_ROUTER]
    )
    schema_text = PATIENTS_SCHEMA.read_text(encoding="utf-8")

    for missing_route in [
        '@router.get("/{patient_id}/messages"',
        '@router.get("/{patient_id}/message"',
        '@router.get("/messages"',
    ]:
        assert missing_route not in router_text
    assert "class PatientMessageSummaryOut" not in schema_text
    assert "class MessageSummary" not in schema_text


def test_design_names_existing_model_evidence_without_claiming_read_model():
    text = _design_text()
    model_text = MESSAGING_MODEL.read_text(encoding="utf-8")

    assert "class InternalMessage" in model_text
    assert "class SmsLog" in model_text
    assert 'Index("ix_internal_messages_practice_id"' in model_text
    assert 'Index("ix_sms_log_patient_id"' in model_text
    assert "potential backing evidence only" in text
    assert "not evidence that `Query.patient.messages` is implemented" in text


def test_future_route_requirements_remain_read_only_patient_scoped_and_summary_only():
    section = _design_text().split("## Future Route Requirements", 1)[1].split(
        "\n## ", 1
    )[0]

    for phrase in [
        "patient-scoped GET read",
        "filter by `current_user.practice_id`",
        "verify the requested patient belongs to the authenticated user's practice",
        "only `id`, `sentAt`, `channel`, bounded `summary`, and `status`",
        "two-table union must document ID namespace, timestamp ordering, channel derivation, and status mapping",
        "`EMAIL` must remain unreachable or omitted",
        "raw message bodies must not be exposed without a truncation/redaction policy",
        "`InternalMessage.subject` should be preferred over `InternalMessage.body`",
        "bulk SMS should be default-excluded unless a later review explicitly approves it",
        "ordering must be deterministic",
        "pagination or bounded result-size policy",
        "must not send, receive, create, mark-read, retry, deliver, or mutate messages",
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
