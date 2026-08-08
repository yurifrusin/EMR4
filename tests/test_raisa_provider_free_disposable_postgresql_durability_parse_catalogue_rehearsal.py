"""Deterministic and hostile checks for the disposable PostgreSQL rehearsal."""

from __future__ import annotations

import ast
import copy
import io
import inspect
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal as rehearsal,
)

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-parse-catalogue-rehearsal"
)
CONTRACT = json.loads((DIR / "rehearsal-contract.json").read_text(encoding="utf-8"))
CONTRACT_SCHEMA = json.loads(
    (DIR / "rehearsal-contract.schema.json").read_text(encoding="utf-8")
)
PREREQUISITE = json.loads(
    (DIR / "synthetic-prerequisite-contract.json").read_text(encoding="utf-8")
)
PREREQUISITE_SCHEMA = json.loads(
    (DIR / "synthetic-prerequisite-contract.schema.json").read_text(encoding="utf-8")
)
EVIDENCE_SCHEMA = json.loads(
    (DIR / "rehearsal-evidence.schema.json").read_text(encoding="utf-8")
)
MANIFEST = json.loads((ROOT / CONTRACT["parent"]["manifest_path"]).read_text(encoding="utf-8"))
ARTIFACT = rehearsal._canonical_artifact(  # noqa: SLF001 - exact acceptance surface
    (ROOT / CONTRACT["parent"]["artifact_path"]).read_bytes()
)


def _manifest_ids(kind: str) -> list[str]:
    return [row["identifier"] for row in MANIFEST["ordered_nodes"] if row["kind"] == kind]


def _valid_facts() -> dict[str, Any]:
    role_login = {
        match.group(1): match.group(2) is None
        for match in rehearsal.ROLE_LINE.finditer(ARTIFACT.decode("utf-8"))
    }
    roles = [
        {
            "name": name,
            "login": role_login[name],
            "inherit": False,
            "createdb": False,
            "createrole": False,
            "replication": False,
            "bypassrls": False,
            "superuser": False,
        }
        for name in sorted(_manifest_ids("ROLE"))
    ]
    types = []
    for kind, pg_kind in (("DOMAIN", "d"), ("ENUM", "e"), ("COMPOSITE", "c")):
        types.extend(
            {
                "name": name,
                "type_kind": pg_kind,
                "owner": "context_schema_owner",
            }
            for name in _manifest_ids(kind)
        )
    relations = [
        {
            "name": name,
            "relation_kind": "r",
            "owner": "context_schema_owner",
            "rls_enabled": True,
            "rls_forced": True,
            "acl": "",
        }
        for name in _manifest_ids("TABLE")
    ]
    app_columns = []
    type_name = {
        "uuid": "uuid",
        "text": "text",
        "timestamptz": "timestamp with time zone",
        "integer": "integer",
        "bigint": "bigint",
        "jsonb": "jsonb",
    }
    for table in PREREQUISITE["tables"]:
        for position, column in enumerate(table["columns"], start=1):
            app_columns.append(
                {
                    "relation": "public." + table["name"],
                    "position": position,
                    "name": column["name"],
                    "data_type": type_name[column["type"]],
                    "not_null": not column["nullable"],
                    "default_sql": column["default_sql"] or "",
                }
            )
    app_columns.sort(key=lambda row: (row["relation"], row["position"]))
    fabric_columns = [
        {
            "relation": name,
            "position": 1,
            "name": "synthetic_manifest_bound_column",
            "data_type": "uuid",
            "not_null": True,
            "default_sql": "",
        }
        for name in _manifest_ids("TABLE")
    ]
    function_names = (
        _manifest_ids("SUPPORT_FUNCTION")
        + _manifest_ids("ENTRY_POINT")
        + _manifest_ids("TRIGGER_FUNCTION")
    )
    functions = [
        {
            "name": name,
            "identity_arguments": "",
            "owner": "context_schema_owner",
            "language": "plpgsql",
            "security_definer": True,
            "volatility": "v",
            "strict": False,
            "parallel_safety": "u",
            "configuration": '{"search_path=pg_catalog, emr4_context_fabric"}',
            "acl": "",
        }
        for name in function_names
    ]
    triggers = [
        {
            "name": name,
            "relation": "public.appointments",
            "function": _manifest_ids("TRIGGER_FUNCTION")[index % 14],
            "enabled": "O",
            "deferrable": index >= 7,
            "initially_deferred": index >= 7,
            "definition": "fixed",
        }
        for index, name in enumerate(_manifest_ids("TRIGGER_DECLARATION"))
    ]
    facts: dict[str, Any] = {
        "server": {"server_version_num": 160010, "database": "emr4_synthetic_success"},
        "roles": roles,
        "schema": [{"name": "emr4_context_fabric", "owner": "context_schema_owner", "acl": ""}],
        "types": types,
        "relations": relations,
        "columns": sorted(
            app_columns + fabric_columns,
            key=lambda row: (row["relation"], row["position"]),
        ),
        "constraints": [
            {
                "identifier": name,
                "constraint_kind": "c",
                "deferrable": False,
                "initially_deferred": False,
                "definition": "fixed",
            }
            for name in _manifest_ids("CONSTRAINT")
        ],
        "indexes": [
            {"name": name, "relation": "fixed", "unique_index": True, "definition": "fixed"}
            for name in _manifest_ids("UNIQUE_INDEX")
        ],
        "rls": [
            {"name": name, "enabled": True, "forced": True}
            for name in _manifest_ids("TABLE")
        ],
        "policies": [
            {
                "name": name,
                "relation": "fixed",
                "command": "r",
                "permissive": True,
                "qualification": "fixed",
                "with_check": "",
            }
            for name in _manifest_ids("RLS_POLICY")
        ],
        "functions": functions,
        "triggers": triggers,
        "schema_acl": [],
        "relation_acl": [],
        "function_acl": [],
        "application_relations": [
            {"name": "public." + table["name"], "owner": PREREQUISITE["owner"], "row_count": 0}
            for table in PREREQUISITE["tables"]
        ],
        "extensions": [{"name": "plpgsql", "version": "1.0"}],
    }
    assert set(facts) == set(CONTRACT["catalogue_query_ids"])
    return facts


