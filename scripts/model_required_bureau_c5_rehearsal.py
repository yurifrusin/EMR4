"""Bureau C5 fixed process adapter, argument-vector builder and controller.

This module implements the real capability adapters and controller logic for
the frozen C5 disposable live-development-recovery foundation.  The capability
adapters are implemented but remain inert in provider-free readiness and test
tranches.  The separately source-gated live runner may invoke them only after
the frozen deterministic and independent pre-execution gates pass.  All
ordinary tests and acceptance generation use provider-free fakes and exact
operation counters.

The real process adapter uses only an argument-array process API with
``shell=False`` semantics.  It resolves and hashes the exact repository
virtual-environment Python executable and frozen target module, includes
``-I``, passes host/port/nonce/generation as distinct arguments, supplies a
minimal explicit credential-free environment and retains the exact process
handle.  It never accepts caller executable/path/PID/environment/command
values, never discovers or enumerates processes, never invokes a shell, never
uses dynamic import/reflection, never inherits stdin and never terminates
anything except its owned handle.
"""

from __future__ import annotations

import hashlib
import errno
import json
import os
import re
import secrets
import subprocess  # nosec B404  # real adapter; never invoked in this tranche
import sys
import tempfile
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

from scripts.model_required_bureau_c5_contract import (
    C5SharedStore,
    ExecutionApproval,
    ForbiddenOperationCounters,
    FORWARD_RUNBOOK,
    HOST,
    IdempotencyRecord,
    PLAN_REVISION,
    PLAN_SHA256,
    PLAN_ENVIRONMENT,
    RecoveryDiagnosisCandidate,
    ROLLBACK_RUNBOOK,
    SystemAnatomyFrameSet,
    TARGET_ID,
    TARGET_KIND,
    ProofreaderDisposition,
    TargetRef,
    build_command_material_digest,
    build_provider_request_metadata,
    canonical_sha256,
    materialise_execution_approval,
    parse_recovery_candidate,
    proofread_candidate,
    sha256_hex,
    strict_json_loads,
    validate_execution_approval,
    validate_frame_semantics,
)

_HEX32_64_RE = re.compile(r"^[0-9a-f]{32,64}$")
_UUID36_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_OBSERVATION_ID_RE = re.compile(r"^obs-[a-z0-9-]+$")

SUPERSESSION_KEY = "synthetic.c5-recovery-target.recovery"
HEALTH_PATH = "/healthz"
GENERATION_BASELINE = 1
GENERATION_RECOVERED = 2
STATE_HEALTHY = "healthy"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TARGET_MODULE_PATH = REPOSITORY_ROOT / "scripts" / "model_required_bureau_c5_target.py"


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------------- #
# Fixed path resolution and argument-vector construction
# --------------------------------------------------------------------------- #

def resolve_python_executable() -> Path:
    """Resolve the exact interpreter already executing the C5 controller.

    ``sys.executable`` is process-owned rather than caller supplied.  Binding
    the child to that absolute path keeps the interpreter identity stable in a
    linked Git worktree, where the source root intentionally has no duplicate
    ``.venv`` directory.  The real adapter hashes this exact file during live
    preflight and verifies the same digest again before each launch.
    """
    if not isinstance(sys.executable, str) or not sys.executable:
        raise ValueError("active Python executable is unavailable")
    python = Path(sys.executable)
    if not python.is_absolute():
        raise ValueError("active Python executable is not absolute")
    python = python.absolute()
    if not python.is_file():
        raise ValueError("active Python executable is absent")
    return python


def resolve_target_module() -> Path:
    """Resolve the exact frozen C5 service module path."""
    return TARGET_MODULE_PATH


