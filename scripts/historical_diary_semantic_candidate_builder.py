"""Build approved H15 semantic candidate fixtures from safe neutral aggregates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.historical_diary_deidentification_gate import load_json as load_gate_json
from scripts.historical_diary_deidentification_gate import validate_deidentification_gate
from scripts.historical_diary_output_safety import (
    validate_historical_diary_output,
    validate_historical_diary_semantic_fixture_output,
)


SCHEMA_VERSION = "historical_diary.semantic_fixture.v1"
SOURCE = "approved_h15_review_payload"
FIXTURE_FAMILY = "action_grammar_candidates"
APPROVED_SLICE = "single_root_single_dense_day_max_80"
MAX_SAMPLE_SIZE = 80


def build_semantic_candidates(
    aggregate_payload: dict[str, Any],
    approved_gate_payload: dict[str, Any],
) -> dict[str, Any]:
    """Create source-safe semantic candidates from an H15-approved aggregate.

    The builder intentionally uses only neutral counts and sequence indexes from
    an aggregate already accepted by the H5 validator. It emits coarse candidate
    action labels, not raw diary text or committed appointment facts.
    """
    validate_historical_diary_output(aggregate_payload)
    validate_deidentification_gate(approved_gate_payload)
    _assert_approved_scope(approved_gate_payload)

    roots = aggregate_payload.get("roots")
    if not isinstance(roots, list) or len(roots) != 1:
        raise ValueError("H15 prototype requires exactly one root")
    root = roots[0]
    if root.get("requested_sample_size", 0) > MAX_SAMPLE_SIZE:
        raise ValueError("H15 prototype sample size exceeds approved cap")

    snapshots = root.get("ordered_neutral_snapshots")
    if not isinstance(snapshots, list) or not snapshots:
        raise ValueError("H15 prototype requires ordered neutral snapshots")

    fixture_count = min(len(snapshots), MAX_SAMPLE_SIZE)
    fixtures = []
    for index, snapshot in enumerate(snapshots[:fixture_count]):
        fixtures.append(_candidate_from_snapshot(index, snapshot))

    payload = {
        "schema_version": SCHEMA_VERSION,
        "source": SOURCE,
        "privacy": {
            "local_raw_processing_only": True,
            "raw_data_external_provider_allowed": False,
            "emits_document_text": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "emits_exact_document_timestamps": False,
            "emits_patient_or_staff_labels": False,
        },
        "semantic_scope": {
            "fixture_family": FIXTURE_FAMILY,
            "date_policy": approved_gate_payload["deidentification_policy"]["date_policy"],
            "allowed_action_names": sorted(
                {
                    "create",
                    "move",
                    "resize",
                    "cancel",
                    "status_change",
                    "check_in",
                    "waiting_area_move",
                    "link_patient",
                    "slot_search",
                    "explain_schedule",
                    "handoff",
                }
            ),
            "approval_expires_on": approved_gate_payload["approval"]["approval_expires_on"],
        },
        "fixtures": fixtures,
    }

    validate_historical_diary_semantic_fixture_output(payload)
    return payload


def _assert_approved_scope(gate_payload: dict[str, Any]) -> None:
    if gate_payload.get("decision") != "approved_for_semantic_fixture_promotion":
        raise ValueError("H15 semantic candidate builder requires an approved gate payload")
    scope = gate_payload.get("approval", {}).get("semantic_scope", {})
    if scope.get("prototype_slice") != APPROVED_SLICE:
        raise ValueError("H15 gate approval does not match the bounded prototype slice")
    if scope.get("memory_use") != "prohibited":
        raise ValueError("H15 gate approval must prohibit memory use")
    families = scope.get("fixture_families")
    if families != [FIXTURE_FAMILY]:
        raise ValueError("H15 gate approval must be limited to action_grammar_candidates")


def _candidate_from_snapshot(index: int, snapshot: dict[str, Any]) -> dict[str, Any]:
    sequence_index = snapshot.get("sequence_index")
    if not isinstance(sequence_index, int):
        raise ValueError("ordered snapshot sequence_index must be an integer")

    return {
        "synthetic_event_id": f"event_{index:03d}",
        "relative_day_index": 0,
        "time_of_day": _time_bucket(snapshot.get("inferred_time_interval_mode_minutes")),
        "duration_minutes": _duration_bucket(snapshot.get("inferred_time_interval_mode_minutes")),
        "synthetic_resource_id": "resource_001",
        "action_name": "explain_schedule",
        "status_categories": ["unknown"],
        "transition_label": "candidate_explain_schedule",
        "confidence_label": "low",
        "bucket_flags": _bucket_flags(snapshot),
    }


def _time_bucket(value: Any) -> str:
    if isinstance(value, int) and value > 0:
        return f"time_bucket_interval_{value}"
    return "time_bucket_unknown"


def _duration_bucket(value: Any) -> int:
    if isinstance(value, int) and 5 <= value <= 120:
        return value
    return 10


def _bucket_flags(snapshot: dict[str, Any]) -> list[str]:
    flags = ["candidate_only"]
    if snapshot.get("structure_class") == "strong_diary_grid":
        flags.append("strong_grid")
    if snapshot.get("table_count") == 2:
        flags.append("two_tables")
    if snapshot.get("time_like_token_count", 0) >= 70:
        flags.append("dense_time_tokens")
    return flags


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate", required=True, type=Path)
    parser.add_argument("--gate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    aggregate = load_json(args.aggregate)
    gate = load_gate_json(args.gate)
    if not isinstance(aggregate, dict) or not isinstance(gate, dict):
        raise ValueError("aggregate and gate payloads must be JSON objects")

    output = build_semantic_candidates(aggregate, gate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(f"semantic candidates safe: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
