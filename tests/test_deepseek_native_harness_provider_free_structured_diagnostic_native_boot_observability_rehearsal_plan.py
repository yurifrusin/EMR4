from __future__ import annotations

import json
from pathlib import Path
import re

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-structured-diagnostic-"
    "native-boot-observability-rehearsal"
)
PLAN = ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT = ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTINUITY = ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT = CONTINUITY / "contract.json"
CONTRACT_SCHEMA = CONTINUITY / "contract.schema.json"
EVIDENCE_SCHEMA = CONTINUITY / "evidence.schema.json"
FULL_OID = re.compile(r"^[0-9a-f]{40}$")


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_plan_and_threat_freeze_exact_no_worker_boundary() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    assert "Status: `frozen`" in plan
    assert "structured-diagnostic-native-boot-observability-attempt-001" in plan
    assert "emr4-diagnostic-observability-missing" in plan
    assert "There is no trailing task, prompt, work order" in plan
    assert "no broker, worker session, task prompt, tool execution" in plan.lower()
    assert "provider-free pre-HMR diagnostic composition" in threat
    assert "No task argument, worker session, broker, tool call" in threat


def test_contract_is_schema_valid_and_uses_full_git_objects() -> None:
    contract = _load(CONTRACT)
    jsonschema.validate(contract, _load(CONTRACT_SCHEMA))
    assert FULL_OID.fullmatch(str(contract["planning_source"]))
    accepted = contract["accepted_sources"]
    assert isinstance(accepted, dict)
    assert all(FULL_OID.fullmatch(str(value)) for value in accepted.values())
    assert contract["attempt"] == {
        "attempt_id": "structured-diagnostic-native-boot-observability-attempt-001",
        "native_process_limit": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
        "reclassification": False,
    }


def test_contract_freezes_exact_argv_diagnostic_terminal_and_zero_counts() -> None:
    contract = _load(CONTRACT)
    assert contract["launch"] == {
        "node_flag": "--expose-internals",
        "profile_flag": "--profile",
        "profile": "emr4-diagnostic-observability-missing",
        "task_arguments": [],
        "timeout_seconds": 30,
        "expected_exit_code": 1,
        "expected_hmr_event_count": 0,
    }
    assert contract["diagnostic"]["cause_chain"] == [
        {
            "position": 0,
            "error_kind": "error",
            "code_coordinate": "none",
            "config_stage": "none",
            "message_coordinate": "none",
            "aggregate_shape": "none",
        }
    ]
    assert contract["terminal"]["schema_version"].endswith(".v2")
    boundary = contract["process_boundary"]
    assert boundary["native_harness_processes"] == 1
    assert boundary["package_materializer_processes"] == 0
    for field in (
        "broker_processes",
        "worker_sessions",
        "prompts",
        "tool_executions",
        "model_requests",
        "provider_requests",
        "network_attempts",
        "docker_invocations",
        "database_invocations",
    ):
        assert boundary[field] == 0


def test_evidence_schema_and_immutable_attempt_bindings_are_closed() -> None:
    schema = _load(EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    contract = _load(CONTRACT)
    artifacts = contract["immutable_artifacts"]
    assert len(artifacts) == 7
    assert len({row["path"] for row in artifacts}) == 7
    assert all(re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) for row in artifacts)
    assert contract["cleanup_required"] is True
    assert contract["raw_streams_retained"] is False
