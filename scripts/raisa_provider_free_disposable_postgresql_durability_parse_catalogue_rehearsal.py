"""Run one fixed, provider-free disposable PostgreSQL 16 catalogue rehearsal.

The module has no caller-selected runtime inputs. It verifies fixed repository
contracts before resolving ``docker.exe`` and can operate only one uniquely
named, labelled, networkless, tmpfs-backed container. SQL is supplied on stdin;
no workspace path is mounted. Cleanup can target only the captured container ID
after exact ownership and containment re-verification.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
REHEARSAL_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-parse-catalogue-rehearsal"
)
CONTRACT_PATH = REHEARSAL_DIR / "rehearsal-contract.json"
PREREQUISITE_PATH = REHEARSAL_DIR / "synthetic-prerequisite-contract.json"
EVIDENCE_PATH = REHEARSAL_DIR / "provider-free-disposable-postgresql-evidence.json"

EXPECTED_CONTRACT_PATH = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-parse-catalogue-rehearsal/rehearsal-contract.json"
)
EXPECTED_PREREQUISITE_PATH = (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-parse-catalogue-rehearsal/synthetic-prerequisite-contract.json"
)
EXPECTED_CONTRACT_SHA256 = (
    "sha256:0283abb17666ce5abdacd506666ec3d5130a3cc74f45e18324a9ee23f8ceb00b"
)
EXPECTED_PREREQUISITE_SHA256 = (
    "sha256:0cafc71c8368b227fdb626df386b6ebdac659a77c279901ac2a3e4aa844c0b11"
)

FABRIC_SCHEMA = "emr4_context_fabric"
IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
POSTGRES_16_VERSION_NUM = re.compile(rb"^16[0-9]{4}$")
VERBOSE_SQLSTATE = re.compile(rb"(?:ERROR|FATAL):\s+([0-9A-Z]{5}):")
VERBOSE_PSQL_ERROR_LINE = re.compile(
    rb"psql:<stdin>:([1-9][0-9]*):\s+(?:ERROR|FATAL):"
)
VERBOSE_STATEMENT_LINE = re.compile(rb"(?:^|\n)LINE\s+([1-9][0-9]*):", re.MULTILINE)
VERBOSE_POSITION = re.compile(
    rb"(?:^|\n)(?:POSITION|INTERNAL POSITION):\s+([1-9][0-9]*)",
    re.MULTILINE,
)
VERBOSE_CONTEXT_LINE = re.compile(
    rb"(?:compilation of PL/pgSQL function[^\n]*?(?:near )?|PL/pgSQL function[^\n]*?)"
    rb"line\s+([1-9][0-9]*)",
    re.IGNORECASE,
)
ROLE_LINE = re.compile(
    r"^CREATE ROLE ([a-z][a-z0-9_]*) (NO)?LOGIN (NO)?INHERIT "
    r"NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;$",
    re.MULTILINE,
)
FORBIDDEN_ARTIFACT_TX = re.compile(
    r"^\s*(BEGIN|START\s+TRANSACTION|COMMIT|END|ROLLBACK|SAVEPOINT|"
    r"RELEASE\s+SAVEPOINT|PREPARE\s+TRANSACTION)\b",
    re.IGNORECASE | re.MULTILINE,
)
FORBIDDEN_META = re.compile(r"^\s*\\", re.MULTILINE)
DOLLAR_TAG = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*\$")

PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_durability_"
    "parse_catalogue_rehearsal_pass"
)
EVIDENCE_MODE = "provider_free_disposable_local_postgresql_authored_synthetic"
CLAIM_BOUNDARY = (
    "postgresql_16_exact_artifact_parse_atomic_installation_and_catalogue_shape_only"
)


class DockerOperation(str, Enum):
    IMAGE_INSPECT = "image_inspect"
    NAME_INSPECT = "name_inspect"
    RUN = "run"
    ID_INSPECT = "id_inspect"
    READY = "ready"
    READY_SQL = "ready_sql"
    PSQL_COMMAND = "psql_command"
    PSQL_FILE = "psql_file"
    REMOVE = "remove"
    ID_ABSENCE = "id_absence"


class RehearsalFailure(RuntimeError):
    def __init__(self, stage: str, code: str, detail: str = "") -> None:
        super().__init__(f"{stage}:{code}")
        self.stage = stage
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: bytes
    stderr: bytes


Runner = Callable[[list[str], bytes | None, float, int], ProcessResult]


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RehearsalFailure("contract", "json_object_required", str(path.name))
    return payload


def _canonical_sha(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _bytes_sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _bounded_digest(payload: bytes) -> dict[str, Any]:
    return {"byte_count": len(payload), "sha256": "sha256:" + _bytes_sha(payload)}


def _canonical_artifact(raw: bytes) -> bytes:
    if b"\r\n" in raw:
        without_pairs = raw.replace(b"\r\n", b"")
        if b"\r" in without_pairs:
            raise RehearsalFailure("parent", "lone_carriage_return")
        raw = raw.replace(b"\r\n", b"\n")
    elif b"\r" in raw:
        raise RehearsalFailure("parent", "lone_carriage_return")
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RehearsalFailure("parent", "artifact_not_utf8", str(error.start)) from error
    return raw


def _outside_dollar_quoted(sql: str) -> str:
    """Return only top-level text outside fixed PostgreSQL dollar bodies."""
    output: list[str] = []
    active_tag: str | None = None
    position = 0
    while position < len(sql):
        if active_tag is None:
            match = DOLLAR_TAG.search(sql, position)
            if match is None:
                output.append(sql[position:])
                break
            output.append(sql[position : match.start()])
            active_tag = match.group(0)
            position = match.end()
        else:
            closing = sql.find(active_tag, position)
            if closing < 0:
                raise RehearsalFailure("parent", "unterminated_dollar_quote")
            position = closing + len(active_tag)
            active_tag = None
    if active_tag is not None:
        raise RehearsalFailure("parent", "unterminated_dollar_quote")
    return "".join(output)


def _validate_contracts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], bytes]:
    if CONTRACT_PATH.relative_to(ROOT).as_posix() != EXPECTED_CONTRACT_PATH:
        raise RehearsalFailure("contract", "rehearsal_path_drift")
    if PREREQUISITE_PATH.relative_to(ROOT).as_posix() != EXPECTED_PREREQUISITE_PATH:
        raise RehearsalFailure("contract", "prerequisite_path_drift")
    contract = _json(CONTRACT_PATH)
    prerequisite = _json(PREREQUISITE_PATH)
    if _canonical_sha(contract) != EXPECTED_CONTRACT_SHA256:
        raise RehearsalFailure("contract", "rehearsal_contract_sha256")
    if _canonical_sha(prerequisite) != EXPECTED_PREREQUISITE_SHA256:
        raise RehearsalFailure("contract", "prerequisite_contract_sha256")
    if contract.get("schema_version") != (
        "emr4.disposable-postgresql-durability-rehearsal-contract.v1"
    ):
        raise RehearsalFailure("contract", "schema_version")
    if prerequisite.get("schema_version") != (
        "emr4.disposable-postgresql-synthetic-prerequisite-contract.v1"
    ):
        raise RehearsalFailure("contract", "prerequisite_schema_version")
    parent = contract["parent"]
    if not SHA256.fullmatch(parent["artifact_sha256"]):
        raise RehearsalFailure("parent", "invalid_sha_contract")
    artifact_path = ROOT / parent["artifact_path"]
    manifest_path = ROOT / parent["manifest_path"]
    manifest = _json(manifest_path)
    artifact = _canonical_artifact(artifact_path.read_bytes())
    if len(artifact) != parent["artifact_byte_count"]:
        raise RehearsalFailure("parent", "artifact_byte_count")
    if _bytes_sha(artifact) != parent["artifact_sha256"]:
        raise RehearsalFailure("parent", "artifact_sha256")
    for key in ("statement_count", "postgresql_major"):
        if manifest.get(key) != parent[key]:
            raise RehearsalFailure("parent", f"manifest_{key}")
    if len(manifest.get("phases", [])) != parent["phase_count"]:
        raise RehearsalFailure("parent", "manifest_phase_count")
    if manifest.get("sql_byte_count") != len(artifact):
        raise RehearsalFailure("parent", "manifest_sql_byte_count")
    if manifest.get("sql_sha256") != "sha256:" + _bytes_sha(artifact):
        raise RehearsalFailure("parent", "manifest_sql_sha256")
    grouped: dict[str, int] = {}
    for row in manifest.get("ordered_nodes", []):
        grouped[row["kind"]] = grouped.get(row["kind"], 0) + 1
    if grouped != contract["manifest_kind_counts"]:
        raise RehearsalFailure("parent", "manifest_kind_counts")
    if manifest.get("catalogue_assertions") != contract["catalogue_assertions"]:
        raise RehearsalFailure("parent", "catalogue_assertions")
    expected_digest_ids = set(contract["catalogue_query_ids"]) - {
        "server",
        "extensions",
    }
    expectation = contract.get("catalogue_expectation", {})
    mode = expectation.get("mode")
    expected_digests = expectation.get("expected_query_digests")
    if mode not in {"characterization_only", "exact_digest_bound"} or not isinstance(
        expected_digests, dict
    ):
        raise RehearsalFailure("contract", "catalogue_expectation")
    if mode == "characterization_only" and expected_digests:
        raise RehearsalFailure("contract", "characterization_digest_population")
    if mode == "exact_digest_bound":
        if set(expected_digests) != expected_digest_ids or any(
            not isinstance(value, str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", value)
            for value in expected_digests.values()
        ):
            raise RehearsalFailure("contract", "expected_catalogue_digests")
    decoded = artifact.decode("utf-8")
    top_level = _outside_dollar_quoted(decoded)
    if FORBIDDEN_ARTIFACT_TX.search(top_level):
        raise RehearsalFailure("parent", "transaction_control_present")
    if FORBIDDEN_META.search(top_level):
        raise RehearsalFailure("parent", "psql_meta_command_present")
    expected_roles = {
        row["identifier"]
        for row in manifest["ordered_nodes"]
        if row["kind"] == "ROLE"
    }
    parsed_roles = {match.group(1) for match in ROLE_LINE.finditer(decoded)}
    if parsed_roles != expected_roles:
        raise RehearsalFailure("parent", "role_statement_population")
    _validate_prerequisite(prerequisite)
    return contract, prerequisite, manifest, artifact


def _validate_prerequisite(contract: dict[str, Any]) -> None:
    expected_tables = {
        "appointments",
        "appointment_command_idempotency",
        "appointment_audit_log",
        "diary_committed_events",
    }
    tables = contract.get("tables", [])
    if {row.get("name") for row in tables} != expected_tables or len(tables) != 4:
        raise RehearsalFailure("contract", "prerequisite_table_population")
    for table in tables:
        if not IDENTIFIER.fullmatch(table["name"]):
            raise RehearsalFailure("contract", "unsafe_table_identifier")
        column_names = [column["name"] for column in table["columns"]]
        if len(column_names) != len(set(column_names)) or "xmin" in column_names:
            raise RehearsalFailure("contract", "prerequisite_columns")
        for column in table["columns"]:
            if not IDENTIFIER.fullmatch(column["name"]):
                raise RehearsalFailure("contract", "unsafe_column_identifier")
            if column["type"] not in {
                "uuid",
                "text",
                "timestamptz",
                "integer",
                "bigint",
                "jsonb",
            }:
                raise RehearsalFailure("contract", "unsafe_column_type")
            if column["default_sql"] not in {None, "15", "pg_catalog.now()"}:
                raise RehearsalFailure("contract", "unsafe_default")
        for constraint in table["constraints"]:
            if not IDENTIFIER.fullmatch(constraint["name"]):
                raise RehearsalFailure("contract", "unsafe_constraint_identifier")
            if constraint["kind"] not in {"PRIMARY KEY", "UNIQUE"}:
                raise RehearsalFailure("contract", "unsafe_constraint_kind")
            if not set(constraint["columns"]).issubset(column_names):
                raise RehearsalFailure("contract", "constraint_column_missing")


def render_prerequisite_sql(contract: dict[str, Any]) -> bytes:
    """Render the closed four-table empty prerequisite DDL."""
    _validate_prerequisite(contract)
    statements: list[str] = []
    for table in contract["tables"]:
        members: list[str] = []
        for column in table["columns"]:
            rendered = f'    "{column["name"]}" {column["type"]}'
            if not column["nullable"]:
                rendered += " NOT NULL"
            if column["default_sql"] is not None:
                rendered += " DEFAULT " + column["default_sql"]
            members.append(rendered)
        for constraint in table["constraints"]:
            columns = ", ".join(f'"{name}"' for name in constraint["columns"])
            members.append(
                f'    CONSTRAINT "{constraint["name"]}" '
                f'{constraint["kind"]} ({columns})'
            )
        statements.append(
            f'CREATE TABLE public."{table["name"]}" (\n'
            + ",\n".join(members)
            + "\n);"
        )
    return ("\n\n".join(statements) + "\n").encode("utf-8")


def _subprocess_runner(
    argv: list[str], stdin: bytes | None, timeout: float, cap: int
) -> ProcessResult:
    if not argv or Path(argv[0]).name.lower() != "docker.exe":
        raise RehearsalFailure("process", "executable_not_docker_exe")
    try:
        process = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except OSError as error:
        raise RehearsalFailure("process", "start_failed", str(error.errno)) from error
    if process.stdout is None or process.stderr is None:
        process.kill()
        raise RehearsalFailure("process", "capture_pipe_missing")
    stdout_buffer = bytearray()
    stderr_buffer = bytearray()
    overflow = threading.Event()
    io_errors: list[str] = []
    error_lock = threading.Lock()

    def record_io_error(name: str) -> None:
        with error_lock:
            io_errors.append(name)

    def read_bounded(stream: Any, buffer: bytearray, name: str) -> None:
        try:
            while True:
                chunk = stream.read(8192)
                if not chunk:
                    break
                remaining = cap - len(buffer)
                if remaining > 0:
                    buffer.extend(chunk[:remaining])
                if len(chunk) > remaining:
                    overflow.set()
                    try:
                        process.kill()
                    except OSError:
                        pass
                    break
        except (OSError, ValueError):
            record_io_error(name)
        finally:
            try:
                stream.close()
            except (OSError, ValueError):
                pass

    def write_input() -> None:
        if process.stdin is None or stdin is None:
            return
        try:
            process.stdin.write(stdin)
            process.stdin.flush()
        except (BrokenPipeError, OSError, ValueError):
            if process.poll() is None:
                record_io_error("stdin")
        finally:
            try:
                process.stdin.close()
            except (OSError, ValueError):
                pass

    threads = [
        threading.Thread(
            target=read_bounded,
            args=(process.stdout, stdout_buffer, "stdout"),
            daemon=True,
        ),
        threading.Thread(
            target=read_bounded,
            args=(process.stderr, stderr_buffer, "stderr"),
            daemon=True,
        ),
    ]
    if stdin is not None:
        threads.append(threading.Thread(target=write_input, daemon=True))
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as error:
        timed_out = True
        process.kill()
        process.wait()
        for thread in threads:
            thread.join()
        raise RehearsalFailure(
            "process",
            "timeout",
            _bytes_sha(bytes(stdout_buffer) + bytes(stderr_buffer)),
        ) from error
    finally:
        if timed_out and process.poll() is None:
            process.kill()
    for thread in threads:
        thread.join()
    if overflow.is_set():
        raise RehearsalFailure("process", "output_cap_exceeded")
    if io_errors:
        raise RehearsalFailure("process", "pipe_io_failure", sorted(io_errors)[0])
    return ProcessResult(
        int(process.returncode), bytes(stdout_buffer), bytes(stderr_buffer)
    )


def _with_total_deadline(runner: Runner, deadline: float) -> Runner:
    """Cap every non-cleanup call by one absolute monotonic deadline."""

    def bounded(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> ProcessResult:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RehearsalFailure("process", "total_timeout")
        return runner(argv, stdin, min(float(timeout), remaining), cap)

    return bounded


def docker_argv(
    operation: DockerOperation,
    *,
    docker: str,
    profile: dict[str, Any],
    name: str = "",
    nonce: str = "",
    container_id: str = "",
    database: str = "",
    sql_command: str = "",
) -> list[str]:
    """Build only a closed Docker operation; values come from fixed state."""
    image = profile["image_reference"]
    if operation is DockerOperation.IMAGE_INSPECT:
        return [docker, "image", "inspect", image, "--format", "{{json .}}"]
    if operation in {DockerOperation.NAME_INSPECT}:
        return [docker, "container", "inspect", name, "--format", "{{json .}}"]
    if operation in {DockerOperation.ID_INSPECT, DockerOperation.ID_ABSENCE}:
        return [
            docker,
            "container",
            "inspect",
            container_id,
            "--format",
            "{{json .}}",
        ]
    if operation is DockerOperation.RUN:
        labels = profile["ownership_labels"]
        return [
            docker,
            "run",
            "--detach",
            "--name",
            name,
            "--label",
            f'com.emr4.harness={labels["com.emr4.harness"]}',
            "--label",
            f"com.emr4.cleanup-nonce={nonce}",
            "--pull=never",
            "--network=none",
            "--tmpfs",
            profile["tmpfs"],
            "--memory",
            profile["memory"],
            "--cpus",
            profile["cpus"],
            "--pids-limit",
            str(profile["pids_limit"]),
            "--restart",
            profile["restart"],
            "--env",
            f'POSTGRES_USER={profile["postgres_user"]}',
            "--env",
            f'POSTGRES_PASSWORD={profile["postgres_password"]}',
            "--env",
            f'POSTGRES_DB={profile["postgres_database"]}',
            "--env",
            f'PGDATA={profile["pgdata"]}',
            image,
        ]
    if operation is DockerOperation.READY:
        return [
            docker,
            "exec",
            container_id,
            "pg_isready",
            "--host",
            "/var/run/postgresql",
            "--port",
            "5432",
            "--username",
            profile["postgres_user"],
            "--dbname",
            profile["postgres_database"],
            "--timeout",
            "1",
        ]
    if operation is DockerOperation.READY_SQL:
        return _psql_base(
            docker,
            container_id,
            profile["postgres_database"],
            profile,
            stdin_enabled=False,
            connect_timeout_seconds=profile["readiness_connect_timeout_seconds"],
        ) + [
            "--tuples-only",
            "--no-align",
            "--command",
            "SELECT pg_catalog.current_setting('server_version_num');",
        ]
    if operation is DockerOperation.PSQL_COMMAND:
        return _psql_base(docker, container_id, database, profile) + [
            "--command",
            sql_command,
        ]
    if operation is DockerOperation.PSQL_FILE:
        return _psql_base(docker, container_id, database, profile) + [
            "--tuples-only",
            "--no-align",
            "--set",
            "VERBOSITY=verbose",
            "--file=-",
            "--single-transaction",
        ]
    if operation is DockerOperation.REMOVE:
        return [docker, "container", "rm", "--force", container_id]
    raise RehearsalFailure("command", "unknown_operation", str(operation))


def _psql_base(
    docker: str,
    container_id: str,
    database: str,
    profile: dict[str, Any],
    *,
    stdin_enabled: bool = True,
    connect_timeout_seconds: int | None = None,
) -> list[str]:
    argv = [
        docker,
        "exec",
    ]
    if stdin_enabled:
        argv.append("-i")
    argv.append(container_id)
    if connect_timeout_seconds is not None:
        argv.extend(["env", f"PGCONNECT_TIMEOUT={connect_timeout_seconds}"])
    return argv + [
        "psql",
        "--host",
        "/var/run/postgresql",
        "--username",
        profile["postgres_user"],
        "--dbname",
        database,
        "--no-psqlrc",
        "--quiet",
        "--set",
        "ON_ERROR_STOP=1",
    ]


def assert_closed_argv(argv: list[str], operation: DockerOperation) -> None:
    rendered = "\x1f".join(argv)
    forbidden_tokens = {
        "pull",
        "build",
        "login",
        "compose",
        "ps",
        "images",
        "system",
        "prune",
        "ls",
        "list",
        "--privileged",
        "--network=host",
        "-p",
        "--publish",
        "--volume",
        "-v",
    }
    if any(token in argv[1:] for token in forbidden_tokens):
        raise RehearsalFailure("command", "forbidden_token", rendered)
    if any("docker.sock" in token or "*" in token or "?" in token for token in argv):
        raise RehearsalFailure("command", "forbidden_path_or_glob")
    for token in argv:
        if token.startswith("--pull=") and token != "--pull=never":
            raise RehearsalFailure("command", "forbidden_pull_policy")
        if token.startswith("--network=") and token != "--network=none":
            raise RehearsalFailure("command", "forbidden_network_mode")
    if operation is DockerOperation.RUN:
        required = {"--pull=never", "--network=none", "--tmpfs", "--restart"}
        if not required.issubset(argv):
            raise RehearsalFailure("command", "run_containment_missing")
    if operation is DockerOperation.PSQL_FILE:
        for required in ("--file=-", "--single-transaction", "ON_ERROR_STOP=1"):
            if required not in argv:
                raise RehearsalFailure("command", "psql_atomicity_missing", required)


def _call(
    runner: Runner,
    argv: list[str],
    *,
    operation: DockerOperation,
    stdin: bytes | None,
    timeout: int,
    cap: int,
) -> ProcessResult:
    assert_closed_argv(argv, operation)
    return runner(argv, stdin, timeout, cap)


def _one_json(result: ProcessResult, stage: str) -> dict[str, Any]:
    if result.returncode != 0:
        raise RehearsalFailure(stage, "docker_command_failed", str(result.returncode))
    try:
        parsed = json.loads(result.stdout.decode("utf-8").strip())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RehearsalFailure(stage, "invalid_json_output") from error
    if not isinstance(parsed, dict):
        raise RehearsalFailure(stage, "json_object_required")
    return parsed


def _is_exact_absence(result: ProcessResult) -> bool:
    if result.returncode == 0:
        return False
    bounded = (result.stdout + result.stderr).lower()
    return b"no such object" in bounded or b"no such container" in bounded


def _readiness_failure_class(stderr: bytes) -> str:
    """Map fixed local psql diagnostics to a closed, value-free evidence class."""
    lowered = stderr.lower()
    patterns = (
        (b"syntax error", "sql_syntax"),
        (b"role ", "role_missing"),
        (b"database ", "database_missing"),
        (b"password authentication failed", "password_authentication_failed"),
        (b"peer authentication failed", "peer_authentication_failed"),
        (b"no password supplied", "password_missing"),
        (b"connection refused", "connection_refused"),
        (b"no such file or directory", "socket_missing"),
        (b"server closed the connection unexpectedly", "server_handoff"),
        (b"executable file not found", "command_unavailable"),
    )
    for fragment, classification in patterns:
        if fragment in lowered:
            return classification
    return "unclassified"


def _is_postgres_16_version_output(stdout: bytes) -> bool:
    """Admit one exact six-digit version row with at most its line ending."""
    value = stdout
    if value.endswith(b"\r\n"):
        value = value[:-2]
    elif value.endswith(b"\n"):
        value = value[:-1]
    return POSTGRES_16_VERSION_NUM.fullmatch(value) is not None


def _observed_sqlstates(stderr: bytes) -> list[str]:
    """Extract only closed five-character SQLSTATE identifiers from stderr."""
    return sorted(
        {match.decode("ascii") for match in VERBOSE_SQLSTATE.findall(stderr)}
    )


def _bounded_psql_rejection(
    result: ProcessResult, *, max_error_line: int, max_error_position: int
) -> dict[str, Any]:
    """Retain only closed SQLSTATE identifiers and an opaque stderr digest."""
    error_lines = sorted(
        {
            int(match)
            for match in VERBOSE_PSQL_ERROR_LINE.findall(result.stderr)
            if int(match) <= max_error_line
        }
    )
    return {
        "status": "rejected",
        "psql_exit": result.returncode,
        "observed_sqlstates": _observed_sqlstates(result.stderr),
        "error_lines": error_lines,
        "statement_lines": sorted(
            {
                int(match)
                for match in VERBOSE_STATEMENT_LINE.findall(result.stderr)
                if int(match) <= max_error_line
            }
        ),
        "positions": sorted(
            {
                int(match)
                for match in VERBOSE_POSITION.findall(result.stderr)
                if int(match) <= max_error_position
            }
        ),
        "context_lines": sorted(
            {
                int(match)
                for match in VERBOSE_CONTEXT_LINE.findall(result.stderr)
                if int(match) <= max_error_line
            }
        ),
        "stderr": _bounded_digest(result.stderr),
    }


def _wait_for_stable_postgres(
    runner: Runner,
    docker: str,
    container_id: str,
    profile: dict[str, Any],
    *,
    observation: dict[str, Any] | None = None,
    clock: Callable[[], float] = time.monotonic,
    sleeper: Callable[[float], None] = time.sleep,
) -> None:
    """Require a continuous authenticated SQL-ready interval after bootstrap."""
    deadline = clock() + float(profile["startup_timeout_seconds"])
    stability = float(profile["readiness_stability_seconds"])
    interval = float(profile["readiness_probe_interval_seconds"])
    stable_since: float | None = None
    state = observation if observation is not None else {}
    state.clear()
    state.update(
        {
            "status": "probing",
            "pg_isready_attempts": 0,
            "pg_isready_successes": 0,
            "sql_probe_attempts": 0,
            "sql_probe_successes": 0,
            "continuous_success_ms": 0,
        }
    )
    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            state["status"] = "timeout"
            raise RehearsalFailure("postgres", "readiness_timeout")
        state["pg_isready_attempts"] += 1
        try:
            ready = _call(
                runner,
                docker_argv(
                    DockerOperation.READY,
                    docker=docker,
                    profile=profile,
                    container_id=container_id,
                ),
                operation=DockerOperation.READY,
                stdin=None,
                timeout=min(float(profile["command_timeout_seconds"]), remaining),
                cap=profile["stdout_stderr_cap_bytes"],
            )
        except RehearsalFailure as error:
            if error.stage == "process" and error.code == "timeout":
                state["status"] = "probe_timeout"
                state["timed_out_operation"] = DockerOperation.READY.value
                raise RehearsalFailure(
                    "postgres", "readiness_probe_timeout", DockerOperation.READY.value
                ) from error
            raise
        state["last_pg_isready_exit"] = ready.returncode
        state["last_pg_isready_stderr_digest"] = "sha256:" + _bytes_sha(ready.stderr)
        if ready.returncode == 0:
            state["pg_isready_successes"] += 1
        sql_ready = False
        if ready.returncode == 0:
            remaining = deadline - clock()
            if remaining <= 0:
                state["status"] = "timeout"
                raise RehearsalFailure("postgres", "readiness_timeout")
            state["sql_probe_attempts"] += 1
            try:
                sql_probe = _call(
                    runner,
                    docker_argv(
                        DockerOperation.READY_SQL,
                        docker=docker,
                        profile=profile,
                        container_id=container_id,
                    ),
                    operation=DockerOperation.READY_SQL,
                    stdin=None,
                    timeout=min(float(profile["command_timeout_seconds"]), remaining),
                    cap=profile["stdout_stderr_cap_bytes"],
                )
            except RehearsalFailure as error:
                if error.stage == "process" and error.code == "timeout":
                    state["status"] = "probe_timeout"
                    state["timed_out_operation"] = DockerOperation.READY_SQL.value
                    raise RehearsalFailure(
                        "postgres",
                        "readiness_probe_timeout",
                        DockerOperation.READY_SQL.value,
                    ) from error
                raise
            state["last_sql_probe_exit"] = sql_probe.returncode
            state["last_sql_stdout_digest"] = "sha256:" + _bytes_sha(
                sql_probe.stdout
            )
            state["last_sql_stderr_digest"] = "sha256:" + _bytes_sha(
                sql_probe.stderr
            )
            state["last_sql_failure_class"] = _readiness_failure_class(
                sql_probe.stderr
            )
            sql_ready = (
                sql_probe.returncode == 0
                and _is_postgres_16_version_output(sql_probe.stdout)
            )
            if sql_ready:
                state["sql_probe_successes"] += 1
                state["last_sql_failure_class"] = "none"
        now = clock()
        if ready.returncode == 0 and sql_ready:
            if stable_since is None:
                stable_since = now
            state["continuous_success_ms"] = int((now - stable_since) * 1000)
            if now - stable_since >= stability:
                state["status"] = "stable"
                return
        else:
            stable_since = None
            state["continuous_success_ms"] = 0
        if now >= deadline:
            state["status"] = "timeout"
            raise RehearsalFailure("postgres", "readiness_timeout")
        sleeper(interval)


def _expected_sets(manifest: dict[str, Any]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = {}
    for row in manifest["ordered_nodes"]:
        grouped.setdefault(row["kind"], set()).add(row["identifier"])
    return grouped


def _query_json(
    runner: Runner,
    docker: str,
    container_id: str,
    database: str,
    profile: dict[str, Any],
    sql: str,
) -> Any:
    wrapped = (
        "SET TRANSACTION READ ONLY;\n"
        + sql.rstrip().rstrip(";")
        + ";\n"
    ).encode("utf-8")
    argv = docker_argv(
        DockerOperation.PSQL_FILE,
        docker=docker,
        profile=profile,
        container_id=container_id,
        database=database,
    )
    result = _call(
        runner,
        argv,
        operation=DockerOperation.PSQL_FILE,
        stdin=wrapped,
        timeout=profile["command_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )
    if result.returncode != 0:
        raise RehearsalFailure("catalogue", "query_failed", str(result.returncode))
    text = result.stdout.decode("utf-8").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise RehearsalFailure("catalogue", "query_not_json") from error


CATALOGUE_SQL: dict[str, str] = {
    "server": """
