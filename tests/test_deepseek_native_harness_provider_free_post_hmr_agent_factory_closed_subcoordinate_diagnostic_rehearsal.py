from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_post_hmr_agent_factory_closed_subcoordinate_diagnostic_rehearsal as subject,
)


def _contract() -> dict:
    return subject.load_contract()


def _sidecar(contract: dict, *, result: str = "prepublication_veto_diagnosed") -> dict:
    success = result == "prepublication_veto_diagnosed"
    return {
        "schema_version": subject.SIDECAR_SCHEMA,
        "operation_id": subject.OPERATION_ID,
        "execution_attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "candidate_source": "a" * 40,
        "result": result,
        "last_admitted_stage": (
            "postrollback_registries_empty" if success else "loader_ready"
        ),
        "error_class": None if success else "package_import_rejected",
        "runner_sha256": contract["source_bindings"]["diagnostic_runner_sha256"],
        "effective_tool_guard_sha256": contract["source_bindings"][
            "effective_tool_guard_sha256"
        ],
        "preset_sha256": contract["preset"]["sha256"],
        "fixed_identity_sha256": subject.sha256_bytes(
            subject.PRIVATE_SESSION_ID.encode()
        ),
        "target_path_sha256": subject.sha256_bytes(subject.TARGET_PATH.encode()),
        "agent_create_invocation_count": 1 if success else 0,
        "private_agent_preparation_count": 1 if success else 0,
        "private_session_preparation_count": 1 if success else 0,
        "live_agent_count": 0,
        "live_session_count": 0,
        "session_created_event_count": 0,
        "agent_created_event_count": 0,
        "agent_session_start_event_count": 0,
        "preset_mounted": success,
        "model_selection_installed": success,
        "veto_exact": success,
        "veto_rejected": success,
        "raw_error_retained": False,
        "target_created": False,
        "target_used": False,
        "turn_count": 0,
        "request_count": 0,
        "broker_process_count": 0,
        "broker_request_count": 0,
        "occupied_worker_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "database_invocation_count": 0,
        "docker_invocation_count": 0,
    }


def test_contract_freezes_exact_closed_vocabulary_and_one_process() -> None:
    contract = _contract()
    assert contract["closed_vocabulary"] == {
        "stages": subject.STAGES,
        "error_classes": subject.ERROR_CLASSES,
        "terminals": subject.TERMINALS,
    }
    assert contract["execution_attempt"] == {
        "attempt_id": subject.EXECUTION_ATTEMPT_ID,
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }


def test_runner_static_imports_only_node_builtins_and_dynamically_imports_packages() -> None:
    source = subject.runner_source().decode()
    result = subject.validate_runner_source(source.encode())
    assert all(result["checks"].values())
    assert 'from "@deepseek-ai/' not in source
    assert 'from "./effective-tool-guard.mjs"' not in source
    assert source.index('let lastStage = "runner_apply_entered"') < source.index(
        'await import("@deepseek-ai/dsh-agent")'
    )


def test_runner_has_one_factory_call_and_two_exclusive_terminal_paths() -> None:
    source = subject.runner_source().decode()
    assert source.count("await agents.create({") == 1
    assert source.count('openSync(path, "wx")') == 1
    assert source.count('emit("prepublication_veto_diagnosed", null)') == 1
    assert (
        source.count(
            'emit("closed_subcoordinate_failure", classify(error, lastStage))'
        )
        == 1
    )
    assert "runner_link_or_apply_absence" not in source