def test_contract_schemas_are_whole_document_valid() -> None:
    for schema, payload in (
        (CONTRACT_SCHEMA, CONTRACT),
        (PREREQUISITE_SCHEMA, PREREQUISITE),
    ):
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
    Draft202012Validator.check_schema(EVIDENCE_SCHEMA)


def test_parent_artifact_and_manifest_are_exact_before_docker() -> None:
    contract, prerequisite, manifest, artifact = rehearsal._validate_contracts()  # noqa: SLF001
    assert contract == CONTRACT
    assert prerequisite == PREREQUISITE
    assert manifest == MANIFEST
    assert len(artifact) == 1_405_495
    assert rehearsal._bytes_sha(artifact) == CONTRACT["parent"]["artifact_sha256"]  # noqa: SLF001
    assert len(manifest["ordered_nodes"]) == 388
    assert rehearsal._canonical_sha(CONTRACT) == rehearsal.EXPECTED_CONTRACT_SHA256  # noqa: SLF001
    assert (  # noqa: SLF001
        rehearsal._canonical_sha(PREREQUISITE)
        == rehearsal.EXPECTED_PREREQUISITE_SHA256
    )


def test_exact_catalogue_kind_population_is_frozen() -> None:
    assert CONTRACT["manifest_kind_counts"] == {
        "ROLE": 8,
        "SCHEMA": 1,
        "DOMAIN": 4,
        "ENUM": 19,
        "COMPOSITE": 9,
        "TABLE": 18,
        "CONSTRAINT": 81,
        "UNIQUE_INDEX": 4,
        "SUPPORT_FUNCTION": 1,
        "RLS_ENABLE": 18,
        "RLS_FORCE": 18,
        "RLS_POLICY": 44,
        "TYPE_OWNER": 32,
        "RELATION_OWNER": 18,
        "ENTRY_POINT": 9,
        "TRIGGER_FUNCTION": 14,
        "TRIGGER_DECLARATION": 14,
        "REVOKE": 43,
        "GRANT": 33,
    }


def test_type_owner_population_is_exact_one_to_one() -> None:
    typed = set(_manifest_ids("DOMAIN") + _manifest_ids("ENUM") + _manifest_ids("COMPOSITE"))
    owners = set(_manifest_ids("TYPE_OWNER"))
    assert len(typed) == len(owners) == 32
    assert typed == owners


def test_prerequisite_contract_is_exactly_four_empty_minimum_shapes() -> None:
    assert [table["name"] for table in PREREQUISITE["tables"]] == [
        "appointments",
        "appointment_command_idempotency",
        "appointment_audit_log",
        "diary_committed_events",
    ]
    assert all("xmin" not in [column["name"] for column in table["columns"]] for table in PREREQUISITE["tables"])
    assert set(PREREQUISITE["forbidden"]) >= {
        "rows",
        "patient_identifiers",
        "product_values",
        "triggers",
        "policies",
        "grants",
        "application_behavior",
    }


