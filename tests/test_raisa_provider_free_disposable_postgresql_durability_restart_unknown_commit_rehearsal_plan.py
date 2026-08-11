from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal"
CONTRACT_PATH = BASE / "restart-unknown-commit-rehearsal-contract.json"
SCHEMA_PATH = BASE / "restart-unknown-commit-rehearsal-contract.schema.json"
PLAN_PATH = ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-plan.md"
DESIGN_PATH = ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-design.md"
THREAT_PATH = ROOT / "docs/security/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-threat-model-delta.md"

SCENARIO_ORDER = ["CFD2-R01", "CFD2-R02", "CFD2-R03", "CFD2-R04"]
CATEGORIES = [
    "CONFIRMED_COMMIT_RESTART",
    "CONFIRMED_ROLLBACK_RESTART",
    "UNKNOWN_COMMIT_COMMITTED_RECOVERY",
    "UNKNOWN_COMMIT_ROLLED_BACK_RECOVERY",
]
CLASSIFICATIONS = [
    "COMMITTED_CONFIRMED",
    "ROLLED_BACK_CONFIRMED",
    "COMMITTED_RECOVERED",
    "ROLLED_BACK_RECOVERED",
]
PARENT_IDS = [
    "accepted_concurrency_pass_evidence",
    "current_concurrency_contract",
    "current_concurrency_evidence_schema",
    "current_concurrency_harness",
    "accepted_concurrency_closeout",
    "accepted_concurrency_sol_acceptance",
    "inert_sql",
    "render_manifest",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_semantics(contract: dict[str, Any]) -> None:
    assert contract["schema_version"] == (
        "emr4.raisa-context-fabric-disposable-postgresql-durability-"
        "restart-unknown-commit-rehearsal.v1"
    )
    assert contract["status"] == "frozen_provider_free_planning_runtime_closed"
    assert contract["planning_baseline_head"] == "e690eefaf91115343b8fcbbecc7c3f5fe0b25193"
    assert contract["accepted_concurrency_runtime_source_head"] == (
        "fed81847b4155d49cf997905e79cf31808ceb017"
    )
    assert contract["accepted_concurrency_functional_source_head"] == (
        "43f168f3d5d1f71ec0f9071c40fadf14b6107621"
    )

    bindings = contract["parent_bindings"]
    assert [row["id"] for row in bindings] == PARENT_IDS
    assert len({row["path"] for row in bindings}) == 8
    assert len({row["sha256"] for row in bindings}) == 8
    for row in bindings:
        path = ROOT / row["path"]
        assert path.is_file()
        assert row["sha256"] == _sha256(path)

    runtime = contract["runtime_profile"]
    assert runtime == {
        "postgresql_major": 16,
        "image": "postgres:16-bookworm",
        "pull_policy": "never",
        "network_mode": "none",
        "published_ports": 0,
        "bind_mounts": 0,
        "named_volumes": 0,
        "anonymous_volumes": 0,
        "declared_volume_shield": "tmpfs_at_image_declared_default_pgdata_only",
        "durable_cluster_storage": "owned_container_writable_layer_outside_declared_volume",
        "database_count": 1,
        "container_count": 1,
        "restart_policy": "none",
        "max_total_connections": 4,
        "connection_pool": False,
        "caller_selected_inputs": False,
        "cleanup": "exact_captured_container_id_after_ownership_reverification",
    }

    durability = contract["durability_profile"]
    assert durability["fsync"] == "on"
    assert durability["synchronous_commit"] == "on"
    assert durability["full_page_writes"] == "on"
    assert durability["data_checksums"] == "on"
    assert durability["crash_method"] == (
        "docker_kill_sigkill_exact_captured_container_then_start_same_id"
    )
    assert durability["crash_count"] == 4
    assert durability["graceful_stop_accepted_as_crash_evidence"] is False
    assert durability["restart_reuses_exact_cluster"] is True
    assert durability["wal_reset_or_recovery_target"] is False
    assert durability["server_log_or_wal_payload_inspection"] is False
    assert durability["participant_retry_count"] == 0

    client = contract["client_observation_profile"]
    assert client["indeterminate_observation"] == (
        "CONNECTION_LOST_WITHOUT_ALLOWLISTED_TERMINAL_RESULT"
    )
    assert client["committed_cutpoint"] == (
        "server_post_commit_pg_sleep_before_one_shot_client_process_exit"
    )
    assert client["rolled_back_cutpoint"] == (
        "server_pre_commit_pg_sleep_after_transition_staging"
    )
    assert client["required_cutpoint_wait_event_type"] == "Timeout"
    assert client["required_cutpoint_wait_event"] == "PgSleep"
    assert client["accepted_recovery_classes"] == [
        "COMMITTED_RECOVERED",
        "ROLLED_BACK_RECOVERED",
    ]
    assert client["unresolved_or_partial_is_pass"] is False
    assert set(client["forbidden_recovery_decision_inputs"]) >= {
        "client_guess",
        "connection_loss_as_success",
        "connection_loss_as_rollback",
        "cutpoint_schedule_as_outcome",
        "stdout_fragment",
        "stderr_fragment",
        "server_log",
        "wal_payload",
        "blind_retry",
    }

    authority = contract["fixture_authority"]
    assert authority["data_class"] == "repository_authored_opaque_synthetic_only"
    assert authority["principals"] == [
        "context_lifecycle",
        "context_producer",
        "context_observer",
        "context_coordinator",
    ]
    assert authority["fabric_direct_grant_changes"] == []
    assert set(authority["forbidden"]) >= {
        "superuser_as_recovery_classifier_or_participant",
        "bypassrls",
        "fabric_direct_dml",
        "operational_credential",
        "product_or_patient_value",
    }

    assert contract["scenario_order"] == SCENARIO_ORDER
    scenarios = contract["scenarios"]
    assert [row["id"] for row in scenarios] == SCENARIO_ORDER
    assert [row["category"] for row in scenarios] == CATEGORIES
    assert [row["post_restart_classification"] for row in scenarios] == CLASSIFICATIONS
    assert [row["client_observation"] for row in scenarios] == [
        "COMMIT_ACKNOWLEDGED",
        "ROLLBACK_SQLSTATE_P0001_ACKNOWLEDGED",
        "CONNECTION_LOST_WITHOUT_ALLOWLISTED_TERMINAL_RESULT",
        "CONNECTION_LOST_WITHOUT_ALLOWLISTED_TERMINAL_RESULT",
    ]
    for row in scenarios:
        assert len(row["post_restart_outcomes"]) >= 2
        assert len(row["readback"]) >= 4
        assert len(row["forbidden_effects"]) >= 3
        assert len(set(row["post_restart_outcomes"])) == len(row["post_restart_outcomes"])
        assert len(set(row["readback"])) == len(row["readback"])
        assert len(set(row["forbidden_effects"])) == len(row["forbidden_effects"])

    assert scenarios[2]["post_restart_outcomes"] == [
        "RECEIPT_REPLAYED",
        "CF303_BEFORE_ANCHOR",
        "ANCHOR_APPENDED",
        "RECEIPT_APPLIED_AFTER_ANCHOR",
    ]
    assert scenarios[3]["post_restart_outcomes"] == [
        "NO_RECEIPT_OR_EFFECT",
        "RECEIPT_APPLIED",
        "ANCHOR_APPENDED",
        "RECEIPT_REPLAYED",
    ]

    coverage = contract["category_coverage"]
    assert coverage == {
        "CONFIRMED_COMMIT_RESTART": 1,
        "CONFIRMED_ROLLBACK_RESTART": 1,
        "UNKNOWN_COMMIT_COMMITTED_RECOVERY": 1,
        "UNKNOWN_COMMIT_ROLLED_BACK_RECOVERY": 1,
        "total": 4,
    }

    evidence = contract["evidence_contract"]
    assert all(value is True for key, value in evidence.items() if key.startswith("record_"))
    assert set(evidence["forbidden"]) >= {
        "raw_sql_or_query_text",
        "raw_server_log_or_error_text",
        "backend_pid_or_lock_key",
        "database_url_or_credential",
        "patient_product_or_real_person_value",
        "stdout_or_stderr_fragment_from_indeterminate_client",
        "global_docker_enumeration",
    }

    claim = contract["claim_boundary"]
    assert "two_no_terminal_result_cases_resolved_only_from_complete_post_restart_durable_state" in claim["proves"]
    assert set(claim["does_not_prove"]) >= {
        "literal_crash_during_wal_commit_or_protocol_ack_boundary",
        "hardware_storage_power_loss_or_filesystem_durability",
        "application_driver_retry_or_connection_pool_behavior",
        "key_rotation_retention_purge_load_or_performance",
        "operational_source_or_long_lived_persistence",
    }

    assert set(contract["closed_surfaces"]) >= {
        "app",
        "alembic",
        "api_spine_change",
        "diary_ui",
        "operational_database_or_persistence",
        "patient_product_protected_data",
        "provider_model_external_retrieval",
        "deployment_production_release_pages",
        "protected_refs",
        "docs_branding",
    }


def test_plan_packet_exists_and_contract_validates_as_a_whole_document() -> None:
    for path in (CONTRACT_PATH, SCHEMA_PATH, PLAN_PATH, DESIGN_PATH, THREAT_PATH):
        assert path.is_file()
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(contract, schema)
    _validate_semantics(contract)


def test_plan_and_security_text_freeze_the_no_guess_boundary() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    design = DESIGN_PATH.read_text(encoding="utf-8")
    threat = THREAT_PATH.read_text(encoding="utf-8")
    combined = "\n".join((plan, design, threat))
    for required in (
        "Connection loss",
        "COMMITTED_RECOVERED",
        "ROLLED_BACK_RECOVERED",
        "SIGKILL",
        "same cluster",
        "recovery anchor",
        "CF303",
        "zero-residue",
        "docs/branding/",
        "explicit path",
    ):
        assert required.lower() in combined.lower()
    for forbidden_claim in (
        "proves production",
        "authorizes production",
        "patient data is allowed",
        "network access is allowed",
        "blind retry is safe",
    ):
        assert forbidden_claim not in combined.lower()


Mutation = Callable[[dict[str, Any]], None]


def _set(path: tuple[Any, ...], value: Any) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        target: Any = candidate
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value

    return mutate


def _delete(path: tuple[Any, ...]) -> Mutation:
    def mutate(candidate: dict[str, Any]) -> None:
        target: Any = candidate
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]

    return mutate


