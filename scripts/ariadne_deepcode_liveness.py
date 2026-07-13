"""Observe Deep Code PTY progress without owning or terminating the worker."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration_harness.deepcode_artifact import parse_artifact_marker

SCHEMA_VERSION = "ariadne.deepcode_liveness.v1"
STATUSES = ("progressing", "idle_observed", "completed", "process_missing")
SIGNAL_NAMES = ("artifact", "git", "files", "processes", "receipt", "mailbox")


def _digest_bytes(chunks: Iterable[bytes]) -> str:
    digest = hashlib.sha256()
    for chunk in chunks:
        digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _digest_json(value: Any) -> str:
    return _digest_bytes((json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"),))


def _file_digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        with path.open("rb") as stream:
            return _digest_bytes(iter(lambda: stream.read(1024 * 1024), b""))
    except OSError:
        return None


def _relative_label(cwd: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(cwd.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _file_state(path: Path) -> dict[str, Any]:
    try:
        stat = path.stat()
    except FileNotFoundError:
        return {"exists": False}
    except OSError as error:
        return {"exists": False, "observation_error": type(error).__name__}
    return {
        "exists": True,
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "digest": _file_digest(path),
    }


def _artifact_state(path: Path, artifact_kind: str) -> dict[str, Any]:
    state = _file_state(path)
    state["valid_marker"] = False
    if not state["exists"]:
        return state
    try:
        body = path.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        state["observation_error"] = type(error).__name__
        return state
    marker = parse_artifact_marker(body, artifact_kind)
    state["valid_marker"] = marker["valid"]
    state["marker_reason"] = marker["reason"]
    return state


def _receipt_state(path: Path) -> dict[str, Any]:
    state = _file_state(path)
    state["status"] = None
    if not state["exists"]:
        return state
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state["status"] = "invalid"
        return state
    if isinstance(payload, dict) and isinstance(payload.get("status"), str):
        state["status"] = payload["status"]
    else:
        state["status"] = "invalid"
    return state


def _mailbox_state(outbox: Path) -> dict[str, Any]:
    if not outbox.is_dir():
        return {"exists": False, "event_count": 0, "event_fingerprint": _digest_json([])}
    events: list[dict[str, Any]] = []
    try:
        paths = sorted(path for path in outbox.iterdir() if path.is_file() and path.suffix == ".json")
    except OSError as error:
        return {
            "exists": True,
            "event_count": 0,
            "event_fingerprint": _digest_json([]),
            "observation_error": type(error).__name__,
        }
    for path in paths:
        state = _file_state(path)
        events.append({"name": path.name, "size": state.get("size"), "mtime_ns": state.get("mtime_ns"), "digest": state.get("digest")})
    return {
        "exists": True,
        "event_count": len(events),
        "event_fingerprint": _digest_json(events),
    }


def _run_text(command: list[str], cwd: Path) -> tuple[str | None, int | None]:
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    except (OSError, ValueError):
        return None, None
    if result.returncode != 0:
        return None, result.returncode
    return result.stdout, result.returncode


def _stream_command_digest(command: list[str], cwd: Path) -> tuple[str | None, int | None]:
    try:
        process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except (OSError, ValueError):
        return None, None
    assert process.stdout is not None
    digest = hashlib.sha256()
    for chunk in iter(lambda: process.stdout.read(1024 * 1024), b""):
        digest.update(chunk)
    return f"sha256:{digest.hexdigest()}", process.wait()


def _git_state(cwd: Path) -> dict[str, Any]:
    root, returncode = _run_text(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], cwd)
    if not root:
        return {"available": False, "return_code": returncode}
    head, head_code = _run_text(["git", "-C", str(cwd), "rev-parse", "HEAD"], cwd)
    status, status_code = _run_text(["git", "-C", str(cwd), "status", "--short", "--branch"], cwd)
    diff, diff_code = _stream_command_digest(["git", "-C", str(cwd), "diff", "--no-ext-diff", "--binary"], cwd)
    cached_diff, cached_code = _stream_command_digest(
        ["git", "-C", str(cwd), "diff", "--cached", "--no-ext-diff", "--binary"], cwd
    )
    return {
        "available": True,
        "root_label": _relative_label(cwd, Path(root.strip())),
        "head": head.strip() if head else None,
        "head_observation_code": head_code,
        "status_fingerprint": _digest_bytes(((status or "").encode("utf-8"),)),
        "status_observation_code": status_code,
        "diff_fingerprint": diff,
        "diff_observation_code": diff_code,
        "cached_diff_fingerprint": cached_diff,
        "cached_diff_observation_code": cached_code,
    }


def _process_state(pid: int) -> dict[str, Any]:
    state: dict[str, Any] = {"pid": pid, "present": False, "activity_available": False}
    if platform.system() == "Windows":
        process_query_limited_information = 0x1000
        still_active = 259
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.OpenProcess(process_query_limited_information, False, pid)
        if not handle:
            state["observation_error_code"] = ctypes.get_last_error()
            return state
        try:
            exit_code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                state["observation_error_code"] = ctypes.get_last_error()
                return state
            state["present"] = exit_code.value == still_active
            return state
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        state["present"] = True
    except ProcessLookupError:
        return state
    except PermissionError:
        state["present"] = True
        state["observation_error"] = "permission_denied"
    except OSError as error:
        state["observation_error"] = type(error).__name__

    if not state["present"]:
        return state
    output, returncode = _run_text(["ps", "-p", str(pid), "-o", "stat=,time="], Path.cwd())
    if output and returncode == 0:
        state["activity_available"] = True
        state["activity_fingerprint"] = _digest_bytes((output.strip().encode("utf-8"),))
    else:
        state["activity_observation_code"] = returncode
    return state


def capture_snapshot(
    cwd: Path,
    artifact: Path,
    receipt: Path,
    outbox: Path,
    *,
    artifact_kind: str = "decision",
    watched_files: Iterable[Path] = (),
    process_pids: Iterable[int] = (),
) -> dict[str, Any]:
    cwd = cwd.resolve()
    artifact = artifact if artifact.is_absolute() else cwd / artifact
    receipt = receipt if receipt.is_absolute() else cwd / receipt
    outbox = outbox if outbox.is_absolute() else cwd / outbox
    files: dict[str, Any] = {}
    for path in watched_files:
        resolved = path if path.is_absolute() else cwd / path
        files[_relative_label(cwd, resolved)] = _file_state(resolved)
    return {
        "schema_version": SCHEMA_VERSION,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "observed_at_epoch": time.time(),
        "artifact": _artifact_state(artifact, artifact_kind),
        "git": _git_state(cwd),
        "files": files,
        "processes": [_process_state(pid) for pid in process_pids],
        "receipt": _receipt_state(receipt),
        "mailbox": _mailbox_state(outbox),
    }


def _signal_value(snapshot: dict[str, Any], name: str) -> Any:
    return snapshot.get(name)


def classify_liveness(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    """Classify from observable changes; elapsed time is intentionally ignored."""
    if current.get("artifact", {}).get("valid_marker") is True:
        return {"status": "completed", "reason": "canonical_artifact_marker_observed", "changed_signals": []}

    current_processes = current.get("processes", [])
    if current_processes and not any(process.get("present") for process in current_processes):
        return {"status": "process_missing", "reason": "all_observed_processes_absent", "changed_signals": []}

    if previous is None:
        return {
            "status": "idle_observed",
            "reason": "baseline_established_without_comparable_previous_observation",
            "changed_signals": [],
        }

    changed = [
        name for name in SIGNAL_NAMES if _digest_json(_signal_value(previous, name)) != _digest_json(_signal_value(current, name))
    ]
    if changed:
        return {"status": "progressing", "reason": "observable_signals_changed", "changed_signals": changed}
    return {"status": "idle_observed", "reason": "no_observable_signal_change", "changed_signals": []}


def observe_liveness(
    cwd: Path,
    artifact: Path,
    receipt: Path,
    outbox: Path,
    *,
    previous: dict[str, Any] | None = None,
    artifact_kind: str = "decision",
    watched_files: Iterable[Path] = (),
    process_pids: Iterable[int] = (),
) -> dict[str, Any]:
    current = capture_snapshot(
        cwd,
        artifact,
        receipt,
        outbox,
        artifact_kind=artifact_kind,
        watched_files=watched_files,
        process_pids=process_pids,
    )
    classification = classify_liveness(previous, current)
    previous_epoch = previous.get("observed_at_epoch") if previous else None
    current_epoch = current["observed_at_epoch"]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": classification["status"],
        "reason": classification["reason"],
        "changed_signals": classification["changed_signals"],
        "observed_at": current["observed_at"],
        "elapsed_seconds_advisory": max(0.0, current_epoch - previous_epoch) if isinstance(previous_epoch, (int, float)) else None,
        "elapsed_time_used_for_classification": False,
        "process_termination_requested": False,
        "snapshot": current,
    }


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload.get("snapshot", payload)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Observe Deep Code progress without killing or owning its lifecycle.")
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--artifact-kind", choices=("decision", "completion"), default="decision")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--outbox", type=Path, required=True)
    parser.add_argument("--watch", type=Path, action="append", default=[], help="Relevant file to observe; repeatable")
    parser.add_argument("--process-pid", type=int, action="append", default=[], help="Supervisor/child PID to observe; repeatable")
    parser.add_argument("--previous", type=Path, help="Prior snapshot or observation JSON")
    parser.add_argument("--state", type=Path, help="Read prior state and write this observation here")
    parser.add_argument("--evidence", type=Path, help="Also write this observation JSON")
    args = parser.parse_args()
    try:
        previous_path = args.previous or args.state
        previous = _read_json(previous_path) if previous_path else None
        result = observe_liveness(
            args.cwd,
            args.artifact,
            args.receipt,
            args.outbox,
            previous=previous,
            artifact_kind=args.artifact_kind,
            watched_files=args.watch,
            process_pids=args.process_pid,
        )
        if args.state:
            _write_json(args.state, result)
        if args.evidence:
            _write_json(args.evidence, result)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "invalid_observation", "reason": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
