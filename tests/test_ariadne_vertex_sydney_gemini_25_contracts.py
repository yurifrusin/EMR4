from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
from pathlib import Path

import pytest
from google.cloud import aiplatform_v1
from google.protobuf.json_format import ParseDict

from scripts import ariadne_vertex_sydney_gemini_25_broker as broker
from scripts import ariadne_vertex_sydney_gemini_25_contracts as contracts
from scripts import ariadne_vertex_sydney_gemini_25_launcher as launcher


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_cell_request_contains_no_provider_or_credential_boundary() -> None:
    request = load(contracts.CELL_REQUEST_PATH)
    assert contracts.validate_cell_request(request) == []
    serialized = json.dumps(request, sort_keys=True)
    assert "service_account" not in serialized
    assert "oauth" not in serialized
    assert "credential" not in serialized
    assert "aiplatform" not in serialized
    assert "googleapis" not in serialized
    assert "gemini-2.5-flash" not in serialized
    assert "bernie-emr4-dev" not in serialized


def test_vertex_request_contract_is_exact_and_toolless() -> None:
    request = contracts.build_vertex_request(load(contracts.CELL_REQUEST_PATH))
    assert set(request) == {"systemInstruction", "contents", "generationConfig"}
    config = request["generationConfig"]
    assert config["temperature"] == 0
    assert config["maxOutputTokens"] == 256
    assert config["responseMimeType"] == "application/json"
    assert config["thinkingConfig"] == {"thinkingBudget": 0}
    assert "tools" not in request
    assert "toolConfig" not in request
    assert "cachedContent" not in request
    assert config["responseSchema"] == contracts.provider_response_schema()
    assert config["responseSchema"]["properties"]["total_tiles"] == {
        "type": "INTEGER",
        "minimum": 5,
        "maximum": 5,
    }
    wire_request = {
        "model": (
            "projects/bernie-emr4-dev/locations/australia-southeast1/"
            "publishers/google/models/gemini-2.5-flash"
        ),
        **request,
    }
    ParseDict(
        wire_request,
        aiplatform_v1.types.GenerateContentRequest.pb()(),
    )
    assert contracts.canonical_hash(config["responseSchema"]) == (
        "sha256:21a2208ab1dc4b73f6134bd378eb532a6b5c974e822985e23c5aa7ecc5d37621"
    )
    assert contracts.canonical_hash(request) == (
        "sha256:784a68a5d4f45d62d2dbe8ab3b0388585d5938abdb8185ead99952eb41375357"
    )


def test_repair_requests_have_distinct_single_use_bindings() -> None:
    dry = load(
        contracts.ARTIFACT_ROOT / "repair-dry-run-cell-request.json"
    )
    occupied = load(
        contracts.ARTIFACT_ROOT / "repair-occupied-cell-request.json"
    )
    assert contracts.validate_cell_request(dry) == []
    assert contracts.validate_cell_request(occupied) == []
    assert dry["attempt_id"] != occupied["attempt_id"]
    assert dry["ledger_id"] != occupied["ledger_id"]
    assert (
        dry["attempt_id"],
        dry["ledger_id"],
    ) in contracts.ADMITTED_ATTEMPT_LEDGER_PAIRS
    assert (
        occupied["attempt_id"],
        occupied["ledger_id"],
    ) in contracts.ADMITTED_ATTEMPT_LEDGER_PAIRS


def test_second_repair_requests_have_distinct_single_use_bindings() -> None:
    dry = load(
        contracts.ARTIFACT_ROOT / "repair-dry-run-002-cell-request.json"
    )
    occupied = load(
        contracts.ARTIFACT_ROOT / "repair-occupied-002-cell-request.json"
    )
    assert contracts.validate_cell_request(dry) == []
    assert contracts.validate_cell_request(occupied) == []
    assert dry["attempt_id"] != occupied["attempt_id"]
    assert dry["ledger_id"] != occupied["ledger_id"]
    assert (
        dry["attempt_id"],
        dry["ledger_id"],
    ) in contracts.ADMITTED_ATTEMPT_LEDGER_PAIRS
    assert (
        occupied["attempt_id"],
        occupied["ledger_id"],
    ) in contracts.ADMITTED_ATTEMPT_LEDGER_PAIRS


