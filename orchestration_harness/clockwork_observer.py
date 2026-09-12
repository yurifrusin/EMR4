"""Supervisor-owned capture of fixed reviewed local Python programs.

Call only from the trusted controller with its reviewed assignment and source
allowlist. Worker output cannot select a source, role, context or anchor. This is
an execution observer, not a sandbox for hostile same-user programs. Actual model
and provider adapters remain closed. The caller retains the final anchor in its
existing trusted checkpoint/receipt; this adapter does not create that authority.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import threading
import time

from . import clockwork_provenance as proof


def _regular(path, maximum):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        info = part.lstat()
        proof.need(not part.is_symlink() and not getattr(info, "st_file_attributes", 0) & 0x400,
                   "linked_capture_path")
    first = path.stat()
    proof.need(path.is_file() and first.st_size <= maximum, "capture_file_size")
    raw = path.read_bytes()
    last = path.stat()
    signature = lambda info: (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns)
    proof.need(signature(first) == signature(last), "capture_file_changed")
    return raw


def _write_new(path, raw):
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def _partial(directory, value):
    temporary = directory / "partial.next.json"
    _write_new(temporary, proof.canonical(value))
    os.replace(temporary, directory / "partial.json")


def _run(executable, source, packet, cwd, timeout, assignment, role):
    """Drain bounded pipes concurrently and retain only bounded output bytes."""
    proof.need(proof.sha(_regular(executable, 64 * 1024 * 1024)) == assignment["executable_sha256"],
               "executable_changed")
    worker = assignment["workers"][role]
    proof.need(type(source) is bytes and len(source) <= 8192
               and proof.sha(source) == worker["source_sha256"], "unreviewed_worker_source")
    try:
        program = source.decode("utf-8")
    except UnicodeError as error:
        raise proof.ProvenanceError("worker_source_encoding") from error
    proof.blob(packet)  # Check size before any process creation.
    environment = {"SYSTEMROOT": os.environ["SYSTEMROOT"]} if os.name == "nt" else {"LANG": "C.UTF-8"}
    started = time.time_ns()
    proof.need(assignment["created_ns"] <= started < assignment["not_after_ns"], "assignment_expired")
    timeout = min(timeout, (assignment["not_after_ns"] - started) / 1_000_000_000)
    argv = [str(executable), "-I", "-B", "-S", "-c", program]
    process = subprocess.Popen(argv,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=environment)
    output = {"stdout": bytearray(), "stderr": bytearray()}
    truncated = threading.Event()
    input_written = threading.Event()
    pipe_error = threading.Event()

    def terminate():
        try:
            process.kill()
        except ProcessLookupError:
            pass

    def drain(name, handle):
        try:
            while True:
                block = handle.read(min(8192, proof.MAX_BLOB + 1 - len(output[name])))
                if not block:
                    break
                output[name].extend(block)
                if len(output[name]) > proof.MAX_BLOB:
                    del output[name][proof.MAX_BLOB:]
                    truncated.set()
                    terminate()
                    break
        except (OSError, ValueError):
            pipe_error.set()
            terminate()
        finally:
            handle.close()

    def supply():
        try:
            written = process.stdin.write(packet)
            process.stdin.flush()
            if written == len(packet):
                input_written.set()
        except (BrokenPipeError, OSError):
            pipe_error.set()
        finally:
            try:
                process.stdin.close()
            except OSError:
                pipe_error.set()

    threads = [threading.Thread(target=drain, args=(name, getattr(process, name)), daemon=True)
               for name in ("stdout", "stderr")]
    threads.append(threading.Thread(target=supply, daemon=True))
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        terminate()
        process.wait(timeout=2)
    for thread in threads:
        thread.join(timeout=1)
    closed = all(not thread.is_alive() for thread in threads) and input_written.is_set() and not pipe_error.is_set()
    stopped = time.time_ns()
    proof.need(proof.sha(_regular(executable, 64 * 1024 * 1024)) == assignment["executable_sha256"],
               "executable_changed")
    return {"role": role, "run_id": role + "-" + str(process.pid) + "-" + str(started),
        "worker_id": worker["worker_id"], "principal_id": worker["principal_id"], "lineage_id": worker["lineage_id"],
        "source": proof.blob(source), "executable_sha256": assignment["executable_sha256"],
        "argv": argv, "environment": environment, "cwd": str(cwd),
        "pid": process.pid, "started_ns": started, "stopped_ns": stopped,
        "packet": proof.blob(packet), "stdout": proof.blob(bytes(output["stdout"])),
        "stderr": proof.blob(bytes(output["stderr"])), "exit_code": process.returncode,
        "timed_out": timed_out, "output_truncated": truncated.is_set(), "streams_closed": closed}


def capture_assignment(assignment, sources, *, executable, capture_directory, retain_anchor,
                       process_timeout_seconds=10):
    """Run once, seal a bundle, and ask the existing trusted controller to anchor it.

    retain_anchor must atomically retain the supplied exact bytes in the caller's
    trusted checkpoint/receipt and return their digest only after durable success.
    It is a trusted controller callback, never a function obtained from a worker.
    Existing capture directories are refused; interruption does not permit retry.
    """
    assignment = proof.document(proof.canonical(assignment))
    proof.validate_assignment(assignment)
    proof.need(not assignment["policy"]["live_model_required"], "live_model_provenance_unavailable")
    proof.need(type(sources) is dict and set(sources) == set(assignment["workers"]), "source_allowlist")
    proof.need(callable(retain_anchor) and type(process_timeout_seconds) in (int, float)
               and 0 < process_timeout_seconds <= 30, "capture_controller_required")
    executable = Path(executable).absolute()
    proof.need(proof.sha(_regular(executable, 64 * 1024 * 1024)) == assignment["executable_sha256"],
               "executable_changed")
    proof.need(proof.sha(_regular(Path(__file__), 256 * 1024)) == assignment["observer_source_sha256"],
               "observer_source_changed")
    for role, source in sources.items():
        proof.need(type(source) is bytes and len(source) <= 8192
                   and proof.sha(source) == assignment["workers"][role]["source_sha256"], "unreviewed_worker_source")
    directory = Path(capture_directory).absolute()
    for part in (directory.parent, *directory.parent.parents):
        info = part.lstat()
        proof.need(not part.is_symlink() and not getattr(info, "st_file_attributes", 0) & 0x400,
                   "linked_capture_path")
    directory.mkdir(exist_ok=False)
    partial = {"assignment": assignment, "observations": [], "complete": False, "next_role": "generator"}
    _partial(directory, partial)
    candidate = None
    for role in proof.ROLES:
        if role not in assignment["workers"]:
            continue
        partial["next_role"] = role
        _partial(directory, partial)
        cwd = directory / role
        cwd.mkdir()
        packet = proof.packet_for(assignment, role, candidate)
        observation = _run(executable, sources[role], packet, cwd, process_timeout_seconds, assignment, role)
        partial["observations"].append(observation)
        _partial(directory, partial)
        proof.need(observation["exit_code"] == 0 and not observation["timed_out"]
                   and not observation["output_truncated"] and observation["streams_closed"], "execution_incomplete")
        proof.need(proof.unblob(observation["stderr"]) == b"", "execution_stderr")
        result = proof._worker_artifact(proof.unblob(observation["stdout"]), role)
        if role == "generator":
            candidate = proof.unblob(result["candidate"])
            proof.need(len(candidate) <= 32768, "candidate_size")
        elif role == "verifier":
            proof.need(set(result["checks"]) == set(assignment["policy"]["required_checks"]), "required_checks_missing")
            proof.need(all(value == 0 for value in result["checks"].values()), "deterministic_check_failed")
    sealed = time.time_ns()
    proof.need(sealed < assignment["not_after_ns"], "assignment_expired")
    bundle = {"schema_version": proof.VERSION, "profile": proof.PROFILE, "assignment": assignment,
        "observations": partial["observations"], "candidate": proof.blob(candidate), "sealed_ns": sealed, "complete": True}
    bundle_raw = proof.canonical(bundle)
    anchor = {"schema_version": proof.ANCHOR_VERSION, "assignment_id": assignment["assignment_id"],
        "assignment_sha256": proof.sha(proof.canonical(assignment)), "bundle_sha256": proof.sha(bundle_raw),
        "observer_source_sha256": assignment["observer_source_sha256"],
        "controller_reference": assignment["controller_reference"], "scope_sha256": assignment["scope_sha256"],
        "sealed_ns": sealed, "profile": proof.PROFILE}
    anchor_raw = proof.canonical(anchor)
    # This validation checks composition, not anchor authenticity. Only the
    # independent controller retention below makes the capture replayable.
    proof.inspect_capture(bundle_raw, anchor_raw, expected_anchor_sha256=proof.sha(anchor_raw),
        expected_assignment_id=assignment["assignment_id"], expected_scope_sha256=assignment["scope_sha256"],
        expected_controller_reference=assignment["controller_reference"], now_ns=sealed)
    _write_new(directory / "bundle.json", bundle_raw)
    retained = retain_anchor(anchor_raw)
    proof.need(retained == proof.sha(anchor_raw), "controller_anchor_not_retained")
    return {"bundle_path": str(directory / "bundle.json"), "bundle_sha256": proof.sha(bundle_raw),
        "anchor_sha256": retained, "assignment_id": assignment["assignment_id"], "profile": proof.PROFILE,
        "execution_authorized": False, "integration_authorized": False, "usage_settlement_authorized": False}
