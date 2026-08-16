from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from scripts import (
    raisa_provider_free_disposable_postgresql_delete_confirm_scaffold_parse_catalogue_rehearsal
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
    assert len(hashes) == 11
    assert rehearsal.hostile_mutations_rejected(CONTRACT) == 80


def test_contract_binds_plan_threat_and_all_plan_sources() -> None:
    bound = {item["path"]: item["sha256"] for item in CONTRACT["source_bindings"]}
    assert (
        bound["docs/raisa-provider-free-disposable-postgresql-delete-confirm-scaffold-parse-catalogue-rehearsal-plan.md"]
        == "71486b39e69bdab10e23b22bafa9d48a348c816b0270ad4e11c38700dcd06b62"
    )
    assert (
        bound["docs/security/raisa-provider-free-disposable-postgresql-delete-confirm-scaffold-parse-catalogue-rehearsal-threat-model-delta.md"]
        == "653658d228eecdd48389d7158cfa5b211f062a35ab9af0ba85a9db4a91a68edd"
    )
    assert bound["alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py"] == (
        "e6542c960a9378cf7c1c3c22dd876a1c9f242b68047a180f9f383c1c62d348bb"
    )
    assert CONTRACT["source_head"] == "38f2fbb054736cbd63627daea6951d676907461c"


def test_offline_alembic_range_is_exact_and_database_free() -> None:
    assert CONTRACT["alembic"]["synthetic_url"].endswith(
        "@127.0.0.1:1/synthetic"
    )
    body = rehearsal._generate_offline_sql(CONTRACT)  # noqa: SLF001
    assert body.startswith(b"-- Running upgrade w2x3y4z5a6b7 -> x3y4z5a6b7c8")
    assert b"BEGIN;" not in body
    assert b"COMMIT;" not in body
    assert b"ALTER TABLE users ADD COLUMN authority_generation BIGINT" in body
    assert b"CREATE TABLE user_capability_grants" in body
    assert b"CREATE FUNCTION public.emr4_user_authority_generation_guard()" in body
    assert b"CREATE TRIGGER trg_users_authority_generation_guard" in body
    assert b"CREATE TRIGGER trg_user_capability_grants_generation" in body
    assert b"CREATE TRIGGER trg_user_capability_grants_reject_update" in body
    assert b"confirmAppointmentDeleteProposal" in body
    assert b"ck_appt_audit_log_delete_v1_complete" in body
    assert b"version_num='x3y4z5a6b7c8'" in body
    assert b"DROP TABLE" not in body
    assert b"CREATE DATABASE" not in body


def test_container_argv_is_networkless_tmpfs_bounded_and_no_pull() -> None:
    assert CONTRACT["docker_profile"]["context"] == "default"
    argv = rehearsal.build_container_argv(
        r"C:\Docker\docker.exe",
        "emr4-delete-confirm-pg16-catalogue-0123456789abcdef",
        "0" * 32,
        CONTRACT,
    )
    joined = " ".join(argv)
    assert argv[:5] == [
        r"C:\Docker\docker.exe",
        "--context",
        "default",
        "run",
        "--detach",
    ]
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
        "Name": "/emr4-delete-confirm-pg16-catalogue-0123456789abcdef",
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
        "name": "emr4-delete-confirm-pg16-catalogue-0123456789abcdef",
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
        "emr4-delete-confirm-pg16-catalogue-0123456789abcdef",
        "0" * 32,
        "sha256:" + "b" * 64,
        CONTRACT["docker_profile"],
    )
    assert result["status"] == "cleanup_verified"
    assert calls[1] == [
        r"C:\Docker\docker.exe",
        "--context",
        "default",
        "container",
        "rm",
        "--force",
        "a" * 64,
    ]


def test_cleanup_refuses_removal_when_ownership_unverified() -> None:
    calls: list[list[str]] = []

    def runner(argv, stdin, timeout, cap):
        del stdin, timeout, cap
        calls.append(argv)
        return rehearsal.ProcessResult(1, b"", b"Error: No such object: " + b"a" * 64)

    result = rehearsal._cleanup(  # noqa: SLF001
        runner,
        r"C:\Docker\docker.exe",
        "a" * 64,
        "emr4-delete-confirm-pg16-catalogue-0123456789abcdef",
        "0" * 32,
        "sha256:" + "b" * 64,
        CONTRACT["docker_profile"],
    )
    assert result["status"] == "cleanup_ownership_unverified"
    assert all("rm" not in call for call in calls)


