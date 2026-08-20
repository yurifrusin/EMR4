from __future__ import annotations

import json
from pathlib import Path
import sys

import jsonschema
import pytest
import yaml

from scripts import (
    deepseek_native_harness_provider_free_emr4_bounded_worker_preset_materialisation_recovery
    as recovery,
)


def _contract() -> dict:
    return recovery.load_contract()


def _evidence() -> dict:
    return json.loads(recovery.EVIDENCE_PATH.read_text(encoding="utf-8"))


def test_contract_is_exact_and_uses_full_git_ids() -> None:
    contract = _contract()
    assert contract["schema_version"] == recovery.CONTRACT_SCHEMA
    assert contract["operation_id"] == recovery.OPERATION_ID
    assert len(contract["planning_source"]) == 40
    assert all(len(value) == 40 for value in contract["accepted_sources"].values())
    assert contract["preset"]["id"] == recovery.PRESET_ID
    assert contract["preset"]["selected_tools"] == ["edit", "glob", "read"]


def test_materialised_payload_is_complete_exact_yaml() -> None:
    projection = recovery.validate_preset_bytes(recovery.PRESET_BYTES)
    assert yaml.safe_load(recovery.PRESET_BYTES) == recovery.EXPECTED_ROWS
    assert projection["install_relative_path"] == (
        ".agent-presets/emr4-bounded-worker/agent.cordis.yml"
    )
    assert projection["row_ids"] == ["tool-fs", "tool-fs-search"]
    assert projection["sample_over_cap_glob_results"] is False


@pytest.mark.parametrize(
    "value",
    [
        "../emr4-bounded-worker/agent.cordis.yml",
        ".agent-presets/../agent.cordis.yml",
        ".agent-presets/emr4_bounded_worker/agent.cordis.yml",
        ".agent-presets/EMR4-bounded-worker/agent.cordis.yml",
        ".agent-presets/emr4-bounded-worker/agent.yml",
        "/.agent-presets/emr4-bounded-worker/agent.cordis.yml",
    ],
)
def test_hostile_relative_paths_fail_closed(value: str) -> None:
    with pytest.raises(
        recovery.PresetMaterialisationError, match="preset_relative_path_invalid"
    ):
        recovery.validate_preset_relative_path(value)


def test_all_frozen_hostile_payload_and_path_variants_reject() -> None:
    results = recovery.hostile_variant_results()
    assert len(results) == 21
    assert all(row["result"] == "rejected" for row in results)
    assert len({row["scenario"] for row in results}) == 21


def test_symbolic_projection_excludes_broader_inherited_surface() -> None:
    minimal = recovery.project_effective_tools(
        list(recovery.UNCONDITIONAL_TOOLS)
    )
    attachment_present = recovery.project_effective_tools(
        [*recovery.UNCONDITIONAL_TOOLS, *recovery.CONDITIONAL_TOOLS]
    )
    assert minimal == ["edit", "glob", "read"]
    assert attachment_present == ["edit", "glob", "read"]
    assert "write" not in minimal
    assert "grep" not in minimal
    assert "read_image" not in attachment_present


def test_symbolic_projection_rejects_missing_selected_tool() -> None:
    with pytest.raises(
        recovery.PresetMaterialisationError, match="selected_tool_not_inherited"
    ):
        recovery.project_effective_tools(["edit", "read", "write"])


def test_symbolic_projection_rejects_scope_local_tool() -> None:
    with pytest.raises(
        recovery.PresetMaterialisationError, match="scope_local_tools_forbidden"
    ):
        recovery.project_effective_tools(
            list(recovery.UNCONDITIONAL_TOOLS), local=["read"]
        )


def test_symbolic_projection_rejects_selection_drift() -> None:
    with pytest.raises(
        recovery.PresetMaterialisationError, match="selected_tools_invalid"
    ):
        recovery.project_effective_tools(
            list(recovery.UNCONDITIONAL_TOOLS),
            selected=["edit", "read", "glob"],
        )


def test_build_evidence_proves_exact_source_semantics() -> None:
    evidence = recovery.build_evidence()
    assert evidence["result"] == "pass"
    checks = evidence["source_semantics"]["checks"]
    assert checks
    assert all(checks.values())
    assert evidence["source_semantics"]["preset_is_authority_boundary"] is False
    assert evidence["source_semantics"]["accepted_guard_remains_mandatory"] is True
    assert evidence["source_semantics"][
        "outer_broker_allowlist_remains_mandatory"
    ] is True


