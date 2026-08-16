"""Closed contract, plan and evidence tests for the delete-confirm HTTP integration rehearsal."""

import ast
import hashlib
import json
from pathlib import Path

from fastapi.routing import APIRoute
from jsonschema import Draft202012Validator

from app.main import app
from scripts import (
    raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal
    as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "delete-confirm-http-integration-rehearsal"
)
CONTRACT = BASE / "rehearsal-contract.json"
CONTRACT_SCHEMA = BASE / "rehearsal-contract.schema.json"
EVIDENCE = BASE / "provider-free-http-postgresql-evidence.json"
EVIDENCE_SCHEMA = BASE / "provider-free-http-postgresql-evidence.schema.json"
PLAN = ROOT / "docs/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-plan.md"
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-disposable-postgresql-delete-confirm-http-integration-rehearsal-threat-model-delta.md"
)
OWNED_PATHS = (
    "scripts/raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal.py",
    "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal.py",
    "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal_plan.py",
)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )
    ).hexdigest()


def test_contract_is_closed_and_all_hostile_mutations_fail() -> None:
    contract = _load(CONTRACT)
    Draft202012Validator(_load(CONTRACT_SCHEMA)).validate(contract)
    rehearsal._validate_contract(contract, require_digest=True)  # noqa: SLF001
    assert rehearsal.hostile_mutations_rejected(contract) == rehearsal.HOSTILE_MUTATION_TARGET
    assert rehearsal.HOSTILE_MUTATION_TARGET >= 120
    assert _canonical_digest(contract) == rehearsal.EXPECTED_CONTRACT_DIGEST


def test_contract_freezes_scenarios_endpoints_and_tenant_tables() -> None:
    contract = _load(CONTRACT)
    assert [item["id"] for item in contract["scenarios"]] == [
        f"DHI-S{index:02d}" for index in range(1, 13)
    ]
    assert contract["canonical_path"] == (
        "/api/v1/appointments/proposals/delete/confirm"
    )
    assert contract["compatibility_alias"] == (
        "/api/v1/appointments/proposals/delete-confirm"
    )
    assert tuple(contract["tenant_contract"]["forced_rls_tables"]) == (
        "appointments",
        "users",
        "practitioners",
        "patients",
        "appointment_types",
        "user_capability_grants",
        "appointment_command_idempotency",
        "appointment_audit_log",
    )
    assert contract["tenant_contract"]["application_role_superuser"] is False
    assert contract["tenant_contract"]["application_role_bypass_rls"] is False


def test_contract_and_evidence_schemas_are_closed_whole_documents() -> None:
    contract_schema = _load(CONTRACT_SCHEMA)
    evidence_schema = _load(EVIDENCE_SCHEMA)
    assert contract_schema["additionalProperties"] is False
    assert evidence_schema["additionalProperties"] is False
    Draft202012Validator.check_schema(contract_schema)
    Draft202012Validator.check_schema(evidence_schema)
    contract = _load(CONTRACT)
    assert tuple(contract["evidence_allowlist"]) == rehearsal.EXPECTED_EVIDENCE_ALLOWLIST
    assert tuple(contract["evidence_forbidden"]) == rehearsal.EXPECTED_EVIDENCE_FORBIDDEN
    assert tuple(contract["forbidden_surfaces"]) == rehearsal.EXPECTED_FORBIDDEN_SURFACES


def test_plan_freezes_owned_paths_containment_and_twelve_scenarios() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for path in OWNED_PATHS:
        assert path in text
    assert "postgres:16-bookworm" in text
    assert "pull policy `never`" in text
    assert "--internal" in text
    assert "tmpfs" in text
    assert "bounded memory, CPU and PID resources" in text
    assert "non-superuser, non-`BYPASSRLS`" in text
    for index in range(1, 13):
        assert f"DHI-S{index:02d}" in text
    assert "live_local_backend_postgres" in text
    assert "current-authority denial" in text
    assert "closed unavailable result" in text
    assert "return 503" in text


def test_contract_docker_profile_pins_exact_bounded_resources() -> None:
    profile = _load(CONTRACT)["docker_profile"]
    assert profile["context"] == "default"
    assert profile["memory_bytes"] == 536870912
    assert profile["nano_cpus"] == 1000000000
    assert profile["pids_limit"] == 128
    assert profile["restart_policy"] == "no"
    assert profile["published_ports"] is False
    assert profile["network_internal"] is True
    assert profile["pull_policy"] == "never"
    assert profile["relay_container_executable"] == "bash"
    assert profile["relay_container_command"].startswith("exec 3<>/dev/tcp/127.0.0.1/5432")
    psql_argv = rehearsal.catalogue._psql_argv(  # noqa: SLF001
        "docker.exe", "0" * 64, profile
    )
    assert psql_argv[:4] == ["docker.exe", "--context", "default", "exec"]


def test_threat_delta_freezes_fail_closed_controls() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "set_config" in text
    assert "two-pool postflight requires the setting absent" in text
    assert "forced RLS" in text
    assert "current-authority checks" in text
    assert "same typed unavailable result" in text
    assert "Evidence leaks" in text
    assert "row values" in text
    assert "exact-ID absence postflight" in text


def test_canonical_and_compatibility_routes_share_one_handler() -> None:
    canonical = [
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == rehearsal.CANONICAL_URL
        and "POST" in route.methods
    ]
    compatibility = [
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path == rehearsal.ALIAS_URL
        and "POST" in route.methods
    ]
    assert len(canonical) == len(compatibility) == 1
    assert canonical[0].endpoint is compatibility[0].endpoint
    assert canonical[0].include_in_schema is True
    assert compatibility[0].include_in_schema is False


def test_delete_route_owns_no_local_write_or_fallback_path() -> None:
    source = (ROOT / "app/routers/appointments.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    handler = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "confirm_delete_proposal_route"
    )
    span = ast.get_source_segment(source, handler)
    assert span is not None
    assert span.count("compose_product_delete_confirm(") == 1
    assert "db.commit(" not in span
    assert "_apply_appointment_delete(" not in span
    assert "result.stored_response_bytes" in span

def test_released_evidence_when_present_is_complete_and_sanitized() -> None:
    if not EVIDENCE.exists():
        return
    contract = _load(CONTRACT)
    evidence = _load(EVIDENCE)
    Draft202012Validator(_load(EVIDENCE_SCHEMA)).validate(evidence)
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["contract_sha256"] == _sha(CONTRACT)
    assert evidence["hostile_mutations"] == {
        "attempted": rehearsal.HOSTILE_MUTATION_TARGET,
        "rejected": rehearsal.HOSTILE_MUTATION_TARGET,
        "minimum_required": 120,
    }
    assert [item["id"] for item in evidence["scenarios"]] == [
        f"DHI-S{index:02d}" for index in range(1, 13)
    ]
    assert all(item["status"] == "passed" for item in evidence["scenarios"])
    assert evidence["cleanup"]["status"] == "cleanup_verified"
    assert evidence["environment"]["provider_calls"] == 0
    assert evidence["environment"]["product_rows"] == 0
    assert evidence["catalogue"]["two_connection_tenant_context_absent"] is True
    for path, digest in evidence["source_hashes"].items():
        assert digest == _sha(ROOT / path)
    for path, digest in evidence["implementation_hashes"].items():
        assert digest == _sha(ROOT / path)
    rendered = EVIDENCE.read_text(encoding="utf-8").lower()
    for forbidden in (
        "authorization: bearer",
        "postgresql://",
        "response_body_canonical_bytes",
        "synthetic-user-",
        "password_hash",
        "insert into",
        "select *",
    ):
        assert forbidden not in rendered
