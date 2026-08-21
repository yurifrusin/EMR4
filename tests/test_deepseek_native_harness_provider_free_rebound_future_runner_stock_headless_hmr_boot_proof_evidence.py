from __future__ import annotations

import json
from pathlib import Path
import subprocess

import jsonschema


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-rebound-future-runner-stock-headless-hmr-boot-proof"
)
CONTRACT = json.loads((OPERATION_ROOT / "contract.json").read_bytes())
EVIDENCE = json.loads((OPERATION_ROOT / "native-boot-evidence.json").read_bytes())
EFFICACY = json.loads((OPERATION_ROOT / "efficacy-reading.json").read_bytes())
REPORT = (OPERATION_ROOT / "native-boot-report.md").read_text(encoding="utf-8")
EXECUTION_SOURCE = "560f471b72bef0b9790120238657dc7afd4d602b"


def test_native_boot_evidence_is_strict_and_bound_to_execution_source() -> None:
    schema = json.loads((OPERATION_ROOT / "evidence.schema.json").read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(EVIDENCE)
    assert EVIDENCE["candidate_source"] == EXECUTION_SOURCE
    assert (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", EXECUTION_SOURCE, "HEAD"],
            cwd=REPO_ROOT,
            check=False,
        ).returncode
        == 0
    )
    assert EVIDENCE["result"] == "pass"
    assert EVIDENCE["failure_classification"] is None


def test_controller_terminal_exactly_matches_the_frozen_contract() -> None:
    terminal = EVIDENCE["controller_terminal"]
    assert all(
        terminal[key] == value
        for key, value in CONTRACT["expected_terminal"].items()
    )
    assert terminal["occupied_launch_authorized"] is False
    assert terminal["raw_error_retained"] is False
    assert terminal["raw_stream_read"] is False
    assert terminal["source_bindings"] == {
        key: CONTRACT["source_bindings"][key]
        for key in (
            "future_runner_sha256",
            "generated_helper_sha256",
            "controller_module_sha256",
        )
    }
    assert terminal["target_binding"] == CONTRACT["target_binding"]


def test_one_process_one_hmr_mutation_and_every_prohibited_count_is_zero() -> None:
    assert EVIDENCE["launch"]["native_process_count"] == 1
    assert EVIDENCE["launch"]["hmr_mutation_count"] == 1
    assert EVIDENCE["launch"]["retry_count"] == 0
    assert EVIDENCE["launch"]["resume_count"] == 0
    assert EVIDENCE["readiness"] == {
        "events": CONTRACT["readiness"]["events"],
        "valid": True,
        "exact_expected_order": True,
    }
    assert all(
        EVIDENCE["provider_boundary"][key] == 0
        for key in (
            "agent_create_count",
            "session_count",
            "turn_count",
            "broker_process_count",
            "broker_request_count",
            "worker_count",
            "model_request_count",
            "provider_request_count",
            "database_invocation_count",
            "docker_invocation_count",
            "network_attempt_count",
        )
    )
    assert all(
        EVIDENCE["broker_reading"][key] == 0
        for key in (
            "request_count",
            "request_rejected",
            "provider_call_started",
            "provider_call_completed",
            "provider_call_failed",
        )
    )


def test_package_seed_copy_bundle_target_and_cleanup_are_exact() -> None:
    materialisation = EVIDENCE["package"]["offline_install"]
    assert materialisation["process_count"] == 0
    assert materialisation["retry_count"] == 0
    assert materialisation["strategy"] == "verified_installed_tree_seed_copy"
    assert materialisation["seed"]["tree_sha256"] == CONTRACT["materialisation"][
        "tree_sha256"
    ]
    assert materialisation["copy"] == {
        key: materialisation["seed"][key]
        for key in (
            "tree_sha256",
            "file_count",
            "byte_count",
            "reparse_point_count",
        )
    }
    assert EVIDENCE["composition"]["runner_copy_equal"] is True
    assert EVIDENCE["composition"]["helper_copy_equal"] is True
    assert EVIDENCE["composition"]["bundle_manifest_unchanged"] is True
    assert EVIDENCE["composition"]["runner_fallback_terminal_absent"] is True
    assert EVIDENCE["target"] == {
        "file_created": False,
        "used": False,
        "absent_after_process": True,
    }
    assert EVIDENCE["cleanup"]["process_absent"] is True
    assert EVIDENCE["cleanup"]["disposable_root_absent"] is True


def test_report_and_efficacy_keep_the_claim_boundary_closed() -> None:
    assert "Result: **pass**" in REPORT
    assert f"Full execution source: `{EXECUTION_SOURCE}`" in REPORT
    assert "not an occupied DeepSeek worker" in REPORT
    assert EFFICACY == {
        "control_gain": "exact_rebound_runner_native_activation_is_machine_joined_to_typed_pre_request_and_broker_zero_evidence",
        "deepseek_worker_request_count": 0,
        "free_form_finite_control_fields": 0,
        "model_request_count": 0,
        "native_process_count": 1,
        "next_gate": "one_bounded_provider_free_deepseek_worker_attempt_only_if_separately_frozen",
        "operation_id": CONTRACT["operation_id"],
        "provider_request_count": 0,
        "result": "pass",
        "retry_count": 0,
        "schema_version": "ariadne.native_harness_rebound_stock_headless_hmr_boot_efficacy.v1",
    }
