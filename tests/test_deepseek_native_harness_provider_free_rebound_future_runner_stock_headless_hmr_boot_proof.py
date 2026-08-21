from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from orchestration_harness import native_post_hmr_future_attempt_materialisation as base_bundle
from scripts import (
    deepseek_native_harness_provider_free_rebound_future_runner_stock_headless_hmr_boot_proof as subject,
)


CONTRACT = json.loads(subject.CONTRACT_PATH.read_bytes())


def _paths() -> dict[str, Path]:
    root = Path("C:/deterministic/rebound-runner-test").resolve()
    return {
        "profile": root / "home" / "profiles" / "headless",
        "readiness": root / "readiness.jsonl",
        "diagnostic": root / "bundle" / "control" / "post-hmr-diagnostic.json",
        "terminal": root / "bundle" / "control" / "future-attempt-bundle.json",
        "shipped": root / "mismatch-shipped",
        "user": root / "mismatch-user",
    }


def _patches() -> tuple[bytes, bytes]:
    paths = _paths()
    return subject.build_patch_pair(
        profile_dir=paths["profile"],
        readiness_path=paths["readiness"],
        diagnostic_path=paths["diagnostic"],
        collision_terminal_path=paths["terminal"],
        shipped_mismatch=paths["shipped"],
        user_mismatch=paths["user"],
    )


