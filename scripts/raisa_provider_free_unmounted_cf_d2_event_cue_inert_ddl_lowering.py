"""Render and statically admit the inert CF-D2 event/cue DDL artifact.

This module reads exact repository JSON and writes fixed repository evidence
paths only. It never imports a database driver, opens a connection, executes
SQL, starts a process, observes a source, or persists operational state.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PARENT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture"
)
PARENT_PATH = PARENT_DIR / "representation-contract.json"
PARENT_SCHEMA_PATH = PARENT_DIR / "representation-contract.schema.json"
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering"
)
CONTRACT_PATH = CONTINUITY / "inert-ddl-contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY / "inert-ddl-contract.schema.json"
SQL_PATH = CONTINUITY / "event-cue-schema.sql.inert"
MANIFEST_PATH = CONTINUITY / "inert-ddl-manifest.json"
EVIDENCE_PATH = CONTINUITY / "provider-free-unmounted-inert-ddl-evidence.json"

PARENT_SHA256 = "sha256:ff72cb2b6458193fb723b19209ac0ca487d3fdda5846d43ccdfafb6986957f64"
SCHEMA_NAME = "emr4_context_fabric_cue"

EXPECTED_FIELDS: dict[str, list[tuple[str, str, bool]]] = {
    "event_partition": [
        ("partition_id", "digest", False),
        ("source_system", "enum", False),
        ("practice_scope_digest", "digest", False),
        ("event_family", "enum", False),
        ("source_epoch_digest", "digest", False),
        ("lease_generation", "positive_integer", False),
    ],
    "observer_coordinate": [
        ("partition_id", "digest", False),
        ("consumer_scope", "enum", False),
        ("source_epoch_digest", "digest", False),
        ("observed_state", "enum", False),
        ("observed_position", "nullable_positive_integer", True),
        ("source_head_state", "enum", False),
        ("source_head_epoch_digest", "nullable_digest", True),
        ("source_head_position", "nullable_positive_integer", True),
    ],
    "terminal_receipt": [
        ("receipt_id", "opaque_id", False),
        ("partition_id", "digest", False),
        ("source_epoch_digest", "digest", False),
        ("source_position", "positive_integer", False),
        ("event_fingerprint_digest", "digest", False),
        ("classification", "enum", False),
        ("reason_code", "nullable_enum", True),
        ("obligation_id", "opaque_id", True),
    ],
    "cue_obligation": [
        ("obligation_id", "opaque_id", False),
        ("partition_id", "digest", False),
        ("consumer_scope", "enum", False),
        ("source_epoch_digest", "digest", False),
        ("from_position", "positive_integer", False),
        ("through_position", "positive_integer", False),
        ("reason_code", "enum", False),
        ("fresh_authorized_read_required", "boolean", False),
        ("state", "enum", False),
    ],
    "consumer_checkpoint": [
        ("partition_id", "digest", False),
        ("consumer_scope", "enum", False),
        ("source_epoch_digest", "digest", False),
        ("checkpoint_state", "enum", False),
        ("checkpoint_position", "nullable_positive_integer", True),
        ("lease_generation", "positive_integer", False),
    ],
    "dispatch_attempt": [
        ("obligation_id", "opaque_id", False),
        ("attempt_ordinal", "positive_integer", False),
        ("lease_generation", "positive_integer", False),
        ("outcome", "enum", False),
        ("failure_class", "nullable_enum", True),
    ],
    "reconciliation_receipt": [
        ("reconciliation_id", "opaque_id", False),
        ("obligation_id", "opaque_id", False),
        ("dispatch_attempt_ordinal", "positive_integer", False),
        ("outcome", "enum", False),
        ("scope_authorized", "boolean", False),
        ("fresh_read_performed", "boolean", False),
        ("acknowledgement", "enum", False),
        ("display_disposition", "enum", False),
    ],
}

CHECK_BINDINGS: dict[str, list[tuple[str, str, str | None]]] = {
    "event_partition": [
        ("partition_id_matches_exact_partition_tuple_digest", "sql_check_constraint", "ck_event_partition_identity"),
        ("lease_generation_positive", "sql_check_constraint", "ck_event_partition_generation"),
    ],
    "observer_coordinate": [
        ("observed_none_iff_position_null", "sql_check_constraint", "ck_observer_coordinate_observed_shape"),
        ("source_head_state_matches_nullable_coordinate", "sql_check_constraint", "ck_observer_coordinate_head_shape"),
        ("coordinate_is_non_authoritative", "inert_semantic_annotation", None),
    ],
    "terminal_receipt": [
        ("classification_reason_and_obligation_shape_exact", "sql_check_constraint", "ck_terminal_receipt_classification_shape"),
        ("source_position_positive", "sql_check_constraint", "ck_terminal_receipt_position"),
    ],
    "cue_obligation": [
        ("range_positive_and_ordered", "sql_check_constraint", "ck_cue_obligation_range"),
        ("consumer_and_reason_allowlisted", "sql_check_constraint", "ck_cue_obligation_scope_reason"),
        ("fresh_authorized_read_literal_true", "sql_check_constraint", "ck_cue_obligation_fresh_read"),
        ("state_pending_or_delivered", "sql_check_constraint", "ck_cue_obligation_state"),
    ],
    "consumer_checkpoint": [
        ("checkpoint_none_iff_position_null", "sql_check_constraint", "ck_consumer_checkpoint_shape"),
        ("lease_generation_positive", "sql_check_constraint", "ck_consumer_checkpoint_generation"),
    ],
    "dispatch_attempt": [
        ("attempt_ordinal_positive", "sql_check_constraint", "ck_dispatch_attempt_ordinal"),
        ("dispatch_outcome_failure_shape_exact", "sql_check_constraint", "ck_dispatch_attempt_outcome"),
        ("lease_generation_positive", "sql_check_constraint", "ck_dispatch_attempt_generation"),
    ],
    "reconciliation_receipt": [
        ("reconciliation_truth_table_exact", "sql_check_constraint", "ck_reconciliation_receipt_truth_table"),
        ("acknowledgement_one_fresh_read_attempt_only", "sql_check_constraint", "ck_reconciliation_receipt_acknowledgement"),
        ("display_disposition_matches_outcome", "sql_check_constraint", "ck_reconciliation_receipt_display"),
    ],
}

REFERENCE_NAMES = [
    "fk_observer_coordinate_partition",
    "fk_terminal_receipt_partition",
    "fk_terminal_receipt_obligation",
    "fk_cue_obligation_partition",
    "fk_consumer_checkpoint_partition",
    "fk_dispatch_attempt_obligation",
    "fk_reconciliation_receipt_attempt",
]

FORBIDDEN_LINE_STARTS = (
    "BEGIN", "COMMIT", "ROLLBACK", "SAVEPOINT", "DO", "COPY", "INSERT",
    "UPDATE", "DELETE", "TRUNCATE", "MERGE", "CREATE FUNCTION",
    "CREATE PROCEDURE", "CREATE TRIGGER", "CREATE RULE", "CREATE ROLE",
    "GRANT", "REVOKE", "CREATE EXTENSION", "ALTER SYSTEM", "SET ROLE",
)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _parent_field_shape(relation: dict[str, Any]) -> list[tuple[str, str, bool]]:
    return [
        (field["name"], field["type"], field["nullable"])
        for field in relation["fields"]
    ]


def validate_inputs(
    contract: dict[str, Any],
    contract_schema: dict[str, Any],
    parent: dict[str, Any],
    parent_schema: dict[str, Any],
) -> list[str]:
    errors = [
        f"lowering_schema:{error.message}"
        for error in sorted(
            Draft202012Validator(contract_schema).iter_errors(contract), key=str
        )
    ]
    errors.extend(
        f"parent_schema:{error.message}"
        for error in sorted(
            Draft202012Validator(parent_schema).iter_errors(parent), key=str
        )
    )
    if errors:
        return errors
    if _sha256_path(PARENT_PATH) != PARENT_SHA256:
        errors.append("accepted_representation_contract_hash_mismatch")
    if contract["accepted_representation_contract_sha256"] != PARENT_SHA256:
        errors.append("lowering_parent_hash_binding_mismatch")
    if ROOT / contract["accepted_representation_contract_path"] != PARENT_PATH:
        errors.append("lowering_parent_path_binding_mismatch")
    expected_outputs = {
        "sql": SQL_PATH,
        "manifest": MANIFEST_PATH,
        "evidence": EVIDENCE_PATH,
    }
    for key, expected in expected_outputs.items():
        if ROOT / contract["output_paths"][key] != expected:
            errors.append(f"output_path_mismatch:{key}")

    relations = parent["relations"]
    if [relation["name"] for relation in relations] != list(EXPECTED_FIELDS):
        errors.append("parent_relation_order_or_census_mismatch")
    for relation in relations:
        name = relation["name"]
        if _parent_field_shape(relation) != EXPECTED_FIELDS.get(name):
            errors.append(f"parent_field_shape_mismatch:{name}")
        expected_checks = [item[0] for item in CHECK_BINDINGS.get(name, [])]
        if relation["checks"] != expected_checks:
            errors.append(f"parent_check_order_or_census_mismatch:{name}")
    if sum(len(fields) for fields in EXPECTED_FIELDS.values()) != 50:
        errors.append("internal_field_census_mismatch")
    if sum(len(items) for items in CHECK_BINDINGS.values()) != 19:
        errors.append("internal_check_census_mismatch")
    if sum(item[1] == "sql_check_constraint" for items in CHECK_BINDINGS.values() for item in items) != 18:
        errors.append("internal_sql_check_census_mismatch")
    if [p["name"] for p in parent["transaction_protocols"]] != [
        "admit_terminal", "coalesce_pending", "advance_contiguous_checkpoint",
        "record_dispatch_attempt", "record_reconciliation",
    ]:
        errors.append("parent_transaction_protocol_census_mismatch")
    if contract["unlowered_enforcement_classes"] != [
        "transaction_protocol", "external_authority"
    ]:
        errors.append("unlowered_enforcement_boundary_mismatch")
    return errors


def render_sql(parent: dict[str, Any]) -> str:
    mutable = {
        relation["name"]: ",".join(relation["mutable_fields"]) or "none"
        for relation in parent["relations"]
    }
    return f"""-- EMR4 CF-D2 INERT POSTGRESQL-16 DDL TEXT — DO NOT EXECUTE AS A MIGRATION
