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
FAILURE_EVIDENCE_002 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-002.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_003 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-003.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_004 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-004.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_005 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-005.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_006 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-006.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_007 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-007.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_008 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-008.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_009 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-009.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_010 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-010.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_011 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-011.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_012 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-012.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_013 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-013.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_014 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-014.json").read_text(
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
                "isolation": (
                    "serializable"
                    if scenario["id"] in rehearsal.SERIALIZABLE_SCENARIOS
                    else "read committed"
                ),
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
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(FAILURE_EVIDENCE_002)
    assert FAILURE_EVIDENCE_002["environment"]["failure"]["stage"] == "fixture"
    assert FAILURE_EVIDENCE_002["environment"]["failure"]["code"] == (
        "bootstrap_failed"
    )
    assert FAILURE_EVIDENCE_002["scenario_reconciliation"]["observed"] == 0
    assert FAILURE_EVIDENCE_002["cleanup"]["absence_verified"] is True
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(FAILURE_EVIDENCE_003)
    assert FAILURE_EVIDENCE_003["environment"]["failure"]["stage"] == "fixture"
    assert FAILURE_EVIDENCE_003["environment"]["failure"]["code"] == (
        "bootstrap_failed"
    )
    assert FAILURE_EVIDENCE_003["scenario_reconciliation"]["observed"] == 0
    assert FAILURE_EVIDENCE_003["cleanup"]["absence_verified"] is True
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(FAILURE_EVIDENCE_004)
    assert FAILURE_EVIDENCE_004["environment"]["failure"] == {
        "code": "bootstrap_failed",
        "detail_digest": FAILURE_EVIDENCE_004["environment"]["failure"][
            "detail_digest"
        ],
        "sqlstate": "23502",
        "stage": "fixture",
    }
    assert FAILURE_EVIDENCE_004["scenario_reconciliation"]["observed"] == 0
    assert FAILURE_EVIDENCE_004["cleanup"]["absence_verified"] is True
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(FAILURE_EVIDENCE_005)
    assert FAILURE_EVIDENCE_005["environment"]["failure"]["sqlstate"] == "23502"
    assert "coordinate_status" not in FAILURE_EVIDENCE_005["environment"]["failure"]
    assert FAILURE_EVIDENCE_005["scenario_reconciliation"]["observed"] == 0
    assert FAILURE_EVIDENCE_005["cleanup"]["absence_verified"] is True
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(FAILURE_EVIDENCE_006)
    assert FAILURE_EVIDENCE_006["environment"]["failure"]["sqlstate"] == "23502"
    assert FAILURE_EVIDENCE_006["environment"]["failure"]["coordinate_status"] == (
        "missing"
    )
    assert FAILURE_EVIDENCE_006["scenario_reconciliation"]["observed"] == 0
    assert FAILURE_EVIDENCE_006["cleanup"]["absence_verified"] is True
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(FAILURE_EVIDENCE_007)
    assert FAILURE_EVIDENCE_007["environment"]["failure"]["sqlstate"] == "23502"
    assert FAILURE_EVIDENCE_007["environment"]["failure"]["coordinate_status"] == (
        "missing"
    )
    assert FAILURE_EVIDENCE_007["scenario_reconciliation"]["observed"] == 0
    assert FAILURE_EVIDENCE_007["cleanup"]["absence_verified"] is True
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(FAILURE_EVIDENCE_008)
    assert FAILURE_EVIDENCE_008["environment"]["failure"] == {
        "code": "catalogue_delta",
        "detail_digest": rehearsal._sha256(  # noqa: SLF001
            b"application_relations,relation_acl"
        ),
        "stage": "fixture",
    }
    assert FAILURE_EVIDENCE_008["lifecycle"][-1] == "cleanup_verified"
    assert FAILURE_EVIDENCE_008["scenario_reconciliation"] == {
        "expected": 20,
        "observed": 0,
        "passed": 0,
    }
    assert FAILURE_EVIDENCE_008["cleanup"]["absence_verified"] is True
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(FAILURE_EVIDENCE_009)
    assert FAILURE_EVIDENCE_009["environment"]["failure"] == {
        "code": "query_failed",
        "detail_digest": rehearsal._sha256(b"3"),  # noqa: SLF001
        "stage": "catalogue",
    }
    assert FAILURE_EVIDENCE_009["lifecycle"][-2:] == [
        "fixtures_closed",
        "cleanup_verified",
    ]
    assert FAILURE_EVIDENCE_009["scenario_reconciliation"]["observed"] == 0
    assert FAILURE_EVIDENCE_009["cleanup"]["absence_verified"] is True


