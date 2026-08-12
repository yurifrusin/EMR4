from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_scaffold_parse_catalogue_rehearsal
    as rehearsal,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = rehearsal._load_contract()  # noqa: SLF001
SCHEMA = json.loads(rehearsal.SCHEMA_PATH.read_text(encoding="utf-8"))
EVIDENCE_SCHEMA = json.loads(
    (
        rehearsal.BASE / "provider-free-disposable-postgresql-evidence.schema.json"
    ).read_text(encoding="utf-8")
)


def test_contract_schema_hashes_and_hostile_mutations_pass() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    Draft202012Validator(SCHEMA).validate(CONTRACT)
    observed_contract, hashes = rehearsal.verify_contract()
    assert observed_contract == CONTRACT
    assert len(hashes) == 8
    assert rehearsal.hostile_mutations_rejected(CONTRACT) == 80


def test_offline_alembic_range_is_exact_and_database_free() -> None:
    body = rehearsal._generate_offline_sql(CONTRACT)  # noqa: SLF001
    assert body.startswith(b"-- Running upgrade v1w2x3y4z5b6 -> w2x3y4z5a6b7")
    assert b"BEGIN;" not in body
    assert b"COMMIT;" not in body
    assert b"appointment_state_version BIGINT" in body
    assert b"trg_appointments_advance_state_version" in body
    assert b"completed_receipt_version SMALLINT" in body
    assert b"version_num='w2x3y4z5a6b7'" in body


def test_container_argv_is_networkless_tmpfs_bounded_and_no_pull() -> None:
    argv = rehearsal.build_container_argv(
        r"C:\Docker\docker.exe",
        "emr4-status-confirm-pg16-catalogue-0123456789abcdef",
        "0" * 32,
        CONTRACT,
    )
    joined = " ".join(argv)
    assert argv[:3] == [r"C:\Docker\docker.exe", "run", "--detach"]
    assert "--pull never" in joined
    assert "--network none" in joined
    assert "--tmpfs /var/lib/postgresql/data:" in joined
    assert "--memory 512m" in joined
    assert "--cpus 1" in joined
    assert "--pids-limit 128" in joined
    assert argv[-1] == "postgres:16-bookworm"
    for forbidden in ("--publish", "-p", "--volume", "-v", "--mount", "trust"):
        assert forbidden not in argv


def _owned_inspect() -> dict:
    profile = CONTRACT["docker_profile"]
    return {
        "Id": "a" * 64,
        "Name": "/emr4-status-confirm-pg16-catalogue-0123456789abcdef",
        "Image": "sha256:" + "b" * 64,
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
                "PATH=/usr/local/bin",
            ],
        },
        "HostConfig": {
            "NetworkMode": "none",
            "Binds": None,
            "PortBindings": {},
            "Privileged": False,
            "Memory": profile["memory_bytes"],
            "NanoCpus": profile["nano_cpus"],
            "PidsLimit": profile["pids_limit"],
            "RestartPolicy": {"Name": "no"},
            "Tmpfs": {
                profile["data_destination"]: profile["tmpfs_options"]
            },
        },
        "Mounts": [],
    }


def test_cleanup_ownership_is_position_closed() -> None:
    kwargs = {
        "container_id": "a" * 64,
        "name": "emr4-status-confirm-pg16-catalogue-0123456789abcdef",
        "nonce": "0" * 32,
        "image_id": "sha256:" + "b" * 64,
        "profile": CONTRACT["docker_profile"],
    }
    assert rehearsal._container_owned(_owned_inspect(), **kwargs)  # noqa: SLF001
    mutations = (
        ("Id", "c" * 64),
        ("Name", "/other"),
        ("Image", "sha256:" + "c" * 64),
    )
    for key, value in mutations:
        payload = _owned_inspect()
        payload[key] = value
        assert not rehearsal._container_owned(payload, **kwargs)  # noqa: SLF001
    for mutate in ("network", "bind", "port", "memory", "cpu", "pids", "tmpfs"):
        payload = _owned_inspect()
        if mutate == "network":
            payload["HostConfig"]["NetworkMode"] = "bridge"
        elif mutate == "bind":
            payload["HostConfig"]["Binds"] = ["C:\\workspace:/workspace"]
        elif mutate == "port":
            payload["HostConfig"]["PortBindings"] = {"5432/tcp": [{}]}
        elif mutate == "memory":
            payload["HostConfig"]["Memory"] = 0
        elif mutate == "cpu":
            payload["HostConfig"]["NanoCpus"] = 0
        elif mutate == "pids":
            payload["HostConfig"]["PidsLimit"] = 0
        else:
            payload["HostConfig"]["Tmpfs"] = {}
        assert not rehearsal._container_owned(payload, **kwargs)  # noqa: SLF001


