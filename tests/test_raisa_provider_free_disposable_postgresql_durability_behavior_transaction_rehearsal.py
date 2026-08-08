from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from scripts import (
    raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal as rehearsal,
)

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-behavior-transaction-rehearsal"
)
CONTRACT = json.loads(
    (DIR / "behavior-transaction-rehearsal-contract.json").read_text(encoding="utf-8")
)
CONTRACT_SCHEMA = json.loads(
    (DIR / "behavior-transaction-rehearsal-contract.schema.json").read_text(
        encoding="utf-8"
    )
)
EVIDENCE_SCHEMA = json.loads(
    (DIR / "provider-free-behavior-transaction-evidence.schema.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-001.json").read_text(
        encoding="utf-8"
    )
)


def _snapshot() -> dict[str, dict[str, Any]]:
    return {
        relation: {"count": 0, "digest": "sha256:" + "0" * 64}
        for relation in rehearsal.SNAPSHOT_RELATIONS
    }


def _passing_evidence() -> dict[str, Any]:
    snapshot = _snapshot()
    stderr = {"byte_count": 0, "sha256": "0" * 64}
    records: list[dict[str, Any]] = []
    for scenario in CONTRACT["scenarios"]:
        records.append(
            {
                "scenario_id": scenario["id"],
                "category": scenario["category"],
                "principal": scenario["principal"],
                "transaction_shape": scenario["transaction_shape"],
                "expected_outcome": scenario["expected_outcome"],
                "observed_outcome": scenario["expected_outcome"],
                "expected_sqlstate": scenario["expected_sqlstate"],
                "observed_sqlstate": scenario["expected_sqlstate"],
                "expected_failure_id": scenario["expected_failure_id"],
                "observed_failure_id": scenario["expected_failure_id"],
                "stable_reason": "accepted",
                "session_user": scenario["principal"],
                "current_user": scenario["principal"],
                "isolation": "read committed",
                "read_only": scenario["id"] == "BTR-R01",
                "before": snapshot,
                "after": snapshot,
                "readback_checks": {name: True for name in scenario["readback"]},
                "forbidden_effects_absent": {
                    name: True for name in scenario["forbidden_effects"]
                },
                "transport": {"psql_exit": 0, "stderr_digest": stderr},
                "passed": True,
            }
        )
    return {
        "schema_version": (
            "emr4.raisa-context-fabric-disposable-postgresql-"
            "behavior-transaction-evidence.v1"
        ),
        "result": rehearsal.PASS_RESULT,
        "evidence_mode": rehearsal.EVIDENCE_MODE,
        "attempt_id": "0" * 24,
        "parent": {
            "behavior_contract_sha256": "sha256:" + "1" * 64,
            "artifact_sha256": "sha256:" + "2" * 64,
            "manifest_sha256": "sha256:" + "3" * 64,
            "prerequisite_sha256": "sha256:" + "4" * 64,
            "statement_count": 1,
        },
        "environment": {
            "docker_client": "resolved_exact_docker_exe",
            "image": {
                "reference": "postgres:16-bookworm",
                "id": "sha256:" + "5" * 64,
                "pull_attempted": False,
            },
            "readiness": {},
            "elapsed_ms": 1,
        },
        "lifecycle": ["passed"],
        "preconditions": ["position_two_projected", "rollback_primary_precommitted"],
        "scenarios": records,
        "scenario_reconciliation": {"expected": 20, "observed": 20, "passed": 20},
        "cleanup": {
            "status": "cleanup_verified",
            "container_id": "a" * 64,
            "removed": True,
            "absence_verified": True,
        },
        "claim_boundary": rehearsal.CLAIM_BOUNDARY,
    }