def test_sidecar_schema_is_closed_and_finite() -> None:
    schema = json.loads(subject.SIDECAR_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["last_admitted_stage"]["enum"] == subject.STAGES
    assert schema["properties"]["error_class"]["enum"] == [
        None,
        *subject.ERROR_CLASSES,
    ]


@pytest.mark.parametrize(
    "result",
    ["prepublication_veto_diagnosed", "closed_subcoordinate_failure"],
)
def test_read_sidecar_accepts_both_runner_terminals(tmp_path: Path, result: str) -> None:
    contract = _contract()
    root = tmp_path.resolve()
    sidecar = root / "control" / "post-hmr-diagnostic.json"
    sidecar.parent.mkdir()
    sidecar.write_text(json.dumps(_sidecar(contract, result=result)) + "\n")
    observed = subject.read_sidecar(
        sidecar,
        disposable_root=root,
        contract=contract,
        candidate_source="a" * 40,
    )
    assert observed["result"] == result


def test_sidecar_factory_count_must_match_last_stage(tmp_path: Path) -> None:
    contract = _contract()
    value = _sidecar(contract, result="closed_subcoordinate_failure")
    value["agent_create_invocation_count"] = 1
    sidecar = tmp_path / "post-hmr-diagnostic.json"
    sidecar.write_text(json.dumps(value) + "\n")
    with pytest.raises(subject.ClosedSubcoordinateError, match="stage_mismatch"):
        subject.read_sidecar(
            sidecar,
            disposable_root=tmp_path.resolve(),
            contract=contract,
            candidate_source="a" * 40,
        )


def test_controller_link_absence_has_no_projected_factory_counts() -> None:
    terminal = subject.build_controller_terminal(None)
    assert terminal == {
        "result": "runner_link_or_apply_absence",
        "last_admitted_stage": None,
        "error_class": None,
        "factory_boundary": None,
        "raw_runtime_detail_retained": False,
    }


@pytest.mark.parametrize(
    ("terminal_result", "exit_code"),
    [
        ("prepublication_veto_diagnosed", 0),
        ("closed_subcoordinate_failure", 2),
        ("runner_link_or_apply_absence", 2),
    ],
)
def test_controller_accepts_only_terminal_specific_exit_code(
    terminal_result: str, exit_code: int
) -> None:
    terminal = {
        "result": terminal_result,
        "last_admitted_stage": None,
        "error_class": None,
        "factory_boundary": None,
        "raw_runtime_detail_retained": False,
    }
    assert (
        subject._controller_failure(
            process_started=True,
            exit_code=exit_code,
            readiness_valid=True,
            readiness_events=["sentinel_activated", "stock_headless_hmr_ready"],
            hmr_mutation_count=1,
            sidecar_file_seen=terminal_result != "runner_link_or_apply_absence",
            sidecar_valid=terminal_result != "runner_link_or_apply_absence",
            terminal=terminal,
            broker_zero=True,
            network_attempt_count=0,
            network_ledger_valid=True,
            bundle_unchanged=True,
            target_absent=True,
            process_absent=True,
            root_absent=True,
        )
        is None
    )


def test_invalid_seen_sidecar_is_not_downgraded_to_link_absence() -> None:
    failure = subject._controller_failure(
        process_started=True,
        exit_code=2,
        readiness_valid=True,
        readiness_events=["sentinel_activated", "stock_headless_hmr_ready"],
        hmr_mutation_count=1,
        sidecar_file_seen=True,
        sidecar_valid=False,
        terminal=subject.build_controller_terminal(None),
        broker_zero=True,
        network_attempt_count=0,
        network_ledger_valid=True,
        bundle_unchanged=True,
        target_absent=True,
        process_absent=True,
        root_absent=True,
    )
    assert failure == "TYPED_SIDECAR_REJECTED"


def test_patch_adds_only_sentinel_presets_and_diagnostic_runner(tmp_path: Path) -> None:
    contract = _contract()
    profile = tmp_path / "home" / "profiles" / "headless"
    initial, changed = subject.build_patch_pair(
        profile_dir=profile,
        readiness_path=tmp_path / "readiness.jsonl",
        sidecar_path=tmp_path / "bundle" / "control" / "post-hmr-diagnostic.json",
        shipped_root=tmp_path / "installation" / "shipped",
        user_root=tmp_path / "home" / ".agent-presets",
        preset_path=tmp_path / "home" / ".agent-presets" / subject.PRESET_ID / "agent.cordis.yml",
        candidate_source="b" * 40,
        source_bindings=contract["source_bindings"],
    )
    _, initial_inserted = subject._patch_rows(initial)
    _, changed_inserted = subject._patch_rows(changed)
    assert [row["id"] for row in initial_inserted] == [
        "provider-free-rebound-hmr-sentinel",
        "agent-presets",
    ]
    assert [row["id"] for row in changed_inserted] == [
        "provider-free-rebound-hmr-sentinel",
        "agent-presets",
        "provider-free-agent-factory-closed-subcoordinate-runner",
    ]


def test_deterministic_check_creates_no_native_process() -> None:
    result = subject.deterministic_check()
    assert result["native_process_count"] == 0
    assert result["verified_cached_package_count"] == 4
    assert result["package_seed"]["lock_package_count"] == 588
    assert result["package_seed"]["tree_sha256"] == (
        "d84e73067c8dbbf4836969eb948012fd364ee454bb07744cfe486995a256084d"
    )
