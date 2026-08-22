from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_integrated_runner_accepted_guard_graph_materialization_recovery
    as subject,
)


def test_contract_and_every_schema_are_closed_and_bound() -> None:
    contract = subject.load_contract()
    assert contract["operation_id"] == subject.OPERATION_ID
    assert contract["accepted_inventory"] == subject.EXPECTED_INVENTORY
    assert contract["expected_import_closure"] == {
        "module_count": 5,
        "relative_edge_count": 4,
        "bare_edge_count": 8,
        "builtin_edge_count": 3,
        "bare_target_count": 6,
        "all_targets_present": True,
    }
    for path in (
        subject.CONTRACT_SCHEMA_PATH,
        subject.EVIDENCE_SCHEMA_PATH,
        subject.FAILURE_SCHEMA_PATH,
    ):
        schema = json.loads(path.read_bytes())
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False


def test_exact_runner_and_accepted_graph_inventory_are_recovered() -> None:
    sources = subject.accepted_sources(subject.load_contract())
    assert {
        name: {"bytes": len(value), "sha256": subject.sha256_bytes(value)}
        for name, value in sources.items()
    } == subject.EXPECTED_INVENTORY
    runner_text = sources["runner"].decode()
    guard_text = sources["guard"].decode()
    assert (
        'assertEffectiveToolComposition(agentCtx, presets, "emr4-bounded-worker", TOOLS)'
        in runner_text
    )
    assert (
        "export async function assertEffectiveToolComposition("
        "agentCtx, presetService, presetId, requiredTools)"
        in guard_text
    )
    assert "EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID" not in runner_text


def test_complete_import_closure_uses_exact_installed_package_scope() -> None:
    source_root = (
        subject.predecessor.predecessor.package_projection.MATERIALIZATION_SOURCE_ROOT.resolve(
            strict=True
        )
    )
    package_root = source_root / "node_modules" / "@deepseek-ai" / "dsh"
    assert subject.import_closure(subject.load_contract(), package_root) == {
        "module_count": 5,
        "relative_edge_count": 4,
        "bare_edge_count": 8,
        "builtin_edge_count": 3,
        "bare_target_count": 6,
        "all_targets_present": True,
    }


def test_fixture_is_scoped_installed_agent_registry_setup_only() -> None:
    source = subject.fixture_source().decode()
    for required in (
        'import { Context } from "@deepseek-ai/cordis"',
        'import { AgentRegistry } from "@deepseek-ai/dsh-agent"',
        'import { createScope } from "@deepseek-ai/dsh-scope"',
        "await options.setup(agentCtx)",
        "CONTROLLED_POST_GUARD_SENTINEL",
        "await scoped.dispose()",
        "EFFECTIVE_TOOL_COMPOSITION_PASSED",
    ):
        assert required in source
    for forbidden in ("AgentLoop(", "Harness(", "DeepSeek", "provider request"):
        assert forbidden not in source


def _valid_fixture() -> dict[str, object]:
    return {
        "schema_version": subject.FIXTURE_SCHEMA,
        "result": subject.PASS_RESULT,
        "structured_coordinate": subject.SUCCESS_COORDINATE,
        "old_input_invalid_observed": False,
        "factory_create_agent_invocations": 1,
        "setup_invocations": 1,
        "setup_resolved": True,
        "preset_root_reads": 2,
        "preset_mount_reads": 1,
        "preset_mount_calls": 1,
        "tool_view_calls": 1,
        "tool_restrict_calls": 1,
        "tool_schema_calls": 1,
        "hook_installations": 3,
        "scope_disposals": 1,
        "runner_app_exit_code": 1,
        "runner_status": "failed",
        "runner_failure_stage": "factory",
        "runner_request_count": 0,
        "runner_tool_result_count": 0,
        "runner_turn_kind": None,
        "runner_conclusion_marked": False,
        "live_agent_count": 0,
        "raw_error_retained": False,
        "cordis_disposed": True,
    }


