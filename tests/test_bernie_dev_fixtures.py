"""
GET /api/v1/appointments/dev/bernie-review-fixtures

Dev-only fixture route for Bernie supervised review payloads.

Verifies: auth gate, dev-only gate, all-states default response, state filter,
no appointment writes, no audit writes, no LLM/provider imports.
"""
import inspect
import json

import pytest

import app.routers.bernie_dev as bernie_dev_module
from app.models.appointments import Appointment, AppointmentAuditLog
from tests.conftest import make_token

FIXTURES_URL = "/api/v1/appointments/dev/bernie-review-fixtures"
H15_PREVIEW_URL = "/api/v1/appointments/dev/h15-read-only-explanation-preview"
ALL_STATES = {"blocked", "candidate_selection_required", "confirmation_ready"}


def _get(client, token, url=FIXTURES_URL, **params):
    return client.get(
        url,
        params=params,
        headers={"Authorization": f"Bearer {token}"},
    )


# ── Auth gate ─────────────────────────────────────────────────────────────────

def test_fixtures_require_auth(client):
    resp = client.get(FIXTURES_URL)
    assert resp.status_code == 401


# ── Dev-only gate ─────────────────────────────────────────────────────────────

def test_fixtures_return_404_in_non_dev_environment(client, gp_user, monkeypatch):
    monkeypatch.setattr(bernie_dev_module.settings, "environment", "production")
    token = make_token(gp_user)
    resp = _get(client, token)
    assert resp.status_code == 404


def test_fixtures_available_in_dev_environment(client, gp_user):
    token = make_token(gp_user)
    resp = _get(client, token)
    assert resp.status_code == 200


# ── Default response: all three states ───────────────────────────────────────

def test_default_response_contains_all_three_states(client, gp_user):
    token = make_token(gp_user)
    data = _get(client, token).json()
    assert set(data.keys()) == ALL_STATES


def test_blocked_fixture_structure(client, gp_user):
    token = make_token(gp_user)
    blocked = _get(client, token).json()["blocked"]
    assert blocked["result"] == "blocked"
    assert blocked["safe"] is False
    assert blocked["autonomy_tier"] == "blocked"
    assert blocked["requires_confirmation"] is False
    assert blocked["staff_review"]["status"] == "blocked"
    assert blocked["staff_review"]["confirmation_ready"] is False
    assert len(blocked["blocks"]) > 0
    assert blocked["search_proposal"] is None


def test_candidate_selection_fixture_structure(client, gp_user):
    token = make_token(gp_user)
    candidate = _get(client, token).json()["candidate_selection_required"]
    assert candidate["result"] == "candidate_selection_required"
    assert candidate["safe"] is True
    assert candidate["requires_confirmation"] is False
    assert candidate["staff_review"]["status"] == "candidate_selection_required"
    assert candidate["staff_review"]["confirmation_ready"] is False
    assert len(candidate["staff_review"]["candidate_slots"]) == 3
    assert candidate["search_proposal"] is not None
    assert len(candidate["search_proposal"]["candidates"]) == 3
    assert candidate["selection_proposal"] is None


def test_confirmation_ready_fixture_structure(client, gp_user):
    token = make_token(gp_user)
    conf = _get(client, token).json()["confirmation_ready"]
    assert conf["result"] == "confirmation_ready"
    assert conf["safe"] is True
    assert conf["requires_confirmation"] is True
    assert conf["staff_review"]["status"] == "confirmation_ready"
    assert conf["staff_review"]["confirmation_ready"] is True
    assert conf["staff_review"]["selected_slot"] is not None
    assert conf["staff_review"]["confirm_endpoint"] == "/api/v1/appointments/proposals/create/confirm-bernie"
    assert conf["staff_review"]["confirm_payload"] is not None
    assert conf["staff_review"]["confirm_payload"]["confirmed"] is False
    assert len(conf["staff_review"]["confirm_evidence"]) == 3
    assert conf["selection_proposal"] is not None
    assert conf["selection_proposal"]["create_proposal"] is not None


# ── State filter ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("state", ["blocked", "candidate_selection_required", "confirmation_ready"])
def test_state_filter_returns_only_requested_state(client, gp_user, state):
    token = make_token(gp_user)
    data = _get(client, token, state=state).json()
    assert set(data.keys()) == {state}
    assert data[state]["result"] == state


