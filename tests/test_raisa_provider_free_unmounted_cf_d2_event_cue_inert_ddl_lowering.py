from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_unmounted_cf_d2_event_cue_inert_ddl_lowering import (
    CHECK_BINDINGS,
    CONTRACT_PATH,
    CONTRACT_SCHEMA_PATH,
    EVIDENCE_PATH,
    EXPECTED_FIELDS,
    MANIFEST_PATH,
    PARENT_PATH,
    PARENT_SCHEMA_PATH,
    PARENT_SHA256,
    ROOT,
    SQL_PATH,
    build_manifest,
    hostile_candidates,
    recognize_candidate,
    render_sql,
    run,
    validate_inputs,
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def test_closed_lowering_contract_and_parent_pass_schema_and_semantics() -> None:
    contract = _json(CONTRACT_PATH)
    schema = _json(CONTRACT_SCHEMA_PATH)
    parent = _json(PARENT_PATH)
    parent_schema = _json(PARENT_SCHEMA_PATH)

    assert list(Draft202012Validator(schema).iter_errors(contract)) == []
    assert validate_inputs(contract, schema, parent, parent_schema) == []


def test_exact_accepted_parent_and_fixed_paths_are_bound() -> None:
    contract = _json(CONTRACT_PATH)
    assert _sha256(PARENT_PATH) == PARENT_SHA256
    assert contract["accepted_representation_source"] == (
        "16ec7993ee3c46d83772f47aa7dab61fc1fcb7ed"
    )
    assert ROOT / contract["accepted_representation_contract_path"] == PARENT_PATH
    assert ROOT / contract["output_paths"]["sql"] == SQL_PATH
    assert ROOT / contract["output_paths"]["manifest"] == MANIFEST_PATH
    assert ROOT / contract["output_paths"]["evidence"] == EVIDENCE_PATH
    assert SQL_PATH.suffix == ".inert"
    assert "alembic" not in SQL_PATH.parts


def test_two_isolated_renders_are_byte_identical() -> None:
    parent = _json(PARENT_PATH)
    assert render_sql(parent).encode("utf-8") == render_sql(_json(PARENT_PATH)).encode(
        "utf-8"
    )
    assert SQL_PATH.read_bytes() == render_sql(parent).encode("utf-8")


def test_manifest_preserves_exact_relations_fields_keys_and_mutability() -> None:
    parent = _json(PARENT_PATH)
    sql = render_sql(parent)
    manifest = build_manifest(parent, sql)

    assert [row["name"] for row in manifest["relations"]] == list(EXPECTED_FIELDS)
    assert sum(len(row["fields"]) for row in manifest["relations"]) == 50
    assert sum(len(row["primary_key"]) > 0 for row in manifest["relations"]) == 7
    assert sum(len(row["unique_keys"]) for row in manifest["relations"]) == 3
    assert sum(row["reference_count"] for row in manifest["relations"]) == 7
    for source, lowered in zip(parent["relations"], manifest["relations"], strict=True):
        assert lowered["fields"] == source["fields"]
        assert lowered["mutable_fields"] == source["mutable_fields"]
        assert lowered["mutable_fields_enforced_by_ddl"] is False


def test_all_parent_check_labels_have_one_honest_disposition() -> None:
    parent = _json(PARENT_PATH)
    manifest = _json(MANIFEST_PATH)
    bindings = manifest["check_bindings"]

    assert len(bindings) == 19
    assert sum(row["disposition"] == "sql_check_constraint" for row in bindings) == 18
    annotations = [
        row for row in bindings if row["disposition"] == "inert_semantic_annotation"
    ]
    assert annotations == [
        {
            "constraint_name": None,
            "disposition": "inert_semantic_annotation",
            "label": "coordinate_is_non_authoritative",
            "relation": "observer_coordinate",
        }
    ]
    assert {
        (row["relation"], row["label"])
        for row in bindings
    } == {
        (relation["name"], label)
        for relation in parent["relations"]
        for label in relation["checks"]
    }
    assert sum(len(rows) for rows in CHECK_BINDINGS.values()) == 19


def test_sql_has_exact_closed_statement_inventory() -> None:
    sql = SQL_PATH.read_text(encoding="utf-8")
    assert sql.count(";\n") == 18
    assert sql.count("CREATE SCHEMA emr4_context_fabric_cue;") == 1
    assert sql.count("CREATE DOMAIN emr4_context_fabric_cue.") == 3
    assert sql.count("CREATE TABLE emr4_context_fabric_cue.") == 7
    assert sql.count("ALTER TABLE emr4_context_fabric_cue.") == 7
    assert sql.count(" PRIMARY KEY (") == 7
    assert sql.count(" UNIQUE (") == 3
    assert sql.count("    FOREIGN KEY (") == 7


def test_nullable_future_reference_is_exactly_deferred() -> None:
    sql = SQL_PATH.read_text(encoding="utf-8")
    expected = """ALTER TABLE emr4_context_fabric_cue.terminal_receipt
    ADD CONSTRAINT fk_terminal_receipt_obligation
    FOREIGN KEY (obligation_id) REFERENCES emr4_context_fabric_cue.cue_obligation (obligation_id)
    DEFERRABLE INITIALLY DEFERRED;"""
    assert sql.count(expected) == 1
    assert sql.count("DEFERRABLE INITIALLY DEFERRED") == 1


def test_row_local_allowlists_and_truth_table_are_explicit() -> None:
    sql = SQL_PATH.read_text(encoding="utf-8")
    for token in (
        "source_system = 'emr4_diary'",
        "event_family = 'diary_appointment_change'",
        "consumer_scope = 'reception_one_diary_projection'",
        "classification = 'cue_required'",
        "classification = 'suppressed_irrelevant'",
        "classification = 'rejected_unsupported'",
        "outcome = 'projection_unchanged'",
        "outcome = 'projection_refreshed'",
        "outcome = 'local_selection_or_proposal_cleared'",
        "outcome = 'authorization_rejected'",
        "outcome = 'source_unavailable'",
        "outcome = 'stale_session'",
        "acknowledgement = 'one_fresh_read_attempt_only'",
    ):
        assert token in sql


def test_transaction_protocols_and_external_authority_remain_unlowered() -> None:
    manifest = _json(MANIFEST_PATH)
    sql = SQL_PATH.read_text(encoding="utf-8")
    assert all(
        row == {
            "disposition": "unlowered_transaction_protocol",
            "name": row["name"],
            "proved_by_ddl": False,
        }
        for row in manifest["transaction_protocols"]
    )
    assert manifest["external_authority"]["proved_by_ddl"] is False
    assert manifest["external_authority"]["source_owns_current_truth"] is True
    assert "current source truth and command authority remain external" in sql
    assert sql.count("sql_enforced=false") == 6


def test_canonical_candidate_passes_static_recognizer() -> None:
    parent = _json(PARENT_PATH)
    sql = render_sql(parent)
    manifest = build_manifest(parent, sql)
    assert recognize_candidate(sql, sql, manifest) == []
    assert _json(MANIFEST_PATH) == manifest


def test_all_sixty_five_hostile_candidates_fail_closed() -> None:
    parent = _json(PARENT_PATH)
    sql = render_sql(parent)
    manifest = build_manifest(parent, sql)
    hostile = hostile_candidates(sql)

    assert len(hostile) == 65
    for name, candidate in hostile.items():
        assert recognize_candidate(candidate, sql, manifest), name


def test_hostile_evaluation_does_not_change_canonical_objects() -> None:
    parent = _json(PARENT_PATH)
    sql = render_sql(parent)
    manifest = build_manifest(parent, sql)
    sql_before = sql.encode("utf-8")
    manifest_before = json.dumps(manifest, sort_keys=True).encode("utf-8")

    for candidate in hostile_candidates(sql).values():
        recognize_candidate(candidate, sql, manifest)

    assert sql.encode("utf-8") == sql_before
    assert json.dumps(manifest, sort_keys=True).encode("utf-8") == manifest_before


def test_evidence_is_passed_and_records_zero_external_effects() -> None:
    evidence = _json(EVIDENCE_PATH)
    assert evidence == run(write=False)
    assert evidence["status"] == "passed"
    assert evidence["hostile_candidate_count"] == 65
    assert evidence["hostile_rejection_count"] == 65
    assert evidence["admitted_hostiles"] == []
    for key in (
        "sql_or_migration_executed",
        "database_or_source_opened",
        "operational_state_persisted",
        "runtime_started",
        "command_or_write",
        "product_patient_or_clinical_data",
    ):
        assert evidence[key] is False
    assert evidence["provider_calls"] == 0


def test_renderer_import_surface_has_no_runtime_or_database_modules() -> None:
    source = (
        ROOT
        / "scripts"
        / "raisa_provider_free_unmounted_cf_d2_event_cue_inert_ddl_lowering.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imported.isdisjoint(
        {
            "subprocess", "socket", "psycopg", "psycopg2", "sqlalchemy",
            "requests", "httpx", "google", "alembic",
        }
    )


def test_api_spine_command_and_fresh_read_boundary_is_unchanged() -> None:
    contract = _json(CONTRACT_PATH)
    authority = contract["authority"]
    assert authority == {
        "event_and_cue_are_acceleration_hints_only": True,
        "cue_may_update_display_directly": False,
        "fresh_authorized_scoped_read_required": True,
        "command_rechecks_current_authority_and_source_truth": True,
        "ddl_confers_command_authority": False,
    }
    api_contract = (
        ROOT / "docs" / "api-spine" / "async" / "durable-diary-event-cue-observability.yaml"
    ).read_text(encoding="utf-8")
    assert "event_or_cue_is_command_authority: false" in api_contract
    assert "fresh_authorized_read_before_display: true" in api_contract
    assert "consequential_mutation_requires_rest_command: true" in api_contract


def test_new_plan_design_and_threat_delta_have_date_and_timestamp() -> None:
    paths = [
        ROOT / "docs" / "raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering-plan.md",
        ROOT / "docs" / "raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering-design.md",
        ROOT / "docs" / "security" / "raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering-threat-model-delta.md",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "Date: 2026-08-13" in text
        assert "Timestamp: 2026-08-13T18:14:01+10:00 (Australia/Brisbane)" in text
        assert "database" in text.lower()
