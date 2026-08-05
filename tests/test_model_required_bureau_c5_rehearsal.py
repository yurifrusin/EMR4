"""Focused deterministic tests for the Bureau C5 process adapter and controller.

These tests use provider-free fakes and source checks only.  They never start a
process, bind or connect a socket, allocate a port, create or remove a
directory, invoke a provider, inspect ADC or run the live rehearsal.  The real
capability adapters are implemented but never invoked here.
"""

from __future__ import annotations

import errno
import inspect
import socket
from dataclasses import replace
from pathlib import Path

import pytest

from scripts import model_required_bureau_c5_rehearsal as rehearsal
from scripts.model_required_bureau_c5_acceptance import (
    EXPECTED_ARTIFACT_SHA256,
    CORRELATION_ID,
    IDEMPOTENCY_KEY,
    PORT,
    TARGET_NONCE,
    FakeHttpObserver,
    FakePortAllocator,
    FakeProcessObserver,
    admit_provider_candidate,
    build_approval,
    build_frame,
    mint_evidence,
    new_controller,
    now_callable,
    parse_candidate,
)
from scripts.model_required_bureau_c5_contract import (
    C5EvidenceIssuer,
    C5SharedStore,
    proofread_candidate,
)
from scripts.model_required_bureau_c5_rehearsal import (
    LoopbackPortAllocator,
    PortReservation,
    ProcessAdapter,
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
    assert set(signature.parameters) == {"port", "nonce", "generation"}
    argv = build_launch_argv(port=PORT, nonce=TARGET_NONCE, generation=2)
    assert len(argv) == 11
    assert argv[1] == "-I"
    assert argv[3] == "--host" and argv[4] == "127.0.0.1"
    assert argv[5] == "--port" and argv[6] == str(PORT)
    assert argv[7] == "--nonce" and argv[8] == TARGET_NONCE
    assert argv[9] == "--generation" and argv[10] == "2"
    validate_launch_argv(argv)

    bad = list(argv)
    bad[0] = "C:/not-the-pinned-python.exe"
    with pytest.raises(ValueError):
        validate_launch_argv(bad)

    bad = list(argv)
    bad[2] = "C:/not-the-target.py"
    with pytest.raises(ValueError):
        validate_launch_argv(bad)

    bad = list(argv)
    bad[4] = "0.0.0.0"
    with pytest.raises(ValueError):
        validate_launch_argv(bad)

    with pytest.raises(ValueError):
        build_launch_argv(port=0, nonce=TARGET_NONCE, generation=2)
    with pytest.raises(ValueError):
        build_launch_argv(port=PORT, nonce="not-a-nonce", generation=2)
    with pytest.raises(ValueError):
        build_launch_argv(port=PORT, nonce=TARGET_NONCE, generation=3)


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


def test_post_fault_absence_uses_exact_port_reacquisition_not_http_inference():
    process = FakeProcessObserver()
    http = FakeHttpObserver()
    http.is_live_capability = True
    port_allocator = FakePortAllocator()
    port_allocator.is_live_capability = True
    controller = new_controller(
        process=process,
        http=http,
        port_allocator=port_allocator,
    )
    http.generation = 1
    handle, healthy = controller.run_baseline(
        port=PORT, nonce=TARGET_NONCE, artifact_sha256=EXPECTED_ARTIFACT_SHA256
    )
    assert healthy is True
    assert controller.inject_fault(handle) is True
    assert controller.post_fault_verify(handle, port=PORT) is True
    assert controller.operation_counters["socket_connects"] == 1
    assert controller.operation_counters["socket_binds"] == 2
    assert controller.operation_counters["port_allocations"] == 2
    assert port_allocator.allocations == 2


def test_post_fault_does_not_bind_until_owned_process_is_absent():
    process = FakeProcessObserver()
    http = FakeHttpObserver()
    port_allocator = FakePortAllocator()
    controller = new_controller(
        process=process,
        http=http,
        port_allocator=port_allocator,
    )
    http.generation = 1
    handle, healthy = controller.run_baseline(
        port=PORT, nonce=TARGET_NONCE, artifact_sha256=EXPECTED_ARTIFACT_SHA256
    )
    assert healthy is True
    controller.store.launch_state = "fault_injected"
    assert controller.post_fault_verify(handle, port=PORT) is False
    assert port_allocator.allocations == 1


def test_failed_exact_port_reacquisition_counts_every_bind_attempt():
    process = FakeProcessObserver()
    http = FakeHttpObserver()
    port_allocator = FakePortAllocator()
    port_allocator.is_live_capability = True
    controller = new_controller(
        process=process,
        http=http,
        port_allocator=port_allocator,
    )
    http.generation = 1
    handle, healthy = controller.run_baseline(
        port=PORT, nonce=TARGET_NONCE, artifact_sha256=EXPECTED_ARTIFACT_SHA256
    )
    assert healthy is True
    assert controller.inject_fault(handle) is True

    def exhausted(_port):
        error = OSError(errno.EADDRINUSE, "address remains in use")
        error.bind_attempts = 3
        raise error

    port_allocator.reserve_exact = exhausted
    assert controller.post_fault_verify(handle, port=PORT) is False
    assert controller.operation_counters["socket_binds"] == 4
    assert controller.operation_counters["port_allocations"] == 1


def test_windows_port_allocator_sets_exclusive_before_bind_and_never_reuse(
    monkeypatch,
):
    events = []

    class FakeSocket:
        def __init__(self):
            self.bound_port = 0

        def setsockopt(self, level, option, value):
            events.append(("setsockopt", level, option, value))

        def bind(self, endpoint):
            events.append(("bind", endpoint))
            self.bound_port = 49199

        def getsockname(self):
            return ("127.0.0.1", self.bound_port)

        def close(self):
            events.append(("close",))

    monkeypatch.setattr(rehearsal.os, "name", "nt")
    monkeypatch.setattr(socket, "SO_EXCLUSIVEADDRUSE", -5, raising=False)
    monkeypatch.setattr(socket, "socket", lambda *_args: FakeSocket())
    reservation = LoopbackPortAllocator().reserve()
    assert events[0] == (
        "setsockopt",
        socket.SOL_SOCKET,
        socket.SO_EXCLUSIVEADDRUSE,
        1,
    )
    assert events[1] == ("bind", ("127.0.0.1", 0))
    assert all(
        event[2] != socket.SO_REUSEADDR
        for event in events
        if event[0] == "setsockopt"
    )
    assert reservation.exclusive_address_use is True


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
            port=PORT,
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
            port=PORT,
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
    assert directory.validate_owned_path(ROOT) is False
    assert directory.validate_owned_path(ROOT.parent) is False
    assert directory.validate_owned_path(task_root) is True
    assert directory.validate_owned_path(task_root / "nested") is False


def test_real_adapter_source_uses_argument_array_with_shell_false():
    source = Path("scripts/model_required_bureau_c5_rehearsal.py").read_text(encoding="utf-8")
    assert "subprocess.Popen(" in source
    assert "shell=False" in source
    assert "shell=True" not in source
    assert "os.system(" not in source and "os.popen(" not in source
    assert '"stdin": subprocess.DEVNULL' in source
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


def _execution_fixture(*, process=None, http=None, port_allocator=None, directory=None):
    store = C5SharedStore()
    frame = build_frame()
    candidate = parse_candidate(frame)
    proofreader = proofread_candidate(candidate, frame)
    admission = admit_provider_candidate(
        store, frame=frame, candidate=candidate, proofreader=proofreader
    )
    issuer = C5EvidenceIssuer(now_callable, store)
    issued = mint_evidence(
        issuer,
        frame=frame,
        candidate=candidate,
        proofreader=proofreader,
        provider_admission_digest=admission,
    )
    controller = new_controller(
        store=store,
        process=process,
        http=http,
        port_allocator=port_allocator,
        directory=directory,
        ready_for_execute=True,
    )
    return controller, frame, candidate, proofreader, admission, issued


def _execute(controller, frame, candidate, proofreader, admission, issued, **overrides):
    values = {
        "approval": build_approval(),
        "evidence_reference_sha256": issued.record.reference_sha256,
        "candidate": candidate,
        "frame": frame,
        "proofreader": proofreader,
        "provider_admission_digest": admission,
        "target_nonce": TARGET_NONCE,
        "port": PORT,
        "artifact_sha256": EXPECTED_ARTIFACT_SHA256,
        "correlation_id": CORRELATION_ID,
        "idempotency_key": IDEMPOTENCY_KEY,
    }
    values.update(overrides)
    return controller.execute_recovery(**values)


def test_execution_rejects_attacker_candidate_frame_runbook_and_port_bindings():
    controller, frame, candidate, proofreader, admission, issued = _execution_fixture()
    alternate = replace(candidate, uncertainty=candidate.uncertainty + " Bounded note.")
    alternate_proof = proofread_candidate(alternate, frame)
    result = _execute(
        controller,
        frame,
        alternate,
        alternate_proof,
        admission,
        issued,
    )
    assert result["reason_code"] == "EVIDENCE_BINDING_MISMATCH"

    controller, frame, candidate, proofreader, admission, issued = _execution_fixture()
    result = _execute(
        controller,
        frame,
        candidate,
        proofreader,
        admission,
        issued,
        port=PORT + 1,
    )
    assert result["reason_code"] == "TARGET_DRIFT_REJECTED"

    controller, frame, candidate, proofreader, admission, issued = _execution_fixture()
    changed_frame = replace(frame, policy_digest="0" * 64, frame_digest="")
    changed_frame = replace(changed_frame, frame_digest=changed_frame.digest())
    result = _execute(
        controller,
        changed_frame,
        candidate,
        proofreader,
        admission,
        issued,
    )
    assert result["reason_code"] == "AUTHORITY_OR_FRAME_INVALID"

    controller, frame, candidate, proofreader, admission, issued = _execution_fixture()
    controller.store.evidence_records[issued.record.reference_sha256] = replace(
        issued.record, runbook_id="attacker-runbook"
    )
    result = _execute(
        controller,
        frame,
        candidate,
        proofreader,
        admission,
        issued,
    )
    assert result["reason_code"] == "SCOPE_EXPANSION_REJECTED"


def test_execution_cannot_skip_the_baseline_fault_and_recovery_port_sequence():
    store = C5SharedStore()
    frame = build_frame()
    candidate = parse_candidate(frame)
    proofreader = proofread_candidate(candidate, frame)
    admission = admit_provider_candidate(
        store, frame=frame, candidate=candidate, proofreader=proofreader
    )
    issuer = C5EvidenceIssuer(now_callable, store)
    issued = mint_evidence(
        issuer,
        frame=frame,
        candidate=candidate,
        proofreader=proofreader,
        provider_admission_digest=admission,
    )
    controller = new_controller(store=store)
    result = _execute(
        controller, frame, candidate, proofreader, admission, issued
    )
    assert result["reason_code"] == "CURRENT_BINDING_INVALID"
    assert controller.process.starts == 0


def test_fresh_process_absence_or_http_port_mismatch_rolls_back_without_success():
    process = FakeProcessObserver()
    process.alive_disposition = "absent"
    http = FakeHttpObserver()
    http.mode = "refused"
    controller, frame, candidate, proofreader, admission, issued = _execution_fixture(
        process=process, http=http
    )
    result = _execute(
        controller, frame, candidate, proofreader, admission, issued
    )
    assert result["result"] == "denied"
    assert result["reason_code"] == "LIVE_RECOVERY_ROLLBACK_VERIFIED"
    assert process.observation_calls >= 2
    assert process.any_running() is False

    controller, frame, candidate, proofreader, admission, issued = _execution_fixture()
    controller.http.generation = 2
    original_probe = controller.http.probe

    def wrong_port_probe(host, port, path):
        observation = original_probe(host, port, path)
        observation["body"]["port"] = port + 1
        return observation

    controller.http.probe = wrong_port_probe
    result = _execute(
        controller, frame, candidate, proofreader, admission, issued
    )
    assert result["result"] == "denied"
    assert result["reason_code"].startswith("LIVE_RECOVERY_ROLLBACK_")


def test_post_launch_observer_exceptions_are_terminal_and_contained_by_rollback():
    class RaisingProcess(FakeProcessObserver):
        def observe_process(self, handle):
            self.observation_calls += 1
            if self.starts:
                raise RuntimeError("observation failed")
            return super().observe_process(handle)

    process = RaisingProcess()
    http = FakeHttpObserver()
    http.mode = "refused"
    controller, frame, candidate, proofreader, admission, issued = _execution_fixture(
        process=process, http=http
    )
    result = _execute(
        controller, frame, candidate, proofreader, admission, issued
    )
    assert result["result"] == "denied"
    assert result["reason_code"] == "LIVE_RECOVERY_ROLLBACK_UNVERIFIED"
    assert process.any_running() is False
    assert controller.store.launch_state == "rollback_inconclusive"

    process = FakeProcessObserver()
    http = FakeHttpObserver()
    http.raise_on_probe = True
    controller, frame, candidate, proofreader, admission, issued = _execution_fixture(
        process=process, http=http
    )
    result = _execute(
        controller, frame, candidate, proofreader, admission, issued
    )
    assert result["result"] == "denied"
    assert result["reason_code"] == "LIVE_RECOVERY_ROLLBACK_VERIFIED"
    assert process.any_running() is False


def test_audit_failure_is_terminal_before_launch_and_consumes_one_use_evidence():
    class FailingAudit(list):
        def append(self, value):
            raise RuntimeError("audit write failed")

    process = FakeProcessObserver()
    controller, frame, candidate, proofreader, admission, issued = _execution_fixture(
        process=process
    )
    controller.store.attempt_audit = FailingAudit()
    result = _execute(
        controller, frame, candidate, proofreader, admission, issued
    )
    assert result["reason_code"] == "AUDIT_FAILED"
    assert result["evidence_consumed"] is True
    assert process.starts == 0
    assert controller.store.launch_state == "audit_failed"


@pytest.mark.parametrize(
    "failed_proof",
    ["process", "listener", "directory", "ledger", "capability"],
)
def test_cleanup_never_claims_verified_when_an_absence_proof_is_false(failed_proof):
    controller = new_controller()
    if failed_proof == "process":
        controller.process.any_running = lambda: True
    elif failed_proof == "listener":
        def occupied(_port):
            raise OSError(errno.EADDRINUSE, "exact port remains occupied")

        controller.port_allocator.reserve_exact = occupied
    elif failed_proof == "directory":
        controller.directory.remove_task_dir = lambda candidate: False
    elif failed_proof == "ledger":
        controller.store.provider_open_count = lambda: 1
    else:
        class Issued:
            state = "issued"

        class StickyEvidence(dict):
            def items(self):
                return []

            def values(self):
                return [Issued()]

        controller.store.evidence_records = StickyEvidence()
    receipt = controller.cleanup(correlation_id=CORRELATION_ID)
    assert receipt["result"] == "cleanup_inconclusive"


def test_real_adapter_contract_is_complete_pinned_and_uses_socket_inheritance():
    assert {"preflight", "start", "observe_process", "terminate", "any_running", "close"}.issubset(
        set(dir(ProcessAdapter))
    )
    assert {"reserve", "reserve_exact"}.issubset(set(dir(LoopbackPortAllocator)))
    assert {"prepare_exact_launch", "complete_handoff", "close"}.issubset(
        set(dir(PortReservation))
    )
    source = Path("scripts/model_required_bureau_c5_rehearsal.py").read_text()
    assert "EMR4_C5_INHERITED_SOCKET_FD" in source
    assert '"handle_list": [inherited_fd]' in source
    assert '"pass_fds"' in source
    assert "def resolve_python_executable()" in source
    assert "def resolve_target_module()" in source
    assert "repo_root" not in str(inspect.signature(build_launch_argv))


def test_live_marked_fake_adapters_produce_truthful_append_only_counts():
    process = FakeProcessObserver()
    http = FakeHttpObserver()
    from scripts.model_required_bureau_c5_acceptance import FakeDirectoryOps, FakePortAllocator

    port_allocator = FakePortAllocator()
    directory = FakeDirectoryOps()
    for adapter in (process, http, port_allocator, directory):
        adapter.is_live_capability = True
    controller, frame, candidate, proofreader, admission, issued = _execution_fixture(
        process=process,
        http=http,
        port_allocator=port_allocator,
        directory=directory,
    )
    result = _execute(
        controller, frame, candidate, proofreader, admission, issued
    )
    assert result["result"] == "live_development_recovery_verified"
    counts = result["operation_counters"]
    assert counts["directory_creates"] == 1
    assert counts["socket_binds"] == 1
    assert counts["port_allocations"] == 1
    assert counts["process_starts"] == 1
    assert counts["socket_connects"] == 1
    assert len(controller.store.operation_audit) == sum(counts.values())
    assert all(event["counter"] in counts for event in controller.store.operation_audit)
