"""Prove the relay-free OCI result channel without starting PostgreSQL."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import secrets
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, NoReturn

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / (
    "orchestration/continuity/raisa-provider-free-default-off-check-in-"
    "relay-free-unknown-response-transport-redesign"
)
CONTRACT_PATH = TOPIC / "contract.json"
CONTRACT_SCHEMA_PATH = TOPIC / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = TOPIC / "evidence.schema.json"
EVIDENCE_PATH = TOPIC / "transport-evidence.json"
FAILURE_PATH = TOPIC / "transport-failure-evidence.json"
DECISION_SOURCE = "44c1c8efa2357d9ebdc9ec895fd31e5758bc66d4"
PROTECTED_SOURCE = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PASS_RESULT = (
    "raisa_provider_free_default_off_check_in_relay_free_unknown_response_"
    "transport_redesign_pass"
)
EVIDENCE_LABEL = (
    "authored_synthetic_provider_free_no_database_relay_free_oci_result_transport"
)
CONTAINER_OUTCOME = (
    "simulated_connection_lost_without_complete_terminal_response"
)
DENIED_OUTCOME = "unresolved_denied"
WRAPPER = """set -eu
IFS= read -r emr4_token
case "$emr4_token" in
  ""|*[!0-9a-f]*) exit 43 ;;
esac
[ "${#emr4_token}" -eq 64 ] || exit 43
unset emr4_token
set +e
sh -c 'exit 17' >/dev/null 2>&1
emr4_child_status=$?
set -e
if [ "$emr4_child_status" -eq 17 ]; then
  exit 42
