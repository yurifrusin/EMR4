from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal"
)
CONTRACT_PATH = BASE / "restart-unknown-commit-recovery-descendant-contract.json"
SCHEMA_PATH = BASE / "restart-unknown-commit-recovery-descendant-contract.schema.json"
PLAN_PATH = ROOT / (
    "docs/raisa-context-fabric-durability-restart-unknown-commit-"
    "recovery-descendant-plan.md"
)
THREAT_PATH = ROOT / (
    "docs/security/raisa-context-fabric-durability-restart-unknown-commit-"
    "recovery-descendant-threat-model-delta.md"
)
DIAGNOSTIC_ATTEMPT_002_PATH = BASE / (
    "provider-free-durability-restart-unknown-commit-recovery-diagnostic-"
    "evidence-attempt-002.json"
)
STOP_CLOSEOUT_PATH = ROOT / (
    "docs/raisa-context-fabric-durability-restart-unknown-commit-recovery-"
    "descendant-stop-closeout.md"
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _validate(contract: dict[str, Any]) -> None:
    schema = _load(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(contract, schema)

    assert contract["planning_baseline_head"] == (
        "2edfbf0c5990335947b40a370b676aad25aba023"
    )
    assert contract["last_accepted_durability"] == {
        "result": "raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_pass",
        "continuity_revision": 243,
        "compass_revision": 225,
    }
    assert contract["phase_order"] == [
        "CLOSED_COORDINATE_INSTRUMENTATION",
        "NO_CRASH_FIRST_SEQUENCE_DIAGNOSTIC",
        "ONE_NEW_FOUR_SCENARIO_ATTEMPT",
    ]

    failures = contract["immutable_failures"]
    assert [row["attempt"] for row in failures] == [
        "CFD2-ATTEMPT-001",
        "CFD2-ATTEMPT-002",
    ]
    for row in failures:
        assert row["sigkill"] == 0
        assert _sha256(ROOT / row["path"]) == row["sha256"]

    terminal = contract["terminal_evidence"]
    assert terminal["coordinate_required"] is True
    assert terminal["failure_stage_equals_coordinate"] is True
    assert terminal["returncode_classes"] == ["zero", "nonzero"]
    assert terminal["result_token_vocabulary"] == [
        "PRIMARY",
        "RECEIPT_APPLIED",
        "RECEIPT_REPLAYED",
        "1",
        "2",
    ]
    assert terminal["allowed_sqlstates"] == ["P0001", "CF303"]
    assert {
        "raw_sql",
        "query_text",
        "stdout",
        "stderr",
        "error_text",
        "server_log",
        "wal",
        "backend_pid",
        "lock_key",
        "database_url",
        "credential",
    } <= set(terminal["forbidden"])

    coordinates = contract["terminal_coordinates"]
    assert len(coordinates) == len(set(coordinates)) == 27
    assert coordinates[:10] == [
        "fixture_register_observer_r01",
        "fixture_register_observer_r02",
        "fixture_register_observer_r03",
        "fixture_register_observer_r04",
        "fixture_produce_position_1",
        "fixture_produce_position_2",
        "fixture_admit_observer_r01_position_1",
        "fixture_admit_observer_r02_position_1",
        "fixture_admit_observer_r03_position_1",
        "fixture_admit_observer_r04_position_1",
    ]

    diagnostic = contract["diagnostic_profile"]
    assert diagnostic["measured_coordinate_order"] == [
        "cfd2_r01_apply_position_1",
        "cfd2_r01_append_anchor_2",
    ]
    assert diagnostic["setup_precondition_count"] == 10
    assert diagnostic["sigkill_count"] == diagnostic["restart_count"] == 0
    assert diagnostic["participant_retry_count"] == 0
    assert diagnostic["maximum_immutable_attempts"] == 2
    assert diagnostic["maximum_corrections"] == 1
    assert diagnostic["stop_after_first_failure"] is True

    assert set(contract["correction_allowlist"]) == {
        "terminal_expectation",
        "participant_script_framing",
        "coordinate_propagation",
        "harness_sequencing",
    }
    assert {
        "accepted_inert_sql",
        "role_or_rls_grants",
        "atomic_transition_membership",
        "recovery_classification",
        "anchor_authority",
        "transaction_isolation",
        "durability_settings",
        "scenario_meaning",
        "claim_boundary",
    } == set(contract["correction_forbidden"])

    full = contract["full_attempt_gate"]
    assert full["attempt_id"] == "CFD2-ATTEMPT-003"
    assert full["scenario_order"] == [
        "CFD2-R01",
        "CFD2-R02",
        "CFD2-R03",
        "CFD2-R04",
    ]
    assert full["sigkill_count"] == full["restart_count"] == 4
    assert full["maximum_attempts"] == 1
    assert full["post_attempt_correction_or_retry"] is False

    assert {
        "protected_holdouts",
        "historical_diary_phi",
        "docs_branding",
        "real_product_patient_clinical_data",
        "operational_database_source_or_watcher",
        "provider_or_external_retrieval",
        "credentials_or_iam",
        "executable_product_tool_or_command",
        "deployment_production_release_pages",
        "protected_refs",
    } <= set(contract["closed_surfaces"])


def test_recovery_plan_packet_is_whole_document_valid_and_fail_closed() -> None:
    for path in (CONTRACT_PATH, SCHEMA_PATH, PLAN_PATH, THREAT_PATH):
        assert path.is_file()
    _validate(_load(CONTRACT_PATH))

    plan = PLAN_PATH.read_text(encoding="utf-8")
    threat = THREAT_PATH.read_text(encoding="utf-8")
    for phrase in (
        "coordinate-specific evidence",
        "zero `SIGKILL`, restart, blind retry",
        "At most two diagnostic attempts",
        "There is no post-attempt-003 correction or rerun allowance",
        "explicit-path staging only",
    ):
        assert phrase in plan
    for phrase in (
        "first failed coordinate stops the sequence",
        "Exactly one attempt 003",
        "No patient, clinical, product, provider",
    ):
        assert phrase in threat


Mutation = Callable[[dict[str, Any]], None]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value.update(status="runtime_open"),
        lambda value: value["immutable_failures"][1].update(
            sha256="sha256:" + "0" * 64
        ),
        lambda value: value["terminal_coordinates"].pop(),
        lambda value: value["terminal_coordinates"].__setitem__(
            1, value["terminal_coordinates"][0]
        ),
        lambda value: value["diagnostic_profile"].update(network_mode="bridge"),
        lambda value: value["diagnostic_profile"].update(sigkill_count=1),
        lambda value: value["diagnostic_profile"].update(maximum_immutable_attempts=3),
        lambda value: value["diagnostic_profile"].update(maximum_corrections=2),
        lambda value: value["full_attempt_gate"].update(maximum_attempts=2),
        lambda value: value["full_attempt_gate"].update(
            post_attempt_correction_or_retry=True
        ),
    ],
)
def test_recovery_contract_rejects_boundary_mutations(mutate: Mutation) -> None:
    candidate = copy.deepcopy(_load(CONTRACT_PATH))
    mutate(candidate)
    with pytest.raises((jsonschema.ValidationError, AssertionError)):
        _validate(candidate)