def test_snapshot_query_failure_releases_only_bounded_site_and_sqlstate() -> None:
    captured: dict[str, Any] = {}

    def runner(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> rehearsal.parent.ProcessResult:
        captured.update(argv=argv, stdin=stdin, timeout=timeout, cap=cap)
        return rehearsal.parent.ProcessResult(
            3,
            b"",
            b"psql:<stdin>:2: ERROR:  42883: prohibited detail\n",
        )

    profile = rehearsal._profile()  # noqa: SLF001
    with pytest.raises(rehearsal.BehaviorFailure) as raised:
        rehearsal._query_json_bounded(  # noqa: SLF001
            runner,
            r"C:\Docker\docker.exe",
            "a" * 64,
            profile["postgres_database"],
            profile,
            "SELECT '{}'::json::text",
            query_id="scenario_snapshot",
        )

    assert raised.value.stage == "readback"
    assert raised.value.code == "query_failed"
    assert raised.value.detail == {
        "query_id": "scenario_snapshot",
        "sqlstate": "42883",
    }
    assert captured["stdin"].startswith(b"SET TRANSACTION READ ONLY;\n")
    assert "--file=-" in captured["argv"]


def test_snapshot_query_uses_unqualified_postgresql_special_form() -> None:
    sql = rehearsal._snapshot_sql()  # noqa: SLF001

    assert "pg_catalog.coalesce" not in sql.lower()
    assert sql.count("COALESCE(") == len(rehearsal.SNAPSHOT_RELATIONS)


def test_snapshot_undefined_function_failure_is_preserved_and_closed() -> None:
    evidence = FAILURE_EVIDENCE_010
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)

    assert evidence["environment"]["failure"] == {
        "code": "query_failed",
        "detail_digest": evidence["environment"]["failure"]["detail_digest"],
        "query_id": "scenario_snapshot",
        "sqlstate": "42883",
        "stage": "readback",
    }
    assert evidence["lifecycle"][-2:] == ["fixtures_closed", "cleanup_verified"]
    assert evidence["scenario_reconciliation"]["observed"] == 0
    assert evidence["cleanup"]["absence_verified"] is True


def test_snapshot_query_id_schema_rejects_every_other_value() -> None:
    evidence = copy.deepcopy(FAILURE_EVIDENCE_010)
    evidence["environment"]["failure"]["query_id"] = "caller_selected_query"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)


def test_catalogue_deltas_separate_fixture_rows_from_structural_drift() -> None:
    before = {
        "application_relations": [{"name": "public.appointments", "row_count": 0}],
        "relation_acl": [],
        "types": [{"name": "synthetic", "domain_not_null": False}],
    }
    fixture = copy.deepcopy(before)
    fixture["application_relations"][0]["row_count"] = 1
    fixture["relation_acl"] = [{"relation": "public.appointments"}]

    fixture_digests = rehearsal._assert_fixture_catalogue_delta(  # noqa: SLF001
        before, fixture
    )
    assert rehearsal.EXPECTED_FIXTURE_CATALOGUE_CHANGES == {
        "application_relations",
        "relation_acl",
    }

    final = copy.deepcopy(fixture)
    final["application_relations"][0]["row_count"] = 2
    rehearsal._assert_post_behavior_catalogue_stability(  # noqa: SLF001
        fixture_digests, final
    )

    hostile = copy.deepcopy(final)
    hostile["types"][0]["domain_not_null"] = True
    with pytest.raises(rehearsal.BehaviorFailure, match="post_behavior_drift"):
        rehearsal._assert_post_behavior_catalogue_stability(  # noqa: SLF001
            fixture_digests, hostile
        )


