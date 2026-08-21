from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import jsonschema
import pytest

from orchestration_harness import (
    bounded_worker_structured_diagnostic_controller as controller,
)
from orchestration_harness import native_pre_hmr_diagnostic as diagnostic
from orchestration_harness import native_startup_terminal as legacy_terminal
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_controller,
)
from scripts import (
    raisa_provider_free_authored_synthetic_native_harness_structured_diagnostic_bounded_worker_controller_convergence_rehearsal
    as rehearsal,
)


IDENTITY = {
    "operation_id": rehearsal.OPERATION_ID,
    "attempt_id": rehearsal.ATTEMPT_ID,
    "candidate_source": "1" * 40,
}


def stream(payload: bytes) -> dict[str, object]:
    return {
        "byte_count": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "classification_bytes": payload,
        "limit_exceeded": False,
    }


def select(root: Path, path: Path) -> dict[str, object]:
    return controller.select_pre_hmr_terminal(
        **IDENTITY,
        native_process_started=True,
        exit_code=1,
        controller_coordinate="native_process_exited_nonzero",
        hmr_events=[],
        stdout=stream(b""),
        stderr=stream(b"secret-shaped stderr"),
        diagnostic_path=path,
        disposable_root=root,
    )


def test_launch_binding_uses_canonical_wrapper_and_accepted_task(tmp_path: Path) -> None:
    root = (tmp_path / "root").resolve()
    package = root / "package"
    (package / "lib").mkdir(parents=True)
    (package / "lib" / "bin.js").write_bytes(b"throw new Error('fixture')\n")
    value = controller.build_launch_binding(
        disposable_root=root,
        package_root=package,
        **IDENTITY,
        target_path="C:/synthetic/synthetic_window_coalescer.py",
        node_executable="node",
    )
    assert value["command"][:5] == [
        "node",
        "--expose-internals",
        str(root / controller.WRAPPER_LEAF),
        "--profile",
        "headless",
    ]
    assert value["command"][5] == accepted_controller.task_text(
        "C:/synthetic/synthetic_window_coalescer.py"
    )
    assert value["wrapper_path"].parent == root
    assert value["diagnostic_path"].parent == root
    assert all(value["wrapper_projection"]["checks"].values())
    assert value["wrapper_sha256"] == hashlib.sha256(
        value["wrapper_path"].read_bytes()
    ).hexdigest()
    with pytest.raises(controller.ControllerConvergenceError):
        controller.build_launch_binding(
            disposable_root=root,
            package_root=package,
            **IDENTITY,
            target_path="C:/synthetic/synthetic_window_coalescer.py",
            node_executable="node",
        )


def test_exact_canonical_sidecar_selects_v2_and_writes_outside_root(
    tmp_path: Path,
) -> None:
    root = (tmp_path / "root").resolve()
    evidence = (tmp_path / "evidence").resolve()
    root.mkdir()
    evidence.mkdir()
    path = root / controller.DIAGNOSTIC_LEAF
    value = diagnostic.build_diagnostic_from_fixture(
        {"name": "Error", "message": "dynamic secret"}, **IDENTITY
    )
    path.write_bytes(diagnostic.diagnostic_bytes(value))
    selected = select(root, path)
    assert selected["structured_accepted"] is True
    assert selected["failure_coordinate"] is None
    terminal = selected["terminal"]
    assert terminal["schema_version"] == diagnostic.TERMINAL_SCHEMA_VERSION
    assert terminal["structured_diagnostic"] == value
    output = evidence / "terminal.json"
    digest = controller.write_selected_terminal_exclusive(
        path=output,
        terminal=terminal,
        evidence_root=evidence,
        disposable_root=root,
    )
    assert digest == hashlib.sha256(output.read_bytes()).hexdigest()
    assert b"dynamic secret" not in output.read_bytes()