def test_proofreader_allows_only_mechanical_safe_repair() -> None:
    proof = contracts.proofread(
        {
            "summary": "  Project Lark has 5 tiles: 3 blue and 2 green.  ",
            "total_tiles": 5,
            "risk_level": "NONE",
            "evidence_ids": ["fact_beta", "fact_alpha"],
        }
    )
    assert proof["disposition"] == "released"
    assert proof["safe_repairs"] == [
        "summary_whitespace_normalized",
        "risk_level_enum_casing_normalized",
        "evidence_ids_deterministically_ordered",
    ]
    assert proof["release"] == {
        "summary": contracts.EXPECTED_SUMMARY,
        "total_tiles": 5,
        "risk_level": "none",
        "evidence_ids": ["fact_alpha", "fact_beta"],
    }


@pytest.mark.parametrize(
    "draft,reason",
    [
        (
            {
                "summary": "Project Lark has 6 tiles.",
                "total_tiles": 5,
                "risk_level": "none",
                "evidence_ids": ["fact_alpha", "fact_beta"],
            },
            "summary_not_exactly_grounded",
        ),
        (
            {
                "summary": contracts.EXPECTED_SUMMARY,
                "total_tiles": 4,
                "risk_level": "none",
                "evidence_ids": ["fact_alpha", "fact_beta"],
            },
            "total_tiles_invalid",
        ),
        (
            {
                "summary": contracts.EXPECTED_SUMMARY,
                "total_tiles": 5,
                "risk_level": "none",
                "evidence_ids": ["fact_alpha", "invented"],
            },
            "evidence_ids_invalid",
        ),
    ],
)
def test_proofreader_fails_closed(draft: dict, reason: str) -> None:
    proof = contracts.proofread(draft)
    assert proof["disposition"] == "edge_aborted"
    assert reason in proof["findings"]
    assert proof["release"] is None
    assert proof["released_field_manifest"] == []


def test_provider_error_contract_is_bounded_and_scanned() -> None:
    raw = json.dumps(
        {
            "error": {
                "code": 400,
                "status": "INVALID_ARGUMENT",
                "message": "Project Lark fact_alpha was rejected",
                "details": [
                    {
                        "fieldViolations": [
                            {"field": "generationConfig.responseSchema"},
                            {"field": "unreviewed.secret.path"},
                        ]
                    }
                ],
            }
        }
    ).encode()
    safe = contracts.sanitize_provider_error(http_status=400, raw=raw)
    assert safe["http_status"] == 400
    assert safe["provider_error_code"] == 400
    assert safe["normalized_status"] == "INVALID_ARGUMENT"
    assert safe["field_violation_paths"] == [
        "generationConfig.responseSchema"
    ]
    assert safe["sanitized_message"] == "provider_diagnostic_redacted"
    assert safe["discarded_raw_error_hash"].startswith("sha256:")
    assert "Project Lark" not in json.dumps(safe)


def test_provider_error_contract_discards_neutral_message_and_untyped_code() -> None:
    raw = json.dumps(
        {
            "error": {
                "code": {"unexpected": "shape"},
                "status": "INVALID_ARGUMENT",
                "message": "A neutral but unconstrained upstream explanation",
                "details": [],
            }
        }
    ).encode()
    safe = contracts.sanitize_provider_error(http_status=400, raw=raw)
    assert safe["provider_error_code"] == 400
    assert safe["normalized_status"] == "INVALID_ARGUMENT"
    assert safe["sanitized_message"] == "provider_diagnostic_redacted"
    serialized = json.dumps(safe, sort_keys=True)
    assert "neutral" not in serialized.casefold()
    assert "unconstrained" not in serialized.casefold()


