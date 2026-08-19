from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts import (
    raisa_provider_free_docker_created_state_profile_conformance_repair as repair,
)


def _contract() -> dict[str, object]:
    return repair.validate_contract(repair._load_json(repair.CONTRACT_PATH))


def _created_row(
    *,
    endpoint_network_id: str = "",
    network_key: str | None = None,
    network_mode: str | None = None,
) -> tuple[dict[str, object], dict[str, str]]:
    profile = repair.EXPECTED_DOCKER_PROFILE
    values = {
        "container_id": "c" * 64,
        "container_name": "emr4-checkin-cspr-container-0123456789abcdef",
        "network_id": "a" * 64,
        "network_name": "emr4-checkin-cspr-net-0123456789abcdef",
        "nonce": "b" * 32,
    }
    key = values["network_name"] if network_key is None else network_key
    mode = values["network_id"] if network_mode is None else network_mode
    row: dict[str, object] = {
        "Id": values["container_id"],
        "Name": "/" + values["container_name"],
        "Image": profile["image_id"],
        "Config": {
            "Image": profile["image_reference"],
            "Labels": {
                profile["harness_label_key"]: profile["harness_label_value"],
                profile["nonce_label_key"]: values["nonce"],
                profile["conformance_label_key"]: profile[
                    "conformance_label_value"
                ],
            },
            "OpenStdin": True,
            "Env": ["PG_MAJOR=16"],
        },
        "HostConfig": {
            "NetworkMode": mode,
            "PortBindings": {},
            "Binds": None,
            "Mounts": None,
            "LogConfig": {"Type": "none"},
            "RestartPolicy": {"Name": "no"},
            "Memory": profile["server_memory_bytes"],
            "NanoCpus": profile["server_nano_cpus"],
            "PidsLimit": profile["server_pids_limit"],
            "SecurityOpt": ["no-new-privileges"],
            "Tmpfs": {
                profile["server_tmpfs_destination"]: profile[
                    "server_tmpfs_options"
                ]
            },
        },
        "State": {"Status": "created", "Running": False},
        "NetworkSettings": {
            "Ports": {},
            "Networks": {key: {"NetworkID": endpoint_network_id}},
        },
    }
    return row, values


def _classify(row: dict[str, object], values: dict[str, str]) -> dict[str, object]:
    return repair.classify_created_state(
        row,
        container_id=values["container_id"],
        container_name=values["container_name"],
        network_id=values["network_id"],
        network_name=values["network_name"],
        nonce=values["nonce"],
        canaries=("d" * 64, "e" * 64),
        profile=repair.EXPECTED_DOCKER_PROFILE,
        representation_profile=repair.EXPECTED_REPRESENTATION_PROFILE,
    )


def test_static_admission_binds_historical_bytes_and_hostile_floor() -> None:
    result = repair.static_check(require_historical_current=False)
    assert result["status"] == "passed"
    assert result["source_head"] and len(result["source_head"]) == 40
    assert result["current_harness_is_historical"] is False
    assert result["hostile_contract_mutations"] == {
        "attempted": 128,
        "rejected": 128,
    }


def test_contract_is_closed_and_full_git_bound() -> None:
    contract = _contract()
    assert contract["plan_source"] == repair.PLAN_SOURCE
    assert len(contract["plan_source"]) == 40
    assert contract["historical_harness"]["source_commit"] == (
        repair.HISTORICAL_HARNESS_SOURCE
    )
    assert contract["correction_profile"]["credential_scan_includes_nonce"] is False
    assert contract["correction_profile"]["artifact_redaction_includes_nonce"] is True
    hostile = copy.deepcopy(contract)
    hostile["plan_source"] = hostile["plan_source"][:7]
    with pytest.raises(repair.ConformanceFailure, match="contract_schema_invalid"):
        repair.validate_contract(hostile)


def test_command_allowlist_has_no_process_or_credential_delivery_path() -> None:
    for denied in (
        ("start", "container"),
        ("attach", "container"),
        ("exec", "container"),
        ("run", "image"),
        ("logs", "container"),
        ("cp", "source", "target"),
    ):
        assert repair._docker_command_allowed(denied) is False
    for admitted in (
        ("version",),
        ("image", "inspect"),
        ("network", "create"),
        ("network", "inspect"),
        ("create",),
        ("container", "inspect"),
        ("rm",),
        ("network", "rm"),
    ):
        assert repair._docker_command_allowed(admitted) is True


def test_created_state_accepts_exact_empty_endpoint_representation() -> None:
    row, values = _created_row(endpoint_network_id="")
    assert _classify(row, values) == {
        "network_cardinality": 1,
        "network_key_relation": "captured_network_name",
        "network_mode_relation": "captured_network_id",
        "endpoint_network_id_relation": "empty",
    }


def test_deterministic_attached_fixture_accepts_only_captured_endpoint_id() -> None:
    row, values = _created_row(endpoint_network_id="a" * 64)
    assert _classify(row, values)["endpoint_network_id_relation"] == (
        "captured_network_id"
    )
    row["NetworkSettings"]["Networks"][values["network_name"]]["NetworkID"] = (
        "f" * 64
    )
    with pytest.raises(
        repair.ConformanceFailure, match="endpoint_network_id_relation_denied"
    ):
        _classify(row, values)


