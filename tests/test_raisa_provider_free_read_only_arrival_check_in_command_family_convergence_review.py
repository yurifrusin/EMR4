from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review.md"
CONFIG = ROOT / "app/config.py"
ROUTER = ROOT / "app/routers/appointments.py"
STATUS_ADAPTER = ROOT / "app/services/appointment_status_product_adapter.py"
GRAMMAR = ROOT / "app/services/diary/action_grammar.py"
CONFIRM_ACTIONS = ROOT / "app/services/diary/confirm_actions.py"
ROUTE_CONTRACT = ROOT / "app/services/diary/action_route_contract.py"
PROMOTION = ROOT / "app/services/diary/planned_action_promotion.py"
DIARY = ROOT / "docs/diary/diary.js"
META_GRID = ROOT / "docs/diary/meta-grid.js"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_review_selects_one_canonical_arrival_meaning_and_successor() -> None:
    report = _text(REPORT)
    normalized = " ".join(report.split())
    head = "\n".join(report.splitlines()[:20])
    assert "repository_static_authored_synthetic" in head
    assert "dedicated check-in family is selected" in report
    assert "`Arrived` remains the authoritative appointment state" in normalized
    operation_id = "raisa-provider-free-unmounted-canonical-check-in-product-adapter-extraction-rehearsal"
    assert report.count(operation_id) == 1
    assert "Open exactly one provider-free unmounted implementation tranche" in report


def test_repository_proves_distinct_current_admission_and_effect_contracts() -> None:
    config = _text(CONFIG)
    router = _text(ROUTER)
    adapter = _text(STATUS_ADAPTER)
    assert "rayleen_a5_check_in_enabled: bool = False" in config
    assert 'rayleen_a5_check_in_synthetic_practice_ids: str = ""' in config
    assert '"/proposals/check-in/{appointment_id:uuid}"' in router
    assert '"/proposals/check-in/confirm"' in router
    assert "require_role(UserRole.Receptionist)" in router
    assert "AppointmentStatus.Arrived" in router
    assert "record_appointment_checked_in_event(" in router
    assert 'command.__class__.__name__ != "AppointmentStatusCommand"' in adapter
    assert 'transport["proposal_intent"] != "update_appointment_status"' in adapter
    assert 'if command["waiting_area_id_supplied"]:' in adapter


def test_report_preserves_material_semantic_differences() -> None:
    report = " ".join(_text(REPORT).split())
    for phrase in (
        "Exact `Booked|Confirmed -> Arrived` check-in",
        "different-key reuse of the same signed evidence is rejected",
        "same-practice and same non-null appointment location",
        "diary.appointment_checked_in.v1",
        "Waiting-area-only movement remains a separate command family",
        "must not remain a second interchangeable canonical path",
    ):
        assert phrase in report


def test_first_party_clients_still_use_generic_status_before_cutover() -> None:
    diary = _text(DIARY)
    meta = _text(META_GRID)
    assert 'renderFlowList("flow-list-expected", filteredExpected, "Check In", "Arrived")' in diary
    assert "await setAppointmentStatus(a, targetStatus, null, waitingAreaId);" in diary
    assert '["status", "time", "duration", "practitioner", "cancel"]' in meta
    assert 'status_allowlist: ["Booked", "Arrived", "InConsult", "Completed"]' in meta
    assert "Until the later atomic cutover" in _text(ROOT / "docs/security/raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review-threat-model-delta.md")


def test_static_contract_classification_matches_repository() -> None:
    grammar = _text(GRAMMAR)
    actions = _text(CONFIRM_ACTIONS)
    route_contract = _text(ROUTE_CONTRACT)
    promotion = _text(PROMOTION)
    report = _text(REPORT)
    assert "DiaryActionVerb.check_in: DiaryActionVerbDescriptor(" in grammar
    assert "implemented=False" in grammar
    assert "DiaryConfirmAction.check_in" not in actions
    assert "authority=RouteAuthority.planned_not_implemented" in route_contract
    assert "no check-in confirm action exists" in route_contract
    assert "dedicated signed check-in confirm action" in promotion
    assert "scope-qualified current" in report
    assert "factually superseded" in report
    assert "superseded/incomplete" in report


def test_typed_route_spelling_is_classified_without_claiming_runtime_shadowing() -> None:
    router = _text(ROUTER)
    route_contract = _text(ROUTE_CONTRACT)
    report = " ".join(_text(REPORT).split())
    assert '"/proposals/status/{appointment_id:uuid}"' in router
    assert '/api/v1/appointments/proposals/status/{appointment_id}' in route_contract
    for phrase in (
        "simplistic parameter detector does not recognise the typed segment",
        "falsely reports",
        "static normalization/test drift",
        "not an actual route-order or command authority defect",
    ):
        assert phrase in report


def test_review_does_not_claim_product_admission() -> None:
    report = " ".join(_text(REPORT).lower().split())
    for phrase in (
        "this selection does not enable a5.1",
        "may not yet",
        "enable any practice or call the route",
        "graphql remains read-only",
        "event records the result but is not current truth",
        "does not prove live route or database behavior",
    ):
        assert phrase in report