SELECT pg_catalog.json_build_object(
  'server_version_num', pg_catalog.current_setting('server_version_num')::integer,
  'database', pg_catalog.current_database()
)::text
""",
    "roles": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name), '[]'::json)::text
FROM (
  SELECT rolname AS name, rolcanlogin AS login, rolinherit AS inherit,
         rolcreatedb AS createdb, rolcreaterole AS createrole,
         rolreplication AS replication, rolbypassrls AS bypassrls,
         rolsuper AS superuser
  FROM pg_catalog.pg_roles
  WHERE rolname LIKE 'context_%'
) AS q
""",
    "schema": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name), '[]'::json)::text
FROM (
  SELECT n.nspname AS name, pg_catalog.pg_get_userbyid(n.nspowner) AS owner,
         COALESCE(n.nspacl::text, '') AS acl
  FROM pg_catalog.pg_namespace AS n
  WHERE n.nspname = 'emr4_context_fabric'
) AS q
""",
    "types": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name), '[]'::json)::text
FROM (
  SELECT n.nspname || '.' || t.typname AS name, t.typtype AS type_kind,
         pg_catalog.pg_get_userbyid(t.typowner) AS owner,
         CASE WHEN t.typtype = 'd'
              THEN pg_catalog.format_type(t.typbasetype, t.typtypmod)
              ELSE '' END AS domain_base_type,
         CASE WHEN t.typtype = 'd' THEN t.typnotnull ELSE false END AS domain_not_null,
         CASE WHEN t.typtype = 'd' THEN COALESCE(t.typdefault, '') ELSE '' END AS domain_default_sql,
         CASE WHEN t.typtype = 'd' THEN COALESCE((
           SELECT pg_catalog.json_agg(
             pg_catalog.json_build_object(
               'name', con.conname,
               'definition', pg_catalog.pg_get_constraintdef(con.oid, true)
             ) ORDER BY con.conname
           )
           FROM pg_catalog.pg_constraint AS con
           WHERE con.contypid = t.oid
         ), '[]'::json) ELSE '[]'::json END AS domain_constraints,
         CASE WHEN t.typtype = 'e' THEN COALESCE((
           SELECT pg_catalog.json_agg(e.enumlabel ORDER BY e.enumsortorder)
           FROM pg_catalog.pg_enum AS e
           WHERE e.enumtypid = t.oid
         ), '[]'::json) ELSE '[]'::json END AS enum_labels,
         CASE WHEN t.typtype = 'c' THEN COALESCE((
           SELECT pg_catalog.json_agg(
             pg_catalog.json_build_object(
               'position', a.attnum,
               'name', a.attname,
               'data_type', pg_catalog.format_type(a.atttypid, a.atttypmod)
             ) ORDER BY a.attnum
           )
           FROM pg_catalog.pg_attribute AS a
           WHERE a.attrelid = t.typrelid
             AND a.attnum > 0 AND NOT a.attisdropped
         ), '[]'::json) ELSE '[]'::json END AS composite_attributes
  FROM pg_catalog.pg_type AS t
  JOIN pg_catalog.pg_namespace AS n ON n.oid = t.typnamespace
  LEFT JOIN pg_catalog.pg_class AS c ON c.oid = t.typrelid
  WHERE n.nspname = 'emr4_context_fabric'
    AND (t.typtype IN ('d', 'e') OR (t.typtype = 'c' AND c.relkind = 'c'))
) AS q
""",
    "relations": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name), '[]'::json)::text
