from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-reception-one-cancellation-command-path-readiness-review-plan.md"
REPORT = ROOT / "docs" / "raisa-reception-one-cancellation-command-path-readiness-review.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-reception-one-cancellation-command-path-readiness-review-threat-model-delta.md"
)
ROUTER = ROOT / "app" / "routers" / "appointments.py"
SCHEMAS = ROOT / "app" / "schemas" / "appointments.py"
DIARY = ROOT / "docs" / "diary" / "diary.js"
META_GRID = ROOT / "docs" / "diary" / "meta-grid.js"
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"
CONCURRENCY_TEST = ROOT / "tests" / "test_api_spine_delete_confirm_idempotency_route_contract.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _between(text: str, start: str, end: str) -> str:
    return text[text.index(start) : text.index(end)]


def test_readiness_artifacts_freeze_read_only_boundary_and_one_prerequisite():
    plan = _read(PLAN)
    report = _read(REPORT)
    threat = _read(THREAT)

    for text in (plan, report, threat):
        assert "Date: 2026-08-15" in text
        assert "Timestamp:" in text
        assert "Australia/Brisbane" in text

    assert "raisa_reception_one_cancellation_command_path_readiness_review_pass" in plan
    assert "raisa_reception_one_cancellation_command_path_readiness_review_pass" in report
    assert "provider-free, unmounted delete-confirm" in report
    assert "changes no product or runtime behavior" in plan
    assert "No runtime surface changes" in threat


def test_dedicated_delete_family_has_existing_confirmation_safety_controls():
    router = _read(ROUTER)
    route = _between(
        router,
        "def confirm_delete_proposal_route(",
        "def propose_delete_appointment(",
    )

    for marker in (
        "claim_appointment_command(",
        '"explicit_confirmation_required"',
        "verify_signed_confirmation_evidence_block(",
        '"stale_delete_proposal_freshness_id"',
        '"stale_delete_waiting_area_state"',
        "complete_appointment_command(",
        "db.commit()",
    ):
        assert marker in route


def test_delete_confirm_still_lacks_locked_truth_and_in_transaction_authority():
    router = _read(ROUTER)
    route = _between(
        router,
        "def confirm_delete_proposal_route(",
        "def propose_delete_appointment(",
    )
    get_appointment = _between(router, "def _get_appointment(", "def _ensure_patient(")

    assert "_get_appointment(" in route
    assert ".with_for_update(" not in route
    assert ".with_for_update(" not in get_appointment
    assert "current_authority" not in route
    assert "authenticated_bearer_token" not in route
    assert "command_session_factory" not in route


def test_native_diary_fallback_crosses_families_and_drops_text_reason():
    diary = _read(DIARY)
    delete_booking = _between(
        diary,
        "async function deleteBooking()",
        "PATIENT FLOW WORKBENCH & WAITING ROOM LOGIC",
    )
    apply_delete = _between(
        diary,
        "async function applySignedDeleteProposal(",
        "async function setAppointmentStatus(",
    )

    assert "/appointments/proposals/delete/${editingAppointmentId}" in delete_booking
    assert "Fallback to status proposal (omitting cancellation_reason)" in delete_booking
    assert "/appointments/proposals/status/${editingAppointmentId}" in delete_booking
    assert "cancellation_reason" not in delete_booking.split(
        "Fallback to status proposal (omitting cancellation_reason)", 1
    )[1].split("proposal = await propRes.json()", 1)[0]
    assert "/appointments/proposals/status-confirm" in apply_delete
    assert "deleteConfirmIdempotencyKey" in apply_delete
    assert "cancellationReason" not in apply_delete.split("{", 1)[1]
    assert "statusReasonCode" not in apply_delete.split("{", 1)[1]


def test_openapi_and_runtime_delete_shapes_are_deliberately_not_claimed_equal():
    router = _read(ROUTER)
    schemas = _read(SCHEMAS)
    openapi = _read(OPENAPI)
    report = _read(REPORT)

    assert "/appointments/proposals/delete:" in openapi
    assert "/appointments/proposals/delete/confirm:" in openapi
    assert "required: [meta, appointment_id, delete_reason]" in openapi
    assert '@router.post("/proposals/delete/{appointment_id}"' in router
    assert '"/proposals/delete-confirm"' in router
    assert "class AppointmentDeleteIn(BaseModel):" in schemas
    assert "cancellation_reason: Optional[str]" in schemas
    assert "OpenAPI is therefore\nan architecture draft here" in report


def test_reception_one_has_four_controls_and_no_cancellation_bridge():
    meta_grid = _read(META_GRID)
    diary = _read(DIARY)
    palette = _between(
        meta_grid,
        "const palette = createElement",
        "consolePanel.appendChild(palette);",
    )
    bridge = _between(
        diary,
        "window.EMR4DiaryMetaGridBridge = Object.freeze({",
        "async function checkBerniePilotEligibility",
    )

    for action in ("status", "time", "duration", "practitioner"):
        assert f'["{action}",' in palette
    assert '["cancel",' not in palette
    assert "cancelAppointment" not in bridge
    assert "deleteBooking" not in bridge


def test_existing_different_key_test_is_serial_not_overlapping_concurrency():
    tests = _read(CONCURRENCY_TEST)
    case = tests[tests.index("def test_concurrent_different_keys_on_same_delete") :]

    assert case.index('"delete-first-concurrency-key"') < case.index(
        '"delete-second-concurrency-key"'
    )
    assert "Thread" not in case
    assert "Barrier" not in case
