from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import jsonschema
import pytest

from orchestration_harness import native_startup_terminal as terminal
from scripts import (
    deepseek_native_harness_provider_free_pre_hmr_startup_terminal_recovery
    as recovery,
)
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as controller,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-pre-hmr-startup-failure-"
    "classification-and-terminalization-recovery"
)
ATTEMPT_ID = "synthetic-attempt-003"
CANDIDATE_SOURCE = "1" * 40
EMPTY_DIGEST = hashlib.sha256(b"").hexdigest()


def reading(payload: bytes) -> dict[str, object]:
    return {
        "byte_count": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "classification_bytes": payload[: terminal.MAX_CLASSIFICATION_BYTES],
        "limit_exceeded": len(payload) > terminal.MAX_CLASSIFICATION_BYTES,
    }


def build(
    *,
    stdout: bytes = b"",
    stderr: bytes = b"unknown startup failure",
    started: bool = True,
    exit_code: int | None = 1,
    coordinate: str = "native_process_exited_nonzero",
    hmr_events: tuple[str, ...] = (),
) -> dict[str, object]:
    return terminal.build_pre_hmr_terminal(
        operation_id=OPERATION_ID,
        attempt_id=ATTEMPT_ID,
        candidate_source=CANDIDATE_SOURCE,
        native_process_started=started,
        exit_code=exit_code,
        controller_coordinate=coordinate,
        hmr_events=hmr_events,
        stdout=reading(stdout),
        stderr=reading(stderr),
    )


@pytest.mark.parametrize(
    ("cause", "signature"),
    [
        (cause, signature)
        for cause, signatures in terminal.SIGNATURE_GROUPS.items()
        for signature in signatures
    ],
)
def test_each_fixed_signature_group_is_classified_case_insensitively(
    cause: str, signature: bytes
) -> None:
    value = build(stderr=b"prefix " + signature.upper() + b" suffix")
    assert value["cause"] == cause
    assert value["matched_signature_groups"] == [cause]


def test_duplicate_signatures_in_one_group_do_not_create_ambiguity() -> None:
    value = build(stderr=b"ERR_MODULE_NOT_FOUND then Cannot Find Module")
    assert value["cause"] == "module_resolution_failed"
    assert value["matched_signature_groups"] == ["module_resolution_failed"]


def test_cross_group_signatures_fail_closed_as_ambiguous() -> None:
    value = build(
        stdout=b"ERR_MODULE_NOT_FOUND",
        stderr=b"profile validation failed",
    )
    assert value["cause"] == "ambiguous_startup_signatures"
    assert value["matched_signature_groups"] == [
        "module_resolution_failed",
        "profile_load_or_validation_failed",
    ]


def test_unknown_bytes_remain_unclassified() -> None:
    value = build(stderr=b"opaque nonzero exit")
    assert value["cause"] == "unclassified_nonzero_exit"
    assert value["matched_signature_groups"] == []


def test_process_creation_and_controller_coordinates_do_not_use_text() -> None:
    creation = build(
        stderr=b"",
        started=False,
        exit_code=None,
        coordinate="native_process_creation_failed",
    )
    controller = build(
        stderr=b"ERR_MODULE_NOT_FOUND",
        exit_code=None,
        coordinate="unexpected_controller_failure",
    )
    timeout = build(
        stderr=b"opaque timeout",
        exit_code=None,
        coordinate="native_worker_timeout",
    )
    assert creation["stage"] == "native_process_creation"
    assert creation["cause"] == "operating_system_process_failure"
    assert controller["cause"] == "controller_startup_exception"
    assert controller["matched_signature_groups"] == []
    assert timeout["cause"] == "hmr_bootstrap_failed"
    assert timeout["matched_signature_groups"] == []


def test_stream_limit_is_dominant_and_never_classifies_truncated_text() -> None:
    payload = b"ERR_MODULE_NOT_FOUND" + b"x" * terminal.MAX_CLASSIFICATION_BYTES
    value = build(stderr=payload)
    assert value["cause"] == "startup_stream_limit_exceeded"
    assert value["matched_signature_groups"] == []
    assert value["stderr"]["byte_count"] == len(payload)


def test_incremental_reader_hashes_all_bytes_and_retains_only_bounded_prefix(
    tmp_path: Path,
) -> None:
    boundary = b"a" * terminal.MAX_CLASSIFICATION_BYTES
    boundary_path = tmp_path / "boundary.raw"
    boundary_path.write_bytes(boundary)
    boundary_reading = terminal.read_startup_stream(boundary_path)
    assert boundary_reading == reading(boundary)

    oversized = boundary + b"tail"
    oversized_path = tmp_path / "oversized.raw"
    oversized_path.write_bytes(oversized)
    oversized_reading = terminal.read_startup_stream(oversized_path)
    assert oversized_reading == reading(oversized)
    assert oversized_reading["classification_bytes"] == boundary


