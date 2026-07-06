from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
GAP_DOC = ROOT / "orchestration" / "api_spine_appointment_idempotency_gap.md"
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"

OPENAPI_IDEMPOTENCY_PATHS = {
    "/appointments/proposals/create",
    "/appointments/proposals/create/confirm",
    "/appointments/proposals/update",
    "/appointments/proposals/update/confirm",
    "/appointments/proposals/status",
    "/appointments/proposals/status/confirm",
    "/appointments/proposals/delete",
    "/appointments/proposals/delete/confirm",
}


def test_gap_doc_records_sprint_and_source_pass():
    text = GAP_DOC.read_text(encoding="utf-8")

    assert "# API Spine Appointment Idempotency-Key Gap Inspection" in text
    assert "| Sprint | 124 |" in text
    for source in (
        "docs/api-spine/openapi/appointment-commands.yaml",
        "orchestration/api_spine_appointment_command_alignment_inventory.md",
        "tests/test_api_spine_appointment_openapi_drift_guard.py",
        "app/routers/appointments.py",
        "app/schemas/appointments.py",
        "app/services/bernie/session_store.py",
        "tests/test_bernie_session_store.py",
        "tests/test_bernie_session_routes.py",
    ):
        assert f"`{source}`" in text


def test_openapi_idempotency_paths_are_documented_as_missing_enforcement():
    doc_text = GAP_DOC.read_text(encoding="utf-8")
    openapi_text = OPENAPI.read_text(encoding="utf-8")

    for path in OPENAPI_IDEMPOTENCY_PATHS:
        assert path in openapi_text
        assert path in doc_text
    assert doc_text.count("missing_http_header_enforcement") == len(
        OPENAPI_IDEMPOTENCY_PATHS
    )


def test_current_appointments_router_has_no_http_idempotency_header_binding():
    router_text = APPOINTMENTS_ROUTER.read_text(encoding="utf-8")

    assert "Idempotency-Key" not in router_text
    assert not re.search(r"idempotency[_-]?key[^\n]{0,120}Header\(", router_text, re.IGNORECASE)
    assert not re.search(r"Header\([^\n]{0,120}idempotency[_-]?key", router_text, re.IGNORECASE)


def test_gap_doc_distinguishes_existing_safety_controls_from_idempotency():
    text = GAP_DOC.read_text(encoding="utf-8")

    for existing_control in (
        "proposal freshness ids",
        "signed confirmation evidence",
        "explicit `confirmed=true`",
        "raw compatibility routes",
        "Bernie session event routes",
    ):
        assert existing_control in text
    assert "not equivalent to HTTP idempotency" in text
    assert "does not satisfy appointment command-plane `Idempotency-Key`" in text


def test_gap_doc_preserves_closed_gate_posture_and_next_slice():
    text = GAP_DOC.read_text(encoding="utf-8")

    assert "Recommended Sprint 125" in text
    assert "Appointment command idempotency policy packet" in text
    for closed_gate in (
        "live providers",
        "runtime FGA clients",
        "external patient clients",
        "GraphQL mutations",
        "broad historical diary trove mining",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "model-to-database writes",
    ):
        assert closed_gate in text