def test_build_evidence_binds_six_exact_cached_packages() -> None:
    evidence = recovery.build_evidence()
    packages = evidence["package_checks"]
    assert [row["name"] for row in packages] == [
        "@deepseek-ai/dsh-base",
        "@deepseek-ai/dsh-headless",
        "@deepseek-ai/dsh-agent-presets",
        "@deepseek-ai/dsh-tools",
        "@deepseek-ai/dsh-tool-fs",
        "@deepseek-ai/dsh-tool-fs-search",
    ]
    assert all(row["version"] == "0.1.0-rc.7" for row in packages)
    assert all(len(row["tar_sha256"]) == 64 for row in packages)


def test_build_evidence_keeps_both_native_attempts_immutable() -> None:
    attempts = recovery.build_evidence()["predecessor_bindings"][
        "immutable_attempts"
    ]
    assert [row["attempt_id"] for row in attempts] == [
        "native-composition-attempt-001",
        "preterminal-observable-composition-recovery-boot-attempt-001",
    ]
    assert all(row["result"] == "fail" for row in attempts)
    assert all(row["unchanged"] is True for row in attempts)


def test_default_cache_root_survives_stripped_localappdata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    cache_root = recovery.default_cache_root()
    assert cache_root.is_dir()
    assert not cache_root.is_symlink()
    assert cache_root.name == "npm-cache"


def test_all_runtime_provider_and_data_action_counts_are_zero() -> None:
    evidence = recovery.build_evidence()
    assert evidence["provider_boundary"] == {
        name: 0 for name in _contract()["required_zero_counts"]
    }
    assert evidence["claim_boundary"]["future_native_execution_authorised"] is False


def test_contract_and_evidence_validate_against_schemas() -> None:
    contract_schema = json.loads(
        recovery.CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    evidence_schema = json.loads(
        recovery.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8")
    )
    jsonschema.validate(_contract(), contract_schema)
    jsonschema.validate(_evidence(), evidence_schema)


def test_committed_outputs_are_byte_exact_and_idempotent() -> None:
    expected = recovery.expected_outputs(recovery.build_evidence())
    recovery.check_outputs(expected)
    assert recovery.MATERIALISED_PATH.read_bytes() == recovery.PRESET_BYTES
    assert recovery.EVIDENCE_PATH.read_bytes() == expected[recovery.EVIDENCE_PATH]
    assert recovery.REPORT_PATH.read_bytes() == expected[recovery.REPORT_PATH]


def test_report_states_two_stage_boundary_and_claim_ceiling() -> None:
    report = recovery.REPORT_PATH.read_text(encoding="utf-8")
    assert "raw inherited surface is deliberately broader" in report
    assert "`edit`, `glob`, `read`" in report
    assert "outer broker allowlist remains separately required" in report
    assert "does not prove live discovery" in report
    assert "occupied DeepSeek worker" in report


def test_controller_has_no_node_network_or_subprocess_execution_path() -> None:
    source = recovery.CONTROLLER_PATH.read_text(encoding="utf-8")
    assert "import subprocess" not in source
    assert "from subprocess" not in source
    assert "import socket" not in source
    assert "\nimport urllib" not in source
    assert "\nfrom urllib" not in source
    assert "\nimport requests" not in source
    assert "\nfrom requests" not in source
    assert "npm " not in source
    assert "node " not in source


def test_cli_check_passes_without_writing(monkeypatch: pytest.MonkeyPatch) -> None:
    before = {
        path: path.read_bytes()
        for path in (
            recovery.MATERIALISED_PATH,
            recovery.EVIDENCE_PATH,
            recovery.REPORT_PATH,
        )
    }
    monkeypatch.setattr(sys, "argv", [recovery.CONTROLLER_PATH.name, "--check"])
    assert recovery.main() == 0
    assert before == {path: path.read_bytes() for path in before}


def test_materialised_output_path_is_inside_operation_root() -> None:
    assert recovery.MATERIALISED_PATH.is_relative_to(recovery.ROOT)
    assert recovery.MATERIALISED_PATH.relative_to(recovery.ROOT).as_posix() == (
        "materialised-home/.agent-presets/emr4-bounded-worker/agent.cordis.yml"
    )
    assert Path(recovery.PRESET_RELATIVE_PATH).name == "agent.cordis.yml"