def _valid_catalogue() -> dict:
    return {
        "head": "w2x3y4z5a6b7",
        "columns": [
            {
                "table_name": item["table"],
                "ordinal": index + 1,
                "name": item["name"],
                "type": item["type"],
                "nullable": item["nullable"],
                "default": item["default"],
            }
            for index, item in enumerate(CONTRACT["catalogue"]["columns"])
        ],
        "constraints": [
            {
                "name": "ck_appointments_state_version_positive",
                "definition": "CHECK (appointment_state_version >= 1)",
            },
            {
                "name": "ck_appt_cmd_idem_receipt_version",
                "definition": (
                    "CHECK (completed_receipt_version IS NULL OR "
                    "completed_receipt_version = 1)"
                ),
            },
            {
                "name": "ck_appt_cmd_idem_status_receipt_v1_complete",
                "definition": (
                    "CHECK (confirmAppointmentStatusProposal status-confirm "
                    "octet_length(session_binding_digest) = 32 "
                    "post_state_version = pre_state_version + 1 "
                    "octet_length(response_body_canonical_bytes) > 0)"
                ),
            },
        ],
        "function": {
            "schema": "public",
            "name": "emr4_advance_appointment_state_version",
            "arguments": "",
            "result": "trigger",
            "language": "plpgsql",
            "security_definer": False,
            "volatility": "v",
            "definition": (
                "OLD.appointment_state_version >= 9223372036854775807 "
                "NEW.appointment_state_version := OLD.appointment_state_version + 1 "
                "ERRCODE = '22003'"
            ),
        },
        "trigger": {
            "name": "trg_appointments_advance_state_version",
            "enabled": "O",
            "internal": False,
            "definition": (
                "CREATE TRIGGER trg_appointments_advance_state_version BEFORE UPDATE "
                "ON appointments FOR EACH ROW EXECUTE FUNCTION "
                "emr4_advance_appointment_state_version()"
            ),
        },
        "cutover_version": 1,
        "unexpected_function_count": 0,
        "unexpected_trigger_count": 0,
    }


def test_catalogue_assertion_accepts_exact_and_rejects_mutations() -> None:
    rehearsal._assert_catalogue(_valid_catalogue(), CONTRACT)  # noqa: SLF001
    for mutate in ("head", "column", "constraint", "function", "trigger", "cutover"):
        facts = _valid_catalogue()
        if mutate == "head":
            facts["head"] = "other"
        elif mutate == "column":
            facts["columns"][0]["type"] = "int4"
        elif mutate == "constraint":
            facts["constraints"][0]["definition"] = "CHECK (true)"
        elif mutate == "function":
            facts["function"]["security_definer"] = True
        elif mutate == "trigger":
            facts["trigger"]["enabled"] = "D"
        else:
            facts["cutover_version"] = 2
        with pytest.raises(rehearsal.RehearsalFailure):
            rehearsal._assert_catalogue(facts, CONTRACT)  # noqa: SLF001


def test_catalogue_assertion_accepts_postgresql_presentation_parentheses() -> None:
    facts = _valid_catalogue()
    facts["constraints"][2]["definition"] = (
        "CHECK (((completed_receipt_version IS NULL) OR "
        "((operation_id)::text = 'confirmAppointmentStatusProposal'::text AND "
        "(route_family)::text = 'status-confirm'::text AND "
        "(octet_length(session_binding_digest) = 32) AND "
        "(post_state_version = (pre_state_version + 1)) AND "
        "(octet_length(response_body_canonical_bytes) > 0))))"
    )
    facts["trigger"]["definition"] = (
        "CREATE TRIGGER trg_appointments_advance_state_version BEFORE UPDATE ON "
        "public.appointments FOR EACH ROW EXECUTE FUNCTION "
        "public.emr4_advance_appointment_state_version()"
    )
    rehearsal._assert_catalogue(facts, CONTRACT)  # noqa: SLF001


def test_psql_transport_has_no_host_port_or_caller_database_url() -> None:
    argv = rehearsal._psql_argv(  # noqa: SLF001
        r"C:\Docker\docker.exe",
        "a" * 64,
        CONTRACT["docker_profile"],
        single_transaction=True,
        tuples_only=True,
    )
    joined = " ".join(argv)
    assert "docker.exe exec -i" in joined
    assert "--host /var/run/postgresql" in joined
    assert "--single-transaction" in argv
    assert "--file=-" in argv
    assert "localhost" not in joined
    assert "--port" not in argv


