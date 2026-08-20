from __future__ import annotations

import inspect
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from scripts import (
    raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal
    as subject,
)


def _candidate_paths() -> tuple[Path, Path, Path, Path, Path]:
    root = Path("C:/emr4-preset-mount-test").resolve()
    proof = root / "installation" / "proof"
    return (
        root,
        root / "events.jsonl",
        root / "runner-terminal.json",
        proof / "sentinel.mjs",
        proof / "runner.mjs",
    )


def test_contract_is_exact_and_provider_free() -> None:
    contract = subject.load_contract()
    assert contract["profile"]["include_user_root"] is True
    assert contract["profile"]["effective_roots"] == [
        {"role": "shipped", "trust": "system"},
        {"role": "derived_user", "trust": "user"},
    ]
    assert contract["guard"]["expected_tools"] == ["edit", "glob", "read"]
    assert contract["native"]["process_limit"] == 1
    assert contract["native"]["automatic_retry_limit"] == 0


def test_predecessors_and_generated_guard_remain_exact() -> None:
    projection = subject.bind_predecessors(subject.load_contract())
    assert len(projection["files"]) == 6
    assert projection["guard"]["sha256"] == subject.load_contract()["guard"][
        "generated_sha256"
    ]
    assert projection["service_root_transformation"]["corrected_include_user_root"]
    assert projection["preset_bytes"] == 158


def test_patch_pair_adds_only_user_root_service_and_reviewed_runner() -> None:
    initial, changed = subject.build_patch_pair(*_candidate_paths())
    projection = subject.validate_patch_pair(changed=changed, initial=initial, root=_candidate_paths()[0])
    assert projection["include_user_root"] is True
    assert projection["runner_inject"] == ["hmr", "agentPresets", "tools"]
    assert projection["inserted_ids"] == [
        "agent-presets",
        "provider-free-effective-tool-hmr-sentinel",
        "provider-free-effective-tool-proof-runner",
    ]


def test_patch_pair_rejects_disabled_user_root() -> None:
    initial, changed = subject.build_patch_pair(*_candidate_paths())
    value = yaml.safe_load(changed)
    insertion = next(row["insert"] for row in value if "insert" in row)
    insertion[0]["config"]["includeUserRoot"] = False
    mutated = yaml.safe_dump(value, sort_keys=False).encode()
    with pytest.raises(subject.PresetMountProjectionError, match="user_root_not_enabled"):
        subject.validate_patch_pair(initial, mutated, _candidate_paths()[0])


def test_runner_is_one_scope_one_guard_no_agent_or_model() -> None:
    projection = subject.validate_runner_source(subject.runner_source())
    assert projection["one_scope"]
    assert projection["one_guard_call"]
    assert projection["one_terminal"]
    assert projection["one_dispose"]
    assert projection["post_root_failure_classification"]
    assert projection["no_agents_create"]
    assert projection["no_session_or_turn"]
    assert projection["no_broker_or_provider"]


