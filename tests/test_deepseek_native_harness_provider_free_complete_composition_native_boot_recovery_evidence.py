from __future__ import annotations

import json

import jsonschema

from scripts.deepseek_native_harness_provider_free_complete_composition_native_boot_recovery import (
    ATTEMPT_ID,
    CONTRACT_PATH,
    EVIDENCE_PATH,
)


def _evidence() -> dict[str, object]:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def test_canonical_evidence_validates_against_the_frozen_schema() -> None:
    evidence = _evidence()
    schema = json.loads(
        CONTRACT_PATH.with_name("evidence.schema.json").read_text(encoding="utf-8")
    )

    jsonschema.validate(evidence, schema)
    assert evidence["attempt_id"] == ATTEMPT_ID
    assert evidence["result"] == "pass"
    assert evidence["failure_classification"] is None


def test_sole_process_reached_exact_readiness_activation_and_terminal() -> None:
    evidence = _evidence()

    assert evidence["readiness"] == {
        "events": ["sentinel_activated", "stock_headless_hmr_ready"],
        "exact_expected_order": True,
        "ledger_valid": True,
        "writer": "provider-free-effective-tool-hmr-sentinel",
    }
    assert evidence["activation"]["coordinates"] == [
        "BOOTSTRAP_APPLY_ENTERED",
        "RUNTIME_MODULES_IMPORTED",
        "SCOPE_CREATED",
        "GUARD_ENTRY_REACHED",
        "GUARD_TERMINAL_REACHED",
        "SCOPE_DISPOSED",
        "EXIT_REQUESTED",
    ]
    assert evidence["activation"]["exact_success_order"] is True
    assert evidence["terminal"] == {
        "schema_version": "ariadne.deepseek_native_harness_effective_tool_native_boot_terminal.v1",
        "stage": "preterminal_activation",
        "code": "EFFECTIVE_TOOL_COMPOSITION_PASSED",
        "detail": None,
        "effective_tool_names": ["edit", "glob", "read"],
        "effective_tool_count": 3,
    }


def test_required_services_and_exact_accepted_payload_are_retained() -> None:
    evidence = _evidence()

    assert evidence["source_contract"]["required_services"] == [
        "hmr",
        "agentPresets",
        "tools",
    ]
    assert evidence["source_contract"]["service_dependency_gate"] == (
        "cordis_inactive_until_all_declared_services_active"
    )
    assert evidence["composition"]["preset_sha256"] == (
        "3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1"
    )
    assert evidence["composition"]["runner_sha256"] == (
        "d199c9aa8361a30a2f3f7de3a228ab93d962904dd2e9291c3d1c30666ca72367"
    )
    assert evidence["composition"]["effective_tool_guard_sha256"] == (
        "6678ed31bdcd30a5018689b72ad509c182854bf5d63862f59b397acc8de40894"
    )


def test_provider_boundary_process_accounting_and_cleanup_are_closed() -> None:
    evidence = _evidence()
    boundary = evidence["provider_boundary"]

    for key in (
        "network_attempt_count",
        "agent_session_count",
        "turn_count",
        "broker_request_count",
        "model_request_count",
        "provider_request_count",
        "occupied_worker_count",
        "docker_invocation_count",
        "database_invocation_count",
    ):
        assert boundary[key] == 0
    assert evidence["launch"]["native_process_count"] == 1
    assert evidence["launch"]["retry_count"] == 0
    assert evidence["launch"]["exit_code"] == 0
    assert evidence["launch"]["duration_ms"] >= 0
    assert evidence["cleanup"] == {
        "process_wait_completed": True,
        "process_absent": True,
        "disposable_root_absent": True,
        "raw_environment_retained": False,
        "raw_logs_retained": False,
        "npm_cache_retained_by_boot": False,
    }
