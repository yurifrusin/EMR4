import ast
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from app.services.appointment_status_composition import (
    canonical_status_confirm_envelope_bytes,
    status_confirm_envelope_projection,
)
from scripts import (
    raisa_provider_free_unmounted_status_confirm_route_convergence_composition_rehearsal
    as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "app/services/appointment_status_composition.py"
ROUTER = ROOT / "app/routers/appointments.py"
PLAN = ROOT / (
    "docs/raisa-provider-free-unmounted-status-confirm-route-convergence-"
    "composition-rehearsal-plan.md"
)
THREAT = ROOT / (
    "docs/security/raisa-provider-free-unmounted-status-confirm-route-convergence-"
    "composition-rehearsal-threat-model-delta.md"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_is_closed_and_schema_valid() -> None:
    contract = _load(rehearsal.CONTRACT_PATH)
    schema = _load(rehearsal.SCHEMA_PATH)
    Draft202012Validator(schema).validate(contract)
    rehearsal.validate_contract(contract, schema)
    assert contract["implementation_authorized"] is False
    assert set(contract["forbidden"].values()) == {False}


def test_all_nine_frozen_source_hashes_match() -> None:
    evidence = _load(rehearsal.EVIDENCE_PATH)
    assert len(evidence["source_hashes"]) == 9
    for relative, expected in evidence["source_hashes"].items():
        assert rehearsal._sha256(ROOT / relative) == expected


def test_generated_evidence_matches_exact_builder() -> None:
    assert _load(rehearsal.EVIDENCE_PATH) == rehearsal.build_evidence()


def test_all_twelve_scenarios_pass() -> None:
    evidence = _load(rehearsal.EVIDENCE_PATH)
    assert evidence["scenario_count"] == 12
    assert all(row["passed"] is True for row in evidence["scenarios"])
    assert {
        "src-001-clean-execute",
        "src-002-same-digest-replay",
        "src-003-different-digest-conflict",
        "src-004-authority-revoked",
        "src-005-target-unavailable",
        "src-006-incomplete-scaffold",
        "src-007-locked-generation-changed",
        "src-008-waiting-area-discriminated",
        "src-009-warning-mismatch",
        "src-010-terminal-transition-deferred",
        "src-011-corrupt-stored-bytes",
        "src-012-response-loss-recovery",
    } == {row["id"] for row in evidence["scenarios"]}


def test_initial_and_replay_delivery_are_exact_stored_bytes() -> None:
    db = rehearsal.FakeDatabase()
    initial = rehearsal.compose(db)
    db.mode = "replay"
    replay = rehearsal.compose(db)
    assert initial.kind == "committed"
    assert replay.kind == "replay"
    assert initial.stored_response_bytes == replay.stored_response_bytes
    assert db.effect_count == 1
    assert db.audit_count == 1
    assert db.commit_count == 1


def test_complete_public_envelope_round_trips_with_five_field_projection() -> None:
    envelope = rehearsal.successful_envelope()
    encoded = canonical_status_confirm_envelope_bytes(envelope)
    assert json.loads(encoded) == envelope
    assert status_confirm_envelope_projection(encoded) == {
        "appointment_id": rehearsal.APPOINTMENT_ID,
        "status": "Confirmed",
        "status_reason_code": None,
        "waiting_area_id": None,
        "warning_codes": [],
    }


def test_envelope_is_exact_and_cannot_expand_or_degrade() -> None:
    missing = rehearsal.successful_envelope()
    missing.pop("audit_evidence")
    expanded = rehearsal.successful_envelope()
    expanded["unexpected"] = True
    blocked = rehearsal.successful_envelope()
    blocked["safe"] = False
    for candidate in (missing, expanded, blocked):
        with pytest.raises(ValueError):
            canonical_status_confirm_envelope_bytes(candidate)


def test_all_hostile_mutations_fail_closed() -> None:
    evidence = _load(rehearsal.EVIDENCE_PATH)
    assert evidence["hostile_mutations"] == {"attempted": 65, "rejected": 65}


def test_client_authority_fields_cannot_override_server_owned_ingress() -> None:
    transport = rehearsal.base_transport()
    transport["practice_id"] = "client-practice"
    transport["actor_id"] = "client-actor"
    transport["session_id"] = "client-session"
    db = rehearsal.FakeDatabase()
    result = rehearsal.compose(db, transport=transport)
    assert result.kind == "committed"
    assert db.record.actor_role == "Receptionist"
    assert db.record.target_appointment_id == rehearsal.APPOINTMENT_ID
    assert db.effect_count == 1
    assert db.commit_count == 1


def test_route_does_not_import_or_call_composition() -> None:
    router = ROUTER.read_text(encoding="utf-8")
    assert "appointment_status_composition" not in router
    assert "compose_status_confirm" not in router


def test_service_contains_no_provider_network_or_process_import() -> None:
    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    forbidden_prefixes = (
        "google",
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "asyncio.subprocess",
    )
    assert not any(name.startswith(forbidden_prefixes) for name in imported)


def test_plan_and_threat_delta_freeze_the_unmounted_boundary() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    for phrase in (
        "complete current `AppointmentConfirmStatusProposalOut` payload",
        "initial success and replay release the exact same stored bytes",
        "does not mount or call an",
        "`docs/branding/`",
    ):
        assert phrase in plan
    assert "`implementation_authorized: false`" in threat
    assert "No route, real database, provider" in threat


def test_response_tampering_fails_without_commit() -> None:
    envelope = copy.deepcopy(rehearsal.successful_envelope())
    envelope["appointment"]["id"] = "66666666-6666-4666-8666-666666666666"
    db = rehearsal.FakeDatabase()

    def effect(_decision, _request):
        return rehearsal.StatusConfirmEffectResult(envelope, rehearsal.AUDIT_ID)

    result = rehearsal.compose(db, effect=effect)
    assert result.kind == "error"
    assert result.status_code == 503
    assert db.effect_count == 0
    assert db.audit_count == 0
    assert db.commit_count == 0
    assert db.rollback_count == 1