@pytest.mark.parametrize(
    ("network_key", "network_mode", "code"),
    [
        ("foreign-network", None, "network_key_relation_denied"),
        (None, "foreign-network", "network_mode_relation_denied"),
    ],
)
def test_foreign_network_key_or_mode_denies(
    network_key: str | None, network_mode: str | None, code: str
) -> None:
    row, values = _created_row(
        network_key=network_key, network_mode=network_mode
    )
    with pytest.raises(repair.ConformanceFailure, match=code):
        _classify(row, values)


def test_nonce_is_allowed_only_at_exact_label_and_canaries_are_absent() -> None:
    row, values = _created_row()
    row["Config"]["Env"].append("UNRELATED=" + values["nonce"])
    with pytest.raises(repair.ConformanceFailure, match="created_state_profile_denied"):
        _classify(row, values)
    row, values = _created_row()
    row["Config"]["Env"].append("UNRELATED=" + "d" * 64)
    with pytest.raises(repair.ConformanceFailure, match="created_state_profile_denied"):
        _classify(row, values)
    row, values = _created_row()
    del row["Config"]["Labels"][repair.EXPECTED_DOCKER_PROFILE["nonce_label_key"]]
    with pytest.raises(repair.ConformanceFailure, match="container_ownership_mismatch"):
        _classify(row, values)


@pytest.mark.parametrize(
    "credential_key",
    ["PGPASSWORD", "POSTGRES_PASSWORD", "POSTGRES_PASSWORD_FILE"],
)
def test_credential_key_in_environment_denies(credential_key: str) -> None:
    row, values = _created_row()
    row["Config"]["Env"].append(f"{credential_key}=not-a-real-credential")
    with pytest.raises(repair.ConformanceFailure, match="created_state_profile_denied"):
        _classify(row, values)


def test_evidence_and_failure_schemas_deny_raw_or_extra_fields() -> None:
    evidence = repair._example_evidence()
    repair._validate_evidence(evidence)
    hostile = json.loads(json.dumps(evidence))
    hostile["docker_inspect"] = {"raw": True}
    with pytest.raises(repair.ConformanceFailure, match="evidence_schema_invalid"):
        repair._validate_evidence(hostile)
    failure = {
        "schema_version": (
            "emr4.docker-created-state-profile-conformance-failure.v1"
        ),
        "result": "failed_closed",
        "stage": "representation",
        "code": "network_mode_relation_denied",
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
    repair._validate_failure(failure)
    failure["retry_count"] = 1
    with pytest.raises(repair.ConformanceFailure, match="failure_schema_invalid"):
        repair._validate_failure(failure)


def test_cleanup_removes_only_exact_owned_objects(monkeypatch: pytest.MonkeyPatch) -> None:
    row, values = _created_row()
    network_row = {
        "Id": values["network_id"],
        "Name": values["network_name"],
        "Internal": True,
        "Driver": "bridge",
        "Labels": {
            repair.EXPECTED_DOCKER_PROFILE["harness_label_key"]: repair.EXPECTED_DOCKER_PROFILE[
                "harness_label_value"
            ],
            repair.EXPECTED_DOCKER_PROFILE["nonce_label_key"]: values["nonce"],
            repair.EXPECTED_DOCKER_PROFILE["conformance_label_key"]: repair.EXPECTED_DOCKER_PROFILE[
                "conformance_label_value"
            ],
        },
    }
    present = {"container": True, "network": True}
    calls: list[tuple[str, ...]] = []

    def fake_docker(
        executable: str,
        *arguments: str,
        check: bool = True,
        timeout: int = 30,
    ) -> object:
        del executable, check, timeout
        calls.append(arguments)
        if arguments[:2] == ("container", "inspect"):
            return type(
                "Result",
                (),
                {
                    "returncode": 0 if present["container"] else 1,
                    "stdout": json.dumps([row]) if present["container"] else "",
                },
            )()
        if arguments[:2] == ("network", "inspect"):
            return type(
                "Result",
                (),
                {
                    "returncode": 0 if present["network"] else 1,
                    "stdout": (
                        json.dumps([network_row]) if present["network"] else ""
                    ),
                },
            )()
        if arguments[0] == "rm":
            present["container"] = False
        if arguments[:2] == ("network", "rm"):
            present["network"] = False
        return type("Result", (), {"returncode": 0, "stdout": ""})()

    monkeypatch.setattr(repair, "_docker", fake_docker)
    monkeypatch.setattr(repair, "_matching_resource_count", lambda *_: 0)
    cleanup = repair._cleanup(
        "docker.exe",
        repair.EXPECTED_DOCKER_PROFILE,
        container_id=values["container_id"],
        container_name=values["container_name"],
        network_id=values["network_id"],
        network_name=values["network_name"],
        nonce=values["nonce"],
    )
    assert cleanup["status"] == "cleanup_verified"
    assert ("rm", "--force", values["container_id"]) in calls
    assert ("network", "rm", values["network_id"]) in calls


def test_one_execution_evidence_and_repair_attestation_are_retained() -> None:
    assert repair.EVIDENCE_PATH.exists()
    assert not repair.FAILURE_PATH.exists()
    assert repair.ATTESTATION_PATH.exists()
    evidence = repair._load_json(repair.EVIDENCE_PATH)
    repair._validate_evidence(evidence)
    assert evidence["execution_count"] == 1
    assert evidence["retry_count"] == 0
    attestation = repair._load_json(repair.ATTESTATION_PATH)
    repair._validate_attestation(attestation)
    assert attestation["database_execution_authorized"] is False


def test_source_contains_no_database_or_product_import() -> None:
    source = Path(repair.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "psycopg",
        "sqlalchemy",
        "app.models",
        "app.routers",
        "subprocess.Popen",
    ):
        assert forbidden not in source
