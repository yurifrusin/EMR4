import re
from pathlib import Path

import pytest

GRAPHQL_PATH = Path("docs/api-spine/graphql/appointment-diary-read.graphql")
OPENAPI_PATH = Path("docs/api-spine/openapi/appointment-commands.yaml")
INDEX_PATH = Path("docs/api-spine/audit-correlation-continuity-index.md")

ALLOWED_STATUSES = {"bridged", "read_model_only", "command_plane_only"}

REQUIRED_BLOCKED_GATE_PHRASES = {
    "proposal-only route idempotency enforcement",
    "raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement",
    "slot-search reservation or replay semantics",
    "provider calls or live provider gates",
    "runtime FGA clients",
    "external patient clients",
    "GraphQL mutations",
    "H15/H-series runtime imports",
    "memory/RAG/GraphRAG runtime wiring",
    "broad historical diary trove mining",
    "model-to-database writes outside REST command handlers",
}

FORBIDDEN_READ_MODEL_FIELDS = {
    "idempotencyKey",
    "idempotency_key",
    "confirmer",
}


def _load_openapi() -> dict:
    pytest.importorskip("yaml", reason="PyYAML not installed.")
    import yaml

    return yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))


def _graphql_text() -> str:
    return GRAPHQL_PATH.read_text(encoding="utf-8")


def _graphql_enum_values(enum_name: str) -> set[str]:
    match = re.search(rf"enum {enum_name} \{{(?P<body>.*?)\n\}}", _graphql_text(), re.S)
    assert match, f"GraphQL enum {enum_name} not found"
    values = set()
    for raw_line in match.group("body").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        values.add(line.split()[0])
    return values


def _graphql_type_body(type_name: str) -> str:
    match = re.search(rf"type {type_name} \{{(?P<body>.*?)\n\}}", _graphql_text(), re.S)
    assert match, f"GraphQL type {type_name} not found"
    return match.group("body")


def _graphql_input_body(input_name: str) -> str:
    match = re.search(rf"input {input_name} \{{(?P<body>.*?)\n\}}", _graphql_text(), re.S)
    assert match, f"GraphQL input {input_name} not found"
    return match.group("body")


def _openapi_audit_actions() -> set[str]:
    enum = (
        _load_openapi()["components"]["schemas"]["AuditIntent"]["properties"][
            "audit_action"
        ]["enum"]
    )
    return set(enum)


def _openapi_target_kinds() -> set[str]:
    enum = (
        _load_openapi()["components"]["schemas"]["AuditIntent"]["properties"][
            "target_kind"
        ]["enum"]
    )
    return set(enum)


def _action_rows() -> list[dict[str, str]]:
    return _table_rows("## Action Bridge")


def _target_rows() -> list[dict[str, str]]:
    return _table_rows("## Target-Kind Bridge")


def _correlation_rows() -> list[dict[str, str]]:
    return _table_rows("## Correlation Bridge")


def _table_rows(section_heading: str) -> list[dict[str, str]]:
    text = INDEX_PATH.read_text(encoding="utf-8")
    section = text.split(section_heading, 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        assert len(cells) == 4
        assert cells[2].startswith("`") and cells[2].endswith("`")
        rows.append(
            {
                "left": cells[0].strip("`"),
                "right": cells[1].strip("`"),
                "status": cells[2].strip("`"),
                "notes": cells[3],
            }
        )
    return rows


def test_audit_action_bridge_covers_graphql_and_openapi_actions():
    graphql_actions = _graphql_enum_values("AppointmentAuditAction")
    openapi_actions = _openapi_audit_actions()
    rows = _action_rows()

    indexed_graphql = {row["left"] for row in rows if row["left"] != "none"}
    indexed_openapi = {row["right"] for row in rows if row["right"] != "none"}

    assert indexed_graphql == graphql_actions
    assert indexed_openapi == openapi_actions
    assert {row["status"] for row in rows} <= ALLOWED_STATUSES


def test_audit_action_bridge_pins_deliberate_asymmetry():
    rows = _action_rows()
    by_graphql = {row["left"]: row for row in rows if row["left"] != "none"}
    by_openapi_only = {row["right"]: row for row in rows if row["left"] == "none"}

    assert by_graphql["DIRECT_COMPATIBILITY_WRITE"]["status"] == "read_model_only"
    assert by_graphql["READ"]["status"] == "read_model_only"
    assert by_graphql["CONFIRMED_WAITING_AREA_MOVE"]["right"] == (
        "appointment_status_changed"
    )
    assert by_graphql["CONFIRMED_WAITING_AREA_MOVE"]["status"] == "bridged"

    assert by_openapi_only["slot_search_normalized"]["status"] == "command_plane_only"
    assert by_openapi_only["slot_search_proposed"]["status"] == "command_plane_only"
    assert (
        by_openapi_only["slot_selected_for_proposal"]["status"]
        == "command_plane_only"
    )


def test_correlation_bridge_matches_graphql_and_openapi_surfaces():
    spec = _load_openapi()
    graphql = _graphql_text()
    rows = _correlation_rows()

    assert "X-Correlation-Id" in OPENAPI_PATH.read_text(encoding="utf-8")
    assert "correlation_id" in (
        spec["components"]["schemas"]["CommandMeta"]["properties"]
    )
    assert "correlation_id" in (
        spec["components"]["schemas"]["ConfirmationAuditEvent"]["properties"]
    )
    assert "correlationId" in _graphql_type_body("AuditEvent")
    assert "correlationId" in _graphql_type_body("AppointmentAuditEvent")
    assert "correlationId" in _graphql_input_body("AuditFilter")

    for row in rows:
        assert row["status"] == "bridged"
        for token in row["left"].split("."):
            assert token in graphql


def test_target_kind_bridge_covers_graphql_and_openapi_targets():
    graphql_targets = _graphql_enum_values("AuditTargetType")
    openapi_targets = _openapi_target_kinds()
    rows = _target_rows()

    indexed_graphql = {row["left"] for row in rows if row["left"] != "none"}
    indexed_openapi = {row["right"] for row in rows if row["right"] != "none"}

    assert indexed_graphql == graphql_targets
    assert indexed_openapi == openapi_targets
    assert {row["status"] for row in rows} <= ALLOWED_STATUSES


def test_graphql_audit_read_models_do_not_absorb_command_fields():
    audit_bodies = "\n".join(
        [
            _graphql_type_body("AuditEvent"),
            _graphql_type_body("AppointmentAuditEvent"),
        ]
    )

    for field in FORBIDDEN_READ_MODEL_FIELDS:
        assert field not in audit_bodies


def test_audit_correlation_index_preserves_closed_gate_boundary():
    text = INDEX_PATH.read_text(encoding="utf-8")
    compact = " ".join(text.split())

    for phrase in REQUIRED_BLOCKED_GATE_PHRASES:
        assert phrase in text
    assert "does not authorize" in text
    assert "does not prove runtime correlation-id propagation" in compact
    assert "GraphQL mutations" in text


def test_audit_correlation_index_names_static_sources():
    text = INDEX_PATH.read_text(encoding="utf-8")

    assert "docs/api-spine/graphql/appointment-diary-read.graphql" in text
    assert "docs/api-spine/openapi/appointment-commands.yaml" in text