def test_sqlstate_accepts_exactly_one_code_across_docker_streams() -> None:
    assert rehearsal._sqlstate(  # noqa: SLF001
        rehearsal.ProcessResult(1, b"ERROR: 23514\n", b"")
    ) == "23514"
    assert rehearsal._sqlstate(  # noqa: SLF001
        rehearsal.ProcessResult(1, b"", b"ERROR: 22003\n")
    ) == "22003"
    with pytest.raises(rehearsal.RehearsalFailure):
        rehearsal._sqlstate(  # noqa: SLF001
            rehearsal.ProcessResult(1, b"ERROR: 23514\n", b"ERROR: 22003\n")
        )


def test_environment_stop_never_calls_docker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rehearsal, "_generate_offline_sql", lambda _contract: b"ddl")
    monkeypatch.setattr(rehearsal.shutil, "which", lambda _name: None)

    def forbidden_runner(*_args, **_kwargs):
        raise AssertionError("runner must not be called")

    evidence = rehearsal.run_rehearsal(runner=forbidden_runner)
    assert evidence["result"] == "rehearsal_failed"
    assert evidence["failure"]["code"] == "docker_client_missing"
    assert evidence["cleanup"]["status"] == "not_needed"
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)


def test_occupied_rehearsal_evidence_is_complete_and_minimized() -> None:
    evidence = json.loads(rehearsal.EVIDENCE_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(EVIDENCE_SCHEMA)
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["hostile_mutations_rejected"] == 80
    assert evidence["environment"] == {
        "postgresql_major": 16,
        "image_reference": "postgres:16-bookworm",
        "image_id_sha256": evidence["environment"]["image_id_sha256"],
        "network_mode": "none",
        "storage": "container_local_tmpfs",
    }
    assert len(evidence["environment"]["image_id_sha256"]) == 64
    assert evidence["catalogue"]["status"] == "exact_match"
    assert evidence["catalogue"]["columns"] == 6
    assert evidence["catalogue"]["constraints"] == 3
    assert [item["id"] for item in evidence["probes"]] == [
        item["id"] for item in CONTRACT["probes"]
    ]
    assert all(item["status"] == "passed" for item in evidence["probes"])
    assert evidence["cleanup"]["status"] == "cleanup_verified"
    serialized = json.dumps(evidence).lower()
    for forbidden in (
        "container_id\"",
        CONTRACT["docker_profile"]["postgres_password"],
        "database_url",
        "patient_name",
        "credential",
    ):
        assert forbidden not in serialized


def test_exact_owned_cleanup_uses_only_captured_id() -> None:
    calls: list[list[str]] = []
    responses = [
        rehearsal.ProcessResult(0, json.dumps([_owned_inspect()]).encode(), b""),
        rehearsal.ProcessResult(0, b"a" * 64 + b"\n", b""),
        rehearsal.ProcessResult(1, b"", b"Error: No such object: " + b"a" * 64),
    ]

    def runner(argv, stdin, timeout, cap):
        del stdin, timeout, cap
        calls.append(argv)
        return responses.pop(0)

    result = rehearsal._cleanup(  # noqa: SLF001
        runner,
        r"C:\Docker\docker.exe",
        "a" * 64,
        "emr4-status-confirm-pg16-catalogue-0123456789abcdef",
        "0" * 32,
        "sha256:" + "b" * 64,
        CONTRACT["docker_profile"],
    )
    assert result["status"] == "cleanup_verified"
    assert calls[1] == [
        r"C:\Docker\docker.exe",
        "container",
        "rm",
        "--force",
        "a" * 64,
    ]


def test_harness_has_no_shell_or_broad_docker_discovery() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "run":
                keywords = {item.arg: item.value for item in node.keywords}
                assert isinstance(keywords.get("shell"), ast.Constant)
                assert keywords["shell"].value is False
    for forbidden in (
        '"container", "ls"',
        '"image", "ls"',
        '"volume", "ls"',
        '"network", "ls"',
        '"prune"',
        '"pull"',
        '"build"',
        '"login"',
    ):
        assert forbidden not in source


def test_main_rejects_caller_selected_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rehearsal.sys, "argv", ["harness", "--image", "other"])
    assert rehearsal.main() == 2
