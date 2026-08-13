from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_unmounted_cf_d2_event_cue_representation_architecture as representation,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture"
)
CONTRACT = BASE / "representation-contract.json"
SCHEMA = BASE / "representation-contract.schema.json"
EVIDENCE = BASE / "provider-free-unmounted-representation-evidence.json"
PLAN = (
    ROOT
    / "docs"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture-plan.md"
)
ARCHITECTURE = (
    ROOT
    / "docs"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture.md"
)
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture-threat-model-delta.md"
)
LATCH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-active-operation-latch"
    / "current.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_closed_contract_schema_and_semantics_pass() -> None:
    contract = _load(CONTRACT)
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)
    assert representation.validate_contract(contract, schema) == []


def test_exact_seven_relations_and_five_protocols_are_frozen() -> None:
    contract = _load(CONTRACT)
    assert [relation["name"] for relation in contract["relations"]] == list(
        representation.EXPECTED_RELATIONS
    )
    assert [protocol["name"] for protocol in contract["transaction_protocols"]] == list(
        representation.EXPECTED_PROTOCOLS
    )
    assert len(contract["relations"]) == 7
    assert len(contract["transaction_protocols"]) == 5


def test_all_twelve_representability_families_pass() -> None:
    scenarios = representation.build_scenarios()
    assert list(scenarios) == representation.EXPECTED_SCENARIOS
    assert len(scenarios) == 12
    assert all(representation.validate_rows(rows) == [] for rows in scenarios.values())


def test_committed_evidence_is_exact_and_provider_free() -> None:
    report = representation.run_acceptance()
    assert report == _load(EVIDENCE)
    assert report["status"] == "passed"
    assert report["relation_count"] == 7
    assert report["transaction_protocol_count"] == 5
    assert report["representability_scenario_count"] == 12
    assert report["contract_hostile_rejection_count"] == 52
    assert report["row_hostile_rejection_count"] == 28
    assert report["total_hostile_rejection_count"] == 80
    assert report["admitted_contract_hostiles"] == []
    assert report["admitted_row_hostiles"] == []
    assert report["database_or_source_opened"] is False
    assert report["sql_or_ddl_rendered"] is False
    assert report["provider_calls"] == 0
    assert report["command_or_write"] is False
    assert report["product_patient_or_clinical_data"] is False


def test_every_hostile_contract_and_row_variant_fails_closed() -> None:
    contract = _load(CONTRACT)
    schema = _load(SCHEMA)
    scenarios = representation.build_scenarios()
    contract_before = representation._canonical_digest(contract)
    rows_before = representation._canonical_digest(scenarios)
    contract_hostiles = representation.build_contract_hostiles(contract)
    row_hostiles = representation.build_row_hostiles(scenarios)
    assert len(contract_hostiles) == 52
    assert len(row_hostiles) == 28
    assert all(
        representation.validate_contract(candidate, schema)
        for _, candidate in contract_hostiles
    )
    assert all(representation.validate_rows(candidate) for _, candidate in row_hostiles)
    assert representation._canonical_digest(contract) == contract_before
    assert representation._canonical_digest(scenarios) == rows_before


def test_checkpoint_gap_crossing_and_stale_generation_reject() -> None:
    gap = copy.deepcopy(representation.build_scenarios()["out_of_order_gap_held"])
    checkpoint = gap["consumer_checkpoint"][0]
    checkpoint["checkpoint_state"] = "exact"
    checkpoint["checkpoint_position"] = 2
    assert "consumer_checkpoint[0]:gap_at:1" in representation.validate_rows(gap)

    stale = copy.deepcopy(
        representation.build_scenarios()["one_required_pending"]
    )
    stale["consumer_checkpoint"][0]["lease_generation"] = 6
    assert "consumer_checkpoint[0]:stale_generation" in representation.validate_rows(
        stale
    )