@pytest.mark.parametrize(
    ("key", "hostile"),
    (
        ("structured_coordinate", subject.OLD_COORDINATE),
        ("old_input_invalid_observed", True),
        ("setup_resolved", False),
        ("hook_installations", 2),
        ("runner_request_count", 1),
        ("scope_disposals", 0),
    ),
)
def test_fixture_validator_fails_closed(key: str, hostile: object) -> None:
    value = _valid_fixture()
    assert subject.validate_fixture_result(value) == value
    value[key] = hostile
    with pytest.raises(subject.AcceptedGuardGraphError, match="fixture_result_rejected"):
        subject.validate_fixture_result(value)


def test_provider_free_check_starts_no_process_and_preserves_attempt_identity() -> None:
    check_source = inspect.getsource(subject.provider_free_check)
    controller_source = Path(subject.__file__).read_text(encoding="utf-8")
    execute_source = inspect.getsource(subject.execute)
    assert "subprocess.run" not in check_source
    assert "shutil.which" not in check_source
    assert controller_source.count("subprocess.run(") == 1
    assert execute_source.count("subprocess.run(") == 1
    assert subject.ATTEMPT_ID == "accepted-guard-graph-materialization-001"
    result = subject.provider_free_check()
    assert result["result"] == "provider_free_failure_readback_pass"
    assert result["import_closure"]["all_targets_present"] is True
    assert result["node_process_count"] == 0
    assert result["native_harness_process_count"] == 0
    assert result["model_request_count"] == 0
    assert result["provider_request_count"] == 0


def test_persisted_evidence_is_exact_when_attempt_has_run() -> None:
    if not subject.EVIDENCE_PATH.exists():
        failure = json.loads(subject.FAILURE_PATH.read_bytes())
        failure_schema = json.loads(subject.FAILURE_SCHEMA_PATH.read_bytes())
        jsonschema.Draft202012Validator(failure_schema).validate(failure)
        consumed = json.loads(subject.CONSUMED_PATH.read_bytes())
        envelope = json.loads(subject.PROCESS_ENVELOPE_PATH.read_bytes())
        assert failure["result"] == "fixture_result_rejected"
        assert failure["retry_count"] == 0
        assert consumed["status"] == "consumed_before_node_launch"
        assert consumed["retry_count"] == 0
        assert envelope["exit_code"] == 0
        assert envelope["stdout_bytes"] == 756
        assert envelope["stdout_sha256"] == (
            "6e75c083f6b42d5c828d53c7f16a11ae09897023bf0a8139abde615c674225ff"
        )
        assert envelope["stderr_bytes"] == 0
        assert envelope["raw_stream_retained"] is False
        assert not subject.DISPOSABLE_ROOT.exists()
        return
    evidence = json.loads(subject.EVIDENCE_PATH.read_bytes())
    schema = json.loads(subject.EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert evidence["result"] == subject.PASS_RESULT
    assert evidence["fixture"]["structured_coordinate"] == subject.SUCCESS_COORDINATE
    assert evidence["fixture"]["old_input_invalid_observed"] is False
    assert evidence["process_boundary"]["node_process_count"] == 1
    assert evidence["process_boundary"]["model_request_count"] == 0
    assert evidence["process_boundary"]["provider_request_count"] == 0
    assert evidence["process_boundary"]["retry_count"] == 0
    assert evidence["cleanup"]["disposable_root_absent"] is True
    assert not subject.DISPOSABLE_ROOT.exists()
    assert not subject.FAILURE_PATH.exists()


def test_plan_preserves_exact_attempt_and_product_boundaries() -> None:
    plan = (
        subject.REPO_ROOT
        / "docs"
        / "deepseek-native-harness-provider-free-integrated-runner-accepted-guard-graph-materialization-recovery-plan.md"
    ).read_text(encoding="utf-8")
    threat = (
        subject.REPO_ROOT
        / "docs"
        / "security"
        / "deepseek-native-harness-provider-free-integrated-runner-accepted-guard-graph-materialization-recovery-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for required in (
        "one provider-free Node process",
        "There is no retry, resume, fallback, second fixture",
        "No native Harness process",
        "2e34bdad732fdab32fbf778280b3d3c70d66d602",
        "docs/branding/",
        "EFFECTIVE_TOOL_COMPOSITION_PASSED",
        "EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID",
    ):
        assert required in plan
    assert "every edge must match a frozen finite inventory" in threat
    assert "Native Harness, provider, broker, network, database, Docker and product-target" in threat