-- evidence_label: provider_free_unmounted_inert_postgresql_16_ddl_text
-- accepted_representation_sha256: {PARENT_SHA256}

-- phase 1: dedicated schema and scalar domains
CREATE SCHEMA {SCHEMA_NAME};

CREATE DOMAIN {SCHEMA_NAME}.digest_v1 AS pg_catalog.text
    CONSTRAINT ck_digest_v1_format
    CHECK (VALUE ~ '^sha256:[0-9a-f]{{64}}$');

CREATE DOMAIN {SCHEMA_NAME}.opaque_id_v1 AS pg_catalog.text
    CONSTRAINT ck_opaque_id_v1_nonempty
    CHECK (pg_catalog.char_length(VALUE) > 0);

CREATE DOMAIN {SCHEMA_NAME}.positive_integer_v1 AS pg_catalog.int8
    CONSTRAINT ck_positive_integer_v1_above_zero
    CHECK (VALUE > 0);

-- phase 2: exact seven relations in accepted order
-- relation event_partition mutable_fields={mutable['event_partition']} ddl_enforced=false
CREATE TABLE {SCHEMA_NAME}.event_partition (
    partition_id {SCHEMA_NAME}.digest_v1 NOT NULL,
    source_system pg_catalog.text NOT NULL,
    practice_scope_digest {SCHEMA_NAME}.digest_v1 NOT NULL,
    event_family pg_catalog.text NOT NULL,
    source_epoch_digest {SCHEMA_NAME}.digest_v1 NOT NULL,
    lease_generation {SCHEMA_NAME}.positive_integer_v1 NOT NULL,
    CONSTRAINT pk_event_partition PRIMARY KEY (partition_id),
    CONSTRAINT uq_event_partition_scope UNIQUE (source_system, practice_scope_digest, event_family),
    CONSTRAINT ck_event_partition_identity CHECK (
        source_system = 'emr4_diary'
        AND event_family = 'diary_appointment_change'
        AND partition_id = 'sha256:' || pg_catalog.encode(
            pg_catalog.sha256(pg_catalog.convert_to(
                source_system || '|' || practice_scope_digest || '|' || event_family,
                'UTF8'
            )),
            'hex'
        )
    ),
    CONSTRAINT ck_event_partition_generation CHECK (lease_generation > 0)
);