FROM (
  SELECT n.nspname || '.' || c.relname AS name, c.relkind AS relation_kind,
         pg_catalog.pg_get_userbyid(c.relowner) AS owner,
         c.relrowsecurity AS rls_enabled, c.relforcerowsecurity AS rls_forced,
         COALESCE(c.relacl::text, '') AS acl
  FROM pg_catalog.pg_class AS c
  JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
  WHERE n.nspname = 'emr4_context_fabric' AND c.relkind = 'r'
) AS q
""",
    "columns": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.relation, q.position), '[]'::json)::text
FROM (
  SELECT n.nspname || '.' || c.relname AS relation, a.attnum AS position,
         a.attname AS name, pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
         a.attnotnull AS not_null,
         COALESCE(pg_catalog.pg_get_expr(d.adbin, d.adrelid), '') AS default_sql
  FROM pg_catalog.pg_attribute AS a
  JOIN pg_catalog.pg_class AS c ON c.oid = a.attrelid
  JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
  LEFT JOIN pg_catalog.pg_attrdef AS d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
  WHERE n.nspname IN ('emr4_context_fabric', 'public')
    AND (n.nspname = 'emr4_context_fabric' OR c.relname IN (
      'appointments', 'appointment_command_idempotency',
      'appointment_audit_log', 'diary_committed_events'))
    AND a.attnum > 0 AND NOT a.attisdropped
) AS q
""",
    "constraints": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.identifier), '[]'::json)::text