def test_event_parser_accepts_exact_prefix_and_sequence(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    rows = [
        {
            "schema_version": subject.EVENT_SCHEMA,
            "sequence": index,
            "event": event,
        }
        for index, event in enumerate(subject.EXPECTED_EVENTS[:4], start=1)
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    assert [row["event"] for row in subject.parse_events(path, allow_incomplete=True)] == subject.EXPECTED_EVENTS[:4]


def test_event_parser_rejects_reordered_prefix(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    rows = [
        {"schema_version": subject.EVENT_SCHEMA, "sequence": 1, "event": subject.EXPECTED_EVENTS[1]},
    ]
    path.write_text(json.dumps(rows[0]) + "\n", encoding="utf-8")
    with pytest.raises(subject.PresetMountProjectionError, match="event_prefix_mismatch"):
        subject.parse_events(path, allow_incomplete=True)


def test_runner_terminal_accepts_only_safe_exact_projection(tmp_path: Path) -> None:
    path = tmp_path / "terminal.json"
    value = {
        "schema_version": subject.RUNNER_TERMINAL_SCHEMA,
        "stage": "pre_provider_tool_composition",
        "code": subject.SUCCESS_CODE,
        "detail": None,
        "effective_tool_names": subject.EXPECTED_TOOLS,
        "effective_tool_count": 3,
    }
    path.write_text(json.dumps(value), encoding="utf-8")
    assert subject.parse_runner_terminal(path) == value


def test_runner_terminal_rejects_unsafe_detail(tmp_path: Path) -> None:
    path = tmp_path / "terminal.json"
    value = {
        "schema_version": subject.RUNNER_TERMINAL_SCHEMA,
        "stage": "pre_provider_tool_composition",
        "code": "EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED",
        "detail": "C:/secret",
        "effective_tool_names": [],
        "effective_tool_count": 0,
    }
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(subject.PresetMountProjectionError, match="runner_terminal_detail_invalid"):
        subject.parse_runner_terminal(path)


def test_deterministic_evidence_passes_without_native_process() -> None:
    evidence = subject.deterministic_evidence()
    assert evidence["result"] == "pass"
    assert evidence["root_fixture"]["scenario_count"] == 5
    assert evidence["guard_fixture"]["scenario_count"] == 13
    assert evidence["candidate"]["native_process_checkpoint_admitted"] is False
    assert evidence["process_boundary"]["native_harness_processes"] == 0
    assert all(
        evidence["process_boundary"][name] == 0
        for name in (
            "agent_sessions",
            "turns",
            "broker_requests",
            "model_requests",
            "provider_requests",
            "network_attempts",
            "occupied_workers",
            "docker_invocations",
            "database_invocations",
        )
    )


def test_deterministic_schema_rejects_broadened_projection() -> None:
    evidence = subject.deterministic_evidence()
    evidence["unexpected"] = True
    schema = json.loads(subject.DETERMINISTIC_SCHEMA_PATH.read_text(encoding="utf-8"))
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(evidence)


def test_deterministic_schema_rejects_nonzero_provider_boundary() -> None:
    evidence = subject.deterministic_evidence()
    evidence["process_boundary"]["provider_requests"] = 1
    schema = json.loads(subject.DETERMINISTIC_SCHEMA_PATH.read_text(encoding="utf-8"))
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(evidence)


def test_native_schema_rejects_boundary_and_cleanup_broadening() -> None:
    schema = json.loads(subject.NATIVE_SCHEMA_PATH.read_text(encoding="utf-8"))
    provider = schema["properties"]["provider_boundary"]
    cleanup = schema["properties"]["cleanup"]
    assert provider["additionalProperties"] is False
    assert provider["properties"]["agent_session_count"]["const"] == 0
    assert provider["properties"]["provider_request_count"]["const"] == 0
    assert cleanup["additionalProperties"] is False
    assert cleanup["properties"]["raw_logs_retained"]["type"] == "boolean"
    assert cleanup["properties"]["raw_environment_retained"]["const"] is False
    assert (
        schema["allOf"][0]["then"]["properties"]["cleanup"]["properties"]
        ["raw_logs_retained"]["const"]
        is False
    )


def test_accepted_package_tree_materialises_before_proof_without_npm() -> None:
    source = inspect.getsource(subject.execute_native)
    assert source.index("package_root, _ = materialize_accepted_node_modules") < source.index(
        "proof.mkdir(parents=True)"
    )
    assert "NATIVE_PRELAUNCH_ACCEPTED_MATERIALIZATION_FAILED" in source
    assert "_offline_install" not in source


def test_attempt_003_uses_fresh_exclusive_lifecycle_paths() -> None:
    assert subject.NATIVE_ATTEMPT_ID == "check-in-preset-mount-effective-tool-native-003"
    assert subject.NATIVE_CHECKPOINT_PATH.name.endswith("attempt-003.json")
    assert subject.NATIVE_CONSUMED_PATH.name.endswith("attempt-003.json")
    assert subject.NATIVE_TERMINAL_PATH.name.endswith("attempt-003.json")
    assert subject.NATIVE_REPORT_PATH.name.endswith("attempt-003.md")


def test_materialization_source_is_exact_and_uses_no_process() -> None:
    projection = subject.validate_materialization_source(subject.load_contract())
    assert projection["materialization_process_count"] == 0
    assert projection["validated_packages"] == {
        "@deepseek-ai/dsh": "0.1.0-rc.7",
        "@deepseek-ai/dsh-tools": "0.1.0-rc.7",
        "@deepseek-ai/dsh-agent-presets": "0.1.0-rc.7",
        "@deepseek-ai/dsh-scope": "0.1.0-rc.7",
        "@deepseek-ai/dsh-tool-fs": "0.1.0-rc.7",
        "@deepseek-ai/dsh-tool-fs-search": "0.1.0-rc.7",
    }


def test_accepted_package_tree_materialization_fixture() -> None:
    fixture = subject.run_materialization_fixture()
    assert fixture == {
        "result": "pass",
        "materialization_process_count": 0,
        "critical_package_count": 6,
        "copied_package_root_observed": True,
        "disposable_root_absent": True,
    }


def test_cleanup_is_bounded_and_preserves_failure_terminal_path() -> None:
    source = inspect.getsource(subject.execute_native)
    assert "for _cleanup_attempt in range(26)" in source
    assert 'failure = "NATIVE_CLEANUP_FAILED"' in source
    assert '"raw_logs_retained": not root_absent' in source


def test_native_schema_admits_zero_process_prelaunch_failure_but_not_zero_process_pass() -> None:
    schema = json.loads(subject.NATIVE_SCHEMA_PATH.read_text(encoding="utf-8"))
    terminal = {
        "schema_version": subject.NATIVE_TERMINAL_SCHEMA,
        "operation_id": subject.OPERATION_ID,
        "attempt_id": subject.NATIVE_ATTEMPT_ID,
        "result": "failed_closed",
        "terminal_code": "NATIVE_PRELAUNCH_OFFLINE_INSTALL_FAILED",
        "events": [],
        "effective_tool_names": [],
        "effective_tool_count": 0,
        "native_process_count": 0,
        "automatic_retry_count": 0,
        "provider_boundary": {
            "credential_environment_names_removed_count": 0,
            "agent_session_count": 0,
            "turn_count": 0,
            "broker_request_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_attempt_count": 0,
            "occupied_worker_count": 0,
            "docker_invocation_count": 0,
            "database_invocation_count": 0,
        },
        "cleanup": {
            "process_absent": True,
            "disposable_root_absent": True,
            "raw_logs_retained": False,
            "raw_environment_retained": False,
            "stdout_bytes": 0,
            "stderr_bytes": 0,
            "stdout_sha256": "0" * 64,
            "stderr_sha256": "0" * 64,
        },
    }
    validator = jsonschema.Draft202012Validator(schema)
    validator.validate(terminal)
    terminal["result"] = "pass"
    terminal["terminal_code"] = subject.SUCCESS_CODE
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(terminal)


def test_missing_checkpoint_fails_before_native_consumption(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(subject, "NATIVE_CHECKPOINT_PATH", tmp_path / "missing.json")
    monkeypatch.setattr(subject, "NATIVE_CONSUMED_PATH", tmp_path / "consumed.json")
    monkeypatch.setattr(subject, "NATIVE_TERMINAL_PATH", tmp_path / "terminal.json")
    with pytest.raises(FileNotFoundError):
        subject.execute_native()
    assert not (tmp_path / "consumed.json").exists()
    assert not (tmp_path / "terminal.json").exists()


def test_attempt_003_terminal_is_consumed_exact_and_clean() -> None:
    assert subject.NATIVE_CHECKPOINT_PATH.is_file()
    assert subject.NATIVE_CONSUMED_PATH.is_file()
    assert subject.NATIVE_TERMINAL_PATH.is_file()
    assert subject.NATIVE_REPORT_PATH.is_file()
    consumed = json.loads(subject.NATIVE_CONSUMED_PATH.read_text(encoding="utf-8"))
    terminal = json.loads(subject.NATIVE_TERMINAL_PATH.read_text(encoding="utf-8"))
    assert consumed["state"] == "consumed"
    assert consumed["resume_permitted"] is False
    assert consumed["automatic_retry_count"] == 0
    assert terminal["result"] == "pass"
    assert terminal["terminal_code"] == subject.SUCCESS_CODE
    assert terminal["events"] == subject.EXPECTED_EVENTS
    assert terminal["effective_tool_names"] == subject.EXPECTED_TOOLS
    assert terminal["native_process_count"] == 1
    assert terminal["automatic_retry_count"] == 0
    assert terminal["cleanup"]["process_absent"] is True
    assert terminal["cleanup"]["disposable_root_absent"] is True
    assert terminal["cleanup"]["raw_logs_retained"] is False
    jsonschema.Draft202012Validator(
        json.loads(subject.NATIVE_SCHEMA_PATH.read_text(encoding="utf-8"))
    ).validate(terminal)
