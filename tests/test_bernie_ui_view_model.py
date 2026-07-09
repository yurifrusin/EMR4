import json
from pathlib import Path

import pytest

from app.services.bernie.ui_view_model import (
    BernieUiViewModel,
    build_bernie_ui_view_model,
)


FIXTURE = Path("tests/fixtures/bernie_ui_view_model/cases.json")
FORBIDDEN_COPY = ("booked", "confirmed", "not found", "missing_practitioner_id", "_id")
FORBIDDEN_SCHEMA_FIELDS = {
    "writes_authorized",
    "write_authorized",
    "confirm_payload",
    "confirmation_payload",
    "signed_confirmation_evidence",
    "proposal_freshness_id",
    "appointment_id",
    "patient_id",
    "practitioner_id",
}


def _cases() -> list[dict]:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "bernie.ui_view_model.fixture.v1"
    return payload["cases"]


@pytest.mark.parametrize("case", _cases(), ids=lambda case: case["id"])
def test_fixture_cases_project_expected_view_model(case):
    view_model = build_bernie_ui_view_model(
        case["snapshot"],
        client_confirmation_request_state=case["client_confirmation_request_state"],
    )
    data = view_model.model_dump(mode="json")

    for field, expected in case["expected"].items():
        if field in data["flags"]:
            assert data["flags"][field] is expected
        elif field.endswith("_state") or field == "copy_mode":
            assert data[field]["value"] == expected
        else:
            assert data[field] == expected


def test_confirmation_state_conditions_multiple_unrelated_flags():
    ready = next(case for case in _cases() if case["id"] == "margaret_dr_shera_proposal_ready")
    awaiting = next(case for case in _cases() if case["id"] == "awaiting_backend_hides_old_candidates")

    ready_model = build_bernie_ui_view_model(ready["snapshot"])
    awaiting_model = build_bernie_ui_view_model(
        awaiting["snapshot"],
        client_confirmation_request_state="awaiting_backend",
    )

    assert ready_model.confirmation_state.value == "ready"
    assert ready_model.flags.show_candidate_slots is True
    assert ready_model.flags.show_confirm_button is True
    assert ready_model.flags.show_choose_another_time is True
    assert ready_model.flags.show_success_copy is False
    assert awaiting_model.confirmation_state.value == "awaiting_backend"
    assert awaiting_model.flags.show_candidate_slots is False
    assert awaiting_model.flags.show_confirm_button is False
    assert awaiting_model.flags.show_choose_another_time is False
    assert awaiting_model.flags.show_success_copy is False


def test_success_copy_only_from_backend_confirmed_session_state():
    for case in _cases():
        model = build_bernie_ui_view_model(
            case["snapshot"],
            client_confirmation_request_state=case["client_confirmation_request_state"],
        )
        if case["snapshot"]["state"] == "confirmed":
            assert model.copy_mode.value == "success"
            assert model.flags.show_success_copy is True
            assert model.confirmation_state.source == "server_snapshot"
        else:
            assert model.copy_mode.value != "success"
            assert model.flags.show_success_copy is False


def test_pre_confirmed_copy_never_claims_booking_or_leaks_raw_codes():
    for case in _cases():
        if case["snapshot"]["state"] == "confirmed":
            continue
        model = build_bernie_ui_view_model(
            case["snapshot"],
            client_confirmation_request_state=case["client_confirmation_request_state"],
        )
        copy = " ".join(
            part for part in [model.primary_copy, model.secondary_copy] if part
        ).lower()
        for forbidden in FORBIDDEN_COPY:
            assert forbidden not in copy, case["id"]


def test_unknown_session_or_client_state_fails_closed():
    base = _cases()[0]["snapshot"]

    with pytest.raises(ValueError, match="Invalid BernieSessionSnapshotOut input"):
        build_bernie_ui_view_model({**base, "state": "surprise_state"})
    with pytest.raises(ValueError, match="Unknown client confirmation request state"):
        build_bernie_ui_view_model(base, client_confirmation_request_state="already_done")


def test_view_model_schema_has_no_write_echo_or_identifier_payload_fields():
    schema_text = json.dumps(BernieUiViewModel.model_json_schema()).lower()

    for forbidden in FORBIDDEN_SCHEMA_FIELDS:
        assert forbidden not in schema_text


def test_selector_source_is_provider_route_db_memory_and_trove_free():
    source = Path("app/services/bernie/ui_view_model.py").read_text(encoding="utf-8").lower()

    for forbidden in [
        "app.routers",
        "sqlalchemy",
        "sessionlocal",
        "get_db",
        "provider",
        "access_ai",
        "rag",
        "graphrag",
        "h15",
        "h_series",
        "historical_diary",
        "local_data",
        "appointmentauditlog",
        "db.commit",
        "db.add",
        "db.flush",
        "writes_authorized",
    ]:
        assert forbidden not in source


def test_only_approved_bernie_route_imports_selector_after_d5_approval():
    allowed_importers = {Path("app/routers/appointments.py")}
    offenders = []
    for path in Path("app/routers").glob("*.py"):
        source = path.read_text(encoding="utf-8", errors="replace")
        imports_selector = (
            "app.services.bernie.ui_view_model" in source
            or "build_bernie_ui_view_model" in source
        )
        if imports_selector and path not in allowed_importers:
            offenders.append(str(path))

    assert offenders == []