def test_invalid_state_filter_is_rejected(client, gp_user):
    token = make_token(gp_user)
    resp = _get(client, token, state="invalid_state")
    assert resp.status_code == 422


# ── No-write proof ────────────────────────────────────────────────────────────

def test_fixture_route_writes_no_appointment_rows(client, gp_user, db):
    token = make_token(gp_user)
    before = db.query(Appointment).count()
    _get(client, token)
    db.expire_all()
    assert db.query(Appointment).count() == before


def test_fixture_route_writes_no_audit_rows(client, gp_user, db):
    token = make_token(gp_user)
    before = db.query(AppointmentAuditLog).count()
    _get(client, token)
    db.expire_all()
    assert db.query(AppointmentAuditLog).count() == before


# ── No-LLM proof ─────────────────────────────────────────────────────────────

def test_fixture_module_has_no_llm_provider_imports():
    source = inspect.getsource(bernie_dev_module)
    for forbidden in ["google.genai", "google.generativeai", "vertexai", "openai", "anthropic"]:
        assert forbidden not in source, f"LLM provider import found: {forbidden!r}"


# ── Non-PHI proof ─────────────────────────────────────────────────────────────

def test_fixture_payloads_contain_no_real_pii(client, gp_user):
    token = make_token(gp_user)
    payload_str = json.dumps(_get(client, token).json()).lower()
    for pattern in ["medicare", "@gmail.com", "0412", "0408"]:
        assert pattern not in payload_str, f"Possible PHI found: {pattern!r}"


# ── Determinism ───────────────────────────────────────────────────────────────

def test_fixture_response_is_deterministic_across_calls(client, gp_user):
    token = make_token(gp_user)
    first = _get(client, token).json()
    second = _get(client, token).json()
    assert first == second


# -- H15 read-only explanation preview ---------------------------------------

def test_h15_preview_requires_auth(client):
    resp = client.get(H15_PREVIEW_URL)
    assert resp.status_code == 401


def test_h15_preview_returns_404_in_non_dev_environment(client, gp_user, monkeypatch):
    monkeypatch.setattr(bernie_dev_module.settings, "environment", "production")
    token = make_token(gp_user)
    resp = _get(client, token, url=H15_PREVIEW_URL)
    assert resp.status_code == 404


def test_h15_preview_is_advisory_read_only_and_non_authoritative(client, gp_user):
    token = make_token(gp_user)
    payload = _get(client, token, url=H15_PREVIEW_URL).json()

    assert payload["schema_version"] == "h15_read_only_explanation_preview.v1"
    assert payload["source"] == "authored_synthetic_route_preview"
    assert payload["status"] == "advisory_only"
    assert payload["action_name"] == "explain_schedule"
    assert payload["dispatch"] == "route_read_only"

    assert payload["candidate_scope"] == {
        "origin": "hand_authored_synthetic",
        "uses_raw_diary_text": False,
        "uses_local_trove_payloads": False,
        "uses_historical_diary_candidate_builder": False,
    }
    assert payload["route_boundary"] == {
        "can_search_slots": False,
        "can_offer_candidates": False,
        "can_prepare_proposal": False,
        "can_confirm_or_write": False,
        "authority": "none",
    }
    assert payload["execution_boundary"] == {
        "provider_calls": "prohibited",
        "memory_persistence": "prohibited",
        "database_writes": "prohibited",
        "appointment_writes": "prohibited",
        "audit_writes": "prohibited",
    }


def test_h15_preview_writes_no_appointment_or_audit_rows(client, gp_user, db):
    token = make_token(gp_user)
    before_appointments = db.query(Appointment).count()
    before_audits = db.query(AppointmentAuditLog).count()

    _get(client, token, url=H15_PREVIEW_URL)

    db.expire_all()
    assert db.query(Appointment).count() == before_appointments
    assert db.query(AppointmentAuditLog).count() == before_audits


def test_h15_preview_module_has_no_local_payload_or_provider_coupling():
    source = inspect.getsource(bernie_dev_module).lower()
    for forbidden in [
        "local_data",
        "semantic_h15_candidate_fixtures",
        "semantic_h15_prototype_neutral_aggregate",
        "historical_diary_semantic_candidate_builder",
        "tests.fixtures.h15_semantic_candidates",
        "tests.h15_advisory_adapter",
        "google.genai",
        "google.generativeai",
        "vertexai",
        "openai",
        "anthropic",
    ]:
        assert forbidden not in source, f"H15 preview coupling found: {forbidden!r}"