def _hash_file(path: Path) -> str:
    """Hash one internally resolved pinned file."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_launch_argv(
    *,
    port: int,
    nonce: str,
    generation: int,
) -> list[str]:
    """Build the fixed allowlisted argument vector.

    The function accepts only server-held ``port``/``nonce``/``generation``.
    It does **not** accept a caller executable, path, host,
    module or environment override.  It contains no shell or string command.
    """
    if not isinstance(port, int) or isinstance(port, bool) or port <= 0 or port > 65535:
        raise ValueError("port must be a valid OS-assigned server-held port")
    if not isinstance(nonce, str) or not _HEX32_64_RE.match(nonce):
        raise ValueError("nonce must be an opaque hexadecimal value")
    if generation not in (GENERATION_BASELINE, GENERATION_RECOVERED):
        raise ValueError("generation must be exactly 1 or 2")
    python = resolve_python_executable()
    target = resolve_target_module()
    return [
        str(python),
        "-I",
        str(target),
        "--host",
        HOST,
        "--port",
        str(port),
        "--nonce",
        nonce,
        "--generation",
        str(generation),
    ]


_SHELL_META = set("|&;<>()")


def validate_launch_argv(argv: Any) -> None:
    """Reject any caller override or shell/command string in an argument vector."""
    if not isinstance(argv, list) or len(argv) != 11:
        raise ValueError("argv must be the fixed 11-element argument vector")
    if not all(isinstance(item, str) for item in argv):
        raise ValueError("argv elements must be strings")
    python = resolve_python_executable()
    target = resolve_target_module()
    if argv[0] != str(python):
        raise ValueError("executable override rejected")
    if argv[1] != "-I":
        raise ValueError("isolated-mode flag missing")
    if argv[2] != str(target):
        raise ValueError("target module override rejected")
    if argv[3] != "--host" or argv[4] != HOST:
        raise ValueError("host override rejected")
    if argv[5] != "--port":
        raise ValueError("port flag missing")
    try:
        port = int(argv[6])
    except (TypeError, ValueError):
        raise ValueError("invalid port value")
    if port <= 0 or port > 65535:
        raise ValueError("invalid port value")
    if argv[7] != "--nonce":
        raise ValueError("nonce flag missing")
    if not _HEX32_64_RE.match(argv[8]):
        raise ValueError("nonce must be an opaque hexadecimal value")
    if argv[9] != "--generation":
        raise ValueError("generation flag missing")
    if argv[10] not in ("1", "2"):
        raise ValueError("generation must be exactly 1 or 2")
    for item in argv:
        if any(ch in _SHELL_META for ch in item):
            raise ValueError("shell metacharacter rejected in argument vector")


def build_minimal_environment() -> dict[str, str]:
    """Build a minimal explicit credential-free child environment.

    Only an explicit allowlist of benign system variables is copied; no
    provider/cloud/credential variable is ever inherited by the child.
    """
    allowlist = ("PATH", "SYSTEMROOT", "SYSTEMDRIVE", "TEMP", "TMP", "COMSPEC", "PATHEXT")
    blocked = ("GOOGLE", "CLOUD", "ADC", "CREDENTIAL", "TOKEN", "SECRET", "AWS", "AZURE", "KEY")
    env: dict[str, str] = {}
    for name in allowlist:
        value = os.environ.get(name)
        if value is not None:
            env[name] = value
    return {k: v for k, v in env.items() if not any(tok in k.upper() for tok in blocked)}


# --------------------------------------------------------------------------- #
# Real capability adapters (implemented, never invoked in this tranche)
# --------------------------------------------------------------------------- #

class OwnedProcessHandle:
    """The exact controller-owned child-process handle."""

    def __init__(
        self,
        proc: Any,
        argv: list[str],
        started_at: str,
        *,
        port: int,
        nonce: str,
        generation: int,
        artifact_sha256: str,
        python_executable_sha256: str,
    ) -> None:
        self._proc = proc
        self.argv = list(argv)
        self.started_at = started_at
        self.port = port
        self.nonce = nonce
        self.generation = generation
        self.artifact_sha256 = artifact_sha256
        self.python_executable_sha256 = python_executable_sha256
        self.closed = False

    @property
    def pid(self) -> int:
        return int(self._proc.pid)

    def poll(self) -> Optional[int]:
        return self._proc.poll()

    def terminate_owned(self) -> bool:
        """Terminate only this owned handle and prove exit."""
        if self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait(timeout=5)
        return self._proc.poll() is not None


class ProcessAdapter:
    """Argument-array process API with ``shell=False`` semantics.

    The real adapter is never invoked in this worker tranche; acceptance uses a
    provider-free fake process observer with exact operation counters.
    """

    is_live_capability = True

    def __init__(self) -> None:
        self.repo_root = REPOSITORY_ROOT
        self._owned_handles: dict[int, OwnedProcessHandle] = {}

    def preflight(
        self,
        *,
        expected_python_sha256: str,
        expected_target_sha256: str,
    ) -> dict[str, str]:
        python = resolve_python_executable()
        target = resolve_target_module().resolve()
        active_python = Path(sys.executable).absolute()
        if python != active_python:
            raise ValueError("python executable drifted from the active controller")
        if target != TARGET_MODULE_PATH.resolve():
            raise ValueError("target module escaped the pinned repository")
        if not python.is_file() or not target.is_file():
            raise ValueError("pinned executable or target is absent")
        python_sha256 = _hash_file(python)
        target_sha256 = _hash_file(target)
        if python_sha256 != expected_python_sha256:
            raise ValueError("python executable digest drift")
        if target_sha256 != expected_target_sha256:
            raise ValueError("target artifact digest drift")
        return {
            "python_executable_sha256": python_sha256,
            "target_artifact_sha256": target_sha256,
        }

    def start(
        self,
        argv: list[str],
        env: dict[str, str],
        *,
        expected_python_sha256: str,
        expected_target_sha256: str,
        reservation: Any = None,
    ) -> OwnedProcessHandle:
        validate_launch_argv(argv)
        self.preflight(
            expected_python_sha256=expected_python_sha256,
            expected_target_sha256=expected_target_sha256,
        )
        port = int(argv[6])
        nonce = argv[8]
        generation = int(argv[10])
        if not isinstance(reservation, PortReservation):
            raise ValueError("exact owned port reservation is required")
        inherited_fd = reservation.prepare_exact_launch(port=port, host=HOST)
        child_env = dict(env)
        child_env["EMR4_C5_INHERITED_SOCKET_FD"] = str(inherited_fd)
        popen_options: dict[str, Any] = {
            "shell": False,
            "env": child_env,
            "cwd": str(self.repo_root),
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "close_fds": True,
        }
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.lpAttributeList = {"handle_list": [inherited_fd]}
            popen_options["startupinfo"] = startupinfo
        else:
            popen_options["pass_fds"] = (inherited_fd,)
        proc = None
        try:
            proc = subprocess.Popen(  # nosec B603  # fixed argv, shell=False
                argv,
                **popen_options,
            )
            reservation.complete_handoff()
        except Exception:
            reservation.close()
            if proc is not None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
            raise
        handle = OwnedProcessHandle(
            proc,
            argv,
            _format_time(datetime.now(timezone.utc)),
            port=port,
            nonce=nonce,
            generation=generation,
            artifact_sha256=expected_target_sha256,
            python_executable_sha256=expected_python_sha256,
        )
        self._owned_handles[id(handle)] = handle
        return handle

    def _require_owned(self, handle: Any) -> OwnedProcessHandle:
        if not isinstance(handle, OwnedProcessHandle) or self._owned_handles.get(id(handle)) is not handle:
            raise ValueError("process handle is not controller-owned")
        return handle

    def observe_process(self, handle: Any) -> dict[str, Any]:
        owned = self._require_owned(handle)
        return {
            "observation_id": "obs-process-" + secrets.token_hex(8),
            "disposition": "alive" if owned.poll() is None else "absent",
            "pid": owned.pid,
            "owned": True,
            "argv_sha256": canonical_sha256(owned.argv),
            "port": owned.port,
            "generation": owned.generation,
            "nonce": owned.nonce,
            "artifact_sha256": owned.artifact_sha256,
            "python_executable_sha256": owned.python_executable_sha256,
        }

    def terminate(self, handle: Any) -> bool:
        return self._require_owned(handle).terminate_owned()

    def any_running(self) -> bool:
        return any(handle.poll() is None for handle in self._owned_handles.values())

    def close(self, handle: Any) -> None:
        owned = self._require_owned(handle)
        if owned.poll() is None:
            raise ValueError("cannot close a running owned process handle")
        for stream in (owned._proc.stdout, owned._proc.stderr):
            if stream is not None:
                stream.close()
        owned.closed = True
        self._owned_handles.pop(id(owned), None)


class HttpReadbackProbe:
    """Loopback HTTP health readback probe (real; never invoked in this tranche)."""

    is_live_capability = True

    def probe(self, host: str, port: int, path: str) -> dict[str, Any]:
        if host != HOST or path != HEALTH_PATH:
            raise ValueError("HTTP probe scope drift")
        if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
            raise ValueError("HTTP probe port drift")
        import http.client

        conn = http.client.HTTPConnection(host, port, timeout=1)
        try:
            conn.request("GET", path)
            response = conn.getresponse()
            body = response.read().decode("utf-8")
            return {
                "observation_id": "obs-http-" + secrets.token_hex(8),
                "status": int(response.status),
                "body": body,
                "host": host,
                "port": port,
                "path": path,
            }
        except ConnectionRefusedError:
            return {
                "observation_id": "obs-http-" + secrets.token_hex(8),
                "status": "connection_refused",
                "host": host,
                "port": port,
                "path": path,
            }
        except ConnectionResetError:
            return {
                "observation_id": "obs-http-" + secrets.token_hex(8),
                "status": "connection_reset",
                "host": host,
                "port": port,
                "path": path,
            }
        except TimeoutError:
            return {
                "observation_id": "obs-http-" + secrets.token_hex(8),
                "status": "connection_timeout",
                "host": host,
                "port": port,
                "path": path,
            }
        finally:
            conn.close()

    def probe_until_healthy(
        self,
        host: str,
        port: int,
        path: str,
        *,
        deadline_seconds: float = 2.0,
    ) -> dict[str, Any]:
        """Retry only connection-refused while an exact owned child starts.

        Any response, scope error or other transport error returns or raises
        immediately.  The bounded wait never changes the target, port or
        request and is not used for post-fault absence or cleanup proofs.
        """
        if deadline_seconds <= 0 or deadline_seconds > 5:
            raise ValueError("health readiness deadline drift")
        deadline = time.monotonic() + deadline_seconds
        attempts = 0
        while True:
            observation = self.probe(host, port, path)
            attempts += 1
            if observation.get("status") != "connection_refused":
                return {**observation, "probe_attempts": attempts}
            if time.monotonic() >= deadline:
                return {**observation, "probe_attempts": attempts}
            time.sleep(0.025)

    def any_listener(self, *, port: int) -> bool:
        return self.probe(HOST, port, HEALTH_PATH).get("status") != "connection_refused"


class PortReservation:
    """Controller-held loopback reservation released only inside exact start."""

    def __init__(
        self,
        sock: Any,
        *,
        exclusive_address_use: bool = False,
        bind_attempts: int = 1,
    ) -> None:
        self._socket = sock
        self.host = HOST
        self.port = int(sock.getsockname()[1])
        self.exclusive_address_use = exclusive_address_use
        self.bind_attempts = bind_attempts
        self.released = False
        self.prepared = False

    def prepare_exact_launch(self, *, port: int, host: str) -> int:
        if self.released or self.prepared or port != self.port or host != self.host:
            raise ValueError("port reservation handoff drift")
        self._socket.listen(1)
        self._socket.set_inheritable(True)
        self.prepared = True
        return int(self._socket.fileno())

    def complete_handoff(self) -> None:
        if self.released or not self.prepared:
            raise ValueError("port reservation was not prepared for handoff")
        self._socket.close()
        self.released = True

    def close(self) -> None:
        if not self.released:
            self._socket.close()
            self.released = True


class LoopbackPortAllocator:
    """OS-assigned ephemeral loopback port allocator (real; never invoked here)."""

    is_live_capability = True

    @staticmethod
    def _new_socket() -> tuple[Any, bool]:
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        exclusive_address_use = False
        if os.name == "nt":
            if not hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                sock.close()
                raise RuntimeError("Windows exclusive-address control is unavailable")
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            exclusive_address_use = True
        return sock, exclusive_address_use

    def reserve(self) -> PortReservation:
        sock, exclusive_address_use = self._new_socket()
        try:
            sock.bind((HOST, 0))
            return PortReservation(
                sock,
                exclusive_address_use=exclusive_address_use,
            )
        except Exception:
            sock.close()
            raise

    def reserve_exact(self, port: int) -> PortReservation:
        if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
            raise ValueError("exact port reservation drift")
        sock, exclusive_address_use = self._new_socket()
        try:
            sock.bind((HOST, port))
            return PortReservation(
                sock,
                exclusive_address_use=exclusive_address_use,
            )
        except Exception:
            sock.close()
            raise

    def reserve_exact_until_owned(
        self,
        port: int,
        *,
        deadline_seconds: float = 2.0,
    ) -> PortReservation:
        """Reacquire and retain the exact port without address sharing.

        A successful bind is the absence proof.  On Windows every candidate
        socket has ``SO_EXCLUSIVEADDRUSE`` set before bind; ``SO_REUSEADDR`` is
        never used.  Only address-in-use is retried, covering the bounded TCP
        teardown interval after exact child termination.  Any other socket
        error fails immediately.
        """
        if deadline_seconds <= 0 or deadline_seconds > 5:
            raise ValueError("exact-port reacquisition deadline drift")
        deadline = time.monotonic() + deadline_seconds
        attempts = 0
        while True:
            attempts += 1
            try:
                reservation = self.reserve_exact(port)
                reservation.bind_attempts = attempts
                return reservation
            except OSError as exc:
                exc.bind_attempts = attempts
                address_in_use = exc.errno == errno.EADDRINUSE or getattr(
                    exc, "winerror", None
                ) == 10048
                if not address_in_use or time.monotonic() >= deadline:
                    raise
                time.sleep(0.025)


class TaskDirectoryOps:
    """Owned task-directory lifecycle (real; never invoked in this tranche)."""

    is_live_capability = True

    def __init__(self) -> None:
        self._owned_path: Optional[Path] = None
        self._marker_name: Optional[str] = None
        self._metadata_name = "launch-metadata.json"

    def create_task_dir(self) -> str:
        if self._owned_path is not None:
            raise ValueError("task directory already exists")
        temp_root = Path(tempfile.gettempdir()).resolve()
        repository_root = REPOSITORY_ROOT.resolve()
        if (
            temp_root in {repository_root, repository_root.parent, Path(temp_root.anchor)}
            or repository_root in temp_root.parents
        ):
            raise ValueError("OS temporary root overlaps a protected workspace path")
        path = Path(tempfile.mkdtemp(prefix="emr4-c5-", dir=str(temp_root))).resolve()
        if path.parent != temp_root:
            raise ValueError("task directory escaped the validated OS temporary root")
        marker_name = ".c5-owned-" + secrets.token_hex(16)
        (path / marker_name).write_text("c5-owned\n", encoding="utf-8", newline="\n")
        self._owned_path = path
        self._marker_name = marker_name
        return str(path)

    def materialise_launch_metadata(self, candidate: Any, metadata: dict[str, Any]) -> str:
        if not self.validate_owned_path(candidate):
            raise ValueError("launch metadata path is not the owned task directory")
        expected_keys = {
            "schema_version",
            "host",
            "port",
            "target_nonce_sha256",
            "python_executable_sha256",
            "target_artifact_sha256",
        }
        if set(metadata) != expected_keys:
            raise ValueError("launch metadata shape drift")
        metadata_path = self._owned_path / self._metadata_name
        metadata_path.write_text(
            json.dumps(metadata, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return str(metadata_path)

    def validate_owned_path(self, candidate: Any) -> bool:
        if self._owned_path is None or self._marker_name is None:
            return False
        candidate_path = Path(candidate).resolve()
        if candidate_path != self._owned_path:
            return False
        if candidate_path in {REPOSITORY_ROOT.resolve(), REPOSITORY_ROOT.parent.resolve(), Path(candidate_path.anchor)}:
            return False
        marker = candidate_path / self._marker_name
        return marker.is_file() and marker.read_text(encoding="utf-8") == "c5-owned\n"

    def remove_task_dir(self, candidate: Any) -> bool:
        if not self.validate_owned_path(candidate):
            raise ValueError("cleanup path is not an owned task directory")
        path = Path(candidate).resolve()
        metadata = path / self._metadata_name
        if metadata.exists():
            metadata.unlink()
        marker = path / (self._marker_name or "")
        marker.unlink()
        path.rmdir()
        self._owned_path = None
        self._marker_name = None
        return not path.exists()


# --------------------------------------------------------------------------- #
# Controller logic (one shared store/critical section)
# --------------------------------------------------------------------------- #

OCCUPIED_LABEL = "occupied_authored_synthetic_disposable_live_development_recovery"
ATTEMPT_RECEIPT_SCHEMA = "emr4.live_recovery_attempt_receipt.v1"
CLEANUP_SCHEMA = "emr4.cleanup_receipt.v1"


@dataclass
class LiveRecoveryController:
    """Task-owned controller state machine using injected observer fakes.

    In this worker tranche the injected ``process``/``http``/``port_allocator``/
    ``directory``/``ledger`` objects are always provider-free fakes with exact
    operation counters; the real capability adapters are never invoked.
    """

    store: C5SharedStore
    process: Any
    http: Any
    port_allocator: Any
    directory: Any
    now: Callable[[], datetime]
    python_executable_sha256: str
    _counters: ForbiddenOperationCounters = ForbiddenOperationCounters()
    _last_handle: Any = None
    _last_port: Optional[int] = None
    _last_reservation: Any = None
    _task_directory_path: Optional[str] = None

    @property
    def operation_counters(self) -> dict[str, int]:
        counters = self._counters.to_dict()
        with self.store.transaction_lock:
            for event in self.store.operation_audit:
                name = event.get("counter")
                if name in counters:
                    counters[name] += 1
        return counters

    @property
    def attempt_audit_records(self) -> list[dict[str, Any]]:
        with self.store.transaction_lock:
            return list(self.store.attempt_audit)

    # -- helpers ------------------------------------------------------------ #

    def _record_operation(self, adapter: Any, counter: str, outcome: str) -> None:
        if getattr(adapter, "is_live_capability", False):
            with self.store.transaction_lock:
                self.store.operation_audit.append(
                    {
                        "counter": counter,
                        "outcome": outcome,
                        "recorded_at": _format_time(self.now()),
                    }
                )

    def _record_http_observation(self, observation: dict[str, Any]) -> None:
        attempts = observation.get("probe_attempts", 1)
        if (
            not isinstance(attempts, int)
            or isinstance(attempts, bool)
            or not 1 <= attempts <= 128
        ):
            raise ValueError("HTTP probe attempt accounting drift")
        outcome = str(observation.get("status"))
        for _ in range(attempts):
            self._record_operation(self.http, "socket_connects", outcome)

    def _acquire_exact_absence_reservation(self, port: int) -> Any:
        acquire = getattr(self.port_allocator, "reserve_exact_until_owned", None)
        try:
            reservation = (
                acquire(port)
                if callable(acquire)
                else self.port_allocator.reserve_exact(port)
            )
        except OSError as exc:
            attempts = getattr(exc, "bind_attempts", 1)
            if (
                not isinstance(attempts, int)
                or isinstance(attempts, bool)
                or not 1 <= attempts <= 256
            ):
                attempts = 1
            for _ in range(attempts):
                self._record_operation(
                    self.port_allocator,
                    "socket_binds",
                    "exact_absence_bind_failed",
                )
            raise
        if (
            reservation.host != HOST
            or reservation.port != port
            or reservation.released
            or reservation.prepared
        ):
            reservation.close()
            raise ValueError("exact-port absence reservation drift")
        if (
            os.name == "nt"
            and getattr(self.port_allocator, "is_live_capability", False)
            and getattr(reservation, "exclusive_address_use", False) is not True
        ):
            reservation.close()
            raise ValueError("Windows exact-port reservation is not exclusive")
        attempts = getattr(reservation, "bind_attempts", 1)
        if (
            not isinstance(attempts, int)
            or isinstance(attempts, bool)
            or not 1 <= attempts <= 256
        ):
            reservation.close()
            raise ValueError("exact-port bind-attempt accounting drift")
        for attempt in range(1, attempts + 1):
            self._record_operation(
                self.port_allocator,
                "socket_binds",
                (
                    "exact_absence_bound"
                    if attempt == attempts
                    else "exact_absence_address_in_use"
                ),
            )
        self._record_operation(
            self.port_allocator,
            "port_allocations",
            "exact_absence_owned",
        )
        return reservation

    def _denial(
        self,
        reason_code: str,
        correlation_id: str,
        issued_at: str,
        counters: dict[str, int],
        *,
        rollback_invoked: bool = False,
        rollback_verified: Optional[bool] = None,
        evidence_consumed: bool = False,
    ) -> dict[str, Any]:
        return {
            "schema_version": "emr4.live_recovery_denial.v1",
            "evidence_label": OCCUPIED_LABEL,
            "result": "denied",
            "reason_code": reason_code,
            "correlation_digest": sha256_hex(correlation_id.encode("utf-8")),
            "rollback": {"invoked": rollback_invoked, "verified": rollback_verified},
            "evidence_consumed": evidence_consumed,
            "operation_counters": counters,
            "issued_at": issued_at,
        }

    @staticmethod
    def _parse_health_body(http_observation: dict[str, Any]) -> Optional[dict[str, Any]]:
        body = http_observation.get("body")
        if isinstance(body, dict):
            return body
        if isinstance(body, str):
            try:
                return strict_json_loads(body)
            except ValueError:
                return None
        return None

    def _matches_health(
        self,
        http_observation: dict[str, Any],
        *,
        port: int,
        nonce: str,
        generation: int,
        artifact_sha256: str,
    ) -> bool:
        if http_observation.get("status") != 200:
            return False
        if (
            http_observation.get("host") != HOST
            or http_observation.get("port") != port
            or http_observation.get("path") != HEALTH_PATH
        ):
            return False
        body = self._parse_health_body(http_observation)
        if body is None:
            return False
        if set(body) != {
            "schema_version",
            "environment",
            "kind",
            "target_id",
            "host",
            "port",
            "nonce",
            "generation",
            "artifact_sha256",
            "state",
        }:
            return False
        return (
            body.get("schema_version") == "emr4.c5_health_body.v1"
            and body.get("environment") == PLAN_ENVIRONMENT
            and body.get("kind") == TARGET_KIND
            and body.get("target_id") == TARGET_ID
            and body.get("host") == HOST
            and body.get("port") == port
            and body.get("generation") == generation
            and body.get("nonce") == nonce
            and body.get("artifact_sha256") == artifact_sha256
            and body.get("state") == STATE_HEALTHY
        )

    def _fingerprint(self, *, approval, evidence_reference_sha256, candidate, frame, proofreader, provider_admission_digest, target_nonce, port, artifact_sha256, correlation_id) -> str:
        return canonical_sha256(
            {
                "approval_id": approval.approval_id,
                "approval_sha256": approval.digest(),
                "evidence_reference_sha256": evidence_reference_sha256,
                "candidate_digest": candidate.digest(),
                "frame_digest": frame.frame_digest,
                "proofreader_digest": proofreader.digest(),
                "provider_admission_digest": provider_admission_digest,
                "target_nonce": target_nonce,
                "port": port,
                "generation": GENERATION_RECOVERED,
                "artifact_sha256": artifact_sha256,
                "python_executable_sha256": self.python_executable_sha256,
                "correlation_id": correlation_id,
            }
        )

    # -- state-machine steps ------------------------------------------------ #

    def prepare_runtime(
        self,
        *,
        target_nonce: str,
        artifact_sha256: str,
    ) -> dict[str, Any]:
        """Create the exact owned directory and race-free port reservation.

        No caller path, host or port is accepted. The OS-selected port remains
        bound to the owned socket until it is inherited by the exact child.
        """
        if self._task_directory_path is not None or self._last_reservation is not None:
            raise ValueError("runtime resources are already prepared")
        if not _HEX32_64_RE.match(target_nonce):
            raise ValueError("target nonce drift")
        if not _SHA256_RE.match(artifact_sha256):
            raise ValueError("target artifact digest drift")
        task_path = self.directory.create_task_dir()
        self._record_operation(self.directory, "directory_creates", "created")
        reservation = None
        try:
            if not self.directory.validate_owned_path(task_path):
                raise ValueError("created task directory ownership could not be proved")
            reservation = self.port_allocator.reserve()
            self._record_operation(self.port_allocator, "socket_binds", "bound")
            self._record_operation(self.port_allocator, "port_allocations", "allocated")
            if reservation.host != HOST or not 1 <= reservation.port <= 65535:
                raise ValueError("port reservation scope drift")
            metadata = {
                "schema_version": "emr4.c5_launch_metadata.v1",
                "host": HOST,
                "port": reservation.port,
                "target_nonce_sha256": sha256_hex(target_nonce.encode("utf-8")),
                "python_executable_sha256": self.python_executable_sha256,
                "target_artifact_sha256": artifact_sha256,
            }
            self.directory.materialise_launch_metadata(task_path, metadata)
        except Exception:
            try:
                if reservation is not None:
                    reservation.close()
                if self.directory.validate_owned_path(task_path):
                    self.directory.remove_task_dir(task_path)
                    self._record_operation(
                        self.directory, "directory_removals", "removed"
                    )
            finally:
                self._task_directory_path = None
            raise
        self._task_directory_path = task_path
        self._last_reservation = reservation
        self._last_port = reservation.port
        self.store.launch_state = "runtime_prepared"
        return {"task_directory": task_path, "port": reservation.port}

    def run_baseline(self, *, port: int, nonce: str, artifact_sha256: str) -> tuple[Any, bool]:
        """Start generation 1 and prove baseline by process and HTTP agreement."""
        if self.store.launch_state != "runtime_prepared":
            raise ValueError("baseline is out of sequence")
        if self._last_reservation is None or port != self._last_port:
            raise ValueError("baseline port is not the server-held reservation")
        argv = build_launch_argv(
            port=port, nonce=nonce, generation=GENERATION_BASELINE
        )
        self.process.preflight(
            expected_python_sha256=self.python_executable_sha256,
            expected_target_sha256=artifact_sha256,
        )
        handle = None
        try:
            handle = self.process.start(
                argv,
                build_minimal_environment(),
                expected_python_sha256=self.python_executable_sha256,
                expected_target_sha256=artifact_sha256,
                reservation=self._last_reservation,
            )
            self._last_handle = handle
            self._last_port = port
            self._record_operation(self.process, "process_starts", "started")
            proc_disposition = self.process.observe_process(handle).get("disposition")
            readiness_probe = getattr(self.http, "probe_until_healthy", None)
            http_observation = (
                readiness_probe(HOST, port, HEALTH_PATH)
                if callable(readiness_probe)
                else self.http.probe(HOST, port, HEALTH_PATH)
            )
            self._record_http_observation(http_observation)
            healthy = proc_disposition == "alive" and self._matches_health(
                http_observation,
                port=port,
                nonce=nonce,
                generation=GENERATION_BASELINE,
                artifact_sha256=artifact_sha256,
            )
        except Exception:
            if handle is None:
                self.store.launch_state = "baseline_launch_failed"
                raise
            healthy = False
        if not healthy and handle is not None:
            try:
                stopped = self.process.terminate(handle)
                self._record_operation(
                    self.process,
                    "process_stops",
                    "stopped" if stopped else "failed",
                )
            except Exception:
                self.store.cleanup_complete = False
        self.store.launch_state = "baseline_verified" if healthy else "baseline_failed"
        return handle, healthy

    def inject_fault(self, handle: Any) -> bool:
        """Terminate the exact controller-owned child handle."""
        if self.store.launch_state != "baseline_verified" or handle is not self._last_handle:
            raise ValueError("fault injection is out of sequence or handle-substituted")
        stopped = self.process.terminate(handle)
        self._record_operation(self.process, "process_stops", "stopped" if stopped else "failed")
        self.store.launch_state = "fault_injected" if stopped else "fault_failed"
        return stopped

    def post_fault_verify(self, handle: Any, *, port: int) -> bool:
        """Prove process absence and atomically reacquire the exact port."""
        if (
            self.store.launch_state != "fault_injected"
            or handle is not self._last_handle
            or port != self._last_port
        ):
            raise ValueError("post-fault verification is out of sequence")
        proc_disposition = self.process.observe_process(handle).get("disposition")
        reservation = None
        if proc_disposition == "absent":
            try:
                reservation = self._acquire_exact_absence_reservation(port)
            except Exception:
                reservation = None
        verified = reservation is not None
        if verified:
            self._last_reservation = reservation
        self.store.launch_state = "post_fault_verified" if verified else "post_fault_failed"
        return verified

    def reserve_recovery_port(self) -> int:
        """Reacquire the exact baseline port and hold it until generation 2."""
        if self.store.launch_state != "post_fault_verified":
            raise ValueError("recovery port reservation is out of sequence")
        if self._last_port is None:
            raise ValueError("baseline port is absent")
        if self._last_handle is None:
            raise ValueError("baseline handle is absent")
        if self.process.observe_process(self._last_handle).get("disposition") != "absent":
            raise ValueError("baseline process is not absent")
        baseline_handle = self._last_handle
        reservation = self._last_reservation
        if (
            reservation is None
            or reservation.host != HOST
            or reservation.port != self._last_port
            or reservation.released
            or reservation.prepared
        ):
            raise ValueError("recovery port reservation drift")
        close = getattr(self.process, "close", None)
        if callable(close):
            try:
                close(baseline_handle)
            except Exception:
                reservation.close()
                raise
        self._last_handle = None
        self.store.launch_state = "recovery_port_reserved"
        return reservation.port

    def reserve_provider_ledger(self, *, correlation_id: str, frame_digest: str) -> dict[str, Any]:
        """Record provider ledger/reservation state without making a provider call."""
        state = self.store.reserve_provider_attempt(
            correlation_id=correlation_id,
            request_metadata=build_provider_request_metadata(),
            frame_digest=frame_digest,
        )
        return {
            "correlation_id": state.correlation_id,
            "request_digest": state.request_digest,
            "frame_digest": state.frame_digest,
            "state": state.state,
        }

    def admit_candidate(self, raw: Any, frame: SystemAnatomyFrameSet) -> dict[str, Any]:
        """Parse and proofread a closed candidate; return a proofreader disposition."""
        candidate, parse_denial = parse_recovery_candidate(raw, _format_time(self.now()))
        if parse_denial is not None:
            return parse_denial.to_dict()
        if candidate is None:
            raise ValueError("candidate parse returned neither a candidate nor a denial")
        return proofread_candidate(candidate, frame).to_dict()

    def materialise_approval(self, *, approval_id: str, expires_at: str) -> ExecutionApproval:
        return materialise_execution_approval(
            approval_id=approval_id,
            plan_sha256=PLAN_SHA256,
            plan_revision=PLAN_REVISION,
            expires_at=expires_at,
        )

    # -- the fixed execute/readback/rollback critical section --------------- #

    def execute_recovery(
        self,
        *,
        approval: ExecutionApproval,
        evidence_reference_sha256: str,
        candidate: RecoveryDiagnosisCandidate,
        frame: SystemAnatomyFrameSet,
        proofreader: Any,
        provider_admission_digest: str,
        target_nonce: str,
        port: int,
        artifact_sha256: str,
        correlation_id: str,
        idempotency_key: str,
        fault: Optional[str] = None,
    ) -> dict[str, Any]:
        with self.store.transaction_lock:
            now_iso = _format_time(self.now())
            if not isinstance(correlation_id, str) or not _UUID36_RE.match(correlation_id):
                correlation_id = "00000000-0000-4000-8000-000000000000"
                return self._denial(
                    "SCHEMA_REJECTED", correlation_id, now_iso, self.operation_counters
                )
            if (
                not isinstance(approval, ExecutionApproval)
                or not isinstance(frame, SystemAnatomyFrameSet)
                or not isinstance(candidate, RecoveryDiagnosisCandidate)
                or not isinstance(proofreader, ProofreaderDisposition)
                or not isinstance(evidence_reference_sha256, str)
                or not _SHA256_RE.match(evidence_reference_sha256)
                or not isinstance(provider_admission_digest, str)
                or not _SHA256_RE.match(provider_admission_digest)
                or not isinstance(target_nonce, str)
                or not _HEX32_64_RE.match(target_nonce)
                or not isinstance(port, int)
                or isinstance(port, bool)
                or not 1 <= port <= 65535
                or not isinstance(artifact_sha256, str)
                or not _SHA256_RE.match(artifact_sha256)
                or not isinstance(idempotency_key, str)
                or not _UUID36_RE.match(idempotency_key)
                or fault not in {None, "launch_failed", "audit_failed", "readback_failed"}
            ):
                return self._denial(
                    "SCHEMA_REJECTED", correlation_id, now_iso, self.operation_counters
                )
            fingerprint = self._fingerprint(
                approval=approval,
                evidence_reference_sha256=evidence_reference_sha256,
                candidate=candidate,
                frame=frame,
                proofreader=proofreader,
                provider_admission_digest=provider_admission_digest,
                target_nonce=target_nonce,
                port=port,
                artifact_sha256=artifact_sha256,
                correlation_id=correlation_id,
            )

            existing = self.store.idempotency_records.get(idempotency_key)
            if existing is not None:
                if existing.fingerprint != fingerprint:
                    return self._denial("IDEMPOTENCY_CONFLICT", correlation_id, now_iso, self.operation_counters)
                if existing.terminal_receipt is None:
                    return self._denial("IDEMPOTENCY_IN_PROGRESS", correlation_id, now_iso, self.operation_counters)
                return existing.terminal_receipt

            try:
                validate_execution_approval(approval, now=self.now())
                validate_frame_semantics(frame, now=self.now())
            except ValueError:
                return self._denial("AUTHORITY_OR_FRAME_INVALID", correlation_id, now_iso, self.operation_counters)
            expected_proofreader = proofread_candidate(candidate, frame)
            if (
                proofreader != expected_proofreader
                or proofreader.admitted is not True
                or proofreader.reason_codes
                or proofreader.correction_ticket is not None
                or not all(proofreader.grounding.values())
            ):
                return self._denial("PROOFREADER_REJECTED", correlation_id, now_iso, self.operation_counters)

            record = self.store.evidence_records.get(evidence_reference_sha256)
            if record is None:
                return self._denial("EXECUTION_EVIDENCE_INVALID", correlation_id, now_iso, self.operation_counters)
            if record.state != "issued":
                return self._denial("EXECUTION_EVIDENCE_REPLAY", correlation_id, now_iso, self.operation_counters)
            if record.approval_id != approval.approval_id or record.approval_sha256 != approval.digest():
                return self._denial("AUTHORITY_MISMATCH", correlation_id, now_iso, self.operation_counters)
            if record.target != TargetRef.frozen() or record.runbook_id != FORWARD_RUNBOOK:
                return self._denial("SCOPE_EXPANSION_REJECTED", correlation_id, now_iso, self.operation_counters)
            if record.rollback_runbook_id != ROLLBACK_RUNBOOK:
                return self._denial("UNKNOWN_ROLLBACK", correlation_id, now_iso, self.operation_counters)
            if (
                record.generation != GENERATION_RECOVERED
                or record.artifact_sha256 != artifact_sha256
                or record.port != port
                or record.python_executable_sha256 != self.python_executable_sha256
            ):
                return self._denial("TARGET_DRIFT_REJECTED", correlation_id, now_iso, self.operation_counters)
            if record.target_nonce != target_nonce:
                return self._denial("NONCE_MISMATCH", correlation_id, now_iso, self.operation_counters)
            if (
                record.frame_digest != frame.frame_digest
                or record.candidate_digest != candidate.digest()
                or record.proofreader_digest != proofreader.digest()
                or record.provider_admission_digest != provider_admission_digest
                or record.correlation_id != correlation_id
            ):
                return self._denial("EVIDENCE_BINDING_MISMATCH", correlation_id, now_iso, self.operation_counters)
            command_material_sha256 = build_command_material_digest(
                approval=approval,
                port=port,
                target_nonce=target_nonce,
                generation=GENERATION_RECOVERED,
                artifact_sha256=artifact_sha256,
                python_executable_sha256=self.python_executable_sha256,
                frame_digest=frame.frame_digest,
                candidate_digest=candidate.digest(),
                proofreader_digest=proofreader.digest(),
                provider_admission_digest=provider_admission_digest,
                correlation_id=correlation_id,
            )
            if record.command_material_sha256 != command_material_sha256:
                return self._denial("COMMAND_BINDING_MISMATCH", correlation_id, now_iso, self.operation_counters)
            if self.now() >= self._parse(record.expires_at):
                return self._denial("STALE_OR_SUPERSEDED", correlation_id, now_iso, self.operation_counters)
            if record.supersession_key in self.store.superseded_keys:
                return self._denial("STALE_OR_SUPERSEDED", correlation_id, now_iso, self.operation_counters)
            if (
                self.store.launch_state != "recovery_port_reserved"
                or
                self._last_reservation is None
                or getattr(self._last_reservation, "released", True)
                or port != self._last_port
            ):
                return self._denial(
                    "CURRENT_BINDING_INVALID", correlation_id, now_iso, self.operation_counters
                )
            try:
                self.store.require_provider_admission(
                    correlation_id=correlation_id,
                    admission_digest=provider_admission_digest,
                    frame_digest=frame.frame_digest,
                    candidate_digest=candidate.digest(),
                    proofreader_digest=proofreader.digest(),
                )
                self.process.preflight(
                    expected_python_sha256=self.python_executable_sha256,
                    expected_target_sha256=artifact_sha256,
                )
            except (ValueError, AttributeError):
                return self._denial("CURRENT_BINDING_INVALID", correlation_id, now_iso, self.operation_counters)

            self.store.idempotency_records[idempotency_key] = IdempotencyRecord(
                key=idempotency_key, fingerprint=fingerprint
            )
            self.store.evidence_records[evidence_reference_sha256] = replace(record, state="consumed")
            self.store.consume_provider_admission(correlation_id, provider_admission_digest)
            attempt_id = self.store.next_attempt_id()
            attempt_record = {
                "kind": "attempt",
                "attempt_id": attempt_id,
                "correlation_id": correlation_id,
                "idempotency_key_sha256": sha256_hex(idempotency_key.encode("utf-8")),
                "evidence_reference_sha256": evidence_reference_sha256,
                "runbook_id": FORWARD_RUNBOOK,
                "frame_digest": frame.frame_digest,
                "candidate_digest": candidate.digest(),
                "proofreader_digest": proofreader.digest(),
                "provider_admission_digest": provider_admission_digest,
                "port": port,
                "artifact_sha256": artifact_sha256,
                "python_executable_sha256": self.python_executable_sha256,
                "command_material_sha256": command_material_sha256,
                "sealed_at": now_iso,
                "immutable": True,
            }
            try:
                self.store.attempt_audit.append(attempt_record)
                attempt_evidence_sha256 = canonical_sha256(attempt_record)
            except Exception:
                self.store.launch_state = "audit_failed"
                receipt = self._denial(
                    "AUDIT_FAILED",
                    correlation_id,
                    now_iso,
                    self.operation_counters,
                    evidence_consumed=True,
                )
                self.store.idempotency_records[idempotency_key].terminal_receipt = receipt
                return receipt
            self.store.launch_state = "launching"

            argv = build_launch_argv(
                port=port,
                nonce=target_nonce,
                generation=GENERATION_RECOVERED,
            )
            handle = None
            try:
                handle = self.process.start(
                    argv,
                    build_minimal_environment(),
                    expected_python_sha256=self.python_executable_sha256,
                    expected_target_sha256=artifact_sha256,
                    reservation=self._last_reservation,
                )
                self._record_operation(self.process, "process_starts", "started")
            except Exception:
                if handle is not None:
                    self._last_handle = handle
                    self._last_port = port
                    self.store.launch_state = "launch_failed"
                    return self._rollback_path(
                        correlation_id=correlation_id,
                        idempotency_key=idempotency_key,
                        handle=handle,
                        port=port,
                        issued_at=now_iso,
                    )
                self.store.launch_state = "launch_failed"
                receipt = self._denial(
                    "LAUNCH_FAILED",
                    correlation_id,
                    now_iso,
                    self.operation_counters,
                    evidence_consumed=True,
                )
                self.store.idempotency_records[idempotency_key].terminal_receipt = receipt
                return receipt
            self._last_handle = handle
            self._last_port = port

            try:
                if fault in ("launch_failed", "audit_failed"):
                    raise RuntimeError("injected post-launch failure")
                process_observation = self.process.observe_process(handle)
                if (
                    process_observation.get("disposition") != "alive"
                    or process_observation.get("owned") is not True
                    or process_observation.get("port") != port
                    or process_observation.get("generation") != GENERATION_RECOVERED
                    or process_observation.get("nonce") != target_nonce
                    or process_observation.get("artifact_sha256") != artifact_sha256
                    or process_observation.get("python_executable_sha256") != self.python_executable_sha256
                    or process_observation.get("argv_sha256") != canonical_sha256(argv)
                    or not isinstance(process_observation.get("observation_id"), str)
                    or not _OBSERVATION_ID_RE.match(process_observation["observation_id"])
                ):
                    raise RuntimeError("fresh process readback mismatch")
                readiness_probe = getattr(self.http, "probe_until_healthy", None)
                http_observation = (
                    readiness_probe(HOST, port, HEALTH_PATH)
                    if callable(readiness_probe)
                    else self.http.probe(HOST, port, HEALTH_PATH)
                )
                self._record_http_observation(http_observation)
                if fault == "readback_failed":
                    http_observation = {"status": 503, "body": "{}"}
                if not self._matches_health(
                    http_observation,
                    port=port,
                    nonce=target_nonce,
                    generation=GENERATION_RECOVERED,
                    artifact_sha256=artifact_sha256,
                ):
                    raise RuntimeError("fresh HTTP readback mismatch")
                http_observation_id = http_observation.get("observation_id")
                if (
                    not isinstance(http_observation_id, str)
                    or not _OBSERVATION_ID_RE.match(http_observation_id)
                ):
                    raise RuntimeError("HTTP observation identity missing")
                self.store.launch_state = "verified"
                receipt = {
                    "schema_version": ATTEMPT_RECEIPT_SCHEMA,
                    "evidence_label": OCCUPIED_LABEL,
                    "result": "live_development_recovery_verified",
                    "runbook_id": FORWARD_RUNBOOK,
                    "target": TargetRef.frozen().to_dict(),
                    "generation": GENERATION_RECOVERED,
                    "state": STATE_HEALTHY,
                    "artifact_sha256": artifact_sha256,
                    "python_executable_sha256": self.python_executable_sha256,
                    "port": port,
                    "target_nonce": target_nonce,
                    "process_observation_id": process_observation["observation_id"],
                    "http_readback_observation_id": http_observation_id,
                    "command_material_sha256": command_material_sha256,
                    "attempt_evidence_sha256": attempt_evidence_sha256,
                    "rollback": {"invoked": False, "verified": None},
                    "operation_counters": self.operation_counters,
                    "issued_at": now_iso,
                }
                self.store.idempotency_records[idempotency_key].terminal_receipt = receipt
                return receipt
            except Exception:
                self.store.launch_state = "readback_failed"
                return self._rollback_path(
                    correlation_id=correlation_id,
                    idempotency_key=idempotency_key,
                    handle=handle,
                    port=port,
                    issued_at=now_iso,
                )

    def _parse(self, value: str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _rollback_path(
        self,
        *,
        correlation_id: str,
        idempotency_key: str,
        handle: Any,
        port: int,
        issued_at: str,
    ) -> dict[str, Any]:
        """Exact stop rollback with verified vs inconclusive terminal outcomes."""
        rollback_invoked = False
        rollback_verified: Optional[bool] = None
        try:
            stopped = self.process.terminate(handle)
            self._record_operation(self.process, "process_stops", "stopped" if stopped else "failed")
            rollback_invoked = True
        except Exception:
            stopped = False
        if stopped:
            try:
                proc_absent = self.process.observe_process(handle).get("disposition") == "absent"
            except Exception:
                proc_absent = False
            try:
                reservation = self._acquire_exact_absence_reservation(port)
                self._last_reservation = reservation
                exact_port_reacquired = True
            except Exception:
                exact_port_reacquired = False
            rollback_verified = bool(proc_absent and exact_port_reacquired)
        else:
            rollback_verified = False
        self.store.launch_state = "rolled_back" if rollback_verified else "rollback_inconclusive"
        receipt = self._denial(
            "LIVE_RECOVERY_ROLLBACK_VERIFIED" if rollback_verified else "LIVE_RECOVERY_ROLLBACK_UNVERIFIED",
            correlation_id,
            issued_at,
            self.operation_counters,
            rollback_invoked=rollback_invoked,
            rollback_verified=rollback_verified,
            evidence_consumed=True,
        )
        self.store.idempotency_records[idempotency_key].terminal_receipt = receipt
        return receipt

    # -- idempotent cleanup of only validated owned resources -------------- #

    def cleanup(self, *, correlation_id: str) -> dict[str, Any]:
        """Idempotent cleanup proving no process, listener, task directory,
        open ledger or reusable capability remains."""
        now_iso = _format_time(self.now())
        removed_paths: list[str] = []
        cleanup_failures: list[str] = []
        directory_removed = self._task_directory_path is None
        if self._last_handle is not None:
            try:
                observation = self.process.observe_process(self._last_handle)
                if observation.get("disposition") != "absent":
                    stopped = self.process.terminate(self._last_handle)
                    self._record_operation(self.process, "process_stops", "stopped" if stopped else "failed")
                close = getattr(self.process, "close", None)
                if callable(close):
                    close(self._last_handle)
            except Exception:
                cleanup_failures.append("process_handle_cleanup")
        if self._last_reservation is not None:
            try:
                self._last_reservation.close()
            except Exception:
                cleanup_failures.append("port_reservation_cleanup")
        self.store.close_provider_attempts()
        with self.store.transaction_lock:
            for reference_sha256, record in list(self.store.evidence_records.items()):
                if record.state == "issued":
                    self.store.evidence_records[reference_sha256] = replace(record, state="consumed")
        if self._task_directory_path is not None:
            try:
                if self.directory.validate_owned_path(self._task_directory_path):
                    removed_path = str(Path(self._task_directory_path).resolve())
                    if self.directory.remove_task_dir(self._task_directory_path):
                        self._record_operation(
                            self.directory, "directory_removals", "removed"
                        )
                        removed_paths.append(removed_path)
                        directory_removed = True
            except Exception:
                cleanup_failures.append("task_directory_cleanup")

        try:
            no_process = self.process.any_running() is False
        except Exception:
            no_process = False
        try:
            if self._last_port is None:
                no_listener = True
            else:
                cleanup_reservation = self._acquire_exact_absence_reservation(
                    self._last_port
                )
                cleanup_reservation.close()
                no_listener = True
        except Exception:
            no_listener = False
        no_task_directory = (
            directory_removed
            and (
                self._task_directory_path is None
                or not Path(self._task_directory_path).resolve().exists()
            )
        )
        no_open_ledger = self.store.provider_open_count() == 0
        no_issued_evidence = all(
            record.state == "consumed" for record in self.store.evidence_records.values()
        )
        no_reusable_capability = no_issued_evidence and no_open_ledger
        verified = all(
            (no_process, no_listener, no_task_directory, no_open_ledger, no_reusable_capability)
        ) and not cleanup_failures
        self.store.cleanup_complete = verified
        if verified:
            self.store.launch_state = "cleaned"
        return {
            "schema_version": CLEANUP_SCHEMA,
            "evidence_label": OCCUPIED_LABEL,
            "result": "cleanup_verified" if verified else "cleanup_inconclusive",
            "no_process": no_process,
            "no_listener": no_listener,
            "no_task_directory": no_task_directory,
            "no_open_ledger": no_open_ledger,
            "no_reusable_capability": no_reusable_capability,
            "removed_paths": removed_paths,
            "ledger_consumed": no_open_ledger,
            "operation_counters": self.operation_counters,
            "issued_at": now_iso,
        }