def _idempotency_constraint_definition() -> str:
    return (
        "CHECK (completed_receipt_version IS NULL OR "
        "(state = 'completed' AND "
        "operation_id = 'confirmAppointmentStatusProposal' AND "
        "route_family = 'status-confirm' AND "
        "result_kind = 'confirmed_write' AND "
        "session_binding_digest IS NOT NULL AND "
        "octet_length(session_binding_digest) = 32 AND "
        "pre_state_version IS NOT NULL AND pre_state_version >= 1 AND "
        "post_state_version IS NOT NULL AND "
        "post_state_version = pre_state_version + 1 AND "
        "response_body_canonical_bytes IS NOT NULL AND "
        "octet_length(response_body_canonical_bytes) > 0 AND "
        "target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL AND "
        "response_status_code IS NOT NULL AND response_body_hash IS NOT NULL AND "
        "response_body_json IS NOT NULL) OR "
        "(state = 'completed' AND "
        "operation_id = 'confirmAppointmentDeleteProposal' AND "
        "route_family = 'delete-confirm' AND "
        "result_kind = 'confirmed_write' AND "
        "authority_generation IS NOT NULL AND authority_generation >= 1 AND "
        "session_binding_digest IS NOT NULL AND "
        "octet_length(session_binding_digest) = 32 AND "
        "pre_state_version IS NOT NULL AND pre_state_version >= 1 AND "
        "post_state_version IS NOT NULL AND "
        "post_state_version = pre_state_version + 1 AND "
        "response_body_canonical_bytes IS NOT NULL AND "
        "octet_length(response_body_canonical_bytes) > 0 AND "
        "target_appointment_id IS NOT NULL AND audit_log_id IS NOT NULL AND "
        "response_status_code IS NOT NULL AND response_body_hash IS NOT NULL AND "
        "response_body_json IS NOT NULL))"
    )


def _audit_constraint_definition() -> str:
    return (
        "CHECK (audit_contract_version IS NULL OR "
        "(audit_contract_version = 1 AND action = 'delete' AND "
        "command_id IS NOT NULL AND "
        "authority_generation IS NOT NULL AND authority_generation >= 1 AND "
        "pre_state_version IS NOT NULL AND pre_state_version >= 1 AND "
        "post_state_version IS NOT NULL AND post_state_version >= 1 AND "
        "post_state_version = pre_state_version + 1 AND "
        "status_after = 'Cancelled' AND status_reason_code IS NOT NULL AND "
        "waiting_area_after_id IS NULL AND "
        "confirmed_warnings IS NOT NULL AND "
        "jsonb_typeof(confirmed_warnings) = 'array' AND "
        "audit_evidence_codes IS NOT NULL AND "
        "jsonb_typeof(audit_evidence_codes) = 'array'))"
    )


