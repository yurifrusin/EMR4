from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/raisa-provider-free-read-only-post-cancellation-programme-orientation.md"
CONFIG = ROOT / "app/config.py"
ROUTER = ROOT / "app/routers/appointments.py"
OPENAPI = ROOT / "docs/api-spine/openapi/appointment-commands.yaml"
GRAMMAR = ROOT / "app/services/diary/action_grammar.py"
ROUTE_CONTRACT = ROOT / "app/services/diary/action_route_contract.py"
PROMOTION = ROOT / "app/services/diary/planned_action_promotion.py"
DIARY = ROOT / "docs/diary/diary.js"
META_GRID = ROOT / "docs/diary/meta-grid.js"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_orientation_selects_exactly_one_read_only_successor() -> None:
    report = _text(REPORT)
    head = "\n".join(report.splitlines()[:18])
    assert "Date: 2026-08-18" in head
    assert "Timestamp: 2026-08-18T" in head
    assert "+10:00 (Australia/Brisbane)" in head
    assert "repository_static_authored_synthetic" in head
    operation_id = "raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review"
    assert report.count(operation_id) == 1
    assert "Open exactly one provider-free repository-static read-only tranche" in report


def test_repository_proves_default_off_a5_1_routes_and_openapi_contract() -> None:
    config = _text(CONFIG)
    router = _text(ROUTER)
    spec = _text(OPENAPI)
    assert "rayleen_a5_check_in_enabled: bool = False" in config
    assert 'rayleen_a5_check_in_synthetic_practice_ids: str = ""' in config
    assert '"/proposals/check-in/{appointment_id:uuid}"' in router
    assert '"/proposals/check-in/confirm"' in router
    assert "_a5_check_in_gate_open(current_user)" in router
    assert "operationId: proposeAppointmentCheckIn" in spec
    assert "operationId: confirmAppointmentCheckInProposal" in spec


def test_repository_proves_static_check_in_lifecycle_conflict() -> None:
    grammar = _text(GRAMMAR)
    route_contract = _text(ROUTE_CONTRACT)
    promotion = _text(PROMOTION)
    assert "DiaryActionVerb.check_in: DiaryActionVerbDescriptor(" in grammar
    assert "implemented=False" in grammar
    assert "No signed confirm action or endpoint exists yet" in grammar
    assert "DiaryActionVerb.check_in: DiaryActionRouteContract(" in route_contract
    assert "authority=RouteAuthority.planned_not_implemented" in route_contract
    assert 'proposal_routes=("/api/v1/appointments/proposals/status/{appointment_id}",)' in route_contract
    assert "no check-in confirm action exists" in route_contract
    assert "dedicated signed check-in confirm action" in promotion
    assert "reviewed status-confirm binding that records check-in semantics" in promotion
    assert '/api/v1/appointments/proposals/status/{appointment_id}' in route_contract
    assert '"/proposals/status/{appointment_id:uuid}"' in _text(ROUTER)


def test_first_party_clients_use_general_arrived_status_not_a5_1() -> None:
    diary = _text(DIARY)
    meta_grid = _text(META_GRID)
    bridge = diary.split("window.EMR4DiaryMetaGridBridge = Object.freeze({", 1)[1]
    bridge = bridge.split("});", 1)[0]
    assert 'renderFlowList("flow-list-expected", filteredExpected, "Check In", "Arrived")' in diary
    assert 'await setAppointmentStatus(a, targetStatus, null, waitingAreaId);' in diary
    assert "setAppointmentStatus: metaGridSetAppointmentStatus" in bridge
    assert "checkIn" not in bridge
    assert '["status", "time", "duration", "practitioner", "cancel"]' in meta_grid
    assert 'status_allowlist: ["Booked", "Arrived", "InConsult", "Completed"]' in meta_grid


def test_report_matrix_preserves_completed_and_retained_families() -> None:
    report = _text(REPORT)
    for phrase in (
        "Create plus slot selection",
        "Update/reschedule",
        "General status",
        "Waiting-area move",
        "Delete/cancel",
        "Dedicated check-in",
        "Link patient",
        "Preserve",
        "Selected provider-free read-only convergence review",
        "Retain as a later distinct identity/authority gate",
    ):
        assert phrase in report


def test_report_preserves_exact_baseline_endpoint_coverage_failure() -> None:
    report = " ".join(_text(REPORT).split())
    for phrase in (
        "test_diary_action_route_endpoint_coverage.py",
        "reports six failures",
        "{appointment_id}",
        "{appointment_id:uuid}",
        "preserved negative evidence",
        "not a failure caused by this documentation-only candidate",
    ):
        assert phrase in report


def test_orientation_does_not_claim_route_existence_is_product_admission() -> None:
    report = " ".join(_text(REPORT).lower().split())
    for phrase in (
        "route existence, product admission",
        "default-off and restricted to an authored-synthetic practice allowlist",
        "no option is selected by this orientation",
        "keep the a5.1 runtime default-off, uncalled and unmodified",
        "graphql remains read-only",
        "events remain acceleration hints",
    ):
        assert phrase in report
