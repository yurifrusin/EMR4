from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal
    as rehearsal,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal
    as status_btr,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = rehearsal._load_json(rehearsal.CONTRACT_PATH)  # noqa: SLF001
SCHEMA = rehearsal._load_json(rehearsal.SCHEMA_PATH)  # noqa: SLF001
EVIDENCE_SCHEMA = rehearsal._load_json(rehearsal.EVIDENCE_SCHEMA_PATH)  # noqa: SLF001
PROFILE = CONTRACT["docker_profile"]


def test_contract_schema_sources_groups_and_hostile_gate_pass() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    Draft202012Validator(SCHEMA).validate(CONTRACT)
    rehearsal._validate_contract(CONTRACT, require_digest=True)  # noqa: SLF001
    assert len(CONTRACT["source_bindings"]) == 16
    assert rehearsal.hostile_mutations_rejected(CONTRACT) == rehearsal.HOSTILE_MUTATION_TARGET
    assert [g["id"] for g in CONTRACT["authority_groups"]] == [
        f"AUTH-S{index:02d}" for index in range(1, 10)
    ]
    assert [g["id"] for g in CONTRACT["transaction_groups"]] == [
        f"TX-S{index:02d}" for index in range(1, 12)
    ]
    assert sum(CONTRACT["scenario_categories"].values()) == 20


def test_verify_contract_accepts_checkout_stable_lf_hashes() -> None:
    verified, observed = rehearsal.verify_contract()
    assert verified == CONTRACT
    assert observed == {
        binding["path"]: binding["sha256"] for binding in CONTRACT["source_bindings"]
    }
    lf = b'{\n  "result": "pass"\n}\n'
    crlf = lf.replace(b"\n", b"\r\n")
    assert rehearsal._source_text_sha256_bytes(lf) == rehearsal._source_text_sha256_bytes(  # noqa: SLF001
        crlf
    )


def test_source_hash_rejects_bare_carriage_return() -> None:
    with pytest.raises(rehearsal.RehearsalFailure) as excinfo:
        rehearsal._source_text_sha256_bytes(b"left\rright")  # noqa: SLF001
    assert excinfo.value.code == "source_bare_carriage_return"


def test_overflow_fixture_is_transaction_local_and_proves_trigger_restore() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert "SET LOCAL session_replication_role = replica" in source
    assert 'text("SET session_replication_role = replica")' not in source
    assert "SHOW session_replication_role" in source
    assert "AUTH-S08_trigger_restore_unproved" in source
    assert "t.tgenabled = 'O'" in source


def test_all_auth_auxiliary_users_are_disjoint_from_scenario_actors() -> None:
    auth_s01_actor = rehearsal._fixture(1).actor_id  # noqa: SLF001
    auth_s02_actor = rehearsal._fixture(2).actor_id  # noqa: SLF001
    auxiliary = {
        rehearsal._sub_uuid(auth_s02_actor, salt)  # noqa: SLF001
        for salt in rehearsal.AUTH_S02_AUXILIARY_USER_SALTS
    }
    auxiliary.add(
        rehearsal._sub_uuid(  # noqa: SLF001
            auth_s01_actor, rehearsal.AUTH_S01_AUXILIARY_USER_SALT
        )
    )
    scenario_actors = {
        rehearsal._fixture(index).actor_id  # noqa: SLF001
        for index in range(1, 401)
    }
    assert len(auxiliary) == 5
    assert auxiliary.isdisjoint(scenario_actors)


def test_auth_group_runtime_attributes_unexpected_sql_errors() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert "_run_auth_case_attributed(engine, group, index)" in source
    assert "unexpected_sql_error" in source


def test_contract_rejects_added_reordered_or_widened_surfaces() -> None:
    mutations = []
    added = copy.deepcopy(CONTRACT)
    added["caller_database_url"] = "postgresql://product"
    mutations.append(added)
    reordered = copy.deepcopy(CONTRACT)
    reordered["authority_groups"][0], reordered["authority_groups"][1] = (
        reordered["authority_groups"][1],
        reordered["authority_groups"][0],
    )
    mutations.append(reordered)
    widened = copy.deepcopy(CONTRACT)
    widened["transaction_contract"]["concurrency"] = True
    mutations.append(widened)
    for candidate in mutations:
        with pytest.raises(rehearsal.RehearsalFailure):
            rehearsal._validate_contract(candidate, require_digest=False)  # noqa: SLF001