fi
exit 43
"""
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
CONTAINER_ID = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEY_PARTS = {
    "password",
    "secret",
    "token",
    "container_id",
    "container_name",
    "process_id",
    "local_path",
    "stdout",
    "stderr",
    "exception",
    "command_text",
    "argv",
    "environment_value",
    "dsn",
    "backend_pid",
    "raw_sql",
    "raw_output",
    "patient",
    "appointment",
    "clinical",
}


class TransportFailure(RuntimeError):
    def __init__(self, stage: str, code: str) -> None:
        self.stage = stage
        self.code = code
        super().__init__(f"{stage}:{code}")


def _fail(stage: str, code: str) -> NoReturn:
    raise TransportFailure(stage, code)


def _canonical_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise TransportFailure("source", "utf8_required") from error
    normalized = raw.replace(b"\r\n", b"\n")
    if b"\r" in normalized:
        _fail("source", "bare_cr_rejected")
    return normalized


def _sha256(value: bytes | str) -> str:
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(payload).hexdigest()


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        _fail("contract", "object_required")
    return value


def _git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def _docker(
    executable: str,
    *arguments: str,
    timeout: int = 30,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [executable, *arguments],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=timeout,
    )


def _docker_json(executable: str, *arguments: str) -> list[dict[str, Any]]:
    completed = _docker(executable, *arguments)
    value = json.loads(completed.stdout)
    if not isinstance(value, list) or not value or not all(
        isinstance(item, dict) for item in value
    ):
        _fail("environment", "docker_json_invalid")
    return value


def _assert_redacted(value: object, *, forbidden_values: tuple[str, ...]) -> None:
    def visit(item: object) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                lowered = str(key).lower()
                if any(part in lowered for part in FORBIDDEN_KEY_PARTS):
                    _fail("redaction", "forbidden_key")
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, str):
            if any(secret and secret in item for secret in forbidden_values):
                _fail("redaction", "forbidden_value")

    visit(value)


def _source_hashes(contract: dict[str, Any]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = (ROOT / binding["path"]).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as error:
            raise TransportFailure("source", "path_escape") from error
        if not path.is_file():
            _fail("source", "path_missing")
        digest = _sha256(_canonical_bytes(path))
        if digest != binding["sha256"]:
            _fail("source", "sha256_mismatch")
        observed[binding["path"]] = digest
    return observed


def validate_contract(value: object, *, verify_sources: bool = True) -> dict[str, Any]:
    schema = _load(CONTRACT_SCHEMA_PATH)
    Draft202012Validator(schema).validate(value)
    if not isinstance(value, dict):
        _fail("contract", "object_required")
    contract = copy.deepcopy(value)
    profile = contract["containment_profile"]
    if (
        contract["schema_version"] != "emr4.relay-free-oci-transport-contract.v1"
        or contract["operation_id"]
        != "raisa-provider-free-default-off-check-in-relay-free-unknown-response-transport-redesign"
        or contract["decision_transition_source"] != DECISION_SOURCE
        or contract["protected_source"] != PROTECTED_SOURCE
        or contract["result"] != PASS_RESULT
        or contract["evidence_label"] != EVIDENCE_LABEL
        or profile["wrapper_sha256"] != _sha256(WRAPPER)
        or profile["image_id"]
        != "sha256:64154d0babcb1741988719e703419af0382b19953706149f9872fbd0f438efa8"
        or contract["outcome_profile"]["admitted_exit_code"] != 42
        or contract["outcome_profile"]["denied_exit_codes"] != [0, 43]
        or contract["hostile_thresholds"] != {
            "contract": 256,
            "evidence_state": 96,
            "escapes": 0,
        }
        or any(contract["closed_boundaries"].values())
    ):
        _fail("contract", "semantic_mismatch")
    paths = [binding["path"] for binding in contract["source_bindings"]]
    if len(paths) != len(set(paths)):
        _fail("contract", "duplicate_source_path")
    if verify_sources:
        _source_hashes(contract)
    return contract


def hostile_contract_mutations_rejected(
    contract: dict[str, Any], threshold: int
) -> tuple[int, int]:
    candidates: list[dict[str, Any]] = []
    keys = list(contract)
    bindings = contract["source_bindings"]
    closed_keys = list(contract["closed_boundaries"])
    for index in range(threshold):
        candidate = copy.deepcopy(contract)
        mode = index % 6
        if mode == 0:
            candidate[f"unexpected_{index}"] = index
        elif mode == 1:
            candidate[keys[index % len(keys)]] = None
        elif mode == 2:
            candidate["containment_profile"][f"unexpected_{index}"] = True
        elif mode == 3:
            candidate["source_bindings"][index % len(bindings)]["sha256"] = (
                f"{index:064x}"[-64:]
            )
        elif mode == 4:
            candidate["closed_boundaries"][
                closed_keys[index % len(closed_keys)]
            ] = True
        else:
            candidate["outcome_profile"]["admitted_exit_code"] = index + 100
        candidates.append(candidate)
    rejected = 0
    for candidate in candidates:
        try:
            validate_contract(candidate)
        except Exception:
            rejected += 1
    if len(candidates) < threshold or rejected != len(candidates):
        _fail("contract", "hostile_mutation_escape")
    return len(candidates), rejected


def classify_oci_state(value: object) -> str:
    expected_keys = {
        "identity_match",
        "running",
        "exit_code",
        "oom_killed",
        "state_error",
        "restart_count",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        return DENIED_OUTCOME
    if (
        type(value["identity_match"]) is not bool
        or type(value["running"]) is not bool
        or type(value["exit_code"]) is not int
        or type(value["oom_killed"]) is not bool
        or not isinstance(value["state_error"], str)
        or type(value["restart_count"]) is not int
    ):
        return DENIED_OUTCOME
    if value == {
        "identity_match": True,
        "running": False,
        "exit_code": 42,
        "oom_killed": False,
        "state_error": "",
        "restart_count": 0,
    }:
        return CONTAINER_OUTCOME
    return DENIED_OUTCOME


def hostile_states_rejected(threshold: int) -> tuple[int, int]:
    baseline: dict[str, Any] = {
        "identity_match": True,
        "running": False,
        "exit_code": 42,
        "oom_killed": False,
        "state_error": "",
        "restart_count": 0,
    }
    candidates: list[dict[str, Any]] = []
    fields = list(baseline)
    replacements: dict[str, list[Any]] = {
        "identity_match": [False, None, 1],
        "running": [True, None, 0],
        "exit_code": [0, 43, 1, -1, None, True],
        "oom_killed": [True, None, 0],
        "state_error": ["runtime_error", None, 1],
        "restart_count": [1, 2, -1, None, True],
    }
    for field, values in replacements.items():
        for replacement in values:
            candidate = copy.deepcopy(baseline)
            candidate[field] = replacement
            candidates.append(candidate)
    index = 0
    while len(candidates) < threshold:
        candidate = copy.deepcopy(baseline)
        candidate[f"unexpected_{index}"] = index
        candidates.append(candidate)
        index += 1
    rejected = sum(
        classify_oci_state(candidate) == DENIED_OUTCOME
        for candidate in candidates
    )
    if len(candidates) < threshold or rejected != len(candidates):
        _fail("classifier", "hostile_state_escape")
    return len(candidates), rejected


def _docker_executable(contract: dict[str, Any]) -> str:
    executable = shutil.which(contract["containment_profile"]["executable"])
    if executable is None or Path(executable).name.lower() not in {
        "docker",
        "docker.exe",
    }:
        _fail("environment", "docker_unavailable")
    return executable


def _inspect_image(executable: str, contract: dict[str, Any]) -> dict[str, Any]:
    profile = contract["containment_profile"]
    images = _docker_json(executable, "image", "inspect", profile["image_reference"])
    if len(images) != 1:
        _fail("environment", "image_inventory_invalid")
    image = images[0]
    if (
        image.get("Id") != profile["image_id"]
        or profile["image_digest"] not in image.get("RepoDigests", [])
        or image.get("Os") != "linux"
        or image.get("Architecture") != "amd64"
    ):
        _fail("environment", "image_identity_mismatch")
    return image


def _inspect_container(executable: str, container_id: str) -> dict[str, Any]:
    rows = _docker_json(executable, "inspect", container_id)
    if len(rows) != 1:
        _fail("environment", "container_inventory_invalid")
    return rows[0]


def _identity_matches(
    row: dict[str, Any],
    *,
    container_id: str,
    container_name: str,
    nonce: str,
    contract: dict[str, Any],
) -> bool:
    profile = contract["containment_profile"]
    config = row.get("Config", {})
    host = row.get("HostConfig", {})
    labels = config.get("Labels", {}) or {}
    return bool(
        row.get("Id") == container_id
        and row.get("Name") == "/" + container_name
        and row.get("Image") == profile["image_id"]
        and config.get("Image") == profile["image_reference"]
        and config.get("OpenStdin") is True
        and config.get("Tty") is False
        and config.get("Entrypoint") == ["sh"]
        and config.get("Cmd") == ["-c", WRAPPER]
        and labels.get(profile["harness_label_key"])
        == profile["harness_label_value"]
        and labels.get(profile["nonce_label_key"]) == nonce
        and host.get("NetworkMode") == "none"
        and (host.get("LogConfig") or {}).get("Type") == "none"
        and not host.get("PortBindings")
        and not host.get("Binds")
        and not host.get("Mounts")
        and host.get("ReadonlyRootfs") is True
        and host.get("CapDrop") == ["ALL"]
        and host.get("SecurityOpt") == ["no-new-privileges"]
        and host.get("Memory") == profile["memory_bytes"]
        and host.get("NanoCpus") == profile["nano_cpus"]
        and host.get("PidsLimit") == profile["pids_limit"]
        and (host.get("RestartPolicy") or {}).get("Name") == "no"
        and host.get("Tmpfs")
        == {profile["tmpfs_destination"]: profile["tmpfs_options"]}
    )


def _closed_state(
    row: dict[str, Any], *, identity_match: bool
) -> dict[str, Any]:
    state = row.get("State", {})
    return {
        "identity_match": identity_match,
        "running": state.get("Running"),
        "exit_code": state.get("ExitCode"),
        "oom_killed": state.get("OOMKilled"),
        "state_error": state.get("Error"),
        "restart_count": row.get("RestartCount"),
    }


def _stop_attachment(attachment: subprocess.Popen[bytes] | None) -> bool:
    if attachment is None:
        return True
    try:
        attachment.wait(timeout=5)
    except subprocess.TimeoutExpired:
        attachment.terminate()
        try:
            attachment.wait(timeout=5)
        except subprocess.TimeoutExpired:
            attachment.kill()
            attachment.wait(timeout=5)
    return attachment.poll() is not None


def _cleanup_container(
    executable: str,
    *,
    container_id: str | None,
    container_name: str,
    nonce: str,
    contract: dict[str, Any],
) -> dict[str, Any]:
    if container_id is None:
        return {
            "attachment_absent_before_cleanup": True,
            "captured_container_absent": True,
            "matching_nonce_resources": 0,
            "status": "cleanup_verified",
        }
    inspect = _docker(executable, "inspect", container_id, check=False)
    if inspect.returncode == 0:
        rows = json.loads(inspect.stdout)
        if (
            not isinstance(rows, list)
            or len(rows) != 1
            or not _identity_matches(
                rows[0],
                container_id=container_id,
                container_name=container_name,
                nonce=nonce,
                contract=contract,
            )
        ):
            return {
                "attachment_absent_before_cleanup": True,
                "captured_container_absent": False,
                "matching_nonce_resources": -1,
                "status": "cleanup_identity_mismatch",
            }
        _docker(executable, "rm", "--force", container_id)
    absent = _docker(executable, "inspect", container_id, check=False).returncode != 0
    profile = contract["containment_profile"]
    matches = _docker(
        executable,
        "ps",
        "-a",
        "--filter",
        f"label={profile['nonce_label_key']}={nonce}",
        "--format",
        "{{.ID}}",
    ).stdout.splitlines()
    return {
        "attachment_absent_before_cleanup": True,
        "captured_container_absent": absent,
        "matching_nonce_resources": len([item for item in matches if item]),
        "status": (
            "cleanup_verified"
            if absent and not matches
            else "cleanup_incomplete"
        ),
    }


def static_check() -> dict[str, Any]:
    contract = validate_contract(_load(CONTRACT_PATH))
    head = _git("rev-parse", "HEAD")
    if HEX40.fullmatch(head) is None:
        _fail("git", "full_head_required")
    _git("merge-base", "--is-ancestor", DECISION_SOURCE, head)
    protected = {
        _git("rev-parse", ref)
        for ref in (
            "master",
            "handoff/current",
            "origin/master",
            "origin/handoff/current",
        )
    }
    if protected != {PROTECTED_SOURCE}:
        _fail("git", "protected_refs_mismatch")
    contract_mutations = hostile_contract_mutations_rejected(
        contract, contract["hostile_thresholds"]["contract"]
    )
    state_mutations = hostile_states_rejected(
        contract["hostile_thresholds"]["evidence_state"]
    )
    executable = _docker_executable(contract)
    image = _inspect_image(executable, contract)
    return {
        "schema_version": "emr4.relay-free-oci-transport-static-check.v1",
        "status": "passed",
        "source_head": head,
        "decision_transition_source": DECISION_SOURCE,
        "source_binding_count": len(contract["source_bindings"]),
        "contract_mutations": {
            "attempted": contract_mutations[0],
            "rejected": contract_mutations[1],
        },
        "state_mutations": {
            "attempted": state_mutations[0],
            "rejected": state_mutations[1],
        },
        "image_cached": True,
        "image_id_sha256": _sha256(image["Id"]),
        "provider_calls": 0,
        "database_processes": 0,
    }


def _failure_evidence(
    error: TransportFailure,
    lifecycle: list[str],
    cleanup: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.relay-free-oci-transport-failure.v1",
        "result": "failed_closed",
        "stage": error.stage,
        "code": error.code,
        "success_released": False,
        "automatic_retries": 0,
        "database_processes": 0,
        "provider_calls": 0,
        "lifecycle": lifecycle,
        "cleanup": cleanup,
    }


def execute_once() -> dict[str, Any]:
    if EVIDENCE_PATH.exists() or FAILURE_PATH.exists():
        _fail("execution", "terminal_artifact_already_exists")
    static = static_check()
    contract = validate_contract(_load(CONTRACT_PATH))
    executable = _docker_executable(contract)
    profile = contract["containment_profile"]
    nonce = secrets.token_hex(16)
    token = secrets.token_hex(32)
    container_name = profile["container_name_prefix"] + secrets.token_hex(8)
    container_id: str | None = None
    attachment: subprocess.Popen[bytes] | None = None
    lifecycle: list[str] = ["static_admission_passed"]
    cleanup: dict[str, Any] = {
        "attachment_absent_before_cleanup": False,
        "captured_container_absent": False,
        "matching_nonce_resources": -1,
        "status": "not_started",
    }
    result: dict[str, Any] | None = None
    error: TransportFailure | None = None
    started = time.monotonic()
    try:
        create_arguments = [
            "create",
            "--pull",
            "never",
            "--interactive",
            "--name",
            container_name,
            "--label",
            f"{profile['harness_label_key']}={profile['harness_label_value']}",
            "--label",
            f"{profile['nonce_label_key']}={nonce}",
            "--network",
            "none",
            "--log-driver",
            "none",
            "--read-only",
            "--tmpfs",
            f"{profile['tmpfs_destination']}:{profile['tmpfs_options']}",
            "--memory",
            str(profile["memory_bytes"]),
            "--cpus",
            "0.25",
            "--pids-limit",
            str(profile["pids_limit"]),
            "--restart",
            "no",
            "--security-opt",
            "no-new-privileges",
            "--cap-drop",
            "ALL",
            "--entrypoint",
            "sh",
            profile["image_reference"],
            "-c",
            WRAPPER,
        ]
        created = _docker(executable, *create_arguments)
        container_id = created.stdout.strip()
        if CONTAINER_ID.fullmatch(container_id) is None:
            _fail("environment", "container_id_invalid")
        lifecycle.append("captured_container_created_without_network_or_logs")
        before = _inspect_container(executable, container_id)
        if not _identity_matches(
            before,
            container_id=container_id,
            container_name=container_name,
            nonce=nonce,
            contract=contract,
        ):
            _fail("environment", "container_profile_mismatch")
        serialized_config = json.dumps(
            {"Config": before.get("Config"), "HostConfig": before.get("HostConfig")},
            sort_keys=True,
        )
        if token in serialized_config:
            _fail("credential", "token_in_docker_config_before_delivery")
        lifecycle.append("exact_no_secret_container_configuration_verified")
        _docker(executable, "start", container_id)
        attachment = subprocess.Popen(
            [executable, "attach", "--sig-proxy=false", container_id],
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
        if attachment.stdin is None:
            _fail("credential", "attachment_stdin_missing")
        attachment.stdin.write((token + "\n").encode("ascii"))
        attachment.stdin.flush()
        attachment.stdin.close()
        lifecycle.append("token_delivered_over_attached_stdin_only")
        deadline = time.monotonic() + profile["state_timeout_seconds"]
        state_row: dict[str, Any] | None = None
        while time.monotonic() < deadline:
            observed = _inspect_container(executable, container_id)
            if observed.get("State", {}).get("Running") is False:
                state_row = observed
                break
            time.sleep(0.05)
        if state_row is None:
            _fail("outcome", "container_state_timeout")
        identity_match = _identity_matches(
            state_row,
            container_id=container_id,
            container_name=container_name,
            nonce=nonce,
            contract=contract,
        )
        closed_state = _closed_state(state_row, identity_match=identity_match)
        classification = classify_oci_state(closed_state)
        if classification != CONTAINER_OUTCOME:
            _fail("outcome", "closed_state_mismatch")
        lifecycle.append("oci_state_classified_before_attachment_disposition")
        hostile = hostile_states_rejected(
            contract["hostile_thresholds"]["evidence_state"]
        )
        lifecycle.append("hostile_oci_states_denied")
        attachment_absent = _stop_attachment(attachment)
        attachment = None
        if not attachment_absent:
            _fail("cleanup", "attachment_absence_unverified")
        lifecycle.append("attachment_absent_before_container_cleanup")
        result = {
            "schema_version": "emr4.relay-free-oci-transport-evidence.v1",
            "result": PASS_RESULT,
            "evidence_label": EVIDENCE_LABEL,
            "source_head": static["source_head"],
            "decision_transition_source": DECISION_SOURCE,
            "contract_sha256": _sha256(_canonical_bytes(CONTRACT_PATH)),
            "source_binding_count": static["source_binding_count"],
            "hostile_mutations": {
                "contract_attempted": static["contract_mutations"]["attempted"],
                "contract_rejected": static["contract_mutations"]["rejected"],
                "state_attempted": hostile[0],
                "state_rejected": hostile[1],
                "escapes": 0,
            },
            "containment": {
                "image_reference": profile["image_reference"],
                "image_id_sha256": static["image_id_sha256"],
                "pulls": 0,
                "network_mode": "none",
                "published_ports": False,
                "bind_mounts": 0,
                "volumes": 0,
                "tmpfs_count": 1,
                "log_driver": "none",
                "read_only_rootfs": True,
            },
            "transport": {
                "credential_input": "attached_stdin_process_memory_only",
                "attachment_is_outcome_evidence": False,
                "outcome_source": "captured_container_oci_state",
                "classification": classification,
                "complete_terminal_response": False,
                "success_released": False,
                "automatic_retries": 0,
            },
            "closed_state": {
                "identity_match": True,
                "running": False,
                "exit_code": 42,
                "oom_killed": False,
                "state_error_empty": True,
                "restart_count": 0,
            },
            "database": {
                "postgres_process_started": False,
                "connections": 0,
                "transactions": 0,
                "sql_statements": 0,
                "product_rows": 0,
                "ordinary_admission_releases": 0,
            },
            "provider_calls": 0,
            "lifecycle": lifecycle,
            "elapsed_milliseconds": int((time.monotonic() - started) * 1000),
        }
    except TransportFailure as caught:
        error = caught
        lifecycle.append(f"failed_{caught.stage}_{caught.code}")
    except Exception as caught:
        error = TransportFailure("harness", type(caught).__name__)
        lifecycle.append("failed_harness_closed_exception")
    finally:
        attachment_absent = _stop_attachment(attachment)
        cleanup = _cleanup_container(
            executable,
            container_id=container_id,
            container_name=container_name,
            nonce=nonce,
            contract=contract,
        )
        cleanup["attachment_absent_before_cleanup"] = attachment_absent
        if cleanup["status"] == "cleanup_verified":
            lifecycle.append("captured_container_absent")
        if (
            error is None
            and (
                not attachment_absent
                or cleanup["status"] != "cleanup_verified"
            )
        ):
            error = TransportFailure("cleanup", "exact_cleanup_unverified")
    if error is not None:
        failure = _failure_evidence(error, lifecycle, cleanup)
        _assert_redacted(failure, forbidden_values=(token, nonce, container_name))
        FAILURE_PATH.write_text(
            json.dumps(failure, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        raise error
    assert result is not None
    result["lifecycle"] = lifecycle
    result["cleanup"] = cleanup
    result["elapsed_milliseconds"] = int((time.monotonic() - started) * 1000)
    _assert_redacted(result, forbidden_values=(token, nonce, container_name))
    Draft202012Validator(_load(EVIDENCE_SCHEMA_PATH)).validate(result)
    EVIDENCE_PATH.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--execute", action="store_true")
    arguments = parser.parse_args(argv)
    result = static_check() if arguments.check else execute_once()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