def _valid_catalogue() -> dict:
    return {
        "head": "x3y4z5a6b7c8",
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
                "table_name": "users",
                "name": "ck_users_authority_generation_positive",
                "definition": "CHECK (authority_generation >= 1)",
            },
            {
                "table_name": "users",
                "name": "uq_users_practice_id_id",
                "definition": "UNIQUE (practice_id, id)",
            },
            {
                "table_name": "user_capability_grants",
                "name": "pk_user_capability_grants",
                "definition": "PRIMARY KEY (practice_id, user_id, capability_code)",
            },
            {
                "table_name": "user_capability_grants",
                "name": "fk_user_capability_grants_user",
                "definition": (
                    "FOREIGN KEY (practice_id, user_id) "
                    "REFERENCES users(practice_id, id)"
                ),
            },
            {
                "table_name": "user_capability_grants",
                "name": "ck_user_capability_grants_capability_code",
                "definition": (
                    "CHECK (capability_code IN "
                    "('appointment.cancel.confirm', 'appointment.read'))"
                ),
            },
            {
                "table_name": "appointment_command_idempotency",
                "name": "ck_appt_cmd_idem_status_receipt_v1_complete",
                "definition": _idempotency_constraint_definition(),
            },
            {
                "table_name": "appointment_audit_log",
                "name": "ck_appt_audit_log_delete_v1_complete",
                "definition": _audit_constraint_definition(),
            },
        ],
        "index": [
            {
                "name": "ix_user_capability_grants_user",
                "definition": (
                    "CREATE INDEX ix_user_capability_grants_user "
                    "ON public.user_capability_grants USING btree "
                    "(practice_id, user_id)"
                ),
            }
        ],
        "functions": [
            {
                "schema": "public",
                "name": "emr4_user_authority_generation_guard",
                "arguments": "",
                "result": "trigger",
                "language": "plpgsql",
                "security_definer": False,
                "volatility": "v",
                "definition": (
                    " ".join(CONTRACT["catalogue"]["functions"][0]["tokens"])
                ),
            },
            {
                "schema": "public",
                "name": "emr4_user_capability_grant_generation_guard",
                "arguments": "",
                "result": "trigger",
                "language": "plpgsql",
                "security_definer": False,
                "volatility": "v",
                "definition": (
                    " ".join(CONTRACT["catalogue"]["functions"][1]["tokens"])
                ),
            },
            {
                "schema": "public",
                "name": "emr4_reject_user_capability_grant_update",
                "arguments": "",
                "result": "trigger",
                "language": "plpgsql",
                "security_definer": False,
                "volatility": "v",
                "definition": " ".join(
                    CONTRACT["catalogue"]["functions"][2]["tokens"]
                ),
            },
        ],
        "triggers": [
            {
                "name": "trg_users_authority_generation_guard",
                "enabled": "O",
                "internal": False,
                "table_name": "users",
                "definition": (
                    "CREATE TRIGGER trg_users_authority_generation_guard "
                    "BEFORE INSERT OR UPDATE ON public.users FOR EACH ROW "
                    "EXECUTE FUNCTION public.emr4_user_authority_generation_guard()"
                ),
            },
            {
                "name": "trg_user_capability_grants_generation",
                "enabled": "O",
                "internal": False,
                "table_name": "user_capability_grants",
                "definition": (
                    "CREATE TRIGGER trg_user_capability_grants_generation "
                    "BEFORE INSERT OR DELETE ON public.user_capability_grants "
                    "FOR EACH ROW "
                    "EXECUTE FUNCTION public.emr4_user_capability_grant_generation_guard()"
                ),
            },
            {
                "name": "trg_user_capability_grants_reject_update",
                "enabled": "O",
                "internal": False,
                "table_name": "user_capability_grants",
                "definition": (
                    "CREATE TRIGGER trg_user_capability_grants_reject_update "
                    "BEFORE UPDATE ON public.user_capability_grants FOR EACH ROW "
                    "EXECUTE FUNCTION public.emr4_reject_user_capability_grant_update()"
                ),
            },
        ],
        "unexpected_function_count": 0,
        "unexpected_trigger_count": 0,
        "zero_rows": {
            "users": 0,
            "user_capability_grants": 0,
            "appointment_command_idempotency": 0,
            "appointment_audit_log": 0,
        },
    }


def test_catalogue_assertion_accepts_exact_and_rejects_mutations() -> None:
    rehearsal._assert_catalogue(_valid_catalogue(), CONTRACT)  # noqa: SLF001
    for mutate in (
        "head",
        "column",
        "constraint",
        "constraint_table",
        "index",
        "function",
        "trigger",
        "unexpected_function",
        "zero_rows",
    ):
        facts = _valid_catalogue()
        if mutate == "head":
            facts["head"] = "other"
        elif mutate == "column":
            facts["columns"][0]["type"] = "int4"
        elif mutate == "constraint":
            facts["constraints"][0]["definition"] = "CHECK (true)"
        elif mutate == "constraint_table":
            facts["constraints"][0]["table_name"] = "appointment_audit_log"
        elif mutate == "index":
            facts["index"][0]["definition"] = "CREATE INDEX other"
        elif mutate == "function":
            facts["functions"][0]["security_definer"] = True
        elif mutate == "trigger":
            facts["triggers"][0]["enabled"] = "D"
        elif mutate == "unexpected_function":
            facts["unexpected_function_count"] = 1
        else:
            facts["zero_rows"]["users"] = 1
        with pytest.raises(rehearsal.RehearsalFailure):
            rehearsal._assert_catalogue(facts, CONTRACT)  # noqa: SLF001