FROM (
  SELECT n.nspname || '.' || c.relname || '.' || con.conname AS identifier,
         con.contype AS constraint_kind, con.condeferrable AS deferrable,
         con.condeferred AS initially_deferred,
         pg_catalog.pg_get_constraintdef(con.oid, true) AS definition
  FROM pg_catalog.pg_constraint AS con
  JOIN pg_catalog.pg_class AS c ON c.oid = con.conrelid
  JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
  WHERE n.nspname = 'emr4_context_fabric'
    AND con.contype <> 't'
) AS q
""",
    "indexes": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name), '[]'::json)::text
FROM (
  SELECT ic.relname AS name, n.nspname || '.' || tc.relname AS relation,
         i.indisunique AS unique_index, pg_catalog.pg_get_indexdef(i.indexrelid) AS definition
  FROM pg_catalog.pg_index AS i
  JOIN pg_catalog.pg_class AS ic ON ic.oid = i.indexrelid
  JOIN pg_catalog.pg_class AS tc ON tc.oid = i.indrelid
  JOIN pg_catalog.pg_namespace AS n ON n.oid = tc.relnamespace
  LEFT JOIN pg_catalog.pg_constraint AS con ON con.conindid = i.indexrelid
  WHERE n.nspname = 'emr4_context_fabric' AND con.oid IS NULL
) AS q
""",
    "policies": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name), '[]'::json)::text
