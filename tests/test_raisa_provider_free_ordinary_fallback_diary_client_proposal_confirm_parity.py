import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
ROUTER = ROOT / "app" / "routers" / "appointments.py"
CONFIG = ROOT / "app" / "config.py"
PLAN = (
    ROOT
    / "docs"
    / "raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-plan.md"
)
DESIGN = (
    ROOT
    / "docs"
    / "raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-design.md"
)
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-threat-model-delta.md"
)
INVENTORY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity"
    / "native-diary-raw-call-site-inventory.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _function_source(source: str, name: str) -> str:
    marker = f"function {name}("
    start = source.index(marker)
    next_start = source.find("\nfunction ", start + len(marker))
    if next_start == -1:
        return source[start:]
    return source[start:next_start]


def test_frozen_inventory_names_exactly_seven_unique_source_bound_sites():
    inventory = json.loads(_read(INVENTORY))
    assert inventory["schema_version"] == "raisa.native_diary_raw_call_site_inventory.v1"
    assert inventory["source_head"] == "d08b32db3f7cfbfb2307f3b03b8b83ec3d017f34"
    assert inventory["client_path"] == "docs/diary/diary.js"
    assert inventory["pre_tranche_raw_call_count"] == 7
    assert inventory["accepted_target_raw_call_count"] == 0
    assert inventory["backend_compatibility_routes_remain_mounted"] is True
    sites = inventory["sites"]
    assert len(sites) == 7
    assert len({site["site_id"] for site in sites}) == 7
    assert {site["raw_method"] for site in sites} == {"POST", "PUT", "PATCH", "DELETE"}
    assert all(site["missing_evidence_posture"].startswith("fail_closed") for site in sites)


def test_native_diary_contains_zero_raw_appointment_mutation_calls():
    source = _read(DIARY_JS)
    forbidden_fragments = (
        'apiFetch(`/appointments`,',
        'apiFetch(`/appointments/${editingAppointmentId}`,',
        'apiFetch(`/appointments/${appt.id}`,',
        'apiFetch(`/appointments/${editingAppointmentId}/status`,',
        'apiFetch(`/appointments/${newApptObj.id}/status`,',
        'apiFetch(`/appointments/${appt.id}/status`,',
    )
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_every_native_proposal_family_emits_a_client_idempotency_header():
    source = _read(DIARY_JS)
    save = _function_source(source, "saveBooking")
    move = _function_source(source, "handleMoveResize")
    status = _function_source(source, "setAppointmentStatus")
    delete = _function_source(source, "deleteBooking")
    follow_up_status = _function_source(source, "applyBookingStatusAfterConfirmedBase")

    assert "idempotencyHeadersFor(ensureElementIdempotencyKey(saveBtn))" in save
    assert 'headers: idempotencyHeadersFor(generateClientIdempotencyKey())' in move
    assert "const proposalHeaders = idempotencyHeadersFor(generateClientIdempotencyKey());" in status
    assert status.count("headers: proposalHeaders") == 2
    assert "const proposalHeaders = idempotencyHeadersFor(generateClientIdempotencyKey());" in delete
    assert delete.count("headers: proposalHeaders") == 2
    assert 'headers: idempotencyHeadersFor(generateClientIdempotencyKey())' in follow_up_status


def test_booking_reproposal_blocks_and_warning_drift_are_checked_before_confirm():
    source = _read(DIARY_JS)
    save = _function_source(source, "saveBooking")

    assert "if (proposal)" in save
    block_index = save.index("if (proposal.blocks && proposal.blocks.length > 0)")
    update_confirm_index = save.index("updateConfirmIdempotencyKey(proposal, confirmPayload)")
    assert block_index < update_confirm_index
    assert "storedProposalWarningCodes(saveBtn)" in save
    assert "sameWarningCodes(" in save
    assert "saveBtn.dataset.confirmedWarningCodes = JSON.stringify(warningCodes);" in save
    assert "delete saveBtn.dataset.confirmedWarningCodes;" in source


def test_missing_signed_evidence_fails_closed_for_every_former_fallback():
    source = _read(DIARY_JS)
    expected = {
        "saveBooking": (
            "The appointment update could not be prepared securely.",
            "The appointment could not be prepared securely.",
        ),
        "handleMoveResize": ("The appointment update could not be prepared securely.",),
        "applySignedStatusProposal": ("The status change could not be prepared securely.",),
        "applySignedDeleteProposal": (
            "The appointment cancellation could not be prepared securely.",
        ),
    }
    for function_name, messages in expected.items():
        block = _function_source(source, function_name)
        assert "!confirmEndpoint || !confirmPayload" in block
        for message in messages:
            assert message in block


def test_create_and_update_follow_up_status_use_signed_status_family_and_report_partial_outcome():
    source = _read(DIARY_JS)
    save = _function_source(source, "saveBooking")
    helper = _function_source(source, "applyBookingStatusAfterConfirmedBase")

    assert save.count("applyBookingStatusAfterConfirmedBase(") == 2
    assert 'apiFetch(`/appointments/proposals/status/${appt.id}`' in helper
    assert "showStatusProposalDialog(proposal)" in helper
    assert "applySignedStatusProposal(appt, proposal, newStatus, null)" in helper
    assert "Booking details were saved, but the selected status was not applied." in helper


def test_backend_compatibility_routes_signals_and_default_audit_mode_are_unchanged():
    router = _read(ROUTER)
    config = _read(CONFIG)
    expected = (
        ('@router.post("", response_model=AppointmentOut', "def create_appointment(", "raw_compat_create"),
        ('@router.put("/{appointment_id}"', "def update_appointment(", "raw_compat_update"),
        ('@router.patch("/{appointment_id}/status"', "def update_appointment_status(", "raw_compat_status"),
        ('@router.delete("/{appointment_id}"', "def cancel_appointment(", "raw_compat_delete"),
    )
    for decorator, handler, signal in expected:
        assert decorator in router
        assert handler in router
        assert f'_raw_compat_evidence_and_headers("{signal}")' in router
    assert 'appointment_raw_compat_mode: Literal["audit", "header", "off"] = "audit"' in config


def test_plan_and_security_boundary_deny_route_retirement_and_runtime_expansion():
    combined = "\n".join((_read(PLAN), _read(DESIGN), _read(THREAT)))
    for phrase in (
        "The native client no longer selects the raw routes.",
        "no backend command-kernel convergence",
        "no database/source/watcher/event",
        "no provider call",
        "no deployment, production, release, Pages or protected-ref movement",
        "External raw-route",
    ):
        assert phrase in combined