def test_prerequisite_sql_has_no_behavior_or_authority() -> None:
    sql = rehearsal.render_prerequisite_sql(PREREQUISITE).decode("utf-8")
    assert sql.count("CREATE TABLE public.") == 4
    assert "INSERT" not in sql
    assert "CREATE TRIGGER" not in sql
    assert "CREATE POLICY" not in sql
    assert "GRANT " not in sql
    assert "xmin" not in sql


def test_prerequisite_renderer_rejects_xmin_and_unknown_defaults() -> None:
    hostile = copy.deepcopy(PREREQUISITE)
    hostile["tables"][0]["columns"].append(
        {"name": "xmin", "type": "uuid", "nullable": False, "default_sql": None}
    )
    with pytest.raises(rehearsal.RehearsalFailure, match="prerequisite_columns"):
        rehearsal.render_prerequisite_sql(hostile)
    hostile = copy.deepcopy(PREREQUISITE)
    hostile["tables"][0]["columns"][0]["default_sql"] = "nextval('hostile')"
    with pytest.raises(rehearsal.RehearsalFailure, match="unsafe_default"):
        rehearsal.render_prerequisite_sql(hostile)


def test_windows_crlf_is_the_only_artifact_normalization() -> None:
    assert rehearsal._canonical_artifact(b"a\r\nb\r\n") == b"a\nb\n"  # noqa: SLF001
    with pytest.raises(rehearsal.RehearsalFailure, match="lone_carriage_return"):
        rehearsal._canonical_artifact(b"a\rb\n")  # noqa: SLF001


def test_artifact_contains_no_transaction_control_or_psql_meta_commands() -> None:
    text = rehearsal._outside_dollar_quoted(ARTIFACT.decode("utf-8"))  # noqa: SLF001
    assert rehearsal.FORBIDDEN_ARTIFACT_TX.search(text) is None
    assert rehearsal.FORBIDDEN_META.search(text) is None


def test_run_argv_is_networkless_no_pull_no_mount_and_bounded() -> None:
    argv = rehearsal.docker_argv(
        rehearsal.DockerOperation.RUN,
        docker=r"C:\Program Files\Docker\docker.exe",
        profile=CONTRACT["docker_profile"],
        name="emr4-cf-pg16-catalogue-0123456789abcdef",
        nonce="0" * 32,
    )
    rehearsal.assert_closed_argv(argv, rehearsal.DockerOperation.RUN)
    assert "--pull=never" in argv
    assert "--network=none" in argv
    assert "--tmpfs" in argv
    assert "--publish" not in argv and "--volume" not in argv and "-v" not in argv
    assert "POSTGRES_HOST_AUTH_METHOD=trust" not in argv
    assert argv[-1] == "postgres:16-bookworm"


def test_psql_file_argv_binds_atomic_stdin_mode() -> None:
    argv = rehearsal.docker_argv(
        rehearsal.DockerOperation.PSQL_FILE,
        docker=r"C:\Docker\docker.exe",
        profile=CONTRACT["docker_profile"],
        container_id="a" * 64,
        database="emr4_synthetic_rollback",
    )
    rehearsal.assert_closed_argv(argv, rehearsal.DockerOperation.PSQL_FILE)
    assert argv.count("--file=-") == 1
    assert argv.count("--single-transaction") == 1
    assert argv.count("ON_ERROR_STOP=1") == 1
    assert "--command" not in argv


def test_ready_sql_argv_is_noninteractive_and_connection_bounded() -> None:
    argv = rehearsal.docker_argv(
        rehearsal.DockerOperation.READY_SQL,
        docker=r"C:\Docker\docker.exe",
        profile=CONTRACT["docker_profile"],
        container_id="a" * 64,
    )
    rehearsal.assert_closed_argv(argv, rehearsal.DockerOperation.READY_SQL)
    assert argv[:4] == [
        r"C:\Docker\docker.exe",
        "exec",
        "a" * 64,
        "env",
    ]
    assert "-i" not in argv
    assert "PGCONNECT_TIMEOUT=1" in argv
    assert "current_setting('server_version_num')" in argv[-1]


@pytest.mark.parametrize(
    "token",
    ["pull", "build", "login", "compose", "ps", "images", "system", "prune", "ls", "list", "--privileged", "--network=host", "-p", "--publish", "--volume", "-v"],
)
def test_hostile_docker_tokens_are_rejected(token: str) -> None:
    with pytest.raises(rehearsal.RehearsalFailure, match="forbidden_token"):
        rehearsal.assert_closed_argv(
            [r"C:\Docker\docker.exe", "container", "inspect", token],
            rehearsal.DockerOperation.ID_INSPECT,
        )


