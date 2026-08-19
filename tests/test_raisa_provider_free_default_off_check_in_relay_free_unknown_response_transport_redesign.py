from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from scripts import (
    raisa_provider_free_default_off_check_in_relay_free_unknown_response_transport_redesign
    as transport,
)


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / (
    "orchestration/continuity/raisa-provider-free-default-off-check-in-"
    "relay-free-unknown-response-transport-redesign"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _baseline_state() -> dict:
    return {
        "identity_match": True,
        "running": False,
        "exit_code": 42,
        "oom_killed": False,
        "state_error": "",
        "restart_count": 0,
    }


def _inspect_row(contract: dict, *, container_id: str, name: str, nonce: str) -> dict:
    profile = contract["containment_profile"]
    return {
        "Id": container_id,
        "Name": "/" + name,
        "Image": profile["image_id"],
        "RestartCount": 0,
        "Config": {
            "Image": profile["image_reference"],
            "OpenStdin": True,
            "Tty": False,
            "Entrypoint": ["sh"],
            "Cmd": ["-c", transport.WRAPPER],
            "Labels": {
                profile["harness_label_key"]: profile["harness_label_value"],
                profile["nonce_label_key"]: nonce,
            },
        },
        "HostConfig": {
            "NetworkMode": "none",
            "LogConfig": {"Type": "none"},
            "PortBindings": {},
            "Binds": None,
            "Mounts": None,
            "ReadonlyRootfs": True,
            "CapDrop": ["ALL"],
            "SecurityOpt": ["no-new-privileges"],
            "Memory": profile["memory_bytes"],
            "NanoCpus": profile["nano_cpus"],
            "PidsLimit": profile["pids_limit"],
            "RestartPolicy": {"Name": "no"},
            "Tmpfs": {profile["tmpfs_destination"]: profile["tmpfs_options"]},
        },
        "State": {
            "Running": False,
            "ExitCode": 42,
            "OOMKilled": False,
            "Error": "",
        },
    }


def test_contract_sources_and_wrapper_are_exact() -> None:
    contract = transport.validate_contract(_json(TOPIC / "contract.json"))
    assert contract["decision_transition_source"] == transport.DECISION_SOURCE
    assert contract["accepted_runtime_role_source"] == (
        "6a2832575e9b4df5c40a13984db7281e79814a94"
    )
    assert contract["containment_profile"]["wrapper_sha256"] == transport._sha256(
        transport.WRAPPER
    )
    assert len(contract["source_bindings"]) == 14
    attempt_two = next(
        binding
        for binding in contract["source_bindings"]
        if binding["path"].endswith("rehearsal-failure-evidence-attempt-002.json")
    )
    assert attempt_two["sha256"] == (
        "bea605006bf36996d439876a4976ec5b733ddc4bb841d5942aae1057c5f514ed"
    )


def test_contract_and_state_hostile_mutation_gates_have_zero_escapes() -> None:
    contract = transport.validate_contract(_json(TOPIC / "contract.json"))
    attempted, rejected = transport.hostile_contract_mutations_rejected(
        contract, 256
    )
    assert (attempted, rejected) == (256, 256)
    attempted, rejected = transport.hostile_states_rejected(96)
    assert (attempted, rejected) == (96, 96)


def test_only_exact_closed_oci_state_is_admitted() -> None:
    baseline = _baseline_state()
    assert transport.classify_oci_state(baseline) == transport.CONTAINER_OUTCOME
    replacements = {
        "identity_match": False,
        "running": True,
        "exit_code": 0,
        "oom_killed": True,
        "state_error": "runtime_error",
        "restart_count": 1,
    }
    for field, value in replacements.items():
        candidate = copy.deepcopy(baseline)
        candidate[field] = value
        assert transport.classify_oci_state(candidate) == transport.DENIED_OUTCOME
    for invalid in (None, [], {**baseline, "extra": True}):
        assert transport.classify_oci_state(invalid) == transport.DENIED_OUTCOME


def test_container_identity_and_closed_state_are_exact() -> None:
    contract = transport.validate_contract(_json(TOPIC / "contract.json"))
    container_id = "a" * 64
    name = "emr4-checkin-relay-free-0123456789abcdef"
    nonce = "b" * 32
    row = _inspect_row(contract, container_id=container_id, name=name, nonce=nonce)
    assert transport._identity_matches(
        row,
        container_id=container_id,
        container_name=name,
        nonce=nonce,
        contract=contract,
    )
    state = transport._closed_state(row, identity_match=True)
    assert state == _baseline_state()
    row["HostConfig"]["NetworkMode"] = "bridge"
    assert not transport._identity_matches(
        row,
        container_id=container_id,
        container_name=name,
        nonce=nonce,
        contract=contract,
    )


def test_evidence_schema_is_closed_and_requires_no_database() -> None:
    schema = _json(TOPIC / "evidence.schema.json")
    evidence = {
        "schema_version": "emr4.relay-free-oci-transport-evidence.v1",
        "result": transport.PASS_RESULT,
        "evidence_label": transport.EVIDENCE_LABEL,
        "source_head": "c" * 40,
        "decision_transition_source": transport.DECISION_SOURCE,
        "contract_sha256": "d" * 64,
        "source_binding_count": 14,
        "hostile_mutations": {
            "contract_attempted": 256,
            "contract_rejected": 256,
            "state_attempted": 96,
            "state_rejected": 96,
            "escapes": 0,
        },
        "containment": {
            "image_reference": "postgres:16-bookworm",
            "image_id_sha256": "e" * 64,
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
            "classification": transport.CONTAINER_OUTCOME,
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
        "lifecycle": [f"closed_step_{index}" for index in range(8)],
        "cleanup": {
            "attachment_absent_before_cleanup": True,
            "captured_container_absent": True,
            "matching_nonce_resources": 0,
            "status": "cleanup_verified",
        },
        "elapsed_milliseconds": 100,
    }
    Draft202012Validator(schema).validate(evidence)
    escaped = copy.deepcopy(evidence)
    escaped["raw_output"] = "forbidden"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(escaped)
    database = copy.deepcopy(evidence)
    database["database"]["postgres_process_started"] = True
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(database)


def test_redaction_rejects_secret_values_and_forbidden_keys() -> None:
    transport._assert_redacted(
        {"closed_state": "passed"}, forbidden_values=("sensitive",)
    )
    with pytest.raises(transport.TransportFailure, match="forbidden_value"):
        transport._assert_redacted(
            {"value": "contains-sensitive-material"},
            forbidden_values=("sensitive",),
        )
    with pytest.raises(transport.TransportFailure, match="forbidden_key"):
        transport._assert_redacted(
            {"raw_output": "none"}, forbidden_values=("sensitive",)
        )


def test_new_transport_source_has_no_relay_or_multiprocessing_path() -> None:
    source = (
        ROOT
        / "scripts/raisa_provider_free_default_off_check_in_relay_free_unknown_response_transport_redesign.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "import socket",
        "import multiprocessing",
        "multiprocessing.Queue",
        "DockerExecRelay",
        "relay.start(",
        "host_port",
    ):
        assert forbidden not in source
    assert '"--network",\n            "none"' in source
    assert '"--log-driver",\n            "none"' in source
    assert '"--pull",\n            "never"' in source