def test_provider_error_stream_hash_covers_bytes_beyond_parse_prefix() -> None:
    raw = b'{"error":{"status":"INVALID_ARGUMENT"}}' + b"x" * 100_000
    prefix, observed_hash = broker.read_and_hash_provider_error(
        io.BytesIO(raw), parse_limit=64
    )
    assert prefix == raw[:64]
    assert observed_hash == "sha256:" + hashlib.sha256(raw).hexdigest()
    safe = contracts.sanitize_provider_error(
        http_status=400,
        raw=prefix,
        discarded_raw_error_hash=observed_hash,
    )
    assert safe["discarded_raw_error_hash"] == observed_hash


def _state(tmp_path: Path) -> broker.BrokerState:
    token = tmp_path / "broker-token"
    token.write_text("x" * 48, encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    ledger.write_text(
        json.dumps(
            {
                "schema_version": "ariadne.vertex_sydney_single_use_ledger.v1",
                "ledger_id": "gemini-25-primary-ledger-001",
                "attempt_id": "gemini-25-primary-001",
                "policy_id": contracts.POLICY_ID,
                "status": "open",
                "maximum_provider_calls": 0,
                "provider_calls_consumed": 0,
                "fallback_permitted": False,
            }
        ),
        encoding="utf-8",
    )
    return broker.BrokerState(
        argparse.Namespace(
            mode="dry-run",
            token_file=str(token),
            ledger=str(ledger),
            audit=str(tmp_path / "audit.jsonl"),
            policy=str(contracts.POLICY_PATH),
            request=str(contracts.CELL_REQUEST_PATH),
        )
    )


def test_one_use_broker_dry_run_consumes_ledger_and_audits(tmp_path: Path) -> None:
    state = _state(tmp_path)
    state.append_event("broker_ready", {"provider_call": False})
    result = state.execute(load(contracts.CELL_REQUEST_PATH))
    assert result["status"] == "completed"
    assert result["release"]["total_tiles"] == 5
    ledger = load(state.ledger_path)
    assert ledger["status"] == "consumed"
    assert ledger["provider_calls_consumed"] == 0
    assert contracts.validate_audit_chain(state.events)
    assert not any(
        event["event_type"] in {"provider_call_started", "provider_call_completed"}
        for event in state.events
    )
    assert any(
        event["event_type"] == "provider_call_simulated"
        for event in state.events
    )
    with pytest.raises(broker.BrokerError, match="broker_already_used"):
        state.execute(load(contracts.CELL_REQUEST_PATH))


def test_broker_policy_rejects_every_fallback_surface() -> None:
    policy = load(contracts.POLICY_PATH)
    assert policy["automatic_fallback"] is False
    assert policy["allowed_data_plane_hosts"] == [
        "australia-southeast1-aiplatform.googleapis.com"
    ]
    assert {
        "generativelanguage.googleapis.com",
        "aiplatform.googleapis.com",
        "api.openai.com",
        "api.deepseek.com",
    } <= set(policy["rejected_hosts"])
    assert policy["api_key_authentication"] is False
    assert policy["service_account_key_authentication"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider", "other_provider"),
        ("project", "other-project"),
        ("service_account", "other@example.invalid"),
        ("model_id", "other-model"),
        ("location", "global"),
        ("endpoint_hostname", "aiplatform.googleapis.com"),
        ("automatic_fallback", True),
        ("api_key_authentication", True),
    ],
)
def test_broker_fails_closed_for_every_frozen_binding_mismatch(
    tmp_path: Path, field: str, value: object
) -> None:
    policy = load(contracts.POLICY_PATH)
    policy[field] = value
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    token_path = tmp_path / "token"
    token_path.write_text("x" * 48, encoding="utf-8")
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text("{}", encoding="utf-8")
    with pytest.raises(broker.BrokerError, match="broker_policy_invalid"):
        broker.BrokerState(
            argparse.Namespace(
                mode="dry-run",
                token_file=str(token_path),
                ledger=str(ledger_path),
                audit=str(tmp_path / "audit.jsonl"),
                policy=str(policy_path),
                request=str(contracts.CELL_REQUEST_PATH),
            )
        )