def test_bootstrap_failure_telemetry_releases_only_one_safe_sqlstate() -> None:
    result = rehearsal.parent.ProcessResult(
        3,
        b"",
        b"psql:<stdin>:19: ERROR:  23503: synthetic detail must not escape\n",
    )
    assert rehearsal._safe_sqlstate(result) == "23503"

    ambiguous = rehearsal.parent.ProcessResult(
        3,
        b"ERROR:  23503: first\n",
        b"ERROR:  42501: second\n",
    )
    assert rehearsal._safe_sqlstate(ambiguous) is None
    assert (
        rehearsal._safe_sqlstate(
            rehearsal.parent.ProcessResult(3, b"patient-shaped prose", b"")
        )
        is None
    )

    evidence = _passing_evidence()
    evidence["result"] = "rehearsal_failed"
    evidence["environment"]["failure"] = {
        "stage": "fixture",
        "code": "bootstrap_failed",
        "detail_digest": "sha256:" + "0" * 64,
        "sqlstate": "23503",
    }
    evidence["lifecycle"] = ["cleanup_verified"]
    evidence["preconditions"] = []
    evidence["scenarios"] = []
    evidence["scenario_reconciliation"] = {
        "expected": 20,
        "observed": 0,
        "passed": 0,
    }
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)


def test_bootstrap_diagnostic_metadata_is_exactly_allowlisted() -> None:
    accepted = rehearsal.parent.ProcessResult(
        3,
        b"",
        (
            b"psql:<stdin>:19: ERROR:  23502: prohibited message\n"
            b"SCHEMA NAME:  emr4_context_fabric\n"
            b"TABLE NAME:  context_durability_checkpoint\n"
            b"COLUMN NAME:  audit_head_digest\n"
        ),
    )
    assert rehearsal._safe_bootstrap_failure_metadata(accepted) == {
        "sqlstate": "23502",
        "coordinate_status": "released",
        "relation": "emr4_context_fabric.context_durability_checkpoint",
        "column": "audit_head_digest",
    }

    unlisted = rehearsal.parent.ProcessResult(
        3,
        b"",
        (
            b"ERROR:  23502: prohibited message\n"
            b"SCHEMA NAME:  private\nTABLE NAME:  patient\nCOLUMN NAME:  name\n"
        ),
    )
    assert rehearsal._safe_bootstrap_failure_metadata(unlisted) == {
        "sqlstate": "23502",
        "coordinate_status": "unlisted_relation",
    }

    ambiguous = rehearsal.parent.ProcessResult(
        3,
        b"",
        (
            b"ERROR:  23502: prohibited message\n"
            b"SCHEMA NAME:  public\nSCHEMA NAME:  emr4_context_fabric\n"
            b"TABLE NAME:  appointments\nCOLUMN NAME:  id\n"
        ),
    )
    assert rehearsal._safe_bootstrap_failure_metadata(ambiguous) == {
        "sqlstate": "23502",
        "coordinate_status": "ambiguous",
    }

    missing = rehearsal.parent.ProcessResult(
        3, b"", b"ERROR:  23502: prohibited message\n"
    )
    assert rehearsal._safe_bootstrap_failure_metadata(missing) == {
        "sqlstate": "23502",
        "coordinate_status": "missing",
    }

    header_only = rehearsal.parent.ProcessResult(
        3,
        b"",
        (
            b"psql:<stdin>:19: ERROR:  23502: null value in column "
            b'"audit_head_digest" of relation "context_durability_checkpoint" '
            b"violates not-null constraint\n"
        ),
    )
    assert rehearsal._safe_bootstrap_failure_metadata(header_only) == {
        "sqlstate": "23502",
        "coordinate_status": "released",
        "relation": "emr4_context_fabric.context_durability_checkpoint",
        "column": "audit_head_digest",
    }

    header_unlisted = rehearsal.parent.ProcessResult(
        3,
        b"",
        (
            b'ERROR:  23502: null value in column "name" of relation '
            b'"patient" violates not-null constraint\n'
        ),
    )
    assert rehearsal._safe_bootstrap_failure_metadata(header_unlisted) == {
        "sqlstate": "23502",
        "coordinate_status": "unlisted_relation",
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


def test_bootstrap_closes_beta_projection_foreign_key_topology() -> None:
    sql = rehearsal.render_bootstrap_sql(CONTRACT).decode("utf-8")

    ctes = [
        "WITH beta_barrier AS (",
        "), beta_generation AS (",
        "), beta_checkpoint AS (",
        "), beta_frame AS (",
        "), beta_watermark AS (",
        "), beta_obligation AS (",
    ]
    offsets = [sql.index(cte) for cte in ctes]
    assert offsets == sorted(offsets)
    assert "FROM beta_barrier" in sql
    assert sql.count("FROM beta_checkpoint") == 2
    assert "FROM beta_frame" in sql
    assert "last_contiguous_position,last_observation_digest,lifecycle_revision" in sql


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
    bindings = {row["id"]: row for row in contract["parent_bindings"]}
    assert bindings["accepted_runtime_source"] == {
        "id": "accepted_runtime_source",
        "path": (
            "docs/raisa-provider-free-disposable-postgresql-durability-"
            "parse-catalogue-row-composite-projection-order-rebind-closeout.md"
        ),
        "source_head": "2f0047cd90a8448ec4e738483a7237fbf2860bcb",
        "sha256": (
            "sha256:b78536969ce420332974a9ac2a404b1560d9cdb6da233185691987916c7a9940"
        ),
    }
    assert bindings["inert_sql"]["source_head"] == (
        "0931f3e658f06e02e7de4c5ea02238184da9e767"
    )
    assert bindings["inert_sql"]["sha256"] == (
        "sha256:83359fbc0cf2fb8f7d147b5dc820aa28910129428c9727daa1e1dc0259ce73f5"
    )
    assert bindings["render_manifest"]["sha256"] == (
        "sha256:66c103adac8c9ba52440077e25d2f3fc58ed6d30005576034bb42115c746dd71"
    )


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
    registration = rehearsal.render_scenario_sql(CONTRACT, "BTR-E01").decode("utf-8")
    conflict = rehearsal.render_scenario_sql(CONTRACT, "BTR-I02").decode("utf-8")

    assert registration.count("BEGIN ISOLATION LEVEL SERIALIZABLE;") == 3
    assert conflict.count("BEGIN ISOLATION LEVEL READ COMMITTED;") == 3
    for sql in (registration, conflict):
        assert sql.count("COMMIT;") == 3
        assert sql.count("SET SESSION AUTHORIZATION") == 1


def test_entry_point_isolation_matches_parent_fail_closed_guards() -> None:
    for scenario in CONTRACT["scenarios"]:
        if scenario["id"] == "BTR-R03":
            continue
        sql = rehearsal.render_scenario_sql(CONTRACT, scenario["id"]).decode("utf-8")
        expected = (
            "SERIALIZABLE"
            if scenario["id"] in rehearsal.SERIALIZABLE_SCENARIOS
            else "READ COMMITTED"
        )
        assert f"BEGIN ISOLATION LEVEL {expected}" in sql
        assert ("serializable" in scenario["transaction_shape"]) == (
            scenario["id"] in rehearsal.SERIALIZABLE_SCENARIOS
        )


def test_isolation_mismatch_failure_is_preserved_and_cleaned_up() -> None:
    evidence = FAILURE_EVIDENCE_012
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)

    assert evidence["environment"]["failure"] == {
        "code": "unexpected_rejection",
        "detail_digest": "sha256:a2e676f192b59e7ba720d3544883451fbbd0034f0ccde3787dbbe71c0c5dad31",
        "scenario_id": "BTR-E01",
        "sqlstate": "CF303",
        "stage": "scenario",
    }
    assert evidence["scenario_reconciliation"]["observed"] == 0
    assert evidence["cleanup"]["absence_verified"] is True


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
    assert rehearsal._bounded_outcome(accepted, None, "BTR-E01")[0] is None
    rejected = rehearsal.parent.ProcessResult(
        3, b"", b"psql:<stdin>:4: ERROR:  CF603: synthetic detail\n"
    )
    observed, bounded = rehearsal._bounded_outcome(rejected, "CF603", "BTR-T01")
    assert observed == "CF603"
    assert set(bounded) == {"psql_exit", "stderr_digest"}
    with pytest.raises(rehearsal.BehaviorFailure, match="sqlstate_mismatch"):
        rehearsal._bounded_outcome(rejected, "CF601", "BTR-T02")