-- relation observer_coordinate mutable_fields={mutable['observer_coordinate']} ddl_enforced=false
-- semantic assertion coordinate_is_non_authoritative sql_enforced=false
CREATE TABLE {SCHEMA_NAME}.observer_coordinate (
    partition_id {SCHEMA_NAME}.digest_v1 NOT NULL,
    consumer_scope pg_catalog.text NOT NULL,
    source_epoch_digest {SCHEMA_NAME}.digest_v1 NOT NULL,
    observed_state pg_catalog.text NOT NULL,
    observed_position {SCHEMA_NAME}.positive_integer_v1,
    source_head_state pg_catalog.text NOT NULL,
    source_head_epoch_digest {SCHEMA_NAME}.digest_v1,
    source_head_position {SCHEMA_NAME}.positive_integer_v1,
    CONSTRAINT pk_observer_coordinate PRIMARY KEY (partition_id, consumer_scope),
    CONSTRAINT ck_observer_coordinate_observed_shape CHECK (
        consumer_scope = 'reception_one_diary_projection'
        AND (
            (observed_state = 'none' AND observed_position IS NULL)
            OR (observed_state = 'exact' AND observed_position IS NOT NULL)
        )
    ),
    CONSTRAINT ck_observer_coordinate_head_shape CHECK (
        (source_head_state = 'unknown' AND source_head_epoch_digest IS NULL AND source_head_position IS NULL)
        OR (source_head_state = 'exact' AND source_head_epoch_digest = source_epoch_digest AND source_head_position IS NOT NULL)
        OR (source_head_state = 'epoch_mismatch' AND source_head_epoch_digest IS NOT NULL AND source_head_epoch_digest <> source_epoch_digest AND source_head_position IS NOT NULL)
    )
);