def test_contract_and_schema_are_closed_and_valid() -> None:
    schema = json.loads(subject.CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(CONTRACT)
    assert schema["additionalProperties"] is False
    assert CONTRACT["planning_source"] == "d1f9e549068c4ac1bb6348219b389e02e10352da"


def test_execution_attempt_is_exactly_one_process_without_retry() -> None:
    assert CONTRACT["execution_attempt"] == {
        "attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }


def test_prelaunch_materialisation_generation_two_owns_direct_npm_cli() -> None:
    assert CONTRACT["materialisation"] == {
        "generation": 2,
        "process_count": 1,
        "retry_count": 0,
        "direct_node_npm_cli": True,
        "timeout_seconds": 600,
        "node_executable_sha256": "9a4eb5f1c29c6a2e93852ead46b999e284a6a5ca8bab4d4e241d587d025a52de",
        "npm_cli_sha256": "3ce7cba6f5128dd5f54c98b6a5036b0f850496878cc2e21044b675fe3c594e3e",
    }


def test_owned_materializer_is_direct_and_waited_without_wrapper() -> None:
    source = inspect.getsource(subject._owned_offline_install)
    assert source.count("subprocess.Popen(") == 1
    assert "subprocess.run(" not in source
    assert '"npm-cli.js"' not in source
    assert "npm.cmd" not in source.lower()
    assert "stdout=subprocess.DEVNULL" in source
    assert "stderr=subprocess.DEVNULL" in source
    assert "process.wait(" in source
    assert source.count("_terminate_process(process)") == 2


def test_owned_materializer_paths_are_hash_bound() -> None:
    node, npm_cli = subject._owned_materializer_paths(CONTRACT)
    assert subject.sha256_file(node) == CONTRACT["materialisation"][
        "node_executable_sha256"
    ]
    assert subject.sha256_file(npm_cli) == CONTRACT["materialisation"][
        "npm_cli_sha256"
    ]


def test_prelaunch_failure_is_typed_and_did_not_consume_native_attempt() -> None:
    value = json.loads(subject.PRELAUNCH_FAILURE_PATH.read_bytes())
    assert value["result"] == "prelaunch_rejected"
    assert value["cause_coordinate"] == (
        "npm_descendant_outlived_parent_and_held_disposable_installation"
    )
    assert value["native_harness_process_count"] == 0
    assert value["execution_attempt_consumed"] is False
    assert value["owned_orphan_terminated"] is True
    assert value["disposable_root_cleanup_complete"] is True


def test_bundle_identity_remains_the_accepted_rebound_identity() -> None:
    assert CONTRACT["bundle_identity"] == {
        "operation_id": "deepseek-native-harness-provider-free-future-attempt-identity-and-target-rebinding-rehearsal",
        "attempt_id": "future-identity-target-rebinding-fixture-001",
        "candidate_source": "deaf0b3ccc23adb2f2f17b275a6a7faa4d2ae2ac",
    }


def test_source_payloads_are_exactly_bound() -> None:
    runner, helper, guard, sentinel, bindings = subject.source_payloads(CONTRACT)
    assert bindings == CONTRACT["source_bindings"]
    assert subject.sha256_bytes(runner) == CONTRACT["source_bindings"][
        "future_runner_sha256"
    ]
    assert subject.sha256_bytes(helper) == CONTRACT["source_bindings"][
        "generated_helper_sha256"
    ]
    assert subject.sha256_bytes(guard) == CONTRACT["source_bindings"][
        "effective_tool_guard_sha256"
    ]
    assert subject.sha256_bytes(sentinel) == CONTRACT["source_bindings"][
        "readiness_sentinel_sha256"
    ]


def test_target_is_inert_and_use_is_not_authorized() -> None:
    assert CONTRACT["target_binding"] == {
        "classification": "inert_authored_synthetic_relative_python_fixture",
        "relative_path": "workspace/authored_synthetic_control_probe.py",
        "coordinate_sha256": "f1a4634e24e1cde4bcddfcc88e932a44d75843f6c8a47c1568599775f219c72d",
        "occupied_target_use_authorized": False,
    }


def test_initial_patch_contains_only_sentinel_after_disabled_rows() -> None:
    initial, _ = _patches()
    direct, inserted = subject._patch_rows(initial)
    assert direct == [
        {"id": "headless-runner", "disabled": True},
        {"id": "code-runtime", "disabled": True},
        {"id": "session-telemetry-otel", "disabled": True},
    ]
    assert [row["id"] for row in inserted] == ["provider-free-rebound-hmr-sentinel"]


def test_changed_patch_preserves_sentinel_and_adds_exact_services() -> None:
    initial, changed = _patches()
    _, initial_inserted = subject._patch_rows(initial)
    _, changed_inserted = subject._patch_rows(changed)
    assert changed_inserted[:1] == initial_inserted
    assert [row["id"] for row in changed_inserted] == [
        "provider-free-rebound-hmr-sentinel",
        "agent-presets",
        "provider-free-rebound-future-runner",
    ]
    assert changed_inserted[-1]["inject"] == [
        "hmr",
        "headlessStartup",
        "agents",
        "sessions",
        "agentPresets",
    ]


def test_runner_terminal_collides_with_existing_bundle_manifest_by_contract() -> None:
    _, changed = _patches()
    rows = yaml.safe_load(changed)
    runner = rows[-1]["insert"][-1]
    assert runner["config"]["terminalPath"].endswith(
        "bundle\\control\\future-attempt-bundle.json"
    )
    assert runner["config"]["diagnosticPath"].endswith(
        "bundle\\control\\post-hmr-diagnostic.json"
    )


def test_mismatch_coordinates_are_distinct_and_deliberate() -> None:
    _, changed = _patches()
    runner = yaml.safe_load(changed)[-1]["insert"][-1]
    assert runner["config"]["shippedRoot"] != runner["config"]["userRoot"]
    assert runner["config"]["shippedRoot"].endswith("mismatch-shipped")
    assert runner["config"]["userRoot"].endswith("mismatch-user")


def test_patch_validator_rejects_service_injection_drift() -> None:
    initial, changed = _patches()
    paths = _paths()
    mutated = changed.replace(
        b"hmr, headlessStartup, agents, sessions, agentPresets",
        b"hmr, agents, sessions, agentPresets",
    )
    with pytest.raises(subject.ReboundNativeBootError, match="runner_patch_row_invalid"):
        subject.validate_patch_pair(
            initial,
            mutated,
            diagnostic_path=paths["diagnostic"],
            collision_terminal_path=paths["terminal"],
            shipped_mismatch=paths["shipped"],
            user_mismatch=paths["user"],
        )


def test_expected_terminal_is_one_closed_subcoordinate() -> None:
    assert CONTRACT["expected_terminal"] == {
        "coordinate": "post_hmr_pre_request_failure",
        "diagnostic_accepted": True,
        "broker_zero": True,
        "pre_request_supported": True,
        "stage": "preset_root_roster_admission",
        "cause_coordinate": "preset_root_roster_mismatch",
        "error_kind": "error",
    }


def test_success_classifier_requires_every_containment_reading() -> None:
    assert (
        subject._failure_coordinate(
            process_started=True,
            readiness_valid=True,
            readiness_events=["sentinel_activated", "stock_headless_hmr_ready"],
            mutated=True,
            sidecar={
                "stage": "preset_root_roster_admission",
                "cause_coordinate": "preset_root_roster_mismatch",
                "error_kind": "error",
            },
            terminal={"coordinate": "post_hmr_pre_request_failure"},
            network_attempt_count=0,
            network_ledger_valid=True,
            bundle_unchanged=True,
            target_absent=True,
            process_absent=True,
            root_absent=True,
        )
        is None
    )


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("network_attempt_count", 1, "NETWORK_BOUNDARY_REJECTED"),
        ("mutated", False, "HMR_MUTATION_REJECTED"),
        ("bundle_unchanged", False, "CANONICAL_BUNDLE_MUTATED"),
        ("target_absent", False, "TARGET_BOUNDARY_REJECTED"),
        ("root_absent", False, "CLEANUP_REJECTED"),
    ],
)
def test_success_classifier_fails_closed(field: str, value: object, expected: str) -> None:
    arguments = {
        "process_started": True,
        "readiness_valid": True,
        "readiness_events": ["sentinel_activated", "stock_headless_hmr_ready"],
        "mutated": True,
        "sidecar": {
            "stage": "preset_root_roster_admission",
            "cause_coordinate": "preset_root_roster_mismatch",
            "error_kind": "error",
        },
        "terminal": {"coordinate": "post_hmr_pre_request_failure"},
        "network_attempt_count": 0,
        "network_ledger_valid": True,
        "bundle_unchanged": True,
        "target_absent": True,
        "process_absent": True,
        "root_absent": True,
    }
    arguments[field] = value
    assert subject._failure_coordinate(**arguments) == expected