def test_internal_network_container_and_fixed_relay_argv_are_exact() -> None:
    network = status_btr.build_network_argv(
        r"C:\Docker\docker.exe",
        "emr4-delete-confirm-btr-net-0123456789abcdef",
        "0" * 32,
        PROFILE,
    )
    container = status_btr.build_container_argv(
        r"C:\Docker\docker.exe",
        "emr4-delete-confirm-btr-pg16-0123456789abcdef",
        "0" * 32,
        "a" * 64,
        PROFILE,
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
    relay = status_btr.build_relay_argv(r"C:\Docker\docker.exe", "b" * 64, PROFILE)
    assert relay == [
        r"C:\Docker\docker.exe",
        "exec",
        "-i",
        "b" * 64,
        "bash",
        "-c",
        rehearsal.FIXED_RELAY_COMMAND,
    ]
    assert PROFILE["relay_host_ip"] == "127.0.0.1"
    assert PROFILE["relay_dynamic_host_port"] is True
    assert PROFILE["network_internal"] is True
    assert PROFILE["published_ports"] is False


def _owned_network(*, empty: bool = True) -> dict:
    return {
        "Id": "a" * 64,
        "Name": "emr4-delete-confirm-btr-net-0123456789abcdef",
        "Driver": "bridge",
        "Internal": True,
        "Labels": {
            "com.emr4.harness": PROFILE["harness_label"],
            "com.emr4.cleanup-nonce": "0" * 32,
        },
        "Containers": {} if empty else {"b" * 64: {}},
    }


def _owned_container() -> dict:
    return {
        "Id": "b" * 64,
        "Name": "/emr4-delete-confirm-btr-pg16-0123456789abcdef",
        "Image": "sha256:" + "c" * 64,
        "Config": {
            "Image": PROFILE["image_reference"],
            "Labels": {
                "com.emr4.harness": PROFILE["harness_label"],
                "com.emr4.cleanup-nonce": "0" * 32,
            },
            "Env": [
                f"POSTGRES_USER={PROFILE['postgres_user']}",
                f"POSTGRES_PASSWORD={PROFILE['postgres_password']}",
                f"POSTGRES_DB={PROFILE['postgres_database']}",
                f"PGDATA={PROFILE['pgdata']}",
            ],
        },
        "HostConfig": {
            "Binds": None,
            "Privileged": False,
            "Memory": PROFILE["memory_bytes"],
            "NanoCpus": PROFILE["nano_cpus"],
            "PidsLimit": PROFILE["pids_limit"],
            "RestartPolicy": {"Name": "no"},
            "Tmpfs": {PROFILE["data_destination"]: PROFILE["tmpfs_options"]},
            "PortBindings": {},
        },
        "NetworkSettings": {
            "Networks": {"owned": {"NetworkID": "a" * 64}},
            "Ports": {"5432/tcp": None},
        },
        "Mounts": [],
    }


def test_owned_network_and_container_profiles_fail_closed() -> None:
    network_kwargs = {
        "network_id": "a" * 64,
        "name": "emr4-delete-confirm-btr-net-0123456789abcdef",
        "nonce": "0" * 32,
        "profile": PROFILE,
        "require_empty": True,
    }
    assert status_btr._network_owned(_owned_network(), **network_kwargs)  # noqa: SLF001
    assert not status_btr._network_owned(  # noqa: SLF001
        _owned_network(empty=False), **network_kwargs
    )
    container_kwargs = {
        "container_id": "b" * 64,
        "name": "emr4-delete-confirm-btr-pg16-0123456789abcdef",
        "nonce": "0" * 32,
        "image_id": "sha256:" + "c" * 64,
        "network_id": "a" * 64,
        "profile": PROFILE,
    }
    assert status_btr._container_profile(  # noqa: SLF001
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
        assert status_btr._container_profile(  # noqa: SLF001
            item, **container_kwargs
        ) is False


@pytest.mark.parametrize(
    ("statement", "expected"),
    [
        ("SELECT * FROM users FOR SHARE", "user_for_share"),
        ("SELECT * FROM appointments FOR UPDATE", "appointment_for_update"),
        (
            "SELECT EXISTS (SELECT 1 FROM user_capability_grants WHERE practice_id = 'x')",
            "grant_authority_check",
        ),
        (
            "SELECT * FROM appointment_command_idempotency FOR UPDATE",
            "idempotency_for_update",
        ),
        (
            "INSERT INTO appointment_command_idempotency VALUES (1) ON CONFLICT DO NOTHING",
            "idempotency_insert_on_conflict",
        ),
        ("SELECT * FROM practices", None),
        ("UPDATE users SET authority_generation = 1", None),
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

    monkeypatch.setattr(status_btr.catalogue, "_run", runner)
    result = status_btr._cleanup(  # noqa: SLF001
        r"C:\Docker\docker.exe",
        container_id="b" * 64,
        container_name="emr4-delete-confirm-btr-pg16-0123456789abcdef",
        network_id="a" * 64,
        network_name="emr4-delete-confirm-btr-net-0123456789abcdef",
        nonce="0" * 32,
        image_id="sha256:" + "c" * 64,
        profile=PROFILE,
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


def test_timeout_case_replaces_and_restores_imported_monotonic() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert "physical.time.monotonic = fake_monotonic" in source
    assert "physical.time.monotonic = original_monotonic" in source
    tree = ast.parse(source)
    found_finally_restore = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and node.finalbody:
            final_source = ast.get_source_segment(source, node.finalbody[0])
            if final_source and "physical.time.monotonic = original_monotonic" in final_source:
                found_finally_restore = True
    assert found_finally_restore


def test_second_check_revocation_hook_is_fixed_and_not_a_caller_surface() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert "def revoke_hook" in source
    assert "idempotency_winner_for_update" in source
    signature = source.split("def _invoke_tx(")[1].split("):")[0]
    assert "current_authority" not in signature
    assert "sql_callback" not in signature
    assert "practice_is_active" not in signature


def test_pass_evidence_when_present_is_complete_and_minimized() -> None:
    if not rehearsal.EVIDENCE_PATH.exists():
        pytest.skip("occupied evidence not generated yet")
    evidence = rehearsal._load_json(rehearsal.EVIDENCE_PATH)  # noqa: SLF001
    Draft202012Validator.check_schema(EVIDENCE_SCHEMA)
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["hostile_mutations_rejected"] == rehearsal.HOSTILE_MUTATION_TARGET
    assert len(evidence["authority_groups"]) == 9
    assert len(evidence["transaction_groups"]) == 11
    assert all(item["status"] == "passed" for item in evidence["authority_groups"])
    assert all(item["status"] == "passed" for item in evidence["transaction_groups"])
    assert evidence["cleanup"]["status"] == "cleanup_verified"
    serialized = json.dumps(evidence).lower()
    for forbidden in (
        PROFILE["postgres_password"],
        "postgresql+psycopg://",
        "response_body_canonical_bytes",
        "session_binding_digest",
        "raw_sql",
        "synthetic-user-",
        "synthetic-session-",
    ):
        assert forbidden not in serialized
