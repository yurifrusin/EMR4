from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import pytest
from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-plan.md"
)
DESIGN = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-design.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-threat-model-delta.md"
)
BASE = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal"
)
CONTRACT = BASE / "concurrency-rehearsal-contract.json"
SCHEMA = BASE / "concurrency-rehearsal-contract.schema.json"

EXPECTED_ORDER = [
    "CFD1-C01",
    "CFD1-C02",
    "CFD1-C03",
    "CFD1-C04",
    "CFD1-C05",
    "CFD1-C06",
]
EXPECTED_COVERAGE = {
    "REGISTRATION": 1,
    "PRODUCER": 1,
    "ADMISSION": 2,
    "COORDINATOR": 2,
    "total": 6,
}
EXPECTED_PARENT_BINDINGS = {
    "accepted_serial_pass_evidence": (
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence-admission-replay-recovery-pass.json",
        "26c6dec802e46dec055c1c42aecc97df9942180014fc9fa410f96e1305798200",
    ),
    "current_serial_contract": (
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/behavior-transaction-rehearsal-contract.json",
        "273856de0d66dc58169c1f5fb2e933ae0171ddd95ccb1e1b37de3a77ca27a220",
    ),
    "current_serial_evidence_schema": (
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.schema.json",
        "d946d8aa9bc763892a9f724ffc8de1413519fc1e172b1bf5a55f57335b93d3fd",
    ),
    "current_serial_harness": (
        "scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py",
        "83ee8865e984603851b46469ef32d4367bdf7a07a489aa6e76f441da5c01cb02",
    ),
    "accepted_serial_closeout": (
        "docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-closeout.md",
        "86192f5587d9eb37f427f3196d96381bf57d094221e28a967ee68037ff4075fa",
    ),
    "accepted_serial_sol_acceptance": (
        "orchestration/agent_inbox/codex/raisa-context-fabric-durability-behavior-transaction-rehearsal-sol-acceptance.md",
        "1afeb63d4958d927f1dbf5920002d0a3ffcbf7e9bc1828c15048add56131d682",
    ),
    "inert_sql": (
        "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert",
        "dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7",
    ),
    "render_manifest": (
        "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json",
        "2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271",
    ),
}


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _contract() -> dict[str, Any]:
    return _json(CONTRACT)


def _validator() -> Draft202012Validator:
    schema = _json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _flat(*paths: Path) -> str:
    return " ".join(
        "\n".join(path.read_text(encoding="utf-8") for path in paths).split()
    ).lower()


def _assert_semantics(candidate: dict[str, Any]) -> None:
    _validator().validate(candidate)
    assert candidate["scenario_order"] == EXPECTED_ORDER
    scenarios = candidate["scenarios"]
    assert [scenario["id"] for scenario in scenarios] == EXPECTED_ORDER
    counts = Counter(scenario["category"] for scenario in scenarios)
    assert {**counts, "total": len(scenarios)} == EXPECTED_COVERAGE
    assert candidate["category_coverage"] == EXPECTED_COVERAGE

    by_id = {scenario["id"]: scenario for scenario in scenarios}
    assert {
        scenario_id
        for scenario_id, scenario in by_id.items()
        if scenario["isolation"] == "serializable"
    } == {"CFD1-C01", "CFD1-C05", "CFD1-C06"}
    assert by_id["CFD1-C01"]["contender_sqlstate"] == "40001"
    assert by_id["CFD1-C04"]["contender_sqlstate"] == "CF004"
    assert by_id["CFD1-C05"]["contender_sqlstate"] == "40001"
    assert by_id["CFD1-C06"]["leader_outcome"] == "ROLLBACK_INJECTED"
    assert by_id["CFD1-C06"]["contender_outcome"] == "COMMIT_PASS"

    for scenario in scenarios:
        assert scenario["principal"].startswith("context_")
        if scenario["contender_outcome"] in {
            "COMMIT_PASS",
            "COMMIT_IDEMPOTENT_REPLAY",
        }:
            assert scenario["contender_sqlstate"] is None
        else:
            assert scenario["contender_sqlstate"] is not None

    sync = candidate["synchronization_profile"]
    assert sync == {
        "leader_hold": "fixed_pg_sleep_after_target_function_before_transaction_end",
        "leader_hold_milliseconds": 1500,
        "leader_required_wait_event_type": "Timeout",
        "leader_required_wait_event": "PgSleep",
        "contender_required_wait_event_type": "Lock",
        "poll_interval_milliseconds": 25,
        "overlap_observation_ceiling_milliseconds": 1000,
        "statement_timeout_milliseconds": 8000,
        "lock_timeout_milliseconds": 5000,
        "idle_in_transaction_timeout_milliseconds": 8000,
        "participant_retry_count": 0,
        "raw_activity_fields_retained": [],
    }
    runtime = candidate["runtime_profile"]
    assert runtime["network_mode"] == "none"
    assert runtime["published_ports"] == 0
    assert runtime["mounts"] == 0
    assert runtime["max_concurrent_participants"] == 2
    assert runtime["max_total_connections"] == 4
    assert runtime["connection_pool"] is False
    assert runtime["caller_selected_inputs"] is False

    authority = candidate["fixture_authority"]
    assert authority["fabric_direct_grant_changes"] == []
    assert authority["data_class"] == "repository_authored_opaque_synthetic_only"
    assert set(authority["principals"]) == {
        "context_lifecycle",
        "context_producer",
        "context_observer",
        "context_coordinator",
    }
    assert "superuser_as_participant" in authority["forbidden"]
    assert "bypassrls" in authority["forbidden"]

    assert candidate["closed_surfaces"] == [
        "app",
        "alembic",
        "api_spine_change",
        "diary_ui",
        "outbox_feed_watcher_listener",
        "operational_database_or_persistence",
        "patient_product_protected_data",
        "provider_model_external_retrieval",
        "tool_command_or_product_write_authority",
        "deployment_production_release_pages",
        "protected_refs",
        "docs_branding",
    ]


