"""Export a safe neutral derived graph from historical diary trend data."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.historical_diary_output_safety import (
    load_json,
    validate_historical_diary_output,
)


DEFAULT_OUTPUT = Path(
    "local_data/historical-diary-trove/inventory/neutral_derived_graph_h18.json"
)
DELTA_BUCKETS = (
    (0, "none"),
    (2, "tiny"),
    (10, "small"),
    (100, "medium"),
)


def build_neutral_derived_graph(trend_payload: dict[str, Any]) -> dict[str, Any]:
    validate_historical_diary_output(trend_payload)

    roots = sorted(trend_payload.get("roots", []), key=lambda root: root["root_label"])
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    event_classes = sorted(
        {
            item["value"]
            for root in roots
            for item in root.get("event_class_distribution", [])
        }
    )
    delta_buckets = sorted(
        {
            _delta_bucket_node_value(range_key, range_value)
            for root in roots
            for range_key, range_value in root.get(
                "adjacent_neutral_delta_ranges", {}
            ).items()
        }
    )

    for root in roots:
        root_label = root["root_label"]
        nodes.append(
            {
                "node_id": _root_node_id(root_label),
                "node_kind": "root",
                "root_label": root_label,
                "snapshot_count": int(root["snapshot_count"]),
                "transition_count": int(root["transition_count"]),
            }
        )

    for event_class in event_classes:
        nodes.append(
            {
                "node_id": _event_class_node_id(event_class),
                "node_kind": "event_class",
                "event_class": event_class,
            }
        )

    for value in delta_buckets:
        nodes.append(
            {
                "node_id": _delta_bucket_node_id(value),
                "node_kind": "delta_bucket",
                "value": value,
            }
        )

    for root in roots:
        root_label = root["root_label"]
        for item in sorted(
            root.get("event_class_distribution", []), key=lambda value: value["value"]
        ):
            event_class = item["value"]
            count = int(item["count"])
            if count == 0:
                continue
            edges.append(
                {
                    "edge_id": f"edge:{root_label}:{event_class}",
                    "edge_kind": "has_event_class_count",
                    "source_node_id": _root_node_id(root_label),
                    "target_node_id": _event_class_node_id(event_class),
                    "count": count,
                }
            )
        for range_key, range_value in sorted(
            root.get("adjacent_neutral_delta_ranges", {}).items()
        ):
            value = _delta_bucket_node_value(range_key, range_value)
            edges.append(
                {
                    "edge_id": f"edge:{root_label}:{value}",
                    "edge_kind": "has_delta_bucket",
                    "source_node_id": _root_node_id(root_label),
                    "target_node_id": _delta_bucket_node_id(value),
                    "min": int(range_value["min"]),
                    "max": int(range_value["max"]),
                }
            )

    output = {
        "classifier": {
            "output_class": "neutral_derived_graph",
            "version": 1,
            "sample_only": True,
        },
        "privacy": {
            "emits_document_text": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "emits_exact_document_timestamps": False,
            "emits_patient_or_staff_labels": False,
        },
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "graph": {
            "version": 1,
            "sample_only": True,
            "output_class": "neutral_derived_graph",
            "root_count": len(roots),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "transition_count": sum(int(root["transition_count"]) for root in roots),
        },
        "nodes": nodes,
        "edges": edges,
    }
    validate_historical_diary_output(output)
    return output


def _root_node_id(root_label: str) -> str:
    return f"root:{root_label}"


def _event_class_node_id(event_class: str) -> str:
    return f"event_class:{event_class}"


def _delta_bucket_node_id(value: str) -> str:
    return f"delta_bucket:{value}"


def _delta_bucket_node_value(range_key: str, range_value: dict[str, Any]) -> str:
    return f"{range_key}:{_bucket_name(int(range_value['max']))}"


def _bucket_name(max_value: int) -> str:
    for upper_bound, name in DELTA_BUCKETS:
        if max_value <= upper_bound:
            return name
    return "large"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cross_pilot_event_trends_json", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = build_neutral_derived_graph(load_json(args.cross_pilot_event_trends_json))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote safe neutral derived graph: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