def test_recovery_descendant_stops_after_failed_diagnostic_attempt_002() -> None:
    evidence = _load(DIAGNOSTIC_ATTEMPT_002_PATH)
    closeout = " ".join(STOP_CLOSEOUT_PATH.read_text(encoding="utf-8").split())

    assert evidence["parent"]["source_head"] == (
        "fe8313d224a92115aa31bea14f0cd3b14e4c9967"
    )
    assert evidence["result"] == "rehearsal_failed"
    assert evidence["terminal_failure"] == {
        "code": "unexpected_terminal_success",
        "coordinate": "cfd2_r01_append_anchor_2",
        "result_lines": [],
        "returncode_class": "nonzero",
        "sqlstate": None,
    }
    assert len(evidence["preconditions"]) == 10
    assert evidence["terminal_observations"] == []
    assert evidence["operation_counters"] == {
        "external_network_operations": 0,
        "participant_retry": 0,
        "product_commands": 0,
        "product_reads": 0,
        "provider_calls": 0,
        "restart": 0,
        "sigkill": 0,
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "removed": True,
        "status": "cleanup_verified",
    }
    assert _sha256(DIAGNOSTIC_ATTEMPT_002_PATH) == (
        "sha256:c595cd56b5b9a24dfdecc77fe12d998d1f16d593a33142cc3e9e9deffe7f1d12"
    )
    for phrase in (
        "stopped_unproved_after_diagnostic_attempt_002",
        "falsifies the earlier sole-cause claim",
        "attempt 003 is ineligible and was not run",
        "workflow-incident diagnosis",
    ):
        assert phrase in closeout