def test_expected_success_rejection_releases_only_scenario_and_sqlstate() -> None:
    rejected = rehearsal.parent.ProcessResult(
        3,
        b"",
        b"psql:<stdin>:4: ERROR:  42883: synthetic detail\n",
    )

    with pytest.raises(rehearsal.BehaviorFailure) as caught:
        rehearsal._bounded_outcome(rejected, None, "BTR-E01")

    assert caught.value.stage == "scenario"
    assert caught.value.code == "unexpected_rejection"
    assert caught.value.detail == {"scenario_id": "BTR-E01", "sqlstate": "42883"}


def test_expected_success_rejection_releases_one_allowlisted_function_coordinate() -> (
    None
):
    rejected = rehearsal.parent.ProcessResult(
        3,
        b"",
        (
            b"psql:<stdin>:4: ERROR:  22P02: prohibited detail\n"
            b"CONTEXT:  PL/pgSQL function "
            b"emr4_context_fabric.register_observer_generation_v1("
            b"emr4_context_fabric.generation_registration_v1) line 62 "
            b"at assignment\n"
        ),
    )

    with pytest.raises(rehearsal.BehaviorFailure) as caught:
        rehearsal._bounded_outcome(rejected, None, "BTR-E01")

    assert caught.value.detail == {
        "scenario_id": "BTR-E01",
        "sqlstate": "22P02",
        "function_id": ("emr4_context_fabric.register_observer_generation_v1"),
        "function_line": 62,
    }

    assert rehearsal._safe_plpgsql_coordinate(rejected, "BTR-E02") == {}
    unqualified = rehearsal.parent.ProcessResult(
        3,
        b"",
        (
            b"psql:<stdin>:4: ERROR:  22P02: prohibited detail\n"
            b"CONTEXT:  PL/pgSQL function register_observer_generation_v1("
            b"generation_registration_v1) line 62 at assignment\n"
        ),
    )
    assert rehearsal._safe_plpgsql_coordinate(unqualified, "BTR-E01") == {
        "function_id": "emr4_context_fabric.register_observer_generation_v1",
        "function_line": 62,
    }
    foreign_schema = rehearsal.parent.ProcessResult(
        3,
        b"",
        rejected.stderr.replace(
            b"emr4_context_fabric.register_observer_generation_v1",
            b"other_schema.register_observer_generation_v1",
        ),
    )
    assert rehearsal._safe_plpgsql_coordinate(foreign_schema, "BTR-E01") == {}
    ambiguous = rehearsal.parent.ProcessResult(
        3,
        b"",
        rejected.stderr
        + (
            b"CONTEXT:  PL/pgSQL function "
            b"emr4_context_fabric.register_observer_generation_v1("
            b"emr4_context_fabric.generation_registration_v1) line 63 "
            b"at SQL statement\n"
        ),
    )
    assert rehearsal._safe_plpgsql_coordinate(ambiguous, "BTR-E01") == {}