FROM (
  SELECT p.polname AS name, c.relname AS relation, p.polcmd AS command,
         p.polpermissive AS permissive,
         ARRAY(
           SELECT CASE WHEN role_oid = 0 THEN 'PUBLIC'
                       ELSE pg_catalog.pg_get_userbyid(role_oid) END
           FROM pg_catalog.unnest(p.polroles) AS role_ids(role_oid)
           ORDER BY 1
         ) AS roles,
         COALESCE(pg_catalog.pg_get_expr(p.polqual, p.polrelid), '') AS qualification,
         COALESCE(pg_catalog.pg_get_expr(p.polwithcheck, p.polrelid), '') AS with_check
  FROM pg_catalog.pg_policy AS p
  JOIN pg_catalog.pg_class AS c ON c.oid = p.polrelid
  JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
  WHERE n.nspname = 'emr4_context_fabric'
) AS q
""",
    "functions": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name, q.identity_arguments), '[]'::json)::text
FROM (
  SELECT n.nspname || '.' || p.proname AS name,
         pg_catalog.pg_get_function_identity_arguments(p.oid) AS identity_arguments,
         pg_catalog.pg_get_function_result(p.oid) AS result_type,
         pg_catalog.pg_get_userbyid(p.proowner) AS owner, l.lanname AS language,
         p.prokind AS function_kind, p.prosecdef AS security_definer,
         p.provolatile AS volatility,
         p.proisstrict AS strict, p.proparallel AS parallel_safety,
         COALESCE(p.proconfig::text, '') AS configuration,
         COALESCE(p.proacl::text, '') AS acl
  FROM pg_catalog.pg_proc AS p
  JOIN pg_catalog.pg_namespace AS n ON n.oid = p.pronamespace
  JOIN pg_catalog.pg_language AS l ON l.oid = p.prolang
  WHERE n.nspname = 'emr4_context_fabric'
) AS q
""",
    "triggers": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name), '[]'::json)::text
FROM (
  SELECT t.tgname AS name, n.nspname || '.' || c.relname AS relation,
         pn.nspname || '.' || p.proname AS function, t.tgenabled AS enabled,
         t.tgdeferrable AS deferrable, t.tginitdeferred AS initially_deferred,
         CASE WHEN (t.tgtype & 2) <> 0 THEN 'BEFORE'
              WHEN (t.tgtype & 64) <> 0 THEN 'INSTEAD OF'
              ELSE 'AFTER' END AS timing,
         CASE WHEN (t.tgtype & 1) <> 0 THEN 'ROW' ELSE 'STATEMENT' END AS level,
         (t.tgtype & 4) <> 0 AS fires_insert,
         (t.tgtype & 8) <> 0 AS fires_delete,
         (t.tgtype & 16) <> 0 AS fires_update,
         (t.tgtype & 32) <> 0 AS fires_truncate,
         pg_catalog.pg_get_triggerdef(t.oid, true) AS definition
  FROM pg_catalog.pg_trigger AS t
  JOIN pg_catalog.pg_class AS c ON c.oid = t.tgrelid
  JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
  JOIN pg_catalog.pg_proc AS p ON p.oid = t.tgfoid
  JOIN pg_catalog.pg_namespace AS pn ON pn.oid = p.pronamespace
  WHERE NOT t.tgisinternal AND (
    n.nspname = 'emr4_context_fabric' OR
    (n.nspname = 'public' AND c.relname IN (
      'appointments', 'appointment_command_idempotency',
      'appointment_audit_log', 'diary_committed_events')))
    AND t.tgname LIKE 'trg_cf_%'
) AS q
""",
    "rls": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name), '[]'::json)::text
FROM (
  SELECT n.nspname || '.' || c.relname AS name,
         c.relrowsecurity AS enabled, c.relforcerowsecurity AS forced
  FROM pg_catalog.pg_class AS c
  JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
  WHERE n.nspname = 'emr4_context_fabric' AND c.relkind = 'r'
) AS q
""",
    "schema_acl": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.grantee, q.privilege), '[]'::json)::text
FROM (
  SELECT CASE WHEN x.grantee = 0 THEN 'PUBLIC' ELSE pg_catalog.pg_get_userbyid(x.grantee) END AS grantee,
         x.privilege_type AS privilege, x.is_grantable AS grantable
  FROM pg_catalog.pg_namespace AS n
  CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(n.nspacl, pg_catalog.acldefault('n', n.nspowner))) AS x
  WHERE n.nspname = 'emr4_context_fabric' AND x.grantee <> n.nspowner
) AS q
""",
    "relation_acl": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.relation, q.grantee, q.privilege), '[]'::json)::text
FROM (
  SELECT n.nspname || '.' || c.relname AS relation,
         CASE WHEN x.grantee = 0 THEN 'PUBLIC' ELSE pg_catalog.pg_get_userbyid(x.grantee) END AS grantee,
         x.privilege_type AS privilege, x.is_grantable AS grantable
  FROM pg_catalog.pg_class AS c
  JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
  CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(c.relacl, pg_catalog.acldefault('r', c.relowner))) AS x
  WHERE (
      (n.nspname = 'emr4_context_fabric' AND c.relkind = 'r')
      OR (n.nspname = 'public' AND c.relname IN (
        'appointments', 'appointment_command_idempotency',
        'appointment_audit_log', 'diary_committed_events'))
    )
    AND x.grantee <> c.relowner
) AS q
""",
    "function_acl": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q."function", q.grantee, q.privilege), '[]'::json)::text
FROM (
  SELECT n.nspname || '.' || p.proname AS "function",
         CASE WHEN x.grantee = 0 THEN 'PUBLIC' ELSE pg_catalog.pg_get_userbyid(x.grantee) END AS grantee,
         x.privilege_type AS privilege, x.is_grantable AS grantable
  FROM pg_catalog.pg_proc AS p
  JOIN pg_catalog.pg_namespace AS n ON n.oid = p.pronamespace
  CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(p.proacl, pg_catalog.acldefault('f', p.proowner))) AS x
  WHERE n.nspname = 'emr4_context_fabric' AND x.grantee <> p.proowner
) AS q
""",
    "application_relations": """
SELECT pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name)::text
FROM (
  SELECT n.nspname || '.' || c.relname AS name,
         pg_catalog.pg_get_userbyid(c.relowner) AS owner,
         CASE c.relname
           WHEN 'appointments' THEN (SELECT count(*) FROM public.appointments)
           WHEN 'appointment_command_idempotency' THEN (SELECT count(*) FROM public.appointment_command_idempotency)
           WHEN 'appointment_audit_log' THEN (SELECT count(*) FROM public.appointment_audit_log)
           WHEN 'diary_committed_events' THEN (SELECT count(*) FROM public.diary_committed_events)
         END AS row_count
  FROM pg_catalog.pg_class AS c
  JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
  WHERE n.nspname = 'public' AND c.relname IN (
    'appointments', 'appointment_command_idempotency',
    'appointment_audit_log', 'diary_committed_events')
) AS q
""",
    "extensions": """