def test_coalesced_receipts_share_one_exact_covering_obligation() -> None:
    rows = representation.build_scenarios()["same_reason_coalesced"]
    obligation = rows["cue_obligation"][0]
    receipts = rows["terminal_receipt"]
    assert obligation["from_position"] == 1
    assert obligation["through_position"] == 2
    assert {receipt["obligation_id"] for receipt in receipts} == {
        obligation["obligation_id"]
    }
    assert representation.validate_rows(rows) == []


def test_failed_dispatch_retains_pending_obligation() -> None:
    rows = representation.build_scenarios()["dispatch_failed_pending"]
    assert rows["cue_obligation"][0]["state"] == "pending"
    assert rows["dispatch_attempt"][0]["outcome"] == "failed"
    assert rows["dispatch_attempt"][0]["failure_class"] == "transient_transport"
    assert representation.validate_rows(rows) == []


def test_reconciliation_requires_delivered_attempt_and_exact_truth_table() -> None:
    rows = copy.deepcopy(
        representation.build_scenarios()["reconciliation_refreshed"]
    )
    rows["dispatch_attempt"][0]["outcome"] = "failed"
    rows["dispatch_attempt"][0]["failure_class"] = "transient_transport"
    assert "reconciliation_receipt[0]:delivered_attempt_missing" in (
        representation.validate_rows(rows)
    )

    rows = copy.deepcopy(
        representation.build_scenarios()["reconciliation_refreshed"]
    )
    rows["reconciliation_receipt"][0]["fresh_read_performed"] = False
    assert "reconciliation_receipt[0]:truth_table_mismatch" in (
        representation.validate_rows(rows)
    )


def test_no_payload_column_is_representable() -> None:
    contract = _load(CONTRACT)
    field_names = {
        field["name"]
        for relation in contract["relations"]
        for field in relation["fields"]
    }
    for fragment in contract["prohibited_field_fragments"]:
        assert all(fragment not in field_name for field_name in field_names)
    assert not any("json" in field_name or "blob" in field_name for field_name in field_names)


def test_transaction_and_external_authority_are_not_mislabelled_as_row_checks() -> None:
    contract = _load(CONTRACT)
    classes = contract["enforcement_classification"]
    assert "atomic_receipt_obligation" in classes["transaction_protocol"]
    assert "contiguous_checkpoint" in classes["transaction_protocol"]
    assert "current_source_truth" in classes["external_authority"]
    assert "current_user_authority" in classes["external_authority"]
    assert "atomic_receipt_obligation" not in classes["row_constraint"]
    assert "current_source_truth" not in classes["key_or_reference"]


def test_checker_imports_no_database_network_process_or_provider_modules() -> None:
    tree = ast.parse(Path(representation.__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported.isdisjoint(
        {
            "asyncpg",
            "boto3",
            "google",
            "httpx",
            "psycopg",
            "requests",
            "socket",
            "sqlalchemy",
            "subprocess",
        }
    )


def test_plan_architecture_and_threat_freeze_the_inert_boundary() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8") for path in (PLAN, ARCHITECTURE, THREAT)
    ).lower()
    for phrase in (
        "exactly seven abstract relations",
        "transaction_protocol",
        "external_authority",
        "events and cues remain acceleration hints",
        "not sql",
        "no database connection",
        "no arbitrary json",
        "current source truth",
        "fresh authorised read",
        "patient/product/clinical data",
        "docs/branding/",
        "explicit-path only",
    ):
        assert phrase in text


def test_plan_architecture_and_threat_have_brisbane_timestamps() -> None:
    for path in (PLAN, ARCHITECTURE, THREAT):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
        assert "Date: 2026-08-13" in head
        assert "Timestamp: 2026-08-13T" in head
        assert "+10:00 (Australia/Brisbane)" in head


def test_active_latch_is_on_the_representation_architecture() -> None:
    latch = _load(LATCH)
    assert latch["status"] == "in_progress"
    assert (
        latch["operation_id"]
        == "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture"
    )
    assert latch["source_head"] == "784fdc4c0237e1c363676638d010b2bd4b033210"
    assert latch["terminal_response"]["permitted"] is False
