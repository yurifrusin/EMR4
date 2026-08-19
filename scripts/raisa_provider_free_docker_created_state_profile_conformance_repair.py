"""No-credential Docker Created-state representation and predicate repair."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import secrets
import shutil
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal as historical,
)


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-docker-created-state-profile-conformance-repair"
)
CONTRACT_PATH = TOPIC / "contract.json"
CONTRACT_SCHEMA_PATH = TOPIC / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = TOPIC / "evidence.schema.json"
FAILURE_SCHEMA_PATH = TOPIC / "failure.schema.json"
ATTESTATION_SCHEMA_PATH = TOPIC / "repair-attestation.schema.json"
EVIDENCE_PATH = TOPIC / "created-state-representation-evidence.json"
FAILURE_PATH = TOPIC / "created-state-representation-failure.json"
ATTESTATION_PATH = TOPIC / "repair-attestation.json"
BASE_CONTRACT_PATH = historical.CONTRACT_PATH

PLAN_SOURCE = "df5950e2309ca5a912b797fcaca61df7371be9b1"
PROTECTED_SOURCE = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
HISTORICAL_HARNESS_SOURCE = "fc772085a02d7db790b938fb845ef4546156d31e"
HISTORICAL_HARNESS_SHA256 = (
    "5c60e6e4b0d554b3c323a932e8aa5a96943705e30a4d09afb2d6b8794a1503f4"
)
PASS_RESULT = "raisa_provider_free_docker_created_state_profile_conformance_repair_pass"
EVIDENCE_LABEL = "provider_free_no_credential_docker_created_state_profile_conformance"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
DOCKER_ID = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_DOCKER_PROFILE = {
    "executable": "docker.exe",
    "engine_version": "29.5.3",
    "image_reference": "postgres:16-bookworm",
    "image_id": (
        "sha256:64154d0babcb1741988719e703419af0382b19953706149f9872fbd0f438efa8"
    ),
    "pull_policy": "never",
    "network_name_prefix": "emr4-checkin-cspr-net-",
    "container_name_prefix": "emr4-checkin-cspr-container-",
    "network_alias": "check-in-rfr-postgres",
    "harness_label_key": "emr4.harness",
    "harness_label_value": "check-in-relay-free-recovery-v1",
    "nonce_label_key": "emr4.owner-nonce",
    "conformance_label_key": "emr4.conformance",
    "conformance_label_value": "check-in-created-state-profile-v1",
    "server_tmpfs_destination": "/var/lib/postgresql/data",
    "server_tmpfs_options": "rw,noexec,nosuid,size=268435456",
    "server_memory_bytes": 536870912,
    "server_nano_cpus": 1000000000,
    "server_pids_limit": 128,
}
EXPECTED_REPRESENTATION_PROFILE = {
    "container_status": "created",
    "running": False,
    "network_cardinality": 1,
    "network_key_relations": [
        "captured_network_name",
        "captured_network_id",
        "other",
        "missing",
    ],
    "network_mode_relations": [
        "captured_network_name",
        "captured_network_id",
        "other",
        "missing",
    ],
    "endpoint_network_id_relations": [
        "captured_network_id",
        "empty",
        "other",
        "missing",
    ],
    "admitted_network_key_relations": ["captured_network_name"],
    "admitted_network_mode_relations": [
        "captured_network_name",
        "captured_network_id",
    ],
    "admitted_endpoint_network_id_relations": ["empty", "captured_network_id"],
}
EXPECTED_CORRECTED_PREDICATES = [
    "one_network",
    "captured_network_name_key",
    "captured_network_mode",
    "endpoint_network_id_lifecycle_state",
    "credentials_absent",
    "nonce_label",
    "nonce_absent_outside_label",
]
EXPECTED_CORRECTION_PROFILE = {
    "corrected_predicates": EXPECTED_CORRECTED_PREDICATES,
    "credential_scan_includes_nonce": False,
    "artifact_redaction_includes_nonce": True,
    "endpoint_created_state": "empty",
    "endpoint_attached_state": "captured_network_id",
}
EXPECTED_CLOSED_BOUNDARIES = {
    "container_started_or_attached": False,
    "credential_created_or_delivered": False,
    "postgresql_process_sql_or_database_attempt": False,
    "provider_or_external_network_used": False,
    "ordinary_practice_enabled_or_released": False,
    "product_or_protected_data_used": False,
    "product_api_schema_configuration_or_client_changed": False,
    "production_deployment_release_pages_or_protected_ref": False,
}
EVIDENCE_CLOSED_BOUNDARIES = {
    key: value
    for key, value in EXPECTED_CLOSED_BOUNDARIES.items()
    if key
    in {
        "container_started_or_attached",
        "credential_created_or_delivered",
        "postgresql_process_sql_or_database_attempt",
        "provider_or_external_network_used",
        "ordinary_practice_enabled_or_released",
        "product_or_protected_data_used",
    }
}


class ConformanceFailure(RuntimeError):
    """Closed failure coordinate without raw Docker or secret details."""

    def __init__(self, stage: str, code: str):
        super().__init__(f"{stage}:{code}")
        self.stage = stage
        self.code = code


def _fail(stage: str, code: str) -> None:
    raise ConformanceFailure(stage, code)


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        _fail("static", "json_object_required")
    return value


def _schema_errors(value: object, schema_path: Path) -> list[Any]:
    return list(
        Draft202012Validator(_load_json(schema_path)).iter_errors(value)
    )


def _git_text(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        shell=False,
    )
    if completed.returncode != 0:
        _fail("static", "git_binding_failed")
    return completed.stdout.strip()


def _git_bytes(source: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{source}:{path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        shell=False,
    )
    if completed.returncode != 0:
        _fail("static", "git_blob_binding_failed")
    return completed.stdout


def _source_head() -> str:
    head = _git_text("rev-parse", "HEAD")
    if HEX40.fullmatch(head) is None:
        _fail("static", "source_head_invalid")
    for source in (PLAN_SOURCE, HISTORICAL_HARNESS_SOURCE):
        if _git_text("cat-file", "-t", source) != "commit":
            _fail("static", "source_binding_not_commit")
        relation = subprocess.run(
            ["git", "merge-base", "--is-ancestor", source, head],
            cwd=ROOT,
            check=False,
            capture_output=True,
            shell=False,
        )
        if relation.returncode != 0:
            _fail("static", "source_binding_not_ancestor")
    return head


def validate_contract(value: object) -> dict[str, Any]:
    if _schema_errors(value, CONTRACT_SCHEMA_PATH):
        _fail("static", "contract_schema_invalid")
    if not isinstance(value, dict):
        _fail("static", "contract_object_required")
    row = value
    if row.get("plan_source") != PLAN_SOURCE:
        _fail("static", "plan_source_invalid")
    if row.get("protected_source") != PROTECTED_SOURCE:
        _fail("static", "protected_source_invalid")
    if row.get("docker_profile") != EXPECTED_DOCKER_PROFILE:
        _fail("static", "docker_profile_invalid")
    if row.get("representation_profile") != EXPECTED_REPRESENTATION_PROFILE:
        _fail("static", "representation_profile_invalid")
    if row.get("correction_profile") != EXPECTED_CORRECTION_PROFILE:
        _fail("static", "correction_profile_invalid")
    if row.get("closed_boundaries") != EXPECTED_CLOSED_BOUNDARIES:
        _fail("static", "closed_boundaries_invalid")
    historical_row = row.get("historical_harness")
    if historical_row != {
        "path": (
            "scripts/raisa_provider_free_disposable_postgresql_default_off_"
            "check_in_relay_free_rollback_unknown_commit_recovery_rehearsal.py"
        ),
        "source_commit": HISTORICAL_HARNESS_SOURCE,
        "sha256": HISTORICAL_HARNESS_SHA256,
    }:
        _fail("static", "historical_harness_invalid")
    return row


def _verify_source_bindings(contract: dict[str, Any]) -> None:
    bindings = contract["source_bindings"]
    if len({row["path"] for row in bindings}) != len(bindings):
        _fail("static", "source_binding_duplicate")
    for binding in bindings:
        path = ROOT / binding["path"]
        if not path.is_file() or _sha256_path(path) != binding["sha256"]:
            _fail("static", "source_binding_digest_mismatch")
    historical_row = contract["historical_harness"]
    historical_bytes = _git_bytes(
        historical_row["source_commit"], historical_row["path"]
    )
    if _sha256_bytes(historical_bytes) != historical_row["sha256"]:
        _fail("static", "historical_harness_blob_mismatch")


def _assert_redacted(value: object, forbidden_values: tuple[str, ...]) -> None:
    forbidden_keys = {
        "argv",
        "canary",
        "container_id",
        "container_name",
        "docker_inspect",
        "environment",
        "network_id",
        "network_name",
        "nonce",
        "password",
        "path",
        "raw",
        "secret",
        "stderr",
        "stdin",
        "stdout",
    }

    def walk(item: object) -> None:
        if isinstance(item, dict):
            for key, nested in item.items():
                if key.lower() in forbidden_keys:
                    _fail("evidence", "forbidden_field")
                walk(nested)
        elif isinstance(item, list):
            for nested in item:
                walk(nested)
        elif isinstance(item, str):
            if any(secret and secret in item for secret in forbidden_values):
                _fail("evidence", "forbidden_value")

    walk(value)


def _validate_evidence(
    value: dict[str, Any], forbidden_values: tuple[str, ...] = ()
) -> None:
    if _schema_errors(value, EVIDENCE_SCHEMA_PATH):
        _fail("evidence", "evidence_schema_invalid")
    _assert_redacted(value, forbidden_values)


def _validate_failure(
    value: dict[str, Any], forbidden_values: tuple[str, ...] = ()
) -> None:
    if _schema_errors(value, FAILURE_SCHEMA_PATH):
        _fail("evidence", "failure_schema_invalid")
    _assert_redacted(value, forbidden_values)


def _validate_attestation(value: dict[str, Any]) -> None:
    if _schema_errors(value, ATTESTATION_SCHEMA_PATH):
        _fail("evidence", "attestation_schema_invalid")
    _assert_redacted(value, ())


def hostile_contract_mutations_rejected(
    contract: dict[str, Any], count: int
) -> dict[str, int]:
    rejected = 0
    for index in range(count):
        candidate = copy.deepcopy(contract)
        selector = index % 12
        if selector == 0:
            candidate["unexpected"] = True
        elif selector == 1:
            candidate["plan_source"] = "a" * 7
        elif selector == 2:
            candidate["protected_source"] = "a" * 40
        elif selector == 3:
            candidate["docker_profile"]["engine_version"] = "29.5.4"
        elif selector == 4:
            candidate["docker_profile"]["pull_policy"] = "always"
        elif selector == 5:
            candidate["representation_profile"][
                "admitted_network_key_relations"
            ] = ["other"]
        elif selector == 6:
            candidate["representation_profile"][
                "admitted_endpoint_network_id_relations"
            ].append("other")
        elif selector == 7:
            candidate["correction_profile"]["credential_scan_includes_nonce"] = (
                True
            )
        elif selector == 8:
            candidate["correction_profile"]["artifact_redaction_includes_nonce"] = (
                False
            )
        elif selector == 9:
            candidate["closed_boundaries"]["container_started_or_attached"] = True
        elif selector == 10:
            candidate["historical_harness"]["source_commit"] = "a" * 7
        else:
            candidate["source_bindings"][0]["sha256"] = "0" * 64
        try:
            admitted = validate_contract(candidate)
            _verify_source_bindings(admitted)
        except ConformanceFailure:
            rejected += 1
    if rejected != count:
        _fail("static", "hostile_contract_escape")
    return {"attempted": count, "rejected": rejected}


def _example_evidence() -> dict[str, Any]:
    return {
        "schema_version": "emr4.docker-created-state-profile-conformance-evidence.v1",
        "result": PASS_RESULT,
        "source_head": "a" * 40,
        "plan_source": PLAN_SOURCE,
        "evidence_label": EVIDENCE_LABEL,
        "execution_count": 1,
        "retry_count": 0,
        "docker_engine_version": EXPECTED_DOCKER_PROFILE["engine_version"],
        "image_id": EXPECTED_DOCKER_PROFILE["image_id"],
        "object_profile": {
            "network_owned": True,
            "container_owned": True,
            "created": True,
            "running": False,
            "never_started": True,
            "never_attached": True,
        },
        "representation": {
            "network_cardinality": 1,
            "network_key_relation": "captured_network_name",
            "network_mode_relation": "captured_network_id",
            "endpoint_network_id_relation": "empty",
        },
        "separation_profile": {
            "credential_canaries_absent": True,
            "credential_keys_absent": True,
            "nonce_exact_label": True,
            "nonce_absent_outside_label": True,
        },
        "cleanup": {
            "container_absent": True,
            "network_absent": True,
            "matching_labelled_resources": 0,
            "status": "cleanup_verified",
        },
        "closed_boundaries": EVIDENCE_CLOSED_BOUNDARIES,
    }


def static_check(*, require_historical_current: bool = False) -> dict[str, Any]:
    head = _source_head()
    contract = validate_contract(_load_json(CONTRACT_PATH))
    _verify_source_bindings(contract)
    current_harness_sha256 = _sha256_path(Path(historical.__file__))
    if require_historical_current and (
        current_harness_sha256 != HISTORICAL_HARNESS_SHA256
    ):
        _fail("static", "historical_harness_current_digest_mismatch")
    mutations = hostile_contract_mutations_rejected(
        contract, contract["hostile_threshold"]
    )
    _validate_evidence(_example_evidence())
    _validate_failure(
        {
            "schema_version": (
                "emr4.docker-created-state-profile-conformance-failure.v1"
            ),
            "result": "failed_closed",
            "stage": "environment",
            "code": "example_failure",
            "execution_count": 1,
            "retry_count": 0,
            "success_released": False,
            "cleanup": {
                "container_absent": True,
                "network_absent": True,
                "matching_labelled_resources": 0,
                "status": "cleanup_verified",
            },
        }
    )
    _validate_attestation(
        {
            "schema_version": (
                "emr4.docker-created-state-profile-conformance-repair-attestation.v1"
            ),
            "result": "profile_predicates_corrected_and_bound",
            "source_head": "a" * 40,
            "representation_evidence_sha256": "b" * 64,
            "historical_harness_source": HISTORICAL_HARNESS_SOURCE,
            "historical_harness_sha256": HISTORICAL_HARNESS_SHA256,
            "corrected_harness_sha256": "c" * 64,
            "corrected_predicates": EXPECTED_CORRECTED_PREDICATES,
            "database_execution_authorized": False,
        }
    )
    return {
        "schema_version": "emr4.docker-created-state-profile-conformance-static.v1",
        "status": "passed",
        "source_head": head,
        "plan_source": PLAN_SOURCE,
        "historical_harness_sha256": HISTORICAL_HARNESS_SHA256,
        "current_harness_sha256": current_harness_sha256,
        "current_harness_is_historical": (
            current_harness_sha256 == HISTORICAL_HARNESS_SHA256
        ),
        "hostile_contract_mutations": mutations,
    }


def _docker_command_allowed(arguments: tuple[str, ...]) -> bool:
    if not arguments:
        return False
    return bool(
        arguments[0] in {"create", "rm", "ps", "version"}
        or arguments[:2] in {
            ("image", "inspect"),
            ("container", "inspect"),
            ("network", "create"),
            ("network", "inspect"),
            ("network", "rm"),
            ("network", "ls"),
        }
    )


def _docker(
    executable: str,
    *arguments: str,
    check: bool = True,
    timeout: int = 30,
) -> subprocess.CompletedProcess[str]:
    if not _docker_command_allowed(arguments):
        _fail("static", "docker_command_not_allowlisted")
    completed = subprocess.run(
        [executable, *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=timeout,
        shell=False,
    )
    if check and completed.returncode != 0:
        _fail("environment", "docker_command_failed")
    return completed


def _docker_json(executable: str, *arguments: str) -> list[dict[str, Any]]:
    completed = _docker(executable, *arguments)
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ConformanceFailure("environment", "docker_json_invalid") from error
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        _fail("environment", "docker_json_shape_invalid")
    return value


def _docker_executable(profile: dict[str, Any]) -> str:
    executable = shutil.which(profile["executable"]) or shutil.which("docker")
    if not executable:
        _fail("environment", "docker_unavailable")
    return executable


def _engine_and_image(executable: str, profile: dict[str, Any]) -> None:
    version = _docker(
        executable, "version", "--format", "{{.Server.Version}}"
    ).stdout.strip()
    if version != profile["engine_version"]:
        _fail("environment", "docker_engine_version_mismatch")
    rows = _docker_json(executable, "image", "inspect", profile["image_reference"])
    if len(rows) != 1 or rows[0].get("Id") != profile["image_id"]:
        _fail("environment", "image_identity_mismatch")


def _relation(value: object, captured_id: str, captured_name: str) -> str:
    if value is None:
        return "missing"
    if value == captured_id:
        return "captured_network_id"
    if value == captured_name:
        return "captured_network_name"
    if value == "":
        return "empty"
    return "other"


def _network_owned(
    row: dict[str, Any],
    *,
    network_id: str,
    network_name: str,
    nonce: str,
    profile: dict[str, Any],
) -> bool:
    labels = row.get("Labels") or {}
    return bool(
        row.get("Id") == network_id
        and row.get("Name") == network_name
        and row.get("Internal") is True
        and row.get("Driver") == "bridge"
        and labels.get(profile["harness_label_key"])
        == profile["harness_label_value"]
        and labels.get(profile["nonce_label_key"]) == nonce
        and labels.get(profile["conformance_label_key"])
        == profile["conformance_label_value"]
    )


def _container_owned(
    row: dict[str, Any],
    *,
    container_id: str,
    container_name: str,
    nonce: str,
    profile: dict[str, Any],
) -> bool:
    config = row.get("Config") or {}
    labels = config.get("Labels") or {}
    return bool(
        row.get("Id") == container_id
        and row.get("Name") == "/" + container_name
        and row.get("Image") == profile["image_id"]
        and config.get("Image") == profile["image_reference"]
        and labels.get(profile["harness_label_key"])
        == profile["harness_label_value"]
        and labels.get(profile["nonce_label_key"]) == nonce
        and labels.get(profile["conformance_label_key"])
        == profile["conformance_label_value"]
    )


def classify_created_state(
    row: dict[str, Any],
    *,
    container_id: str,
    container_name: str,
    network_id: str,
    network_name: str,
    nonce: str,
    canaries: tuple[str, ...],
    profile: dict[str, Any],
    representation_profile: dict[str, Any],
) -> dict[str, Any]:
    if not _container_owned(
        row,
        container_id=container_id,
        container_name=container_name,
        nonce=nonce,
        profile=profile,
    ):
        _fail("representation", "container_ownership_mismatch")
    try:
        config = row["Config"]
        host = row["HostConfig"]
        state = row["State"]
        labels = config["Labels"] or {}
        networks = row["NetworkSettings"]["Networks"]
        ports = row["NetworkSettings"].get("Ports") or {}
    except (KeyError, TypeError):
        _fail("representation", "inspect_shape_invalid")
    if not isinstance(networks, dict) or len(networks) != 1:
        _fail("representation", "network_cardinality_invalid")
    network_key, endpoint = next(iter(networks.items()))
    if not isinstance(endpoint, dict):
        _fail("representation", "endpoint_shape_invalid")
    network_key_relation = _relation(network_key, network_id, network_name)
    network_mode_relation = _relation(
        host.get("NetworkMode"), network_id, network_name
    )
    endpoint_relation = _relation(
        endpoint.get("NetworkID"), network_id, network_name
    )
    if network_key_relation not in representation_profile[
        "admitted_network_key_relations"
    ]:
        _fail("representation", "network_key_relation_denied")
    if network_mode_relation not in representation_profile[
        "admitted_network_mode_relations"
    ]:
        _fail("representation", "network_mode_relation_denied")
    if endpoint_relation not in representation_profile[
        "admitted_endpoint_network_id_relations"
    ]:
        _fail("representation", "endpoint_network_id_relation_denied")
    serialized = json.dumps(
        {"Config": config, "HostConfig": host}, sort_keys=True
    )
    canaries_absent = not any(value and value in serialized for value in canaries)
    credential_keys = {"PGPASSWORD", "POSTGRES_PASSWORD", "POSTGRES_PASSWORD_FILE"}
    env = config.get("Env") or []
    credential_keys_absent = isinstance(env, list) and all(
        isinstance(item, str) and item.split("=", 1)[0] not in credential_keys
        for item in env
    )
    pruned = copy.deepcopy({"Config": config, "HostConfig": host})
    pruned_labels = pruned["Config"].get("Labels") or {}
    pruned_labels.pop(profile["nonce_label_key"], None)
    nonce_absent_outside_label = nonce not in json.dumps(pruned, sort_keys=True)
    tmpfs = (host.get("Tmpfs") or {}).get(profile["server_tmpfs_destination"])
    containment = all(
        (
            state.get("Status") == representation_profile["container_status"],
            state.get("Running") is representation_profile["running"],
            config.get("OpenStdin") is True,
            host.get("PortBindings") in (None, {}),
            all(value in (None, []) for value in ports.values()),
            host.get("Binds") in (None, []),
            host.get("Mounts") in (None, []),
            (host.get("LogConfig") or {}).get("Type") == "none",
            (host.get("RestartPolicy") or {}).get("Name") == "no",
            host.get("Memory") == profile["server_memory_bytes"],
            host.get("NanoCpus") == profile["server_nano_cpus"],
            host.get("PidsLimit") == profile["server_pids_limit"],
            host.get("SecurityOpt") == ["no-new-privileges"],
            isinstance(tmpfs, str)
            and set(tmpfs.split(","))
            == set(profile["server_tmpfs_options"].split(",")),
            labels.get(profile["nonce_label_key"]) == nonce,
            canaries_absent,
            credential_keys_absent,
            nonce_absent_outside_label,
        )
    )
    if not containment:
        _fail("representation", "created_state_profile_denied")
    return {
        "network_cardinality": 1,
        "network_key_relation": network_key_relation,
        "network_mode_relation": network_mode_relation,
        "endpoint_network_id_relation": endpoint_relation,
    }


def _matching_resource_count(executable: str, profile: dict[str, Any]) -> int:
    label = (
        f"{profile['conformance_label_key']}="
        f"{profile['conformance_label_value']}"
    )
    containers = _docker(
        executable,
        "ps",
        "-aq",
        "--filter",
        f"label={label}",
    ).stdout.splitlines()
    networks = _docker(
        executable,
        "network",
        "ls",
        "-q",
        "--filter",
        f"label={label}",
    ).stdout.splitlines()
    return len([value for value in (*containers, *networks) if value.strip()])


def _cleanup(
    executable: str,
    profile: dict[str, Any],
    *,
    container_id: str | None,
    container_name: str,
    network_id: str | None,
    network_name: str,
    nonce: str,
) -> dict[str, Any]:
    container_absent = container_id is None
    network_absent = network_id is None
    if container_id is not None:
        inspect = _docker(
            executable, "container", "inspect", container_id, check=False
        )
        if inspect.returncode != 0:
            container_absent = True
        else:
            rows = json.loads(inspect.stdout)
            if (
                isinstance(rows, list)
                and len(rows) == 1
                and isinstance(rows[0], dict)
                and _container_owned(
                    rows[0],
                    container_id=container_id,
                    container_name=container_name,
                    nonce=nonce,
                    profile=profile,
                )
            ):
                _docker(executable, "rm", "--force", container_id, check=False)
                container_absent = (
                    _docker(
                        executable,
                        "container",
                        "inspect",
                        container_id,
                        check=False,
                    ).returncode
                    != 0
                )
    if network_id is not None:
        inspect = _docker(executable, "network", "inspect", network_id, check=False)
        if inspect.returncode != 0:
            network_absent = True
        else:
            rows = json.loads(inspect.stdout)
            if (
                isinstance(rows, list)
                and len(rows) == 1
                and isinstance(rows[0], dict)
                and _network_owned(
                    rows[0],
                    network_id=network_id,
                    network_name=network_name,
                    nonce=nonce,
                    profile=profile,
                )
            ):
                _docker(executable, "network", "rm", network_id, check=False)
                network_absent = (
                    _docker(
                        executable, "network", "inspect", network_id, check=False
                    ).returncode
                    != 0
                )
    matching = _matching_resource_count(executable, profile)
    passed = container_absent and network_absent and matching == 0
    return {
        "container_absent": container_absent,
        "network_absent": network_absent,
        "matching_labelled_resources": matching,
        "status": "cleanup_verified" if passed else "cleanup_unverified",
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_bytes(_json_bytes(value))


def _failure(
    error: ConformanceFailure, cleanup: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.docker-created-state-profile-conformance-failure.v1",
        "result": "failed_closed",
        "stage": error.stage,
        "code": error.code,
        "execution_count": 1,
        "retry_count": 0,
        "success_released": False,
        "cleanup": cleanup,
    }


def run_rehearsal() -> dict[str, Any]:
    if EVIDENCE_PATH.exists() or FAILURE_PATH.exists():
        _fail("static", "terminal_artifact_already_exists")
    static = static_check(require_historical_current=True)
    contract = validate_contract(_load_json(CONTRACT_PATH))
    profile = contract["docker_profile"]
    executable = _docker_executable(profile)
    _engine_and_image(executable, profile)
    if _matching_resource_count(executable, profile) != 0:
        _fail("environment", "preexisting_labelled_resource")
    base_contract = historical.validate_contract(_load_json(BASE_CONTRACT_PATH))
    nonce = secrets.token_hex(16)
    canaries = (secrets.token_hex(32), secrets.token_hex(32))
    network_id: str | None = None
    network_name = ""
    container_id: str | None = None
    container_name = ""
    primary: ConformanceFailure | None = None
    representation: dict[str, Any] | None = None
    cleanup: dict[str, Any] = {
        "container_absent": True,
        "network_absent": True,
        "matching_labelled_resources": -1,
        "status": "not_started",
    }
    try:
        network_name = profile["network_name_prefix"] + secrets.token_hex(8)
        network_id = _docker(
            executable,
            "network",
            "create",
            "--internal",
            "--driver",
            "bridge",
            "--label",
            f"{profile['harness_label_key']}={profile['harness_label_value']}",
            "--label",
            f"{profile['nonce_label_key']}={nonce}",
            "--label",
            (
                f"{profile['conformance_label_key']}="
                f"{profile['conformance_label_value']}"
            ),
            network_name,
        ).stdout.strip()
        if DOCKER_ID.fullmatch(network_id) is None:
            _fail("environment", "network_id_invalid")
        network_rows = _docker_json(executable, "network", "inspect", network_id)
        if len(network_rows) != 1 or not _network_owned(
            network_rows[0],
            network_id=network_id,
            network_name=network_name,
            nonce=nonce,
            profile=profile,
        ):
            _fail("environment", "network_ownership_mismatch")
        container_name = profile["container_name_prefix"] + secrets.token_hex(8)
        container_id = _docker(
            executable,
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
            "--label",
            (
                f"{profile['conformance_label_key']}="
                f"{profile['conformance_label_value']}"
            ),
            "--network",
            network_id,
            "--network-alias",
            profile["network_alias"],
            "--log-driver",
            "none",
            "--tmpfs",
            (
                f"{profile['server_tmpfs_destination']}:"
                f"{profile['server_tmpfs_options']}"
            ),
            "--memory",
            str(profile["server_memory_bytes"]),
            "--cpus",
            "1",
            "--pids-limit",
            str(profile["server_pids_limit"]),
            "--restart",
            "no",
            "--security-opt",
            "no-new-privileges",
            "--entrypoint",
            "sh",
            profile["image_reference"],
            "-c",
            historical._server_wrapper(base_contract),
        ).stdout.strip()
        if DOCKER_ID.fullmatch(container_id) is None:
            _fail("environment", "container_id_invalid")
        rows = _docker_json(executable, "container", "inspect", container_id)
        if len(rows) != 1:
            _fail("representation", "container_inspect_cardinality")
        representation = classify_created_state(
            rows[0],
            container_id=container_id,
            container_name=container_name,
            network_id=network_id,
            network_name=network_name,
            nonce=nonce,
            canaries=canaries,
            profile=profile,
            representation_profile=contract["representation_profile"],
        )
    except ConformanceFailure as error:
        primary = error
    except Exception:
        primary = ConformanceFailure("environment", "unexpected_controller_failure")
    finally:
        try:
            cleanup = _cleanup(
                executable,
                profile,
                container_id=container_id,
                container_name=container_name,
                network_id=network_id,
                network_name=network_name,
                nonce=nonce,
            )
        except Exception:
            cleanup = {
                "container_absent": False,
                "network_absent": False,
                "matching_labelled_resources": -1,
                "status": "cleanup_unverified",
            }
    if cleanup["status"] != "cleanup_verified" and primary is None:
        primary = ConformanceFailure("cleanup", "exact_cleanup_unverified")
    if primary is not None:
        failure = _failure(primary, cleanup)
        _validate_failure(failure, (*canaries, nonce))
        _write_json(FAILURE_PATH, failure)
        raise primary
    if representation is None:
        _fail("evidence", "representation_missing")
    result = _example_evidence()
    result["source_head"] = static["source_head"]
    result["representation"] = representation
    result["cleanup"] = cleanup
    _validate_evidence(result, (*canaries, nonce))
    _write_json(EVIDENCE_PATH, result)
    return result


def attest_repair() -> dict[str, Any]:
    static = static_check(require_historical_current=False)
    if not EVIDENCE_PATH.is_file() or FAILURE_PATH.exists() or ATTESTATION_PATH.exists():
        _fail("evidence", "repair_attestation_precondition_failed")
    evidence = _load_json(EVIDENCE_PATH)
    _validate_evidence(evidence)
    current_sha256 = _sha256_path(Path(historical.__file__))
    if current_sha256 == HISTORICAL_HARNESS_SHA256:
        _fail("evidence", "corrected_harness_not_distinct")
    source = Path(historical.__file__).read_text(encoding="utf-8")
    for predicate in EXPECTED_CORRECTED_PREDICATES:
        if f'"{predicate}"' not in source:
            _fail("evidence", "corrected_predicate_missing")
    attestation = {
        "schema_version": (
            "emr4.docker-created-state-profile-conformance-repair-attestation.v1"
        ),
        "result": "profile_predicates_corrected_and_bound",
        "source_head": static["source_head"],
        "representation_evidence_sha256": _sha256_path(EVIDENCE_PATH),
        "historical_harness_source": HISTORICAL_HARNESS_SOURCE,
        "historical_harness_sha256": HISTORICAL_HARNESS_SHA256,
        "corrected_harness_sha256": current_sha256,
        "corrected_predicates": EXPECTED_CORRECTED_PREDICATES,
        "database_execution_authorized": False,
    }
    _validate_attestation(attestation)
    _write_json(ATTESTATION_PATH, attestation)
    return attestation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--attest-repair", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        if arguments.check:
            result = static_check(
                require_historical_current=not EVIDENCE_PATH.exists()
            )
        elif arguments.execute:
            result = run_rehearsal()
        else:
            result = attest_repair()
    except ConformanceFailure as error:
        print(json.dumps({"result": "failed_closed", "code": error.code}))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