SELECT COALESCE(pg_catalog.json_agg(pg_catalog.row_to_json(q) ORDER BY q.name), '[]'::json)::text
FROM (SELECT extname AS name, extversion AS version FROM pg_catalog.pg_extension) AS q
""",
}


def _facts_digest(value: Any) -> str:
    return _canonical_sha(value)


def _constraint_population_diagnostic(
    rows: list[dict[str, Any]], expected_identifiers: set[str]
) -> dict[str, Any]:
    """Return value-free counts/digests for a constraint population mismatch."""
    actual_identifiers = {row["identifier"] for row in rows}
    closed_kinds = ("c", "f", "other", "p", "u")
    expected_kind_counts = {kind: 0 for kind in closed_kinds}
    prefix_kinds = {"ck_": "c", "fk_": "f", "pk_": "p", "uq_": "u"}
    for identifier in expected_identifiers:
        name = identifier.rsplit(".", 1)[-1]
        kind = next(
            (value for prefix, value in prefix_kinds.items() if name.startswith(prefix)),
            "other",
        )
        expected_kind_counts[kind] = expected_kind_counts.get(kind, 0) + 1
    actual_kind_counts = {kind: 0 for kind in closed_kinds}
    for row in rows:
        kind = row.get("constraint_kind", "other")
        if kind not in {"c", "f", "p", "u"}:
            kind = "other"
        actual_kind_counts[kind] += 1
    missing = sorted(expected_identifiers - actual_identifiers)
    unexpected = sorted(actual_identifiers - expected_identifiers)
    return {
        "expected_count": len(expected_identifiers),
        "actual_count": len(actual_identifiers),
        "missing_count": len(missing),
        "unexpected_count": len(unexpected),
        "expected_kind_counts": dict(sorted(expected_kind_counts.items())),
        "actual_kind_counts": dict(sorted(actual_kind_counts.items())),
        "missing_identifiers_sha256": _facts_digest(missing),
        "unexpected_identifiers_sha256": _facts_digest(unexpected),
    }


def _normalized_catalogue_type(value: str) -> str:
    return {
        "timestamp with time zone": "timestamptz",
        "integer": "integer",
        "bigint": "bigint",
        "uuid": "uuid",
        "text": "text",
        "jsonb": "jsonb",
    }.get(value, value)


def _normalized_default(value: str) -> str | None:
    if not value:
        return None
    if value in {"15", "15::integer"}:
        return "15"
    if value in {"now()", "pg_catalog.now()"}:
        return "pg_catalog.now()"
    return value


def _read_catalogue(
    runner: Runner,
    docker: str,
    container_id: str,
    database: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    return {
        query_id: _query_json(
            runner, docker, container_id, database, profile, sql
        )
        for query_id, sql in CATALOGUE_SQL.items()
    }


def _assert_catalogue(
    facts: dict[str, Any],
    manifest: dict[str, Any],
    prerequisite: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    expected = _expected_sets(manifest)
    server = facts["server"]
    if server != {"server_version_num": 160000, "database": "emr4_synthetic_success"}:
        if not (
            server.get("database") == "emr4_synthetic_success"
            and 160000 <= int(server.get("server_version_num", 0)) < 170000
        ):
            raise RehearsalFailure("catalogue", "server_or_database")
    roles = facts["roles"]
    if {row["name"] for row in roles} != expected["ROLE"]:
        raise RehearsalFailure("catalogue", "role_population")
    role_login = {
        match.group(1): match.group(2) is None
        for match in ROLE_LINE.finditer(
            _canonical_artifact((ROOT / _json(CONTRACT_PATH)["parent"]["artifact_path"]).read_bytes()).decode("utf-8")
        )
    }
    for role in roles:
        if role["login"] != role_login[role["name"]] or any(
            role[key]
            for key in (
                "inherit",
                "createdb",
                "createrole",
                "replication",
                "bypassrls",
                "superuser",
            )
        ):
            raise RehearsalFailure("catalogue", "role_attributes", role["name"])
    if len(facts["schema"]) != 1 or any(
        facts["schema"][0].get(key) != value
        for key, value in {
            "name": FABRIC_SCHEMA,
            "owner": "context_schema_owner",
        }.items()
    ):
        raise RehearsalFailure("catalogue", "schema")
    type_kind = {"d": "DOMAIN", "e": "ENUM", "c": "COMPOSITE"}
    actual_types = {kind: set() for kind in type_kind.values()}
    for row in facts["types"]:
        if row["owner"] != "context_schema_owner" or row["type_kind"] not in type_kind:
            raise RehearsalFailure("catalogue", "type_owner_or_kind")
        actual_types[type_kind[row["type_kind"]]].add(row["name"])
    for kind in actual_types:
        if actual_types[kind] != expected[kind]:
            raise RehearsalFailure("catalogue", "type_population", kind)
    relations = facts["relations"]
    if {row["name"] for row in relations} != expected["TABLE"]:
        raise RehearsalFailure("catalogue", "relation_population")
    for row in relations:
        if (
            row["owner"] != "context_schema_owner"
            or not row["rls_enabled"]
            or not row["rls_forced"]
            or row["relation_kind"] != "r"
        ):
            raise RehearsalFailure("catalogue", "relation_attributes", row["name"])
    if len(facts["rls"]) != 18 or any(
        not row["enabled"] or not row["forced"] for row in facts["rls"]
    ):
        raise RehearsalFailure("catalogue", "rls_projection")
    if {row["identifier"] for row in facts["constraints"]} != expected["CONSTRAINT"]:
        raise RehearsalFailure("catalogue", "constraint_population")
    if {row["name"] for row in facts["indexes"]} != expected["UNIQUE_INDEX"]:
        raise RehearsalFailure("catalogue", "index_population")
    if {row["name"] for row in facts["policies"]} != expected["RLS_POLICY"]:
        raise RehearsalFailure("catalogue", "policy_population")
    functions = facts["functions"]
    actual_function_names = {row["name"] for row in functions}
    expected_function_names = (
        expected["SUPPORT_FUNCTION"]
        | expected["ENTRY_POINT"]
        | expected["TRIGGER_FUNCTION"]
    )
    if actual_function_names != expected_function_names or len(functions) != 24:
        raise RehearsalFailure("catalogue", "function_population")
    for row in functions:
        if row["owner"] != "context_schema_owner" or row["language"] not in {
            "sql",
            "plpgsql",
        }:
            raise RehearsalFailure("catalogue", "function_attributes", row["name"])
    if {row["name"] for row in facts["triggers"]} != expected["TRIGGER_DECLARATION"]:
        raise RehearsalFailure("catalogue", "trigger_population")
    if len([row for row in facts["triggers"] if row["deferrable"]]) != 7:
        raise RehearsalFailure("catalogue", "trigger_deferrable_split")
    if any(row["enabled"] != "O" for row in facts["triggers"]):
        raise RehearsalFailure("catalogue", "trigger_enablement")
    for acl_kind in ("schema_acl", "relation_acl", "function_acl"):
        if any(row["grantee"] == "PUBLIC" for row in facts[acl_kind]):
            raise RehearsalFailure("catalogue", "public_acl", acl_kind)
    if any(
        row["privilege"] == "CREATE" and row["grantee"] != "context_schema_owner"
        for row in facts["schema_acl"]
    ):
        raise RehearsalFailure("catalogue", "runtime_schema_create_acl")
    trigger_functions = expected["TRIGGER_FUNCTION"]
    if any(
        row["function"] in trigger_functions
        and row["grantee"] != "context_schema_owner"
        for row in facts["function_acl"]
    ):
        raise RehearsalFailure("catalogue", "runtime_trigger_execute_acl")
    expected_apps = {"public." + table["name"] for table in prerequisite["tables"]}
    app_facts = facts["application_relations"]
    if {row["name"] for row in app_facts} != expected_apps:
        raise RehearsalFailure("catalogue", "application_relation_population")
    if any(
        row["owner"] != prerequisite["owner"] or int(row["row_count"]) != 0
        for row in app_facts
    ):
        raise RehearsalFailure("catalogue", "application_relation_changed")
    if not facts["columns"]:
        raise RehearsalFailure("catalogue", "column_projection_empty")
    actual_app_columns = [
        row for row in facts["columns"] if row["relation"].startswith("public.")
    ]
    expected_app_columns: list[dict[str, Any]] = []
    for table in prerequisite["tables"]:
        for position, column in enumerate(table["columns"], start=1):
            expected_app_columns.append(
                {
                    "relation": "public." + table["name"],
                    "position": position,
                    "name": column["name"],
                    "data_type": column["type"],
                    "not_null": not column["nullable"],
                    "default_sql": column["default_sql"],
                }
            )
    normalized_actual = [
        {
            **row,
            "data_type": _normalized_catalogue_type(row["data_type"]),
            "default_sql": _normalized_default(row["default_sql"]),
        }
        for row in actual_app_columns
    ]
    expected_app_columns.sort(key=lambda row: (row["relation"], row["position"]))
    if normalized_actual != expected_app_columns:
        raise RehearsalFailure("catalogue", "application_column_shape")
    fabric_relations_with_columns = {
        row["relation"]
        for row in facts["columns"]
        if row["relation"].startswith(FABRIC_SCHEMA + ".")
    }
    if fabric_relations_with_columns != expected["TABLE"]:
        raise RehearsalFailure("catalogue", "fabric_column_relation_population")
    query_digests = {key: _facts_digest(value) for key, value in facts.items()}
    expectation = contract["catalogue_expectation"]
    digest_ids = set(contract["catalogue_query_ids"]) - {"server", "extensions"}
    if expectation["mode"] == "exact_digest_bound":
        actual = {key: query_digests[key] for key in sorted(digest_ids)}
        if actual != expectation["expected_query_digests"]:
            mismatch = next(
                key
                for key in sorted(digest_ids)
                if actual.get(key) != expectation["expected_query_digests"].get(key)
            )
            raise RehearsalFailure("catalogue", "exact_query_digest", mismatch)
    return {
        "expectation_mode": expectation["mode"],
        "query_ids": sorted(facts),
        "kind_counts": {
            "roles": len(roles),
            "types": len(facts["types"]),
            "relations": len(relations),
            "columns": len(facts["columns"]),
            "constraints": len(facts["constraints"]),
            "indexes": len(facts["indexes"]),
            "policies": len(facts["policies"]),
            "functions": len(functions),
            "triggers": len(facts["triggers"]),
        },
        "query_digests": query_digests,
    }


def _install_prerequisites(
    runner: Runner,
    docker: str,
    container_id: str,
    database: str,
    profile: dict[str, Any],
    sql: bytes,
) -> None:
    argv = docker_argv(
        DockerOperation.PSQL_FILE,
        docker=docker,
        profile=profile,
        container_id=container_id,
        database=database,
    )
    result = _call(
        runner,
        argv,
        operation=DockerOperation.PSQL_FILE,
        stdin=sql,
        timeout=profile["command_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )
    if result.returncode != 0:
        raise RehearsalFailure("prerequisite", "installation_failed", str(result.returncode))


def _stream_artifact(
    runner: Runner,
    docker: str,
    container_id: str,
    database: str,
    profile: dict[str, Any],
    sql: bytes,
) -> ProcessResult:
    argv = docker_argv(
        DockerOperation.PSQL_FILE,
        docker=docker,
        profile=profile,
        container_id=container_id,
        database=database,
    )
    return _call(
        runner,
        argv,
        operation=DockerOperation.PSQL_FILE,
        stdin=sql,
        timeout=profile["artifact_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )


def _container_owned(
    inspect: dict[str, Any],
    *,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
) -> bool:
    config = inspect.get("Config")
    host = inspect.get("HostConfig")
    mounts = inspect.get("Mounts")
    if not isinstance(config, dict) or not isinstance(host, dict):
        return False
    if not isinstance(mounts, list) or any(
        not isinstance(row, dict) for row in mounts
    ):
        return False
    labels = config.get("Labels") or {}
    environment = config.get("Env") or []
    if not isinstance(labels, dict) or not isinstance(environment, list):
        return False
    forbidden_mount = any(row.get("Type") in {"bind", "volume"} for row in mounts)
    expected_labels = profile["ownership_labels"]
    tmpfs_path, tmpfs_options = profile["tmpfs"].split(":", 1)
    tmpfs_mounts = [
        row
        for row in mounts
        if row.get("Type") == "tmpfs" and row.get("Destination") == tmpfs_path
    ]
    # Docker Desktop can position-close a --tmpfs mount only in
    # HostConfig.Tmpfs while leaving the normalized Mounts projection empty.
    # Linux Engine may additionally expose one matching Mounts row.  The exact
    # HostConfig declaration remains mandatory in both representations, and
    # any other normalized mount remains forbidden.
    normalized_tmpfs_closed = not mounts or (
        len(mounts) == len(tmpfs_mounts) == 1
    )
    expected_environment = {
        f'POSTGRES_USER={profile["postgres_user"]}',
        f'POSTGRES_PASSWORD={profile["postgres_password"]}',
        f'POSTGRES_DB={profile["postgres_database"]}',
        f'PGDATA={profile["pgdata"]}',
    }
    return bool(
        inspect.get("Id") == container_id
        and inspect.get("Name") == "/" + name
        and inspect.get("Image") == image_id
        and config.get("Image") == profile["image_reference"]
        and labels.get("com.emr4.harness") == expected_labels["com.emr4.harness"]
        and labels.get("com.emr4.cleanup-nonce") == nonce
        and host.get("NetworkMode") == "none"
        and not forbidden_mount
        and not host.get("Binds")
        and not host.get("Privileged")
        and not host.get("PortBindings")
        and host.get("Memory") == 768 * 1024 * 1024
        and host.get("NanoCpus") == 1_000_000_000
        and host.get("PidsLimit") == profile["pids_limit"]
        and host.get("RestartPolicy", {}).get("Name") in {"", "no"}
        and (host.get("Tmpfs") or {}) == {tmpfs_path: tmpfs_options}
        and normalized_tmpfs_closed
        and expected_environment.issubset(environment)
    )


def _cleanup(
    runner: Runner,
    docker: str,
    container_id: str,
    name: str,
    nonce: str,
    image_id: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    inspect_result = _call(
        runner,
        docker_argv(
            DockerOperation.ID_INSPECT,
            docker=docker,
            profile=profile,
            container_id=container_id,
        ),
        operation=DockerOperation.ID_INSPECT,
        stdin=None,
        timeout=profile["cleanup_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )
    inspect = _one_json(inspect_result, "cleanup_inspect")
    if not _container_owned(
        inspect,
        container_id=container_id,
        name=name,
        nonce=nonce,
        image_id=image_id,
        profile=profile,
    ):
        return {
            "status": "cleanup_ownership_unverified",
            "container_id": container_id,
            "removed": False,
            "absence_verified": False,
        }
    remove = _call(
        runner,
        docker_argv(
            DockerOperation.REMOVE,
            docker=docker,
            profile=profile,
            container_id=container_id,
        ),
        operation=DockerOperation.REMOVE,
        stdin=None,
        timeout=profile["cleanup_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )
    if remove.returncode != 0:
        raise RehearsalFailure("cleanup", "remove_failed", str(remove.returncode))
    absent = _call(
        runner,
        docker_argv(
            DockerOperation.ID_ABSENCE,
            docker=docker,
            profile=profile,
            container_id=container_id,
        ),
        operation=DockerOperation.ID_ABSENCE,
        stdin=None,
        timeout=profile["cleanup_timeout_seconds"],
        cap=profile["stdout_stderr_cap_bytes"],
    )
    if not _is_exact_absence(absent):
        raise RehearsalFailure("cleanup", "container_still_present")
    return {
        "status": "cleanup_verified",
        "container_id": container_id,
        "removed": True,
        "absence_verified": True,
    }


def run_rehearsal(*, runner: Runner = _subprocess_runner) -> dict[str, Any]:
    started = time.monotonic()
    attempt_id = secrets.token_hex(12)
    lifecycle: list[str] = []
    rollback: dict[str, Any] = {"status": "not_started"}
    catalogue: dict[str, Any] = {"status": "not_started"}
    cleanup: dict[str, Any] = {
        "status": "not_needed",
        "removed": False,
        "absence_verified": False,
    }
    environment: dict[str, Any] = {"docker_client": "unresolved", "image": "uninspected"}
    failure: RehearsalFailure | None = None
    container_id = ""
    image_id = ""
    name = ""
    nonce = ""
    contract: dict[str, Any] = {}
    parent_evidence: dict[str, Any] = {}
    result = "rehearsal_failed"
    cleanup_runner = runner
    try:
        contract, prerequisite, manifest, artifact = _validate_contracts()
        profile = contract["docker_profile"]
        cleanup_reserve = 3 * profile["cleanup_timeout_seconds"]
        execution_seconds = profile["total_timeout_seconds"] - cleanup_reserve
        if execution_seconds <= profile["artifact_timeout_seconds"]:
            raise RehearsalFailure("contract", "total_timeout_budget")
        runner = _with_total_deadline(runner, started + execution_seconds)
        prerequisite_sql = render_prerequisite_sql(prerequisite)
        artifact_line_count = artifact.count(b"\n")
        lifecycle.append("parent_verified")
        parent_evidence = {
            "artifact_sha256": "sha256:" + _bytes_sha(artifact),
            "artifact_byte_count": len(artifact),
            "statement_count": manifest["statement_count"],
            "contract_sha256": _canonical_sha(contract),
            "prerequisite_contract_sha256": _canonical_sha(prerequisite),
            "prerequisite_sql_sha256": "sha256:" + _bytes_sha(prerequisite_sql),
        }
        docker = shutil.which(profile["executable"])
        if not docker or Path(docker).name.lower() != "docker.exe":
            raise RehearsalFailure("environment", "docker_client_missing")
        environment["docker_client"] = "resolved_exact_docker_exe"
        image_result = _call(
            runner,
            docker_argv(DockerOperation.IMAGE_INSPECT, docker=docker, profile=profile),
            operation=DockerOperation.IMAGE_INSPECT,
            stdin=None,
            timeout=profile["command_timeout_seconds"],
            cap=profile["stdout_stderr_cap_bytes"],
        )
        if image_result.returncode != 0:
            raise RehearsalFailure("environment", "exact_local_image_unavailable")
        image = _one_json(image_result, "image_inspect")
        image_id = str(image.get("Id", ""))
        if not image_id.startswith("sha256:"):
            raise RehearsalFailure("environment", "image_id_invalid")
        environment["image"] = {
            "reference": profile["image_reference"],
            "id": image_id,
            "pull_attempted": False,
        }
        nonce = secrets.token_hex(16)
        name = profile["container_name_prefix"] + secrets.token_hex(8)
        name_check = _call(
            runner,
            docker_argv(
                DockerOperation.NAME_INSPECT,
                docker=docker,
                profile=profile,
                name=name,
            ),
            operation=DockerOperation.NAME_INSPECT,
            stdin=None,
            timeout=profile["command_timeout_seconds"],
            cap=profile["stdout_stderr_cap_bytes"],
        )
        if name_check.returncode == 0:
            raise RehearsalFailure("environment", "container_name_collision")
        if not _is_exact_absence(name_check):
            raise RehearsalFailure("environment", "container_name_check_failed")
        lifecycle.append("environment_verified")
        created = _call(
            runner,
            docker_argv(
                DockerOperation.RUN,
                docker=docker,
                profile=profile,
                name=name,
                nonce=nonce,
            ),
            operation=DockerOperation.RUN,
            stdin=None,
            timeout=profile["command_timeout_seconds"],
            cap=profile["stdout_stderr_cap_bytes"],
        )
        if created.returncode != 0:
            raise RehearsalFailure("container", "create_failed", str(created.returncode))
        container_id = created.stdout.decode("ascii").strip()
        if not re.fullmatch(r"[0-9a-f]{12,64}", container_id):
            raise RehearsalFailure("container", "created_id_invalid")
        lifecycle.append("container_created")
        inspected = _one_json(
            _call(
                runner,
                docker_argv(
                    DockerOperation.ID_INSPECT,
                    docker=docker,
                    profile=profile,
                    container_id=container_id,
                ),
                operation=DockerOperation.ID_INSPECT,
                stdin=None,
                timeout=profile["command_timeout_seconds"],
                cap=profile["stdout_stderr_cap_bytes"],
            ),
            "container_inspect",
        )
        if not _container_owned(
            inspected,
            container_id=container_id,
            name=name,
            nonce=nonce,
            image_id=image_id,
            profile=profile,
        ):
            raise RehearsalFailure("container", "containment_mismatch")
        lifecycle.append("container_owned")
        environment["readiness"] = {}
        _wait_for_stable_postgres(
            runner,
            docker,
            container_id,
            profile,
            observation=environment["readiness"],
        )
        lifecycle.append("postgres_ready")
        for database in contract["database_sequence"]:
            create = _call(
                runner,
                docker_argv(
                    DockerOperation.PSQL_COMMAND,
                    docker=docker,
                    profile=profile,
                    container_id=container_id,
                    database=profile["postgres_database"],
                    sql_command=f'CREATE DATABASE "{database}";',
                ),
                operation=DockerOperation.PSQL_COMMAND,
                stdin=None,
                timeout=profile["command_timeout_seconds"],
                cap=profile["stdout_stderr_cap_bytes"],
            )
            if create.returncode != 0:
                raise RehearsalFailure("postgres", "database_create_failed", database)
            if database.endswith("rollback"):
                lifecycle.append("rollback_database_ready")
                _install_prerequisites(
                    runner, docker, container_id, database, profile, prerequisite_sql
                )
                lifecycle.append("rollback_prerequisites_installed")
                invalid = _stream_artifact(
                    runner,
                    docker,
                    container_id,
                    database,
                    profile,
                    artifact + contract["psql_admission"]["invalid_suffix"].encode("utf-8"),
                )
                stderr = invalid.stderr
                expected_sqlstate = contract["psql_admission"]["expected_sqlstate"]
                expected_error_line = artifact_line_count + 2
                bounded_rejection = _bounded_psql_rejection(
                    invalid,
                    max_error_line=expected_error_line,
                    max_error_position=len(artifact)
                    + len(contract["psql_admission"]["invalid_suffix"].encode("utf-8")),
                )
                observed_sqlstates = bounded_rejection["observed_sqlstates"]
                rollback = {
                    "status": "invalid_case_observed",
                    "psql_exit": invalid.returncode,
                    "expected_sqlstate": expected_sqlstate,
                    "expected_sqlstate_seen": expected_sqlstate in observed_sqlstates,
                    "expected_error_line": expected_error_line,
                    "expected_error_line_seen": bounded_rejection["error_lines"]
                    == [expected_error_line],
                    "observed_sqlstates": observed_sqlstates,
                    "error_lines": bounded_rejection["error_lines"],
                    "statement_lines": bounded_rejection["statement_lines"],
                    "positions": bounded_rejection["positions"],
                    "context_lines": bounded_rejection["context_lines"],
                    "stderr": bounded_rejection["stderr"],
                }
                if (
                    invalid.returncode != contract["psql_admission"]["expected_psql_exit"]
                    or not rollback["expected_sqlstate_seen"]
                    or not rollback["expected_error_line_seen"]
                ):
                    raise RehearsalFailure(
                        "rollback", "unexpected_failure_shape", str(invalid.returncode)
                    )
                expected_roles = sorted(_expected_sets(manifest)["ROLE"])
                roles_sql = ", ".join("'" + role + "'" for role in expected_roles)
                absence = _query_json(
                    runner,
                    docker,
                    container_id,
                    database,
                    profile,
                    "SELECT pg_catalog.json_build_object("
                    "'schema_count', (SELECT count(*) FROM pg_catalog.pg_namespace "
                    "WHERE nspname = 'emr4_context_fabric'), "
                    f"'role_count', (SELECT count(*) FROM pg_catalog.pg_roles WHERE rolname IN ({roles_sql}))"
                    ")::text",
                )
                if absence != {"schema_count": 0, "role_count": 0}:
                    raise RehearsalFailure("rollback", "objects_survived")
                rollback.update(
                    {
                        "status": "matched",
                        "database_local_schema_count": 0,
                        "cluster_role_count": 0,
                    }
                )
                lifecycle.append("rollback_case_matched")
            else:
                lifecycle.append("success_database_ready")
                _install_prerequisites(
                    runner, docker, container_id, database, profile, prerequisite_sql
                )
                lifecycle.append("success_prerequisites_installed")
                baseline_extensions = _query_json(
                    runner,
                    docker,
                    container_id,
                    database,
                    profile,
                    CATALOGUE_SQL["extensions"],
                )
                admitted = _stream_artifact(
                    runner, docker, container_id, database, profile, artifact
                )
                if admitted.returncode != 0:
                    catalogue = {
                        "status": "not_started",
                        "artifact_admission": _bounded_psql_rejection(
                            admitted,
                            max_error_line=artifact_line_count,
                            max_error_position=len(artifact),
                        ),
                    }
                    raise RehearsalFailure(
                        "artifact", "postgresql_rejected", str(admitted.returncode)
                    )
                lifecycle.append("artifact_admitted")
                facts = _read_catalogue(
                    runner, docker, container_id, database, profile
                )
                if set(facts) != set(contract["catalogue_query_ids"]):
                    raise RehearsalFailure("catalogue", "query_population")
                if facts["extensions"] != baseline_extensions:
                    raise RehearsalFailure("catalogue", "extension_population_changed")
                expected_constraints = _expected_sets(manifest)["CONSTRAINT"]
                if {
                    row["identifier"] for row in facts["constraints"]
                } != expected_constraints:
                    catalogue = {
                        "status": "population_mismatch",
                        "constraint_population": _constraint_population_diagnostic(
                            facts["constraints"], expected_constraints
                        ),
                    }
                    raise RehearsalFailure("catalogue", "constraint_population")
                assertion = _assert_catalogue(
                    facts, manifest, prerequisite, contract
                )
                if contract["catalogue_expectation"]["mode"] == "characterization_only":
                    catalogue = {"status": "characterized", **assertion}
                    lifecycle.append("catalogue_characterized")
                else:
                    catalogue = {"status": "matched", **assertion}
                    lifecycle.append("catalogue_matched")
        result = (
            "catalogue_characterization_required"
            if contract["catalogue_expectation"]["mode"] == "characterization_only"
            else PASS_RESULT
        )
    except RehearsalFailure as error:
        failure = error
        if error.stage == "environment":
            result = "environment_unavailable"
    finally:
        if container_id:
            try:
                cleanup = _cleanup(
                    cleanup_runner,
                    docker,
                    container_id,
                    name,
                    nonce,
                    image_id,
                    contract["docker_profile"],
                )
                if cleanup["status"] == "cleanup_verified":
                    lifecycle.append("cleanup_verified")
                else:
                    result = "cleanup_ownership_unverified"
            except RehearsalFailure as cleanup_error:
                cleanup = {
                    "status": "cleanup_failed",
                    "removed": False,
                    "absence_verified": False,
                    "failure_stage": cleanup_error.stage,
                    "failure_code": cleanup_error.code,
                }
                result = "rehearsal_failed"
                if failure is None:
                    failure = cleanup_error
        if result == PASS_RESULT and cleanup.get("absence_verified"):
            lifecycle.append("passed")
        elif result == PASS_RESULT:
            result = "rehearsal_failed"
    evidence: dict[str, Any] = {
        "schema_version": "emr4.disposable-postgresql-durability-rehearsal-evidence.v1",
        "result": result,
        "evidence_mode": EVIDENCE_MODE,
        "attempt_id": attempt_id,
        "parent": parent_evidence,
        "environment": environment,
        "lifecycle": lifecycle,
        "rollback": rollback,
        "catalogue": catalogue,
        "cleanup": cleanup,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    if failure is not None:
        evidence["environment"]["failure"] = {
            "stage": failure.stage,
            "code": failure.code,
            "detail_digest": "sha256:" + _bytes_sha(failure.detail.encode("utf-8")),
        }
    evidence["environment"]["elapsed_ms"] = int((time.monotonic() - started) * 1000)
    return evidence


def write_evidence(payload: dict[str, Any]) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    EVIDENCE_PATH.write_bytes(rendered.encode("utf-8"))


def main() -> int:
    if len(sys.argv) != 1:
        print("This fixed-path harness accepts no arguments.", file=sys.stderr)
        return 2
    evidence = run_rehearsal()
    write_evidence(evidence)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "evidence": EVIDENCE_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == PASS_RESULT else 2


if __name__ == "__main__":
    raise SystemExit(main())
