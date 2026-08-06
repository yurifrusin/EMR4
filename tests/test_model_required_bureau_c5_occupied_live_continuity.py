import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_ID = "model-required-bureau-c5-occupied-live-rehearsal"
SOURCE_HEAD = "dff672049ab5ce47058d7340525e63589fefc5c1"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_c5_occupied_live_continuity_and_compass_are_current():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    compass = load("orchestration/continuity/emr4-compass.json")
    assert graph["graph_revision"] == 216
    assert graph["nodes"][-1]["id"] == NODE_ID
    assert graph["nodes"][-1]["coordinates"]["source_head"] == SOURCE_HEAD
    assert compass["map_revision"] == 198
    assert compass["source_graph_revision"] == 216
    assert compass["current_position"]["node_id"] == NODE_ID
    assert "C5 occupied" in compass["orientation_statement"]
    assert "Bureau Memory Bank" in compass["orientation_statement"]


def test_c5_occupied_evidence_is_schema_valid_and_fully_cleaned():
    from jsonschema import Draft202012Validator

    evidence = load(
        "orchestration/continuity/model-required-bureau-c5-disposable-live-"
        "development-recovery/occupied-rehearsal-interpreter-binding-evidence.json"
    )
    schema = load(
        "orchestration/continuity/model-required-bureau-c5-disposable-live-"
        "development-recovery/occupied-rehearsal-evidence.schema.json"
    )
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(evidence)
    assert evidence["result"] == (
        "model_required_bureau_c5_disposable_live_development_recovery_pass"
    )
    assert evidence["source_head"] == SOURCE_HEAD
    assert evidence["proofreader"] == {
        "admitted": True,
        "correction_ticket_used": False,
        "reason_codes": [],
    }
    assert evidence["attempt_receipt"]["generation"] == 2
    assert evidence["attempt_receipt"]["state"] == "healthy"
    cleanup = evidence["cleanup_receipt"]
    assert cleanup["result"] == "cleanup_verified"
    for key in (
        "no_process",
        "no_listener",
        "no_task_directory",
        "no_open_ledger",
        "no_reusable_capability",
        "ledger_consumed",
    ):
        assert cleanup[key] is True


def test_c5_provider_and_cost_accounting_is_exact_and_closed():
    evidence = load(
        "orchestration/continuity/model-required-bureau-c5-disposable-live-"
        "development-recovery/occupied-rehearsal-interpreter-binding-evidence.json"
    )
    ledger = load(
        "orchestration/continuity/model-required-bureau-c5-disposable-live-"
        "development-recovery/occupied-rehearsal-interpreter-binding-cost-ledger.json"
    )
    assert ledger["status"] == "closed"
    assert ledger["provider_calls_consumed"] == 1
    assert ledger["provider_calls_reserved"] == 0
    assert ledger["maximum_reserved_cost_consumed_usd"] == 0.25
    assert ledger["maximum_cost_usd"] == 0.5
    assert ledger["fallback_used"] is False
    assert len(ledger["attempts"]) == 1
    assert ledger["attempts"][0]["admitted"] is True
    assert evidence["operation_counters"]["provider_calls"] == 1
    for key in (
        "cloud_iam_operations",
        "database_operations",
        "deployment_operations",
        "external_event_operations",
        "product_operations",
        "protected_operations",
        "shell_operations",
        "sql_operations",
    ):
        assert evidence["operation_counters"][key] == 0


def test_context_fabric_contract_is_next_but_runtime_remains_closed():
    graph = load("orchestration/continuity/emr4-continuity-graph.json")
    node = graph["nodes"][-1]
    scope = node["authority"]["authorized_openings"][0]["scope"]
    assert "provider-free" in scope
    assert "Bureau Memory Bank" in scope
    assert "no product route" in scope
    unresolved = " ".join(node["unresolved_gates"]).lower()
    for phrase in (
        "product routes",
        "persistence",
        "provider calls",
        "patient",
        "clinical",
        "real databases",
        "commands",
        "writes",
        "deployment",
        "production",
        "release",
        "pages",
        "protected",
    ):
        assert phrase in unresolved