def test_globs_and_docker_socket_are_rejected() -> None:
    for value in ("*", "?", "/var/run/docker.sock"):
        with pytest.raises(rehearsal.RehearsalFailure, match="forbidden_path_or_glob"):
            rehearsal.assert_closed_argv(
                [r"C:\Docker\docker.exe", "container", "inspect", value],
                rehearsal.DockerOperation.ID_INSPECT,
            )


def test_pull_and_network_fallback_values_are_rejected() -> None:
    for token, code in (
        ("--pull=always", "forbidden_pull_policy"),
        ("--network=bridge", "forbidden_network_mode"),
    ):
        with pytest.raises(rehearsal.RehearsalFailure, match=code):
            rehearsal.assert_closed_argv(
                [r"C:\Docker\docker.exe", "run", token],
                rehearsal.DockerOperation.RUN,
            )


def test_subprocess_boundary_is_argv_only_and_shell_false() -> None:
    source = inspect.getsource(rehearsal._subprocess_runner)  # noqa: SLF001
    assert "shell=False" in source
    assert "CREATE_NO_WINDOW" in source
    assert "os.system" not in source
    assert "subprocess.run(" not in source
    assert ".communicate(" not in source
    assert "threading.Thread" in source


def test_subprocess_output_is_bounded_during_pipe_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeProcess:
        def __init__(self) -> None:
            self.stdin = None
            self.stdout = io.BytesIO(b"x" * 2049)
            self.stderr = io.BytesIO(b"")
            self.returncode = 0

        def wait(self, timeout: float | None = None) -> int:
            del timeout
            return self.returncode

        def kill(self) -> None:
            self.returncode = -9

        def poll(self) -> int:
            return self.returncode

    monkeypatch.setattr(rehearsal.subprocess, "Popen", lambda *args, **kwargs: FakeProcess())
    with pytest.raises(rehearsal.RehearsalFailure, match="output_cap_exceeded"):
        rehearsal._subprocess_runner(  # noqa: SLF001
            [r"C:\Docker\docker.exe", "container", "inspect", "fixed"],
            None,
            1.0,
            1024,
        )


