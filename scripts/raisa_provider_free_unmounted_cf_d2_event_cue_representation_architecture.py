"""Validate the inert CF-D2 event/cue relational representation.

This module performs repository-local JSON and Python-object checks only. It
does not render SQL, import a database driver, open a connection, start a
process, observe a source, or persist operational state.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture"
)
CONTRACT_PATH = CONTINUITY / "representation-contract.json"
SCHEMA_PATH = CONTINUITY / "representation-contract.schema.json"
DEFAULT_OUTPUT = CONTINUITY / "provider-free-unmounted-representation-evidence.json"

CONSUMER_SCOPE = "reception_one_diary_projection"
SOURCE_SYSTEM = "emr4_diary"
EVENT_FAMILY = "diary_appointment_change"
CUE_REASONS = {
    "diary_status_may_have_changed",
    "diary_availability_may_have_changed",
}
REJECTION_REASONS = {
    "unsupported_event_schema",
    "unsupported_event_family",
    "policy_rejected",
}
RECONCILIATION_SHAPES = {
    "projection_unchanged": (True, True, "unchanged"),
    "projection_refreshed": (True, True, "refreshed"),
    "local_selection_or_proposal_cleared": (True, True, "cleared"),
    "authorization_rejected": (False, False, "unchanged"),
    "source_unavailable": (True, False, "unchanged"),
    "stale_session": (False, False, "unchanged"),
}

EXPECTED_RELATIONS: dict[str, dict[str, Any]] = {
    "event_partition": {
        "fields": [
            ("partition_id", "digest", False),
            ("source_system", "enum", False),
            ("practice_scope_digest", "digest", False),
            ("event_family", "enum", False),
            ("source_epoch_digest", "digest", False),
            ("lease_generation", "positive_integer", False),
        ],
        "primary_key": ["partition_id"],
        "unique_keys": [["source_system", "practice_scope_digest", "event_family"]],
        "reference_targets": [],
        "checks": [
            "partition_id_matches_exact_partition_tuple_digest",
            "lease_generation_positive",
        ],
        "mutable_fields": ["source_epoch_digest", "lease_generation"],
    },
    "observer_coordinate": {
        "fields": [
            ("partition_id", "digest", False),
            ("consumer_scope", "enum", False),
            ("source_epoch_digest", "digest", False),
            ("observed_state", "enum", False),
            ("observed_position", "nullable_positive_integer", True),
            ("source_head_state", "enum", False),
            ("source_head_epoch_digest", "nullable_digest", True),
            ("source_head_position", "nullable_positive_integer", True),
        ],
        "primary_key": ["partition_id", "consumer_scope"],
        "unique_keys": [],
        "reference_targets": [("event_partition", ("partition_id",))],
        "checks": [
            "observed_none_iff_position_null",
            "source_head_state_matches_nullable_coordinate",
            "coordinate_is_non_authoritative",
        ],
        "mutable_fields": [
            "source_epoch_digest",
            "observed_state",
            "observed_position",
            "source_head_state",
            "source_head_epoch_digest",
            "source_head_position",
        ],
    },
    "terminal_receipt": {
        "fields": [
            ("receipt_id", "opaque_id", False),
            ("partition_id", "digest", False),
            ("source_epoch_digest", "digest", False),
            ("source_position", "positive_integer", False),
            ("event_fingerprint_digest", "digest", False),
            ("classification", "enum", False),
            ("reason_code", "nullable_enum", True),
            ("obligation_id", "opaque_id", True),
        ],
        "primary_key": ["receipt_id"],
        "unique_keys": [["partition_id", "source_epoch_digest", "source_position"]],
        "reference_targets": [
            ("event_partition", ("partition_id",)),
            ("cue_obligation", ("obligation_id",)),
        ],
        "checks": [
            "classification_reason_and_obligation_shape_exact",
            "source_position_positive",
        ],
        "mutable_fields": [],
    },
    "cue_obligation": {
        "fields": [
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
        "primary_key": ["obligation_id"],
        "unique_keys": [],
        "reference_targets": [("event_partition", ("partition_id",))],
        "checks": [
            "range_positive_and_ordered",
            "consumer_and_reason_allowlisted",
            "fresh_authorized_read_literal_true",
            "state_pending_or_delivered",
        ],
        "mutable_fields": ["through_position", "state"],
    },
    "consumer_checkpoint": {
        "fields": [
            ("partition_id", "digest", False),
            ("consumer_scope", "enum", False),
            ("source_epoch_digest", "digest", False),
            ("checkpoint_state", "enum", False),
            ("checkpoint_position", "nullable_positive_integer", True),
            ("lease_generation", "positive_integer", False),
        ],
        "primary_key": ["partition_id", "consumer_scope", "source_epoch_digest"],
        "unique_keys": [],
        "reference_targets": [("event_partition", ("partition_id",))],
        "checks": ["checkpoint_none_iff_position_null", "lease_generation_positive"],
        "mutable_fields": ["checkpoint_state", "checkpoint_position", "lease_generation"],
    },
    "dispatch_attempt": {
        "fields": [
            ("obligation_id", "opaque_id", False),
            ("attempt_ordinal", "positive_integer", False),
            ("lease_generation", "positive_integer", False),
            ("outcome", "enum", False),
            ("failure_class", "nullable_enum", True),
        ],
        "primary_key": ["obligation_id", "attempt_ordinal"],
        "unique_keys": [],
        "reference_targets": [("cue_obligation", ("obligation_id",))],
        "checks": [
            "attempt_ordinal_positive",
            "dispatch_outcome_failure_shape_exact",
            "lease_generation_positive",
        ],
        "mutable_fields": [],
    },
    "reconciliation_receipt": {
        "fields": [
            ("reconciliation_id", "opaque_id", False),
            ("obligation_id", "opaque_id", False),
            ("dispatch_attempt_ordinal", "positive_integer", False),
            ("outcome", "enum", False),
            ("scope_authorized", "boolean", False),
            ("fresh_read_performed", "boolean", False),
            ("acknowledgement", "enum", False),
            ("display_disposition", "enum", False),
        ],
        "primary_key": ["reconciliation_id"],
        "unique_keys": [["obligation_id"]],
        "reference_targets": [("dispatch_attempt", ("obligation_id", "attempt_ordinal"))],
        "checks": [
            "reconciliation_truth_table_exact",
            "acknowledgement_one_fresh_read_attempt_only",
            "display_disposition_matches_outcome",
        ],
        "mutable_fields": [],
    },
}

EXPECTED_PROTOCOLS = {
    "admit_terminal": {
        "requires": [
            "current_lease_generation",
            "unique_position_resolution",
            "exact_duplicate_comparison",
            "receipt_and_required_obligation_same_transaction",
        ],
        "forbids": [
            "divergent_identity_mutation",
            "checkpoint_before_required_obligation",
        ],
    },
    "coalesce_pending": {
        "requires": [
            "current_lease_generation",
            "adjacent_range",
            "same_partition_epoch_consumer_and_reason",
            "obligation_state_pending",
        ],
        "forbids": [
            "delivered_obligation_mutation",
            "range_gap_or_overlap",
            "cross_reason_coalescing",
        ],
    },
    "advance_contiguous_checkpoint": {
        "requires": [
            "current_lease_generation",
            "next_position_terminal_receipt",
            "cue_required_position_covered_by_obligation",
        ],
        "forbids": ["gap_crossing", "delivery_prerequisite", "epoch_crossing"],
    },
    "record_dispatch_attempt": {
        "requires": [
            "current_lease_generation",
            "next_attempt_ordinal",
            "stable_failure_class_for_failed_outcome",
        ],
        "forbids": ["cue_payload_mutation", "delivered_to_pending_regression"],
    },
    "record_reconciliation": {
        "requires": [
            "delivered_dispatch_attempt",
            "exact_outcome_truth_table",
            "exact_duplicate_reuse",
        ],
        "forbids": [
            "conflicting_second_result",
            "future_freshness_claim",
            "direct_source_truth_mutation",
        ],
    },
}

EXPECTED_SCENARIOS = [
    "empty_partition",
    "one_required_pending",
    "same_reason_coalesced",
    "different_reason_separate",
    "out_of_order_gap_held",
    "gap_filled_checkpoint_advanced",
    "suppressed_without_obligation",
    "rejected_without_obligation",
    "dispatch_failed_pending",
    "dispatch_delivered",
    "reconciliation_refreshed",
    "reconciliation_failure_retains_display",
]


def _digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _field_shape(relation: dict[str, Any]) -> list[tuple[str, str, bool]]:
    return [
        (field["name"], field["type"], field["nullable"])
        for field in relation["fields"]
    ]


def _reference_targets(relation: dict[str, Any]) -> list[tuple[str, tuple[str, ...]]]:
    return [
        (reference["relation"], tuple(reference["target_fields"]))
        for reference in relation["references"]
    ]


def validate_contract(contract: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [
        f"schema:{error.message}"
        for error in sorted(Draft202012Validator(schema).iter_errors(contract), key=str)
    ]
    if errors:
        return errors

    if contract["planning_baseline"] != "784fdc4c0237e1c363676638d010b2bd4b033210":
        errors.append("planning_baseline_mismatch")
    if contract["accepted_observability_source"] != "e8677b54d1c339dcd14776ce8bf15e7db2980378":
        errors.append("observability_source_mismatch")
    if contract["accepted_admission_source"] != "a7c6f7a66b06fbc065ae8a6eede7fa8baaee1b6b":
        errors.append("admission_source_mismatch")

    expected_authority = {
        "source_owns_current_truth": True,
        "observer_coordinate_is_non_authoritative": True,
        "event_and_cue_are_acceleration_hints_only": True,
        "cue_may_update_display_directly": False,
        "fresh_authorized_scoped_read_required": True,
        "command_rechecks_current_authority_and_source_truth": True,
        "represented_row_may_assert_command_success_or_authority": False,
    }
    if contract["authority"] != expected_authority:
        errors.append("authority_boundary_mismatch")

    relations = contract["relations"]
    if [relation["name"] for relation in relations] != list(EXPECTED_RELATIONS):
        errors.append("relation_order_or_census_mismatch")
    relation_map = {relation["name"]: relation for relation in relations}
    for name, expected in EXPECTED_RELATIONS.items():
        relation = relation_map.get(name)
        if relation is None:
            continue
        if _field_shape(relation) != expected["fields"]:
            errors.append(f"{name}:field_shape_mismatch")
        for key in ("primary_key", "unique_keys", "checks", "mutable_fields"):
            if relation[key] != expected[key]:
                errors.append(f"{name}:{key}_mismatch")
        if _reference_targets(relation) != expected["reference_targets"]:
            errors.append(f"{name}:reference_target_mismatch")
        field_names = [field["name"] for field in relation["fields"]]
        for fragment in contract["prohibited_field_fragments"]:
            if any(fragment in field for field in field_names):
                errors.append(f"{name}:prohibited_field_fragment:{fragment}")

    protocols = {protocol["name"]: protocol for protocol in contract["transaction_protocols"]}
    if list(protocols) != list(EXPECTED_PROTOCOLS):
        errors.append("transaction_protocol_order_or_census_mismatch")
    for name, expected in EXPECTED_PROTOCOLS.items():
        protocol = protocols.get(name)
        if protocol is None:
            continue
        if protocol["requires"] != expected["requires"]:
            errors.append(f"{name}:requires_mismatch")
        if protocol["forbids"] != expected["forbids"]:
            errors.append(f"{name}:forbids_mismatch")

    if contract["representability_scenario_ids"] != EXPECTED_SCENARIOS:
        errors.append("scenario_census_mismatch")
    if set(contract["enforcement_classification"]) != {
        "row_constraint",
        "key_or_reference",
        "transaction_protocol",
        "external_authority",
    }:
        errors.append("enforcement_class_census_mismatch")
    if set(contract["enforcement_classification"]["external_authority"]) != {
        "current_source_truth",
        "current_user_authority",
        "fresh_scoped_read",
        "command_precondition_mutation_audit_and_readback",
    }:
        errors.append("external_authority_set_mismatch")
    if contract["next_descendant"] != {
        "id": "provider-free-unmounted-event-cue-inert-ddl-lowering",
        "sql_text_rendering_only": True,
        "database_connection": False,
        "migration_execution": False,
        "watcher_or_source": False,
        "persistence_restart_or_delivery": False,
    }:
        errors.append("next_descendant_boundary_mismatch")
    return errors


def _is_positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _valid_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sha256:")
        and len(value) == 71
        and all(character in "0123456789abcdef" for character in value[7:])
    )


def _row_key(row: dict[str, Any], fields: list[str]) -> tuple[Any, ...]:
    return tuple(row[field] for field in fields)


def validate_rows(rows: dict[str, list[dict[str, Any]]]) -> list[str]:
    errors: list[str] = []
    if list(rows) != list(EXPECTED_RELATIONS):
        return ["row_relation_order_or_census_mismatch"]

    relation_rows = rows
    for name, expected in EXPECTED_RELATIONS.items():
        expected_fields = [field[0] for field in expected["fields"]]
        seen_primary: set[tuple[Any, ...]] = set()
        seen_unique: list[set[tuple[Any, ...]]] = [set() for _ in expected["unique_keys"]]
        for index, row in enumerate(relation_rows[name]):
            if list(row) != expected_fields:
                errors.append(f"{name}[{index}]:field_order_or_census_mismatch")
                continue
            for field_name, field_type, nullable in expected["fields"]:
                value = row[field_name]
                if value is None:
                    if not nullable:
                        errors.append(f"{name}[{index}]:{field_name}:null_forbidden")
                    continue
                if field_type in {"digest", "nullable_digest"} and not _valid_digest(value):
                    errors.append(f"{name}[{index}]:{field_name}:digest_invalid")
                elif field_type in {"positive_integer", "nullable_positive_integer"} and not _is_positive_integer(value):
                    errors.append(f"{name}[{index}]:{field_name}:positive_integer_invalid")
                elif field_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"{name}[{index}]:{field_name}:boolean_invalid")
                elif field_type in {"enum", "nullable_enum", "opaque_id"} and (
                    not isinstance(value, str) or not value
                ):
                    errors.append(f"{name}[{index}]:{field_name}:string_invalid")
            primary = _row_key(row, expected["primary_key"])
            if primary in seen_primary:
                errors.append(f"{name}[{index}]:primary_key_duplicate")
            seen_primary.add(primary)
            for unique_index, fields in enumerate(expected["unique_keys"]):
                unique = _row_key(row, fields)
                if unique in seen_unique[unique_index]:
                    errors.append(f"{name}[{index}]:unique_key_duplicate:{unique_index}")
                seen_unique[unique_index].add(unique)

    # Semantic checks below intentionally assume the exact closed row shape.
    # Structural failures are already fail-closed and must not be interpreted.
    if errors:
        return errors

    partitions = {row["partition_id"]: row for row in relation_rows["event_partition"]}
    obligations = {row["obligation_id"]: row for row in relation_rows["cue_obligation"]}
    attempts = {
        (row["obligation_id"], row["attempt_ordinal"]): row
        for row in relation_rows["dispatch_attempt"]
    }
    receipts_by_coordinate = {
        (row["partition_id"], row["source_epoch_digest"], row["source_position"]): row
        for row in relation_rows["terminal_receipt"]
    }

    for index, partition in enumerate(relation_rows["event_partition"]):
        expected_id = _digest(
            "|".join(
                [
                    partition["source_system"],
                    partition["practice_scope_digest"],
                    partition["event_family"],
                ]
            )
        )
        if partition["partition_id"] != expected_id:
            errors.append(f"event_partition[{index}]:partition_digest_mismatch")
        if partition["source_system"] != SOURCE_SYSTEM:
            errors.append(f"event_partition[{index}]:source_system_not_allowlisted")
        if partition["event_family"] != EVENT_FAMILY:
            errors.append(f"event_partition[{index}]:event_family_not_allowlisted")

    for relation_name in (
        "observer_coordinate",
        "terminal_receipt",
        "cue_obligation",
        "consumer_checkpoint",
    ):
        for index, row in enumerate(relation_rows[relation_name]):
            if row["partition_id"] not in partitions:
                errors.append(f"{relation_name}[{index}]:partition_orphan")

    for index, coordinate in enumerate(relation_rows["observer_coordinate"]):
        if coordinate["consumer_scope"] != CONSUMER_SCOPE:
            errors.append(f"observer_coordinate[{index}]:consumer_scope_invalid")
        if (coordinate["observed_state"] == "none") != (coordinate["observed_position"] is None):
            errors.append(f"observer_coordinate[{index}]:observed_state_shape_invalid")
        if coordinate["observed_state"] not in {"none", "exact"}:
            errors.append(f"observer_coordinate[{index}]:observed_state_invalid")
        head_state = coordinate["source_head_state"]
        head_epoch = coordinate["source_head_epoch_digest"]
        head_position = coordinate["source_head_position"]
        if head_state == "unknown":
            if head_epoch is not None or head_position is not None:
                errors.append(f"observer_coordinate[{index}]:unknown_head_has_coordinate")
        elif head_state == "exact":
            if head_epoch != coordinate["source_epoch_digest"] or head_position is None:
                errors.append(f"observer_coordinate[{index}]:exact_head_shape_invalid")
        elif head_state == "epoch_mismatch":
            if head_epoch is None or head_position is None or head_epoch == coordinate["source_epoch_digest"]:
                errors.append(f"observer_coordinate[{index}]:epoch_mismatch_shape_invalid")
        else:
            errors.append(f"observer_coordinate[{index}]:source_head_state_invalid")

    for index, receipt in enumerate(relation_rows["terminal_receipt"]):
        classification = receipt["classification"]
        reason = receipt["reason_code"]
        obligation_id = receipt["obligation_id"]
        if classification == "cue_required":
            if reason not in CUE_REASONS or obligation_id is None:
                errors.append(f"terminal_receipt[{index}]:cue_shape_invalid")
            else:
                obligation = obligations.get(obligation_id)
                if obligation is None:
                    errors.append(f"terminal_receipt[{index}]:obligation_orphan")
                elif not (
                    obligation["partition_id"] == receipt["partition_id"]
                    and obligation["source_epoch_digest"] == receipt["source_epoch_digest"]
                    and obligation["reason_code"] == reason
                    and obligation["from_position"]
                    <= receipt["source_position"]
                    <= obligation["through_position"]
                ):
                    errors.append(f"terminal_receipt[{index}]:obligation_coverage_mismatch")
        elif classification == "suppressed_irrelevant":
            if reason is not None or obligation_id is not None:
                errors.append(f"terminal_receipt[{index}]:suppression_shape_invalid")
        elif classification == "rejected_unsupported":
            if reason not in REJECTION_REASONS or obligation_id is not None:
                errors.append(f"terminal_receipt[{index}]:rejection_shape_invalid")
        else:
            errors.append(f"terminal_receipt[{index}]:classification_invalid")

    for index, obligation in enumerate(relation_rows["cue_obligation"]):
        if obligation["consumer_scope"] != CONSUMER_SCOPE:
            errors.append(f"cue_obligation[{index}]:consumer_scope_invalid")
        if obligation["reason_code"] not in CUE_REASONS:
            errors.append(f"cue_obligation[{index}]:reason_invalid")
        if obligation["fresh_authorized_read_required"] is not True:
            errors.append(f"cue_obligation[{index}]:fresh_read_literal_invalid")
        if obligation["state"] not in {"pending", "delivered"}:
            errors.append(f"cue_obligation[{index}]:state_invalid")
        if not (
            _is_positive_integer(obligation["from_position"])
            and _is_positive_integer(obligation["through_position"])
            and obligation["from_position"] <= obligation["through_position"]
        ):
            errors.append(f"cue_obligation[{index}]:range_invalid")

    for index, checkpoint in enumerate(relation_rows["consumer_checkpoint"]):
        if checkpoint["consumer_scope"] != CONSUMER_SCOPE:
            errors.append(f"consumer_checkpoint[{index}]:consumer_scope_invalid")
        if (checkpoint["checkpoint_state"] == "none") != (
            checkpoint["checkpoint_position"] is None
        ):
            errors.append(f"consumer_checkpoint[{index}]:state_shape_invalid")
        if checkpoint["checkpoint_state"] not in {"none", "exact"}:
            errors.append(f"consumer_checkpoint[{index}]:state_invalid")
        partition = partitions.get(checkpoint["partition_id"])
        if partition is not None and checkpoint["lease_generation"] != partition["lease_generation"]:
            errors.append(f"consumer_checkpoint[{index}]:stale_generation")
        through = checkpoint["checkpoint_position"]
        if through is not None:
            for position in range(1, through + 1):
                coordinate = (
                    checkpoint["partition_id"],
                    checkpoint["source_epoch_digest"],
                    position,
                )
                receipt = receipts_by_coordinate.get(coordinate)
                if receipt is None:
                    errors.append(f"consumer_checkpoint[{index}]:gap_at:{position}")
                    break
                if receipt["classification"] == "cue_required" and receipt["obligation_id"] not in obligations:
                    errors.append(f"consumer_checkpoint[{index}]:obligation_gap_at:{position}")
                    break

    attempt_ordinals: dict[str, list[int]] = {}
    delivered_obligations: set[str] = set()
    for index, attempt in enumerate(relation_rows["dispatch_attempt"]):
        obligation = obligations.get(attempt["obligation_id"])
        if obligation is None:
            errors.append(f"dispatch_attempt[{index}]:obligation_orphan")
            continue
        partition = partitions.get(obligation["partition_id"])
        if partition is not None and attempt["lease_generation"] != partition["lease_generation"]:
            errors.append(f"dispatch_attempt[{index}]:stale_generation")
        attempt_ordinals.setdefault(attempt["obligation_id"], []).append(
            attempt["attempt_ordinal"]
        )
        if attempt["outcome"] == "delivered":
            if attempt["failure_class"] is not None:
                errors.append(f"dispatch_attempt[{index}]:delivered_has_failure")
            delivered_obligations.add(attempt["obligation_id"])
        elif attempt["outcome"] == "failed":
            if attempt["failure_class"] not in {
                "consumer_unavailable",
                "authorization_rejected",
                "transient_transport",
            }:
                errors.append(f"dispatch_attempt[{index}]:failure_class_invalid")
        else:
            errors.append(f"dispatch_attempt[{index}]:outcome_invalid")
    for obligation_id, ordinals in attempt_ordinals.items():
        if sorted(ordinals) != list(range(1, max(ordinals) + 1)):
            errors.append(f"dispatch_attempt:{obligation_id}:ordinal_gap")
    for obligation_id, obligation in obligations.items():
        if obligation["state"] == "delivered" and obligation_id not in delivered_obligations:
            errors.append(f"cue_obligation:{obligation_id}:delivered_without_attempt")
        if obligation["state"] == "pending" and obligation_id in delivered_obligations:
            errors.append(f"cue_obligation:{obligation_id}:pending_after_delivery")

    seen_reconciliation_obligations: set[str] = set()
    for index, reconciliation in enumerate(relation_rows["reconciliation_receipt"]):
        obligation_id = reconciliation["obligation_id"]
        if obligation_id in seen_reconciliation_obligations:
            errors.append(f"reconciliation_receipt[{index}]:obligation_duplicate")
        seen_reconciliation_obligations.add(obligation_id)
        attempt = attempts.get(
            (obligation_id, reconciliation["dispatch_attempt_ordinal"])
        )
        if attempt is None or attempt["outcome"] != "delivered":
            errors.append(f"reconciliation_receipt[{index}]:delivered_attempt_missing")
        expected_shape = RECONCILIATION_SHAPES.get(reconciliation["outcome"])
        actual_shape = (
            reconciliation["scope_authorized"],
            reconciliation["fresh_read_performed"],
            reconciliation["display_disposition"],
        )
        if expected_shape != actual_shape:
            errors.append(f"reconciliation_receipt[{index}]:truth_table_mismatch")
        if reconciliation["acknowledgement"] != "one_fresh_read_attempt_only":
            errors.append(f"reconciliation_receipt[{index}]:acknowledgement_invalid")
        obligation = obligations.get(obligation_id)
        if obligation is None or obligation["state"] != "delivered":
            errors.append(f"reconciliation_receipt[{index}]:obligation_not_delivered")
    return errors


def _base_rows() -> dict[str, list[dict[str, Any]]]:
    practice_digest = _digest("authored-synthetic-practice-alpha")
    epoch_digest = _digest("authored-synthetic-epoch-001")
    partition_id = _digest(f"{SOURCE_SYSTEM}|{practice_digest}|{EVENT_FAMILY}")
    return {
        "event_partition": [
            {
                "partition_id": partition_id,
                "source_system": SOURCE_SYSTEM,
                "practice_scope_digest": practice_digest,
                "event_family": EVENT_FAMILY,
                "source_epoch_digest": epoch_digest,
                "lease_generation": 7,
            }
        ],
        "observer_coordinate": [
            {
                "partition_id": partition_id,
                "consumer_scope": CONSUMER_SCOPE,
                "source_epoch_digest": epoch_digest,
                "observed_state": "none",
                "observed_position": None,
                "source_head_state": "unknown",
                "source_head_epoch_digest": None,
                "source_head_position": None,
            }
        ],
        "terminal_receipt": [],
        "cue_obligation": [],
        "consumer_checkpoint": [
            {
                "partition_id": partition_id,
                "consumer_scope": CONSUMER_SCOPE,
                "source_epoch_digest": epoch_digest,
                "checkpoint_state": "none",
                "checkpoint_position": None,
                "lease_generation": 7,
            }
        ],
        "dispatch_attempt": [],
        "reconciliation_receipt": [],
    }


def _add_receipt(
    rows: dict[str, list[dict[str, Any]]],
    position: int,
    classification: str,
    reason: str | None,
    obligation_id: str | None,
) -> None:
    partition = rows["event_partition"][0]
    rows["terminal_receipt"].append(
        {
            "receipt_id": f"receipt:{position:04d}",
            "partition_id": partition["partition_id"],
            "source_epoch_digest": partition["source_epoch_digest"],
            "source_position": position,
            "event_fingerprint_digest": _digest(f"event-{position}-{classification}"),
            "classification": classification,
            "reason_code": reason,
            "obligation_id": obligation_id,
        }
    )
    coordinate = rows["observer_coordinate"][0]
    coordinate["observed_state"] = "exact"
    coordinate["observed_position"] = max(coordinate["observed_position"] or 0, position)


def _add_obligation(
    rows: dict[str, list[dict[str, Any]]],
    obligation_id: str,
    from_position: int,
    through_position: int,
    reason: str,
    *,
    state: str = "pending",
) -> None:
    partition = rows["event_partition"][0]
    rows["cue_obligation"].append(
        {
            "obligation_id": obligation_id,
            "partition_id": partition["partition_id"],
            "consumer_scope": CONSUMER_SCOPE,
            "source_epoch_digest": partition["source_epoch_digest"],
            "from_position": from_position,
            "through_position": through_position,
            "reason_code": reason,
            "fresh_authorized_read_required": True,
            "state": state,
        }
    )


def _set_checkpoint(rows: dict[str, list[dict[str, Any]]], position: int) -> None:
    checkpoint = rows["consumer_checkpoint"][0]
    checkpoint["checkpoint_state"] = "exact"
    checkpoint["checkpoint_position"] = position


def _required_rows(*, state: str = "pending") -> tuple[dict[str, list[dict[str, Any]]], str]:
    rows = _base_rows()
    obligation_id = "obligation:0001"
    _add_obligation(
        rows,
        obligation_id,
        1,
        1,
        "diary_status_may_have_changed",
        state=state,
    )
    _add_receipt(
        rows,
        1,
        "cue_required",
        "diary_status_may_have_changed",
        obligation_id,
    )
    _set_checkpoint(rows, 1)
    return rows, obligation_id


def build_scenarios() -> dict[str, dict[str, list[dict[str, Any]]]]:
    scenarios: dict[str, dict[str, list[dict[str, Any]]]] = {}
    scenarios["empty_partition"] = _base_rows()

    pending, _ = _required_rows()
    scenarios["one_required_pending"] = pending

    coalesced = _base_rows()
    coalesced_id = "obligation:coalesced"
    _add_obligation(
        coalesced,
        coalesced_id,
        1,
        2,
        "diary_status_may_have_changed",
    )
    for position in (1, 2):
        _add_receipt(
            coalesced,
            position,
            "cue_required",
            "diary_status_may_have_changed",
            coalesced_id,
        )
    _set_checkpoint(coalesced, 2)
    scenarios["same_reason_coalesced"] = coalesced

    separate = _base_rows()
    for position, reason in (
        (1, "diary_status_may_have_changed"),
        (2, "diary_availability_may_have_changed"),
    ):
        obligation_id = f"obligation:{position:04d}"
        _add_obligation(separate, obligation_id, position, position, reason)
        _add_receipt(separate, position, "cue_required", reason, obligation_id)
    _set_checkpoint(separate, 2)
    scenarios["different_reason_separate"] = separate

    gap = _base_rows()
    _add_obligation(
        gap,
        "obligation:0002",
        2,
        2,
        "diary_status_may_have_changed",
    )
    _add_receipt(
        gap,
        2,
        "cue_required",
        "diary_status_may_have_changed",
        "obligation:0002",
    )
    scenarios["out_of_order_gap_held"] = gap

    gap_filled = copy.deepcopy(gap)
    _add_receipt(gap_filled, 1, "suppressed_irrelevant", None, None)
    _set_checkpoint(gap_filled, 2)
    gap_filled["terminal_receipt"].sort(key=lambda row: row["source_position"])
    scenarios["gap_filled_checkpoint_advanced"] = gap_filled

    suppressed = _base_rows()
    _add_receipt(suppressed, 1, "suppressed_irrelevant", None, None)
    _set_checkpoint(suppressed, 1)
    scenarios["suppressed_without_obligation"] = suppressed

    rejected = _base_rows()
    _add_receipt(
        rejected,
        1,
        "rejected_unsupported",
        "unsupported_event_schema",
        None,
    )
    _set_checkpoint(rejected, 1)
    scenarios["rejected_without_obligation"] = rejected

    failed, failed_id = _required_rows()
    failed["dispatch_attempt"].append(
        {
            "obligation_id": failed_id,
            "attempt_ordinal": 1,
            "lease_generation": 7,
            "outcome": "failed",
            "failure_class": "transient_transport",
        }
    )
    scenarios["dispatch_failed_pending"] = failed

    delivered, delivered_id = _required_rows(state="delivered")
    delivered["dispatch_attempt"].append(
        {
            "obligation_id": delivered_id,
            "attempt_ordinal": 1,
            "lease_generation": 7,
            "outcome": "delivered",
            "failure_class": None,
        }
    )
    scenarios["dispatch_delivered"] = delivered

    refreshed = copy.deepcopy(delivered)
    refreshed["reconciliation_receipt"].append(
        {
            "reconciliation_id": "reconciliation:refreshed",
            "obligation_id": delivered_id,
            "dispatch_attempt_ordinal": 1,
            "outcome": "projection_refreshed",
            "scope_authorized": True,
            "fresh_read_performed": True,
            "acknowledgement": "one_fresh_read_attempt_only",
            "display_disposition": "refreshed",
        }
    )
    scenarios["reconciliation_refreshed"] = refreshed

    failed_reconciliation = copy.deepcopy(delivered)
    failed_reconciliation["reconciliation_receipt"].append(
        {
            "reconciliation_id": "reconciliation:authorization-rejected",
            "obligation_id": delivered_id,
            "dispatch_attempt_ordinal": 1,
            "outcome": "authorization_rejected",
            "scope_authorized": False,
            "fresh_read_performed": False,
            "acknowledgement": "one_fresh_read_attempt_only",
            "display_disposition": "unchanged",
        }
    )
    scenarios["reconciliation_failure_retains_display"] = failed_reconciliation
    return scenarios


def build_contract_hostiles(contract: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    hostiles: list[tuple[str, dict[str, Any]]] = []
    for index, relation in enumerate(contract["relations"]):
        for mutation_name in (
            "relation_removed",
            "first_field_removed",
            "primary_key_corrupt",
            "prohibited_field_added",
            "checks_cleared",
        ):
            candidate = copy.deepcopy(contract)
            if mutation_name == "relation_removed":
                candidate["relations"].pop(index)
            elif mutation_name == "first_field_removed":
                candidate["relations"][index]["fields"].pop(0)
            elif mutation_name == "primary_key_corrupt":
                candidate["relations"][index]["primary_key"] = ["not_a_field"]
            elif mutation_name == "prohibited_field_added":
                candidate["relations"][index]["fields"].append(
                    {"name": "patient_id", "type": "opaque_id", "nullable": True}
                )
            else:
                candidate["relations"][index]["checks"] = []
            hostiles.append((f"{relation['name']}:{mutation_name}", candidate))
    for index, protocol in enumerate(contract["transaction_protocols"]):
        candidate = copy.deepcopy(contract)
        candidate["transaction_protocols"].pop(index)
        hostiles.append((f"{protocol['name']}:protocol_removed", candidate))
    for key in contract["authority"]:
        candidate = copy.deepcopy(contract)
        candidate["authority"][key] = not candidate["authority"][key]
        hostiles.append((f"authority:{key}:flipped", candidate))
    for key in contract["enforcement_classification"]:
        candidate = copy.deepcopy(contract)
        del candidate["enforcement_classification"][key]
        hostiles.append((f"enforcement:{key}:removed", candidate))
    candidate = copy.deepcopy(contract)
    candidate["representability_scenario_ids"][-1] = "unfrozen_extra_scenario"
    hostiles.append(("scenario_census:substituted", candidate))
    return hostiles


def build_row_hostiles(
    scenarios: dict[str, dict[str, list[dict[str, Any]]]]
) -> list[tuple[str, dict[str, list[dict[str, Any]]]]]:
    base = scenarios["reconciliation_refreshed"]
    hostiles: list[tuple[str, dict[str, list[dict[str, Any]]]]] = []

    def mutate(name: str, action: Any) -> None:
        candidate = copy.deepcopy(base)
        action(candidate)
        hostiles.append((name, candidate))

    for relation_name in EXPECTED_RELATIONS:
        if base[relation_name]:
            field = EXPECTED_RELATIONS[relation_name]["fields"][0][0]
            mutate(
                f"{relation_name}:field_removed",
                lambda rows, rn=relation_name, fn=field: rows[rn][0].pop(fn),
            )
            mutate(
                f"{relation_name}:payload_added",
                lambda rows, rn=relation_name: rows[rn][0].update({"patient_id": "forbidden"}),
            )
    mutate("partition:digest_mismatch", lambda rows: rows["event_partition"][0].update({"partition_id": _digest("wrong")}))
    mutate("coordinate:unknown_with_position", lambda rows: rows["observer_coordinate"][0].update({"source_head_position": 1}))
    mutate("receipt:position_zero", lambda rows: rows["terminal_receipt"][0].update({"source_position": 0}))
    mutate("receipt:obligation_orphan", lambda rows: rows["terminal_receipt"][0].update({"obligation_id": "obligation:missing"}))
    mutate("obligation:range_reversed", lambda rows: rows["cue_obligation"][0].update({"from_position": 2, "through_position": 1}))
    mutate("obligation:fresh_read_false", lambda rows: rows["cue_obligation"][0].update({"fresh_authorized_read_required": False}))
    mutate("checkpoint:stale_generation", lambda rows: rows["consumer_checkpoint"][0].update({"lease_generation": 6}))
    mutate("checkpoint:gap_crossed", lambda rows: rows["consumer_checkpoint"][0].update({"checkpoint_position": 2}))
    mutate("dispatch:failure_without_class", lambda rows: rows["dispatch_attempt"][0].update({"outcome": "failed", "failure_class": None}))
    mutate("dispatch:stale_generation", lambda rows: rows["dispatch_attempt"][0].update({"lease_generation": 6}))
    mutate("reconciliation:without_delivered_attempt", lambda rows: rows["dispatch_attempt"][0].update({"outcome": "failed", "failure_class": "transient_transport"}))
    mutate("reconciliation:fresh_read_false_on_success", lambda rows: rows["reconciliation_receipt"][0].update({"fresh_read_performed": False}))
    mutate("reconciliation:future_freshness_claim", lambda rows: rows["reconciliation_receipt"][0].update({"acknowledgement": "fresh_forever"}))
    mutate("reconciliation:display_mismatch", lambda rows: rows["reconciliation_receipt"][0].update({"display_disposition": "cleared"}))
    return hostiles


def run_acceptance() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    contract_errors = validate_contract(contract, schema)

    scenarios = build_scenarios()
    scenario_errors = {
        scenario_id: errors
        for scenario_id, rows in scenarios.items()
        if (errors := validate_rows(rows))
    }
    contract_before = _canonical_digest(contract)
    contract_hostiles = build_contract_hostiles(contract)
    admitted_contract_hostiles = [
        name
        for name, candidate in contract_hostiles
        if not validate_contract(candidate, schema)
    ]
    rows_before = _canonical_digest(scenarios)
    row_hostiles = build_row_hostiles(scenarios)
    admitted_row_hostiles = [
        name for name, candidate in row_hostiles if not validate_rows(candidate)
    ]

    evidence = {
        "schema_version": "raisa.context_fabric.unmounted_event_cue_representation.evidence.v1",
        "status": "passed",
        "planning_baseline": contract["planning_baseline"],
        "accepted_observability_source": contract["accepted_observability_source"],
        "accepted_admission_source": contract["accepted_admission_source"],
        "relation_count": len(contract["relations"]),
        "transaction_protocol_count": len(contract["transaction_protocols"]),
        "representability_scenario_count": len(scenarios),
        "representability_scenario_digest": _canonical_digest(scenarios),
        "contract_hostile_rejection_count": len(contract_hostiles)
        - len(admitted_contract_hostiles),
        "row_hostile_rejection_count": len(row_hostiles) - len(admitted_row_hostiles),
        "total_hostile_rejection_count": len(contract_hostiles)
        + len(row_hostiles)
        - len(admitted_contract_hostiles)
        - len(admitted_row_hostiles),
        "contract_errors": contract_errors,
        "scenario_errors": scenario_errors,
        "admitted_contract_hostiles": admitted_contract_hostiles,
        "admitted_row_hostiles": admitted_row_hostiles,
        "canonical_contract_unchanged": _canonical_digest(contract) == contract_before,
        "canonical_rows_unchanged": _canonical_digest(scenarios) == rows_before,
        "sql_or_ddl_rendered": False,
        "database_or_source_opened": False,
        "migration_executed": False,
        "operational_state_persisted": False,
        "runtime_started": False,
        "provider_calls": 0,
        "command_or_write": False,
        "product_patient_or_clinical_data": False,
    }
    if (
        contract_errors
        or scenario_errors
        or admitted_contract_hostiles
        or admitted_row_hostiles
        or evidence["relation_count"] != 7
        or evidence["transaction_protocol_count"] != 5
        or evidence["representability_scenario_count"] != 12
        or evidence["total_hostile_rejection_count"] < 48
        or not evidence["canonical_contract_unchanged"]
        or not evidence["canonical_rows_unchanged"]
    ):
        evidence["status"] = "failed"
    return evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Do not write evidence.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evidence = run_acceptance()
    if not args.check:
        args.output.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(evidence, sort_keys=True))
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
