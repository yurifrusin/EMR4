from __future__ import annotations

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


def test_no_native_canonical_outputs_exist_before_checkpoint() -> None:
    assert not subject.NATIVE_CHECKPOINT_PATH.exists()
    assert not subject.NATIVE_CONSUMED_PATH.exists()
    assert not subject.NATIVE_TERMINAL_PATH.exists()
    assert not subject.NATIVE_REPORT_PATH.exists()
