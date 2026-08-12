from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal
    as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = rehearsal._load_json(rehearsal.CONTRACT_PATH)  # noqa: SLF001
SCHEMA = rehearsal._load_json(rehearsal.SCHEMA_PATH)  # noqa: SLF001
EVIDENCE_SCHEMA = rehearsal._load_json(rehearsal.EVIDENCE_SCHEMA_PATH)  # noqa: SLF001


def test_contract_schema_sources_scenarios_and_hostile_gate_pass() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    Draft202012Validator(SCHEMA).validate(CONTRACT)
    observed, hashes = rehearsal.verify_contract()
    assert observed == CONTRACT
    assert len(hashes) == 11
    assert rehearsal.hostile_mutations_rejected(CONTRACT) == 100
    assert [item["id"] for item in CONTRACT["scenarios"]] == [
        f"BTR-S{index:02d}" for index in range(1, 17)
    ]
    assert sum(CONTRACT["scenario_categories"].values()) == 16


def test_contract_rejects_added_reordered_or_widened_surfaces() -> None:
    mutations = []
    added = copy.deepcopy(CONTRACT)
    added["caller_database_url"] = "postgresql://product"
    mutations.append(added)
    reordered = copy.deepcopy(CONTRACT)
    reordered["scenarios"][0], reordered["scenarios"][1] = (
        reordered["scenarios"][1],
        reordered["scenarios"][0],
    )
    mutations.append(reordered)
    widened = copy.deepcopy(CONTRACT)
    widened["transaction_contract"]["concurrency"] = True
    mutations.append(widened)
    for candidate in mutations:
        with pytest.raises(rehearsal.RehearsalFailure):
            rehearsal._validate_contract(candidate, require_digest=False)  # noqa: SLF001


def test_internal_network_container_and_fixed_relay_argv_are_exact() -> None:
    profile = CONTRACT["docker_profile"]
    network = rehearsal.build_network_argv(
        r"C:\Docker\docker.exe",
        "emr4-status-confirm-btr-net-0123456789abcdef",
        "0" * 32,
        profile,
    )
    container = rehearsal.build_container_argv(
        r"C:\Docker\docker.exe",
        "emr4-status-confirm-btr-pg16-0123456789abcdef",
        "0" * 32,
        "a" * 64,
        profile,
    )
    assert network[:3] == [r"C:\Docker\docker.exe", "network", "create"]
    assert "--internal" in network
    joined = " ".join(container)
    assert "--pull never" in joined
    assert f"--network {'a' * 64}" in joined
    assert "--publish" not in container
    assert "--tmpfs /var/lib/postgresql/data:" in joined
    assert "--memory 512m" in joined
    assert "--cpus 1" in joined
    assert "--pids-limit 128" in joined
    for forbidden in ("0.0.0.0", "--volume", "--mount", "trust"):
        assert forbidden not in container
    relay = rehearsal.build_relay_argv(
        r"C:\Docker\docker.exe", "b" * 64, profile
    )
    assert relay == [
        r"C:\Docker\docker.exe",
        "exec",
        "-i",
        "b" * 64,
        "bash",
        "-c",
        rehearsal.FIXED_RELAY_COMMAND,
    ]
    assert profile["relay_host_ip"] == "127.0.0.1"
    assert profile["relay_dynamic_host_port"] is True


def _owned_network(*, empty: bool = True) -> dict:
    return {
        "Id": "a" * 64,
        "Name": "emr4-status-confirm-btr-net-0123456789abcdef",
        "Driver": "bridge",
        "Internal": True,
        "Labels": {
            "com.emr4.harness": "status-confirm-pg16-behavior-v1",
            "com.emr4.cleanup-nonce": "0" * 32,
        },
        "Containers": {} if empty else {"b" * 64: {}},
    }


def _owned_container() -> dict:
    profile = CONTRACT["docker_profile"]
    return {
        "Id": "b" * 64,
        "Name": "/emr4-status-confirm-btr-pg16-0123456789abcdef",
        "Image": "sha256:" + "c" * 64,
        "Config": {
            "Image": profile["image_reference"],
            "Labels": {
                "com.emr4.harness": profile["harness_label"],
                "com.emr4.cleanup-nonce": "0" * 32,
            },
            "Env": [
                f"POSTGRES_USER={profile['postgres_user']}",
                f"POSTGRES_PASSWORD={profile['postgres_password']}",
                f"POSTGRES_DB={profile['postgres_database']}",
                f"PGDATA={profile['pgdata']}",
            ],
        },
        "HostConfig": {
            "Binds": None,
            "Privileged": False,
            "Memory": profile["memory_bytes"],
            "NanoCpus": profile["nano_cpus"],
            "PidsLimit": profile["pids_limit"],
            "RestartPolicy": {"Name": "no"},
            "Tmpfs": {profile["data_destination"]: profile["tmpfs_options"]},
            "PortBindings": {},
        },
        "NetworkSettings": {
            "Networks": {"owned": {"NetworkID": "a" * 64}},
            "Ports": {"5432/tcp": None},
        },
        "Mounts": [],
    }


