from __future__ import annotations

import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / (
    "deepseek-native-harness-provider-free-structured-diagnostic-wrapper-"
    "node-fixture-rehearsal-plan.md"
)
THREAT = ROOT / "docs" / "security" / (
    "deepseek-native-harness-provider-free-structured-diagnostic-wrapper-"
    "node-fixture-rehearsal-threat-model-delta.md"
)
OPERATION_ROOT = ROOT / "orchestration" / "continuity" / (
    "deepseek-native-harness-provider-free-structured-diagnostic-wrapper-"
    "node-fixture-rehearsal"
)


def test_contract_schema_and_exact_four_scenario_order() -> None:
    contract = json.loads((OPERATION_ROOT / "contract.json").read_text(encoding="utf-8"))
    schema = json.loads(
        (OPERATION_ROOT / "contract.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(contract, schema)
    assert contract["scenario_order"] == [
        "nested_known",
        "unknown_secret_shaped",
        "aggregate_multiple",
        "preexisting_sidecar",
    ]
    assert contract["process_boundary"] == {
        "python_controller_processes": 1,
        "node_processes": 4,
        "native_harness_processes": 0,
        "broker_processes": 0,
        "worker_processes": 0,
        "model_requests": 0,
        "provider_requests": 0,
        "serial": True,
    }


def test_plan_freezes_authored_fixture_only_execution_and_bounded_correction() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for phrase in (
        "at most four serial Node",
        "fixture-package/lib/bin.js",
        "identical JavaScript object",
        "preexisting_sidecar",
        "recursive deterministic key-sorting serializer",
        "new exact source commit",
        "Node/Harness/broker/worker/model/provider counts",
    ):
        assert phrase in text


def test_plan_and_threat_keep_dsh_product_and_protected_surfaces_closed() -> None:
    text = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    for phrase in (
        "no DSH import",
        "no DSH import, native Harness process",
        "ordinary-practice enablement",
        "product/patient/clinical data",
        "protected-ref\nmovement",
    ):
        assert phrase in text
    assert "must resolve under the exact disposable" in threat
    assert "cannot prove\nDSH boot" in threat


def test_evidence_schema_requires_candidate_process_retention_and_cleanup() -> None:
    schema = json.loads(
        (OPERATION_ROOT / "evidence.schema.json").read_text(encoding="utf-8")
    )
    assert schema["required"] == [
        "schema_version",
        "operation_id",
        "candidate_source",
        "result",
        "node",
        "scenarios",
        "proof_boundary",
        "retention",
        "cleanup",
    ]
