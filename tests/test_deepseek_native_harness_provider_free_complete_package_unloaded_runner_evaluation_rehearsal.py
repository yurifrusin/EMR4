from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_complete_package_unloaded_runner_evaluation_rehearsal
    as controller,
)


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_plan_names_direct_occupied_successor_and_no_speculative_gate() -> None:
    plan = controller.PLAN_PATH.read_text(encoding="utf-8")
    assert "12,950" in plan
    assert "exactly one disposable" in plan
    assert "advances directly to one separately frozen, bounded occupied" in plan
    assert "No further\nprovider-free intermediate" in plan
    assert "especially `docs/branding/`" in plan


def test_fresh_five_source_receipt_passes_with_all_lane_dispositions() -> None:
    receipt = json.loads(
        (
            ROOT
            / "orchestration/agent_inbox/codex/deepseek-native-harness-complete-package-unloaded-runner-evaluation-preplanning-receipt.json"
        ).read_text(encoding="utf-8")
    )
    assert receipt["status"] == "passed"
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert [lane["disposition"] for lane in receipt["parallelism_assessment"]["lanes"]] == [
        "declined",
        "declined",
        "declined",
    ]


def test_exact_accepted_source_inventory_and_lineage_equality() -> None:
    sources, inventory = controller.accepted_module_sources()
    assert inventory == controller.EXPECTED_SOURCE_INVENTORY
    assert sum(len(value) for value in sources.values()) == 21551


def test_complete_derived_runner_has_exact_forwarding_and_terminal_seams() -> None:
    sources, _ = controller.accepted_module_sources()
    runner = sources["derived_runner"].decode("utf-8")
    assert runner.count('const presets = ctx.get("agentPresets");') == 1
    assert runner.count(
        "assertEffectiveToolComposition(agentCtx, presets, PRESET_ID, TOOLS)"
    ) == 1
    assert runner.count('emit("prepublication_veto_diagnosed", null)') == 1
    assert runner.count('ctx.get("appExit")(0)') == 1


def test_stub_inventory_is_exact_and_installed_package_independent() -> None:
    stubs = controller.package_stub_sources()
    assert tuple(stubs) == (
        controller.AGENT_MANIFEST,
        controller.AGENT_SOURCE,
        controller.SESSION_MANIFEST,
        controller.SESSION_SOURCE,
        controller.SCOPE_MANIFEST,
        controller.SCOPE_SOURCE,
        controller.PRESETS_MANIFEST,
        controller.PRESETS_SOURCE,
    )
    rendered = b"".join(stubs.values()).decode("utf-8")
    assert "process.env" not in rendered
    assert "node_modules" not in rendered


def test_fixture_is_authored_synthetic_and_has_no_external_coordinate() -> None:
    source = controller.fixture_source().decode("utf-8")
    assert source.count(f'import {{ apply }} from "./{controller.RUNNER_FILENAME}";') == 1
    assert source.count("agents.create") == 0
    assert 'result: "pass"' in source
    for forbidden in (
        "process.env",
        "node:child_process",
        "node:http",
        "node:https",
        "fetch(",
        ".message",
        ".stack",
        ".cause",
    ):
        assert forbidden not in source


def test_import_closure_is_complete_and_exact() -> None:
    closure = controller.import_closure()
    assert closure["relative_edge_count"] == 4
    assert closure["bare_edge_count"] == 4
    assert closure["builtin_edge_count"] == 3
    assert closure["all_local_targets_materialized"] is True
    assert [item["specifier"] for item in closure["builtin_edges"]] == list(
        controller.EXPECTED_NODE_BUILTINS
    )