def test_contract_and_schema_are_whole_document_valid_and_closed() -> None:
    _assert_semantics(_contract())


def test_parent_paths_and_hashes_match_current_exact_files() -> None:
    bindings = {item["id"]: item for item in _contract()["parent_bindings"]}
    assert set(bindings) == set(EXPECTED_PARENT_BINDINGS)
    for binding_id, (relative_path, digest) in EXPECTED_PARENT_BINDINGS.items():
        binding = bindings[binding_id]
        assert binding["path"] == relative_path
        assert binding["sha256"] == f"sha256:{digest}"
        assert hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() == digest


def test_plan_design_and_threat_delta_freeze_the_exact_boundary() -> None:
    combined = _flat(PLAN, DESIGN, THREAT)
    for required in (
        "this is not aes-c6",
        "six fixed races",
        "timeout/pgsleep",
        "wait_event_type=lock",
        "participant retry",
        "40001",
        "cf004",
        "p0001",
        "no crash/restart or unknown-commit claim",
        "docs/branding/",
        "gemini 3.6 flash/high",
        "provider-free",
        "exact captured-container-id cleanup",
    ):
        assert required in combined


def test_claim_boundary_keeps_restart_unknown_commit_and_runtime_closed() -> None:
    candidate = _contract()
    does_not_prove = set(candidate["claim_boundary"]["does_not_prove"])
    assert {
        "server_crash_or_restart",
        "unknown_commit_recovery",
        "arbitrary_deadlock_freedom",
        "automatic_retry_policy",
        "alembic_or_application_runtime_wiring",
        "operational_source_or_persistence",
        "patient_clinical_product_or_provider_safety",
    } <= does_not_prove


def _mutate_extra_top_level(candidate: dict[str, Any]) -> None:
    candidate["runtime_authority"] = True


def _mutate_scenario_order(candidate: dict[str, Any]) -> None:
    candidate["scenario_order"][0], candidate["scenario_order"][1] = (
        candidate["scenario_order"][1],
        candidate["scenario_order"][0],
    )


def _mutate_network(candidate: dict[str, Any]) -> None:
    candidate["runtime_profile"]["network_mode"] = "bridge"


def _mutate_participants(candidate: dict[str, Any]) -> None:
    candidate["runtime_profile"]["max_concurrent_participants"] = 3


def _mutate_retry(candidate: dict[str, Any]) -> None:
    candidate["synchronization_profile"]["participant_retry_count"] = 1


def _mutate_raw_activity(candidate: dict[str, Any]) -> None:
    candidate["synchronization_profile"]["raw_activity_fields_retained"] = ["query"]


def _mutate_isolation(candidate: dict[str, Any]) -> None:
    candidate["scenarios"][0]["isolation"] = "read committed"


def _mutate_sqlstate(candidate: dict[str, Any]) -> None:
    candidate["scenarios"][3]["contender_sqlstate"] = "40001"


def _mutate_direct_grant(candidate: dict[str, Any]) -> None:
    candidate["fixture_authority"]["fabric_direct_grant_changes"] = ["grant_all"]


def _mutate_remove_closed_surface(candidate: dict[str, Any]) -> None:
    candidate["closed_surfaces"].remove("provider_model_external_retrieval")


HOSTILE_MUTATIONS: tuple[Callable[[dict[str, Any]], None], ...] = (
    _mutate_extra_top_level,
    _mutate_scenario_order,
    _mutate_network,
    _mutate_participants,
    _mutate_retry,
    _mutate_raw_activity,
    _mutate_isolation,
    _mutate_sqlstate,
    _mutate_direct_grant,
    _mutate_remove_closed_surface,
)


@pytest.mark.parametrize("mutate", HOSTILE_MUTATIONS, ids=lambda item: item.__name__)
def test_hostile_mutations_fail_closed(
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    candidate = copy.deepcopy(_contract())
    mutate(candidate)
    with pytest.raises((AssertionError, ValidationError)):
        _assert_semantics(candidate)
