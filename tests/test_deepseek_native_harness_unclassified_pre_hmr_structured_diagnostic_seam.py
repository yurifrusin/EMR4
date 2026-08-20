from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from orchestration_harness import native_pre_hmr_diagnostic as diagnostic
from orchestration_harness import native_startup_terminal as startup_terminal
from scripts import (
    deepseek_native_harness_provider_free_unclassified_pre_hmr_structured_diagnostic_seam_recovery
    as recovery,
)


IDENTITY = {
    "operation_id": recovery.OPERATION_ID,
    "attempt_id": "future-source-static-fixture-001",
    "candidate_source": "ae07978123a3fd4029715f971b76e7307a4839c1",
}


def stream(payload: bytes) -> dict[str, object]:
    return {
        "byte_count": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "classification_bytes": payload,
        "limit_exceeded": False,
    }


def structured() -> dict[str, object]:
    return diagnostic.build_diagnostic_from_fixture(
        {
            "name": "Error",
            "message": "dsh: plugin tree failed to load: dynamic plugin",
            "cause": {
                "constructor_name": "ConfigFileError",
                "stage": "parse",
                "cause": {
                    "name": "TypeError",
                    "code": "ERR_MODULE_NOT_FOUND",
                },
            },
        },
        **IDENTITY,
    )


def terminal_v2() -> dict[str, object]:
    return diagnostic.build_structured_pre_hmr_terminal(
        **IDENTITY,
        native_process_started=True,
        exit_code=1,
        controller_coordinate="native_process_exited_nonzero",
        hmr_events=[],
        stdout=stream(b""),
        stderr=stream(b"raw secret-shaped stderr"),
        structured_diagnostic=structured(),
    )


def test_contract_vocabulary_matches_the_component_exactly() -> None:
    contract = recovery.load_contract()
    value = contract["diagnostic"]
    assert value == {
        "schema_version": diagnostic.SCHEMA_VERSION,
        "phase": diagnostic.PHASE,
        "maximum_cause_nodes": diagnostic.MAX_CAUSE_NODES,
        "maximum_sidecar_bytes": diagnostic.MAX_SIDECAR_BYTES,
        "error_kinds": sorted(diagnostic.ERROR_KINDS),
        "code_coordinates": sorted(diagnostic.CODE_COORDINATES),
        "config_stages": sorted(diagnostic.CONFIG_STAGES),
        "message_coordinates": sorted(diagnostic.MESSAGE_COORDINATES),
        "aggregate_shapes": sorted(diagnostic.AGGREGATE_SHAPES),
    }


def test_source_backed_chain_keeps_only_closed_coordinates() -> None:
    value = structured()
    assert value["cause_chain"] == [
        {
            "position": 0,
            "error_kind": "error",
            "code_coordinate": "none",
            "config_stage": "none",
            "message_coordinate": "plugin_tree_failed_to_load",
            "aggregate_shape": "none",
        },
        {
            "position": 1,
            "error_kind": "config_file_error",
            "code_coordinate": "none",
            "config_stage": "parse",
            "message_coordinate": "none",
            "aggregate_shape": "none",
        },
        {
            "position": 2,
            "error_kind": "type_error",
            "code_coordinate": "ERR_MODULE_NOT_FOUND",
            "config_stage": "none",
            "message_coordinate": "none",
            "aggregate_shape": "none",
        },
    ]
    assert value["raw_error_message_retained"] is False
    assert value["raw_stack_retained"] is False
    assert value["raw_paths_retained"] is False


@pytest.mark.parametrize(
    ("errors", "expected"),
    [([], "zero"), (["secret"], "one"), (["secret", "secret"], "multiple")],
)
def test_aggregate_children_are_never_traversed_or_serialized(
    errors: list[str], expected: str
) -> None:
    value = diagnostic.build_diagnostic_from_fixture(
        {"name": "AggregateError", "errors": errors}, **IDENTITY
    )
    assert value["cause_chain"][0]["aggregate_shape"] == expected
    assert b"secret" not in diagnostic.diagnostic_bytes(value)


def test_unknown_dynamic_values_collapse_without_leaking() -> None:
    secret = "sk-live-C:/patients/alice/private-plugin"
    value = diagnostic.build_diagnostic_from_fixture(
        {
            "name": secret,
            "code": secret,
            "stage": secret,
            "message": secret,
            "errors": [secret],
        },
        **IDENTITY,
    )
    assert value["cause_chain"][0] == {
        "position": 0,
        "error_kind": "unknown",
        "code_coordinate": "unrecognized",
        "config_stage": "none",
        "message_coordinate": "none",
        "aggregate_shape": "none",
    }
    assert secret.encode() not in diagnostic.diagnostic_bytes(value)