def test_catalogue_assertion_accepts_postgresql_presentation_parentheses() -> None:
    facts = _valid_catalogue()
    facts["constraints"][5]["definition"] = (
        "CHECK (((completed_receipt_version IS NULL) OR "
        "((state)::text = 'completed'::text AND "
        "(operation_id)::text = 'confirmAppointmentStatusProposal'::text AND "
        "(route_family)::text = 'status-confirm'::text AND "
        "(result_kind)::text = 'confirmed_write'::text AND "
        "(session_binding_digest IS NOT NULL) AND "
        "(octet_length(session_binding_digest) = 32) AND "
        "(pre_state_version IS NOT NULL) AND (pre_state_version >= 1) AND "
        "(post_state_version IS NOT NULL) AND "
        "(post_state_version = (pre_state_version + 1)) AND "
        "(response_body_canonical_bytes IS NOT NULL) AND "
        "(octet_length(response_body_canonical_bytes) > 0) AND "
        "(target_appointment_id IS NOT NULL) AND (audit_log_id IS NOT NULL) AND "
        "(response_status_code IS NOT NULL) AND "
        "(response_body_hash IS NOT NULL) AND (response_body_json IS NOT NULL)) OR "
        "((state)::text = 'completed'::text AND "
        "(operation_id)::text = 'confirmAppointmentDeleteProposal'::text AND "
        "(route_family)::text = 'delete-confirm'::text AND "
        "(result_kind)::text = 'confirmed_write'::text AND "
        "(authority_generation IS NOT NULL) AND (authority_generation >= 1) AND "
        "(session_binding_digest IS NOT NULL) AND "
        "(octet_length(session_binding_digest) = 32) AND "
        "(pre_state_version IS NOT NULL) AND (pre_state_version >= 1) AND "
        "(post_state_version IS NOT NULL) AND "
        "(post_state_version = (pre_state_version + 1)) AND "
        "(response_body_canonical_bytes IS NOT NULL) AND "
        "(octet_length(response_body_canonical_bytes) > 0) AND "
        "(target_appointment_id IS NOT NULL) AND (audit_log_id IS NOT NULL) AND "
        "(response_status_code IS NOT NULL) AND "
        "(response_body_hash IS NOT NULL) AND (response_body_json IS NOT NULL)))"
    )
    facts["constraints"][6]["definition"] = (
        "CHECK (((audit_contract_version IS NULL) OR "
        "((audit_contract_version = 1) AND ((action)::text = 'delete'::text) AND "
        "(command_id IS NOT NULL) AND "
        "(authority_generation IS NOT NULL) AND (authority_generation >= 1) AND "
        "(pre_state_version IS NOT NULL) AND (pre_state_version >= 1) AND "
        "(post_state_version IS NOT NULL) AND (post_state_version >= 1) AND "
        "(post_state_version = (pre_state_version + 1)) AND "
        "((status_after)::text = 'Cancelled'::text) AND "
        "(status_reason_code IS NOT NULL) AND "
        "(waiting_area_after_id IS NULL) AND "
        "(confirmed_warnings IS NOT NULL) AND "
        "(jsonb_typeof(confirmed_warnings) = 'array'::text) AND "
        "(audit_evidence_codes IS NOT NULL) AND "
        "(jsonb_typeof(audit_evidence_codes) = 'array'::text)))"
    )
    facts["triggers"][0]["definition"] = (
        "CREATE TRIGGER trg_users_authority_generation_guard BEFORE INSERT OR "
        "UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION "
        "public.emr4_user_authority_generation_guard()"
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
    assert "docker.exe --context default exec -i" in joined
    assert "--host /var/run/postgresql" in joined
    assert "--single-transaction" in argv
    assert "--file=-" in argv
    assert "localhost" not in joined
    assert "--port" not in argv


def test_environment_stop_never_calls_docker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        rehearsal,
        "_generate_offline_sql",
        lambda _contract, *, deadline: b"ddl",
    )
    monkeypatch.setattr(rehearsal.shutil, "which", lambda _name: None)

    def forbidden_runner(*_args, **_kwargs):
        raise AssertionError("runner must not be called")

    evidence = rehearsal.run_rehearsal(runner=forbidden_runner)
    assert evidence["result"] == "rehearsal_failed"
    assert evidence["failure"]["code"] == "docker_client_missing"
    assert evidence["cleanup"]["status"] == "not_needed"
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)


def test_active_lifecycle_uses_one_total_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, float] = {}
    monkeypatch.setattr(rehearsal.time, "monotonic", lambda: 100.0)

    def offline(_contract, *, deadline):
        captured["deadline"] = deadline
        return b"ddl"

    monkeypatch.setattr(rehearsal, "_generate_offline_sql", offline)
    monkeypatch.setattr(rehearsal.shutil, "which", lambda _name: None)
    evidence = rehearsal.run_rehearsal()
    assert captured["deadline"] == 250.0
    assert evidence["failure"]["code"] == "docker_client_missing"
    assert rehearsal._remaining_timeout(130.0, 60) == 30  # noqa: SLF001
    with pytest.raises(rehearsal.RehearsalFailure, match="total_timeout_exceeded"):
        rehearsal._remaining_timeout(100.0, 1)  # noqa: SLF001