def test_contract_and_evidence_schemas_are_whole_document_valid() -> None:
    jsonschema.Draft202012Validator.check_schema(CONTRACT_SCHEMA)
    jsonschema.Draft202012Validator(CONTRACT_SCHEMA).validate(CONTRACT)
    jsonschema.Draft202012Validator.check_schema(EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(_passing_evidence())
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(FAILURE_EVIDENCE)
    assert FAILURE_EVIDENCE["result"] == "rehearsal_failed"
    assert FAILURE_EVIDENCE["environment"]["failure"] == {
        "code": "server_or_database",
        "detail_digest": "sha256:"
        + "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stage": "catalogue",
    }
    assert FAILURE_EVIDENCE["scenario_reconciliation"] == {
        "expected": 20,
        "observed": 0,
        "passed": 0,
    }
    assert FAILURE_EVIDENCE["cleanup"] == {
        "absence_verified": True,
        "container_id": FAILURE_EVIDENCE["cleanup"]["container_id"],
        "removed": True,
        "status": "cleanup_verified",
    }


def test_parent_catalogue_reuse_preserves_descendant_database_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_parent_assertion(
        facts: dict[str, object],
        manifest: dict[str, object],
        prerequisite: dict[str, object],
        contract: dict[str, object],
    ) -> dict[str, object]:
        captured.update(
            facts=facts,
            manifest=manifest,
            prerequisite=prerequisite,
            contract=contract,
        )
        return {"status": "passed"}

    monkeypatch.setattr(rehearsal.parent, "_assert_catalogue", fake_parent_assertion)
    facts = {
        "server": {
            "server_version_num": 160011,
            "database": "emr4_synthetic_behavior",
        }
    }
    manifest = {"manifest": True}
    prerequisite = {"prerequisite": True}
    contract = {"contract": True}

    assert rehearsal._assert_bound_parent_catalogue(
        facts,
        manifest,
        prerequisite,
        contract,
        expected_database="emr4_synthetic_behavior",
    ) == {"status": "passed"}
    assert facts["server"]["database"] == "emr4_synthetic_behavior"
    assert captured["facts"]["server"]["database"] == "emr4_synthetic_success"

    with pytest.raises(rehearsal.BehaviorFailure) as failure:
        rehearsal._assert_bound_parent_catalogue(
            facts,
            manifest,
            prerequisite,
            contract,
            expected_database="wrong_database",
        )
    assert (failure.value.stage, failure.value.code) == (
        "catalogue",
        "server_or_database",
    )


def test_contract_is_exactly_hash_bound_to_six_canonical_parent_files() -> None:
    contract, prerequisite, manifest, artifact = rehearsal._validate_contract()
    assert contract == CONTRACT
    assert prerequisite["schema_version"].endswith("prerequisite-contract.v1")
    assert manifest["sql_sha256"] == rehearsal._sha256(artifact)
    assert len(contract["parent_bindings"]) == 6
    assert {row["id"] for row in contract["parent_bindings"]} == {
        "accepted_runtime_source",
        "inert_sql",
        "render_manifest",
        "structural_contract",
        "body_contract",
        "parse_prerequisite_contract",
    }


def test_contract_mutation_fails_before_any_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = rehearsal._json

    def hostile(path: Path) -> dict[str, Any]:
        value = original(path)
        if path == rehearsal.CONTRACT_PATH:
            value["runtime_profile"]["network_mode"] = "bridge"
        return value

    monkeypatch.setattr(rehearsal, "_json", hostile)
    with pytest.raises(rehearsal.BehaviorFailure, match="contract_sha256"):
        rehearsal._validate_contract()


def test_canonical_parent_binding_accepts_crlf_only_as_lf_normalization(
    tmp_path: Path,
) -> None:
    target = tmp_path / "parent.txt"
    target.write_bytes(b"one\r\ntwo\r\n")
    assert rehearsal._canonical_bytes(target) == b"one\ntwo\n"
    target.write_bytes(b"one\x00two\n")
    assert rehearsal._canonical_bytes(target) == b"one\x00two\n"


def test_twenty_scenario_renderers_have_one_pre_begin_identity_and_fixed_order() -> (
    None
):
    rendered_ids: list[str] = []
    for scenario in CONTRACT["scenarios"]:
        if scenario["id"] == "BTR-R03":
            continue
        sql = rehearsal.render_scenario_sql(CONTRACT, scenario["id"]).decode("utf-8")
        assert sql.count("SET SESSION AUTHORIZATION") == 1
        assert sql.index("SET SESSION AUTHORIZATION") < sql.index("BEGIN")
        assert "SAVEPOINT" not in sql
        assert "PREPARE TRANSACTION" not in sql
        assert "\\" not in sql
        rendered_ids.append(scenario["id"])
    assert rendered_ids == [
        row for row in CONTRACT["scenario_order"] if row != "BTR-R03"
    ]


def test_multi_transaction_scenarios_are_exactly_three_top_level_transactions() -> None:
    for scenario_id in ("BTR-E01", "BTR-I02"):
        sql = rehearsal.render_scenario_sql(CONTRACT, scenario_id).decode("utf-8")
        assert sql.count("BEGIN ISOLATION LEVEL READ COMMITTED;") == 3
        assert sql.count("COMMIT;") == 3
        assert sql.count("SET SESSION AUTHORIZATION") == 1


def test_trigger_scenarios_bind_the_first_reachable_producer_boundary() -> None:
    scenarios = {row["id"]: row for row in CONTRACT["scenarios"]}
    assert scenarios["BTR-T01"]["expected_sqlstate"] == "CF603"
    assert scenarios["BTR-T02"]["expected_failure_id"] == "F_IMMUTABLE"
    assert scenarios["BTR-T02"]["expected_sqlstate"] == "CF601"
    assert scenarios["BTR-T03"]["action"] == "update_committed_event"
    assert scenarios["BTR-T03"]["expected_sqlstate"] == "CF601"

    t02 = rehearsal.render_scenario_sql(CONTRACT, "BTR-T02").decode("utf-8")
    t03 = rehearsal.render_scenario_sql(CONTRACT, "BTR-T03").decode("utf-8")
    assert "DELETE FROM public.diary_committed_events" in t02
    assert "UPDATE public.diary_committed_events" in t03
    assert "UPDATE emr4_context_fabric" not in t03

    artifact = (
        ROOT
        / "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert"
    ).read_text(encoding="utf-8")
    guard = artifact[
        artifact.index(
            "CREATE FUNCTION emr4_context_fabric.cf_guard_event_v1()"
        ) : artifact.index("CREATE FUNCTION emr4_context_fabric.cf_fence_event_v1()")
    ]
    assert "TG_OP = 'UPDATE'" in guard
    assert "TG_OP = 'DELETE'" in guard
    assert "pg_current_xact_id" in guard
    assert guard.count("ERRCODE = 'CF601'") >= 2


def test_role_matrix_uses_five_fresh_fixed_denial_connections() -> None:
    matrix = rehearsal.render_role_matrix(CONTRACT)
    assert [name for name, _ in matrix] == [
        "producer_direct_fabric_dml",
        "observer_foreign_entry_point",
        "producer_trigger_execute",
        "observer_set_role",
        "application_read_direct_update",
    ]
    for _, raw in matrix:
        sql = raw.decode("utf-8")
        assert sql.count("SET SESSION AUTHORIZATION") == 1
        assert sql.count("BEGIN ISOLATION LEVEL READ COMMITTED;") == 1


def test_bootstrap_is_fixed_to_six_bindings_four_opaque_appointments_and_no_credentials() -> (
    None
):
    sql = rehearsal.render_bootstrap_sql(CONTRACT).decode("utf-8")
    assert sql.count("SET SESSION AUTHORIZATION emr4_synthetic_bootstrap;") == 1
    for role in (
        "context_producer",
        "context_observer",
        "context_coordinator",
        "context_lifecycle",
        "context_retention",
        "context_application_read",
    ):
        assert sql.count(role) >= 1
    for fixture in (
        "appointment_temporal",
        "appointment_non_temporal",
        "appointment_negative",
        "appointment_beta",
    ):
        assert CONTRACT["fixture_namespace"][fixture] in sql
    assert "PASSWORD" not in sql.upper()
    assert "BYPASSRLS" not in sql.upper()
    assert "TRUST" not in sql.upper()


def test_cluster_initialization_uses_peer_local_auth_rejects_host_auth_and_has_no_password() -> (
    None
):
    profile = rehearsal._profile()
    assert "postgres_password" not in profile
    run = rehearsal._run_argv("docker.exe", profile, name="emr4-cf", nonce="0" * 32)
    rehearsal.assert_run_argv(run)
    assert not any("POSTGRES_" in token or "PASSWORD" in token.upper() for token in run)
    init = rehearsal._init_argvs("docker.exe", "a" * 64, profile)
    assert [stage for stage, _, _ in init] == [
        "pgdata_directory",
        "initdb",
        "pg_hba",
        "pg_ident",
        "postgres_start",
    ]
    for _, argv, stdin in init:
        rehearsal.assert_init_argv(argv, stdin)
    initdb = next(argv for stage, argv, _ in init if stage == "initdb")
    assert "--auth-local=peer" in initdb
    assert "--auth-host=reject" in initdb
    hba = next(stdin for stage, _, stdin in init if stage == "pg_hba")
    assert hba is not None and b"peer map=emr4map" in hba and b" reject" in hba
    assert b"trust" not in hba


def _owned_container() -> tuple[dict[str, Any], dict[str, Any]]:
    profile = rehearsal._profile()
    path, options = profile["tmpfs"].split(":", 1)
    inspect = {
        "Id": "a" * 64,
        "Name": "/emr4-cf",
        "Image": "sha256:" + "b" * 64,
        "Config": {
            "Image": "postgres:16-bookworm",
            "Entrypoint": ["/usr/bin/tail"],
            "Cmd": ["--follow", "/dev/null"],
            "Labels": {
                "com.emr4.harness": "disposable-postgresql-durability-behavior-v1",
                "com.emr4.cleanup-nonce": "0" * 32,
            },
            "Env": ["PATH=/usr/local/bin:/usr/bin:/bin"],
        },
        "HostConfig": {
            "NetworkMode": "none",
            "Binds": None,
            "Privileged": False,
            "PortBindings": {},
            "Memory": 768 * 1024 * 1024,
            "NanoCpus": 1_000_000_000,
            "PidsLimit": 192,
            "RestartPolicy": {"Name": "no"},
            "Tmpfs": {path: options},
        },
        "Mounts": [],
    }
    return inspect, profile


def test_cleanup_ownership_requires_exact_inert_passwordless_containment() -> None:
    inspect, profile = _owned_container()
    kwargs = {
        "container_id": "a" * 64,
        "name": "emr4-cf",
        "nonce": "0" * 32,
        "image_id": "sha256:" + "b" * 64,
        "profile": profile,
    }
    assert rehearsal._behavior_container_owned(inspect, **kwargs)
    for mutation in (
        lambda value: value["HostConfig"].__setitem__("NetworkMode", "bridge"),
        lambda value: value["Config"]["Env"].append("POSTGRES_PASSWORD=forbidden"),
        lambda value: value["Config"].__setitem__(
            "Entrypoint", ["docker-entrypoint.sh"]
        ),
        lambda value: value["HostConfig"].__setitem__(
            "PortBindings", {"5432/tcp": [{}]}
        ),
        lambda value: value["Mounts"].append(
            {"Type": "bind", "Destination": "/workspace"}
        ),
    ):
        hostile = copy.deepcopy(inspect)
        mutation(hostile)
        assert not rehearsal._behavior_container_owned(hostile, **kwargs)


def test_scenario_transport_is_stdin_only_noninteractive_and_not_outer_wrapped() -> (
    None
):
    argv = rehearsal._scenario_argv(
        "C:\\Program Files\\Docker\\docker.exe", "a" * 64, rehearsal._profile()
    )
    rehearsal.assert_scenario_argv(argv)
    assert "--file=-" in argv
    assert "--single-transaction" not in argv
    assert "--command" not in argv
    assert "ON_ERROR_STOP=1" in argv


@pytest.mark.parametrize(
    "token", ["--single-transaction", "--command", "-c", "--variable"]
)
def test_hostile_scenario_transport_tokens_fail_closed(token: str) -> None:
    argv = rehearsal._scenario_argv("docker.exe", "a" * 64, rehearsal._profile())
    argv.append(token)
    with pytest.raises(rehearsal.BehaviorFailure):
        rehearsal.assert_scenario_argv(argv)


def test_snapshot_projection_is_exactly_twenty_two_allowlisted_relations_and_value_free() -> (
    None
):
    assert len(rehearsal.SNAPSHOT_RELATIONS) == 22
    sql = rehearsal._snapshot_sql()
    for relation in rehearsal.SNAPSHOT_RELATIONS:
        assert relation in sql
    assert "jsonb_agg" in sql
    assert "sha256" in sql
    assert "payload ->" not in sql
    assert "patient" not in sql.lower()


def test_relation_delta_reconciliation_rejects_hidden_or_unexpected_effects() -> None:
    before = _snapshot()
    after = copy.deepcopy(before)
    for relation, delta in rehearsal.EXPECTED_DELTAS["BTR-E02"].items():
        after[relation]["count"] += delta
        after[relation]["digest"] = "sha256:" + "1" * 64
    for relation in (
        "public.appointments",
        "emr4_context_fabric.context_observation_stream_head",
    ):
        after[relation]["digest"] = "sha256:" + "1" * 64
    rehearsal._assert_delta("BTR-E02", before, after)
    hostile = copy.deepcopy(after)
    hostile["emr4_context_fabric.context_recovery_pin"]["digest"] = "sha256:" + "2" * 64
    with pytest.raises(rehearsal.BehaviorFailure, match="forbidden_relation_change"):
        rehearsal._assert_delta("BTR-E02", before, hostile)


def test_sqlstate_admission_is_exact_and_never_uses_error_text() -> None:
    accepted = rehearsal.parent.ProcessResult(0, b"", b"")
    assert rehearsal._bounded_outcome(accepted, None)[0] is None
    rejected = rehearsal.parent.ProcessResult(
        3, b"", b"psql:<stdin>:4: ERROR:  CF603: synthetic detail\n"
    )
    observed, bounded = rehearsal._bounded_outcome(rejected, "CF603")
    assert observed == "CF603"
    assert set(bounded) == {"psql_exit", "stderr_digest"}
    with pytest.raises(rehearsal.BehaviorFailure, match="sqlstate_mismatch"):
        rehearsal._bounded_outcome(rejected, "CF601")


def test_passing_evidence_rejects_missing_duplicate_or_raw_scenario_material() -> None:
    validator = jsonschema.Draft202012Validator(EVIDENCE_SCHEMA)
    missing = _passing_evidence()
    missing["scenarios"].pop()
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(missing)
    duplicate = _passing_evidence()
    duplicate["scenarios"][1]["scenario_id"] = duplicate["scenarios"][0]["scenario_id"]
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(duplicate)
    raw = _passing_evidence()
    raw["scenarios"][0]["raw_sql"] = "SELECT secret"
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(raw)


def test_environment_stop_never_calls_docker_or_writes_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def forbidden_runner(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> rehearsal.parent.ProcessResult:
        calls.append(argv)
        raise AssertionError("runner must not be reached")

    monkeypatch.setattr(rehearsal.shutil, "which", lambda _: None)
    evidence = rehearsal.run_rehearsal(runner=forbidden_runner)
    assert evidence["result"] == "environment_unavailable"
    assert evidence["scenarios"] == []
    assert evidence["cleanup"]["status"] == "not_needed"
    assert calls == []
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)


def test_harness_has_no_provider_network_environment_or_product_runtime_import() -> (
    None
):
    source = (
        ROOT
        / "scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "import requests",
        "import httpx",
        "import socket",
        "import os",
        "os.environ",
        "google.cloud",
        "vertexai",
        "app.main",
        "sqlalchemy",
    ):
        assert forbidden not in source


def test_main_rejects_every_caller_selected_argument(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rehearsal.sys, "argv", ["harness", "--scenario", "BTR-E01"])
    assert rehearsal.main() == 2