def test_broker_does_not_read_api_key_environment() -> None:
    source = Path(broker.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    referenced_attributes = {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    assert "environ" not in referenced_attributes


def test_broker_reduces_adc_discovery_exception_to_safe_code(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    import google.auth

    state = _state(tmp_path)

    def fail_default(*_args, **_kwargs):
        raise RuntimeError("credential path and upstream auth response")

    monkeypatch.setattr(google.auth, "default", fail_default)
    with pytest.raises(
        broker.BrokerError, match="^impersonated_adc_discovery_failed$"
    ):
        state._credentials()
    captured = capsys.readouterr()
    assert "credential path" not in captured.out
    assert "credential path" not in captured.err


def test_isolation_manifest_keeps_credentials_out_of_cell() -> None:
    manifest = load(
        ROOT
        / "orchestration"
        / "continuity"
        / "ariadne-vertex-sydney-gemini-25"
        / "isolation-manifest.json"
    )
    cell = manifest["cell"]
    assert cell["credential_mount"] is False
    assert cell["docker_socket"] is False
    assert cell["host_network"] is False
    assert cell["product_or_database_mount"] is False
    assert cell["network"] == "task_internal_only"
    assert cell["read_only_root"] is True


def test_provider_blocked_launcher_is_exact_and_inert() -> None:
    plan = launcher.check_committed()
    assert launcher.validate_plan(plan) == []
    assert plan["execution_performed"] is False
    assert plan["provider_contacted"] is False
    assert plan["credential_read"] is False
    assert plan["cell_boundary"]["environment"] == []
    assert plan["cell_boundary"]["mounts"] == []
    assert plan["cell_boundary"]["credential_material"] is False
    assert plan["relay_boundary"]["arbitrary_proxy"] is False
    assert plan["docker_commands"]["create_internal_network"] == [
        "docker",
        "network",
        "create",
        "--internal",
        launcher.NETWORK,
    ]
    relay_command = plan["docker_commands"]["create_relay"]
    alias_index = relay_command.index("--network-alias")
    assert relay_command[alias_index + 1] == "broker"


def test_provider_blocked_launcher_has_no_execution_surface() -> None:
    source = Path(launcher.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports |= {
        (node.module or "").split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not imports & {
        "google",
        "http",
        "os",
        "requests",
        "shutil",
        "socket",
        "subprocess",
        "urllib",
    }


def test_historical_provider_blocked_evidence_remains_immutable() -> None:
    evidence_path = (
        contracts.ARTIFACT_ROOT / "tranche-2-provider-blocked-evidence.json"
    )
    evidence = load(evidence_path)
    assert (
        "sha256:" + hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        == "sha256:03321e79aa28b3fc1a4a5215fc1847fb20e78323244cf75d434f3f3b9c6f8e2d"
    )
    assert evidence["provider_contacted"] is False
    assert evidence["adc_inspected"] is False
    assert evidence["provider_calls"] == 0


def test_repair_provider_blocked_evidence_hashes_current_contracts() -> None:
    evidence_path = (
        contracts.ARTIFACT_ROOT / "repair-provider-blocked-evidence.json"
    )
    evidence = load(evidence_path)
    assert evidence["result"].endswith("_pass")
    assert evidence["historical_artifacts_modified"] is False
    assert evidence["authority_accounting"]["provider_calls"] == 0
    assert (
        "sha256:" + hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        == "sha256:8a4c9761d853e51845b68e48c69f6c7fe11ef2ace950e781025379dc0f399293"
    )