-- relation terminal_receipt mutable_fields={mutable['terminal_receipt']} ddl_enforced=false
CREATE TABLE {SCHEMA_NAME}.terminal_receipt (
    receipt_id {SCHEMA_NAME}.opaque_id_v1 NOT NULL,
    partition_id {SCHEMA_NAME}.digest_v1 NOT NULL,
    source_epoch_digest {SCHEMA_NAME}.digest_v1 NOT NULL,
    source_position {SCHEMA_NAME}.positive_integer_v1 NOT NULL,
    event_fingerprint_digest {SCHEMA_NAME}.digest_v1 NOT NULL,
    classification pg_catalog.text NOT NULL,
    reason_code pg_catalog.text,
    obligation_id {SCHEMA_NAME}.opaque_id_v1,
    CONSTRAINT pk_terminal_receipt PRIMARY KEY (receipt_id),
    CONSTRAINT uq_terminal_receipt_position UNIQUE (partition_id, source_epoch_digest, source_position),
    CONSTRAINT ck_terminal_receipt_classification_shape CHECK (
        (classification = 'cue_required' AND reason_code IN ('diary_status_may_have_changed', 'diary_availability_may_have_changed') AND obligation_id IS NOT NULL)
        OR (classification = 'suppressed_irrelevant' AND reason_code IS NULL AND obligation_id IS NULL)
        OR (classification = 'rejected_unsupported' AND reason_code IN ('unsupported_event_schema', 'unsupported_event_family', 'policy_rejected') AND obligation_id IS NULL)
    ),
    CONSTRAINT ck_terminal_receipt_position CHECK (source_position > 0)
);

-- relation cue_obligation mutable_fields={mutable['cue_obligation']} ddl_enforced=false
CREATE TABLE {SCHEMA_NAME}.cue_obligation (
    obligation_id {SCHEMA_NAME}.opaque_id_v1 NOT NULL,
    partition_id {SCHEMA_NAME}.digest_v1 NOT NULL,
    consumer_scope pg_catalog.text NOT NULL,
    source_epoch_digest {SCHEMA_NAME}.digest_v1 NOT NULL,
    from_position {SCHEMA_NAME}.positive_integer_v1 NOT NULL,
    through_position {SCHEMA_NAME}.positive_integer_v1 NOT NULL,
    reason_code pg_catalog.text NOT NULL,
    fresh_authorized_read_required pg_catalog.bool NOT NULL,
    state pg_catalog.text NOT NULL,
    CONSTRAINT pk_cue_obligation PRIMARY KEY (obligation_id),
    CONSTRAINT ck_cue_obligation_range CHECK (from_position > 0 AND through_position >= from_position),
    CONSTRAINT ck_cue_obligation_scope_reason CHECK (
        consumer_scope = 'reception_one_diary_projection'
        AND reason_code IN ('diary_status_may_have_changed', 'diary_availability_may_have_changed')
    ),
    CONSTRAINT ck_cue_obligation_fresh_read CHECK (fresh_authorized_read_required IS TRUE),
    CONSTRAINT ck_cue_obligation_state CHECK (state IN ('pending', 'delivered'))
);

-- relation consumer_checkpoint mutable_fields={mutable['consumer_checkpoint']} ddl_enforced=false
CREATE TABLE {SCHEMA_NAME}.consumer_checkpoint (
    partition_id {SCHEMA_NAME}.digest_v1 NOT NULL,
    consumer_scope pg_catalog.text NOT NULL,
    source_epoch_digest {SCHEMA_NAME}.digest_v1 NOT NULL,
    checkpoint_state pg_catalog.text NOT NULL,
    checkpoint_position {SCHEMA_NAME}.positive_integer_v1,
    lease_generation {SCHEMA_NAME}.positive_integer_v1 NOT NULL,
    CONSTRAINT pk_consumer_checkpoint PRIMARY KEY (partition_id, consumer_scope, source_epoch_digest),
    CONSTRAINT ck_consumer_checkpoint_shape CHECK (
        consumer_scope = 'reception_one_diary_projection'
        AND (
            (checkpoint_state = 'none' AND checkpoint_position IS NULL)
            OR (checkpoint_state = 'exact' AND checkpoint_position IS NOT NULL)
        )
    ),
    CONSTRAINT ck_consumer_checkpoint_generation CHECK (lease_generation > 0)
);

