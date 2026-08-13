"""Closed contract and evidence tests for status-confirm HTTP convergence."""

import ast
import hashlib
import json
from pathlib import Path

from fastapi.routing import APIRoute
from jsonschema import Draft202012Validator

from app.main import app
from scripts import raisa_provider_free_status_confirm_http_route_convergence as rehearsal


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "orchestration/continuity/raisa-provider-free-status-confirm-http-route-convergence"
CONTRACT = BASE / "rehearsal-contract.json"
CONTRACT_SCHEMA = BASE / "rehearsal-contract.schema.json"
EVIDENCE = BASE / "provider-free-http-postgresql-evidence.json"
EVIDENCE_SCHEMA = BASE / "provider-free-http-postgresql-evidence.schema.json"
PLAN = ROOT / "docs/raisa-provider-free-status-confirm-http-route-convergence-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-status-confirm-http-route-convergence-threat-model-delta.md"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_contract_is_closed_and_all_hostile_mutations_fail() -> None:
    contract = _load(CONTRACT)
    Draft202012Validator(_load(CONTRACT_SCHEMA)).validate(contract)
    rehearsal._validate_contract(contract, exact=True)  # noqa: SLF001
    assert rehearsal.hostile_mutations_rejected(contract) == 112


def test_released_evidence_is_current_complete_and_sanitized() -> None:
    contract = _load(CONTRACT)
    evidence = _load(EVIDENCE)
    Draft202012Validator(_load(EVIDENCE_SCHEMA)).validate(evidence)

    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["contract_sha256"] == _sha(CONTRACT)
    assert evidence["hostile_mutations"] == {
        "attempted": 112,
        "rejected": 112,
        "minimum_required": 100,
    }
    assert [item["id"] for item in evidence["scenarios"]] == [
        f"HRC-S{index:02d}" for index in range(1, 13)
    ]
    assert all(item["status"] == "passed" for item in evidence["scenarios"])
    assert evidence["cleanup"]["status"] == "cleanup_verified"
    assert evidence["cleanup"]["container"] == "container_absent"
    assert evidence["cleanup"]["network"] == "network_absent"
    assert evidence["environment"]["provider_calls"] == 0
    assert evidence["environment"]["product_rows"] == 0
    assert evidence["catalogue"]["two_connection_tenant_context_absent"] is True
    for path, digest in evidence["source_hashes"].items():
        assert digest == contract["read_only_bindings"][path]
        assert digest == _sha(ROOT / path)
    for path, digest in evidence["implementation_hashes"].items():
        assert digest == _sha(ROOT / path)

    forbidden = (
        "authorization: bearer",
        "postgresql://",
        "response_body_canonical_bytes",
        "synthetic-101@",
        "password_hash",
        "insert into",
        "select *",
    )
    rendered = EVIDENCE.read_text(encoding="utf-8").lower()
    assert all(value not in rendered for value in forbidden)


def test_canonical_and_compatibility_routes_share_one_handler() -> None:
    canonical = [
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == "/api/v1/appointments/proposals/status/confirm"
        and "POST" in route.methods
    ]
    compatibility = [
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == "/api/v1/appointments/proposals/status-confirm"
        and "POST" in route.methods
    ]
    assert len(canonical) == len(compatibility) == 1
    assert canonical[0].endpoint is compatibility[0].endpoint
    assert canonical[0].include_in_schema is True
    assert compatibility[0].include_in_schema is False


def test_route_owns_no_local_write_or_fallback_path() -> None:
    source = (ROOT / "app/routers/appointments.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    handler = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "confirm_status_proposal_route"
    )
    span = ast.get_source_segment(source, handler)
    assert span is not None
    assert span.count("compose_product_status_confirm(") == 1
    assert "claim_appointment_command(" not in span
    assert "complete_appointment_command(" not in span
    assert "_apply_appointment_status_update(" not in span
    assert "db.commit(" not in span
    assert "result.stored_response_bytes" in span


def test_plan_and_threat_delta_freeze_required_boundaries() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    for text in (plan, threat):
        assert "Date: 2026-08-13" in text
        assert "Timestamp: 2026-08-13T12:24:35+10:00 (Australia/Brisbane)" in text
    assert "CF-D2" in plan
    assert "visible native Diary" in plan
    assert "exact canonical bytes" in plan
    assert "waiting-area proposal submitted" in plan
    assert "Client selects a database generation" in threat
    assert "Raw bearer enters audit" in threat
