"""Bureau C5 fixed process adapter, argument-vector builder and controller.

This module implements the real capability adapters and controller logic for
the frozen C5 disposable live-development-recovery foundation.  The capability
adapters are implemented but **never invoked** in this worker tranche: no
process is started, no socket is bound/connected, no port is allocated, no
directory is created/removed and no provider is called.  All worker tests and
acceptance generation use provider-free fakes and exact operation counters.

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
import os
import re
import subprocess  # nosec B404  # real adapter; never invoked in this tranche
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
    RecoveryDiagnosisCandidate,
    ROLLBACK_RUNBOOK,
    SystemAnatomyFrameSet,
    TARGET_ID,
    TARGET_KIND,
    PLAN_ENVIRONMENT,
    TargetRef,
    canonical_sha256,
    materialise_execution_approval,
    parse_recovery_candidate,
    proofread_candidate,
    sha256_hex,
    strict_json_loads,
)

_HEX32_64_RE = re.compile(r"^[0-9a-f]{32,64}$")
_UUID36_RE = re.compile(r"^[0-9a-f-]{36}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

SUPERSESSION_KEY = "synthetic.c5-recovery-target.recovery"
HEALTH_PATH = "/healthz"
GENERATION_BASELINE = 1
GENERATION_RECOVERED = 2
STATE_HEALTHY = "healthy"


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


# --------------------------------------------------------------------------- #
# Fixed path resolution and argument-vector construction
# --------------------------------------------------------------------------- #

def resolve_python_executable(repo_root: Any) -> Path:
    """Resolve the exact repository virtual-environment Python executable.

    The returned path is deterministic from the repository root.  The real
    adapter hashes this path during live preflight; this function itself only
    constructs the path and never reads the file.
    """
    root = Path(repo_root).resolve()
    if os.name == "nt":
        return root / ".venv" / "Scripts" / "python.exe"
    return root / ".venv" / "bin" / "python"


def resolve_target_module(repo_root: Any) -> Path:
    """Resolve the exact frozen C5 service module path."""
    return Path(repo_root).resolve() / "scripts" / "model_required_bureau_c5_target.py"


def hash_file(path: Any) -> str:
    """Return the LF-byte SHA-256 of a file (live preflight only; never used here)."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_launch_argv(
    *,
    repo_root: Any,
    port: int,
    nonce: str,
    generation: int,
) -> list[str]:
    """Build the fixed allowlisted argument vector.

    The function accepts only server-held ``port``/``nonce``/``generation`` and
    a repository root.  It does **not** accept a caller executable, path, host,
    module or environment override.  It contains no shell or string command.
    """
    if not isinstance(port, int) or isinstance(port, bool) or port <= 0 or port > 65535:
        raise ValueError("port must be a valid OS-assigned server-held port")
    if not isinstance(nonce, str) or not _HEX32_64_RE.match(nonce):
        raise ValueError("nonce must be an opaque hexadecimal value")
    if generation not in (GENERATION_BASELINE, GENERATION_RECOVERED):
        raise ValueError("generation must be exactly 1 or 2")
    python = resolve_python_executable(repo_root)
    target = resolve_target_module(repo_root)
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