def test_subprocess_timeout_is_bounded_and_docker_environment_is_sanitized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for key in rehearsal.DOCKER_ENV_KEYS:
        monkeypatch.setenv(key, "hostile")

    def timed_out(*_args, env, timeout, **_kwargs):
        assert all(key not in env for key in rehearsal.DOCKER_ENV_KEYS)
        raise rehearsal.subprocess.TimeoutExpired(
            cmd=["docker"], timeout=timeout, output=b"bounded", stderr=b"timeout"
        )

    monkeypatch.setattr(rehearsal.subprocess, "run", timed_out)
    result = rehearsal._run(["docker"], None, 1, 64)  # noqa: SLF001
    assert result.returncode == 124
    assert result.stdout == b"bounded"
    assert b"process_timeout" in result.stderr


def test_evidence_schema_validates_pass_and_failure_shapes() -> None:
    Draft202012Validator.check_schema(EVIDENCE_SCHEMA)
    pass_evidence = {
        "schema_version": rehearsal.EVIDENCE_SCHEMA_VERSION,
        "result": rehearsal.PASS_RESULT,
        "evidence_label": CONTRACT["evidence_label"],
        "source_head": CONTRACT["source_head"],
        "contract_sha256": "c" * 64,
        "source_hashes": {item["path"]: item["sha256"] for item in CONTRACT["source_bindings"]},
        "hostile_mutations_rejected": 80,
        "environment": {
            "postgresql_major": 16,
            "image_reference": "postgres:16-bookworm",
            "image_id_sha256": "d" * 64,
            "network_mode": "none",
            "storage": "container_local_tmpfs",
        },
        "offline_sql": {
            "range": CONTRACT["alembic"]["offline_range"],
            "body_sha256": "e" * 64,
            "body_bytes": 10802,
        },
        "catalogue": {
            "status": "exact_match",
            "facts_sha256": "f" * 64,
            "columns": 12,
            "constraints": 7,
            "functions": [
                "emr4_user_authority_generation_guard",
                "emr4_user_capability_grant_generation_guard",
                "emr4_reject_user_capability_grant_update",
            ],
            "triggers": [
                "trg_users_authority_generation_guard",
                "trg_user_capability_grants_generation",
                "trg_user_capability_grants_reject_update",
            ],
            "head": "x3y4z5a6b7c8",
            "zero_rows": {
                "users": 0,
                "user_capability_grants": 0,
                "appointment_command_idempotency": 0,
                "appointment_audit_log": 0,
            },
        },
        "lifecycle": ["catalogue_verified", "cleanup_verified"],
        "cleanup": {"status": "cleanup_verified", "container_id_sha256": "a" * 64},
        "claim_boundary": rehearsal.CLAIM_BOUNDARY,
    }
    Draft202012Validator(EVIDENCE_SCHEMA).validate(pass_evidence)
    invalid_pass = json.loads(json.dumps(pass_evidence))
    del invalid_pass["cleanup"]["container_id_sha256"]
    with pytest.raises(ValidationError):
        Draft202012Validator(EVIDENCE_SCHEMA).validate(invalid_pass)
    invalid_pass["cleanup"]["container_id"] = "0" * 64
    with pytest.raises(ValidationError):
        Draft202012Validator(EVIDENCE_SCHEMA).validate(invalid_pass)

    failure_evidence = {
        "schema_version": rehearsal.EVIDENCE_SCHEMA_VERSION,
        "result": "rehearsal_failed",
        "evidence_label": CONTRACT["evidence_label"],
        "source_head": CONTRACT["source_head"],
        "lifecycle": ["container_created"],
        "failure": {"stage": "probe", "code": "blocked", "detail_sha256": "b" * 64},
        "cleanup": {"status": "cleanup_ownership_unverified", "container_id": "0" * 64},
        "claim_boundary": rehearsal.CLAIM_BOUNDARY,
    }
    Draft202012Validator(EVIDENCE_SCHEMA).validate(failure_evidence)


def test_no_occupied_evidence_artifact_is_created() -> None:
    assert not rehearsal.EVIDENCE_PATH.exists()
    assert not rehearsal.FAILURE_EVIDENCE_PATH.exists()


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


def test_no_behavior_probe_sql_or_product_row_insert() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "_run_probes",
        "_receipt_values",
        "_sqlstate",
        "ROLLBACK",
        "INSERT INTO public.users",
        "INSERT INTO public.user_capability_grants",
        "INSERT INTO public.appointment_command_idempotency",
        "INSERT INTO public.appointment_audit_log",
        "INSERT INTO appointments",
    ):
        assert forbidden not in source


def test_no_forbidden_source_edit_or_caller_override_paths() -> None:
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "sys.argv[1]",
        "os.environ['DATABASE_URL']",
        "input(",
        "getenv",
    ):
        assert forbidden not in source


def test_main_rejects_caller_selected_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rehearsal.sys, "argv", ["harness", "--image", "other"])
    assert rehearsal.main() == 2
