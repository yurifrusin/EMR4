from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "orchestration" / "api_spine_appointment_command_alignment_inventory.md"
APPOINTMENTS_ROUTER = ROOT / "app" / "routers" / "appointments.py"
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_inventory_records_sprint_and_source_pass():
    text = _read(INVENTORY)

    assert "# API Spine Appointment Command Envelope Alignment Inventory" in text
    assert "| Sprint | 121 |" in text
    for source in (
        "app/routers/appointments.py",
        "app/schemas/appointments.py",
        "docs/api-spine/openapi/appointment-commands.yaml",
        "orchestration/api_spine_post_sprint118_checkpoint.md",
        "orchestration/bernie_release_gates.md",
    ):
        assert f"`{source}`" in text


def test_inventory_covers_current_router_route_families():
    inventory = _read(INVENTORY)
    router = _read(APPOINTMENTS_ROUTER)

    route_markers = (
        ("/proposals/create", "/proposals/create"),
        ("/proposals/create/confirm", "/proposals/create/confirm"),
        ("/proposals/update/{appointment_id}", "/proposals/update/{appointment_id}"),
        ("/proposals/update/confirm", "/proposals/update/confirm"),
        ("/proposals/status/{appointment_id:uuid}", "/proposals/status/{appointment_id:uuid}"),
        ("/proposals/waiting-area/{appointment_id}", "/proposals/waiting-area/{appointment_id}"),
        ("/proposals/status/confirm", "/proposals/status/confirm"),
        ("/proposals/status-confirm", "/proposals/status-confirm"),
        ("/proposals/delete/{appointment_id}", "/proposals/delete/{appointment_id}"),
        ("/proposals/delete/confirm", "/proposals/delete/confirm"),
        ("/proposals/delete-confirm", "/proposals/delete-confirm"),
        ("/proposals/slot-search/normalize", "/proposals/slot-search/normalize"),
        ("/proposals/slot-search", "/proposals/slot-search"),
        ("/proposals/slot-search/normalized", "/proposals/slot-search/normalized"),
        ("/proposals/slot-search/selection", "/proposals/slot-search/selection"),
        ("/proposals/bernie/tool-intent", "/proposals/bernie/tool-intent"),
        (
            "/proposals/bernie/interpret-booking-instruction",
            "/proposals/bernie/interpret-booking-instruction",
        ),
        ("/proposals/bernie/supervised-booking", "/proposals/bernie/supervised-booking"),
        ("/proposals/create/confirm-bernie", "/proposals/create/confirm-bernie"),
        (
            "/proposals/bernie/no-slot-suggestion-selection",
            "/proposals/bernie/no-slot-suggestion-selection",
        ),
        ("/bernie/pilot-eligibility", "/bernie/pilot-eligibility"),
        ("/bernie/sessions/active", "/bernie/sessions/active"),
        ("/bernie/sessions/new", "/bernie/sessions/new"),
        ("/bernie/sessions/{session_id}/events", "/bernie/sessions/{session_id}/events"),
        ("@router.post(\"\"", "POST /api/v1/appointments"),
        ("@router.put(\"/{appointment_id}\"", "PUT /api/v1/appointments/{appointment_id}"),
        (
            "@router.patch(\"/{appointment_id}/status\"",
            "PATCH /api/v1/appointments/{appointment_id}/status",
        ),
        ("@router.delete(\"/{appointment_id}\"", "DELETE /api/v1/appointments/{appointment_id}"),
        ("/{appointment_id}/checkin-defaults", "/{appointment_id}/checkin-defaults"),
        ("/{appointment_id}/audit", "/{appointment_id}/audit"),
        ("/slots/{practitioner_id}", "/slots/{practitioner_id}"),
    )
    for router_marker, inventory_marker in route_markers:
        assert router_marker in router, f"{router_marker} missing from appointments router"
        assert inventory_marker in inventory, f"{inventory_marker} missing from API Spine inventory"


def test_inventory_uses_expected_classification_vocabulary():
    text = _read(INVENTORY)

    for phrase in (
        "proposal command",
        "confirm command",
        "command-style read",
        "Bernie session command",
        "compatibility write",
        "read-only route",
    ):
        assert phrase in text


def test_inventory_records_openapi_drift_without_changing_canonical_draft():
    inventory = _read(INVENTORY)
    openapi = _read(OPENAPI)

    deliberate_drift_pairs = (
        ("status-confirm", "/appointments/proposals/status/confirm"),
        ("delete-confirm", "/appointments/proposals/delete/confirm"),
        ("slot-search/selection", "/appointments/proposals/slot-search/select"),
    )
    for backend_fragment, openapi_path in deliberate_drift_pairs:
        assert backend_fragment in inventory
        assert openapi_path in inventory
        assert openapi_path in openapi

    for backend_only in (
        "confirm-bernie",
        "bernie/supervised-booking",
        "bernie/tool-intent",
        "bernie/interpret-booking-instruction",
        "bernie/no-slot-suggestion-selection",
        "bernie/sessions",
        "compatibility writes",
        "Idempotency-Key",
    ):
        assert backend_only in inventory


def test_inventory_preserves_closed_gate_posture():
    text = _read(INVENTORY)

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