def test_cycle_and_depth_are_bounded() -> None:
    cycle: dict[str, object] = {"name": "Error"}
    cycle["cause"] = cycle
    cycled = diagnostic.build_diagnostic_from_fixture(cycle, **IDENTITY)
    assert cycled["cause_chain_cycle_detected"] is True
    assert cycled["cause_chain_truncated"] is False
    assert len(cycled["cause_chain"]) == 1

    chain: dict[str, object] = {"name": "Error"}
    for _ in range(diagnostic.MAX_CAUSE_NODES + 2):
        chain = {"name": "Error", "cause": chain}
    truncated = diagnostic.build_diagnostic_from_fixture(chain, **IDENTITY)
    assert truncated["cause_chain_cycle_detected"] is False
    assert truncated["cause_chain_truncated"] is True
    assert len(truncated["cause_chain"]) == diagnostic.MAX_CAUSE_NODES


class HostileGetter:
    @property
    def name(self) -> str:
        raise LookupError("secret")

    @property
    def code(self) -> str:
        raise LookupError("secret")

    @property
    def cause(self) -> object:
        raise LookupError("secret")


def test_hostile_getters_collapse_to_unknown() -> None:
    value = diagnostic.build_diagnostic_from_fixture(HostileGetter(), **IDENTITY)
    assert value["cause_chain"][0]["error_kind"] == "unknown"
    assert value["cause_chain"][0]["code_coordinate"] == "none"
    assert len(value["cause_chain"]) == 1


@pytest.mark.parametrize(
    ("field", "replacement", "error"),
    [
        ("schema_version", "v999", "diagnostic_identity_invalid"),
        ("candidate_source", "ae07978", "candidate_source_invalid"),
        ("raw_stack_retained", True, "raw_retention_invalid"),
        ("cause_chain_cycle_detected", "false", "chain_flags_invalid"),
    ],
)
def test_hostile_top_level_mutations_fail_closed(
    field: str, replacement: object, error: str
) -> None:
    value = structured()
    value[field] = replacement
    with pytest.raises(diagnostic.StructuredDiagnosticError, match=error):
        diagnostic.validate_structured_diagnostic(value)


def test_extra_and_relationship_invalid_nodes_fail_closed() -> None:
    extra = structured()
    extra["raw_message"] = "secret"
    with pytest.raises(diagnostic.StructuredDiagnosticError, match="diagnostic_keys_invalid"):
        diagnostic.validate_structured_diagnostic(extra)

    invalid = structured()
    invalid["cause_chain"][0]["config_stage"] = "read"
    with pytest.raises(
        diagnostic.StructuredDiagnosticError,
        match="config_stage_relationship_invalid",
    ):
        diagnostic.validate_structured_diagnostic(invalid)


def test_sidecar_reader_requires_canonical_exact_identity_inside_root(tmp_path: Path) -> None:
    root = tmp_path.resolve()
    path = root / "diagnostic.json"
    value = structured()
    path.write_bytes(diagnostic.diagnostic_bytes(value))
    assert diagnostic.read_structured_diagnostic(
        path,
        disposable_root=root,
        **IDENTITY,
    ) == value

    path.write_bytes(json.dumps(value, indent=2).encode())
    with pytest.raises(
        diagnostic.StructuredDiagnosticError, match="diagnostic_canonical_bytes_required"
    ):
        diagnostic.read_structured_diagnostic(
            path,
            disposable_root=root,
            **IDENTITY,
        )


def test_sidecar_reader_rejects_invalid_json_oversize_and_identity(
    tmp_path: Path,
) -> None:
    root = tmp_path.resolve()
    path = root / "diagnostic.json"
    path.write_bytes(b"not json")
    with pytest.raises(diagnostic.StructuredDiagnosticError, match="diagnostic_json_invalid"):
        diagnostic.read_structured_diagnostic(path, disposable_root=root, **IDENTITY)
    path.write_bytes(b"x" * (diagnostic.MAX_SIDECAR_BYTES + 1))
    with pytest.raises(diagnostic.StructuredDiagnosticError, match="diagnostic_file_invalid"):
        diagnostic.read_structured_diagnostic(path, disposable_root=root, **IDENTITY)
    wrong = structured()
    wrong["attempt_id"] = "different-attempt"
    path.write_bytes(diagnostic.diagnostic_bytes(wrong))
    with pytest.raises(
        diagnostic.StructuredDiagnosticError, match="diagnostic_runtime_identity_mismatch"
    ):
        diagnostic.read_structured_diagnostic(path, disposable_root=root, **IDENTITY)