def test_absent_and_invalid_sidecars_preserve_v1_and_fail_closed(
    tmp_path: Path,
) -> None:
    root = tmp_path.resolve()
    absent = select(root, root / "absent.json")
    assert absent["terminal"]["schema_version"] == legacy_terminal.SCHEMA_VERSION
    assert absent["structured_accepted"] is False
    assert absent["failure_coordinate"] == "structured_diagnostic_absent"

    valid = diagnostic.build_diagnostic_from_fixture(
        {"name": "Error"}, **IDENTITY
    )
    fixtures: dict[str, bytes] = {
        "malformed.json": b"not-json",
        "noncanonical.json": json.dumps(valid, indent=2).encode(),
    }
    wrong = dict(valid)
    wrong["attempt_id"] = "wrong-attempt"
    fixtures["wrong.json"] = diagnostic.diagnostic_bytes(wrong)
    for name, payload in fixtures.items():
        path = root / name
        path.write_bytes(payload)
        selected = select(root, path)
        assert selected["terminal"]["schema_version"] == legacy_terminal.SCHEMA_VERSION
        assert selected["structured_accepted"] is False
        assert selected["failure_coordinate"] == "structured_diagnostic_invalid"

    escaped = tmp_path.parent / f"{tmp_path.name}-escaped-sidecar.json"
    escaped.write_bytes(diagnostic.diagnostic_bytes(valid))
    try:
        selected = select(root, escaped)
        assert selected["failure_coordinate"] == "structured_diagnostic_invalid"
    finally:
        escaped.unlink()


def test_nonapplicable_timeout_retains_v1_without_structured_reclassification(
    tmp_path: Path,
) -> None:
    selected = controller.select_pre_hmr_terminal(
        **IDENTITY,
        native_process_started=True,
        exit_code=None,
        controller_coordinate="native_worker_timeout",
        hmr_events=[],
        stdout=stream(b""),
        stderr=stream(b"timeout"),
        diagnostic_path=tmp_path / "absent.json",
        disposable_root=tmp_path,
    )
    assert selected["terminal"]["schema_version"] == legacy_terminal.SCHEMA_VERSION
    assert selected["failure_coordinate"] is None


def test_lifecycle_envelope_is_serial_terminal_before_cleanup() -> None:
    value = controller.validate_lifecycle_envelope(
        controller.lifecycle_envelope_source()
    )
    assert all(value["checks"].values())


def test_deterministic_evidence_launches_no_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("subprocess_forbidden")

    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    value = rehearsal.deterministic_evidence()
    assert value["result"] == "pass"
    assert set(value["process_boundary"].values()) == {0}
    assert value["immutable_artifact_count"] == 7


def test_contract_evidence_and_report_are_current() -> None:
    contract = rehearsal.load_contract()
    contract_schema = json.loads(rehearsal.CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator(contract_schema).validate(contract)
    value = rehearsal.validate_artifacts()
    assert value["selection_matrix"]["valid_exact_identity"] == contract[
        "selection"
    ]["valid_exact_identity"]
    assert value["selection_matrix"]["absent"] == contract["selection"]["absent"]


def test_plan_and_boundaries_are_explicit() -> None:
    plan = (
        rehearsal.REPO_ROOT
        / "docs"
        / f"{rehearsal.OPERATION_ID}-plan.md"
    ).read_text(encoding="utf-8")
    threat = (
        rehearsal.REPO_ROOT
        / "docs"
        / "security"
        / f"{rehearsal.OPERATION_ID}-threat-model-delta.md"
    ).read_text(encoding="utf-8")
    for token in (
        "Status: `frozen`",
        "descendant controller adapter",
        "structured_diagnostic_absent",
        "structured_diagnostic_invalid",
        "no native Harness, broker, worker",
        "2e34bdad732fdab32fbf778280b3d3c70d66d602",
    ):
        assert token.lower() in plan.lower()
    assert "Historical attempts are silently reclassified" in threat