-- relation dispatch_attempt mutable_fields={mutable['dispatch_attempt']} ddl_enforced=false
CREATE TABLE {SCHEMA_NAME}.dispatch_attempt (
    obligation_id {SCHEMA_NAME}.opaque_id_v1 NOT NULL,
    attempt_ordinal {SCHEMA_NAME}.positive_integer_v1 NOT NULL,
    lease_generation {SCHEMA_NAME}.positive_integer_v1 NOT NULL,
    outcome pg_catalog.text NOT NULL,
    failure_class pg_catalog.text,
    CONSTRAINT pk_dispatch_attempt PRIMARY KEY (obligation_id, attempt_ordinal),
    CONSTRAINT ck_dispatch_attempt_ordinal CHECK (attempt_ordinal > 0),
    CONSTRAINT ck_dispatch_attempt_outcome CHECK (
        (outcome = 'delivered' AND failure_class IS NULL)
        OR (outcome = 'failed' AND failure_class IN ('consumer_unavailable', 'authorization_rejected', 'transient_transport'))
    ),
    CONSTRAINT ck_dispatch_attempt_generation CHECK (lease_generation > 0)
);

-- relation reconciliation_receipt mutable_fields={mutable['reconciliation_receipt']} ddl_enforced=false
CREATE TABLE {SCHEMA_NAME}.reconciliation_receipt (
    reconciliation_id {SCHEMA_NAME}.opaque_id_v1 NOT NULL,
    obligation_id {SCHEMA_NAME}.opaque_id_v1 NOT NULL,
    dispatch_attempt_ordinal {SCHEMA_NAME}.positive_integer_v1 NOT NULL,
    outcome pg_catalog.text NOT NULL,
    scope_authorized pg_catalog.bool NOT NULL,
    fresh_read_performed pg_catalog.bool NOT NULL,
    acknowledgement pg_catalog.text NOT NULL,
    display_disposition pg_catalog.text NOT NULL,
    CONSTRAINT pk_reconciliation_receipt PRIMARY KEY (reconciliation_id),
    CONSTRAINT uq_reconciliation_receipt_obligation UNIQUE (obligation_id),
    CONSTRAINT ck_reconciliation_receipt_truth_table CHECK (
        (outcome = 'projection_unchanged' AND scope_authorized IS TRUE AND fresh_read_performed IS TRUE AND display_disposition = 'unchanged')
        OR (outcome = 'projection_refreshed' AND scope_authorized IS TRUE AND fresh_read_performed IS TRUE AND display_disposition = 'refreshed')
        OR (outcome = 'local_selection_or_proposal_cleared' AND scope_authorized IS TRUE AND fresh_read_performed IS TRUE AND display_disposition = 'cleared')
        OR (outcome = 'authorization_rejected' AND scope_authorized IS FALSE AND fresh_read_performed IS FALSE AND display_disposition = 'unchanged')
        OR (outcome = 'source_unavailable' AND scope_authorized IS TRUE AND fresh_read_performed IS FALSE AND display_disposition = 'unchanged')
        OR (outcome = 'stale_session' AND scope_authorized IS FALSE AND fresh_read_performed IS FALSE AND display_disposition = 'unchanged')
    ),
    CONSTRAINT ck_reconciliation_receipt_acknowledgement CHECK (acknowledgement = 'one_fresh_read_attempt_only'),
    CONSTRAINT ck_reconciliation_receipt_display CHECK (display_disposition IN ('unchanged', 'refreshed', 'cleared'))
);

-- phase 3: exact references after all accepted-order tables exist
ALTER TABLE {SCHEMA_NAME}.observer_coordinate
    ADD CONSTRAINT fk_observer_coordinate_partition
    FOREIGN KEY (partition_id) REFERENCES {SCHEMA_NAME}.event_partition (partition_id);

ALTER TABLE {SCHEMA_NAME}.terminal_receipt
    ADD CONSTRAINT fk_terminal_receipt_partition
    FOREIGN KEY (partition_id) REFERENCES {SCHEMA_NAME}.event_partition (partition_id);

ALTER TABLE {SCHEMA_NAME}.terminal_receipt
    ADD CONSTRAINT fk_terminal_receipt_obligation
    FOREIGN KEY (obligation_id) REFERENCES {SCHEMA_NAME}.cue_obligation (obligation_id)
    DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE {SCHEMA_NAME}.cue_obligation
    ADD CONSTRAINT fk_cue_obligation_partition
    FOREIGN KEY (partition_id) REFERENCES {SCHEMA_NAME}.event_partition (partition_id);