def test_binary_and_secret_shaped_bytes_never_enter_terminal_payload() -> None:
    secret = b"DEEPSEEK_API_KEY=sk-hostile-secret-123\xff\xfe"
    value = build(stderr=secret)
    payload = terminal.terminal_bytes(value)
    assert b"sk-hostile-secret" not in payload
    assert b"DEEPSEEK_API_KEY" not in payload
    assert value["stderr"]["sha256"] == hashlib.sha256(secret).hexdigest()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"hmr_events": ("sentinel_activated",)},
        {"exit_code": 0},
        {"exit_code": True},
        {"exit_code": "1"},
        {"coordinate": "unknown_coordinate"},
        {
            "started": False,
            "exit_code": None,
            "coordinate": "native_process_creation_failed",
            "stderr": b"not empty",
        },
    ],
)
def test_out_of_scope_or_inconsistent_facts_are_rejected(
    kwargs: dict[str, object]
) -> None:
    with pytest.raises(terminal.StartupTerminalError):
        build(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", "wrong"),
        ("cause", "operating_system_process_failure"),
        ("controller_coordinate", "native_process_creation_failed"),
        ("hmr_event_count", 1),
        ("raw_streams_retained", True),
        ("classification_byte_limit_per_stream", 1),
    ],
)
def test_hostile_terminal_mutations_fail_validation(field: str, value: object) -> None:
    mutated = build()
    mutated[field] = value
    with pytest.raises(terminal.StartupTerminalError):
        terminal.validate_pre_hmr_terminal(mutated)


def test_exact_keys_and_relationships_are_validated() -> None:
    value = build(stderr=b"ERR_MODULE_NOT_FOUND")
    extra = dict(value)
    extra["raw_stderr"] = "forbidden"
    with pytest.raises(terminal.StartupTerminalError, match="terminal_keys_invalid"):
        terminal.validate_pre_hmr_terminal(extra)

    mismatched = dict(value)
    mismatched["matched_signature_groups"] = []
    with pytest.raises(terminal.StartupTerminalError):
        terminal.validate_pre_hmr_terminal(mismatched)


def test_exclusive_write_readback_and_stale_second_writer(
    tmp_path: Path,
) -> None:
    evidence_root = (tmp_path / "evidence").resolve()
    disposable_root = (tmp_path / "disposable").resolve()
    evidence_root.mkdir()
    disposable_root.mkdir()
    path = evidence_root / "pre-hmr-terminal.json"
    value = build(stderr=b"ERR_MODULE_NOT_FOUND")

    digest = terminal.write_pre_hmr_terminal_exclusive(
        path=path,
        terminal=value,
        evidence_root=evidence_root,
        disposable_root=disposable_root,
    )
    assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
    assert json.loads(path.read_bytes()) == value
    with pytest.raises(terminal.StartupTerminalError):
        terminal.write_pre_hmr_terminal_exclusive(
            path=path,
            terminal=value,
            evidence_root=evidence_root,
            disposable_root=disposable_root,
        )


def test_writer_rejects_escape_and_disposable_root_output(tmp_path: Path) -> None:
    evidence_root = (tmp_path / "evidence").resolve()
    disposable_root = (evidence_root / "disposable").resolve()
    evidence_root.mkdir()
    disposable_root.mkdir()
    value = build()
    with pytest.raises(terminal.StartupTerminalError):
        terminal.write_pre_hmr_terminal_exclusive(
            path=(tmp_path / "escaped.json").resolve(),
            terminal=value,
            evidence_root=evidence_root,
            disposable_root=disposable_root,
        )
    with pytest.raises(terminal.StartupTerminalError):
        terminal.write_pre_hmr_terminal_exclusive(
            path=disposable_root / "deleted.json",
            terminal=value,
            evidence_root=evidence_root,
            disposable_root=disposable_root,
        )


def test_reader_and_writer_reject_symlinks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    target = tmp_path / "target.raw"
    target.write_bytes(b"hostile")
    link = target
    original_is_symlink = Path.is_symlink
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda self: self == link or original_is_symlink(self),
    )
    with pytest.raises(terminal.StartupTerminalError):
        terminal.read_startup_stream(link)

    evidence_root = (tmp_path / "evidence").resolve()
    disposable_root = (tmp_path / "disposable").resolve()
    real_parent = evidence_root / "real-parent"
    linked_parent = evidence_root / "linked-parent"
    evidence_root.mkdir()
    disposable_root.mkdir()
    real_parent.mkdir()
    linked_parent.mkdir()
    monkeypatch.setattr(
        Path,
        "is_symlink",
        lambda self: self == linked_parent or original_is_symlink(self),
    )
    with pytest.raises(terminal.StartupTerminalError):
        terminal.write_pre_hmr_terminal_exclusive(
            path=linked_parent / "terminal.json",
            terminal=build(),
            evidence_root=evidence_root,
            disposable_root=disposable_root,
        )


