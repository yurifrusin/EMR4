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
FAILURE_EVIDENCE_015 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-015.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_016 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-016.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_017 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-017.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_018 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-018.json").read_text(
        encoding="utf-8"
    )
)
FAILURE_EVIDENCE_024 = json.loads(
    (DIR / "provider-free-behavior-transaction-failure-evidence-024.json").read_text(
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


def test_attempt_015_through_018_evidence_is_preserved_and_coordinate_closed() -> None:
    validator = jsonschema.Draft202012Validator(EVIDENCE_SCHEMA)
    validator.validate(FAILURE_EVIDENCE_015)
    validator.validate(FAILURE_EVIDENCE_016)
    validator.validate(FAILURE_EVIDENCE_017)
    validator.validate(FAILURE_EVIDENCE_018)

    assert FAILURE_EVIDENCE_015["environment"]["failure"] == {
        "code": "unexpected_rejection",
        "detail_digest": FAILURE_EVIDENCE_015["environment"]["failure"][
            "detail_digest"
        ],
        "function_id": "emr4_context_fabric.register_observer_generation_v1",
        "function_line": 36,
        "scenario_id": "BTR-E01",
        "sqlstate": "22P02",
        "stage": "scenario",
    }
    assert FAILURE_EVIDENCE_016["environment"]["failure"] == {
        "code": "unexpected_rejection",
        "detail_digest": FAILURE_EVIDENCE_016["environment"]["failure"][
            "detail_digest"
        ],
        "function_id": "emr4_context_fabric.register_observer_generation_v1",
        "function_line": 51,
        "scenario_id": "BTR-E01",
        "sqlstate": "CF004",
        "stage": "scenario",
    }
    assert FAILURE_EVIDENCE_017["environment"]["failure"] == {
        "code": "unexpected_rejection",
        "detail_digest": FAILURE_EVIDENCE_017["environment"]["failure"][
            "detail_digest"
        ],
        "function_id": "emr4_context_fabric.register_observer_generation_v1",
        "function_line": 58,
        "scenario_id": "BTR-E01",
        "sqlstate": "42883",
        "stage": "scenario",
    }
    assert FAILURE_EVIDENCE_018["environment"]["failure"] == {
        "code": "unexpected_rejection",
        "detail_digest": FAILURE_EVIDENCE_018["environment"]["failure"][
            "detail_digest"
        ],
        "scenario_id": "BTR-E01",
        "sqlstate": "42501",
        "stage": "scenario",
    }
    assert (
        rehearsal.parent._bytes_sha(  # noqa: SLF001
            (
                DIR / "provider-free-behavior-transaction-failure-evidence-018.json"
            ).read_bytes()
        )
        == "aeb88e2f404adb62300c0c0574b114c4254ccceb047140e75dd55eac6de61bc7"
    )
    for evidence in (
        FAILURE_EVIDENCE_015,
        FAILURE_EVIDENCE_016,
        FAILURE_EVIDENCE_017,
        FAILURE_EVIDENCE_018,
    ):
        assert evidence["scenario_reconciliation"] == {
            "expected": 20,
            "observed": 0,
            "passed": 0,
        }
        assert evidence["cleanup"]["absence_verified"] is True


def test_snapshot_query_uses_unqualified_postgresql_special_form() -> None:
    sql = rehearsal._snapshot_sql()  # noqa: SLF001

    assert "pg_catalog.coalesce" not in sql.lower()
    assert sql.count("COALESCE(") == len(rehearsal.SNAPSHOT_RELATIONS)


def test_behavior_payload_uses_valid_named_interval_construction() -> None:
    payload = rehearsal._payload(  # noqa: SLF001
        CONTRACT["fixture_namespace"], "appointment_temporal"
    )

    assert " * pg_catalog.make_interval(" not in payload
    assert "pg_catalog.make_interval(mins=>" in payload


def test_failure_024_undefined_operator_is_preserved_and_closed() -> None:
    jsonschema.Draft202012Validator(EVIDENCE_SCHEMA).validate(FAILURE_EVIDENCE_024)

    assert FAILURE_EVIDENCE_024["attempt_id"] == "556dc0541f0152f96bea4ba5"
    assert FAILURE_EVIDENCE_024["environment"]["failure"] == {
        "code": "unexpected_rejection",
        "detail_digest": "sha256:7c02450d2309736e88b3191a8618f98fc5cad1a95ca672cb0f551d2cde529216",
        "scenario_id": "BTR-E02",
        "sqlstate": "42883",
        "stage": "scenario",
    }
    assert FAILURE_EVIDENCE_024["scenario_reconciliation"] == {
        "expected": 20,
        "observed": 0,
        "passed": 0,
    }
    assert FAILURE_EVIDENCE_024["cleanup"]["absence_verified"] is True
    assert (
        rehearsal.parent._bytes_sha(  # noqa: SLF001
            (
                DIR / "provider-free-behavior-transaction-failure-evidence-024.json"
            ).read_bytes()
        )
        == "bc2efc6fffea47e8104324c822bd6c1afde28f746b05b2a5bff925dbbfe7f57b"
    )


def test_source_membership_fixture_uses_exact_accepted_full_row_digest() -> None:
    fixture = CONTRACT["fixture_namespace"]
    assert fixture["source_membership_digest_rule"] == (
        "canonical_digest_of_complete_same_locator_outbox_row"
    )
    stale = copy.deepcopy(CONTRACT)
    stale["fixture_namespace"]["source_membership_digest_rule"] = (
        "read_exact_outbox_source_contract_digest_for_same_locator"
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(CONTRACT_SCHEMA).validate(stale)
    expression = rehearsal._accepted_source_membership_digest_expression(  # noqa: SLF001
        rehearsal._canonical_bytes(  # noqa: SLF001
            rehearsal.ROOT
            / next(
                row["path"]
                for row in CONTRACT["parent_bindings"]
                if row["id"] == "inert_sql"
            )
        )
    )
    assert rehearsal.SOURCE_MEMBERSHIP_DIGEST_PROFILE in expression
    assert (
        tuple(
            field
            for field in rehearsal.SOURCE_MEMBERSHIP_FIELDS
            if f"source.{field}" in expression
        )
        == rehearsal.SOURCE_MEMBERSHIP_FIELDS
    )
    packet = rehearsal._packet(fixture)  # noqa: SLF001
    assert expression in packet
    assert "SELECT source_contract_digest FROM" not in packet
    assert "FROM emr4_context_fabric.diary_context_observation_outbox_v1 AS source" in (
        packet
    )
    probe = rehearsal._probe_sql(CONTRACT, "BTR-E03")  # noqa: SLF001
    assert expression in probe
    assert "a.source_membership_digest=o.source_contract_digest" not in probe


def test_source_membership_digest_profile_and_operand_drift_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_json = rehearsal._json  # noqa: SLF001
    original_body = original_json(rehearsal.BODY_CONTRACT_PATH)

    def digest_node(body: dict[str, Any]) -> dict[str, Any]:
        program = next(
            row
            for row in body["body_programs"]
            if row["id"] == "emr4_context_fabric.admit_proofread_observation_v1"
        )
        return next(
            node
            for node in rehearsal._walk_nodes(program["ast"])  # noqa: SLF001
            if node.get("op") == "CANONICAL_DIGEST"
            and node.get("profile") == rehearsal.SOURCE_MEMBERSHIP_DIGEST_PROFILE
        )

    hostile_profile = copy.deepcopy(original_body)
    digest_node(hostile_profile)["profile"] = "emr4_context_fabric.wrong_profile_v1"
    hostile_missing_field = copy.deepcopy(original_body)
    digest_node(hostile_missing_field)["operands"].pop()
    hostile_relation = copy.deepcopy(original_body)
    digest_node(hostile_relation)["operands"][0]["relation"] = (
        "emr4_context_fabric.context_proofread_observation_admission"
    )

    for hostile_body, expected in (
        (hostile_profile, "source_membership_digest_population"),
        (hostile_missing_field, "source_membership_digest_definition"),
        (hostile_relation, "source_membership_digest_definition"),
    ):
        monkeypatch.setattr(
            rehearsal,
            "_json",
            lambda path, value=hostile_body: (
                copy.deepcopy(value)
                if path == rehearsal.BODY_CONTRACT_PATH
                else original_json(path)
            ),
        )
        with pytest.raises(rehearsal.BehaviorFailure, match=expected):
            rehearsal._accepted_source_membership_digest_expression()  # noqa: SLF001

    monkeypatch.setattr(rehearsal, "_json", original_json)
    with pytest.raises(
        rehearsal.BehaviorFailure, match="source_membership_digest_lowering"
    ):
        rehearsal._accepted_source_membership_digest_expression(b"")  # noqa: SLF001


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


def test_bootstrap_seeds_exact_alpha_registry_barrier_outside_role_behavior() -> None:
    sql = rehearsal.render_bootstrap_sql(CONTRACT).decode("utf-8")
    alpha_prefix = sql[: sql.index("WITH beta_barrier AS (")]
    relation = "emr4_context_fabric.context_generation_registry_barrier"

    assert alpha_prefix.count(f"INSERT INTO {relation}") == 1
    assert CONTRACT["fixture_namespace"]["practice_alpha"] in alpha_prefix
    assert CONTRACT["fixture_namespace"]["stream_alpha"] in alpha_prefix
    assert "barrier_revision,updated_at" in alpha_prefix
    assert ",0,pg_catalog.transaction_timestamp());" in alpha_prefix
    assert rehearsal.EXPECTED_DELTAS["BTR-E01"][relation] == 0
    assert relation in rehearsal.ALLOWED_DIGEST_CHANGES["BTR-E01"]


def test_registration_probe_requires_one_barrier_advanced_exactly_three_times() -> None:
    sql = rehearsal._probe_sql(CONTRACT, "BTR-E01")  # noqa: SLF001

    assert "context_generation_registry_barrier" in sql
    assert "count(*)=1" in sql
    assert "min(barrier_revision)=3" in sql
    assert "max(barrier_revision)=3" in sql


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
            "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
            "durability-parse-catalogue-rehearsal/provider-free-disposable-"
            "postgresql-evidence-outbox-select-rls-exact-reproduction.json"
        ),
        "source_head": "6a6088e525762c456c6df7fcba5c8377a94fb2ca",
        "sha256": (
            "sha256:b0ce639981a5822e9e66ebbb81cab74009b3ebe368f3d9e6efd75cfd32453386"
        ),
    }
    assert bindings["inert_sql"]["source_head"] == (
        "497a4d1fe5b58fa4bcc03747abb3d389c3b51899"
    )
    assert bindings["inert_sql"]["sha256"] == (
        "sha256:265ce41ec4c3b318cc42c544ab06ebb0fcc67904072b0f8406af4ec8ddec6b0a"
    )
    assert bindings["render_manifest"]["source_head"] == (
        "497a4d1fe5b58fa4bcc03747abb3d389c3b51899"
    )
    assert bindings["render_manifest"]["sha256"] == (
        "sha256:559a66e508c2a38dbfc037d3e1df482cff7106dc09ff35001b55afc63b119cbf"
    )
    assert bindings["structural_contract"] == {
        "id": "structural_contract",
        "path": (
            "orchestration/continuity/raisa-provider-free-unmounted-"
            "durability-migration-transaction-architecture/"
            "migration-transaction-architecture-contract.json"
        ),
        "source_head": "e1ca28915b09636e5d9d693216beef450f71a356",
        "sha256": (
            "sha256:d333ad3ef75725a8a85e7d45a072bca02a087ea869d395459140c405919814c6"
        ),
    }
    assert bindings["parse_prerequisite_contract"]["source_head"] == (
        "1fd3445aea5839b7aa889fc962faa8ad2be0c95e"
    )
    assert bindings["body_contract"] == {
        "id": "body_contract",
        "path": (
            "orchestration/continuity/raisa-provider-free-unmounted-"
            "durability-function-trigger-body-architecture/"
            "function-trigger-body-architecture-contract.json"
        ),
        "source_head": "1a06961916bcf73d553eb401eb08094aa4c45e20",
        "sha256": (
            "sha256:c88653b1db1e379e9d067dbe444a1c2cbdf0dd1dd148fe838bce274741f7c455"
        ),
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
    registration = rehearsal.render_scenario_sql(CONTRACT, "BTR-E01").decode("utf-8")
    conflict = rehearsal.render_scenario_sql(CONTRACT, "BTR-I02").decode("utf-8")

    assert registration.count("BEGIN ISOLATION LEVEL SERIALIZABLE;") == 3
    assert conflict.count("BEGIN ISOLATION LEVEL READ COMMITTED;") == 3
    for sql in (registration, conflict):
        assert sql.count("COMMIT;") == 3
        assert sql.count("SET SESSION AUTHORIZATION") == 1


def test_transition_scenarios_emit_one_exact_transaction_local_result_marker() -> None:
    for scenario_id, expected in rehearsal.EXPECTED_TRANSITION_RESULT_KINDS.items():
        sql = rehearsal.render_scenario_sql(CONTRACT, scenario_id).decode("utf-8")
        assert sql.count(rehearsal.TRANSITION_RESULT_MARKER) == 1
        assert sql.count("apply_durability_transition_v1") == 1
        assert "WITH transition_result AS MATERIALIZED" in sql
        assert f"'scenario_id','{scenario_id}'" in sql
        assert f"'expected_result_kind','{expected}'" in sql
        assert f"CASE WHEN result_kind='{expected}' THEN 1 ELSE 0 END" in sql
        assert sql.index(rehearsal.TRANSITION_RESULT_MARKER) < sql.index("COMMIT;")
    rollback = rehearsal.render_scenario_sql(CONTRACT, "BTR-B03").decode("utf-8")
    assert rollback.index(rehearsal.TRANSITION_RESULT_MARKER) < rollback.index(
        "fixed_injected_rollback"
    )


def test_transition_result_hardening_does_not_widen_relation_deltas() -> None:
    assert (
        "emr4_context_fabric.context_observer_generation"
        not in (rehearsal.ALLOWED_DIGEST_CHANGES["BTR-E04"])
    )


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


def test_role_matrix_uses_nine_fresh_fixed_denial_connections() -> None:
    matrix = rehearsal.render_role_matrix(CONTRACT)
    assert [name for name, _ in matrix] == [
        "producer_direct_fabric_dml",
        "observer_foreign_entry_point",
        "producer_trigger_execute",
        "observer_set_role",
        "application_read_direct_update",
        "coordinator_admission_direct_update",
        "coordinator_recovery_anchor_direct_update",
        "lifecycle_recovery_anchor_direct_update",
        "coordinator_outbox_direct_select",
    ]
    for _, raw in matrix:
        sql = raw.decode("utf-8")
        assert sql.count("SET SESSION AUTHORIZATION") == 1
        assert sql.count("BEGIN ISOLATION LEVEL READ COMMITTED;") == 1
    admission_operation, admission_raw = matrix[-4]
    admission_sql = admission_raw.decode("utf-8")
    assert admission_operation == "coordinator_admission_direct_update"
    assert (
        "UPDATE emr4_context_fabric.context_proofread_observation_admission"
        in admission_sql
    )
    assert "SET decision=decision" in admission_sql
    assert CONTRACT["fixture_namespace"]["observer_happy"] in admission_sql
    for operation, raw in matrix[-3:-1]:
        sql = raw.decode("utf-8")
        assert operation.endswith("recovery_anchor_direct_update")
        assert "UPDATE emr4_context_fabric.context_recovery_anchor" in sql
        assert CONTRACT["fixture_namespace"]["practice_alpha"] in sql
        assert CONTRACT["fixture_namespace"]["stream_alpha"] in sql
    outbox_operation, outbox_raw = matrix[-1]
    assert outbox_operation == "coordinator_outbox_direct_select"
    assert (
        "SELECT count(*) FROM emr4_context_fabric.diary_context_observation_outbox_v1;"
    ) in outbox_raw.decode("utf-8")


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


def _transition_marker(scenario_id: str, result_kind: str, assertion: Any = 1) -> bytes:
    return (
        json.dumps(
            {
                "marker": rehearsal.TRANSITION_RESULT_MARKER,
                "scenario_id": scenario_id,
                "result_kind": result_kind,
                "expected_result_kind": rehearsal.EXPECTED_TRANSITION_RESULT_KINDS[
                    scenario_id
                ],
                "assertion": assertion,
            },
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
    )


def test_transition_result_marker_releases_only_exact_typed_outcomes() -> None:
    applied = rehearsal.parent.ProcessResult(
        0, _transition_marker("BTR-E04", "RECEIPT_APPLIED"), b""
    )
    observed, transport = rehearsal._bounded_outcome(applied, None, "BTR-E04")
    assert observed is None
    assert transport["result_kind"] == "RECEIPT_APPLIED"

    replayed = rehearsal.parent.ProcessResult(
        0, _transition_marker("BTR-I03", "RECEIPT_REPLAYED"), b""
    )
    assert (
        rehearsal._bounded_outcome(replayed, None, "BTR-I03")[1]["result_kind"]
        == "RECEIPT_REPLAYED"
    )

    rollback = rehearsal.parent.ProcessResult(
        3,
        _transition_marker("BTR-B03", "RECEIPT_APPLIED"),
        b"psql:<stdin>:4: ERROR:  P0001: fixed_injected_rollback\n",
    )
    observed, transport = rehearsal._bounded_outcome(rollback, "P0001", "BTR-B03")
    assert observed == "P0001"
    assert transport["result_kind"] == "RECEIPT_APPLIED"


def test_transition_result_marker_fails_closed_on_hostile_shapes() -> None:
    missing = rehearsal.parent.ProcessResult(0, b"", b"")
    with pytest.raises(rehearsal.BehaviorFailure, match="transition_result_missing"):
        rehearsal._bounded_outcome(missing, None, "BTR-E04")

    marker = _transition_marker("BTR-E04", "RECEIPT_APPLIED")
    duplicate = rehearsal.parent.ProcessResult(0, marker + marker, b"")
    with pytest.raises(rehearsal.BehaviorFailure, match="transition_result_duplicate"):
        rehearsal._bounded_outcome(duplicate, None, "BTR-E04")

    wrong = rehearsal.parent.ProcessResult(
        0, _transition_marker("BTR-E04", "RECEIPT_REPLAYED"), b""
    )
    with pytest.raises(rehearsal.BehaviorFailure, match="transition_result_mismatch"):
        rehearsal._bounded_outcome(wrong, None, "BTR-E04")

    boolean_assertion = rehearsal.parent.ProcessResult(
        0, _transition_marker("BTR-E04", "RECEIPT_APPLIED", True), b""
    )
    with pytest.raises(rehearsal.BehaviorFailure, match="transition_result_mismatch"):
        rehearsal._bounded_outcome(boolean_assertion, None, "BTR-E04")

    malformed = rehearsal.parent.ProcessResult(
        0, b'{"marker":"emr4.behavior.transition_result.v1"\n', b""
    )
    with pytest.raises(rehearsal.BehaviorFailure, match="transition_result_malformed"):
        rehearsal._bounded_outcome(malformed, None, "BTR-E04")

    unexpected = rehearsal.parent.ProcessResult(0, marker, b"")
    with pytest.raises(rehearsal.BehaviorFailure, match="transition_result_unexpected"):
        rehearsal._bounded_outcome(unexpected, None, "BTR-E01")


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