ALTER TABLE {SCHEMA_NAME}.consumer_checkpoint
    ADD CONSTRAINT fk_consumer_checkpoint_partition
    FOREIGN KEY (partition_id) REFERENCES {SCHEMA_NAME}.event_partition (partition_id);

ALTER TABLE {SCHEMA_NAME}.dispatch_attempt
    ADD CONSTRAINT fk_dispatch_attempt_obligation
    FOREIGN KEY (obligation_id) REFERENCES {SCHEMA_NAME}.cue_obligation (obligation_id);

ALTER TABLE {SCHEMA_NAME}.reconciliation_receipt
    ADD CONSTRAINT fk_reconciliation_receipt_attempt
    FOREIGN KEY (obligation_id, dispatch_attempt_ordinal)
    REFERENCES {SCHEMA_NAME}.dispatch_attempt (obligation_id, attempt_ordinal);

-- phase 4: transaction protocols and external authority remain deliberately unlowered
-- admit_terminal sql_enforced=false
-- coalesce_pending sql_enforced=false
-- advance_contiguous_checkpoint sql_enforced=false
-- record_dispatch_attempt sql_enforced=false
-- record_reconciliation sql_enforced=false
-- current source truth and command authority remain external
"""


def build_manifest(parent: dict[str, Any], sql: str) -> dict[str, Any]:
    relations = []
    for relation in parent["relations"]:
        relations.append(
            {
                "name": relation["name"],
                "fields": copy.deepcopy(relation["fields"]),
                "primary_key": relation["primary_key"],
                "unique_keys": relation["unique_keys"],
                "reference_count": len(relation["references"]),
                "mutable_fields": relation["mutable_fields"],
                "mutable_fields_enforced_by_ddl": False,
            }
        )
    checks = [
        {
            "relation": relation,
            "label": label,
            "disposition": disposition,
            "constraint_name": constraint,
        }
        for relation, bindings in CHECK_BINDINGS.items()
        for label, disposition, constraint in bindings
    ]
    return {
        "schema_version": "raisa.context_fabric.unmounted_event_cue_inert_ddl.manifest.v1",
        "status": "inert_sql_text_rendered_static_admission_only",
        "evidence_label": "provider_free_unmounted_inert_postgresql_16_ddl_text",
        "postgresql_major_target": 16,
        "accepted_representation_source": "16ec7993ee3c46d83772f47aa7dab61fc1fcb7ed",
        "accepted_representation_contract_sha256": PARENT_SHA256,
        "sql_artifact_path": SQL_PATH.relative_to(ROOT).as_posix(),
        "sql_artifact_sha256": _sha256_bytes(sql.encode("utf-8")),
        "sql_byte_count": len(sql.encode("utf-8")),
        "sql_line_count": len(sql.splitlines()),
        "statement_count": sql.count(";\n"),
        "schema_name": SCHEMA_NAME,
        "domain_names": ["digest_v1", "opaque_id_v1", "positive_integer_v1"],
        "relations": relations,
        "check_bindings": checks,
        "reference_constraint_names": REFERENCE_NAMES,
        "transaction_protocols": [
            {"name": protocol["name"], "disposition": "unlowered_transaction_protocol", "proved_by_ddl": False}
            for protocol in parent["transaction_protocols"]
        ],
        "external_authority": {
            "disposition": "unlowered_external_authority",
            "proved_by_ddl": False,
            "source_owns_current_truth": True,
            "fresh_authorized_scoped_read_required": True,
            "command_rechecks_current_authority_and_source_truth": True,
        },
        "effects": {
            "sql_or_migration_executed": False,
            "database_or_source_opened": False,
            "operational_state_persisted": False,
            "runtime_started": False,
            "provider_calls": 0,
            "command_or_write": False,
            "product_patient_or_clinical_data": False,
        },
    }


def recognize_candidate(
    candidate: str, canonical: str, manifest: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if candidate != canonical:
        errors.append("candidate_not_byte_identical_to_canonical_render")
    if "\r" in candidate or "\x00" in candidate:
        errors.append("encoding_or_control_character_invalid")
    if not candidate.startswith("-- EMR4 CF-D2 INERT POSTGRESQL-16 DDL TEXT"):
        errors.append("inert_header_missing")
    if candidate.count(";\n") != 18:
        errors.append("statement_count_mismatch")
    if candidate.count(f"CREATE DOMAIN {SCHEMA_NAME}.") != 3:
        errors.append("domain_count_mismatch")
    table_names = re.findall(
        rf"^CREATE TABLE {re.escape(SCHEMA_NAME)}\.([a-z_]+) \($",
        candidate,
        flags=re.MULTILINE,
    )
    if table_names != list(EXPECTED_FIELDS):
        errors.append("relation_order_or_census_mismatch")
    if candidate.count(" PRIMARY KEY (") != 7:
        errors.append("primary_key_count_mismatch")
    if candidate.count(" UNIQUE (") != 3:
        errors.append("unique_key_count_mismatch")
    if candidate.count("    FOREIGN KEY (") != 7:
        errors.append("reference_count_mismatch")
    for relation, bindings in CHECK_BINDINGS.items():
        for label, disposition, constraint in bindings:
            if disposition == "sql_check_constraint":
                if candidate.count(f"CONSTRAINT {constraint} CHECK") != 1:
                    errors.append(f"check_constraint_mismatch:{relation}:{label}")
            elif candidate.count(
                f"semantic assertion {label} sql_enforced=false"
            ) != 1:
                errors.append(f"semantic_annotation_mismatch:{relation}:{label}")
    for reference in REFERENCE_NAMES:
        if candidate.count(f"ADD CONSTRAINT {reference}") != 1:
            errors.append(f"reference_constraint_mismatch:{reference}")
    for relation in manifest["relations"]:
        mutable = ",".join(relation["mutable_fields"]) or "none"
        marker = f"relation {relation['name']} mutable_fields={mutable} ddl_enforced=false"
        if candidate.count(marker) != 1:
            errors.append(f"mutability_annotation_mismatch:{relation['name']}")
        if relation["mutable_fields_enforced_by_ddl"] is not False:
            errors.append(f"mutability_enforcement_overclaim:{relation['name']}")
    for protocol in manifest["transaction_protocols"]:
        marker = f"-- {protocol['name']} sql_enforced=false"
        if candidate.count(marker) != 1 or protocol["proved_by_ddl"] is not False:
            errors.append(f"transaction_protocol_overclaim:{protocol['name']}")
    for prefix in FORBIDDEN_LINE_STARTS:
        if re.search(rf"^{re.escape(prefix)}(?:\s|;)", candidate, re.MULTILINE | re.IGNORECASE):
            errors.append(f"forbidden_statement_family:{prefix}")
    for forbidden in ("IF NOT EXISTS", "\\connect", "\\i ", "alembic", "jsonb", "bytea"):
        if forbidden.lower() in candidate.lower():
            errors.append(f"forbidden_sql_fragment:{forbidden}")
    if _sha256_bytes(candidate.encode("utf-8")) != manifest["sql_artifact_sha256"]:
        errors.append("manifest_sql_digest_mismatch")
    if len(candidate.encode("utf-8")) != manifest["sql_byte_count"]:
        errors.append("manifest_sql_byte_count_mismatch")
    if manifest["statement_count"] != 18:
        errors.append("manifest_statement_count_mismatch")
    return sorted(set(errors))


def hostile_candidates(sql: str) -> dict[str, str]:
    hostile: dict[str, str] = {}
    statements = re.findall(
        r"(?ms)^(?:CREATE SCHEMA|CREATE DOMAIN|CREATE TABLE|ALTER TABLE).*?;\n",
        sql,
    )
    for index, statement in enumerate(statements):
        hostile[f"remove_statement_{index:02d}"] = sql.replace(statement, "", 1)
    for name in EXPECTED_FIELDS:
        hostile[f"rename_relation_{name}"] = sql.replace(name, f"x_{name}", 1)
    for bindings in CHECK_BINDINGS.values():
        for label, disposition, constraint in bindings:
            marker = constraint if constraint is not None else label
            hostile[f"change_check_{marker}"] = sql.replace(marker, f"x_{marker}", 1)
    additions = {
        "add_begin": "BEGIN;\n",
        "add_commit": "COMMIT;\n",
        "add_insert": "INSERT INTO x VALUES (1);\n",
        "add_update": "UPDATE x SET y = 1;\n",
        "add_delete": "DELETE FROM x;\n",
        "add_function": "CREATE FUNCTION x() RETURNS void LANGUAGE sql AS 'SELECT 1';\n",
        "add_trigger": "CREATE TRIGGER x AFTER INSERT ON x EXECUTE FUNCTION x();\n",
        "add_role": "CREATE ROLE x;\n",
        "add_grant": "GRANT ALL ON SCHEMA x TO PUBLIC;\n",
        "add_extension": "CREATE EXTENSION pgcrypto;\n",
        "add_copy": "COPY x TO '/tmp/x';\n",
        "add_connect": "\\connect product\n",
        "add_jsonb": "-- jsonb payload\n",
        "add_bytea": "-- bytea payload\n",
        "add_if_not_exists": "-- IF NOT EXISTS\n",
    }
    for name, addition in additions.items():
        hostile[name] = sql + addition
    hostile["crlf"] = sql.replace("\n", "\r\n")
    hostile["missing_header"] = sql.replace("-- EMR4 CF-D2 INERT", "-- altered", 1)
    hostile["nullable_required_field"] = sql.replace("partition_id emr4_context_fabric_cue.digest_v1 NOT NULL", "partition_id emr4_context_fabric_cue.digest_v1", 1)
    hostile["payload_column"] = sql.replace("    lease_generation", "    event_payload pg_catalog.text,\n    lease_generation", 1)
    hostile["transaction_claim"] = sql.replace("admit_terminal sql_enforced=false", "admit_terminal sql_enforced=true", 1)
    hostile["mutability_claim"] = sql.replace("ddl_enforced=false", "ddl_enforced=true", 1)
    return hostile


def build_evidence(
    input_errors: list[str],
    recognition_errors: list[str],
    sql: str,
    manifest: dict[str, Any],
    hostile: dict[str, str],
) -> dict[str, Any]:
    admitted_hostiles = [
        name
        for name, candidate in hostile.items()
        if not recognize_candidate(candidate, sql, manifest)
    ]
    return {
        "schema_version": "raisa.context_fabric.unmounted_event_cue_inert_ddl.evidence.v1",
        "status": "passed" if not input_errors and not recognition_errors and not admitted_hostiles else "failed",
        "evidence_label": "provider_free_unmounted_inert_postgresql_16_ddl_text",
        "accepted_representation_source": "16ec7993ee3c46d83772f47aa7dab61fc1fcb7ed",
        "accepted_representation_contract_sha256": PARENT_SHA256,
        "input_errors": input_errors,
        "recognition_errors": recognition_errors,
        "sql_artifact_sha256": manifest["sql_artifact_sha256"],
        "manifest_sha256": _sha256_bytes(_canonical_json(manifest)),
        "isolated_renders_byte_identical": True,
        "canonical_sql_unchanged_during_hostile_evaluation": True,
        "canonical_manifest_unchanged_during_hostile_evaluation": True,
        "relation_count": len(manifest["relations"]),
        "field_count": sum(len(relation["fields"]) for relation in manifest["relations"]),
        "primary_key_count": 7,
        "unique_key_count": 3,
        "reference_count": len(manifest["reference_constraint_names"]),
        "relation_check_label_count": len(manifest["check_bindings"]),
        "sql_check_binding_count": sum(binding["disposition"] == "sql_check_constraint" for binding in manifest["check_bindings"]),
        "semantic_annotation_count": sum(binding["disposition"] == "inert_semantic_annotation" for binding in manifest["check_bindings"]),
        "transaction_protocol_count": len(manifest["transaction_protocols"]),
        "hostile_candidate_count": len(hostile),
        "hostile_rejection_count": len(hostile) - len(admitted_hostiles),
        "admitted_hostiles": admitted_hostiles,
        "sql_or_migration_executed": False,
        "database_or_source_opened": False,
        "operational_state_persisted": False,
        "runtime_started": False,
        "provider_calls": 0,
        "command_or_write": False,
        "product_patient_or_clinical_data": False,
    }


def run(*, write: bool) -> dict[str, Any]:
    contract = _json(CONTRACT_PATH)
    contract_schema = _json(CONTRACT_SCHEMA_PATH)
    parent = _json(PARENT_PATH)
    parent_schema = _json(PARENT_SCHEMA_PATH)
    input_errors = validate_inputs(contract, contract_schema, parent, parent_schema)
    sql = render_sql(parent)
    second_sql = render_sql(copy.deepcopy(parent))
    if second_sql != sql:
        input_errors.append("isolated_render_mismatch")
    manifest = build_manifest(parent, sql)
    recognition_errors = recognize_candidate(sql, sql, manifest)
    hostile = hostile_candidates(sql)
    evidence = build_evidence(input_errors, recognition_errors, sql, manifest, hostile)
    if len(hostile) < 64:
        evidence["status"] = "failed"
        evidence["input_errors"].append("hostile_census_below_64")
    if write:
        CONTINUITY.mkdir(parents=True, exist_ok=True)
        SQL_PATH.write_bytes(sql.encode("utf-8"))
        MANIFEST_PATH.write_bytes(_canonical_json(manifest))
        EVIDENCE_PATH.write_bytes(_canonical_json(evidence))
    else:
        expected = {
            SQL_PATH: sql.encode("utf-8"),
            MANIFEST_PATH: _canonical_json(manifest),
            EVIDENCE_PATH: _canonical_json(evidence),
        }
        for path, data in expected.items():
            if not path.exists() or path.read_bytes() != data:
                evidence["status"] = "failed"
                evidence["input_errors"].append(f"committed_artifact_mismatch:{path.name}")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write only the fixed canonical continuity artifacts")
    args = parser.parse_args()
    evidence = run(write=args.write)
    print(json.dumps(evidence, sort_keys=True))
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