def test_attempt_001_and_002_evidence_remains_byte_immutable() -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "orchestration"
        / "continuity"
        / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-"
        "monitored-development-rehearsal"
    )
    baseline = json.loads(
        (root / "attempt-002" / "attempt-001-immutability-baseline.json").read_text(
            encoding="utf-8"
        )
    )
    for name, expected in baseline["artifacts"].items():
        payload = (root / name).read_bytes()
        assert len(payload) == expected["bytes"]
        assert hashlib.sha256(payload).hexdigest() == expected["sha256"]

    attempt_two = root / "attempt-002"
    expected_hashes = {
        "occupied-attempt-consumed.json": "d9af398db0e9416f29df6316ac349a50a9c1516fbf54ccf6b0c40357340457a1",
        "occupied-terminal.json": "6f873651c94e81faa8af93bd3d191dd67c13982bfca081479cee6e390ff6cb00",
        "occupied-report.md": "eaaaf7d99e2a36f09516a8f69a4ea8559214d83807c73ccfa97044a1723a3a7c",
        "diagnosis.md": "d3cf50a3d5e94c744931143f2a796069ed5cba487859aacde877dcb3df3a3685",
        "efficacy-reading.json": "19f5f2db1a2a6deec435154ae1cf74b8af9af12b692431971800cebe2f85c7b6",
        "postterminal-command-validation-receipt.json": "fe44bc423fd37b07b019f9dee14c666553713795557a56364cff2839339c49d9",
    }
    for name, expected in expected_hashes.items():
        assert hashlib.sha256((attempt_two / name).read_bytes()).hexdigest() == expected


def test_component_has_no_subprocess_or_provider_surface() -> None:
    source = Path(terminal.__file__).read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "DEEPSEEK_API_KEY" not in source
    assert "requests." not in source
    assert "urllib" not in source


def test_controller_binds_stale_guard_terminal_before_cleanup_and_outer_digest() -> None:
    source = inspect.getsource(controller.execute_native)
    assert "PRE_HMR_TERMINAL_PATH.exists()" in source
    read_index = source.index(
        "stream_readings[label] = startup_terminal.read_startup_stream("
    )
    write_index = source.index("startup_terminal.write_pre_hmr_terminal_exclusive(")
    cleanup_index = source.index("remove_exact_attempt_root(root, parent)")
    outer_index = source.index('"pre_hmr_startup_terminal_sha256"')
    publish_index = source.index("write_json_exclusive(TERMINAL_PATH, terminal)")
    assert read_index < write_index < cleanup_index < outer_index < publish_index

    config = controller.attempt_two_configuration()
    assert config["pre_hmr_terminal_path"].parent == (
        controller.CONTINUITY_ROOT / "attempt-002"
    )
    schema = json.loads(config["terminal_schema_path"].read_text(encoding="utf-8"))
    assert schema["properties"]["pre_hmr_startup_terminal_sha256"] == {
        "type": ["string", "null"],
        "pattern": "^[0-9a-f]{64}$",
    }


def test_recovery_contract_and_evidence_are_current_and_provider_disabled() -> None:
    value = recovery.validate_artifacts()
    contract = json.loads(recovery.CONTRACT_PATH.read_text(encoding="utf-8"))
    assert contract["stages"] == sorted(terminal.STAGES)
    assert contract["causes"] == sorted(terminal.CAUSES)
    assert contract["classification_byte_limit_per_stream"] == 65_536
    assert value["scenario_count"] == 12
    assert value["mutation_count"] == 12
    assert value["immutable_artifact_count"] == 17
    assert all(value["controller_ordering"].values())
    assert set(value["boundary"].values()) == {0}


def test_provider_disabled_validation_cannot_start_any_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("subprocess_forbidden")

    monkeypatch.setattr(controller.subprocess, "Popen", forbidden)
    monkeypatch.setattr(controller.subprocess, "run", forbidden)
    value = recovery.validate_artifacts()
    assert value["boundary"]["subprocess_count"] == 0
    assert value["boundary"]["provider_request_count"] == 0


def test_terminal_schema_rejects_raw_or_unknown_fields() -> None:
    schema = json.loads(recovery.TERMINAL_SCHEMA_PATH.read_text(encoding="utf-8"))
    value = build(stderr=b"ERR_MODULE_NOT_FOUND")
    extra = dict(value)
    extra["raw_stderr"] = "forbidden"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(extra)