def test_owned_network_and_container_profiles_fail_closed() -> None:
    profile = CONTRACT["docker_profile"]
    network_kwargs = {
        "network_id": "a" * 64,
        "name": "emr4-status-confirm-btr-net-0123456789abcdef",
        "nonce": "0" * 32,
        "profile": profile,
        "require_empty": True,
    }
    assert rehearsal._network_owned(_owned_network(), **network_kwargs)  # noqa: SLF001
    assert not rehearsal._network_owned(  # noqa: SLF001
        _owned_network(empty=False), **network_kwargs
    )
    container_kwargs = {
        "container_id": "b" * 64,
        "name": "emr4-status-confirm-btr-pg16-0123456789abcdef",
        "nonce": "0" * 32,
        "image_id": "sha256:" + "c" * 64,
        "network_id": "a" * 64,
        "profile": profile,
    }
    assert rehearsal._container_profile(  # noqa: SLF001
        _owned_container(), **container_kwargs
    ) is True
    for mutate in ("published_host", "network", "mount", "port", "bounds"):
        item = _owned_container()
        if mutate == "published_host":
            item["NetworkSettings"]["Ports"]["5432/tcp"] = [
                {"HostIp": "0.0.0.0", "HostPort": "49153"}
            ]
        elif mutate == "network":
            item["NetworkSettings"]["Networks"]["owned"]["NetworkID"] = "d" * 64
        elif mutate == "mount":
            item["Mounts"] = [{"Type": "volume"}]
        elif mutate == "port":
            item["HostConfig"]["PortBindings"]["9999/tcp"] = [{}]
        else:
            item["HostConfig"]["Memory"] = 0
        assert rehearsal._container_profile(  # noqa: SLF001
            item, **container_kwargs
        ) is False


@pytest.mark.parametrize(
    ("statement", "expected"),
    [
        ("SELECT * FROM practices FOR SHARE", "practice_for_share"),
        ("SELECT * FROM appointments FOR UPDATE", "appointment_for_update"),
        (
            "INSERT INTO appointment_command_idempotency VALUES (1) ON CONFLICT DO NOTHING",
            "idempotency_insert_on_conflict",
        ),
        (
            "SELECT * FROM appointment_command_idempotency FOR UPDATE",
            "idempotency_for_update",
        ),
        ("SELECT * FROM practices", None),
    ],
)
def test_statement_classification_is_value_free(statement: str, expected: str | None) -> None:
    assert rehearsal._statement_token(statement) == expected  # noqa: SLF001


def test_cleanup_uses_captured_ids_container_then_empty_network(monkeypatch) -> None:
    calls: list[list[str]] = []
    responses = [
        rehearsal.catalogue.ProcessResult(0, json.dumps([_owned_container()]).encode(), b""),
        rehearsal.catalogue.ProcessResult(0, b"b" * 64 + b"\n", b""),
        rehearsal.catalogue.ProcessResult(1, b"", b"Error: No such object: " + b"b" * 64),
        rehearsal.catalogue.ProcessResult(0, json.dumps([_owned_network()]).encode(), b""),
        rehearsal.catalogue.ProcessResult(0, b"a" * 64 + b"\n", b""),
        rehearsal.catalogue.ProcessResult(1, b"", b"Error: No such network: " + b"a" * 64),
    ]

    def runner(argv, stdin, timeout, cap):
        del stdin, timeout, cap
        calls.append(argv)
        return responses.pop(0)

    monkeypatch.setattr(rehearsal.catalogue, "_run", runner)
    result = rehearsal._cleanup(  # noqa: SLF001
        r"C:\Docker\docker.exe",
        container_id="b" * 64,
        container_name="emr4-status-confirm-btr-pg16-0123456789abcdef",
        network_id="a" * 64,
        network_name="emr4-status-confirm-btr-net-0123456789abcdef",
        nonce="0" * 32,
        image_id="sha256:" + "c" * 64,
        profile=CONTRACT["docker_profile"],
    )
    assert result["status"] == "cleanup_verified"
    assert calls[1][1:4] == ["container", "rm", "--force"]
    assert calls[4][1:3] == ["network", "rm"]


def test_harness_has_no_shell_or_broad_docker_discovery() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"run", "Popen"}:
                keywords = {item.arg: item.value for item in node.keywords}
                if node.func.attr == "Popen":
                    assert "shell" in keywords
                if "shell" in keywords:
                    assert isinstance(keywords["shell"], ast.Constant)
                    assert keywords["shell"].value is False
    for forbidden in (
        '"container", "ls"',
        '"network", "ls"',
        '"image", "ls"',
        '"volume", "ls"',
        '"prune"',
        '"login"',
    ):
        assert forbidden not in source


def test_main_rejects_caller_selected_arguments(monkeypatch) -> None:
    monkeypatch.setattr(rehearsal.sys, "argv", ["harness", "--port", "5432"])
    assert rehearsal.main() == 2


def test_pass_evidence_when_present_is_complete_and_minimized() -> None:
    if not rehearsal.EVIDENCE_PATH.exists():
        pytest.skip("occupied evidence not generated yet")
    evidence = rehearsal._load_json(rehearsal.EVIDENCE_PATH)  # noqa: SLF001
    Draft202012Validator.check_schema(EVIDENCE_SCHEMA)
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["hostile_mutations_rejected"] == 100
    assert len(evidence["scenarios"]) == 16
    assert all(item["status"] == "passed" for item in evidence["scenarios"])
    assert evidence["cleanup"]["status"] == "cleanup_verified"
    serialized = json.dumps(evidence).lower()
    for forbidden in (
        CONTRACT["docker_profile"]["postgres_password"],
        "postgresql+psycopg://",
        "response_body_canonical_bytes",
        "session_binding_digest",
        "raw_sql",
    ):
        assert forbidden not in serialized