def test_wrapper_source_has_one_safe_write_and_identical_rethrow() -> None:
    contract = recovery.load_contract()
    package_root = Path(contract["installed_source"]["root"]) / "dsh"
    root = Path("C:/deterministic/native-pre-hmr-diagnostic").resolve()
    payload = diagnostic.build_entrypoint_wrapper_source(
        package_root=package_root,
        wrapper_path=root / "wrapper.mjs",
        diagnostic_path=root / "diagnostic.json",
        disposable_root=root,
        **IDENTITY,
    )
    projection = diagnostic.validate_entrypoint_wrapper_source(payload)
    assert all(projection["checks"].values())
    source = payload.decode()
    assert source.count("await import(ENTRYPOINT_URL)") == 1
    assert source.count('openSync(DIAGNOSTIC_PATH, "wx"') == 1
    assert source.count("throw error;") == 1
    assert "process.exit" not in source
    assert ".stack" not in source


def test_v2_embeds_only_validated_diagnostic_and_v1_remains_unchanged() -> None:
    value = terminal_v2()
    assert value["schema_version"] == diagnostic.TERMINAL_SCHEMA_VERSION
    assert value["cause"] == "structured_entrypoint_import_rejected"
    payload = diagnostic.structured_terminal_bytes(value)
    assert b"raw secret-shaped stderr" not in payload
    assert b"dynamic plugin" not in payload

    historical = recovery.ATTEMPT_TERMINAL_PATH.read_bytes()
    historical_value = json.loads(historical)
    assert historical_value["schema_version"] == startup_terminal.SCHEMA_VERSION
    assert startup_terminal.terminal_bytes(historical_value) == historical


def test_v2_identity_and_runtime_relationships_fail_closed() -> None:
    wrong_identity = structured()
    wrong_identity["attempt_id"] = "different-attempt"
    with pytest.raises(diagnostic.StructuredDiagnosticError, match="identity_mismatch"):
        diagnostic.build_structured_pre_hmr_terminal(
            **IDENTITY,
            native_process_started=True,
            exit_code=1,
            controller_coordinate="native_process_exited_nonzero",
            hmr_events=[],
            stdout=stream(b""),
            stderr=stream(b"opaque"),
            structured_diagnostic=wrong_identity,
        )

    invalid = terminal_v2()
    invalid["controller_coordinate"] = "native_worker_timeout"
    with pytest.raises(
        diagnostic.StructuredDiagnosticError,
        match="structured_terminal_runtime_relationship_invalid",
    ):
        diagnostic.validate_structured_pre_hmr_terminal(invalid)


def test_future_controller_envelope_orders_wrapper_sidecar_terminal_and_cleanup() -> None:
    source = recovery.CONTROLLER_PATH.read_text(encoding="utf-8")
    assert source.index('str(package_root / "lib" / "bin.js")') < source.index(
        "harness = subprocess.Popen("
    )
    assert source.index("startup_terminal.write_pre_hmr_terminal_exclusive(") < source.index(
        "cleanup_passed = remove_exact_attempt_root("
    )
    projection = diagnostic.validate_future_controller_binding_envelope(
        diagnostic.future_controller_binding_envelope_source()
    )
    assert all(projection["checks"].values())


def test_deterministic_recovery_launches_no_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("subprocess execution forbidden")

    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    value = recovery.deterministic_evidence()
    assert value["result"] == "pass"
    assert value["proof_boundary"] == {
        "python_process_count": 1,
        "node_process_count": 0,
        "native_harness_process_count": 0,
        "broker_process_count": 0,
        "worker_process_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "raw_attempt_stream_read_count": 0,
    }


def test_canonical_evidence_matches_fresh_projection() -> None:
    assert recovery.EVIDENCE_PATH.is_file()
    observed = json.loads(recovery.EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert observed == recovery.deterministic_evidence()
    assert recovery.REPORT_PATH.is_file()
    assert recovery.CONTRACT_SCHEMA_PATH.is_file()
    assert recovery.EVIDENCE_SCHEMA_PATH.is_file()
