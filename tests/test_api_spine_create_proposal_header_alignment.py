import ast
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"
ROUTER = ROOT / "app" / "routers" / "appointments.py"
DECISION = (
    ROOT / "orchestration" / "api_spine_appointment_idempotency_create_proposal_replay_model.md"
)
ALIGNMENT = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_create_proposal_header_alignment.md"
)
READINESS = (
    ROOT
    / "orchestration"
    / "api_spine_appointment_idempotency_create_proposal_minlength_readiness.md"
)

PROPOSAL_OPERATION_PATHS = {
    "proposeAppointmentCreate": "/appointments/proposals/create",
    "proposeAppointmentUpdate": "/appointments/proposals/update",
    "proposeAppointmentStatus": "/appointments/proposals/status",
    "proposeAppointmentDelete": "/appointments/proposals/delete",
}

UNWIRED_PROPOSAL_HANDLERS = (
    "propose_update_appointment",
    "propose_status_update",
    "propose_delete_appointment",
)


def _openapi_doc():
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed.")
    return yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))


def _router_module() -> ast.Module:
    return ast.parse(ROUTER.read_text(encoding="utf-8"))


def _function_source(name: str) -> str:
    source = ROUTER.read_text(encoding="utf-8")
    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"Could not find function {name}")


def _route_function(name: str) -> ast.FunctionDef:
    for node in _router_module().body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"Could not find route {name}")


def test_openapi_create_proposal_requires_shared_idempotency_header_shape():
    doc = _openapi_doc()
    operation = doc["paths"]["/appointments/proposals/create"]["post"]
    parameter_refs = [parameter["$ref"] for parameter in operation["parameters"]]
    parameter = doc["components"]["parameters"]["IdempotencyKey"]
    schema = parameter["schema"]

    assert operation["operationId"] == "proposeAppointmentCreate"
    assert "#/components/parameters/IdempotencyKey" in parameter_refs
    assert parameter["name"] == "Idempotency-Key"
    assert parameter["in"] == "header"
    assert parameter["required"] is True
    assert schema["type"] == "string"
    assert schema["minLength"] == 8
    assert schema["maxLength"] == 128


def test_openapi_create_proposal_records_runtime_minlength_deferral():
    operation = _openapi_doc()["paths"]["/appointments/proposals/create"]["post"]
    posture = operation["x-emr4-proposal-header-posture"]

    assert posture == {
        "runtime_validation": "non_blank_only",
        "openapi_min_length_runtime_enforcement": "deferred_until_client_readiness_decision",
        "replay_model": "deterministic_re_evaluation_no_proposal_ledger",
    }


def test_openapi_proposal_routes_share_idempotency_header_contract():
    doc = _openapi_doc()

    for operation_id, path in PROPOSAL_OPERATION_PATHS.items():
        operation = doc["paths"][path]["post"]
        parameter_refs = [parameter["$ref"] for parameter in operation["parameters"]]

        assert operation["operationId"] == operation_id
        assert "#/components/parameters/IdempotencyKey" in parameter_refs


def test_fastapi_proposal_header_binding_gap_is_explicitly_documented():
    alignment = ALIGNMENT.read_text(encoding="utf-8")
    readiness = READINESS.read_text(encoding="utf-8")

    assert 'Header(None, alias="Idempotency-Key")' in _function_source(
        "propose_create_appointment"
    )
    for handler in UNWIRED_PROPOSAL_HANDLERS:
        source = _function_source(handler)
        assert 'Header(None, alias="Idempotency-Key")' not in source
        assert handler in alignment
        assert handler in readiness

    assert "3 of 4 canonical" in readiness
    assert "OpenAPI proposal operations" in readiness
    assert "do not yet bind `Idempotency-Key` in FastAPI" in readiness


def test_minlength_enforcement_has_named_client_readiness_preconditions():
    readiness = READINESS.read_text(encoding="utf-8")

    for phrase in (
        "create-proposal clients send a non-blank key",
        "candidate keys are at least 8 characters after trimming",
        "typed short-key rejection contract",
        "All proposal-route header postures are reviewed together",
        "runtime minLength enforcement remains deferred",
    ):
        assert phrase in readiness


def test_fastapi_create_proposal_binds_header_before_proposal_evidence():
    route = _route_function("propose_create_appointment")
    source = _function_source("propose_create_appointment")

    arg_names = [arg.arg for arg in route.args.args]
    assert "idempotency_key" in arg_names
    assert 'Header(None, alias="Idempotency-Key")' in source
    assert source.index("_normalize_create_proposal_idempotency_key(idempotency_key)") < source.index(
        "_build_create_appointment_proposal("
    )


def test_fastapi_create_proposal_runtime_gate_is_non_blank_only_until_client_decision():
    normalizer = _function_source("_normalize_create_proposal_idempotency_key")
    decision = DECISION.read_text(encoding="utf-8")
    alignment = ALIGNMENT.read_text(encoding="utf-8")

    assert 'status.HTTP_400_BAD_REQUEST' in normalizer
    assert '"code": "idempotency_key_required"' in normalizer
    assert "normalized = (raw_key or \"\").strip()" in normalizer
    assert "if not normalized:" in normalizer
    assert "minLength: 8" not in normalizer
    assert "len(normalized)" not in normalizer
    assert "OpenAPI `minLength: 8` validation remains deferred" in decision
    assert "OpenAPI `minLength: 8` is deliberately not enforced at runtime yet" in alignment


def test_create_proposal_alignment_does_not_grant_confirmation_replay_authority():
    route_and_helper = "\n\n".join(
        [
            _function_source("propose_create_appointment"),
            _function_source("_normalize_create_proposal_idempotency_key"),
            _function_source("_build_create_appointment_proposal"),
        ]
    )
    alignment = ALIGNMENT.read_text(encoding="utf-8")

    assert "claim_appointment_command(" not in route_and_helper
    assert "complete_appointment_command(" not in route_and_helper
    assert "AppointmentCommandIdempotency" not in route_and_helper
    assert "no proposal ledger" in alignment
    assert "no stored proposal replay" in alignment
    assert "same-key/different-body conflicts" in alignment


def test_create_proposal_alignment_keeps_other_command_gates_closed():
    text = ALIGNMENT.read_text(encoding="utf-8")

    for phrase in (
        "update/status/waiting-area/delete proposal idempotency enforcement",
        "raw compatibility write idempotency enforcement",
        "slot-search reservation or replay semantics",
        "Bernie interpreter/session command idempotency expansion",
        "provider calls",
        "GraphQL mutations",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "broad historical diary trove mining",
    ):
        assert phrase in text
