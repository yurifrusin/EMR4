"""Focused deterministic tests for the Bureau C5 process adapter and controller.

These tests use provider-free fakes and source checks only.  They never start a
process, bind or connect a socket, allocate a port, create or remove a
directory, invoke a provider, inspect ADC or run the live rehearsal.  The real
capability adapters are implemented but never invoked here.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from scripts.model_required_bureau_c5_acceptance import (
    EXPECTED_ARTIFACT_SHA256,
    PORT,
    TARGET_NONCE,
    FakeHttpObserver,
    FakeProcessObserver,
    new_controller,
)
from scripts.model_required_bureau_c5_rehearsal import (
    build_launch_argv,
    build_minimal_environment,
    validate_launch_argv,
)

ROOT = Path(__file__).resolve().parents[1]


def test_real_adapters_are_never_invoked_by_import():
    from scripts.model_required_bureau_c5_acceptance import _fake_operation_accounting

    accounting = _fake_operation_accounting()
    assert accounting["fake_process_starts"] >= 2
    assert accounting["fake_process_stops"] >= 1


def test_launch_argv_is_fixed_and_rejects_overrides():
    signature = inspect.signature(build_launch_argv)
    assert set(signature.parameters) == {"repo_root", "port", "nonce", "generation"}
    argv = build_launch_argv(repo_root=ROOT, port=PORT, nonce=TARGET_NONCE, generation=2)
    assert len(argv) == 11
    assert argv[1] == "-I"
    assert argv[3] == "--host" and argv[4] == "127.0.0.1"
    assert argv[5] == "--port" and argv[6] == str(PORT)
    assert argv[7] == "--nonce" and argv[8] == TARGET_NONCE
    assert argv[9] == "--generation" and argv[10] == "2"
    validate_launch_argv(argv, ROOT)

    bad = list(argv)
    bad[0] = "C:/not-the-pinned-python.exe"
    with pytest.raises(ValueError):
        validate_launch_argv(bad, ROOT)

    bad = list(argv)
    bad[2] = "C:/not-the-target.py"
    with pytest.raises(ValueError):
        validate_launch_argv(bad, ROOT)

    bad = list(argv)
    bad[4] = "0.0.0.0"
    with pytest.raises(ValueError):
        validate_launch_argv(bad, ROOT)

    with pytest.raises(ValueError):
        build_launch_argv(repo_root=ROOT, port=0, nonce=TARGET_NONCE, generation=2)
    with pytest.raises(ValueError):
        build_launch_argv(repo_root=ROOT, port=PORT, nonce="not-a-nonce", generation=2)
    with pytest.raises(ValueError):
        build_launch_argv(repo_root=ROOT, port=PORT, nonce=TARGET_NONCE, generation=3)


def test_minimal_environment_is_credential_free():
    environment = build_minimal_environment()
    blocked = ("GOOGLE", "CLOUD", "ADC", "CREDENTIAL", "TOKEN", "SECRET", "AWS", "AZURE", "KEY")
    for key in environment:
        assert not any(token in key.upper() for token in blocked)


def test_baseline_fault_post_fault_agreement_with_fakes():
    process = FakeProcessObserver()
    http = FakeHttpObserver()
    controller = new_controller(process=process, http=http)
    http.generation = 1
    handle, healthy = controller.run_baseline(
        port=PORT, nonce=TARGET_NONCE, artifact_sha256=EXPECTED_ARTIFACT_SHA256
    )
    assert healthy is True
    assert process.starts == 1
    assert controller.inject_fault(handle) is True
    http.mode = "refused"
    assert controller.post_fault_verify(handle, port=PORT) is True
    assert process.stops == 1


def test_pid_handle_and_nonce_generation_artifact_checks_prevent_substitution():
    process = FakeProcessObserver()
    http = FakeHttpObserver()
    controller = new_controller(process=process, http=http)
    http.generation = 1
    handle, healthy = controller.run_baseline(
        port=PORT, nonce=TARGET_NONCE, artifact_sha256=EXPECTED_ARTIFACT_SHA256
    )
    assert healthy is True
    http.nonce = "0" * 32
    assert (
        controller._matches_health(
            http.probe("127.0.0.1", PORT, "/healthz"),
            nonce=TARGET_NONCE,
            generation=1,
            artifact_sha256=EXPECTED_ARTIFACT_SHA256,
        )
        is False
    )
    http.nonce = TARGET_NONCE
    assert (
        controller._matches_health(
            http.probe("127.0.0.1", PORT, "/healthz"),
            nonce=TARGET_NONCE,
            generation=1,
            artifact_sha256="0" * 64,
        )
        is False
    )
    assert handle.pid >= 1000
    assert handle.argv[10] == "1"


def test_success_released_only_from_distinct_fresh_process_and_http_readback():
    from scripts.model_required_bureau_c5_acceptance import run_success_path

    process = FakeProcessObserver()
    http = FakeHttpObserver()
    controller, issuer, issued, result = run_success_path(process=process, http=http)
    assert result["result"] == "live_development_recovery_verified"
    assert result["generation"] == 2
    assert result["state"] == "healthy"
    assert result["target_nonce"] == TARGET_NONCE
    assert result["artifact_sha256"] == EXPECTED_ARTIFACT_SHA256
    assert process.starts == 2
    assert process.stops == 1
    assert controller.store.launch_state == "verified"


def test_rollback_distinguishes_verified_from_inconclusive():
    from scripts.model_required_bureau_c5_acceptance import _validate_fault_injection_and_rollback

    faults = _validate_fault_injection_and_rollback()
    verified = faults["readback_failed_rollback_verified"]
    inconclusive = faults["readback_failed_rollback_inconclusive"]
    assert verified["reason_code"] == "LIVE_RECOVERY_ROLLBACK_VERIFIED"
    assert verified["rollback"] == {"invoked": True, "verified": True}
    assert inconclusive["reason_code"] == "LIVE_RECOVERY_ROLLBACK_UNVERIFIED"
    assert inconclusive["rollback"] == {"invoked": True, "verified": False}


def test_cleanup_rejects_workspace_and_caller_paths():
    from scripts.model_required_bureau_c5_acceptance import FakeDirectoryOps

    directory = FakeDirectoryOps()
    task_root = ROOT / "c5-task-0001"
    assert directory.validate_owned_path(ROOT, task_root) is False
    assert directory.validate_owned_path(ROOT.parent, task_root) is False
    assert directory.validate_owned_path(task_root, task_root) is True
    assert directory.validate_owned_path(task_root / "nested", task_root) is True


def test_real_adapter_source_uses_argument_array_with_shell_false():
    source = Path("scripts/model_required_bureau_c5_rehearsal.py").read_text(encoding="utf-8")
    assert "subprocess.Popen(" in source
    assert "shell=False" in source
    assert "shell=True" not in source
    assert "os.system(" not in source and "os.popen(" not in source
    assert "stdin=subprocess.DEVNULL" in source
    assert "psutil" not in source


def test_worker_acceptance_counters_are_zero_for_live_capabilities():
    from scripts.model_required_bureau_c5_contract import ForbiddenOperationCounters

    counters = ForbiddenOperationCounters().to_dict()
    assert len(counters) == 20
    assert set(counters.values()) == {0}


def test_controller_never_imports_or_mounts_product_route():
    source = Path("scripts/model_required_bureau_c5_rehearsal.py").read_text(encoding="utf-8")
    assert "import app" not in source
    assert "fastapi" not in source and "flask" not in source
    assert "app.main" not in source