def test_failure_013_and_function_coordinate_schema_are_closed() -> None:
    validator = jsonschema.Draft202012Validator(EVIDENCE_SCHEMA)
    validator.validate(FAILURE_EVIDENCE_013)
    assert FAILURE_EVIDENCE_013["environment"]["failure"] == {
        "code": "unexpected_rejection",
        "detail_digest": "sha256:4d59e386927664a7cd53f6c2343d5addb718bc35958d1d531eaa775b45fba17b",
        "scenario_id": "BTR-E01",
        "sqlstate": "22P02",
        "stage": "scenario",
    }
    assert FAILURE_EVIDENCE_013["cleanup"]["absence_verified"] is True
    validator.validate(FAILURE_EVIDENCE_014)
    assert FAILURE_EVIDENCE_014["environment"]["failure"] == {
        "code": "unexpected_rejection",
        "detail_digest": "sha256:4d59e386927664a7cd53f6c2343d5addb718bc35958d1d531eaa775b45fba17b",
        "scenario_id": "BTR-E01",
        "sqlstate": "22P02",
        "stage": "scenario",
    }
    assert FAILURE_EVIDENCE_014["cleanup"]["absence_verified"] is True

    admitted = copy.deepcopy(FAILURE_EVIDENCE_013)
    admitted["environment"]["failure"].update(
        function_id="emr4_context_fabric.register_observer_generation_v1",
        function_line=62,
    )
    validator.validate(admitted)

    hostile = copy.deepcopy(admitted)
    hostile["environment"]["failure"]["function_id"] = (
        "emr4_context_fabric.caller_selected_function"
    )
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(hostile)

    hostile = copy.deepcopy(admitted)
    hostile["environment"]["failure"]["function_line"] = "62; SELECT secret"
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(hostile)


def test_first_scenario_rejection_is_preserved_and_cleaned_up() -> None:
    evidence = FAILURE_EVIDENCE_011
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)

    assert evidence["environment"]["failure"] == {
        "code": "unexpected_rejection",
        "detail_digest": "sha256:"
        + "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "stage": "scenario",
    }
    assert evidence["lifecycle"][-2:] == ["fixtures_closed", "cleanup_verified"]
    assert evidence["scenario_reconciliation"]["observed"] == 0
    assert evidence["cleanup"]["absence_verified"] is True


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