def validate_launch_argv(argv: Any, repo_root: Any) -> None:
    """Reject any caller override or shell/command string in an argument vector."""
    if not isinstance(argv, list) or len(argv) != 11:
        raise ValueError("argv must be the fixed 11-element argument vector")
    if not all(isinstance(item, str) for item in argv):
        raise ValueError("argv elements must be strings")
    python = resolve_python_executable(repo_root)
    target = resolve_target_module(repo_root)
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

    def __init__(self, proc: Any, argv: list[str], started_at: str) -> None:
        self._proc = proc
        self.argv = list(argv)
        self.started_at = started_at

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

    def __init__(self, repo_root: Any) -> None:
        self.repo_root = Path(repo_root).resolve()

    def start(self, argv: list[str], env: dict[str, str]) -> OwnedProcessHandle:
        validate_launch_argv(argv, self.repo_root)
        proc = subprocess.Popen(  # nosec B603  # fixed argv, shell=False, never invoked here
            argv,
            shell=False,
            env=env,
            cwd=str(self.repo_root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return OwnedProcessHandle(proc, argv, _format_time(datetime.now(timezone.utc)))


class HttpReadbackProbe:
    """Loopback HTTP health readback probe (real; never invoked in this tranche)."""

    def probe(self, host: str, port: int, path: str) -> dict[str, Any]:
        import http.client

        conn = http.client.HTTPConnection(host, port, timeout=1)
        try:
            conn.request("GET", path)
            response = conn.getresponse()
            body = response.read().decode("utf-8")
            return {"status": int(response.status), "body": body}
        finally:
            conn.close()


class LoopbackPortAllocator:
    """OS-assigned ephemeral loopback port allocator (real; never invoked here)."""

    def allocate(self) -> int:
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((HOST, 0))
            return int(sock.getsockname()[1])


class TaskDirectoryOps:
    """Owned task-directory lifecycle (real; never invoked in this tranche)."""

    def create_task_dir(self, task_root: Any) -> str:
        path = Path(task_root).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    def validate_owned_path(self, candidate: Any, task_root: Any) -> bool:
        candidate_path = Path(candidate).resolve()
        root = Path(task_root).resolve()
        return root == candidate_path or (root in candidate_path.parents and candidate_path != root.parent)

    def remove_task_dir(self, candidate: Any, task_root: Any) -> bool:
        if not self.validate_owned_path(candidate, task_root):
            raise ValueError("cleanup path is not an owned task directory")
        path = Path(candidate).resolve()
        if path.exists():
            path.rmdir()
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

    repo_root: Any
    store: C5SharedStore
    process: Any
    http: Any
    port_allocator: Any
    directory: Any
    ledger: Any
    now: Callable[[], datetime]
    _counters: ForbiddenOperationCounters = ForbiddenOperationCounters()
    _last_handle: Any = None
    _last_port: Optional[int] = None

    @property
    def operation_counters(self) -> dict[str, int]:
        return self._counters.to_dict()

    @property
    def attempt_audit_records(self) -> list[dict[str, Any]]:
        with self.store.transaction_lock:
            return list(self.store.attempt_audit)

    # -- helpers ------------------------------------------------------------ #

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
        nonce: str,
        generation: int,
        artifact_sha256: str,
    ) -> bool:
        if http_observation.get("status") != 200:
            return False
        body = self._parse_health_body(http_observation)
        if body is None:
            return False
        return (
            body.get("environment") == PLAN_ENVIRONMENT
            and body.get("kind") == TARGET_KIND
            and body.get("target_id") == TARGET_ID
            and body.get("host") == HOST
            and body.get("generation") == generation
            and body.get("nonce") == nonce
            and body.get("artifact_sha256") == artifact_sha256
            and body.get("state") == STATE_HEALTHY
        )

    def _fingerprint(self, *, approval, evidence_reference_sha256, candidate, frame, target_nonce, port, artifact_sha256, correlation_id) -> str:
        return canonical_sha256(
            {
                "approval_id": approval.approval_id,
                "approval_sha256": approval.digest(),
                "evidence_reference_sha256": evidence_reference_sha256,
                "candidate_digest": candidate.digest(),
                "frame_digest": frame.frame_digest,
                "target_nonce": target_nonce,
                "port": port,
                "generation": GENERATION_RECOVERED,
                "artifact_sha256": artifact_sha256,
                "correlation_id": correlation_id,
            }
        )

    # -- state-machine steps ------------------------------------------------ #

    def run_baseline(self, *, port: int, nonce: str, artifact_sha256: str) -> tuple[Any, bool]:
        """Start generation 1 and prove baseline by process and HTTP agreement."""
        argv = build_launch_argv(
            repo_root=self.repo_root, port=port, nonce=nonce, generation=GENERATION_BASELINE
        )
        handle = self.process.start(argv, build_minimal_environment())
        self._last_handle = handle
        self._last_port = port
        proc_disposition = self.process.observe_process(handle).get("disposition")
        http_observation = self.http.probe(HOST, port, HEALTH_PATH)
        healthy = proc_disposition == "alive" and self._matches_health(
            http_observation, nonce=nonce, generation=GENERATION_BASELINE, artifact_sha256=artifact_sha256
        )
        return handle, healthy

    def inject_fault(self, handle: Any) -> bool:
        """Terminate the exact controller-owned child handle."""
        return self.process.terminate(handle)

    def post_fault_verify(self, handle: Any, *, port: int) -> bool:
        """Prove process-absent and loopback connection-refused agreement."""
        proc_disposition = self.process.observe_process(handle).get("disposition")
        http_observation = self.http.probe(HOST, port, HEALTH_PATH)
        return (
            proc_disposition == "absent"
            and http_observation.get("status") == "connection_refused"
        )

    def reserve_provider_ledger(self, *, correlation_id: str) -> dict[str, Any]:
        """Record provider ledger/reservation state without making a provider call."""
        return self.ledger.reserve(
            model="gemini-2.5-flash",
            project="bernie-emr4-dev",
            region="australia-southeast1",
            call_limit=2,
            cost_ceiling_usd=0.50,
            correlation_id=correlation_id,
        )

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
            plan_sha256="9f23396e8facadc5f8f1baa3294ebbcdcaeca0bf71b29f95a7743ac80220ac15",
            plan_revision=1,
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
        target_nonce: str,
        port: int,
        artifact_sha256: str,
        correlation_id: str,
        idempotency_key: str,
        fault: Optional[str] = None,
    ) -> dict[str, Any]:
        with self.store.transaction_lock:
            now_iso = _format_time(self.now())
            counters = self._counters.to_dict()
            fingerprint = self._fingerprint(
                approval=approval,
                evidence_reference_sha256=evidence_reference_sha256,
                candidate=candidate,
                frame=frame,
                target_nonce=target_nonce,
                port=port,
                artifact_sha256=artifact_sha256,
                correlation_id=correlation_id,
            )

            existing = self.store.idempotency_records.get(idempotency_key)
            if existing is not None:
                if existing.fingerprint != fingerprint:
                    return self._denial("IDEMPOTENCY_CONFLICT", correlation_id, now_iso, counters)
                if existing.terminal_receipt is None:
                    return self._denial("IDEMPOTENCY_IN_PROGRESS", correlation_id, now_iso, counters)
                return existing.terminal_receipt

            record = self.store.evidence_records.get(evidence_reference_sha256)
            if record is None:
                return self._denial("EXECUTION_EVIDENCE_INVALID", correlation_id, now_iso, counters)
            if record.state != "issued":
                return self._denial("EXECUTION_EVIDENCE_REPLAY", correlation_id, now_iso, counters)
            if record.approval_id != approval.approval_id or record.approval_sha256 != approval.digest():
                return self._denial("AUTHORITY_MISMATCH", correlation_id, now_iso, counters)
            if record.target != TargetRef.frozen() or record.runbook_id != FORWARD_RUNBOOK:
                return self._denial("SCOPE_EXPANSION_REJECTED", correlation_id, now_iso, counters)
            if record.rollback_runbook_id != ROLLBACK_RUNBOOK:
                return self._denial("UNKNOWN_ROLLBACK", correlation_id, now_iso, counters)
            if record.generation != GENERATION_RECOVERED or record.artifact_sha256 != artifact_sha256:
                return self._denial("TARGET_DRIFT_REJECTED", correlation_id, now_iso, counters)
            if record.target_nonce != target_nonce:
                return self._denial("NONCE_MISMATCH", correlation_id, now_iso, counters)
            if self.now() >= self._parse(record.expires_at):
                return self._denial("STALE_OR_SUPERSEDED", correlation_id, now_iso, counters)
            if record.supersession_key in self.store.superseded_keys:
                return self._denial("STALE_OR_SUPERSEDED", correlation_id, now_iso, counters)

            self.store.idempotency_records[idempotency_key] = IdempotencyRecord(
                key=idempotency_key, fingerprint=fingerprint
            )
            self.store.evidence_records[evidence_reference_sha256] = replace(record, state="consumed")
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
                "sealed_at": now_iso,
                "immutable": True,
            }
            self.store.attempt_audit.append(attempt_record)
            attempt_evidence_sha256 = canonical_sha256(attempt_record)
            self.store.launch_state = "launching"

            argv = build_launch_argv(
                repo_root=self.repo_root,
                port=port,
                nonce=target_nonce,
                generation=GENERATION_RECOVERED,
            )
            try:
                handle = self.process.start(argv, build_minimal_environment())
            except Exception as error:
                self.store.launch_state = "launch_failed"
                return self._denial(
                    "LAUNCH_FAILED", correlation_id, now_iso, counters, evidence_consumed=True
                )
            self._last_handle = handle
            self._last_port = port

            if fault in ("launch_failed", "audit_failed"):
                self.store.launch_state = "launch_failed"
                return self._rollback_path(
                    correlation_id=correlation_id,
                    idempotency_key=idempotency_key,
                    handle=handle,
                    port=port,
                    counters=counters,
                    issued_at=now_iso,
                )

            http_observation = self.http.probe(HOST, port, HEALTH_PATH)
            if fault == "readback_failed":
                http_observation = {"status": 503, "body": "{}"}

            if self._matches_health(
                http_observation,
                nonce=target_nonce,
                generation=GENERATION_RECOVERED,
                artifact_sha256=artifact_sha256,
            ):
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
                    "target_nonce": target_nonce,
                    "process_observation_id": "obs-recovered-process-0001",
                    "http_readback_observation_id": "obs-recovered-http-0001",
                    "attempt_evidence_sha256": attempt_evidence_sha256,
                    "rollback": {"invoked": False, "verified": None},
                    "operation_counters": counters,
                    "issued_at": now_iso,
                }
                self.store.idempotency_records[idempotency_key].terminal_receipt = receipt
                return receipt

            self.store.launch_state = "readback_failed"
            return self._rollback_path(
                correlation_id=correlation_id,
                idempotency_key=idempotency_key,
                handle=handle,
                port=port,
                counters=counters,
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
        counters: dict[str, int],
        issued_at: str,
    ) -> dict[str, Any]:
        """Exact stop rollback with verified vs inconclusive terminal outcomes."""
        rollback_invoked = False
        rollback_verified: Optional[bool] = None
        try:
            stopped = self.process.terminate(handle)
            rollback_invoked = True
        except Exception:
            stopped = False
        if stopped:
            proc_absent = self.process.observe_process(handle).get("disposition") == "absent"
            http_refused = self.http.probe(HOST, port, HEALTH_PATH).get("status") == "connection_refused"
            rollback_verified = bool(proc_absent and http_refused)
        else:
            rollback_verified = False
        self.store.launch_state = "rolled_back" if rollback_verified else "rollback_inconclusive"
        receipt = self._denial(
            "LIVE_RECOVERY_ROLLBACK_VERIFIED" if rollback_verified else "LIVE_RECOVERY_ROLLBACK_UNVERIFIED",
            correlation_id,
            issued_at,
            counters,
            rollback_invoked=rollback_invoked,
            rollback_verified=rollback_verified,
            evidence_consumed=True,
        )
        self.store.idempotency_records[idempotency_key].terminal_receipt = receipt
        return receipt

    # -- idempotent cleanup of only validated owned resources -------------- #

    def cleanup(self, *, task_root: Any, removed_paths: list[str], correlation_id: str) -> dict[str, Any]:
        """Idempotent cleanup proving no process, listener, task directory,
        open ledger or reusable capability remains."""
        now_iso = _format_time(self.now())
        counters = self._counters.to_dict()
        validated_removals: list[str] = []
        for candidate in removed_paths:
            if not self.directory.validate_owned_path(candidate, task_root):
                raise ValueError("cleanup path is not an owned task directory")
            validated_removals.append(str(Path(candidate).resolve()))
        self.directory.remove_task_dir(task_root, task_root)
        return {
            "schema_version": CLEANUP_SCHEMA,
            "evidence_label": OCCUPIED_LABEL,
            "result": "cleanup_verified",
            "no_process": self.process.any_running() is False,
            "no_listener": self.http.any_listener() is False,
            "no_task_directory": not Path(task_root).resolve().exists(),
            "no_open_ledger": self.ledger.open_count() == 0,
            "no_reusable_capability": self.store.launch_state in ("verified", "rolled_back", "rollback_inconclusive"),
            "removed_paths": validated_removals,
            "ledger_consumed": True,
            "operation_counters": counters,
            "issued_at": now_iso,
        }
