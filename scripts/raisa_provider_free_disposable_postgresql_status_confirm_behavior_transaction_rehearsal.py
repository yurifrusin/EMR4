"""Run the fixed provider-free status-confirm PostgreSQL transaction rehearsal."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jsonschema import Draft202012Validator
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models.appointments import (
    AppointmentAuditAction,
    AppointmentAuditLog,
    AppointmentStatus,
)
from app.services import appointment_status_physical as physical
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_scaffold_parse_catalogue_rehearsal
    as catalogue,
)


BASE = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "status-confirm-behavior-transaction-rehearsal"
)
CONTRACT_PATH = BASE / "rehearsal-contract.json"
SCHEMA_PATH = BASE / "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA_PATH = BASE / "provider-free-behavior-transaction-evidence.schema.json"
EVIDENCE_PATH = BASE / "provider-free-behavior-transaction-evidence.json"
FAILURE_EVIDENCE_PATH = BASE / "provider-free-behavior-transaction-failure-evidence.json"
PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_status_confirm_"
    "behavior_transaction_rehearsal_pass"
)
EXPECTED_CONTRACT_DIGEST = (
    "b6b9ada2bde03726f6878d86c25705404e0fce5445ae55936455c9c3dc991ff6"
)
HOSTILE_MUTATION_TARGET = 100
CLAIM_BOUNDARY = (
    "Exact serial unmounted SQLAlchemy/PostgreSQL behavior and selected rollback "
    "boundaries only; no route, product database, concurrency, restart, unknown "
    "commit, deployment or production claim."
)
FIXED_RELAY_COMMAND = (
    "exec 3<>/dev/tcp/127.0.0.1/5432; cat <&3 & cat >&3; wait"
)

EXPECTED_SCENARIOS = (
    ("BTR-S01", "clean_commit", "new_command", 1, 1, 1, 1, 2),
    ("BTR-S02", "response_loss_retry", "replay", 1, 1, 1, 1, 4),
    ("BTR-S03", "request_digest_conflict", "conflict", 1, 1, 1, 1, 4),
    ("BTR-S04", "session_binding_conflict", "conflict", 1, 1, 1, 1, 4),
    (
        "BTR-S05",
        "in_progress_not_replayable",
        "in_progress_not_replayable",
        0,
        0,
        0,
        0,
        2,
    ),
    (
        "BTR-S06",
        "legacy_receipt_not_replayable",
        "legacy_receipt_not_replayable",
        0,
        0,
        0,
        0,
        2,
    ),
    (
        "BTR-S07",
        "receipt_integrity_failure",
        "receipt_integrity_failure",
        0,
        0,
        0,
        0,
        2,
    ),
    ("BTR-S08", "inactive_practice", "target_unavailable", 0, 0, 0, 0, 0),
    ("BTR-S09", "target_absent", "target_unavailable", 0, 0, 0, 0, 0),
    (
        "BTR-S10",
        "first_authority_revoked",
        "authority_revoked",
        0,
        0,
        0,
        0,
        1,
    ),
    (
        "BTR-S11",
        "second_authority_revoked",
        "authority_revoked",
        0,
        0,
        0,
        0,
        2,
    ),
    (
        "BTR-S12",
        "replay_after_revocation",
        "authority_revoked",
        1,
        1,
        1,
        1,
        3,
    ),
    ("BTR-S13", "empty_write_set", "scaffold_incomplete", 0, 0, 0, 0, 2),
    ("BTR-S14", "appointment_only", "scaffold_incomplete", 0, 0, 0, 0, 2),
    (
        "BTR-S15",
        "appointment_audit_only",
        "scaffold_incomplete",
        0,
        0,
        0,
        0,
        2,
    ),
    (
        "BTR-S16",
        "complete_write_outer_abort",
        "outer_abort",
        0,
        0,
        0,
        0,
        2,
    ),
)


BOOTSTRAP_SQL = r"""
CREATE TABLE public.practices (
  id uuid PRIMARY KEY, name varchar(255) NOT NULL, abn varchar(20),
  address_line1 varchar(255), address_line2 varchar(255),
  address_suburb varchar(100), address_state varchar(10),
  address_postcode varchar(10), phone varchar(20), email varchar(255),
  logo_url varchar(500), timezone varchar(50), hive_mind_opt_in boolean,
  practice_embedding text, specialty_tags jsonb, asgc_ra_code varchar(10),
  latitude double precision, longitude double precision,
  proda_device_cert_path varchar(500), proda_cert_expiry timestamptz,
  created_at timestamptz DEFAULT now()
);
CREATE TABLE public.appointments (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL, location_id uuid,
  patient_id uuid, patient_name_provisional varchar(200),
  practitioner_id uuid NOT NULL, appointment_type_id uuid, booked_by uuid,
  start_time timestamptz NOT NULL, appointment_date date NOT NULL,
  start_time_local time NOT NULL, duration_minutes integer DEFAULT 15,
  status text DEFAULT 'Booked', reason varchar(500), notes varchar(1000),
  cancellation_reason varchar(500), status_reason_code varchar(50),
  booked_via text DEFAULT 'Receptionist', waiting_room varchar(50),
  waiting_area_id uuid, queue_position integer, created_at timestamptz DEFAULT now(),
  CONSTRAINT uq_appointments_practice_id_id UNIQUE (practice_id, id),
  CONSTRAINT fk_btr_appointment_practice FOREIGN KEY (practice_id)
    REFERENCES public.practices(id)
);
CREATE TABLE public.appointment_command_idempotency (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL, actor_user_id varchar(64) NOT NULL,
  actor_role varchar(64) NOT NULL, operation_id varchar(100) NOT NULL,
  route_family varchar(100) NOT NULL, idempotency_key_hash varchar(128) NOT NULL,
  request_body_hash varchar(128) NOT NULL,
  request_body_canonicalization_version integer NOT NULL DEFAULT 1,
  state varchar(32) NOT NULL, response_status_code integer,
  response_body_hash varchar(128), response_body_json jsonb,
  result_kind varchar(50), target_appointment_id uuid, audit_log_id uuid,
  bernie_session_id varchar(64), created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(), expires_at timestamptz,
  confirmation_evidence_hash varchar(128),
  confirmation_evidence_consumed_at timestamptz,
  CONSTRAINT uq_appt_cmd_idem_practice_id_id UNIQUE (practice_id, id),
  CONSTRAINT uq_appt_cmd_idem_practice_actor_operation_key UNIQUE
    (practice_id, actor_user_id, operation_id, idempotency_key_hash),
  CONSTRAINT ck_appt_cmd_idem_state CHECK
    (state IN ('in_progress', 'completed', 'failed_transient')),
  CONSTRAINT ck_appt_cmd_idem_completed_response CHECK
    (state != 'completed' OR (response_status_code IS NOT NULL AND
      response_body_hash IS NOT NULL AND response_body_json IS NOT NULL)),
  CONSTRAINT ck_appt_cmd_idem_completed_create_correlation CHECK
    (NOT (state = 'completed' AND operation_id IN
      ('confirmAppointmentCreateProposal', 'confirmAppointmentCheckInProposal')
      AND result_kind = 'confirmed_write') OR
      (target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL)),
  CONSTRAINT ck_appt_cmd_idem_completed_check_in_evidence CHECK
    (NOT (state = 'completed' AND operation_id =
      'confirmAppointmentCheckInProposal' AND result_kind = 'confirmed_write') OR
      (confirmation_evidence_hash IS NOT NULL AND
       confirmation_evidence_consumed_at IS NOT NULL))
);
CREATE TABLE public.appointment_audit_log (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL, appointment_id uuid NOT NULL,
  confirmed_by_user_id uuid NOT NULL, action text NOT NULL,
  status_before text, status_after text, cancellation_reason varchar(500),
  status_reason_code varchar(50), confirmed_warnings jsonb, command_id uuid,
  bernie_session_id varchar(64), created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_appt_audit_log_practice_id_id UNIQUE (practice_id, id)
);
CREATE TABLE public.alembic_version (
  version_num varchar(32) NOT NULL PRIMARY KEY
);
INSERT INTO public.alembic_version(version_num) VALUES ('v1w2x3y4z5b6');
"""


CORRELATION_SQL = r"""
ALTER TABLE public.appointment_command_idempotency
  ADD CONSTRAINT fk_appt_cmd_idem_practice_target
  FOREIGN KEY (practice_id, target_appointment_id)
  REFERENCES public.appointments(practice_id, id);