HOSTILE_MUTATIONS: list[Mutation] = [
    _set(("status",), "runtime_open"),
    _set(("planning_baseline_head",), "0" * 40),
    _set(("accepted_concurrency_runtime_source_head",), "0" * 40),
    _set(("accepted_concurrency_functional_source_head",), "0" * 40),
    _set(("parent_bindings", 0, "sha256"), "sha256:" + "0" * 64),
    _set(("runtime_profile", "pull_policy"), "always"),
    _set(("runtime_profile", "network_mode"), "bridge"),
    _set(("runtime_profile", "published_ports"), 5432),
    _set(("runtime_profile", "bind_mounts"), 1),
    _set(("runtime_profile", "named_volumes"), 1),
    _set(("runtime_profile", "anonymous_volumes"), 1),
    _set(("runtime_profile", "durable_cluster_storage"), "host_bind_mount"),
    _set(("runtime_profile", "container_count"), 2),
    _set(("runtime_profile", "restart_policy"), "always"),
    _set(("runtime_profile", "connection_pool"), True),
    _set(("durability_profile", "fsync"), "off"),
    _set(("durability_profile", "synchronous_commit"), "off"),
    _set(("durability_profile", "full_page_writes"), "off"),
    _set(("durability_profile", "data_checksums"), "off"),
    _set(("durability_profile", "crash_method"), "graceful_stop"),
    _set(("durability_profile", "crash_count"), 3),
    _set(("durability_profile", "participant_retry_count"), 1),
    _set(("client_observation_profile", "unresolved_or_partial_is_pass"), True),
    _set(("client_observation_profile", "accepted_recovery_classes"), ["COMMITTED_RECOVERED"]),
    _set(("client_observation_profile", "forbidden_recovery_decision_inputs"), []),
    _set(("fixture_authority", "data_class"), "product_data"),
    _set(("fixture_authority", "fabric_direct_grant_changes"), ["grant_all"]),
    _set(("scenario_order",), list(reversed(SCENARIO_ORDER))),
    _set(("scenarios", 2, "client_observation"), "COMMIT_ACKNOWLEDGED"),
    _set(("scenarios", 2, "post_restart_classification"), "ROLLED_BACK_RECOVERED"),
    _set(("scenarios", 3, "post_restart_classification"), "COMMITTED_RECOVERED"),
    _set(("scenarios", 2, "post_restart_outcomes"), ["RECEIPT_REPLAYED", "RECEIPT_APPLIED_AFTER_ANCHOR"]),
    _set(("scenarios", 3, "post_restart_outcomes"), ["RECEIPT_APPLIED", "RECEIPT_REPLAYED"]),
    _set(("category_coverage", "total"), 3),
    _delete(("evidence_contract", "record_closed_recovery_classification")),
    _set(("evidence_contract", "forbidden"), []),
    _set(("claim_boundary", "does_not_prove"), []),
    _set(("closed_surfaces",), ["docs_branding"]),
]


@pytest.mark.parametrize("mutate", HOSTILE_MUTATIONS, ids=lambda value: value.__name__)
def test_hostile_contract_mutations_fail_closed(mutate: Mutation) -> None:
    candidate = copy.deepcopy(_load(CONTRACT_PATH))
    mutate(candidate)
    with pytest.raises((AssertionError, jsonschema.ValidationError)):
        jsonschema.validate(candidate, _load(SCHEMA_PATH))
        _validate_semantics(candidate)