def test_absolute_execution_deadline_caps_calls_and_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[float] = []

    def runner(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> rehearsal.ProcessResult:
        del argv, stdin, cap
        observed.append(timeout)
        return rehearsal.ProcessResult(0, b"", b"")

    monkeypatch.setattr(rehearsal.time, "monotonic", lambda: 10.0)
    bounded = rehearsal._with_total_deadline(runner, 12.5)  # noqa: SLF001
    bounded(["docker.exe"], None, 30, 1024)
    assert observed == [2.5]
    monkeypatch.setattr(rehearsal.time, "monotonic", lambda: 12.5)
    with pytest.raises(rehearsal.RehearsalFailure, match="total_timeout"):
        bounded(["docker.exe"], None, 30, 1024)


def test_postgres_readiness_requires_continuous_authenticated_sql() -> None:
    profile = copy.deepcopy(CONTRACT["docker_profile"])
    profile["startup_timeout_seconds"] = 5
    profile["readiness_stability_seconds"] = 0.5
    profile["readiness_probe_interval_seconds"] = 0.25
    current = 0.0
    ready_attempts = 0
    sql_attempts = 0
    calls: list[list[str]] = []
    observation: dict[str, Any] = {}

    def clock() -> float:
        return current

    def sleeper(delay: float) -> None:
        nonlocal current
        current += delay

    def runner(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> rehearsal.ProcessResult:
        nonlocal ready_attempts, sql_attempts
        del stdin, timeout, cap
        calls.append(argv)
        if "pg_isready" in argv:
            ready_attempts += 1
            if ready_attempts == 2:
                return rehearsal.ProcessResult(1, b"", b"bootstrap handoff")
            return rehearsal.ProcessResult(0, b"accepting connections\n", b"")
        assert "current_setting('server_version_num')" in argv[-1]
        sql_attempts += 1
        return rehearsal.ProcessResult(0, b"16\n", b"")

    rehearsal._wait_for_stable_postgres(  # noqa: SLF001
        runner,
        r"C:\Docker\docker.exe",
        "a" * 64,
        profile,
        observation=observation,
        clock=clock,
        sleeper=sleeper,
    )
    assert ready_attempts == 5
    assert sql_attempts == 4
    assert current == 1.0
    assert all("CREATE" not in " ".join(call) for call in calls)
    assert observation["status"] == "stable"
    assert observation["pg_isready_attempts"] == 5
    assert observation["pg_isready_successes"] == 4
    assert observation["sql_probe_attempts"] == 4
    assert observation["sql_probe_successes"] == 4
    assert observation["continuous_success_ms"] == 500


def test_postgres_readiness_translates_sql_probe_process_timeout() -> None:
    profile = copy.deepcopy(CONTRACT["docker_profile"])
    observation: dict[str, Any] = {}

    def runner(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> rehearsal.ProcessResult:
        del stdin, timeout, cap
        if "pg_isready" in argv:
            return rehearsal.ProcessResult(0, b"accepting connections\n", b"")
        raise rehearsal.RehearsalFailure("process", "timeout", "synthetic")

    with pytest.raises(rehearsal.RehearsalFailure) as captured:
        rehearsal._wait_for_stable_postgres(  # noqa: SLF001
            runner,
            r"C:\Docker\docker.exe",
            "a" * 64,
            profile,
            observation=observation,
        )
    assert captured.value.stage == "postgres"
    assert captured.value.code == "readiness_probe_timeout"
    assert captured.value.detail == "ready_sql"
    assert observation["status"] == "probe_timeout"
    assert observation["timed_out_operation"] == "ready_sql"
    assert observation["pg_isready_attempts"] == 1
    assert observation["pg_isready_successes"] == 1
    assert observation["sql_probe_attempts"] == 1
    assert observation["sql_probe_successes"] == 0


def test_postgres_readiness_caps_each_probe_to_startup_deadline() -> None:
    profile = copy.deepcopy(CONTRACT["docker_profile"])
    profile["startup_timeout_seconds"] = 1
    profile["readiness_stability_seconds"] = 0
    current = 0.0
    observed_timeouts: list[float] = []

    def clock() -> float:
        return current

    def runner(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> rehearsal.ProcessResult:
        nonlocal current
        del stdin, cap
        observed_timeouts.append(timeout)
        if "pg_isready" in argv:
            current = 0.75
            return rehearsal.ProcessResult(0, b"accepting connections\n", b"")
        return rehearsal.ProcessResult(0, b"16\n", b"")

    rehearsal._wait_for_stable_postgres(  # noqa: SLF001
        runner,
        r"C:\Docker\docker.exe",
        "a" * 64,
        profile,
        clock=clock,
        sleeper=lambda _delay: None,
    )
    assert observed_timeouts == [1.0, 0.25]


def test_module_has_no_database_cloud_http_or_environment_input_import() -> None:
    tree = ast.parse(Path(rehearsal.__file__).read_text(encoding="utf-8"))
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not imports.intersection(
        {"sqlalchemy", "psycopg", "requests", "httpx", "socket", "google", "boto3", "alembic"}
    )


def test_query_transport_sets_read_only_and_uses_file_stdin() -> None:
    captured: dict[str, Any] = {}

    def runner(argv: list[str], stdin: bytes | None, timeout: int, cap: int) -> rehearsal.ProcessResult:
        captured.update(argv=argv, stdin=stdin, timeout=timeout, cap=cap)
        return rehearsal.ProcessResult(0, b"[]\n", b"")

    result = rehearsal._query_json(  # noqa: SLF001
        runner,
        r"C:\Docker\docker.exe",
        "a" * 64,
        "emr4_synthetic_success",
        CONTRACT["docker_profile"],
        "SELECT '[]'::json::text",
    )
    assert result == []
    assert captured["stdin"].startswith(b"SET TRANSACTION READ ONLY;\n")
    assert "--file=-" in captured["argv"]
    assert "--single-transaction" in captured["argv"]


def test_catalogue_projection_matches_every_frozen_population() -> None:
    result = rehearsal._assert_catalogue(  # noqa: SLF001
        _valid_facts(), MANIFEST, PREREQUISITE, CONTRACT
    )
    assert result["kind_counts"] == {
        "roles": 8,
        "types": 32,
        "relations": 18,
        "columns": 52,
        "constraints": 81,
        "indexes": 4,
        "policies": 44,
        "functions": 24,
        "triggers": 14,
    }
    assert set(result["query_ids"]) == set(CONTRACT["catalogue_query_ids"])


def test_catalogue_queries_project_every_definition_and_authority_surface() -> None:
    types_sql = rehearsal.CATALOGUE_SQL["types"]
    policies_sql = rehearsal.CATALOGUE_SQL["policies"]
    functions_sql = rehearsal.CATALOGUE_SQL["functions"]
    triggers_sql = rehearsal.CATALOGUE_SQL["triggers"]
    assert all(
        field in types_sql
        for field in (
            "domain_base_type",
            "domain_not_null",
            "domain_default_sql",
            "domain_constraints",
            "enum_labels",
            "composite_attributes",
        )
    )
    assert "polroles" in policies_sql and "AS roles" in policies_sql
    assert "pg_get_function_identity_arguments" in functions_sql
    assert "pg_get_function_result" in functions_sql
    assert "proconfig" in functions_sql and "prosecdef" in functions_sql
    assert all(
        field in triggers_sql
        for field in (
            "timing",
            "level",
            "fires_insert",
            "fires_delete",
            "fires_update",
            "fires_truncate",
            "pg_get_triggerdef",
        )
    )


def test_characterization_cannot_pass_and_exact_digests_reject_definition_drift() -> None:
    facts = _valid_facts()
    characterized = rehearsal._assert_catalogue(  # noqa: SLF001
        facts, MANIFEST, PREREQUISITE, CONTRACT
    )
    assert characterized["expectation_mode"] == "characterization_only"
    bound = copy.deepcopy(CONTRACT)
    bound["catalogue_expectation"] = {
        "mode": "exact_digest_bound",
        "expected_query_digests": {
            key: characterized["query_digests"][key]
            for key in CONTRACT["catalogue_query_ids"]
            if key not in {"server", "extensions"}
        },
    }
    exact = rehearsal._assert_catalogue(  # noqa: SLF001
        facts, MANIFEST, PREREQUISITE, bound
    )
    assert exact["expectation_mode"] == "exact_digest_bound"
    hostile = copy.deepcopy(facts)
    hostile["constraints"][0]["definition"] = "CHECK (false)"
    with pytest.raises(rehearsal.RehearsalFailure, match="exact_query_digest"):
        rehearsal._assert_catalogue(  # noqa: SLF001
            hostile, MANIFEST, PREREQUISITE, bound
        )


@pytest.mark.parametrize(
    "surface",
    [
        "schema_acl_text",
        "domain_definition",
        "relation_acl_text",
        "fabric_column",
        "index_definition",
        "policy_expression",
        "function_attribute",
        "trigger_definition",
        "relation_grant",
        "function_grant",
    ],
)
def test_exact_digest_binding_rejects_same_population_drift(surface: str) -> None:
    facts = _valid_facts()
    digests = {
        key: rehearsal._facts_digest(value)  # noqa: SLF001
        for key, value in facts.items()
        if key not in {"server", "extensions"}
    }
    bound = copy.deepcopy(CONTRACT)
    bound["catalogue_expectation"] = {
        "mode": "exact_digest_bound",
        "expected_query_digests": digests,
    }
    if surface == "schema_acl_text":
        facts["schema"][0]["acl"] = "hostile"
    elif surface == "domain_definition":
        facts["types"][0]["domain_constraints"] = [
            {"name": "same_name", "definition": "CHECK (false)"}
        ]
    elif surface == "relation_acl_text":
        facts["relations"][0]["acl"] = "hostile"
    elif surface == "fabric_column":
        fabric = next(
            row
            for row in facts["columns"]
            if row["relation"].startswith("emr4_context_fabric.")
        )
        fabric["default_sql"] = "hostile"
    elif surface == "index_definition":
        facts["indexes"][0]["definition"] = "CREATE UNIQUE INDEX same_name ON hostile"
    elif surface == "policy_expression":
        facts["policies"][0]["qualification"] = "false"
    elif surface == "function_attribute":
        facts["functions"][0]["security_definer"] = False
    elif surface == "trigger_definition":
        facts["triggers"][0]["definition"] = "CREATE TRIGGER same_name hostile"
    elif surface == "relation_grant":
        facts["relation_acl"].append(
            {
                "relation": "emr4_context_fabric.context_frame_generation",
                "grantee": "context_observer",
                "privilege": "SELECT",
                "grantable": False,
            }
        )
    elif surface == "function_grant":
        facts["function_acl"].append(
            {
                "function": "emr4_context_fabric.apply_durability_transition_v1",
                "grantee": "context_observer",
                "privilege": "EXECUTE",
                "grantable": False,
            }
        )
    with pytest.raises(rehearsal.RehearsalFailure, match="exact_query_digest"):
        rehearsal._assert_catalogue(  # noqa: SLF001
            facts, MANIFEST, PREREQUISITE, bound
        )


@pytest.mark.parametrize(
    ("field", "code"),
    [
        ("roles", "role_population"),
        ("types", "type_population"),
        ("relations", "relation_population"),
        ("constraints", "constraint_population"),
        ("indexes", "index_population"),
        ("policies", "policy_population"),
        ("functions", "function_population"),
        ("triggers", "trigger_population"),
        ("application_relations", "application_relation_population"),
    ],
)
def test_catalogue_population_mutations_fail_closed(field: str, code: str) -> None:
    facts = _valid_facts()
    facts[field] = facts[field][1:]
    with pytest.raises(rehearsal.RehearsalFailure, match=code):
        rehearsal._assert_catalogue(  # noqa: SLF001
            facts, MANIFEST, PREREQUISITE, CONTRACT
        )


def test_public_acl_and_runtime_schema_create_fail_closed() -> None:
    facts = _valid_facts()
    facts["schema_acl"] = [{"grantee": "PUBLIC", "privilege": "USAGE", "grantable": False}]
    with pytest.raises(rehearsal.RehearsalFailure, match="public_acl"):
        rehearsal._assert_catalogue(  # noqa: SLF001
            facts, MANIFEST, PREREQUISITE, CONTRACT
        )
    facts = _valid_facts()
    facts["schema_acl"] = [{"grantee": "context_producer", "privilege": "CREATE", "grantable": False}]
    with pytest.raises(rehearsal.RehearsalFailure, match="runtime_schema_create_acl"):
        rehearsal._assert_catalogue(  # noqa: SLF001
            facts, MANIFEST, PREREQUISITE, CONTRACT
        )


def test_application_owner_rows_and_column_shape_fail_closed() -> None:
    for mutation in ("owner", "rows", "columns"):
        facts = _valid_facts()
        if mutation == "owner":
            facts["application_relations"][0]["owner"] = "context_schema_owner"
        elif mutation == "rows":
            facts["application_relations"][0]["row_count"] = 1
        else:
            facts["columns"] = facts["columns"][1:]
        with pytest.raises(rehearsal.RehearsalFailure):
            rehearsal._assert_catalogue(  # noqa: SLF001
                facts, MANIFEST, PREREQUISITE, CONTRACT
            )


def _owned_inspect() -> dict[str, Any]:
    profile = CONTRACT["docker_profile"]
    return {
        "Id": "a" * 64,
        "Name": "/emr4-cf-pg16-catalogue-0123456789abcdef",
        "Image": "sha256:" + "b" * 64,
        "Config": {
            "Image": profile["image_reference"],
            "Env": [
                f'POSTGRES_USER={profile["postgres_user"]}',
                f'POSTGRES_PASSWORD={profile["postgres_password"]}',
                f'POSTGRES_DB={profile["postgres_database"]}',
                f'PGDATA={profile["pgdata"]}',
            ],
            "Labels": {
                "com.emr4.harness": profile["ownership_labels"]["com.emr4.harness"],
                "com.emr4.cleanup-nonce": "0" * 32,
            },
        },
        "HostConfig": {
            "NetworkMode": "none",
            "Binds": None,
            "PortBindings": {},
            "Privileged": False,
            "Memory": 768 * 1024 * 1024,
            "NanoCpus": 1_000_000_000,
            "PidsLimit": 192,
            "RestartPolicy": {"Name": "no"},
            "Tmpfs": {"/var/lib/postgresql/data": "rw,noexec,nosuid,size=536870912"},
        },
        "Mounts": [{"Type": "tmpfs", "Destination": "/var/lib/postgresql/data"}],
    }


def test_cleanup_ownership_requires_every_exact_fact() -> None:
    profile = CONTRACT["docker_profile"]
    kwargs = {
        "container_id": "a" * 64,
        "name": "emr4-cf-pg16-catalogue-0123456789abcdef",
        "nonce": "0" * 32,
        "image_id": "sha256:" + "b" * 64,
        "profile": profile,
    }
    assert rehearsal._container_owned(_owned_inspect(), **kwargs)  # noqa: SLF001
    for mutate in (
        "id",
        "name",
        "label",
        "image",
        "network",
        "mount",
        "privileged",
        "memory",
        "cpu",
        "pids",
        "tmpfs",
        "port",
        "environment",
        "unexpected_mount",
    ):
        payload = _owned_inspect()
        if mutate == "id":
            payload["Id"] = "c" * 64
        elif mutate == "name":
            payload["Name"] = "/other"
        elif mutate == "label":
            payload["Config"]["Labels"]["com.emr4.cleanup-nonce"] = "other"
        elif mutate == "image":
            payload["Image"] = "sha256:" + "c" * 64
        elif mutate == "network":
            payload["HostConfig"]["NetworkMode"] = "bridge"
        elif mutate == "mount":
            payload["Mounts"].append({"Type": "bind", "Destination": "/workspace"})
        elif mutate == "privileged":
            payload["HostConfig"]["Privileged"] = True
        elif mutate == "memory":
            payload["HostConfig"]["Memory"] = 0
        elif mutate == "cpu":
            payload["HostConfig"]["NanoCpus"] = 0
        elif mutate == "pids":
            payload["HostConfig"]["PidsLimit"] = 0
        elif mutate == "tmpfs":
            payload["HostConfig"]["Tmpfs"] = {
                "/var/lib/postgresql/data": "rw,size=536870912"
            }
        elif mutate == "port":
            payload["HostConfig"]["PortBindings"] = {"5432/tcp": [{"HostPort": "5432"}]}
        elif mutate == "environment":
            payload["Config"]["Env"] = []
        elif mutate == "unexpected_mount":
            payload["Mounts"] = [{"Type": "npipe", "Destination": "/other"}]
        assert not rehearsal._container_owned(payload, **kwargs)  # noqa: SLF001
    for malformed in (
        {"Config": None, "HostConfig": {}, "Mounts": []},
        {"Config": {}, "HostConfig": None, "Mounts": []},
        {"Config": {}, "HostConfig": {}, "Mounts": None},
        {"Config": {"Labels": []}, "HostConfig": {}, "Mounts": []},
    ):
        assert not rehearsal._container_owned(malformed, **kwargs)  # noqa: SLF001


def test_cleanup_ownership_accepts_docker_desktop_empty_mounts_projection() -> None:
    profile = CONTRACT["docker_profile"]
    payload = _owned_inspect()
    payload["Mounts"] = []
    assert rehearsal._container_owned(  # noqa: SLF001
        payload,
        container_id="a" * 64,
        name="emr4-cf-pg16-catalogue-0123456789abcdef",
        nonce="0" * 32,
        image_id="sha256:" + "b" * 64,
        profile=profile,
    )


def test_exact_absence_requires_documented_no_such_object() -> None:
    assert rehearsal._is_exact_absence(  # noqa: SLF001
        rehearsal.ProcessResult(1, b"", b"Error: No such object: abc")
    )
    assert not rehearsal._is_exact_absence(  # noqa: SLF001
        rehearsal.ProcessResult(1, b"", b"daemon unavailable")
    )
    assert not rehearsal._is_exact_absence(rehearsal.ProcessResult(0, b"{}", b""))  # noqa: SLF001
    assert rehearsal._is_exact_absence(  # noqa: SLF001
        rehearsal.ProcessResult(
            1,
            b"",
            b"Error response from daemon: No such container: exact-owned-name",
        )
    )


def test_exact_owned_cleanup_uses_only_captured_id() -> None:
    calls: list[list[str]] = []
    responses = [
        rehearsal.ProcessResult(0, json.dumps(_owned_inspect()).encode("utf-8"), b""),
        rehearsal.ProcessResult(0, b"a" * 64 + b"\n", b""),
        rehearsal.ProcessResult(1, b"", b"Error: No such object: " + b"a" * 64),
    ]

    def runner(argv: list[str], stdin: bytes | None, timeout: int, cap: int) -> rehearsal.ProcessResult:
        del stdin, timeout, cap
        calls.append(argv)
        return responses.pop(0)

    result = rehearsal._cleanup(  # noqa: SLF001
        runner,
        r"C:\Docker\docker.exe",
        "a" * 64,
        "emr4-cf-pg16-catalogue-0123456789abcdef",
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
    assert all("prune" not in call and "ls" not in call for call in calls)


def test_environment_stop_never_calls_docker_or_writes_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rehearsal.shutil, "which", lambda _name: None)

    def forbidden_runner(
        argv: list[str], stdin: bytes | None, timeout: int, cap: int
    ) -> rehearsal.ProcessResult:
        del argv, stdin, timeout, cap
        raise AssertionError("runner must not be reached")

    evidence = rehearsal.run_rehearsal(runner=forbidden_runner)
    assert evidence["result"] == "environment_unavailable"
    assert evidence["lifecycle"] == ["parent_verified"]
    assert evidence["cleanup"]["status"] == "not_needed"
    assert evidence["environment"]["failure"]["code"] == "docker_client_missing"
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)


def test_evidence_schema_accepts_bounded_environment_stop() -> None:
    payload = {
        "schema_version": "emr4.disposable-postgresql-durability-rehearsal-evidence.v1",
        "result": "environment_unavailable",
        "evidence_mode": rehearsal.EVIDENCE_MODE,
        "attempt_id": "authored-synthetic",
        "parent": {},
        "environment": {"failure": {"stage": "environment", "code": "docker_client_missing"}},
        "lifecycle": ["parent_verified"],
        "rollback": {"status": "not_started"},
        "catalogue": {"status": "not_started"},
        "cleanup": {"status": "not_needed"},
        "claim_boundary": rehearsal.CLAIM_BOUNDARY,
    }
    Draft202012Validator(EVIDENCE_SCHEMA).validate(payload)


def test_main_rejects_all_caller_selected_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rehearsal.sys, "argv", ["harness", "--image", "other"])
    assert rehearsal.main() == 2