def test_controller_discards_streams_and_has_one_popen_site() -> None:
    source = inspect.getsource(subject.execute_boot)
    assert source.count("subprocess.Popen(") == 1
    assert "stdout=subprocess.DEVNULL" in source
    assert "stderr=subprocess.DEVNULL" in source
    assert ".stdout.read" not in source
    assert ".stderr.read" not in source


def test_controller_assembles_terminal_only_after_process_termination() -> None:
    source = inspect.getsource(subject.execute_boot)
    terminate = source.index("_terminate_process(process)")
    assemble = source.index("rebinding.assemble_controller_terminal(")
    cleanup = source.index("shutil.rmtree(root)")
    publish = source.index("_write_exclusive(EVIDENCE_PATH")
    assert terminate < assemble < cleanup < publish


def test_canonical_bundle_roster_excludes_execution_guard_and_sentinel() -> None:
    assert set(base_bundle.PATH_ROSTER) == {
        "runner/synthetic-one-request-worker-runner.mjs",
        "runner/post-hmr-pre-request-diagnostic.mjs",
        "control/future-attempt-bundle.json",
        "control/post-hmr-diagnostic.json",
        "control/broker-request-reading.json",
        "control/controller-terminal.json",
    }
    assert all("guard" not in path and "sentinel" not in path for path in base_bundle.PATH_ROSTER)


def test_no_product_or_data_authority_enters_the_contract() -> None:
    payload = subject.CONTRACT_PATH.read_text(encoding="utf-8").lower()
    for forbidden in (
        "patient_id",
        "appointment_id",
        "clinical",
        "production_runtime",
        "ordinary_practice_enablement",
    ):
        assert forbidden not in payload