ALTER TABLE public.appointment_audit_log
  ADD CONSTRAINT fk_appt_audit_log_practice_appointment
  FOREIGN KEY (practice_id, appointment_id)
  REFERENCES public.appointments(practice_id, id);
ALTER TABLE public.appointment_audit_log
  ADD CONSTRAINT fk_appt_audit_log_practice_command
  FOREIGN KEY (practice_id, command_id)
  REFERENCES public.appointment_command_idempotency(practice_id, id);
ALTER TABLE public.appointment_command_idempotency
  ADD CONSTRAINT fk_appt_cmd_idem_practice_audit
  FOREIGN KEY (practice_id, audit_log_id)
  REFERENCES public.appointment_audit_log(practice_id, id);
CREATE UNIQUE INDEX uq_appt_audit_log_command_id
  ON public.appointment_audit_log(command_id) WHERE command_id IS NOT NULL;
CREATE UNIQUE INDEX uq_appt_cmd_idem_audit_log_id
  ON public.appointment_command_idempotency(audit_log_id)
  WHERE audit_log_id IS NOT NULL;
"""


class RehearsalFailure(RuntimeError):
    def __init__(self, stage: str, code: str, detail: str | bytes = "") -> None:
        self.stage = stage
        self.code = code
        self.detail = detail
        super().__init__(f"{stage}:{code}")


class OuterAbort(RuntimeError):
    pass


@dataclass(frozen=True)
class Fixture:
    index: int
    practice_id: UUID
    appointment_id: UUID
    actor_id: UUID
    actor_text: str
    audit_id: UUID
    idempotency_key_hash: str
    request_body_hash: str
    session_digest: bytes
    session_id: str


@dataclass(frozen=True)
class Invocation:
    outcome: str
    response_digest: str | None
    authority_calls: int
    statement_tokens: tuple[str, ...]


def _sha256(value: bytes | str) -> str:
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(payload).hexdigest()


def _canonical_digest(value: Any) -> str:
    return _sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario_tuple(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        item["id"],
        item["kind"],
        item["expected"],
        item["appointment_delta"],
        item["audit_delta"],
        item["receipt_delta"],
        item["disclosure_count"],
        item["authority_calls"],
    )


def _validate_contract(value: dict[str, Any], *, require_digest: bool) -> None:
    schema = _load_json(SCHEMA_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        raise RehearsalFailure("preflight", "contract_schema_invalid")
    if require_digest and _canonical_digest(value) != EXPECTED_CONTRACT_DIGEST:
        raise RehearsalFailure("preflight", "contract_digest_mismatch")
    if tuple(_scenario_tuple(item) for item in value["scenarios"]) != EXPECTED_SCENARIOS:
        raise RehearsalFailure("preflight", "scenario_contract_mismatch")
    if value["scenario_categories"] != {
        "success_replay": 2,
        "classification": 5,
        "authority": 5,
        "rollback": 4,
    }:
        raise RehearsalFailure("preflight", "scenario_category_mismatch")
    if len({item["path"] for item in value["source_bindings"]}) != 11:
        raise RehearsalFailure("preflight", "source_binding_mismatch")


def hostile_mutations_rejected(contract: dict[str, Any]) -> int:
    mutations: list[dict[str, Any]] = []

    def mutate(path: tuple[str | int, ...], replacement: Any) -> None:
        candidate = copy.deepcopy(contract)
        cursor: Any = candidate
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = replacement
        mutations.append(candidate)

    globals_to_mutate = (
        (("schema_version",), "raisa.status_confirm_behavior_transaction_rehearsal.v2"),
        (("result",), "rehearsal_failed"),
        (("source_head",), "0" * 40),
        (("evidence_label",), "product"),
        (("docker_profile", "image_reference"), "postgres:latest"),
        (("docker_profile", "pull_policy"), "always"),
        (("docker_profile", "network_internal"), False),
        (("docker_profile", "published_ports"), True),
        (("docker_profile", "relay_host_ip"), "0.0.0.0"),
        (("docker_profile", "relay_dynamic_host_port"), False),
        (("docker_profile", "relay_container_command"), "cat"),
        (("docker_profile", "sqlalchemy_driver"), "psycopg"),
        (("docker_profile", "tmpfs_options"), "rw"),
        (("transaction_contract", "entry_point"), "substitute"),
        (("transaction_contract", "isolation"), "AUTOCOMMIT"),
        (("transaction_contract", "lock_order"), list(reversed(contract["transaction_contract"]["lock_order"]))),
        (("transaction_contract", "effect_write_set"), ["appointment_mutation"]),
        (("transaction_contract", "nested_transaction"), True),
        (("transaction_contract", "concurrency"), True),
        (("cleanup", "container_target"), "container_name"),
    )
    for path, replacement in globals_to_mutate:
        mutate(path, replacement)
    for index, scenario in enumerate(contract["scenarios"]):
        mutate(("scenarios", index, "id"), contract["scenarios"][(index + 1) % 16]["id"])
        mutate(("scenarios", index, "kind"), "invalid_kind")
        mutate(("scenarios", index, "expected"), "invalid_expected")
        mutate(("scenarios", index, "appointment_delta"), 1 - scenario["appointment_delta"])
        mutate(("scenarios", index, "authority_calls"), (scenario["authority_calls"] + 1) % 5)
    if len(mutations) != HOSTILE_MUTATION_TARGET:
        raise AssertionError("hostile mutation population drift")
    rejected = 0
    for candidate in mutations:
        try:
            _validate_contract(candidate, require_digest=False)
        except RehearsalFailure:
            rejected += 1
    return rejected


def verify_contract() -> tuple[dict[str, Any], dict[str, str]]:
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, require_digest=True)
    if hostile_mutations_rejected(contract) != HOSTILE_MUTATION_TARGET:
        raise RehearsalFailure("preflight", "hostile_mutation_gate_failed")
    observed: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            raise RehearsalFailure("preflight", "source_missing", binding["path"])
        digest = _sha256(path.read_bytes())
        observed[binding["path"]] = digest
        if digest != binding["sha256"]:
            raise RehearsalFailure("preflight", "source_hash_mismatch", binding["path"])
    return contract, observed


def build_network_argv(docker: str, name: str, nonce: str, profile: dict[str, Any]) -> list[str]:
    return [
        docker,
        "network",
        "create",
        "--driver",
        "bridge",
        "--internal",
        "--label",
        f"com.emr4.harness={profile['harness_label']}",
        "--label",
        f"com.emr4.cleanup-nonce={nonce}",
        name,
    ]


def build_container_argv(
    docker: str,
    name: str,
    nonce: str,
    network_id: str,
    profile: dict[str, Any],
) -> list[str]:
    return [
        docker,
        "run",
        "--detach",
        "--pull",
        profile["pull_policy"],
        "--name",
        name,
        "--label",
        f"com.emr4.harness={profile['harness_label']}",
        "--label",
        f"com.emr4.cleanup-nonce={nonce}",
        "--network",
        network_id,
        "--tmpfs",
        f"{profile['data_destination']}:{profile['tmpfs_options']}",
        "--memory",
        "512m",
        "--cpus",
        "1",
        "--pids-limit",
        str(profile["pids_limit"]),
        "--restart",
        profile["restart_policy"],
        "--env",
        f"POSTGRES_USER={profile['postgres_user']}",
        "--env",
        f"POSTGRES_PASSWORD={profile['postgres_password']}",
        "--env",
        f"POSTGRES_DB={profile['postgres_database']}",
        "--env",
        f"PGDATA={profile['pgdata']}",
        profile["image_reference"],
    ]


def _inspect_one(
    docker: str, kind: str, object_id: str, timeout: int
) -> tuple[catalogue.ProcessResult, dict[str, Any] | None]:
    result = catalogue._run(  # noqa: SLF001
        [docker, kind, "inspect", object_id], None, timeout, 256_000
    )
    if result.returncode != 0:
        return result, None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return result, None
    if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
        return result, None
    return result, payload[0]


def _network_owned(
    item: dict[str, Any], *, network_id: str, name: str, nonce: str, profile: dict[str, Any], require_empty: bool
) -> bool:
    try:
        labels = item["Labels"] or {}
        containers = item["Containers"] or {}
        return bool(
            item["Id"] == network_id
            and item["Name"] == name
            and item["Driver"] == "bridge"
            and item["Internal"] is True
            and labels.get("com.emr4.harness") == profile["harness_label"]
            and labels.get("com.emr4.cleanup-nonce") == nonce
            and (not require_empty or not containers)
        )
    except (KeyError, TypeError):
        return False


def _container_profile(
    item: dict[str, Any], *, container_id: str, name: str, nonce: str, image_id: str, network_id: str, profile: dict[str, Any]
) -> bool:
    try:
        labels = item["Config"]["Labels"] or {}
        host = item["HostConfig"]
        networks = item["NetworkSettings"]["Networks"]
        ports = item["NetworkSettings"].get("Ports") or {}
        host_bindings = host.get("PortBindings")
        expected_tmpfs = host["Tmpfs"].get(profile["data_destination"])
        mounts = item.get("Mounts") or []
        env = set(item["Config"]["Env"] or [])
        no_published_ports = (
            profile["published_ports"] is False
            and host_bindings in (None, {})
            and isinstance(ports, dict)
            and all(value in (None, []) for value in ports.values())
        )
        network_ok = (
            isinstance(networks, dict)
            and len(networks) == 1
            and next(iter(networks.values()))["NetworkID"] == network_id
        )
        required_env = {
            f"POSTGRES_USER={profile['postgres_user']}",
            f"POSTGRES_PASSWORD={profile['postgres_password']}",
            f"POSTGRES_DB={profile['postgres_database']}",
            f"PGDATA={profile['pgdata']}",
        }
        ok = bool(
            item["Id"] == container_id
            and item["Name"] == f"/{name}"
            and item["Image"] == image_id
            and item["Config"]["Image"] == profile["image_reference"]
            and labels.get("com.emr4.harness") == profile["harness_label"]
            and labels.get("com.emr4.cleanup-nonce") == nonce
            and host["Binds"] in (None, [])
            and host.get("Privileged") is False
            and host["Memory"] == profile["memory_bytes"]
            and host["NanoCpus"] == profile["nano_cpus"]
            and host["PidsLimit"] == profile["pids_limit"]
            and host["RestartPolicy"]["Name"] == profile["restart_policy"]
            and set(expected_tmpfs.split(",")) == set(profile["tmpfs_options"].split(","))
            and not mounts
            and required_env <= env
            and network_ok
            and no_published_ports
        )
        return ok
    except (KeyError, TypeError, AttributeError, StopIteration):
        return False


def _exact_absence(result: catalogue.ProcessResult, noun: str) -> bool:
    if result.returncode == 0:
        return False
    message = result.stderr.decode("utf-8", errors="replace").lower()
    if noun == "container":
        return "no such container" in message or "no such object" in message
    return f"no such {noun}" in message or "not found" in message


def build_relay_argv(
    docker: str, container_id: str, profile: dict[str, Any]
) -> list[str]:
    if re.fullmatch(r"[0-9a-f]{64}", container_id) is None:
        raise RehearsalFailure("environment", "relay_container_id_invalid")
    if profile["relay_container_command"] != FIXED_RELAY_COMMAND:
        raise RehearsalFailure("preflight", "relay_command_mismatch")
    return [
        docker,
        "exec",
        "-i",
        container_id,
        profile["relay_container_executable"],
        "-c",
        FIXED_RELAY_COMMAND,
    ]


class DockerExecRelay:
    """Bounded IPv4-loopback relay to one exact internally networked container."""

    def __init__(
        self, docker: str, container_id: str, profile: dict[str, Any]
    ) -> None:
        self._argv = build_relay_argv(docker, container_id, profile)
        self._host = profile["relay_host_ip"]
        self._listener: socket.socket | None = None
        self._accept_thread: threading.Thread | None = None
        self._connections: set[socket.socket] = set()
        self._processes: set[subprocess.Popen[bytes]] = set()
        self._workers: list[threading.Thread] = []
        self._lock = threading.Lock()
        self._stopping = threading.Event()
        self.port: int | None = None

    def start(self) -> int:
        if self._listener is not None:
            raise RehearsalFailure("environment", "relay_already_started")
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((self._host, 0))
        bound_host, bound_port = listener.getsockname()
        if bound_host != "127.0.0.1" or not (1 <= bound_port <= 65535):
            listener.close()
            raise RehearsalFailure("environment", "relay_binding_mismatch")
        listener.listen(8)
        listener.settimeout(0.2)
        self._listener = listener
        self.port = bound_port
        self._accept_thread = threading.Thread(
            target=self._accept_loop, name="status-confirm-btr-relay", daemon=True
        )
        self._accept_thread.start()
        return bound_port

    def _accept_loop(self) -> None:
        assert self._listener is not None
        while not self._stopping.is_set():
            try:
                connection, _address = self._listener.accept()
            except TimeoutError:
                continue
            except OSError:
                break
            with self._lock:
                self._connections.add(connection)
            worker = threading.Thread(
                target=self._bridge,
                args=(connection,),
                name="status-confirm-btr-relay-connection",
                daemon=True,
            )
            with self._lock:
                self._workers.append(worker)
            worker.start()

    def _bridge(self, connection: socket.socket) -> None:
        process: subprocess.Popen[bytes] | None = None
        try:
            process = subprocess.Popen(
                self._argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                shell=False,
                bufsize=0,
            )
            assert process.stdin is not None
            assert process.stdout is not None
            with self._lock:
                self._processes.add(process)

            def socket_to_process() -> None:
                try:
                    while not self._stopping.is_set():
                        payload = connection.recv(65536)
                        if not payload:
                            break
                        process.stdin.write(payload)
                        process.stdin.flush()
                except (BrokenPipeError, OSError):
                    pass
                finally:
                    try:
                        process.stdin.close()
                    except OSError:
                        pass

            def process_to_socket() -> None:
                try:
                    while not self._stopping.is_set():
                        payload = os.read(process.stdout.fileno(), 65536)
                        if not payload:
                            break
                        connection.sendall(payload)
                except OSError:
                    pass

            upstream = threading.Thread(target=socket_to_process, daemon=True)
            downstream = threading.Thread(target=process_to_socket, daemon=True)
            upstream.start()
            downstream.start()
            upstream.join()
            downstream.join()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=3)
        except (OSError, subprocess.SubprocessError):
            pass
        finally:
            try:
                connection.close()
            except OSError:
                pass
            with self._lock:
                self._connections.discard(connection)
                if process is not None:
                    self._processes.discard(process)

    def stop(self) -> None:
        self._stopping.set()
        if self._listener is not None:
            self._listener.close()
        if self._accept_thread is not None:
            self._accept_thread.join(timeout=2)
        with self._lock:
            connections = list(self._connections)
            processes = list(self._processes)
            workers = list(self._workers)
        for connection in connections:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for worker in workers:
            worker.join(timeout=3)
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=3)


def _image_id(docker: str, profile: dict[str, Any]) -> str:
    result = catalogue._run(  # noqa: SLF001
        [docker, "image", "inspect", "--format", "{{.Id}}", profile["image_reference"]],
        None,
        profile["command_timeout_seconds"],
        4096,
    )
    image_id = result.stdout.decode("utf-8").strip()
    if result.returncode != 0 or not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
        raise RehearsalFailure("environment", "local_image_unavailable")
    return image_id


def _wait_ready(docker: str, container_id: str, profile: dict[str, Any]) -> None:
    deadline = time.monotonic() + profile["startup_timeout_seconds"]
    stable = 0
    while time.monotonic() < deadline:
        ready = catalogue._run(  # noqa: SLF001
            [
                docker,
                "exec",
                container_id,
                "pg_isready",
                "--username",
                profile["postgres_user"],
                "--dbname",
                profile["postgres_database"],
                "--host",
                "/var/run/postgresql",
                "--quiet",
            ],
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        version = catalogue._run(  # noqa: SLF001
            catalogue._psql_argv(  # noqa: SLF001
                docker, container_id, profile, tuples_only=True
            ),
            b"SHOW server_version_num;\n",
            profile["command_timeout_seconds"],
            4096,
        )
        value = version.stdout.decode("utf-8").strip()
        if ready.returncode == 0 and version.returncode == 0 and value.startswith("16"):
            stable += 1
            if stable == profile["readiness_observations"]:
                return
        else:
            stable = 0
        time.sleep(0.25)
    raise RehearsalFailure("environment", "postgresql_readiness_timeout")


def _install_database(
    docker: str, container_id: str, contract: dict[str, Any]
) -> bytes:
    profile = contract["docker_profile"]
    catalogue._psql(  # noqa: SLF001
        catalogue._run,  # noqa: SLF001
        docker,
        container_id,
        profile,
        BOOTSTRAP_SQL,
        single_transaction=True,
    )
    offline_sql = catalogue._generate_offline_sql(contract)  # noqa: SLF001
    catalogue._psql(  # noqa: SLF001
        catalogue._run,  # noqa: SLF001
        docker,
        container_id,
        profile,
        offline_sql,
        single_transaction=True,
    )
    catalogue._psql(  # noqa: SLF001
        catalogue._run,  # noqa: SLF001
        docker,
        container_id,
        profile,
        CORRELATION_SQL,
        single_transaction=True,
    )
    return offline_sql


def _engine(host_port: int, profile: dict[str, Any]) -> Engine:
    url = (
        f"postgresql+{profile['sqlalchemy_driver']}://{profile['postgres_user']}:"
        f"{profile['postgres_password']}@{profile['relay_host_ip']}:{host_port}/"
        f"{profile['postgres_database']}"
    )
    engine = create_engine(
        url,
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5, "application_name": "emr4_status_btr"},
    )
    with engine.connect() as connection:
        version = connection.execute(text("SHOW server_version_num")).scalar_one()
        if not str(version).startswith("16"):
            engine.dispose()
            raise RehearsalFailure("environment", "host_connection_version_mismatch")
    return engine


def _fixture(index: int) -> Fixture:
    practice_id = UUID(int=0x10000000000040008000000000000000 + index)
    appointment_id = UUID(int=0x20000000000040008000000000000000 + index)
    actor_id = UUID(int=0x30000000000040008000000000000000 + index)
    session_id = f"synthetic-session-{index:02d}"
    actor_text = str(actor_id)
    return Fixture(
        index=index,
        practice_id=practice_id,
        appointment_id=appointment_id,
        actor_id=actor_id,
        actor_text=actor_text,
        audit_id=UUID(int=0x40000000000040008000000000000000 + index),
        idempotency_key_hash=_sha256(f"idempotency:{index}"),
        request_body_hash=_sha256(f"request:{index}"),
        session_digest=physical.status_confirm_session_binding_digest(
            secret=b"status-confirm-btr-synthetic-secret",
            practice_id=practice_id,
            actor_user_id=actor_text,
            authenticated_session_id=session_id,
        ),
        session_id=session_id,
    )


def _seed_base(engine: Engine, fixture: Fixture, *, appointment: bool = True) -> None:
    with engine.begin() as connection:
        connection.execute(
            text("INSERT INTO practices(id, name, timezone, hive_mind_opt_in) VALUES (:id, :name, 'Australia/Sydney', false)"),
            {"id": fixture.practice_id, "name": f"Synthetic Practice {fixture.index:02d}"},
        )
        if appointment:
            connection.execute(
                text(
                    "INSERT INTO appointments(id, practice_id, practitioner_id, start_time, appointment_date, start_time_local, duration_minutes, status, booked_via) "
                    "VALUES (:id, :practice_id, :practitioner_id, '2026-08-12 09:00:00+10', '2026-08-12', '09:00:00', 15, 'Booked', 'Receptionist')"
                ),
                {
                    "id": fixture.appointment_id,
                    "practice_id": fixture.practice_id,
                    "practitioner_id": UUID(int=0x50000000000040008000000000000000 + fixture.index),
                },
            )


def _seed_classification(engine: Engine, fixture: Fixture, kind: str) -> None:
    command_id = UUID(int=0x60000000000040008000000000000000 + fixture.index)
    base = {
        "id": command_id,
        "practice": fixture.practice_id,
        "actor": fixture.actor_text,
        "key": fixture.idempotency_key_hash,
        "request": fixture.request_body_hash,
        "target": fixture.appointment_id,
        "session_digest": fixture.session_digest,
    }
    with engine.begin() as connection:
        if kind == "in_progress_not_replayable":
            connection.execute(
                text(
                    "INSERT INTO appointment_command_idempotency(id, practice_id, actor_user_id, actor_role, operation_id, route_family, idempotency_key_hash, request_body_hash, state, target_appointment_id, session_binding_digest) "
                    "VALUES (:id, :practice, :actor, 'Receptionist', 'confirmAppointmentStatusProposal', 'status-confirm', :key, :request, 'in_progress', :target, :session_digest)"
                ),
                base,
            )
            return
        if kind == "legacy_receipt_not_replayable":
            connection.execute(
                text(
                    "INSERT INTO appointment_command_idempotency(id, practice_id, actor_user_id, actor_role, operation_id, route_family, idempotency_key_hash, request_body_hash, state, target_appointment_id, session_binding_digest, response_status_code, response_body_hash, response_body_json, result_kind) "
                    "VALUES (:id, :practice, :actor, 'Receptionist', 'confirmAppointmentStatusProposal', 'status-confirm', :key, :request, 'completed', :target, :session_digest, 200, :hash, '{}'::jsonb, 'legacy_result')"
                ),
                {**base, "hash": "0" * 64},
            )
            return
        if kind != "receipt_integrity_failure":
            raise AssertionError("unknown classification seed")
        response_bytes = physical.canonical_status_confirm_response_bytes(
            appointment_id=fixture.appointment_id,
            status="Arrived",
            status_reason_code=None,
            waiting_area_id=None,
            warning_codes=(),
        )
        connection.execute(
            text(
                "INSERT INTO appointment_command_idempotency(id, practice_id, actor_user_id, actor_role, operation_id, route_family, idempotency_key_hash, request_body_hash, state, target_appointment_id, session_binding_digest) "
                "VALUES (:id, :practice, :actor, 'Receptionist', 'confirmAppointmentStatusProposal', 'status-confirm', :key, :request, 'in_progress', :target, :session_digest)"
            ),
            base,
        )
        connection.execute(
            text(
                "INSERT INTO appointment_audit_log(id, practice_id, appointment_id, confirmed_by_user_id, action, status_before, status_after, confirmed_warnings, command_id, bernie_session_id) "
                "VALUES (:audit, :practice, :target, :actor_uuid, 'status_change', 'Booked', 'Arrived', '[]'::jsonb, :id, :session_id)"
            ),
            {
                **base,
                "audit": fixture.audit_id,
                "actor_uuid": fixture.actor_id,
                "session_id": fixture.session_id,
            },
        )
        connection.execute(
            text(
                "UPDATE appointment_command_idempotency SET state='completed', response_status_code=200, response_body_hash=:bad_hash, response_body_json=CAST(:body AS jsonb), result_kind='confirmed_write', audit_log_id=:audit, completed_receipt_version=1, pre_state_version=1, post_state_version=2, response_body_canonical_bytes=:bytes WHERE id=:id"
            ),
            {
                **base,
                "bad_hash": "0" * 64,
                "body": response_bytes.decode("utf-8"),
                "audit": fixture.audit_id,
                "bytes": response_bytes,
            },
        )


def _statement_token(statement: str) -> str | None:
    normalized = " ".join(statement.lower().replace('"', "").split())
    if " from practices " in f" {normalized} " and " for share" in normalized:
        return "practice_for_share"
    if " from appointments " in f" {normalized} " and " for update" in normalized:
        return "appointment_for_update"
    if (
        "insert into appointment_command_idempotency" in normalized
        and "on conflict" in normalized
    ):
        return "idempotency_insert_on_conflict"
    if (
        " from appointment_command_idempotency " in f" {normalized} "
        and " for update" in normalized
    ):
        return "idempotency_for_update"
    return None


def _stage_audit(db: Session, decision: physical.StatusConfirmPhysicalDecision, fixture: Fixture) -> AppointmentAuditLog:
    decision.appointment.status = AppointmentStatus.Arrived
    audit = AppointmentAuditLog(
        id=fixture.audit_id,
        practice_id=fixture.practice_id,
        appointment_id=fixture.appointment_id,
        confirmed_by_user_id=fixture.actor_id,
        action=AppointmentAuditAction.status_change,
        status_before=AppointmentStatus.Booked,
        status_after=AppointmentStatus.Arrived,
        status_reason_code=None,
        confirmed_warnings=[],
        command_id=decision.record.id,
        bernie_session_id=fixture.session_id,
    )
    db.add(audit)
    return audit


def _stage_complete(db: Session, decision: physical.StatusConfirmPhysicalDecision, fixture: Fixture) -> bytes:
    audit = _stage_audit(db, decision, fixture)
    db.flush()
    db.refresh(decision.appointment)
    response_bytes = physical.canonical_status_confirm_response_bytes(
        appointment_id=fixture.appointment_id,
        status=decision.appointment.status,
        status_reason_code=decision.appointment.status_reason_code,
        waiting_area_id=decision.appointment.waiting_area_id,
        warning_codes=(),
    )
    record = decision.record
    record.state = "completed"
    record.response_status_code = 200
    record.response_body_hash = physical.status_confirm_response_digest(response_bytes)
    record.response_body_json = json.loads(response_bytes)
    record.result_kind = "confirmed_write"
    record.audit_log_id = audit.id
    record.bernie_session_id = fixture.session_id
    record.completed_receipt_version = 1
    record.pre_state_version = decision.pre_state_version
    record.post_state_version = decision.appointment.appointment_state_version
    record.response_body_canonical_bytes = response_bytes
    db.flush()
    return response_bytes


def _invoke(
    engine: Engine,
    fixture: Fixture,
    *,
    action: str = "none",
    practice_active: bool = True,
    authority_sequence: tuple[bool, ...] = (True, True),
    request_body_hash: str | None = None,
    session_digest: bytes | None = None,
) -> Invocation:
    tokens: list[str] = []
    authority_calls = 0
    response_bytes: bytes | None = None

    def observe(_conn, _cursor, statement, _parameters, _context, _executemany) -> None:
        token = _statement_token(statement)
        if token is not None:
            tokens.append(token)

    def current_authority(_practice, _appointment) -> bool:
        nonlocal authority_calls
        authority_calls += 1
        expected = (
            ["practice_for_share", "appointment_for_update"]
            if authority_calls == 1
            else list(
                (
                    "practice_for_share",
                    "appointment_for_update",
                    "idempotency_insert_on_conflict",
                    "idempotency_for_update",
                )
            )
        )
        if tokens != expected:
            raise RehearsalFailure("transaction", "lock_authority_order_mismatch")
        if authority_calls > len(authority_sequence):
            raise RehearsalFailure("transaction", "authority_call_overrun")
        return authority_sequence[authority_calls - 1]

    event.listen(engine, "before_cursor_execute", observe)
    try:
        with Session(engine, expire_on_commit=False) as db:
            with physical.status_confirm_locked_transaction(
                db,
                practice_id=fixture.practice_id,
                target_appointment_id=fixture.appointment_id,
                actor_user_id=fixture.actor_text,
                actor_role="Receptionist",
                idempotency_key_hash=fixture.idempotency_key_hash,
                request_body_hash=request_body_hash or fixture.request_body_hash,
                session_binding_digest=session_digest or fixture.session_digest,
                practice_is_active=lambda _practice: practice_active,
                current_authority=current_authority,
                lock_timeout_ms=1500,
            ) as decision:
                outcome = decision.kind
                if decision.kind == "new_command":
                    if action == "complete":
                        response_bytes = _stage_complete(db, decision, fixture)
                    elif action == "appointment":
                        decision.appointment.status = AppointmentStatus.Arrived
                    elif action == "appointment_audit":
                        _stage_audit(db, decision, fixture)
                    elif action == "abort_complete":
                        _stage_complete(db, decision, fixture)
                        raise OuterAbort("fixed authored-synthetic outer abort")
                    elif action != "none":
                        raise AssertionError("unknown transaction action")
                elif decision.response_body_canonical_bytes is not None:
                    response_bytes = decision.response_body_canonical_bytes
        return Invocation(
            outcome=outcome,
            response_digest=(
                physical.status_confirm_response_digest(response_bytes)
                if response_bytes is not None
                else None
            ),
            authority_calls=authority_calls,
            statement_tokens=tuple(tokens),
        )
    except physical.StatusConfirmTargetUnavailable:
        outcome = "target_unavailable"
    except physical.StatusConfirmAuthorityRevoked:
        outcome = "authority_revoked"
    except physical.StatusConfirmScaffoldIncomplete:
        outcome = "scaffold_incomplete"
    except OuterAbort:
        outcome = "outer_abort"
    finally:
        event.remove(engine, "before_cursor_execute", observe)
    return Invocation(
        outcome=outcome,
        response_digest=None,
        authority_calls=authority_calls,
        statement_tokens=tuple(tokens),
    )


def _snapshot(engine: Engine, fixture: Fixture) -> dict[str, Any]:
    with engine.connect() as connection:
        appointment = connection.execute(
            text("SELECT status, appointment_state_version FROM appointments WHERE practice_id=:practice AND id=:appointment"),
            {"practice": fixture.practice_id, "appointment": fixture.appointment_id},
        ).one_or_none()
        params = {"practice": fixture.practice_id, "appointment": fixture.appointment_id}
        audit_count = connection.execute(
            text("SELECT count(*) FROM appointment_audit_log WHERE practice_id=:practice AND appointment_id=:appointment"),
            params,
        ).scalar_one()
        idempotency_rows = connection.execute(
            text("SELECT count(*) FROM appointment_command_idempotency WHERE practice_id=:practice AND target_appointment_id=:appointment"),
            params,
        ).scalar_one()
        complete_count = connection.execute(
            text("SELECT count(*) FROM appointment_command_idempotency WHERE practice_id=:practice AND target_appointment_id=:appointment AND completed_receipt_version=1"),
            params,
        ).scalar_one()
        correlated = connection.execute(
            text(
                "SELECT count(*) FROM appointment_command_idempotency i JOIN appointment_audit_log a ON a.id=i.audit_log_id AND a.command_id=i.id AND a.practice_id=i.practice_id WHERE i.practice_id=:practice AND i.target_appointment_id=:appointment AND a.appointment_id=:appointment"
            ),
            params,
        ).scalar_one()
    return {
        "status": appointment[0] if appointment is not None else None,
        "version": appointment[1] if appointment is not None else None,
        "audit_count": audit_count,
        "idempotency_rows": idempotency_rows,
        "completed_v1_count": complete_count,
        "correlated_count": correlated,
    }


def _assert_scenario(
    scenario: dict[str, Any], before: dict[str, Any], after: dict[str, Any], invocation: Invocation, disclosure_count: int
) -> None:
    if invocation.outcome != scenario["expected"]:
        raise RehearsalFailure("scenario", f"{scenario['id']}_outcome_mismatch")
    before_version = before["version"] or 0
    after_version = after["version"] or 0
    if after_version - before_version != scenario["appointment_delta"]:
        raise RehearsalFailure("scenario", f"{scenario['id']}_appointment_delta_mismatch")
    if after["audit_count"] - before["audit_count"] != scenario["audit_delta"]:
        raise RehearsalFailure("scenario", f"{scenario['id']}_audit_delta_mismatch")
    if after["completed_v1_count"] - before["completed_v1_count"] != scenario["receipt_delta"]:
        raise RehearsalFailure("scenario", f"{scenario['id']}_receipt_delta_mismatch")
    if disclosure_count != scenario["disclosure_count"]:
        raise RehearsalFailure("scenario", f"{scenario['id']}_disclosure_mismatch")
    if invocation.authority_calls != scenario["authority_calls"]:
        raise RehearsalFailure("scenario", f"{scenario['id']}_authority_count_mismatch")
    if scenario["appointment_delta"] == 1:
        if after["status"] != "Arrived" or after["correlated_count"] != 1:
            raise RehearsalFailure("scenario", f"{scenario['id']}_write_set_mismatch")
    elif after != before:
        raise RehearsalFailure("scenario", f"{scenario['id']}_rollback_or_no_effect_mismatch")


def _run_scenario(engine: Engine, scenario: dict[str, Any], index: int) -> dict[str, Any]:
    fixture = _fixture(index)
    kind = scenario["kind"]
    _seed_base(engine, fixture, appointment=kind != "target_absent")
    if kind in {
        "in_progress_not_replayable",
        "legacy_receipt_not_replayable",
        "receipt_integrity_failure",
    }:
        _seed_classification(engine, fixture, kind)
    before = _snapshot(engine, fixture)
    disclosure_count = 0
    traces: list[str] = []

    if kind == "clean_commit":
        invocation = _invoke(engine, fixture, action="complete")
        disclosure_count = int(invocation.response_digest is not None)
    elif kind == "response_loss_retry":
        first = _invoke(engine, fixture, action="complete")
        retry = _invoke(engine, fixture)
        if first.response_digest is None or retry.response_digest != first.response_digest:
            raise RehearsalFailure("scenario", "BTR-S02_stored_bytes_mismatch")
        invocation = Invocation(
            retry.outcome,
            retry.response_digest,
            first.authority_calls + retry.authority_calls,
            first.statement_tokens + retry.statement_tokens,
        )
        disclosure_count = 1
    elif kind in {"request_digest_conflict", "session_binding_conflict"}:
        first = _invoke(engine, fixture, action="complete")
        conflict = _invoke(
            engine,
            fixture,
            request_body_hash=(
                _sha256(f"changed-request:{index}")
                if kind == "request_digest_conflict"
                else None
            ),
            session_digest=(
                _sha256(f"changed-session:{index}").encode("ascii")[:32]
                if kind == "session_binding_conflict"
                else None
            ),
        )
        if conflict.response_digest is not None:
            raise RehearsalFailure("scenario", f"{scenario['id']}_conflict_disclosed")
        invocation = Invocation(
            conflict.outcome,
            None,
            first.authority_calls + conflict.authority_calls,
            first.statement_tokens + conflict.statement_tokens,
        )
        disclosure_count = int(first.response_digest is not None)
    elif kind == "inactive_practice":
        invocation = _invoke(engine, fixture, practice_active=False, authority_sequence=())
    elif kind == "target_absent":
        invocation = _invoke(engine, fixture, authority_sequence=())
    elif kind == "first_authority_revoked":
        invocation = _invoke(engine, fixture, authority_sequence=(False,))
    elif kind == "second_authority_revoked":
        invocation = _invoke(engine, fixture, authority_sequence=(True, False))
    elif kind == "replay_after_revocation":
        first = _invoke(engine, fixture, action="complete")
        revoked = _invoke(engine, fixture, authority_sequence=(False,))
        invocation = Invocation(
            revoked.outcome,
            None,
            first.authority_calls + revoked.authority_calls,
            first.statement_tokens + revoked.statement_tokens,
        )
        disclosure_count = int(first.response_digest is not None)
    elif kind == "empty_write_set":
        invocation = _invoke(engine, fixture)
    elif kind == "appointment_only":
        invocation = _invoke(engine, fixture, action="appointment")
    elif kind == "appointment_audit_only":
        invocation = _invoke(engine, fixture, action="appointment_audit")
    elif kind == "complete_write_outer_abort":
        invocation = _invoke(engine, fixture, action="abort_complete")
    else:
        invocation = _invoke(engine, fixture)

    traces.extend(invocation.statement_tokens)
    after = _snapshot(engine, fixture)
    _assert_scenario(scenario, before, after, invocation, disclosure_count)
    return {
        "id": scenario["id"],
        "status": "passed",
        "outcome": invocation.outcome,
        "appointment_version_before": before["version"],
        "appointment_version_after": after["version"],
        "audit_delta": after["audit_count"] - before["audit_count"],
        "completed_receipt_delta": after["completed_v1_count"] - before["completed_v1_count"],
        "disclosure_count": disclosure_count,
        "authority_calls": invocation.authority_calls,
        "statement_tokens": traces,
    }


def _catalogue_check(engine: Engine) -> dict[str, Any]:
    with engine.connect() as connection:
        head = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        constraints = connection.execute(
            text(
                "SELECT count(*) FROM pg_constraint WHERE conname IN ('fk_appt_cmd_idem_practice_target','fk_appt_audit_log_practice_appointment','fk_appt_audit_log_practice_command','fk_appt_cmd_idem_practice_audit','ck_appt_cmd_idem_status_receipt_v1_complete')"
            )
        ).scalar_one()
        indexes = connection.execute(
            text(
                "SELECT count(*) FROM pg_class WHERE relkind='i' AND relname IN ('uq_appt_audit_log_command_id','uq_appt_cmd_idem_audit_log_id')"
            )
        ).scalar_one()
    if head != "w2x3y4z5a6b7" or constraints != 5 or indexes != 2:
        raise RehearsalFailure("catalogue", "transaction_schema_mismatch")
    return {"head": head, "selected_constraints": constraints, "correlation_indexes": indexes}


def _cleanup(
    docker: str,
    *,
    container_id: str | None,
    container_name: str,
    network_id: str | None,
    network_name: str,
    nonce: str,
    image_id: str | None,
    profile: dict[str, Any],
) -> dict[str, Any]:
    container_status = "not_created"
    network_status = "not_created"
    if container_id is not None:
        inspected_result, inspected = _inspect_one(
            docker, "container", container_id, profile["command_timeout_seconds"]
        )
        owned = (
            _container_profile(
                inspected,
                container_id=container_id,
                name=container_name,
                nonce=nonce,
                image_id=image_id or "",
                network_id=network_id or "",
                profile=profile,
            )
            if inspected is not None
            else False
        )
        if inspected_result.returncode != 0 or not owned:
            return {"status": "cleanup_ownership_unverified", "object": "container"}
        removed = catalogue._run(  # noqa: SLF001
            [docker, "container", "rm", "--force", container_id],
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        absent, _ = _inspect_one(
            docker, "container", container_id, profile["command_timeout_seconds"]
        )
        if removed.returncode != 0 or not _exact_absence(absent, "container"):
            return {"status": "cleanup_absence_unverified", "object": "container"}
        container_status = "container_absent"
    if network_id is not None:
        inspected_result, inspected = _inspect_one(
            docker, "network", network_id, profile["command_timeout_seconds"]
        )
        if (
            inspected_result.returncode != 0
            or inspected is None
            or not _network_owned(
                inspected,
                network_id=network_id,
                name=network_name,
                nonce=nonce,
                profile=profile,
                require_empty=True,
            )
        ):
            return {"status": "cleanup_ownership_unverified", "object": "network"}
        removed = catalogue._run(  # noqa: SLF001
            [docker, "network", "rm", network_id],
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        absent, _ = _inspect_one(
            docker, "network", network_id, profile["command_timeout_seconds"]
        )
        if removed.returncode != 0 or not _exact_absence(absent, "network"):
            return {"status": "cleanup_absence_unverified", "object": "network"}
        network_status = "network_absent"
    return {
        "status": "cleanup_verified",
        "container": container_status,
        "network": network_status,
        "container_id_sha256": _sha256(container_id or "not-created"),
        "network_id_sha256": _sha256(network_id or "not-created"),
    }


def _failure_evidence(error: RehearsalFailure, lifecycle: list[str], cleanup: dict[str, Any]) -> dict[str, Any]:
    detail = error.detail if isinstance(error.detail, bytes) else str(error.detail).encode()
    return {
        "schema_version": "raisa.status_confirm_behavior_transaction_evidence.v1",
        "result": "rehearsal_failed",
        "evidence_label": "authored_synthetic_provider_free_disposable_postgresql_behavior_transaction",
        "source_head": "d4f637d6c2afadccc95d4b7ae8cfc1f522444133",
        "lifecycle": lifecycle,
        "failure": {"stage": error.stage, "code": error.code, "detail_sha256": _sha256(detail)},
        "cleanup": cleanup,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def run_rehearsal() -> dict[str, Any]:
    lifecycle: list[str] = []
    cleanup: dict[str, Any] = {"status": "not_needed"}
    contract: dict[str, Any] | None = None
    source_hashes: dict[str, str] = {}
    docker = ""
    image_id: str | None = None
    network_id: str | None = None
    container_id: str | None = None
    network_name = ""
    container_name = ""
    nonce = secrets.token_hex(16)
    engine: Engine | None = None
    relay: DockerExecRelay | None = None
    evidence: dict[str, Any] | None = None
    error: RehearsalFailure | None = None
    started = time.monotonic()
    try:
        contract, source_hashes = verify_contract()
        lifecycle.append("contract_and_sources_verified")
        profile = contract["docker_profile"]
        docker = shutil.which(profile["executable"]) or ""
        if not docker:
            raise RehearsalFailure("environment", "docker_client_missing")
        image_id = _image_id(docker, profile)
        lifecycle.append("local_image_verified")
        suffix = secrets.token_hex(8)
        network_name = profile["network_name_prefix"] + suffix
        container_name = profile["container_name_prefix"] + suffix
        network_result = catalogue._run(  # noqa: SLF001
            build_network_argv(docker, network_name, nonce, profile),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        network_id = network_result.stdout.decode("utf-8").strip()
        if network_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{64}", network_id):
            raise RehearsalFailure("environment", "network_create_failed", network_result.stderr)
        inspected_result, inspected_network = _inspect_one(
            docker, "network", network_id, profile["command_timeout_seconds"]
        )
        if (
            inspected_result.returncode != 0
            or inspected_network is None
            or not _network_owned(
                inspected_network,
                network_id=network_id,
                name=network_name,
                nonce=nonce,
                profile=profile,
                require_empty=True,
            )
        ):
            raise RehearsalFailure("environment", "network_profile_mismatch")
        lifecycle.append("owned_internal_network_verified")
        container_result = catalogue._run(  # noqa: SLF001
            build_container_argv(docker, container_name, nonce, network_id, profile),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        container_id = container_result.stdout.decode("utf-8").strip()
        if container_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{64}", container_id):
            raise RehearsalFailure("environment", "container_create_failed", container_result.stderr)
        inspected_result, inspected_container = _inspect_one(
            docker, "container", container_id, profile["command_timeout_seconds"]
        )
        owned = (
            _container_profile(
                inspected_container,
                container_id=container_id,
                name=container_name,
                nonce=nonce,
                image_id=image_id,
                network_id=network_id,
                profile=profile,
            )
            if inspected_container is not None
            else False
        )
        if inspected_result.returncode != 0 or not owned:
            raise RehearsalFailure("environment", "container_profile_mismatch")
        lifecycle.append("internal_container_profile_verified")
        _wait_ready(docker, container_id, profile)
        lifecycle.append("postgresql_16_ready")
        offline_sql = _install_database(docker, container_id, contract)
        lifecycle.append("transaction_schema_installed")
        relay = DockerExecRelay(docker, container_id, profile)
        host_port = relay.start()
        lifecycle.append("fixed_loopback_relay_started")
        engine = _engine(host_port, profile)
        catalogue_facts = _catalogue_check(engine)
        lifecycle.append("host_sqlalchemy_catalogue_verified")
        scenario_results = [
            _run_scenario(engine, scenario, index)
            for index, scenario in enumerate(contract["scenarios"], start=1)
        ]
        lifecycle.append("sixteen_serial_scenarios_verified")
        if time.monotonic() - started > profile["total_timeout_seconds"]:
            raise RehearsalFailure("environment", "total_timeout_exceeded")
        evidence = {
            "schema_version": "raisa.status_confirm_behavior_transaction_evidence.v1",
            "result": PASS_RESULT,
            "evidence_label": contract["evidence_label"],
            "source_head": contract["source_head"],
            "contract_sha256": _sha256(CONTRACT_PATH.read_bytes()),
            "source_hashes": source_hashes,
            "hostile_mutations_rejected": HOSTILE_MUTATION_TARGET,
            "environment": {
                "postgresql_major": 16,
                "image_reference": profile["image_reference"],
                "image_id_sha256": _sha256(image_id),
                "network_internal": True,
                "docker_published_ports": False,
                "host_transport": "fixed_in_process_ipv4_loopback_relay",
                "storage": "container_local_tmpfs",
            },
            "offline_sql": {
                "range": contract["alembic"]["offline_range"],
                "body_sha256": _sha256(offline_sql),
                "body_bytes": len(offline_sql),
            },
            "catalogue": catalogue_facts,
            "scenarios": scenario_results,
            "lifecycle": lifecycle,
            "cleanup": {"status": "pending"},
            "claim_boundary": CLAIM_BOUNDARY,
        }
    except RehearsalFailure as caught:
        error = caught
    except Exception as caught:  # fail closed without persisting raw exception text
        error = RehearsalFailure("harness", "unexpected_exception", type(caught).__name__)
    finally:
        if engine is not None:
            engine.dispose()
        if relay is not None:
            relay.stop()
            lifecycle.append("fixed_loopback_relay_stopped")
        if contract is not None and docker:
            cleanup = _cleanup(
                docker,
                container_id=container_id,
                container_name=container_name,
                network_id=network_id,
                network_name=network_name,
                nonce=nonce,
                image_id=image_id,
                profile=contract["docker_profile"],
            )
        if cleanup.get("status") == "cleanup_verified":
            lifecycle.append("cleanup_verified")
        if error is None and cleanup.get("status") != "cleanup_verified":
            error = RehearsalFailure("cleanup", cleanup.get("status", "cleanup_failed"))
        if error is not None:
            evidence = _failure_evidence(error, lifecycle, cleanup)
        else:
            assert evidence is not None
            evidence["lifecycle"] = lifecycle
            evidence["cleanup"] = cleanup
    assert evidence is not None
    Draft202012Validator(_load_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)
    return evidence


def write_evidence(evidence: dict[str, Any]) -> Path:
    target = EVIDENCE_PATH if evidence["result"] == PASS_RESULT else FAILURE_EVIDENCE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def main() -> int:
    if len(sys.argv) != 1:
        print('{"result":"rehearsal_failed","code":"caller_arguments_forbidden"}')
        return 2
    evidence = run_rehearsal()
    path = write_evidence(evidence)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "cleanup": evidence["cleanup"]["status"],
                "evidence": str(path.relative_to(ROOT)).replace("\\", "/"),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == PASS_RESULT else 1


if __name__ == "__main__":
    raise SystemExit(main())