@pytest.mark.parametrize(
    ("old", "new", "code"),
    [
        ('./effective-tool-guard.mjs', '../effective-tool-guard.mjs', "relative_import_target_rejected"),
        ('./effective-tool-guard.mjs', '/effective-tool-guard.mjs', "import_specifier_coordinate_rejected"),
        ('./effective-tool-guard.mjs', 'file:effective-tool-guard.mjs', "import_specifier_coordinate_rejected"),
        ('./effective-tool-guard.mjs', 'https://invalid/guard.mjs', "import_specifier_coordinate_rejected"),
        ('./effective-tool-guard.mjs', '.\\effective-tool-guard.mjs', "import_specifier_coordinate_rejected"),
        ('@deepseek-ai/dsh-agent', '@deepseek-ai/dsh-unlisted', "bare_import_specifier_rejected"),
        ('node:crypto', 'node:net', "builtin_import_rejected"),
    ],
)
def test_import_closure_rejects_hostile_specifier_drift(old: str, new: str, code: str) -> None:
    modules = controller.executable_module_sources()
    target = controller.RUNNER_FILENAME
    source = modules[target].decode("utf-8")
    assert old in source
    modules[target] = source.replace(old, new, 1).encode()
    with pytest.raises(controller.CompleteRunnerError, match=code):
        controller.import_closure(modules=modules)


def test_import_closure_rejects_commonjs() -> None:
    modules = controller.executable_module_sources()
    modules[controller.FIXTURE_FILENAME] += b'\nrequire("forbidden");\n'
    with pytest.raises(controller.CompleteRunnerError, match="import_source_coordinate_rejected"):
        controller.import_closure(modules=modules)


def test_import_closure_rejects_unparsed_dynamic_import() -> None:
    modules = controller.executable_module_sources()
    modules[controller.FIXTURE_FILENAME] += b"\nawait import(variable);\n"
    with pytest.raises(controller.CompleteRunnerError, match="import_parse_rejected"):
        controller.import_closure(modules=modules)


def test_import_closure_rejects_missing_and_extra_modules() -> None:
    modules = controller.executable_module_sources()
    del modules[controller.SANITIZER_FILENAME]
    with pytest.raises(controller.CompleteRunnerError, match="module_inventory_rejected"):
        controller.import_closure(modules=modules)
    modules = controller.executable_module_sources()
    modules["extra.mjs"] = b"export const extra = true;\n"
    with pytest.raises(controller.CompleteRunnerError, match="module_inventory_rejected"):
        controller.import_closure(modules=modules)


def test_import_closure_rejects_missing_and_extra_stubs() -> None:
    stubs = controller.package_stub_sources()
    del stubs[controller.AGENT_SOURCE]
    with pytest.raises(controller.CompleteRunnerError, match="stub_inventory_rejected"):
        controller.import_closure(stubs=stubs)
    stubs = controller.package_stub_sources()
    stubs["node_modules/extra/index.mjs"] = b""
    with pytest.raises(controller.CompleteRunnerError, match="stub_inventory_rejected"):
        controller.import_closure(stubs=stubs)


def test_materialized_inventory_is_exactly_thirteen_files() -> None:
    sources = controller.materialized_sources()
    assert tuple(sources) == controller.MATERIALIZED_RELATIVE_PATHS
    assert len(sources) == 13
    assert all(Path(path).is_absolute() is False for path in sources)


def test_expected_sidecar_has_exact_success_terminal_and_zero_activity() -> None:
    sidecar = controller.expected_sidecar("a" * 40)
    assert len(sidecar) == 39
    assert sidecar["result"] == "prepublication_veto_diagnosed"
    assert sidecar["last_admitted_stage"] == "postrollback_registries_empty"
    assert sidecar["preset_mounted"] is True
    assert sidecar["model_selection_installed"] is True
    assert sidecar["veto_exact"] is True
    assert sidecar["veto_rejected"] is True
    assert sidecar["request_count"] == 0
    assert sidecar["model_request_count"] == 0
    assert sidecar["provider_request_count"] == 0
    assert sidecar["raw_error_retained"] is False


def test_validate_process_result_accepts_only_exact_wire_and_sidecar_order() -> None:
    candidate = "a" * 40
    fixture = controller.exact_fixture_result()
    sidecar = controller.expected_sidecar(candidate)
    completed = subprocess.CompletedProcess(
        args=["node"],
        returncode=0,
        stdout=controller.canonical_bytes(fixture),
        stderr=b"",
    )
    assert controller.validate_process_result(
        completed=completed,
        sidecar_bytes=(json.dumps(sidecar, separators=(",", ":")) + "\n").encode(),
        candidate_source=candidate,
    ) == (fixture, sidecar)


