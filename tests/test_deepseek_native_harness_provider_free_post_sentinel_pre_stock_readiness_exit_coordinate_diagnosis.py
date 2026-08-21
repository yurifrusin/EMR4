from __future__ import annotations

from dataclasses import replace
import json

from scripts import (
    deepseek_native_harness_provider_free_post_sentinel_pre_stock_readiness_exit_coordinate_diagnosis
    as subject,
)


def _replace_component(
    inputs: subject.StaticInputs, role: str, payload: bytes
) -> subject.StaticInputs:
    components = dict(inputs.components)
    components[role] = payload
    return replace(inputs, components=components)


def _replace_package(
    inputs: subject.StaticInputs, role: str, payload: bytes
) -> subject.StaticInputs:
    package_files = dict(inputs.package_files)
    package_files[role] = payload
    return replace(inputs, package_files=package_files)


def test_exact_static_diagnosis_names_unique_exit_coordinate() -> None:
    contract = subject.load_contract()
    evidence = subject.analyze_static_inputs(
        contract, subject.repository_inputs(contract)
    )

    assert evidence["result"] == "pass"
    assert evidence["verdict"] == "unique_supported_exit_coordinate"
    assert evidence["narrowest_supported_coordinate"] == (
        "headless_startup.apply.missing_task_program_error_to_app_exit_one"
    )
    assert evidence["source_chain"]["supported_link_count"] == 8
    assert evidence["source_chain"]["all_links_supported"] is True
    assert all(value == 0 for value in evidence["zero_activity"].values())


def test_task_argument_mutation_breaks_empty_snapshot_link() -> None:
    contract = subject.load_contract()
    inputs = subject.repository_inputs(contract)
    boot_contract = json.loads(inputs.components["boot_contract"])
    boot_contract["launch"]["task_arguments"] = ["inert"]
    mutated = _replace_component(
        inputs, "boot_contract", subject._canonical_json(boot_contract)
    )

    links = subject.source_links(mutated)

    assert links[0]["coordinate"] == "frozen_launch.empty_inner_argument_snapshot"
    assert links[0]["supported"] is False


def test_disabling_headless_startup_breaks_mount_link() -> None:
    contract = subject.load_contract()
    inputs = subject.repository_inputs(contract)
    profile = inputs.components["profile_and_sentinel_author"].replace(
        b"- id: headless-runner\n  disabled: true",
        b"- id: headless-startup\n  disabled: true\n- id: headless-runner\n  disabled: true",
        1,
    )

    links = subject.source_links(
        _replace_component(inputs, "profile_and_sentinel_author", profile)
    )

    assert links[1]["supported"] is False


def test_startup_branch_mutation_breaks_rejection_link() -> None:
    contract = subject.load_contract()
    inputs = subject.repository_inputs(contract)
    startup = inputs.package_files["headless_startup"].replace(
        b'if (task.trim() === "")', b'if (task.trim() !== "")', 1
    )

    links = subject.source_links(_replace_package(inputs, "headless_startup", startup))

    assert links[5]["supported"] is False


def test_commander_exit_default_mutation_breaks_exit_one_link() -> None:
    contract = subject.load_contract()
    inputs = subject.repository_inputs(contract)
    commander = inputs.package_files["commander_command"].replace(
        b"const exitCode = config.exitCode || 1;",
        b"const exitCode = config.exitCode || 2;",
        1,
    )

    links = subject.source_links(
        _replace_package(inputs, "commander_command", commander)
    )

    assert links[6]["supported"] is False


def test_cmdline_exit_route_mutation_breaks_shutdown_link() -> None:
    contract = subject.load_contract()
    inputs = subject.repository_inputs(contract)
    cmdline = inputs.package_files["cmdline_adapter"].replace(
        b"exit(error.exitCode);", b"return;", 1
    )

    links = subject.source_links(_replace_package(inputs, "cmdline_adapter", cmdline))

    assert links[7]["supported"] is False


def test_terminal_event_mutation_fails_closed() -> None:
    contract = subject.load_contract()
    inputs = subject.repository_inputs(contract)
    terminal = json.loads(inputs.components["failed_terminal"])
    terminal["hmr_events"] = ["sentinel_activated", "stock_headless_hmr_ready"]
    mutated = _replace_component(
        inputs, "failed_terminal", subject._canonical_json(terminal)
    )

    evidence = subject.analyze_static_inputs(contract, mutated)

    assert evidence["result"] == "failed_closed"
    assert evidence["verdict"] == "insufficient_static_evidence"
    assert evidence["narrowest_supported_coordinate"] is None


def test_evidence_never_retains_or_uses_stream_digest() -> None:
    contract = subject.load_contract()
    inputs = subject.repository_inputs(contract)
    terminal = json.loads(inputs.components["failed_terminal"])
    stderr_digest = terminal["streams"]["stderr"]["sha256"]

    evidence = subject.analyze_static_inputs(contract, inputs)
    serialized = json.dumps(evidence, sort_keys=True)

    assert stderr_digest not in serialized
    assert "streams" not in evidence
    assert "stderr_sha256" not in serialized
    assert evidence["zero_activity"]["raw_stream_reconstruction_count"] == 0


def test_contract_forbids_all_executable_harness_activity() -> None:
    method = subject.load_contract()["method"]

    assert method["import_repository_components"] is False
    assert method["execute_javascript"] is False
    assert method["node_process_limit"] == 0
    assert method["harness_process_limit"] == 0
    assert method["broker_process_limit"] == 0
    assert method["worker_process_limit"] == 0
    assert method["model_request_limit"] == 0
    assert method["provider_request_limit"] == 0
    assert method["network_request_limit"] == 0
    assert method["raw_stream_reconstruction"] is False