@pytest.mark.parametrize("field", ["returncode", "stdout", "stderr"])
def test_validate_process_result_rejects_process_drift(field: str) -> None:
    fixture = controller.exact_fixture_result()
    values = {
        "args": ["node"],
        "returncode": 0,
        "stdout": controller.canonical_bytes(fixture),
        "stderr": b"",
    }
    values[field] = 2 if field == "returncode" else b"drift"
    completed = subprocess.CompletedProcess(**values)
    with pytest.raises(controller.CompleteRunnerError, match="complete_runner_result_rejected"):
        controller.validate_process_result(
            completed=completed,
            sidecar_bytes=controller.canonical_bytes(controller.expected_sidecar("a" * 40)),
            candidate_source="a" * 40,
        )


def test_validate_process_result_rejects_sidecar_key_order_and_value_drift() -> None:
    candidate = "a" * 40
    fixture = controller.exact_fixture_result()
    completed = subprocess.CompletedProcess(
        args=["node"], returncode=0, stdout=controller.canonical_bytes(fixture), stderr=b""
    )
    sidecar = controller.expected_sidecar(candidate)
    reordered = dict(reversed(list(sidecar.items())))
    with pytest.raises(controller.CompleteRunnerError, match="complete_runner_result_rejected"):
        controller.validate_process_result(
            completed=completed,
            sidecar_bytes=(json.dumps(reordered, separators=(",", ":")) + "\n").encode(),
            candidate_source=candidate,
        )
    changed = copy.deepcopy(sidecar)
    changed["request_count"] = 1
    with pytest.raises(controller.CompleteRunnerError, match="complete_runner_result_rejected"):
        controller.validate_process_result(
            completed=completed,
            sidecar_bytes=(json.dumps(changed, separators=(",", ":")) + "\n").encode(),
            candidate_source=candidate,
        )


def test_process_envelope_is_content_free_and_closes_second_process() -> None:
    envelope = controller.build_process_envelope(
        candidate_source="a" * 40,
        returncode=0,
        stdout=b"fixture",
        stderr=b"",
        sidecar=b"sidecar",
        sidecar_present=True,
        fixture_root_absent=True,
    )
    assert envelope["stream_and_sidecar_content_retained_before_envelope"] is False
    assert envelope["raw_runtime_detail_retained"] is False
    assert envelope["node_process_count"] == 1
    assert envelope["further_process_authorized"] is False
    assert "stdout_content" not in envelope
    assert "stderr_content" not in envelope
    assert "sidecar_content" not in envelope


def test_minimum_environment_has_exact_five_keys_and_forbids_path() -> None:
    source = {key: f"value-{index}" for index, key in enumerate(controller.WINDOWS_ENVIRONMENT_KEYS)}
    source.update({"PATH": "forbidden", "NODE_OPTIONS": "forbidden", "SECRET": "forbidden"})
    observed = controller.minimum_windows_environment(source)
    assert tuple(observed) == controller.WINDOWS_ENVIRONMENT_KEYS
    assert controller.FORBIDDEN_ENVIRONMENT_KEYS.isdisjoint(observed)


def test_contract_is_machine_git_bound_without_caller_authored_oid() -> None:
    contract = controller.contract_value()
    assert contract["git_binding_policy"]["caller_authored_object_id_count"] == 0
    assert controller.FULL_OID.search(json.dumps(contract, sort_keys=True)) is None
    assert contract["import_closure"] == controller.import_closure()
    assert contract["source_byte_total"] == 21551
    assert contract["claim_boundary"]["native_harness_proved"] is False


def test_all_schemas_are_draft_2020_12_valid() -> None:
    for path in (
        controller.CONTRACT_SCHEMA_PATH,
        controller.PROCESS_ENVELOPE_SCHEMA_PATH,
        controller.EVIDENCE_SCHEMA_PATH,
        controller.FAILURE_TERMINAL_SCHEMA_PATH,
    ):
        jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
